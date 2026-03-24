#!/usr/bin/env python3

from __future__ import annotations

import argparse
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import get_settings
from handlers import route_message
from services import LMSApiClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        metavar="MESSAGE",
        help="Run a command in offline test mode and print the result to stdout.",
    )
    return parser.parse_args()


async def render_response(message_text: str) -> str:
    settings = get_settings()
    api_client = LMSApiClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )
    return await route_message(message_text, api_client)


async def run_test_mode(message_text: str) -> int:
    response = await render_response(message_text)
    print(response)
    return 0


async def run_telegram_mode() -> int:
    settings = get_settings()
    if not settings.bot_token or settings.bot_token == "CHANGE_ME_WITH_BOTFATHER_TOKEN":
        raise SystemExit("BOT_TOKEN is required in non-test mode.")

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()

    @dispatcher.message(Command("start", "help", "health", "labs", "scores"))
    async def command_handler(message: Message) -> None:
        response = await render_response(message.text or "")
        await message.answer(response)

    @dispatcher.message()
    async def text_handler(message: Message) -> None:
        response = await render_response(message.text or "")
        await message.answer(response)

    await dispatcher.start_polling(bot)
    return 0


def main() -> int:
    args = parse_args()
    if args.test is not None:
        return asyncio.run(run_test_mode(args.test))
    return asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    raise SystemExit(main())
