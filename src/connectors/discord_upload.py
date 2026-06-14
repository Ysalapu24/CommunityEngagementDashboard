"""Local Discord data package upload parsing."""

from __future__ import annotations

import json
import zipfile
from io import BytesIO
from typing import Any, Iterable

from src.models import Message, normalize_timestamp


def parse_discord_uploads(uploaded_files: Iterable[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse uploaded Discord JSON files or ZIP packages into normalized messages."""
    messages: list[dict[str, Any]] = []
    warnings: list[str] = []

    for uploaded_file in uploaded_files or []:
        name = getattr(uploaded_file, "name", "uploaded-file")
        try:
            raw_bytes = uploaded_file.getvalue()
        except AttributeError:
            raw_bytes = uploaded_file.read()

        if name.lower().endswith(".zip"):
            zip_messages, zip_warnings = _parse_zip(raw_bytes, name)
            messages.extend(zip_messages)
            warnings.extend(zip_warnings)
        elif name.lower().endswith(".json"):
            json_messages, json_warnings = _parse_json_bytes(raw_bytes, name)
            messages.extend(json_messages)
            warnings.extend(json_warnings)
        else:
            warnings.append(f"{name} was skipped because only .zip and .json uploads are supported.")

    if not messages:
        warnings.append("No Discord messages were found in the uploaded files.")

    return messages, warnings


def _parse_zip(raw_bytes: bytes, source_name: str) -> tuple[list[dict[str, Any]], list[str]]:
    messages: list[dict[str, Any]] = []
    warnings: list[str] = []
    try:
        with zipfile.ZipFile(BytesIO(raw_bytes)) as archive:
            for member in archive.namelist():
                if member.endswith("/") or not member.lower().endswith(".json"):
                    continue
                try:
                    with archive.open(member) as handle:
                        member_messages, member_warnings = _parse_json_payload(json.load(handle), f"{source_name}:{member}")
                except (json.JSONDecodeError, UnicodeDecodeError, zipfile.BadZipFile):
                    warnings.append(f"{member} in {source_name} was skipped because it is not valid JSON.")
                    continue
                messages.extend(member_messages)
                warnings.extend(member_warnings)
    except zipfile.BadZipFile:
        warnings.append(f"{source_name} is not a valid ZIP file.")
    return messages, warnings


def _parse_json_bytes(raw_bytes: bytes, source_name: str) -> tuple[list[dict[str, Any]], list[str]]:
    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return [], [f"{source_name} was skipped because it is not valid UTF-8 JSON."]
    return _parse_json_payload(payload, source_name)


def _parse_json_payload(payload: Any, source_name: str) -> tuple[list[dict[str, Any]], list[str]]:
    records = _extract_records(payload)
    messages = [_normalize_uploaded_record(record, source_name) for record in records if _looks_like_message(record)]
    warnings: list[str] = []
    if records and not messages:
        warnings.append(f"{source_name} did not contain recognizable Discord message records.")
    return messages, warnings


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        for key in ("messages", "Messages", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        if _looks_like_message(payload):
            return [payload]

    return []


def _looks_like_message(record: dict[str, Any]) -> bool:
    keys = {key.lower() for key in record.keys()}
    return bool(keys & {"content", "text", "message", "timestamp", "timestamp edited", "id"})


def _normalize_uploaded_record(record: dict[str, Any], source_name: str) -> dict[str, Any]:
    author = record.get("author") or record.get("Author") or {}
    if isinstance(author, dict):
        user_id = str(author.get("id") or author.get("ID") or author.get("username") or author.get("Username") or "discord-export-user")
        user_name = str(author.get("global_name") or author.get("username") or author.get("Username") or author.get("name") or "Discord Export User")
    else:
        user_id = str(author or record.get("user_id") or record.get("User ID") or "discord-export-user")
        user_name = str(author or record.get("user_name") or record.get("User") or "Discord Export User")

    channel_id = str(record.get("channel_id") or record.get("Channel ID") or _source_channel_id(source_name))
    channel_name = str(record.get("channel_name") or record.get("Channel Name") or _source_channel_name(source_name))
    text = str(record.get("content") or record.get("Content") or record.get("text") or record.get("Text") or record.get("message") or "")
    timestamp = record.get("timestamp") or record.get("Timestamp") or record.get("Date") or record.get("date")

    return Message(
        platform="Discord Upload",
        channel_id=channel_id,
        channel_name=channel_name,
        user_id=user_id,
        user_name=user_name,
        text=text,
        timestamp=normalize_timestamp(timestamp),
        reactions=_normalize_reactions(record.get("reactions") or record.get("Reactions")),
        thread_count=0,
        reply_count=0,
        url=str(record.get("url") or record.get("URL") or ""),
    ).to_dict()


def _source_channel_id(source_name: str) -> str:
    parts = [part for part in source_name.replace("\\", "/").split("/") if part]
    return parts[-2] if len(parts) >= 2 else "discord-upload"


def _source_channel_name(source_name: str) -> str:
    channel_id = _source_channel_id(source_name)
    return channel_id.replace("_", " ").replace("-", " ")


def _normalize_reactions(raw_reactions: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_reactions, list):
        return []

    reactions: list[dict[str, Any]] = []
    for reaction in raw_reactions:
        if isinstance(reaction, dict):
            emoji = reaction.get("emoji", {})
            reactions.append(
                {
                    "name": str(emoji.get("name") if isinstance(emoji, dict) else reaction.get("name") or reaction.get("emoji") or ""),
                    "count": int(reaction.get("count") or reaction.get("Count") or 1),
                }
            )
        elif isinstance(reaction, str):
            reactions.append({"name": reaction, "count": 1})
    return reactions
