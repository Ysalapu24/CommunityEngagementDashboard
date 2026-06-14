"""Template-driven insights without external AI services."""

from __future__ import annotations

import pandas as pd


def generate_insights(df: pd.DataFrame, metrics: dict) -> dict[str, list[str]]:
    if df.empty:
        return {
            "what_is_going_well": ["No messages loaded yet. Use Demo Data or connect Slack/Discord to generate insights."],
            "needs_attention": ["Load messages before making engagement decisions."],
            "recommended_actions": ["Start with Demo Data to confirm the dashboard is working."],
            "burnout_warnings": [],
            "channel_notes": [],
            "top_action_items": ["Load data", "Review filters", "Export findings for follow-up"],
        }

    positive_channels = df.groupby("channel_name")["sentiment_score"].mean().sort_values(ascending=False)
    burnout_df = df[df["burnout_signal"]]
    negative_df = df[df["sentiment_label"] == "negative"]

    going_well = [
        f"{metrics['positive_pct']}% of messages are positive, with strongest tone in {metrics['most_positive_channel']}.",
        f"{metrics['active_users']} people are active across {metrics['active_channels']} channels.",
    ]
    if "celebration" in set(df["emotion_label"]):
        going_well.append("Celebration and progress signals are present, which is useful for morale and demo storytelling.")

    needs_attention = []
    if metrics["negative_pct"] > 20:
        needs_attention.append(f"Negative sentiment is elevated at {metrics['negative_pct']}% of messages.")
    if not negative_df.empty:
        top_negative_channel = negative_df["channel_name"].value_counts().index[0]
        needs_attention.append(f"{top_negative_channel} has the highest concentration of negative messages.")
    if metrics["burnout_risk_count"]:
        needs_attention.append(f"{metrics['burnout_risk_count']} burnout-risk messages need manager or moderator review.")
    if not needs_attention:
        needs_attention.append("No major risk cluster is visible in the current filters.")

    recommended_actions = [
        "Review the highest-risk messages before the next team or community check-in.",
        "Assign unblocker support where messages mention blocked, stuck, deadline, or confused.",
        "Share wins from the most positive channel to reinforce healthy momentum.",
    ]

    burnout_warnings = []
    for _, row in burnout_df.head(5).iterrows():
        burnout_warnings.append(
            f"{row['user_name']} in #{row['channel_name']} mentioned {row['stress_keywords_text'] or 'stress'}: {row['text'][:140]}"
        )

    channel_notes = []
    for channel, score in positive_channels.items():
        channel_df = df[df["channel_name"] == channel]
        top_terms = sorted({term for terms in channel_df["stress_keywords"] for term in terms})
        if score < -0.1:
            channel_notes.append(f"#{channel}: sentiment is low; watch {', '.join(top_terms) if top_terms else 'recent blockers'}.")
        elif score > 0.25:
            channel_notes.append(f"#{channel}: positive momentum is strong; preserve what is working here.")

    if burnout_df.empty:
        top_action_items = ["Keep monitoring trend changes", "Celebrate shipped work", "Check channels with low reply activity"]
    else:
        top_action_items = [
            "Follow up with burnout-risk users privately",
            "Clarify urgent deadlines and owners",
            "Create an unblocker thread for stuck work",
        ]

    return {
        "what_is_going_well": going_well,
        "needs_attention": needs_attention,
        "recommended_actions": recommended_actions,
        "burnout_warnings": burnout_warnings,
        "channel_notes": channel_notes[:5],
        "top_action_items": top_action_items[:3],
    }
