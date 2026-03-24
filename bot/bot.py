#!/usr/bin/env python3

from __future__ import annotations

import argparse
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
    return await route_message(message_text, api_client, settings)


def build_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Available Labs", callback_data="ask:labs"),
                InlineKeyboardButton(text="Lab 4 Scores", callback_data="ask:lab4"),
            ],
            [
                InlineKeyboardButton(
                    text="Lowest Pass Rate",
                    callback_data="ask:lowest_pass_rate",
                ),
                InlineKeyboardButton(
                    text="Top Learners",
                    callback_data="ask:top_learners",
                ),
            ],
        ]
    )


def callback_to_prompt(callback_data: str) -> str:
    mapping = {
        "ask:labs": "what labs are available?",
        "ask:lab4": "show me scores for lab 4",
        "ask:lowest_pass_rate": "which lab has the lowest pass rate?",
        "ask:top_learners": "who are the top 5 students in lab 4?",
    }
    return mapping.get(callback_data, "what can you do?")


async def run_test_mode(message_text: str) -> int:
    response = await render_response(message_text)
    print(response)
    return 0


async def run_telegram_mode() -> int:
    settings = get_settings()
    if not settings.bot_token or settings.bot_token == "CHANGE_ME_WITH_BOTFATHER_TOKEN":
        print(
            "BOT_TOKEN is not configured. Waiting for a real Telegram token before polling starts.",
            file=sys.stderr,
        )
        while True:
            await asyncio.sleep(3600)

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()

    @dispatcher.message(Command("start", "help", "health", "labs", "scores"))
    async def command_handler(message: Message) -> None:
        response = await render_response(message.text or "")
        reply_markup = build_start_keyboard() if (message.text or "").startswith("/start") else None
        await message.answer(response, reply_markup=reply_markup)

    @dispatcher.message()
    async def text_handler(message: Message) -> None:
        response = await render_response(message.text or "")
        await message.answer(response)

    @dispatcher.callback_query()
    async def callback_handler(callback_query) -> None:
        prompt = callback_to_prompt(callback_query.data or "")
        response = await render_response(prompt)
        await callback_query.message.answer(response, reply_markup=build_start_keyboard())
        await callback_query.answer()

    await dispatcher.start_polling(bot)
    return 0


def main() -> int:
    args = parse_args()
    if args.test is not None:
        return asyncio.run(run_test_mode(args.test))
    return asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    raise SystemExit(main())
