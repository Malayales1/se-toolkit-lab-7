from __future__ import annotations

import json
import sys
from typing import Any

from openai import OpenAI

from config import Settings
from services.lms_api import LMSApiClient


SYSTEM_PROMPT = """
You are the LMS bot's natural-language router and analyst.

Your job:
- Understand a user's plain-text request.
- Decide whether to answer directly or call tools.
- For any data question about labs, learners, scores, groups, timelines, completion, top learners, or sync status, use the provided tools instead of guessing.
- You may call multiple tools when needed.
- When a query compares labs, first discover available labs with get_items, then call the needed analytics tool for each relevant lab.
- If a message is a greeting, answer warmly and briefly explain what you can do.
- If a message is ambiguous, ask a short clarifying question.
- If a message is gibberish or not actionable, say you did not understand and suggest a few concrete things you can help with.

Response rules:
- Be concise, factual, and user-facing.
- Mention specific lab codes like lab-03 when relevant.
- Use bullet points when listing data.
- Never invent numbers or backend results.
""".strip()


def build_tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "List all labs and tasks from the LMS backend.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "List enrolled learners and their groups.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution buckets for a lab like lab-04.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, for example lab-04.",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, for example lab-04.",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, for example lab-03.",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group performance for a lab, including average scores and student counts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, for example lab-03.",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get the top learners for a lab by average score.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, for example lab-04.",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "How many learners to return.",
                            "default": 5,
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate statistics for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, for example lab-04.",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger an ETL data sync from the autochecker into the backend.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]


class LLMRouter:
    def __init__(self, settings: Settings, api_client: LMSApiClient):
        self.settings = settings
        self.api_client = api_client
        self.client = None
        if settings.llm_api_key and settings.llm_api_base_url:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_api_base_url,
            )
        self.tools = build_tool_schemas()

    async def route(self, user_message: str) -> str:
        if self.client is None:
            return (
                "LLM routing is not configured yet. Set LLM_API_KEY and "
                "LLM_API_BASE_URL in .env.bot.secret."
            )

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        for _ in range(6):
            response = self.client.chat.completions.create(
                model=self.settings.llm_api_model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
            )
            choice = response.choices[0].message
            tool_calls = choice.tool_calls or []

            if not tool_calls:
                content = choice.content or ""
                return content.strip() or (
                    "I could not produce an answer. Try asking about labs, "
                    "scores, groups, learners, or completion rates."
                )

            messages.append(
                {
                    "role": "assistant",
                    "content": choice.content or "",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in tool_calls
                    ],
                }
            )

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                arguments = self._parse_arguments(tool_call.function.arguments)
                print(
                    f"[tool] LLM called: {tool_name}({json.dumps(arguments)})",
                    file=sys.stderr,
                )
                result = await self._execute_tool(tool_name, arguments)
                print(
                    f"[tool] Result: {self._summarize_result(result)}",
                    file=sys.stderr,
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(result, ensure_ascii=True),
                    }
                )

            print(
                f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM",
                file=sys.stderr,
            )

        return (
            "I could not finish the request after several tool calls. "
            "Please try rephrasing the question."
        )

    def _parse_arguments(self, raw_arguments: str) -> dict[str, Any]:
        if not raw_arguments:
            return {}
        try:
            parsed = json.loads(raw_arguments)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _summarize_result(self, result: Any) -> str:
        if isinstance(result, list):
            return f"{len(result)} item(s)"
        if isinstance(result, dict):
            return ", ".join(sorted(result.keys())) or "empty object"
        return str(result)

    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        tool_map = {
            "get_items": lambda: self.api_client.get_items(),
            "get_learners": lambda: self.api_client.get_learners(),
            "get_scores": lambda: self.api_client.get_scores(str(arguments["lab"])),
            "get_pass_rates": lambda: self.api_client.get_pass_rates(str(arguments["lab"])),
            "get_timeline": lambda: self.api_client.get_timeline(str(arguments["lab"])),
            "get_groups": lambda: self.api_client.get_groups(str(arguments["lab"])),
            "get_top_learners": lambda: self.api_client.get_top_learners(
                str(arguments["lab"]),
                int(arguments.get("limit", 5)),
            ),
            "get_completion_rate": lambda: self.api_client.get_completion_rate(
                str(arguments["lab"])
            ),
            "trigger_sync": lambda: self.api_client.trigger_sync(),
        }

        if tool_name not in tool_map:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            return await tool_map[tool_name]()
        except Exception as exc:
            return {"error": self.api_client._format_error(exc)}
