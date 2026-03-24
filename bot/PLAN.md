Task 1 focuses on creating a bot skeleton that is stable enough for the next tasks, not on polishing every feature immediately. The main architectural decision is to separate message transport from business logic. Telegram-specific code should stay only in the entry point, while handlers return plain text and work the same way in test mode and in real bot mode. This keeps the code easy to debug, easy to test, and easy to extend when slash commands, LLM routing, and deployment are added later.

The first step is configuration. The bot needs a small settings layer that loads values from `.env.bot.secret` and supports running from inside the `bot/` directory. In test mode, `BOT_TOKEN` should not be required, because the autochecker must be able to run `uv run bot.py --test "/start"` without opening a Telegram connection. In normal mode, the token must be present.

The second step is a service layer. A lightweight LMS API client will handle authenticated HTTP requests to the backend. Even in Task 1, this gives useful behavior for `/health` and `/labs`, while `/scores` can stay scaffolded and return a friendly placeholder until Task 2.

The third step is a handler layer. Each handler receives simple inputs and returns plain text. A router maps commands like `/start`, `/help`, `/health`, and `/labs` to those handlers. Later tasks can add intent-based routing for natural language and more complex tool orchestration without changing the transport pattern.

The final step is runtime integration. `bot.py` will support two execution modes: `--test` for offline command execution and normal mode for Telegram polling through aiogram. That gives a fast feedback loop for development on the VM and a clean path toward the production bot container in Task 4.
