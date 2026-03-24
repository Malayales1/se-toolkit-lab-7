from __future__ import annotations

from services import LMSApiClient


async def handle_start() -> str:
    return (
        "Welcome to the LMS bot.\n"
        "Use /help to see available commands."
    )


async def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start - welcome message\n"
        "/help - list commands\n"
        "/health - check backend status\n"
        "/labs - list available labs\n"
        "/scores <lab> - show per-task pass rates for a lab"
    )


async def handle_health(api_client: LMSApiClient) -> str:
    return await api_client.health_summary()


async def handle_labs(api_client: LMSApiClient) -> str:
    try:
        labs = await api_client.list_labs()
    except Exception as exc:
        return api_client._format_error(exc)

    if not labs:
        return "No labs are available yet."

    return "Available labs:\n" + "\n".join(labs)


async def handle_scores(lab: str | None, api_client: LMSApiClient) -> str:
    if not lab:
        return "Usage: /scores <lab>"
    return await api_client.pass_rates_summary(lab)


async def handle_plain_text(message: str) -> str:
    if message.startswith("/"):
        return (
            f"Unknown command: {message}\n"
            "Use /help to see the available commands."
        )

    return (
        "Natural language routing is not implemented yet.\n"
        "Try /help to see the available commands."
    )
