from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[1]
BOT_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    bot_token: str | None = None
    lms_api_base_url: str
    lms_api_key: str
    llm_api_model: str = "coder-model"
    llm_api_key: str | None = None
    llm_api_base_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=(
            str(BOT_DIR / ".env.bot.secret"),
            str(ROOT_DIR / ".env.bot.secret"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()
