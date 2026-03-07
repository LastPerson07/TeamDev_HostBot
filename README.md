<div align="center">

# TeamDev Host Bot [Live Demo Bot](https://t.me/TeamDev_HostBot)
### A Powerful Telegram Bot to Host Your Python Projects 24/7 [Live Demo Bot](https://t.me/TeamDev_HostBot)

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Required-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Required-47A248?style=for-the-badge&logo=mongodb)](https://mongodb.com)
[![Telegram Bot API](https://img.shields.io/badge/BotAPI-9.4%2B-26A5E4?style=for-the-badge&logo=telegram)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Deploy, manage, and monitor your Python bots/scripts directly from Telegram — no terminal needed.**

[📖 Setup Guide](#-setup-guide) • [⚙️ Configuration](#️-configuration) • [📋 Commands](#-bot-commands) • [🐛 Troubleshooting](#-troubleshooting) • [💬 Support](#-support)

---

> ⭐ **If this project helps you, please give it a star! We'll keep updating if we reach 50+ stars in the first month.**

</div>

---

## 📌 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📋 Prerequisites](#-prerequisites)
- [🚀 Setup Guide](#-setup-guide)
  - [Option A — Docker Compose (Recommended)](#option-a--docker-compose-recommended)
  - [Option B — Manual / Systemd Service](#option-b--manual--systemd-service)
  - [Option C — Auto Setup Script](#option-c--auto-setup-script)
- [⚙️ Configuration](#️-configuration)
  - [Environment Variables](#environment-variables)
  - [GitHub OAuth Setup](#github-oauth-setup)
- [📋 Bot Commands](#-bot-commands)
  - [User Commands](#user-commands)
  - [Admin Commands](#admin-commands)
  - [VPS Commands](#vps-commands)
- [📦 Project Upload Requirements](#-project-upload-requirements)
- [💎 Tier System](#-tier-system)
- [🖥️ Mini VPS Feature](#️-mini-vps-feature)
- [🔐 Security Features](#-security-features)
- [🗂️ File Structure](#️-file-structure)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)
- [💬 Support](#-support)

---

## ✨ Features

| Feature | Free | Premium |
|--------|------|---------|
| Host Python Projects | ✅ (1 project) | ✅ (3 projects) |
| Upload via ZIP | ✅ (50MB) | ✅ (500MB) |
| Deploy from GitHub | ✅ Public repos | ✅ Public + Private |
| GitHub OAuth Integration | ✅ | ✅ |
| Auto Update from Repo | ✅ | ✅ |
| In-container `/exec` | ✅ | ✅ |
| File Replace (`/replace`) | ✅ | ✅ |
| Environment Variables (`/env`) | ✅ | ✅ |
| pip Install | ✅ | ✅ |
| CPU | 0.25 cores | 2 cores |
| RAM | 256MB | 1024MB |
| Storage | 3GB | 30GB |
| Monthly Uptime | 200h | 720h |
| Auto-Stop | After 12h | ❌ (Always on) |
| Auto-Restart on Crash | ❌ | ✅ |
| Mini VPS (SSH) | 24h trial (once) | 30 days |
| Deployment Speed | Standard | Fast |

**Additional Capabilities:**
- 🔒 Security scanning for malware, miners, DDoS scripts on every GitHub clone
- 📊 Real-time container stats (CPU, RAM, uptime)
- 📋 Live build & runtime logs
- 📢 Premium expiry alerts & auto-downgrade
- 🔁 Background container monitoring
- 👑 Full admin panel with broadcast, user management, and server stats
- 🛡️ Duplicate account detection
- 🔧 Maintenance mode toggle

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Bot API                     │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                     bot.py (Main)                       │
│  ┌────────────┐  ┌───────────────┐  ┌────────────────┐  │
│  │ rate_limiter│  │security_scanner│  │  logger.py     │  │
│  └────────────┘  └───────────────┘  └────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │  docker_manager  │  │   vps_manager    │             │
│  └──────────────────┘  └──────────────────┘             │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │  github_auth     │  │  pip_manager     │             │
│  │  (Flask OAuth)   │  └──────────────────┘             │
│  └──────────────────┘                                   │
└───────────────────────────┬─────────────────────────────┘
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
┌─────────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│   MongoDB      │  │   Docker     │  │  Flask OAuth  │
│  (database.py) │  │  (Containers)│  │  Server :5000 │
└────────────────┘  └──────────────┘  └───────────────┘
```

The bot runs on a **VPS** and uses **Docker** to spin up isolated containers for each user project. MongoDB stores all user data, project metadata, and GitHub tokens. A Flask micro-server handles the GitHub OAuth callback.

---

## 📋 Prerequisites

Before you begin, make sure your VPS/server meets these requirements:

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Ubuntu 20.04 | Ubuntu 22.04 / 24.04 |
| RAM | 1 GB | 2 GB+ |
| Storage | 20 GB | 50 GB+ |
| CPU | 1 vCore | 2 vCores+ |
| Python | 3.11+ | 3.11+ |
| Docker | 24.0+ | Latest |
| Docker Compose | v2 | Latest |

> ⚠️ **This bot MUST be run on a VPS or dedicated server.** It will not work on shared hosting, Heroku free tier, or your local machine without Docker.

**Required accounts/services:**
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Your Telegram User ID (get it from [@userinfobot](https://t.me/userinfobot))
- A MongoDB database — either [MongoDB Atlas (free)](https://www.mongodb.com/atlas) or self-hosted
- *(Optional)* A GitHub OAuth App for private repo support

---

## 🚀 Setup Guide

### Option A — Docker Compose (Recommended)

This is the easiest and most reliable method. Docker Compose manages both the bot and MongoDB automatically.

**Step 1 — Install Docker & Docker Compose**

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo systemctl enable --now docker

# Install Docker Compose plugin
sudo apt-get install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

**Step 2 — Clone the repository**

```bash
git clone https://github.com/justfortestingnothibghere/TeamDev_HostBot.git
cd TeamDev_HostBot
```

Fill in your values (see [Configuration](#️-configuration) section below), then save and exit.

**Step 4 — Build and start**

```bash
docker compose up -d --build
```

**Step 5 — Verify it's running**

```bash
# Check container status
docker compose ps

# View live logs
docker compose logs -f bot
```

You should see `Bot Started: @{YourBotUsername}` in the logs. Send `/start` to your bot on Telegram to confirm it works.

---

### Option B — Manual / Systemd Service

Use this if you prefer running the bot directly with Python (without containerizing the bot itself).

**Step 1 — Install system dependencies**

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3.11 python3.11-pip python3.11-venv git docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

> ⚠️ Log out and back in (or run `newgrp docker`) after adding yourself to the docker group.

**Step 2 — Clone and set up the project**

```bash
git clone https://github.com/justfortestingnothibghere/TeamDev_HostBot
cd TeamDev_HostBot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

**Step 4 — Start MongoDB** (skip if using MongoDB Atlas)

```bash
docker run -d \
  --name telegram-bot-mongo \
  --restart always \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0
```

**Step 5 — Run the bot**

For testing:
```bash
source venv/bin/activate
python bot.py
```

For production (systemd service):

```bash
# Create the service file
sudo nano /etc/systemd/system/telegram-bot.service
```

Paste this content (adjust paths as needed):

```ini
[Unit]
Description=Telegram Host Bot
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/ubuntu/telegram-host-bot # ubuntu change to your System name
ExecStart=/home/ubuntu/telegram-host-bot/venv/bin/python bot.py
Restart=always
RestartSec=10
EnvironmentFile=/home/ubuntu/telegram-host-bot/.env

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f
```

---

### Option C — Auto Setup Script

A convenience script is included that automates the Docker + system setup:

```bash
git clone https://github.com/justfortestingnothibghere/TeamDev_HostBot.git
cd TeamDev_HostBot
sudo chmod +x setup.sh
sudo ./setup.sh
```

The script will:
1. Update system packages
2. Install Docker and Docker Compose
3. Install Git and Python
4. Prompt you to configure your `.env` file
5. Build and launch the containers

> ⚠️ Review `setup.sh` before running it as root. Always audit scripts before execution.

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and set the following:

```env
# ─── Required ───────────────────────────────────────────────────────
BOT_TOKEN=YOUR_BOT_TOKEN_FROM_BOTFATHER
OWNER_ID=YOUR_TELEGRAM_USER_ID
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/dbname

LOG_CHANNEL_ID=-100XXXXXXXXXX     # Telegram channel/group ID for action logs
ADMIN_IDS=123456789               # Comma-separated additional admin IDs
VPS_HOST_IP=YOUR_SERVER_IP        # Your VPS public IP (for Mini VPS SSH feature)

GITHUB_CLIENT_ID=YOUR_GITHUB_OAUTH_APP_CLIENT_ID
GITHUB_CLIENT_SECRET=YOUR_GITHUB_OAUTH_APP_CLIENT_SECRET
```

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Get from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | ✅ | Your Telegram user ID. Has full admin access |
| `MONGODB_URI` | ✅ | Full MongoDB connection string |
| `LOG_CHANNEL_ID` | ✅ | Telegram channel/group to receive activity logs. Bot must be admin in that channel |
| `ADMIN_IDS` | ✅ | Additional admin user IDs, comma-separated |
| `VPS_HOST_IP` | ✅ | Your server's public IP. Required if using the Mini VPS feature |
| `GITHUB_CLIENT_ID` | ✅ | Required for GitHub OAuth (private repo access) |
| `GITHUB_CLIENT_SECRET` | ✅ | Required for GitHub OAuth |

### Getting Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the token provided (format: `1234567890:ABCdefGHIjklmNoPQRsTUVwxyZ`)

### Getting Your User ID

1. Open [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send `/start` — it will reply with your numeric User ID

### Setting Up MongoDB Atlas (Free Tier)

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas) and create a free account
2. Create a free **M0** cluster
3. Under **Database Access**, create a user with read/write permissions
4. Under **Network Access**, add `0.0.0.0/0` (allow all IPs) or your VPS IP
5. Click **Connect → Drivers** and copy the connection string
6. Replace `<password>` in the URI with your database user's password
7. Paste the full URI into `MONGODB_URI` in your `.env`

### GitHub OAuth Setup

To allow users to connect their GitHub accounts and deploy **private repositories**:

1. Go to [GitHub Developer Settings → OAuth Apps](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in:
   - **Application name:** `Script Host Bot` (or your preferred name)
   - **Homepage URL:** `https://yourdomain.com` (can be your VPS IP)
   - **Authorization callback URL:** `https://auth.yourdomain.com/callback`
4. Click **Register Application**
5. Copy the **Client ID** and generate a **Client Secret**
6. Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in your `.env`

> 💡 **Note:** The callback URL in `github_auth.py` is currently set to `https://auth.teamdev.sbs/callback`. You must update this to your own domain/callback URL if you're self-hosting.

---

## 📋 Bot Commands

### User Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with your limits, tier info, and quick menu |
| `/upload` | Upload a `.zip` file containing your Python project to deploy |
| `/github` | Clone and deploy a project from a GitHub URL (public or private) |
| `/repos` | Browse and deploy repos from your connected GitHub account |
| `/connect` | Connect your GitHub account via OAuth for private repo access |
| `/disconnect` | Unlink your GitHub account |
| `/projects` | View and manage all your deployed projects |
| `/logs` | View build and runtime logs for a project |
| `/stop` | Stop a running project |
| `/pip <library>` | Install a Python library inside a running container |
| `/update` | Pull latest commits and rebuild a GitHub-sourced project |
| `/exec <command>` | Execute a shell command inside your container (restricted) |
| `/replace <filename>` | Replace a file inside a running container and auto-restart |
| `/env` | View, set, or delete environment variables in a container |
| `/vps` | Access the Mini VPS (SSH) feature |
| `/premium` | View premium plans and upgrade information |
| `/help` | Full command reference |
| `/support` | Contact links and developer info |

### Admin Commands

Access the admin panel with `/admin` (owner or admin IDs only).

| Command | Description |
|---------|-------------|
| `/admin` | Open the admin panel with stats |
| `/addpremium <user_id> [days]` | Grant premium to a user (default: 30 days) |
| `/removepremium <user_id>` | Remove premium from a user |
| `/setpremiumdays <user_id> <days>` | Update/extend a user's premium duration |
| `/addadmin <user_id>` | Grant admin role (owner only) |
| `/removeadmin <user_id>` | Revoke admin role (owner only) |
| `/ban <user_id> [reason]` | Ban a user from using the bot |
| `/unban <user_id>` | Unban a user |
| `/restrict <user_id>` | Restrict a user (can use bot but not deploy) |
| `/unrestrict <user_id>` | Remove restriction |
| `/warn <user_id> [reason]` | Issue a warning (3 warnings = auto-ban) |
| `/maintenance on/off` | Toggle maintenance mode (blocks non-admins) |
| `/broadcast <message>` | Send a message to all registered users |
| `/userinfo <user_id>` | View detailed info about a user |
| `/serverinfo` | View server CPU, RAM, disk, and Docker stats |
| `/allusers` | List all registered users (first 50) |
| `/premiumusers` | List all active premium users with expiry dates |
| `/stopproject <project_id>` | Force-stop any user's project |
| `/deleteproject <project_id>` | Force-delete any user's project |

### VPS Commands

| Command | Description |
|---------|-------------|
| `/vps` | Open the Mini VPS panel |
| `/vpsList` | *(Admin)* List all active VPS instances |
| `/vpsRemove <user_id>` | *(Admin)* Destroy a user's VPS |
| `/vpsStop <user_id>` | *(Admin)* Stop a user's VPS |
| `/vpsGive <user_id> <tier>` | *(Admin)* Give a VPS to a user |
| `/vpsStats` | *(Admin)* VPS usage statistics |

---

## 📦 Project Upload Requirements

Every project you deploy (via `/upload` or `/github`) **must** contain these files:

### 1. `Dockerfile` (Required)

Defines how your project is built into a Docker container. Example for a Telegram bot:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "your_bot.py"]
```

### 2. `requirements.txt` (Required)

Lists all Python packages your project needs:

```
pyTelegramBotAPI==4.31.0
requests==2.31.0
python-dotenv==1.0.0
```

### Project ZIP Structure

Your `.zip` file should look like this:

```
myproject.zip
├── Dockerfile          ← Required
├── requirements.txt    ← Required
├── your_bot.py         ← Your main script
├── config.py
└── ... (other files)
```

> 💡 **Tip:** Sensitive credentials (like API keys) should be set using `/env` **after** deployment, not hardcoded in your project files.

---

## 💎 Tier System

### Free Tier
- 1 project at a time
- 50MB upload limit
- 0.25 CPU cores
- 256MB RAM
- 3GB storage
- 200 hours/month uptime
- Auto-stops after 12 hours of inactivity
- No auto-restart on crash
- GitHub public repos only

### Premium Tier
- 3 simultaneous projects
- 500MB upload limit
- 2 CPU cores
- 1024MB RAM
- 30GB storage
- 720 hours/month uptime
- Always-on (no auto-stop)
- Auto-restart on crash
- Private GitHub repo support
- Priority deployment speed

### Premium Pricing
Contact the developer [@MR_ARMAN_08](https://t.me/MR_ARMAN_08) for pricing.

Admins can grant premium via:
```
/addpremium <user_id> <days>
```

---

## 🖥️ Mini VPS Feature

The `/vps` command provides users with a dedicated SSH shell environment inside a Docker container.

### How it works
1. User sends `/vps`
2. Bot creates an isolated Docker container with SSH enabled
3. User receives credentials: hostname, port, username, and password
4. User connects via any SSH client: `ssh user@host -p PORT`

### VPS Tiers

| Tier | Duration | RAM | CPU | Storage |
|------|----------|-----|-----|---------|
| Free (one-time) | 24 hours | 256MB | 0.25 cores | 2GB |
| Premium | 30 days | 512MB | 1 core | 10GB |
| Owner | Unlimited | 1GB | 2 cores | 20GB |

### Available in VPS
- Python 3, pip
- Node.js & npm
- Git
- Nano, Vim text editors

> ⚠️ Sudo is disabled in VPS containers for security. Root access is not available.

### VPS Configuration

For the VPS feature to work, `VPS_HOST_IP` must be set to your server's public IP in `.env`. The bot dynamically assigns port numbers to each VPS container.

---

## 🔐 Security Features

The bot includes multiple layers of security:

### Security Scanner (`security_scanner.py`)
Automatically runs on every GitHub clone before deployment. Detects:
- Reverse shells and network backdoors
- Cryptomining scripts (xmrig, cpuminer, etc.)
- DDoS/flooding scripts
- Password/token harvesters
- Suspicious base64-encoded payloads
- Fork bombs and resource exhaustion attacks

> Note: The security scanner is bypassed on ZIP uploads. It only applies to GitHub clones.

### Exec Command Filtering (`/exec`)
The `/exec` command blocks dangerous shell patterns including:
- Network tools (`curl`, `wget`, `nc`, `ssh`)
- Package managers (`apt install`, `pip install` via shell)
- System destructive commands (`rm -rf /`, `mkfs`, `dd`)
- Privilege escalation (`sudo`, `su`)
- Docker socket access
- Shell injection operators

### Container Isolation
- Each project runs in its own Docker container
- CPU and memory limits enforced per tier
- Containers run with restricted capabilities

### Duplicate Account Detection
- Prevents users from operating multiple accounts to bypass free tier limits
- Automatically bans detected duplicate accounts

### Rate Limiting
- Per-user command rate limiting to prevent abuse

---

## 🗂️ File Structure

```
telegram-host-bot/
├── bot.py                  # Main bot — all commands, callbacks, and logic
├── database.py             # MongoDB wrapper — all database operations
├── docker_manager.py       # Docker container lifecycle management
├── vps_manager.py          # Mini VPS creation and management
├── github_auth.py          # GitHub OAuth server (Flask) and repo cloning
├── security_scanner.py     # Malware/threat detection for uploaded code
├── pip_manager.py          # Safe pip install inside containers
├── rate_limiter.py         # Per-user rate limiting
├── logger.py               # Action logging to Telegram channel
├── emoji.py                # Emoji constants used across the bot
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image for the bot itself
├── Dockerfile.vps          # Container image used for user VPS instances
├── docker-compose.yml      # Compose file (bot + MongoDB)
├── setup.sh                # Auto-setup script for fresh VPS
├── build_vps_image.sh      # Script to pre-build the VPS Docker image
├── vps-entrypoint.sh       # Entrypoint for VPS containers (SSH setup)
├── telegram-bot.service    # Systemd service definition
├── .env                    # Your local configuration (never commit this!)
├── .env.example            # Template for environment variables
└── data/
    └── index.html          # Landing page served by the OAuth web server
```

---

## 🐛 Troubleshooting

### Bot is not responding
```bash
# Check if containers are running
docker compose ps

# View bot logs
docker compose logs -f bot

# Restart the bot
docker compose restart bot
```

### "Docker socket not found" error
The bot needs access to the Docker socket to manage containers. Make sure the volume is mounted:
```yaml
# In docker-compose.yml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

### MongoDB connection fails
- Verify your `MONGODB_URI` is correct in `.env`
- If using Atlas, ensure your VPS IP is whitelisted in Atlas Network Access
- If self-hosted, confirm the MongoDB container is running: `docker ps | grep mongo`

### GitHub clone fails for private repos
- Make sure the user has connected their GitHub via `/connect`
- Ensure `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set correctly
- Check that your OAuth app's callback URL matches the one in `github_auth.py`

### Project deployment fails (build error)
- Check that your project's `Dockerfile` is valid
- View build logs in the bot with `/logs` after deployment
- Ensure `requirements.txt` lists all needed packages
- Make sure your Dockerfile's `CMD` points to the correct entry file

### VPS SSH connection refused
- Confirm `VPS_HOST_IP` is set to your server's actual public IP
- Check that the assigned port isn't blocked by your server's firewall:
  ```bash
  sudo ufw allow 10000:20000/tcp  # Allow VPS port range
  ```

### Bot keeps restarting / crash loop
```bash
# View recent logs with timestamps
docker compose logs --tail=100 bot

# Check system resources
docker stats
```

### Containers not stopping / orphan containers
```bash
# List all bot-managed containers
docker ps -a | grep "hostbot_"

# Force remove a specific container
docker rm -f CONTAINER_ID

# Full cleanup (WARNING: removes all stopped containers)
docker container prune
```

---

## 🔄 Updating the Bot

To pull the latest version and restart:

```bash
git pull origin main
docker compose down
docker compose up -d --build
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** this repository
2. **Create a branch** for your feature: `git checkout -b feature/my-feature`
3. **Make your changes** and test thoroughly
4. **Commit** with a clear message: `git commit -m "feat: add XYZ feature"`
5. **Push** to your fork: `git push origin feature/my-feature`
6. **Open a Pull Request** with a description of your changes

### Code Style
- Follow PEP 8 for Python code
- Keep functions focused and well-commented
- Do not commit `.env` files or credentials

### Reporting Bugs
Open an issue with:
- A clear description of the problem
- Steps to reproduce it
- Relevant logs or error messages
- Your OS and Docker version

---

## 📜 License

```
Copyright © 2026 TeamDev | @Team_X_Og

This project is open-sourced under the MIT License.
See LICENSE file for full details.

Project developed by @MR_ARMAN_08 | Powered by @Team_X_Og
```

---

## 💬 Support

| Resource | Link |
|----------|------|
| 💬 Support Group | [@TEAM_X_OG](https://t.me/TEAM_X_OG) |
| 📢 Updates Channel | [@CrimeZone_Update](https://t.me/CrimeZone_Update) |
| 👨‍💻 Developer | [@MR_ARMAN_08](https://t.me/MR_ARMAN_08) |
| 🎥 Video Guide | [Watch on Telegram](https://t.me/TEAM_x_OG/108421) |

For **premium purchases** or **direct support**, contact [@MR_ARMAN_08](https://t.me/MR_ARMAN_08) on Telegram.

---

<div align="center">

**Built with ❤️ by [TeamDev](https://t.me/Team_X_Og)**

*Compatible with Telegram Bot API 9.4+ | Fully tested on 9.5*

</div>
