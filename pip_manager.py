"""
pip_manager.py — Railway compatible.
Installs packages globally (same Python env as the bot).
docker_client arg is kept for API compatibility but ignored.
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
    r"eval\s*\(",  r"pty",        r"pwntools",
    r"scapy",      r"impacket",   r"nmap",
    r"mitmproxy",  r"paramiko",   r"fabric",
    r"netfilter",  r"iptables",   r"nftables",
]


def is_safe_library(library_name: str) -> tuple:
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


def pip_install_in_container(docker_client, container_id: str, library: str) -> tuple:
    """
    docker_client & container_id are ignored on Railway.
    Package is installed into the shared Python environment.
    """
    safe, reason = is_safe_library(library)
    if not safe:
        return False, reason

    try:
        result = subprocess.run(
            ["pip", "install", "--quiet", "--no-warn-script-location", library],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            return True, result.stdout or "Installed successfully."
        else:
            return False, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return False, "pip install timed out."
    except Exception as e:
        return False, str(e)


def get_safe_libraries_list() -> str:
    cats = {
        "🤖 Telegram":  ["pytelegrambotapi", "python-telegram-bot", "aiogram", "telethon", "pyrogram"],
        "🌐 Web":        ["flask", "fastapi", "aiohttp", "httpx", "requests", "django"],
        "🗄 Database":   ["pymongo", "redis", "sqlalchemy", "psycopg2-binary"],
        "📊 Data":       ["pandas", "numpy", "pillow", "matplotlib", "openpyxl"],
        "🔐 Auth":       ["cryptography", "pyjwt", "bcrypt"],
        "🤖 AI":         ["openai", "anthropic", "langchain"],
        "⚙️ Utils":      ["python-dotenv", "loguru", "apscheduler", "tqdm"],
    }
    lines = []
    for cat, libs in cats.items():
        lines.append(f"\n<b>{cat}</b>")
        lines.append(", ".join(f"<code>{l}</code>" for l in libs))
    return "\n".join(lines)
