"""Reusable Streamlit UI components — dark mode with neon accents."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Neon color palette
NEON_GREEN = "#00ff88"
NEON_BLUE = "#00cfff"
NEON_PINK = "#ff2d9b"
NEON_YELLOW = "#ffe600"
NEON_PURPLE = "#b347ff"
BG_DARK = "#0a0a0f"
BG_CARD = "#12121a"
BG_CARD2 = "#1a1a2e"

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(color="#e0e0e0", family="sans-serif"),
        xaxis=dict(gridcolor="#1e1e2e", linecolor="#333"),
        yaxis=dict(gridcolor="#1e1e2e", linecolor="#333"),
        legend=dict(bgcolor=BG_CARD, bordercolor="#333"),
    )
)

DARK_CSS = """
<style>
/* Base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0f !important;
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] {
    background-color: #0d0d16 !important;
    border-right: 1px solid #00ff8833;
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }

/* Header */
.dash-header {
    background: linear-gradient(135deg, #0d0d16 0%, #1a0a2e 100%);
    border-bottom: 2px solid #00ff88;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border-radius: 0 0 12px 12px;
}
.dash-header h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00ff88, #00cfff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.dash-header p {
    color: #888;
    margin: 0.25rem 0 0 0;
    font-size: 0.9rem;
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: linear-gradient(135deg, #12121a, #1a1a2e);
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}
.kpi-card.green::before { background: #00ff88; }
.kpi-card.blue::before { background: #00cfff; }
.kpi-card.pink::before { background: #ff2d9b; }
.kpi-card.yellow::before { background: #ffe600; }
.kpi-card.purple::before { background: #b347ff; }
.kpi-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
.kpi-value {
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.kpi-card.green .kpi-value { color: #00ff88; }
.kpi-card.blue .kpi-value { color: #00cfff; }
.kpi-card.pink .kpi-value { color: #ff2d9b; }
.kpi-card.yellow .kpi-value { color: #ffe600; }
.kpi-card.purple .kpi-value { color: #b347ff; }
.kpi-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }

/* Insight Cards */
.insight-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}
.insight-card {
    background: #12121a;
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 1.25rem;
}
.insight-card h4 {
    margin: 0 0 0.75rem 0;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.insight-card.green h4 { color: #00ff88; }
.insight-card.blue h4 { color: #00cfff; }
.insight-card.yellow h4 { color: #ffe600; }
.insight-card ul { margin: 0; padding-left: 1rem; }
.insight-card li { font-size: 0.85rem; color: #ccc; margin-bottom: 0.4rem; line-height: 1.4; }

/* Activity Feed */
.feed-container {
    background: #12121a;
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 1rem;
    max-height: 400px;
    overflow-y: auto;
}
.feed-item {
    display: flex;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1e1e2e;
    align-items: flex-start;
}
.feed-item:last-child { border-bottom: none; }
.feed-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}
.feed-dot.positive { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
.feed-dot.negative { background: #ff2d9b; box-shadow: 0 0 6px #ff2d9b; }
.feed-dot.neutral { background: #888; }
.feed-dot.burnout { background: #ffe600; box-shadow: 0 0 6px #ffe600; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.feed-user { font-size: 0.75rem; color: #00cfff; font-weight: 600; }
.feed-channel { font-size: 0.7rem; color: #555; }
.feed-text { font-size: 0.82rem; color: #ccc; margin-top: 0.15rem; line-height: 1.4; }

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1.5rem 0 1rem 0;
}
.section-header h3 {
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #00ff88;
    margin: 0;
}
.section-header .line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #00ff8833, transparent);
}

/* Warning/burnout box */
.burnout-box {
    background: linear-gradient(135deg, #1a0a00, #1a1200);
    border: 1px solid #ffe60044;
    border-left: 3px solid #ffe600;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.83rem;
    color: #ccc;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #12121a; }
::-webkit-scrollbar-thumb { background: #00ff8844; border-radius: 3px; }

/* Streamlit overrides */
[data-testid="metric-container"] {
    background: #12121a !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
div[data-testid="stExpander"] {
    background: #12121a !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 12px !important;
}
.stButton button {
    background: linear-gradient(135deg, #00ff88, #00cfff) !important;
    color: #000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
}
.stDownloadButton button {
    background: #1a1a2e !important;
    color: #00ff88 !important;
    border: 1px solid #00ff8844 !important;
    border-radius: 8px !important;
}
</style>
"""


def inject_css() -> None:
    st.markdown(DARK_CSS, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown("""
    <div class="dash-header">
        <h1>⚡ Team & Community Engagement Dashboard</h1>
        <p>Real-time sentiment analysis · Burnout detection · Engagement insights</p>
    </div>
    """, unsafe_allow_html=True)


def _health_color(score: int) -> str:
    if score >= 70:
        return "green"
    if score >= 50:
        return "yellow"
    return "pink"


def render_kpis(metrics: dict) -> None:
    health_color = _health_color(metrics["health_score"])
    burnout_color = "yellow" if metrics["burnout_risk_count"] > 0 else "green"
    sentiment_color = "green" if metrics["average_sentiment"] > 0 else "pink"

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card {health_color}">
            <div class="kpi-icon">🏥</div>
            <div class="kpi-value">{metrics['health_score']}</div>
            <div class="kpi-label">Health Score</div>
        </div>
        <div class="kpi-card {sentiment_color}">
            <div class="kpi-icon">💬</div>
            <div class="kpi-value">{metrics['average_sentiment']}</div>
            <div class="kpi-label">Avg Sentiment</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-icon">📨</div>
            <div class="kpi-value">{metrics['total_messages']}</div>
            <div class="kpi-label">Messages</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-icon">👥</div>
            <div class="kpi-value">{metrics['active_users']}</div>
            <div class="kpi-label">Active Users</div>
        </div>
        <div class="kpi-card {burnout_color}">
            <div class="kpi-icon">🔥</div>
            <div class="kpi-value">{metrics['burnout_risk_count']}</div>
            <div class="kpi-label">Burnout Signals</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_activity_feed(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-header"><h3>⚡ Live Activity Feed</h3><div class="line"></div></div>', unsafe_allow_html=True)

    recent = df.sort_values("timestamp", ascending=False).head(20)
    items_html = ""
    for _, row in recent.iterrows():
        label = str(row.get("sentiment_label", "neutral"))
        is_burnout = bool(row.get("burnout_signal", False))
        dot_class = "burnout" if is_burnout else label
        text = str(row.get("text", ""))[:120]
        user = str(row.get("user_name", "Unknown"))
        channel = str(row.get("channel_name", ""))
        platform = str(row.get("platform", ""))
        emotion = str(row.get("emotion_label", ""))
        badge = "🔥" if is_burnout else ("✨" if label == "positive" else ("⚠️" if label == "negative" else ""))
        items_html += f"""
        <div class="feed-item">
            <div class="feed-dot {dot_class}"></div>
            <div>
                <span class="feed-user">{user}</span>
                <span class="feed-channel"> · #{channel} · {platform} {badge}</span>
                <div class="feed-text">{text}</div>
            </div>
        </div>"""

    st.markdown(f'<div class="feed-container">{items_html}</div>', unsafe_allow_html=True)


def _make_chart(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(color="#e0e0e0"),
        xaxis=dict(gridcolor="#1e1e2e", linecolor="#2a2a3a"),
        yaxis=dict(gridcolor="#1e1e2e", linecolor="#2a2a3a"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor=BG_CARD),
    )
    return fig


def render_charts(
    daily_sentiment: pd.DataFrame,
    channel_sentiment: pd.DataFrame,
    volume_by_day: pd.DataFrame,
    platform_df: pd.DataFrame,
    filtered_df: pd.DataFrame,
) -> None:
    st.markdown('<div class="section-header"><h3>📊 Analytics</h3><div class="line"></div></div>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        fig = px.line(
            daily_sentiment, x="date", y="sentiment_score",
            markers=True, title="Daily Sentiment Trend",
            color_discrete_sequence=[NEON_GREEN],
        )
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.13)")
        st.plotly_chart(_make_chart(fig), use_container_width=True)

        fig2 = px.bar(
            volume_by_day, x="date", y="messages",
            title="Message Volume by Day",
            color_discrete_sequence=[NEON_BLUE],
        )
        st.plotly_chart(_make_chart(fig2), use_container_width=True)

        label_counts = filtered_df["sentiment_label"].value_counts().reset_index()
        label_counts.columns = ["sentiment_label", "messages"]
        fig3 = px.pie(
            label_counts, names="sentiment_label", values="messages",
            title="Sentiment Distribution",
            color_discrete_sequence=[NEON_GREEN, NEON_BLUE, NEON_PINK],
            hole=0.45,
        )
        st.plotly_chart(_make_chart(fig3), use_container_width=True)

    with right:
        fig4 = px.bar(
            channel_sentiment, x="channel_name", y="sentiment_score",
            title="Sentiment by Channel",
            color="sentiment_score",
            color_continuous_scale=[[0, NEON_PINK], [0.5, "#333"], [1, NEON_GREEN]],
        )
        st.plotly_chart(_make_chart(fig4), use_container_width=True)

        fig5 = px.bar(
            platform_df, x="platform", y="messages",
            title="Platform Comparison",
            color="avg_sentiment",
            color_continuous_scale=[[0, NEON_PINK], [0.5, NEON_BLUE], [1, NEON_GREEN]],
            text="messages",
        )
        fig5.update_traces(textposition="outside")
        st.plotly_chart(_make_chart(fig5), use_container_width=True)

        if "emotion_label" in filtered_df.columns:
            emotion_counts = filtered_df["emotion_label"].value_counts().reset_index()
            emotion_counts.columns = ["emotion", "count"]
            fig6 = px.bar(
                emotion_counts, x="count", y="emotion",
                orientation="h", title="Emotion Breakdown",
                color="count",
                color_continuous_scale=[[0, NEON_PURPLE], [1, NEON_GREEN]],
            )
            st.plotly_chart(_make_chart(fig6), use_container_width=True)


def render_insight_cards(insights: dict[str, list[str]]) -> None:
    st.markdown('<div class="section-header"><h3>💡 Insights</h3><div class="line"></div></div>', unsafe_allow_html=True)

    going_well = "".join(f"<li>{i}</li>" for i in insights["what_is_going_well"])
    attention = "".join(f"<li>{i}</li>" for i in insights["needs_attention"])
    actions = "".join(f"<li>{i}</li>" for i in insights["recommended_actions"])

    st.markdown(f"""
    <div class="insight-grid">
        <div class="insight-card green">
            <h4>✅ What's Going Well</h4>
            <ul>{going_well}</ul>
        </div>
        <div class="insight-card blue">
            <h4>⚠️ Needs Attention</h4>
            <ul>{attention}</ul>
        </div>
        <div class="insight-card yellow">
            <h4>🎯 Recommended Actions</h4>
            <ul>{actions}</ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if insights.get("burnout_warnings"):
        st.markdown('<div class="section-header"><h3>🔥 Burnout Warnings</h3><div class="line"></div></div>', unsafe_allow_html=True)
        for item in insights["burnout_warnings"]:
            st.markdown(f'<div class="burnout-box">⚡ {item}</div>', unsafe_allow_html=True)

    if insights.get("channel_notes"):
        st.markdown('<div class="section-header"><h3>📡 Channel Notes</h3><div class="line"></div></div>', unsafe_allow_html=True)
        for item in insights["channel_notes"]:
            st.markdown(f'<div class="burnout-box" style="border-left-color:#00cfff;">{item}</div>', unsafe_allow_html=True)

    if insights.get("top_action_items"):
        cols = st.columns(3)
        for i, item in enumerate(insights["top_action_items"][:3]):
            cols[i].markdown(f"""
            <div class="kpi-card blue" style="text-align:left; padding:1rem;">
                <div style="font-size:0.7rem;color:#888;text-transform:uppercase;margin-bottom:0.4rem;">Action {i+1}</div>
                <div style="font-size:0.85rem;color:#e0e0e0;">{item}</div>
            </div>""", unsafe_allow_html=True)
