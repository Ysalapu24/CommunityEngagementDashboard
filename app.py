from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.insights import generate_insights
from src.analysis.metrics import (
    calculate_metrics,
    channel_summary,
    message_volume_by_day,
    platform_comparison,
    sentiment_by_channel,
    sentiment_by_day,
)
from src.analysis.sentiment import enrich_messages
from src.connectors.demo_loader import load_demo_messages
from src.connectors.discord_client import fetch_discord_messages
from src.connectors.discord_upload import parse_discord_uploads
from src.connectors.slack_client import fetch_slack_messages
from src.ui.components import render_charts, render_insight_cards, render_kpis


st.set_page_config(
    page_title="Team & Community Engagement Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_messages(data_source: str) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    if data_source == "Demo Data":
        return load_demo_messages(ROOT / "data" / "demo_messages.json"), warnings

    if data_source == "Slack API":
        return fetch_slack_messages()

    if data_source == "Discord API":
        return fetch_discord_messages()

    if data_source == "Combined Slack + Discord":
        slack_messages, slack_warnings = fetch_slack_messages()
        discord_messages, discord_warnings = fetch_discord_messages()
        messages = slack_messages + discord_messages
        warnings = slack_warnings + discord_warnings
        if not messages:
            fallback = load_demo_messages(ROOT / "data" / "demo_messages.json")
            warnings.append("No API messages loaded, so demo messages are shown as a safe fallback.")
            return fallback, warnings
        return messages, warnings

    return load_demo_messages(ROOT / "data" / "demo_messages.json"), warnings


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()

    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    platforms = st.sidebar.multiselect("Platform", sorted(df["platform"].dropna().unique()), default=sorted(df["platform"].dropna().unique()))
    channels = st.sidebar.multiselect("Channel", sorted(df["channel_name"].dropna().unique()), default=sorted(df["channel_name"].dropna().unique()))
    users = st.sidebar.multiselect("User/member", sorted(df["user_name"].dropna().unique()), default=sorted(df["user_name"].dropna().unique()))

    filtered = df.copy()
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[(filtered["timestamp"].dt.date >= start) & (filtered["timestamp"].dt.date <= end)]
    if platforms:
        filtered = filtered[filtered["platform"].isin(platforms)]
    if channels:
        filtered = filtered[filtered["channel_name"].isin(channels)]
    if users:
        filtered = filtered[filtered["user_name"].isin(users)]

    return filtered


def main() -> None:
    st.title("Team & Community Engagement Dashboard")

    st.sidebar.header("Configuration")
    data_source = st.sidebar.selectbox(
        "Data source",
        [
            "Demo Data",
            "Slack API",
            "Discord API",
            "Combined Slack + Discord",
            "Personal Discord Conversation Analytics",
        ],
        index=0,
    )
    uploaded_files = []
    if data_source == "Personal Discord Conversation Analytics":
        st.sidebar.caption("Upload your own Discord Data Package ZIP or JSON message files. Files are parsed locally.")
        uploaded_files = st.sidebar.file_uploader(
            "Discord ZIP or JSON files",
            type=["zip", "json"],
            accept_multiple_files=True,
        )

    if st.sidebar.button("Refresh / Load", width="stretch"):
        load_messages.clear()

    if data_source == "Personal Discord Conversation Analytics":
        messages, warnings = parse_discord_uploads(uploaded_files)
    else:
        messages, warnings = load_messages(data_source)
    df = enrich_messages(messages)

    for warning in warnings:
        st.sidebar.warning(warning)

    filtered_df = apply_filters(df)
    metrics = calculate_metrics(filtered_df)

    if filtered_df.empty:
        st.warning("No messages match the current filters.")
        return

    render_kpis(metrics)

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Export filtered CSV",
        data=csv,
        file_name="community_engagement_messages.csv",
        mime="text/csv",
    )

    render_insight_cards(generate_insights(filtered_df, metrics))

    st.subheader("Charts")
    render_charts(
        sentiment_by_day(filtered_df),
        sentiment_by_channel(filtered_df),
        message_volume_by_day(filtered_df),
        platform_comparison(filtered_df),
        filtered_df,
    )

    st.subheader("Risk Review")
    risk_columns = ["platform", "channel_name", "user_name", "timestamp", "sentiment_score", "emotion_label", "stress_keywords_text", "text"]
    st.dataframe(
        filtered_df.sort_values(["burnout_signal", "sentiment_score"], ascending=[False, True])[risk_columns].head(25),
        width="stretch",
        hide_index=True,
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Burnout-Risk Users")
        burnout_users = (
            filtered_df[filtered_df["burnout_signal"]]
            .groupby("user_name")
            .agg(risk_messages=("text", "count"), channels=("channel_name", lambda values: ", ".join(sorted(set(values)))))
            .reset_index()
        )
        st.dataframe(burnout_users, width="stretch", hide_index=True)
    with right:
        st.subheader("Channel Summary")
        st.dataframe(channel_summary(filtered_df), width="stretch", hide_index=True)

    st.subheader("Raw Normalized Messages")
    raw_columns = [
        "platform",
        "channel_id",
        "channel_name",
        "user_id",
        "user_name",
        "text",
        "timestamp",
        "reactions_text",
        "thread_count",
        "reply_count",
        "url",
        "sentiment_label",
        "emotion_label",
        "burnout_signal",
    ]
    st.dataframe(filtered_df[raw_columns], width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
