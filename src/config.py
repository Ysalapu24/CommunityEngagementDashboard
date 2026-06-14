"""Application configuration with Streamlit secrets and .env fallback."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _streamlit_secrets() -> dict[str, Any]:
    try:
        import streamlit as st

        return dict(st.secrets)
    except Exception:
        return {}


def get_setting(name: str, default: str = "") -> str:
    secrets = _streamlit_secrets()
    value = secrets.get(name, os.getenv(name, default))
    if value is None:
        return default
    return str(value)


def get_bool_setting(name: str, default: bool = False) -> bool:
    value = get_setting(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def get_int_setting(name: str, default: int) -> int:
    try:
        return int(get_setting(name, str(default)))
    except ValueError:
        return default


def get_csv_setting(name: str) -> list[str]:
    return [item.strip() for item in get_setting(name).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_mode: str
    slack_bot_token: str
    slack_channel_ids: list[str]
    slack_fetch_threads: bool
    slack_message_limit: int
    discord_bot_token: str
    discord_channel_ids: list[str]
    discord_message_limit: int


def load_settings() -> Settings:
    return Settings(
        app_mode=get_setting("APP_MODE", "demo"),
        slack_bot_token=get_setting("SLACK_BOT_TOKEN"),
        slack_channel_ids=get_csv_setting("SLACK_CHANNEL_IDS"),
        slack_fetch_threads=get_bool_setting("SLACK_FETCH_THREADS", False),
        slack_message_limit=get_int_setting("SLACK_MESSAGE_LIMIT", 100),
        discord_bot_token=get_setting("DISCORD_BOT_TOKEN"),
        discord_channel_ids=get_csv_setting("DISCORD_CHANNEL_IDS"),
        discord_message_limit=get_int_setting("DISCORD_MESSAGE_LIMIT", 100),
    )
