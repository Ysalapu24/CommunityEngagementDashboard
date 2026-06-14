"""Discord REST API ingestion and normalization."""

from __future__ import annotations

from typing import Any

import requests

from src.config import load_settings
from src.models import Message, normalize_timestamp


def _reaction_list(raw_reactions: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    reactions = []
    for reaction in raw_reactions or []:
        emoji = reaction.get("emoji", {})
        reactions.append(
            {
                "name": emoji.get("name", ""),
                "count": int(reaction.get("count") or 0),
            }
        )
    return reactions


def _normalize_discord_message(message: dict[str, Any], channel_id: str) -> dict[str, Any]:
    author = message.get("author", {})
    return Message(
        platform="Discord",
        channel_id=channel_id,
        channel_name=message.get("channel_name", channel_id),
        user_id=str(author.get("id", "unknown")),
        user_name=str(author.get("global_name") or author.get("username") or "Unknown"),
        text=str(message.get("content", "")),
        timestamp=normalize_timestamp(message.get("timestamp")),
        reactions=_reaction_list(message.get("reactions")),
        thread_count=0,
        reply_count=0,
        url=f"https://discord.com/channels/@me/{channel_id}/{message.get('id', '')}",
    ).to_dict()


def fetch_discord_messages() -> tuple[list[dict[str, Any]], list[str]]:
    """Fetch normalized Discord messages. Returns (messages, warnings)."""
    settings = load_settings()
    warnings: list[str] = []
    if not settings.discord_bot_token:
        return [], ["Discord token is missing. Add DISCORD_BOT_TOKEN to enable Discord API mode."]
    if not settings.discord_channel_ids:
        return [], ["No Discord channels configured. Add DISCORD_CHANNEL_IDS to enable Discord API mode."]

    headers = {"Authorization": f"Bot {settings.discord_bot_token}"}
    messages: list[dict[str, Any]] = []

    for channel_id in settings.discord_channel_ids:
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        try:
            response = requests.get(
                url,
                headers=headers,
                params={"limit": settings.discord_message_limit},
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            status = getattr(exc.response, "status_code", None) if getattr(exc, "response", None) is not None else None
            if status == 401:
                detail = "invalid bot token"
            elif status == 403:
                detail = "missing View Channel or Read Message History permission"
            elif status == 404:
                detail = "channel not found or bot is not authorized for it"
            elif status == 429:
                detail = "rate limited by Discord"
            else:
                detail = str(exc)
            warnings.append(f"Discord channel {channel_id} could not be loaded: {detail}")
            continue
        except ValueError:
            warnings.append(f"Discord channel {channel_id} returned invalid JSON.")
            continue

        for message in payload:
            normalized = _normalize_discord_message(message, channel_id)
            if not normalized["text"]:
                warnings.append(
                    f"Discord channel {channel_id} returned a message without content. Enable Message Content Intent if text analysis is needed."
                )
            messages.append(normalized)

    return messages, warnings
