from __future__ import annotations

from config import Settings
from handlers.commands import (
    handle_health,
    handle_help,
    handle_labs,
    handle_plain_text,
    handle_scores,
    handle_start,
)
from services import LLMRouter, LMSApiClient


async def route_message(
    message: str,
    api_client: LMSApiClient,
    settings: Settings,
) -> str:
    text = message.strip()
    if not text:
        return "Please send a command or a message."

    parts = text.split()
    command = parts[0].lower()

    if command == "/start":
        return await handle_start()
    if command == "/help":
        return await handle_help()
    if command == "/health":
        return await handle_health(api_client)
    if command == "/labs":
        return await handle_labs(api_client)
    if command == "/scores":
        return await handle_scores(parts[1] if len(parts) > 1 else None, api_client)
    if command.startswith("/"):
        return await handle_plain_text(text)

    llm_router = LLMRouter(settings, api_client)
    return await llm_router.route(text)
