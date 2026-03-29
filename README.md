# TeamDev HostBot — Railway Edition

## Setup on Railway

### 1. Required Environment Variables
Set these in Railway → Variables:

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `MONGODB_URI` | Your MongoDB connection string |
| `GITHUB_CLIENT_ID` | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App client secret |
| `VPS_HOST_IP` | Your Railway public domain (or leave as-is) |

### 2. Deploy
1. Push this folder to a GitHub repo
2. Connect repo to Railway
3. Set the environment variables above
4. Deploy — Railway will auto-run `python3 bot.py`

### 3. What changed from VPS version
- **No Docker** — user projects run as Python subprocesses
- **No Dockerfile required** — just upload bot.py + requirements.txt
- **VPS feature disabled** — SSH containers not possible on Railway
- Everything else works: GitHub clone, pip install, logs, exec, replace, env vars

### 4. User project requirements (new)
Users now only need:
- `bot.py` or `main.py` (any .py file)
- `requirements.txt` (optional but recommended)

No Dockerfile needed anymore!
