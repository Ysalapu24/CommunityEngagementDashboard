"""Reusable Streamlit UI components."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render_kpis(metrics: dict) -> None:
    columns = st.columns(5)
    columns[0].metric("Health Score", f"{metrics['health_score']}/100")
    columns[1].metric("Avg Sentiment", metrics["average_sentiment"])
    columns[2].metric("Messages", metrics["total_messages"])
    columns[3].metric("Active Users", metrics["active_users"])
    columns[4].metric("Burnout Signals", metrics["burnout_risk_count"])


def render_charts(
    daily_sentiment: pd.DataFrame,
    channel_sentiment: pd.DataFrame,
    volume_by_day: pd.DataFrame,
    platform_df: pd.DataFrame,
    filtered_df: pd.DataFrame,
) -> None:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.line(daily_sentiment, x="date", y="sentiment_score", markers=True, title="Daily Sentiment Trend")
        )
        st.plotly_chart(
            px.bar(volume_by_day, x="date", y="messages", title="Message Volume by Day")
        )
        label_counts = filtered_df["sentiment_label"].value_counts().reset_index()
        label_counts.columns = ["sentiment_label", "messages"]
        st.plotly_chart(
            px.pie(label_counts, names="sentiment_label", values="messages", title="Sentiment Label Distribution")
        )
    with right:
        st.plotly_chart(
            px.bar(channel_sentiment, x="channel_name", y="sentiment_score", color="sentiment_score", title="Sentiment by Channel")
        )
        st.plotly_chart(
            px.bar(platform_df, x="platform", y="messages", color="avg_sentiment", title="Platform Comparison")
        )


def render_insight_cards(insights: dict[str, list[str]]) -> None:
    st.subheader("Insights")
    columns = st.columns(3)
    sections = [
        ("What is going well", insights["what_is_going_well"]),
        ("Needs attention", insights["needs_attention"]),
        ("Recommended actions", insights["recommended_actions"]),
    ]
    for column, (title, items) in zip(columns, sections):
        with column:
            st.markdown(f"**{title}**")
            for item in items:
                st.write(f"- {item}")

    if insights.get("burnout_warnings"):
        st.warning("Burnout warnings")
        for item in insights["burnout_warnings"]:
            st.write(f"- {item}")

    if insights.get("channel_notes"):
        st.info("Channel notes")
        for item in insights["channel_notes"]:
            st.write(f"- {item}")

    st.markdown("**Top 3 action items**")
    for item in insights["top_action_items"]:
        st.write(f"- {item}")
