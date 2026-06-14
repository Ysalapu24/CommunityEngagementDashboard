"""Load local demo messages."""

from __future__ import annotations

import json
from pathlib import Path

from src.models import ensure_message_dict


def load_demo_messages(path: str | Path = "data/demo_messages.json") -> list[dict]:
    demo_path = Path(path)
    with demo_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    messages = payload.get("messages", payload)
    return [ensure_message_dict(message) for message in messages]
