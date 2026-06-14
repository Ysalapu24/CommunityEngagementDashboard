"""Aggregate engagement and health metrics."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _pct(part: int, whole: int) -> float:
    return round((part / whole) * 100, 1) if whole else 0.0


def calculate_metrics(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "total_messages": 0,
            "active_users": 0,
            "active_channels": 0,
            "average_sentiment": 0.0,
            "health_score": 50,
            "positive_pct": 0.0,
            "negative_pct": 0.0,
            "burnout_risk_count": 0,
            "burnout_risk_users": [],
            "most_positive_channel": "N/A",
            "most_negative_channel": "N/A",
        }

    total = len(df)
    positive_count = int((df["sentiment_label"] == "positive").sum())
    negative_count = int((df["sentiment_label"] == "negative").sum())
    burnout_count = int(df["burnout_signal"].sum())
    average_sentiment = float(df["sentiment_score"].mean())
    health_score = round(max(0, min(100, 65 + average_sentiment * 30 + _pct(positive_count, total) * 0.25 - _pct(negative_count, total) * 0.4 - burnout_count * 3)))

    channel_sentiment = df.groupby("channel_name")["sentiment_score"].mean().sort_values()

    return {
        "total_messages": total,
        "active_users": int(df["user_id"].nunique()),
        "active_channels": int(df["channel_id"].nunique()),
        "average_sentiment": round(average_sentiment, 3),
        "health_score": int(health_score),
        "positive_pct": _pct(positive_count, total),
        "negative_pct": _pct(negative_count, total),
        "burnout_risk_count": burnout_count,
        "burnout_risk_users": sorted(df.loc[df["burnout_signal"], "user_name"].dropna().unique().tolist()),
        "most_positive_channel": channel_sentiment.index[-1] if not channel_sentiment.empty else "N/A",
        "most_negative_channel": channel_sentiment.index[0] if not channel_sentiment.empty else "N/A",
    }


def sentiment_by_day(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "sentiment_score"])
    return df.groupby("date", as_index=False)["sentiment_score"].mean()


def sentiment_by_channel(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["channel_name", "sentiment_score", "messages"])
    grouped = df.groupby("channel_name").agg(sentiment_score=("sentiment_score", "mean"), messages=("text", "count")).reset_index()
    grouped["sentiment_score"] = grouped["sentiment_score"].round(3)
    return grouped.sort_values("sentiment_score", ascending=False)


def message_volume_by_day(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "messages"])
    return df.groupby("date").size().reset_index(name="messages")


def platform_comparison(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["platform", "messages", "avg_sentiment", "burnout_signals"])
    return (
        df.groupby("platform")
        .agg(messages=("text", "count"), avg_sentiment=("sentiment_score", "mean"), burnout_signals=("burnout_signal", "sum"))
        .reset_index()
        .round({"avg_sentiment": 3})
    )


def channel_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["channel_name", "messages", "active_users", "avg_sentiment", "negative_pct", "burnout_signals"])
    summary = (
        df.groupby("channel_name")
        .agg(
            messages=("text", "count"),
            active_users=("user_id", "nunique"),
            avg_sentiment=("sentiment_score", "mean"),
            negative_count=("sentiment_label", lambda values: (values == "negative").sum()),
            burnout_signals=("burnout_signal", "sum"),
        )
        .reset_index()
    )
    summary["negative_pct"] = summary.apply(lambda row: _pct(int(row["negative_count"]), int(row["messages"])), axis=1)
    return summary.drop(columns=["negative_count"]).round({"avg_sentiment": 3})
