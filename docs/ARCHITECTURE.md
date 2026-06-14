# Architecture

## Goal

The dashboard measures engagement, sentiment, stress, support requests, and burnout-risk signals across Slack, authorized Discord server channels, personal Discord exports, or demo data.

## Flow

```text
Demo JSON / Slack API / Discord Bot API / Discord Upload
        |
        v
Normalized message schema
        |
        v
Sentiment and rule-based enrichment
        |
        v
Metrics, charts, tables, and template insights
        |
        v
Streamlit dashboard and CSV export
```

## Modules

- `app.py`: Streamlit entry point, data-source selection, filters, and page layout.
- `src/config.py`: Reads Streamlit secrets first, then `.env` and environment variables.
- `src/models.py`: Defines the normalized `Message` model and timestamp normalization.
- `src/connectors/demo_loader.py`: Loads `data/demo_messages.json`.
- `src/connectors/slack_client.py`: Fetches Slack channel history and optional thread replies.
- `src/connectors/discord_client.py`: Fetches authorized Discord server channel messages through the official bot REST API.
- `src/connectors/discord_upload.py`: Parses uploaded Discord Data Package ZIP or JSON files locally for Personal Discord Conversation Analytics.
- `src/analysis/sentiment.py`: Runs VADER sentiment and local keyword rules.
- `src/analysis/metrics.py`: Computes dashboard KPIs and chart-ready aggregates.
- `src/analysis/insights.py`: Produces manager/moderator insight cards without an LLM.
- `src/ui/components.py`: Reusable KPI, chart, and insight rendering functions.

## Normalized Message Schema

Every connector returns dictionaries with these fields:

- `platform`
- `channel_id`
- `channel_name`
- `user_id`
- `user_name`
- `text`
- `timestamp`
- `reactions`
- `thread_count`
- `reply_count`
- `url`

## Analysis Approach

The app intentionally avoids paid AI services. It combines:

- VADER compound sentiment score from `-1` to `1`
- Sentiment labels: positive, neutral, negative
- Rule-based emotion labels: celebration, stress, blocked, conflict, support, neutral
- Stress keyword matching
- Positive keyword matching
- Reaction scoring
- Burnout-risk flags for high-stress language

## Deployment Shape

The app is self-contained in `CommunityEngagementDashboard/`. From the current Buildathon repository, Streamlit Community Cloud should point to:

```text
CommunityEngagementDashboard/app.py
```

## Discord Ingestion Safety Model

### Demo Data Mode

Demo Data mode uses `data/demo_messages.json` for local testing and public demos. It does not require any Discord access.

### Discord Authorized Server Mode

Authorized Server Mode uses only the official Discord bot API:

```text
GET https://discord.com/api/v10/channels/{channel_id}/messages
```

It requires:

- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_IDS`
- `DISCORD_MESSAGE_LIMIT`
- Message Content Intent if message text is needed
- View Channel permission
- Read Message History permission

The user does not need to be the creator of a server, but the bot must be invited and granted access to selected channels. The app cannot analyze random servers just because a personal Discord account joined them.

Invalid tokens, missing permissions, missing message content, rate limits, and unreadable channels are reported as warnings so the app does not crash.

### Discord Data Package Upload Mode

The mode named `Personal Discord Conversation Analytics` lets a user upload their own Discord Data Package ZIP or JSON files. The parser runs locally and converts recognizable message records into the common message schema.

This mode is not labeled as community engagement because uploaded files may represent personal history or private conversations rather than a server community.

A Discord bot cannot read private DMs between two users unless the bot is actually part of the conversation, which normal personal DMs are not. For personal message history, use Discord Data Package upload instead.

The project does not implement or suggest user-token scraping, self-bots, automating a normal Discord user account, reading private DMs through a bot, or scraping servers just because the user personally joined them.
