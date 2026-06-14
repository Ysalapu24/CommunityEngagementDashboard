# Deployment Guide

## 1. Create GitHub Repo

For now, this project can live inside the existing Buildathon repository as:

```text
Buildathon/CommunityEngagementDashboard
```

Later, create a separate GitHub repository if you want this app fully independent.

## 2. Clone Repo Locally

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

If you later split it into a new repo, clone that new repo instead.

## 3. Open In VS Code

```bash
code .
```

Open the integrated terminal and move into the app folder:

```bash
cd CommunityEngagementDashboard
```

## 4. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 5. Install Requirements

```bash
pip install -r requirements.txt
```

## 6. Run Locally

```bash
streamlit run app.py
```

Test Demo Data mode first. It does not need tokens.

## 7. Push To GitHub

From the Buildathon repo root:

```bash
git status
git add CommunityEngagementDashboard
git commit -m "Add community engagement dashboard"
git push origin main
```

If the active branch is not `main`, check it with:

```bash
git branch --show-current
```

Then push that branch:

```bash
git push origin YOUR_BRANCH_NAME
```

## 8. Deploy On Streamlit Community Cloud

1. Go to Streamlit Community Cloud.
2. Choose New app.
3. Select the GitHub repository.
4. Set the main file path to:

```text
CommunityEngagementDashboard/app.py
```

5. Deploy.

## 9. Add Secrets In Streamlit Cloud

Open the app settings and add secrets. Start with empty strings if you only want Demo Data mode.

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

Do not commit real secrets.

## 10. Test Demo Mode

In the app sidebar:

1. Select Demo Data.
2. Click Refresh / Load.
3. Confirm KPI cards, charts, insights, and tables render.
4. Test CSV export.

## 11. Test Slack Mode

Slack setup:

1. Create a Slack app.
2. Add bot scopes:
   - `channels:read`
   - `channels:history`
   - `reactions:read`
   - `users:read`
3. Optional private channel scopes:
   - `groups:read`
   - `groups:history`
4. Install the app to the workspace.
5. Invite the bot to target channels.
6. Add `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_IDS` to secrets.
7. Select Slack API in the sidebar.

## 12. Test Discord Mode

The dashboard supports three safe Discord ingestion modes.

### Demo Data Mode

Use `data/demo_messages.json` for local testing and public demos. This requires no Discord account, bot, token, or upload.

### Discord Authorized Server Mode

Use the official Discord bot API only:

```text
GET https://discord.com/api/v10/channels/{channel_id}/messages
```

Discord setup:

1. Create a bot in the Discord Developer Portal.
2. Enable Message Content Intent for most real servers.
3. Invite the bot to your server.
4. Ensure it can view channels and read message history.
5. Add `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_IDS` to secrets.
6. Select Discord API in the sidebar.

Required settings:

- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_IDS`
- `DISCORD_MESSAGE_LIMIT`
- Message Content Intent if message text is needed
- View Channel permission
- Read Message History permission

You do not need to be the creator of a server, but your bot must be invited and granted channel permissions. You cannot analyze random servers just because your personal account joined them.

The app handles missing permissions, missing message content, invalid tokens, rate limits, and unreadable channels gracefully. It shows warnings instead of crashing.

### Personal Discord Conversation Analytics

Select `Personal Discord Conversation Analytics` in the sidebar and upload your own Discord Data Package ZIP or JSON message files. The app parses uploaded message data locally and converts it into the common schema.

Use this for personal Discord history or DM-style analysis. It is not labeled as community engagement because uploaded files may represent private conversations rather than server community activity.

A bot cannot read private DMs between two users unless the bot is actually part of the conversation, which normal personal DMs are not. For personal message history, use Discord Data Package upload instead.

Do not use or build:

- user-token scraping
- self-bots
- automation of a normal Discord user account
- bot-based access to private DMs between two users
- scraping servers just because a personal account joined them

## 13. Privacy Language

This app analyzes team/community communication data. Use only in workspaces/servers where you have permission. For public demos, use demo data or anonymized exports. Do not expose real user names, tokens, or private messages. For personal Discord history, use the upload mode only with data you have permission to analyze.

## 14. Manual Configuration Still Needed

- Slack app creation and workspace installation
- Slack bot channel invitations
- Discord bot creation and server invitation
- Discord Message Content Intent
- Discord channel permissions for View Channel and Read Message History
- Streamlit Cloud secrets
- Decision on whether to keep this as a Buildathon subfolder or split it into a separate repo later
