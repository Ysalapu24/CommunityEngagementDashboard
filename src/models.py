"""Normalized message model used across all data sources."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Message:
    platform: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    text: str
    timestamp: str
    reactions: list[dict[str, Any]] = field(default_factory=list)
    thread_count: int = 0
    reply_count: int = 0
    url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_timestamp(value: Any) -> str:
    """Return an ISO-8601 UTC timestamp string from common API timestamp shapes."""
    if value in (None, ""):
        return datetime.now(timezone.utc).isoformat()

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()

    text = str(value)
    try:
        return datetime.fromtimestamp(float(text), tz=timezone.utc).isoformat()
    except ValueError:
        pass

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return datetime.now(timezone.utc).isoformat()

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def ensure_message_dict(message: dict[str, Any]) -> dict[str, Any]:
    """Fill missing normalized schema keys for user-provided or API messages."""
    return Message(
        platform=str(message.get("platform", "unknown")),
        channel_id=str(message.get("channel_id", "")),
        channel_name=str(message.get("channel_name", "Unknown")),
        user_id=str(message.get("user_id", "")),
        user_name=str(message.get("user_name", "Unknown")),
        text=str(message.get("text", "")),
        timestamp=normalize_timestamp(message.get("timestamp")),
        reactions=list(message.get("reactions") or []),
        thread_count=int(message.get("thread_count") or 0),
        reply_count=int(message.get("reply_count") or 0),
        url=str(message.get("url") or message.get("permalink") or ""),
    ).to_dict()
