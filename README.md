# Team & Community Engagement Dashboard

A deployable Streamlit dashboard for analyzing Slack and Discord messages to understand team or community engagement, sentiment, blockers, support needs, and burnout-risk signals.

This project is designed to run locally in VS Code and deploy from GitHub to Streamlit Community Cloud. Demo Data mode works without any API tokens.

## Features

- Demo Data, Slack API, Discord API, Combined Slack + Discord, and Personal Discord Conversation Analytics modes
- Sidebar filters for date range, platform, channel, and user/member
- CSV export for filtered normalized messages
- Local VADER sentiment analysis with rule-based emotion and burnout signals
- KPI cards for health score, average sentiment, message volume, active users, and burnout signals
- Charts for daily sentiment, channel sentiment, message volume, platform comparison, and sentiment label distribution
- Tables for high-risk messages, burnout-risk users, channel summary, and raw normalized messages
- Template-generated manager/moderator insights with no paid APIs

## Architecture

```text
app.py
src/
  config.py
  models.py
  connectors/
    demo_loader.py
    slack_client.py
    discord_client.py
  analysis/
    sentiment.py
    metrics.py
    insights.py
  ui/
    components.py
data/
  demo_messages.json
docs/
  ARCHITECTURE.md
  DEPLOYMENT.md
```

All connectors normalize messages into one schema:

- platform
- channel_id
- channel_name
- user_id
- user_name
- text
- timestamp
- reactions
- thread_count
- reply_count
- url

## Local Setup From VS Code

From the Buildathon folder:

```bash
cd CommunityEngagementDashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

The app opens in Demo Data mode by default.

## GitHub Setup

Right now this folder is a sibling of `Visual Memory Search` inside the Buildathon repo:

```text
Buildathon/
  Visual Memory Search/
  CommunityEngagementDashboard/
```

If you commit from the parent repository folder, this project will be pushed inside that existing GitHub repository. Later, you can split `CommunityEngagementDashboard` into its own repository by copying this folder into a new repo or using Git history filtering.

Typical commands from the Buildathon root:

```bash
git status
git add CommunityEngagementDashboard
git commit -m "Add community engagement dashboard"
git push origin main
```

If your branch is not `main`, replace `main` with the current branch name from `git branch --show-current`.

## Slack API Setup

Create a Slack app, install it to your workspace, and add the bot token to `.env` locally or Streamlit secrets in production.

Required environment variables:

```bash
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL_IDS=C1234567890,C0987654321
SLACK_FETCH_THREADS=false
SLACK_MESSAGE_LIMIT=100
```

Recommended Slack bot scopes:

- `channels:read`
- `channels:history`
- `reactions:read`
- `users:read`

Optional private channel scopes:

- `groups:read`
- `groups:history`

Invite the bot to every channel you want to analyze.

## Discord Bot Setup

The dashboard supports three safe Discord ingestion modes.

### 1. Demo Data Mode

Use `data/demo_messages.json` for local testing, hackathon demos, and public demos. This is the safest option when you do not want to expose real communication data.

### 2. Discord Authorized Server Mode

Use the official Discord bot API only. Create a Discord bot in the Discord Developer Portal, invite it to a server, and give it access to selected channels.

Required environment variables:

```bash
DISCORD_BOT_TOKEN=your-token
DISCORD_CHANNEL_IDS=123456789012345678,234567890123456789
DISCORD_MESSAGE_LIMIT=100
```

The app calls:

```text
GET https://discord.com/api/v10/channels/{channel_id}/messages
```

The bot must have:

- Message Content Intent if message text is needed
- View Channel permission
- Read Message History permission

You do not need to be the creator of a server, but your bot must be invited and granted channel permissions. You cannot analyze random servers just because your personal account joined them.

The app handles missing permissions, missing message content, invalid tokens, and rate limits gracefully. If the bot cannot read a channel, the dashboard shows a warning instead of crashing.

### 3. Personal Discord Conversation Analytics

Use the sidebar mode named `Personal Discord Conversation Analytics` to upload your own Discord Data Package ZIP or JSON message files. Uploaded files are parsed locally and converted into the common message schema.

This mode is for personal Discord history or DM-style analysis. It is intentionally not labeled as community engagement because uploads may represent private conversations rather than a server community.

A bot cannot read private DMs between two users unless the bot is actually part of the conversation, which normal personal DMs are not. For personal message history, use Discord Data Package upload instead.

This project does not implement or suggest user-token scraping, self-bots, automation of a normal Discord user account, reading private DMs through a bot, or scraping servers just because a personal account joined them.

## Streamlit Community Cloud Deployment

1. Push this folder to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the GitHub repo.
4. Set the app path to:

```text
CommunityEngagementDashboard/app.py
```

5. Add secrets in Streamlit Cloud for Slack/Discord if needed.
6. Deploy and test Demo Data mode first.

Example Streamlit secrets:

```toml
SLACK_BOT_TOKEN = ""
SLACK_CHANNEL_IDS = ""
SLACK_FETCH_THREADS = "false"
SLACK_MESSAGE_LIMIT = "100"

DISCORD_BOT_TOKEN = ""
DISCORD_CHANNEL_IDS = ""
DISCORD_MESSAGE_LIMIT = "100"

APP_MODE = "demo"
```

Never commit real `.env` files or `.streamlit/secrets.toml`.

## Troubleshooting

- App imports fail: run `pip install -r requirements.txt` inside the project virtual environment.
- Slack returns `not_in_channel`: invite the bot to the channel.
- Slack returns `missing_scope`: add the scopes listed above and reinstall the app.
- Discord messages have empty text: enable Message Content Intent and confirm channel permissions.
- Discord bot cannot read a channel: confirm the bot was invited and has View Channel and Read Message History permissions.
- Personal Discord upload finds no messages: upload JSON message files directly or a ZIP containing JSON message exports.
- Streamlit Cloud cannot find the app: set the main file path to `CommunityEngagementDashboard/app.py`.
- API mode has no token: switch to Demo Data mode or add secrets.

## Privacy Note

This app analyzes team/community communication data. Use only in workspaces/servers where you have permission. For public demos, use demo data or anonymized exports. Do not expose real user names, tokens, or private messages. For personal Discord history, use the upload mode only with data you have permission to analyze.
