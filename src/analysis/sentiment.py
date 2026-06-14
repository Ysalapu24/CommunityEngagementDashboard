"""Rule-based enrichment plus local VADER sentiment analysis."""

from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

STRESS_KEYWORDS = [
    "blocked",
    "stuck",
    "overwhelmed",
    "deadline",
    "tired",
    "burnout",
    "urgent",
    "confused",
    "angry",
    "frustrated",
    "too much",
    "late night",
    "can't keep up",
    "cant keep up",
    "need help",
]

POSITIVE_KEYWORDS = [
    "shipped",
    "solved",
    "great",
    "thanks",
    "appreciate",
    "awesome",
    "launch",
    "fixed",
    "progress",
    "celebrate",
]

POSITIVE_REACTIONS = {"rocket", "tada", "white_check_mark", "raised_hands", "heart", "smile", "clap"}
ATTENTION_REACTIONS = {"eyes", "thinking_face"}
STRESS_REACTIONS = {"warning", "fire", "skull", "tired_face", "face_with_head_bandage"}


def _reaction_score(reactions: list[dict[str, Any]]) -> int:
    score = 0
    for reaction in reactions or []:
        name = str(reaction.get("name", "")).lower()
        count = int(reaction.get("count") or 0)
        if name in POSITIVE_REACTIONS:
            score += count
        elif name in STRESS_REACTIONS:
            score -= count
        elif name in ATTENTION_REACTIONS:
            score += 0
    return score


def _matched_keywords(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in keywords if keyword in lowered]


def _emotion_label(text: str, sentiment_score: float, stress_matches: list[str], positive_matches: list[str]) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["celebrate", "shipped", "launch", "awesome", "great"]):
        return "celebration"
    if any(word in lowered for word in ["help", "support", "thanks", "appreciate"]):
        return "support"
    if any(word in lowered for word in ["blocked", "stuck", "confused"]):
        return "blocked"
    if any(word in lowered for word in ["angry", "frustrated", "disagree", "conflict"]):
        return "conflict"
    if stress_matches:
        return "stress"
    if sentiment_score > 0.35 or positive_matches:
        return "celebration"
    return "neutral"


def enrich_messages(messages: list[dict[str, Any]]) -> pd.DataFrame:
    analyzer = SentimentIntensityAnalyzer()
    rows: list[dict[str, Any]] = []

    for message in messages:
        row = dict(message)
        text = str(row.get("text", ""))
        sentiment_score = analyzer.polarity_scores(text)["compound"]
        stress_matches = _matched_keywords(text, STRESS_KEYWORDS)
        positive_matches = _matched_keywords(text, POSITIVE_KEYWORDS)
        reaction_score = _reaction_score(row.get("reactions", []))

        if sentiment_score >= 0.2:
            sentiment_label = "positive"
        elif sentiment_score <= -0.2:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        burnout_signal = bool(
            any(keyword in stress_matches for keyword in ["burnout", "overwhelmed", "tired", "too much", "late night", "can't keep up", "cant keep up"])
            or (sentiment_score < -0.35 and len(stress_matches) >= 1)
        )

        row.update(
            {
                "sentiment_score": round(sentiment_score, 3),
                "sentiment_label": sentiment_label,
                "emotion_label": _emotion_label(text, sentiment_score, stress_matches, positive_matches),
                "burnout_signal": burnout_signal,
                "stress_keywords": stress_matches,
                "positive_keywords": positive_matches,
                "reaction_score": reaction_score,
            }
        )
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["date"] = df["timestamp"].dt.date
    df["stress_keywords_text"] = df["stress_keywords"].apply(lambda items: ", ".join(items))
    df["reactions_text"] = df["reactions"].apply(_format_reactions)
    return df


def _format_reactions(reactions: list[dict[str, Any]]) -> str:
    counts = Counter()
    for reaction in reactions or []:
        name = str(reaction.get("name", ""))
        if name:
            counts[name] += int(reaction.get("count") or 0)
    return ", ".join(f"{name}: {count}" for name, count in counts.items())
