# Remaining Requirements And Handoff Notes

This document is for the next developer or collaborator continuing the CommunityEngagementDashboard project.

## Current Status

The app already includes:

- Streamlit dashboard entry point in `app.py`
- Demo Data mode using `data/demo_messages.json`
- Slack API connector scaffold using `slack_sdk`
- Discord authorized bot API connector using `requests`
- Personal Discord Conversation Analytics upload mode for ZIP or JSON files
- Local VADER sentiment analysis
- Rule-based stress, blocker, support, conflict, celebration, and burnout-risk detection
- KPI cards, charts, insight sections, risk tables, channel summaries, and CSV export
- Streamlit Community Cloud-ready config and secrets example
- Documentation for architecture and deployment

## Remaining Deployment Requirements

### 1. Choose Final Repository Structure

The project can be deployed from a parent repository as:

```text
CommunityEngagementDashboard/app.py
```

For a standalone repo, move the contents of `CommunityEngagementDashboard/` into the root of a new repository and update deployment paths accordingly.

### 2. Create Or Confirm GitHub Repository

If using a parent repository:

```bash
git add CommunityEngagementDashboard
git commit -m "Add community engagement dashboard"
git push origin main
```

If using a standalone repository:

```bash
git init
git add .
git commit -m "Initial community engagement dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

### 3. Deploy To Streamlit Community Cloud

In Streamlit Community Cloud:

1. Create a new app from the GitHub repository.
2. If deploying from a parent repository, set main file path to:

```text
CommunityEngagementDashboard/app.py
```

3. If deploying from a standalone repository, set main file path to:

```text
app.py
```

4. Add secrets only for the integrations that will be used.
5. Test Demo Data mode first.
6. Test Slack and Discord modes after API setup is complete.

## Required Secrets And Environment Variables

### Shared

```text
APP_MODE=demo
```

### Slack API Mode

```text
SLACK_BOT_TOKEN=
SLACK_CHANNEL_IDS=
SLACK_FETCH_THREADS=false
SLACK_MESSAGE_LIMIT=100
```

### Discord Authorized Server Mode

```text
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_IDS=
DISCORD_MESSAGE_LIMIT=100
```

## Slack Setup Still Needed

To use Slack API mode:

1. Create a Slack app.
2. Add a bot user.
3. Add required bot scopes:

```text
channels:read
channels:history
reactions:read
users:read
```

4. Optional private-channel scopes:

```text
groups:read
groups:history
```

5. Install the app to the workspace.
6. Invite the bot to every channel that should be analyzed.
7. Add channel IDs to `SLACK_CHANNEL_IDS` as a comma-separated list.
8. Add the bot token to `SLACK_BOT_TOKEN`.
9. Test Slack API mode in the sidebar.

## Discord Authorized Server Setup Still Needed

To use Discord API mode:

1. Create a Discord application and bot in the Discord Developer Portal.
2. Copy the bot token into `DISCORD_BOT_TOKEN`.
3. Enable Message Content Intent if message text analysis is needed.
4. Invite the bot to the server.
5. Grant the bot access only to selected channels.
6. Ensure the bot has:

```text
View Channel
Read Message History
```

7. Add channel IDs to `DISCORD_CHANNEL_IDS` as a comma-separated list.
8. Test Discord API mode in the sidebar.

Important boundaries:

- The user does not need to be the creator of a server, but the bot must be invited and granted channel permissions.
- The app cannot analyze random servers just because a personal Discord account joined them.
- A bot cannot read private DMs between two users unless the bot is actually part of the conversation, which normal personal DMs are not.
- For personal message history, use Personal Discord Conversation Analytics upload mode instead.

## Personal Discord Conversation Analytics Setup

This mode does not need a bot or token.

Use it for personal Discord exports:

1. Request or download a Discord Data Package from Discord.
2. Upload ZIP or JSON files in the app sidebar.
3. Confirm the dashboard parses messages and displays metrics.

This mode is intentionally labeled Personal Discord Conversation Analytics because uploaded files may represent personal or private conversations rather than a server community.

## Safety Requirements

Do not implement or suggest:

- user-token scraping
- self-bots
- automating a normal Discord user account
- reading private DMs between two users through a bot
- scraping servers just because a user personally joined them

Use only data that the operator has permission to analyze.

## Quality Checks To Run Before Final Deployment

From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m compileall .
streamlit run app.py
```

Manual checks:

- Demo Data mode loads with no tokens.
- CSV export downloads filtered rows.
- Slack mode shows warnings instead of crashing when token/channel access is missing.
- Discord mode shows warnings instead of crashing when token/channel access is missing.
- Personal Discord Conversation Analytics upload mode parses valid JSON or ZIP files.
- No real `.env` file or `.streamlit/secrets.toml` is committed.

## Suggested Next Improvements

- Add automated tests for metrics, sentiment enrichment, and upload parsing.
- Add better Discord Data Package format coverage after testing real exports.
- Add channel-name lookup for Discord authorized server mode.
- Add pagination for Slack and Discord beyond the current message limit.
- Add optional anonymization controls before CSV export.
- Add clearer empty-state UI for upload mode before files are selected.
