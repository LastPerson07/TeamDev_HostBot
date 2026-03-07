"""
                      [TeamDev](https://team_x_og)
          
          Project Id -> 28.
          Project Name -> Script Host.
          Project Age -> 4Month+ (Updated On 07/03/2026)
          Project Idea By -> @MR_ARMAN_08
          Project Dev -> @MR_ARMAN_08
          Powered By -> @Team_X_Og ( On Telegram )
          Updates -> @CrimeZone_Update ( On telegram )
    
    Setup Guides -> Read > README.md Or VPS_README.md
    
          This Script Part Off https://Team_X_Og's Team.
          Copyright ©️ 2026 TeamDev | @Team_X_Og
          
    • Some Quick Help
    - Use In Vps Other Way This Bot Won't Work.
    - If You Need Any Help Contact Us In @Team_X_Og's Group
    
         Compatible In BotApi 9.5 Fully
         Build For BotApi 9.4
         We'll Keep Update This Repo If We Got 50+ Stars In One Month Of Release.
"""

import subprocess
import re

SAFE_LIBRARIES = {
    "pytelegrambotapi", "python-telegram-bot", "aiogram", "telethon", "pyrogram",
    "flask", "fastapi", "aiohttp", "httpx", "requests", "uvicorn", "starlette",
    "django", "quart", "tornado", "bottle",
    "pymongo", "motor", "redis", "aioredis", "sqlalchemy", "databases",
    "psycopg2-binary", "aiomysql", "tortoise-orm", "peewee",
    "pydantic", "python-dotenv", "loguru", "rich", "click", "typer",
    "pillow", "qrcode", "barcode", "fpdf", "reportlab",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "openpyxl", "xlrd", "xlwt", "tabulate",
    "bs4", "beautifulsoup4", "lxml", "html5lib", "cssselect",
    "selenium", "playwright",
    "celery", "apscheduler", "schedule",
    "cryptography", "pyjwt", "bcrypt", "passlib",
    "boto3", "google-cloud-storage", "azure-storage-blob",
    "stripe", "twilio", "sendgrid",
    "python-slugify", "arrow", "pendulum", "humanize",
    "langchain", "openai", "anthropic", "cohere",
    "python-multipart", "python-jose", "email-validator",
    "tqdm", "colorama", "termcolor", "pyfiglet",
}

BLOCKED_PATTERNS = [
    r"subprocess", r"os\.system", r"exec\s*\(",
    r"eval\s*\(",  r"pty",       r"pwntools",
    r"scapy",      r"impacket",  r"nmap",
    r"mitmproxy",  r"paramiko",  r"fabric",
    r"netfilter",  r"iptables",  r"nftables",
]


def is_safe_library(library_name: str) -> tuple[bool, str]:
    clean = re.split(r"[>=<!~\[]", library_name.strip().lower())[0].strip()

    if not re.match(r"^[a-z0-9_\-]+$", clean):
        return False, "Invalid library name format."

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, clean, re.I):
            return False, f"Library '{clean}' is blocked for security reasons."

    if clean not in SAFE_LIBRARIES:
        return False, (
            f"Library <code>{clean}</code> is not in the approved list.\n\n"
            "Contact @MR_ARMAN_08 to request approval."
        )

    return True, ""


def pip_install_in_container(docker_client, container_id: str, library: str) -> tuple[bool, str]:
    safe, reason = is_safe_library(library)
    if not safe:
        return False, reason

    try:
        container = docker_client.containers.get(container_id)
        if container.status != "running":
            return False, "Container is not running."

        exit_code, output = container.exec_run(
            f"pip install --quiet {library}",
            user="root"
        )
        output_str = output.decode("utf-8", errors="replace") if output else ""

        if exit_code == 0:
            return True, output_str
        else:
            return False, output_str

    except Exception as e:
        return False, str(e)


def get_safe_libraries_list() -> str:
    cats = {
        "🤖 Telegram": ["pytelegrambotapi", "python-telegram-bot", "aiogram", "telethon", "pyrogram"],
        "🌐 Web": ["flask", "fastapi", "aiohttp", "httpx", "requests", "django"],
        "🗄 Database": ["pymongo", "redis", "sqlalchemy", "psycopg2-binary"],
        "📊 Data": ["pandas", "numpy", "pillow", "matplotlib", "openpyxl"],
        "🔐 Auth": ["cryptography", "pyjwt", "bcrypt"],
        "🤖 AI": ["openai", "anthropic", "langchain"],
        "⚙️ Utils": ["python-dotenv", "loguru", "apscheduler", "tqdm"],
    }
    lines = []
    for cat, libs in cats.items():
        lines.append(f"\n<b>{cat}</b>")
        lines.append(", ".join(f"<code>{l}</code>" for l in libs))
    return "\n".join(lines)
