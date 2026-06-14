"""Slack API ingestion and normalization."""

from __future__ import annotations

from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.config import load_settings
from src.models import Message, normalize_timestamp


def _reaction_list(raw_reactions: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    reactions = []
    for reaction in raw_reactions or []:
        reactions.append(
            {
                "name": reaction.get("name", ""),
                "count": int(reaction.get("count") or 0),
            }
        )
    return reactions


def _normalize_slack_message(
    message: dict[str, Any],
    channel_id: str,
    channel_name: str,
    user_names: dict[str, str],
) -> dict[str, Any]:
    user_id = str(message.get("user") or message.get("bot_id") or "unknown")
    return Message(
        platform="Slack",
        channel_id=channel_id,
        channel_name=channel_name,
        user_id=user_id,
        user_name=user_names.get(user_id, user_id),
        text=str(message.get("text", "")),
        timestamp=normalize_timestamp(message.get("ts")),
        reactions=_reaction_list(message.get("reactions")),
        thread_count=int(message.get("reply_count") or 0),
        reply_count=int(message.get("reply_count") or 0),
        url="",
    ).to_dict()


def _channel_name(client: WebClient, channel_id: str) -> str:
    try:
        response = client.conversations_info(channel=channel_id)
        return response.get("channel", {}).get("name", channel_id)
    except SlackApiError:
        return channel_id


def _user_names(client: WebClient, user_ids: set[str]) -> dict[str, str]:
    names: dict[str, str] = {}
    for user_id in user_ids:
        if not user_id or user_id == "unknown":
            continue
        try:
            response = client.users_info(user=user_id)
            user = response.get("user", {})
            names[user_id] = user.get("profile", {}).get("display_name") or user.get("real_name") or user_id
        except SlackApiError:
            names[user_id] = user_id
    return names


def fetch_slack_messages() -> tuple[list[dict[str, Any]], list[str]]:
    """Fetch normalized Slack messages. Returns (messages, warnings)."""
    settings = load_settings()
    warnings: list[str] = []
    if not settings.slack_bot_token:
        return [], ["Slack token is missing. Add SLACK_BOT_TOKEN to enable Slack API mode."]
    if not settings.slack_channel_ids:
        return [], ["No Slack channels configured. Add SLACK_CHANNEL_IDS to enable Slack API mode."]

    client = WebClient(token=settings.slack_bot_token)
    normalized: list[dict[str, Any]] = []

    for channel_id in settings.slack_channel_ids:
        try:
            response = client.conversations_history(channel=channel_id, limit=settings.slack_message_limit)
            raw_messages = response.get("messages", [])
        except SlackApiError as exc:
            error = exc.response.get("error", "unknown_error") if exc.response else "unknown_error"
            warnings.append(f"Slack channel {channel_id} could not be loaded: {error}")
            continue

        channel_name = _channel_name(client, channel_id)
        user_ids = {str(message.get("user", "")) for message in raw_messages if message.get("user")}
        user_names = _user_names(client, user_ids)

        for message in raw_messages:
            normalized.append(_normalize_slack_message(message, channel_id, channel_name, user_names))

            if settings.slack_fetch_threads and message.get("thread_ts") and message.get("reply_count"):
                try:
                    replies = client.conversations_replies(channel=channel_id, ts=message["thread_ts"]).get("messages", [])
                except SlackApiError as exc:
                    error = exc.response.get("error", "unknown_error") if exc.response else "unknown_error"
                    warnings.append(f"Slack thread in {channel_id} could not be loaded: {error}")
                    continue
                reply_names = _user_names(client, {str(reply.get("user", "")) for reply in replies if reply.get("user")})
                for reply in replies[1:]:
                    normalized.append(_normalize_slack_message(reply, channel_id, channel_name, reply_names))

    return normalized, warnings
