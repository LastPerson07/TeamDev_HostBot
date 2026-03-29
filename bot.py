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

import telebot
from telebot import types
import os
import zipfile
import tempfile
import hashlib
import time
import subprocess
import threading
import json
from datetime import datetime, timedelta
from database import Database
from security_scanner import SecurityScanner
from docker_manager import DockerManager
from rate_limiter import RateLimiter
from logger import BotLogger
from pip_manager import pip_install_in_container, is_safe_library, get_safe_libraries_list
from vps_manager import VpsManager
import github_auth
import psutil
import shutil
import requests
import html
import docker as docker_sdk

BOT_TOKEN  = os.environ.get("BOT_TOKEN")
MONGODB_URI = os.environ.get("MONGODB_URI")
LOG_CHANNEL_ID = -1003144372708
OWNER_ID   = 1633472140
ADMIN_IDS  = [1633472140]
VPS_HOST_IP = os.environ.get("VPS_HOST_IP", "YOUR_VPS_IP")

bot            = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
db             = Database(MONGODB_URI)
scanner        = SecurityScanner()
docker_manager = DockerManager(db)
vps_manager    = VpsManager(db, host_ip=VPS_HOST_IP)
rate_limiter   = RateLimiter(db)
logger         = BotLogger(bot, LOG_CHANNEL_ID)
docker_client  = docker_sdk.from_env()

bot_info     = bot.get_me()
BOT_USERNAME = bot_info.username
BOT_NAME     = bot_info.first_name

PREMIUM_EMOJI = "⭐"

from emoji import *

maintenance_mode = False

# ─── Init GitHub OAuth server ───────────────────────────────────────
github_auth.init(db, bot)
github_auth.start_server()

# ── VPS expiry notification callback ────────────────────────────────
def _vps_notify(user_id, text):
    try:
        bot.send_message(user_id, text)
    except:
        pass
vps_manager.notify_callback = _vps_notify


# ─── Helpers ────────────────────────────────────────────────────────
def is_owner(user_id):   return user_id == OWNER_ID
def is_admin(user_id):   return db.is_admin(user_id) or is_owner(user_id)

def check_maintenance(func):
    def wrapper(message):
        if maintenance_mode and not is_admin(message.from_user.id):
            bot.reply_to(message, f"<b>𝙱𝙾𝚃 𝙸𝚂 𝚄𝙽𝙳𝙴𝚁 𝙼𝙰𝙸𝙽𝚃𝙴𝙽𝙰𝙽𝙲𝙴.</b> {maintenance}\n\n𝙿𝙻𝙴𝙰𝚂𝙴 𝚃𝚁𝚈 𝙰𝙶𝙰𝙸𝙽 𝙻𝙰𝚃𝙴𝚁. 𝙸𝙵 𝚈𝙾𝚄 𝚃𝙷𝙸𝙽𝙺 𝚃𝙷𝙸𝚂 𝚆𝙰𝚂 𝙼𝙸𝚂𝚃𝙰𝙺𝙴 𝙲𝙾𝙽𝚃𝙰𝙲𝚃 @MR_ARMAN_08 {verified}")
            return
        return func(message)
    return wrapper

def check_banned(func):
    def wrapper(message):
        if db.is_banned(message.from_user.id):
            bot.reply_to(message, f"<b>𝚈𝙾𝚄 𝙰𝚁𝙴 𝙱𝙰𝙽𝙽𝙴𝙳 𝙵𝚁𝙾𝙼 𝚄𝚂𝙸𝙽𝙶 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃</b>. {banned}\n\n𝙸𝙵 𝚈𝙾𝚄 𝚃𝙷𝙸𝙽𝙺 𝚃𝙷𝙸𝚂 𝚆𝙰𝚂 𝙼𝙸𝚂𝚃𝙰𝙺𝙴 𝙲𝙾𝙽𝚃𝙰𝙲𝚃 @MR_ARMAN_08 {verified}")
            logger.log_action(message.from_user.id, "banned_user_attempt", {"command": message.text})
            return
        return func(message)
    return wrapper

def check_restricted(func):
    def wrapper(message):
        if db.is_restricted(message.from_user.id):
            bot.reply_to(message, f"{r} 𝚈𝙾𝚄𝚁 𝙿𝙴𝚁𝙼𝙸𝚂𝚂𝙸𝙾𝙽𝚂 𝙰𝚁𝙴 𝚁𝙴𝚂𝚃𝚁𝙸𝙲𝚃𝙴𝙳.\n\n𝙲𝙾𝙽𝚃𝙰𝙲𝚃 @MR_ARMAN_08 {verified}")
            return
        return func(message)
    return wrapper

def check_rate_limit(func):
    def wrapper(message):
        if not rate_limiter.check_limit(message.from_user.id):
            bot.reply_to(message, f"{rate} 𝚁𝙰𝚃𝙴 𝙻𝙸𝙼𝙸𝚃 𝙴𝚇𝙲𝙴𝙴𝙳𝙴𝙳. 𝙿𝙻𝙴𝙰𝚂𝙴 𝚆𝙰𝙸𝚃 𝙱𝙴𝙵𝙾𝚁𝙴 𝚃𝚁𝚈𝙸𝙽𝙶 𝙰𝙶𝙰𝙸𝙽.")
            return
        return func(message)
    return wrapper

def edit_message_safe(bot, text, chat_id, message_id, reply_markup=None, parse_mode="HTML"):
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        if "there is no text in the message" in str(e):
            bot.edit_message_caption(text, chat_id, message_id, reply_markup=reply_markup, parse_mode=parse_mode)

def get_user_limits(user_id):
    if db.is_premium(user_id) or is_owner(user_id):
        return {
            'max_projects': 3, 'max_upload_size': 500 * 1024 * 1024,
            'cpu_cores': 2.0, 'memory': 1024, 'storage': 30 * 1024,
            'max_hours': 720, 'auto_stop': False, 'restart_on_crash': True,
            'deployment_speed': 'fast', 'tier': 'Premium'
        }
    else:
        return {
            'max_projects': 1, 'max_upload_size': 50 * 1024 * 1024,
            'cpu_cores': 0.25, 'memory': 256, 'storage': 3 * 1024,
            'max_hours': 200, 'auto_stop': 12, 'restart_on_crash': False,
            'deployment_speed': 'slow', 'tier': 'Free'
        }


# ════════════════════════════════════════════════════════════════════
#  /start
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['start'])
@check_maintenance
@check_banned
def start_command(message):
    user_id  = message.from_user.id
    username = message.from_user.username or "User"
    db.register_user(user_id, username)

    if db.check_duplicate_device(user_id, message):
        bot.reply_to(message, f"{dub} 𝙳𝚄𝙿𝙻𝙸𝙲𝙰𝚃𝙴 𝙰𝙲𝙲𝙾𝚄𝙽𝚃 𝙳𝙴𝚃𝙴𝙲𝚃𝙴𝙳! 𝚈𝙾𝚄 𝙲𝙰𝙽𝙽𝙾𝚃 𝚄𝚂𝙴 𝙼𝚄𝙻𝚃𝙸𝙿𝙻𝙴 𝙰𝙲𝙲𝙾𝚄𝙽𝚃𝚂.\n\n𝙲𝙾𝙽𝚃𝙰𝙲𝚃 @MR_ARMAN_08 {verified}")
        logger.log_action(user_id, "duplicate_account_blocked", {"username": username})
        db.ban_user(user_id, "Duplicate account usage")
        return

    limits      = get_user_limits(user_id)
    tier        = limits['tier']
    gh_info     = db.get_github_info(user_id)
    gh_status   = f"🟢 @{gh_info['github_username']}" if gh_info else "🔴 Not Connected"
    expiry_text = ""

    if tier == 'Premium':
        expiry = db.get_premium_expiry(user_id)
        if expiry:
            days_left = (expiry - datetime.now()).days
            expiry_text = f"\n{check} Pʀᴇᴍɪᴜᴍ Exᴘɪʀᴇs <code>{expiry.strftime('%Y-%m-%d')}</code> ({days_left}d left)"

    welcome_text = f"""
{welcome} <b>𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 {BOT_NAME} {verified_2}</b>

{hello} 𝙷𝙴𝙻𝙻𝙾 <b>{message.from_user.first_name}</b> {verified}

𝙸'𝙼 𝙰 𝙿𝙾𝚆𝙴𝚁𝙵𝚄𝙻 𝙱𝙾𝚃 𝚃𝙷𝙰𝚃 𝙲𝙰𝙽 𝙷𝙾𝚂𝚃 𝚈𝙾𝚄𝚁 𝙿𝚈𝚃𝙷𝙾𝙽 𝙿𝚁𝙾𝙹𝙴𝙲𝚃𝚂 𝟸𝟺/𝟽!

<b>{stats} Yᴏᴜʀ Tɪᴇʀ</b> {premium if tier == 'Premium' else free} <b>{tier}</b>{expiry_text}
<b>{github} GɪᴛHᴜʙ</b> {gh_status}

<b>{limit} 𝒀𝒐𝒖𝒓 𝑳𝒊𝒎𝒊𝒕𝒔</b>
{check} Mᴀx Pʀᴏᴊᴇᴄᴛs <code>{limits['max_projects']}</code>
{check} Uᴘʟᴏᴀᴅ Sɪᴢᴇ <code>{limits['max_upload_size'] // (1024*1024)}MB</code>
{check} CPU Cᴏʀᴇs <code>{limits['cpu_cores']}</code>
{check} RAM <code>{limits['memory']}MB</code>
{check} Sᴛᴏʀᴀɢᴇ <code>{limits['storage'] // 1024}GB</code>
{check} Mᴀx Hᴏᴜʀs/Mᴏɴᴛʜ <code>{limits['max_hours']}h</code>

<b>{quick} 𝑸𝒖𝒊𝒄𝒌 𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒔</b>
{cmd} /upload - Uᴘʟᴏᴀᴅ Nᴇᴡ Pʀᴏᴊᴇᴄᴛ
{cmd} /github - Cʟᴏɴᴇ Fʀᴏᴍ GɪᴛHᴜʙ (Pᴜʙʟɪᴄ/Pʀɪᴠᴀᴛᴇ)
{cmd} /repos - Bʀᴏᴡsᴇ Yᴏᴜʀ GɪᴛHᴜʙ Rᴇᴘᴏs
{cmd} /connect - Cᴏɴɴᴇᴄᴛ GɪᴛHᴜʙ Aᴄᴄᴏᴜɴᴛ
{cmd} /pip - Iɴsᴛᴀʟʟ Pʏᴛʜᴏɴ Lɪʙʀᴀʀʏ
{cmd} /update - Uᴘᴅᴀᴛᴇ Pʀᴏᴊᴇᴄᴛ Fʀᴏᴍ Rᴇᴘᴏ
{cmd} /exec - Rᴜɴ Cᴏᴍᴍᴀɴᴅ Iɴ Cᴏɴᴛᴀɪɴᴇʀ
{cmd} /replace - Rᴇᴘʟᴀᴄᴇ Fɪʟᴇ Iɴ Cᴏɴᴛᴀɪɴᴇʀ
{cmd} /env - Sᴇᴛ/Vɪᴇᴡ Eɴᴠ Vᴀʀɪᴀʙʟᴇs
{cmd} /projects - Mᴀɴᴀɢᴇ Pʀᴏᴊᴇᴄᴛs
{cmd} /logs - Vɪᴇᴡ Pʀᴏᴊᴇᴄᴛ Lᴏɢs
{cmd} /premium - Gᴇᴛ Pʀᴇᴍɪᴜᴍ
{cmd} /help - Fᴜʟʟ Hᴇʟᴘ

<b>{req} 𝑹𝒆𝒒𝒖𝒊𝒓𝒆𝒎𝒆𝒏𝒕𝒔</b>
𝚈𝙾𝚄𝚁 <b>.zip</b> 𝙼𝚄𝚂𝚃 𝙲𝙾𝙽𝚃𝙰𝙸𝙽
{check} <b>Dockerfile</b>
{check} <b>requirements.txt</b>

Vɪᴅᴇᴏ Hᴇʟᴘ = https://t.me/TEAM_x_OG/108421

{support} <b>Sᴜᴘᴘᴏʀᴛ</b> @TEAM_X_OG {verified}
{updates} <b>Uᴘᴅᴀᴛᴇs</b> @CrimeZone_Update {verified}
{dev} <b>Dᴇᴠᴇʟᴏᴘᴇʀ</b> @MR_ARMAN_08 {verified}
"""

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Uᴘʟᴏᴀᴅ Pʀᴏᴊᴇᴄᴛ", callback_data="upload", icon_custom_emoji_id="5258301131615912800", style="success"),
        types.InlineKeyboardButton("My Projects", callback_data="my_projects", icon_custom_emoji_id="5258301131615912800", style="primary")
    )
    markup.row(
        types.InlineKeyboardButton("Cᴏɴɴᴇᴄᴛ GɪᴛHᴜʙ", callback_data="connect_github", icon_custom_emoji_id="5323375426658124630", style="primary"),
        types.InlineKeyboardButton("Gᴇᴛ Pʀᴇᴍɪᴜᴍ", callback_data="premium", icon_custom_emoji_id="5258301131615912800", style="success")
    )
    markup.row(
        types.InlineKeyboardButton("H𝙴𝙻𝙿", callback_data="help", icon_custom_emoji_id="5258301131615912800", style="primary"),
        types.InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url="https://t.me/TEAM_X_OG", icon_custom_emoji_id="5258301131615912800", style="primary")
    )

    try:
        bot.send_video(message.chat.id, START_VIDEO, caption=welcome_text, reply_markup=markup, parse_mode="HTML")
    except Exception as _e:
        try:
            import re as _re
            plain_text = _re.sub(r'<[^>]+>', '', welcome_text)
            bot.send_message(message.chat.id, plain_text, reply_markup=markup)
        except Exception:
            pass
    logger.log_action(user_id, "start_command", {"username": username})


# ════════════════════════════════════════════════════════════════════
#  GITHUB AUTH
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['connect'])
@check_maintenance
@check_banned
def connect_github(message):
    user_id = message.from_user.id

    if db.is_github_connected(user_id):
        gh = db.get_github_info(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Rᴇ-Cᴏɴɴᴇᴄᴛ", callback_data="github_reconnect", icon_custom_emoji_id="5258301131615912800", style="success"),
            types.InlineKeyboardButton("Dɪsᴄᴏɴɴᴇᴄᴛ", callback_data="github_disconnect", icon_custom_emoji_id="5258301131615912800", style="danger")
        )
        bot.reply_to(message,
            f"{github}<b>GitHub Already Connected</b>\n\n"
            f"{check} Account: <code>@{gh['github_username']}</code>\n"
            f"{check} Connected: {gh['connected_at'].strftime('%Y-%m-%d')}\n\n"
            f"Use /repos to browse your repositories.",
            reply_markup=markup
        )
        return

    oauth_url = github_auth.build_oauth_url(user_id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Cᴏɴɴᴇᴄᴛ GɪᴛHᴜʙ", url=oauth_url, icon_custom_emoji_id="5258301131615912800", style="success"))

    bot.reply_to(message,
        f"{github} <b>Connect Your GitHub Account</b>\n\n"
        f"{check} Tap the button below to authorize\n"
        f"{check} Both <b>public & private</b> repos will be accessible\n"
        f"{check} We only read/clone repos, never modify\n\n"
        f"{i} After connecting, use /repos to pick a repo.",
        reply_markup=markup
    )
    logger.log_action(user_id, "github_connect_initiated", {})


@bot.message_handler(commands=['disconnect'])
@check_maintenance
@check_banned
def disconnect_github(message):
    user_id = message.from_user.id
    if not db.is_github_connected(user_id):
        bot.reply_to(message, f"{i} No GitHub account connected. Use /connect to link one.")
        return
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Yes, Disconnect", callback_data="github_disconnect", icon_custom_emoji_id="5855178350263276469", style="danger"),
        types.InlineKeyboardButton("Cancel", callback_data="cancel", icon_custom_emoji_id="5818711397860642669", style="success")
    )
    bot.reply_to(message, f"{warn} <b>Disconnect GitHub?</b>\n\nYour token will be deleted. You can reconnect anytime.", reply_markup=markup)


@bot.message_handler(commands=['repos'])
@check_maintenance
@check_banned
def repos_command(message):
    user_id = message.from_user.id
    if not db.is_github_connected(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("Connect GitHub", callback_data="connect_github", icon_custom_emoji_id="5323375426658124630", style="success"))
        bot.reply_to(message,
            f"{github} <b>GitHub Not Connected</b>\n\n"
            f"Connect your GitHub account first to browse & deploy your repos.",
            reply_markup=markup
        )
        return

    status_msg = bot.reply_to(message, f"{load} Fᴇᴛᴄʜɪɴɢ Yᴏᴜʀ Rᴇᴘᴏsɪᴛᴏʀɪᴇs...")
    access_token = db.get_github_token(user_id)
    repos = github_auth.get_user_repos(access_token, page=1)

    if not repos:
        bot.edit_message_text(f"{empty} Nᴏ Rᴇᴘᴏsɪᴛᴏʀɪᴇs Fᴏᴜɴᴅ.", message.chat.id, status_msg.message_id)
        return

    markup = types.InlineKeyboardMarkup()
    text = f"{github} <b>Yᴏᴜʀ GɪᴛHᴜʙ Rᴇᴘᴏsɪᴛᴏʀɪᴇs</b>\n\nSᴇʟᴇᴄᴛ A Rᴇᴘᴏ Tᴏ Dᴇᴘʟᴏʏ:\n\n"

    for repo in repos[:50]:
        lock = "🔒" if repo['private'] else "🌐"
        lang = repo.get('language') or '?'
        markup.row(
            types.InlineKeyboardButton(
                f"{lock} {repo['name']} ({lang})",
                callback_data=f"deploy_repo_{repo['full_name'].replace('/', '__')}",
                icon_custom_emoji_id="6123067735531327869",
                style="primary"
            )
        )

    markup.row(types.InlineKeyboardButton("« Back", callback_data="cancel", style="success"))
    bot.edit_message_text(text, message.chat.id, status_msg.message_id, reply_markup=markup)
    logger.log_action(user_id, "repos_browsed", {"count": len(repos)})


# ════════════════════════════════════════════════════════════════════
#  /upload — ZIP upload
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['upload'])
@check_maintenance
@check_banned
@check_restricted
@check_rate_limit
def upload_command(message):
    user_id = message.from_user.id
    limits  = get_user_limits(user_id)
    user_projects = db.get_user_projects(user_id)

    if len(user_projects) >= limits['max_projects']:
        bot.reply_to(message,
            f"{limit} 𝚈𝙾𝚄'𝚅𝙴 𝚁𝙴𝙰𝙲𝙷𝙴𝙳 𝚈𝙾𝚄𝚁 𝙿𝚁𝙾𝙹𝙴𝙲𝚃 𝙻𝙸𝙼𝙸𝚃 ({limits['max_projects']}).\n"
            f"𝙳𝙴𝙻𝙴𝚃𝙴 𝙰 𝙿𝚁𝙾𝙹𝙴𝙲𝚃 𝙵𝙸𝚁𝚂𝚃 𝙾𝚁 𝚄𝙿𝙶𝚁𝙰𝙳𝙴 𝚃𝙾 /premium.")
        return

    upload_text = f"""
{upload} 𝑼𝒑𝒍𝒐𝒂𝒅 𝒀𝒐𝒖𝒓 𝑷𝒓𝒐𝒋𝒆𝒄𝒕

Pʟᴇᴀsᴇ Sᴇɴᴅ Mᴇ A .zip Fɪʟᴇ Cᴏɴᴛᴀɪɴɪɴɢ
{check} <code>Dockerfile</code>
{check} <code>requirements.txt</code>
{check} <b>Yᴏᴜʀ Pʏᴛʜᴏɴ Bᴏᴛ Fɪʟᴇs</b>

<b>Mᴀx Sɪᴢᴇ</b> {limits['max_upload_size'] // (1024*1024)}MB
<b>Tɪᴇʀ</b> {premium if limits['tier'] == 'Premium' else free} {limits['tier']}

{send} Sᴇɴᴅ Tʜᴇ .ZIP Fɪʟᴇ Nᴏᴡ Oʀ /cancel Tᴏ Aʙᴏʀᴛ.
"""
    try:
        msg = bot.send_video(message.chat.id, UPLOAD_VIDEO, caption=upload_text, parse_mode="HTML")
    except Exception:
        msg = bot.send_message(message.chat.id, upload_text, parse_mode="HTML")

    bot.register_next_step_handler(msg, process_upload, limits)
    logger.log_action(user_id, "upload_initiated", {})


def process_upload(message, limits):
    user_id = message.from_user.id
    if message.text and message.text.lower() == '/cancel':
        bot.reply_to(message, f"{upload} Uᴘʟᴏᴀᴅ Cᴀɴᴄᴇʟʟᴇᴅ.")
        return
    if not message.document:
        bot.reply_to(message, f"{zip} Pʟᴇᴀsᴇ Sᴇɴᴅ A .ZIP Fɪʟᴇ!")
        return
    if not message.document.file_name.endswith('.zip'):
        bot.reply_to(message, f"{zip} Oɴʟʏ .ZIP Fɪʟᴇs Aʀᴇ Sᴜᴘᴘᴏʀᴛᴇᴅ!")
        return
    if message.document.file_size > limits['max_upload_size']:
        bot.reply_to(message, f"{large} Fɪʟᴇ Tᴏᴏ Lᴀʀɢᴇ! Mᴀx {limits['max_upload_size'] // (1024*1024)}MB")
        return

    status_msg = bot.reply_to(message, f"{load}")
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_dir  = tempfile.mkdtemp()
        zip_path  = os.path.join(temp_dir, 'project.zip')
        with open(zip_path, 'wb') as f:
            f.write(downloaded_file)

        bot.edit_message_text("Vᴀʟɪᴅᴀᴛɪɴɢ Fɪʟᴇs...", message.chat.id, status_msg.message_id)
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        has_dockerfile = has_requirements = False
        for root, dirs, files in os.walk(extract_dir):
            if 'Dockerfile'       in files: has_dockerfile   = True
            if 'requirements.txt' in files: has_requirements = True

        if not has_dockerfile or not has_requirements:
            missing_list = []
            if not has_dockerfile:   missing_list.append('Dockerfile')
            if not has_requirements: missing_list.append('requirements.txt')
            bot.edit_message_text(
                f"{missing} Mɪssɪɴɢ Rᴇϙᴜɪʀᴇᴅ Fɪʟᴇs: {', '.join(missing_list)}\n\n𝙿𝙻𝙴𝙰𝚂𝙴 𝙰𝙳𝙳 𝚃𝙷𝙴𝚂𝙴 𝙵𝙸𝙻𝙴𝚂 𝙰𝙽𝙳 𝚁𝙴-𝚄𝙿𝙻𝙾𝙰𝙳!",
                message.chat.id, status_msg.message_id
            )
            shutil.rmtree(temp_dir); return

        bot.edit_message_text(f"Vᴀʟɪᴅᴀᴛɪᴏɴ Pᴀssᴇᴅ. {verified}\n\nPʟᴇᴀsᴇ Eɴᴛᴇʀ A Pʀᴏᴊᴇᴄᴛ Nᴀᴍᴇ {enter}", message.chat.id, status_msg.message_id)
        bot.register_next_step_handler(message, save_project, extract_dir, temp_dir, limits)
    except Exception as e:
        bot.edit_message_text(f"{err} Eʀʀᴏʀ: {html.escape(str(e))}", message.chat.id, status_msg.message_id)
        logger.log_action(user_id, "upload_error", {"error": str(e)})


def save_project(message, extract_dir, temp_dir, limits, source_url=None):
    user_id      = message.from_user.id
    project_name = message.text.strip()

    if not project_name or len(project_name) > 50:
        bot.reply_to(message, f"{invalid} Iɴᴠᴀʟɪᴅ Pʀᴏᴊᴇᴄᴛ Nᴀᴍᴇ! (1-50 Cʜᴀʀᴀᴄᴛᴇʀs)")
        shutil.rmtree(temp_dir); return

    if db.project_name_exists(user_id, project_name):
        bot.reply_to(message, f"{not_accepted} Pʀᴏᴊᴇᴄᴛ Nᴀᴍᴇ Aʟʀᴇᴀᴅʏ Exɪsᴛs! Cʜᴏᴏsᴇ A Dɪғғᴇʀᴇɴᴛ Nᴀᴍᴇ.")
        shutil.rmtree(temp_dir); return

    status_msg = bot.reply_to(message, f"{deploying} 𝐃𝐞𝐩𝐥𝐨𝐲𝐢𝐧𝐠 𝐏𝐫𝐨𝐣𝐞𝐜𝐭\n\nTʜɪs Mᴀʏ Tᴀᴋᴇ A Fᴇᴡ Mɪɴᴜᴛᴇs. {load}\nWʜɪʟᴇ Jᴏɪɴ Mᴇ Iɴ @TEAM_X_OG {verified}")
    try:
        deployment_result = docker_manager.deploy_project(user_id, project_name, extract_dir, limits)
        if deployment_result['success']:
            project_data = {
                'user_id': user_id, 'name': project_name,
                'container_id': deployment_result['container_id'],
                'created_at': datetime.now(), 'status': 'running',
                'limits': limits, 'usage': {'cpu': 0, 'memory': 0, 'uptime': 0},
                'build_logs': deployment_result.get('build_logs', ''),
                'source': source_url or 'zip_upload'
            }
            db.add_project(project_data)
            docker_manager.start_monitoring(user_id, project_name, limits)

            bot.edit_message_text(
                f"{alert} 𝐏𝐫𝐨𝐣𝐞𝐜𝐭 𝐃𝐞𝐩𝐥𝐨𝐲𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 {success}\n\n"
                f"{check} <b>Nᴀᴍᴇ</b> <code>{project_name}</code>\n"
                f"{check} <b>Cᴏɴᴛᴀɪɴᴇʀ</b> <code>{deployment_result['container_id'][:12]}</code>\n"
                f"{check} <b>Tɪᴇʀ</b> {PREMIUM_EMOJI if limits['tier'] == 'Premium' else '🆓'} {limits['tier']}\n"
                f"{check} <b>Sᴛᴀᴛᴜs</b> Rᴜɴɴɪɴɢ\n\n"
                f"{round} Usᴇ /projects Tᴏ Mᴀɴᴀɢᴇ Yᴏᴜʀ Pʀᴏᴊᴇᴄᴛ.\n"
                f"{alert} /logs - <b>Check Project Logs For Better Knowing What's Going You Can Easily Understand.</b>\n\n"
                f"Usᴇ /pip Tᴏ Iɴsᴛᴀʟʟ Lɪʙʀᴀʀɪᴇs.",
                message.chat.id, status_msg.message_id
            )
            logger.log_action(user_id, "project_deployed", {"project": project_name})
        else:
            error_text = f"{failed} 𝐃𝐞𝐩𝐥𝐨𝐲𝐦𝐞𝐧𝐭 𝐅𝐚𝐢𝐥𝐞𝐝\n\n{err} <b>Eʀʀᴏʀ</b>\n<code>{deployment_result['error'][:3800]}</code>"
            bot.edit_message_text(error_text, message.chat.id, status_msg.message_id)
            logger.log_action(user_id, "deployment_failed", {"project": project_name, "error": deployment_result['error']})
        shutil.rmtree(temp_dir)
    except Exception as e:
        bot.edit_message_text(f"{err} Eʀʀᴏʀ {html.escape(str(e))}", message.chat.id, status_msg.message_id), {"error": str(e)}


# ════════════════════════════════════════════════════════════════════
#  /github — Clone from GitHub (public URL OR private via OAuth)
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['github'])
@check_maintenance
@check_banned
@check_restricted
@check_rate_limit
def github_command(message):
    user_id = message.from_user.id
    limits  = get_user_limits(user_id)
    user_projects = db.get_user_projects(user_id)

    if len(user_projects) >= limits['max_projects']:
        bot.reply_to(message, f"{limit} Yᴏᴜ'ᴠᴇ Rᴇᴀᴄʜᴇᴅ Yᴏᴜʀ Pʀᴏᴊᴇᴄᴛ Lɪᴍɪᴛ ({limits['max_projects']}).")
        return

    is_connected = db.is_github_connected(user_id)
    gh_status = ""
    if is_connected:
        gh = db.get_github_info(user_id)
        gh_status = f"\n\n{github} <b>GɪᴛHᴜʙ</b> {verified} Connected as @{gh['github_username']}\n{check} Pʀɪᴠᴀᴛᴇ ʀᴇᴘᴏs sᴜᴘᴘᴏʀᴛᴇᴅ!"
    else:
        gh_status = f"\n\n{alert} <b>GɪᴛHᴜʙ Nᴏᴛ Cᴏɴɴᴇᴄᴛᴇᴅ</b> — Oɴʟʏ ᴘᴜʙʟɪᴄ ʀᴇᴘᴏs ᴡᴏʀᴋ.\nUsᴇ /connect ᴛᴏ ᴇɴᴀʙʟᴇ ᴘʀɪᴠᴀᴛᴇ ʀᴇᴘᴏs."

    msg = bot.reply_to(message, f"""
{clone} 𝐂𝐥𝐨𝐧𝐞 𝐟𝐫𝐨𝐦 𝐆𝐢𝐭𝐇𝐮𝐛

{check} Sᴇɴᴅ Mᴇ Tʜᴇ GɪᴛHᴜʙ Rᴇᴘᴏsɪᴛᴏʀʏ URL.

𝑬𝒙𝒂𝒎𝒑𝒍𝒆
<code>https://github.com/username/repo</code>

{i} Tʜᴇ Rᴇᴘᴏsɪᴛᴏʀʏ Mᴜsᴛ Cᴏɴᴛᴀɪɴ:
{check} <b>Dockerfile</b>
{check} <b>requirements.txt</b>{gh_status}

Sᴇɴᴅ Tʜᴇ URL Nᴏᴡ Oʀ /cancel Tᴏ Aʙᴏʀᴛ.
""")
    bot.register_next_step_handler(msg, process_github_clone, limits)
    logger.log_action(user_id, "github_clone_initiated", {})


def process_github_clone(message, limits):
    user_id = message.from_user.id
    if message.text and message.text.lower() == '/cancel':
        bot.reply_to(message, f"{cancel} Cʟᴏɴᴇ Cᴀɴᴄᴇʟʟᴇᴅ.")
        return
    if not message.text or not message.text.startswith('https://github.com/'):
        bot.reply_to(message, f"{invalid} Iɴᴠᴀʟɪᴅ GɪᴛHᴜʙ URL!")
        return

    repo_url   = message.text.strip()
    status_msg = bot.reply_to(message, f"{upload} Cʟᴏɴɪɴɢ Rᴇᴘᴏsɪᴛᴏʀʏ...")
    try:
        temp_dir  = tempfile.mkdtemp()
        clone_dir = os.path.join(temp_dir, 'repo')

        access_token = db.get_github_token(user_id)
        if access_token:
            parts = repo_url.replace("https://github.com/", "").rstrip("/")
            success_clone, err_clone = github_auth.clone_private_repo(access_token, parts, clone_dir)
            if not success_clone:
                result = subprocess.run(['git', 'clone', '--depth', '1', repo_url, clone_dir], capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    bot.edit_message_text(f"{failed} Cʟᴏɴᴇ Fᴀɪʟᴇᴅ\n<code>{html.escape(result.stderr[:500])}</code>", message.chat.id, status_msg.message_id)
                    shutil.rmtree(temp_dir); return
        else:
            result = subprocess.run(['git', 'clone', '--depth', '1', repo_url, clone_dir], capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                bot.edit_message_text(f"{failed} Cʟᴏɴᴇ Fᴀɪʟᴇᴅ\n<code>{html.escape(result.stderr[:500])}</code>", message.chat.id, status_msg.message_id)
                shutil.rmtree(temp_dir); return

        bot.edit_message_text(f"{validate} Vᴀʟɪᴅᴀᴛɪɴɢ Fɪʟᴇs...", message.chat.id, status_msg.message_id)
        has_dockerfile   = os.path.exists(os.path.join(clone_dir, 'Dockerfile'))
        has_requirements = os.path.exists(os.path.join(clone_dir, 'requirements.txt'))

        if not has_dockerfile or not has_requirements:
            missing_list = []
            if not has_dockerfile:   missing_list.append('Dockerfile')
            if not has_requirements: missing_list.append('requirements.txt')
            bot.edit_message_text(f"{missing} Mɪssɪɴɢ Rᴇϙᴜɪʀᴇᴅ Fɪʟᴇs: {', '.join(missing_list)}", message.chat.id, status_msg.message_id)
            shutil.rmtree(temp_dir); return

        bot.edit_message_text(f"{security} Sᴇᴄᴜʀɪᴛʏ Sᴄᴀɴɴɪɴɢ...", message.chat.id, status_msg.message_id)
        scan_result = scanner.scan_directory(clone_dir)
        if not scan_result['safe']:
            bot.edit_message_text(f"{alert} Sᴇᴄᴜʀɪᴛʏ Aʟᴇʀᴛ! Dᴇᴛᴇᴄᴛᴇᴅ {', '.join(scan_result['threats'])}", message.chat.id, status_msg.message_id)
            logger.log_action(user_id, "github_security_threat", {"url": repo_url, "threats": scan_result['threats']})
            shutil.rmtree(temp_dir); return

        bot.edit_message_text(f"{validate} Vᴀʟɪᴅᴀᴛɪᴏɴ Pᴀssᴇᴅ.\n\nPʟᴇᴀsᴇ Eɴᴛᴇʀ A Pʀᴏᴊᴇᴄᴛ Nᴀᴍᴇ", message.chat.id, status_msg.message_id)
        bot.register_next_step_handler(message, save_project, clone_dir, temp_dir, limits, source_url=repo_url)

    except subprocess.TimeoutExpired:
        bot.edit_message_text(f"{timeout} Cʟᴏɴᴇ Tɪᴍᴇᴏᴜᴛ! Rᴇᴘᴏsɪᴛᴏʀʏ Tᴏᴏ Lᴀʀɢᴇ.", message.chat.id, status_msg.message_id)
        shutil.rmtree(temp_dir)
    except Exception as e:
        bot.edit_message_text(f"{err} Eʀʀᴏʀ {html.escape(str(e))}", message.chat.id, status_msg.message_id)
        logger.log_action(user_id, "github_clone_error", {"error": str(e)})


# ════════════════════════════════════════════════════════════════════
#  /pip — Install safe libraries into a running container
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['pip'])
@check_maintenance
@check_banned
@check_restricted
@check_rate_limit
def pip_command(message):
    user_id  = message.from_user.id
    projects = db.get_user_projects(user_id)
    running  = [p for p in projects if p['status'] == 'running']

    if not running:
        bot.reply_to(message,
            f"{empty} Yᴏᴜ Hᴀᴠᴇ Nᴏ Rᴜɴɴɪɴɢ Pʀᴏᴊᴇᴄᴛs.\n\nDeploy one first with /upload or /github."
        )
        return

    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 2:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("📦 Safe Libraries List", callback_data="pip_list"))
        bot.reply_to(message,
            f"📦 <b>Iɴsᴛᴀʟʟ A Lɪʙʀᴀʀʏ</b>\n\n"
            f"<b>Usᴀɢᴇ:</b> <code>/pip library_name</code>\n"
            f"<b>Exᴀᴍᴘʟᴇ:</b> <code>/pip requests</code>\n\n"
            f"{i} Oɴʟʏ sᴀғᴇ/ᴀᴘᴘʀᴏᴠᴇᴅ ʟɪʙʀᴀʀɪᴇs ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ.",
            reply_markup=markup
        )
        return

    library = parts[1].strip()
    safe, reason = is_safe_library(library)
    if not safe:
        bot.reply_to(message, f"{err} {reason}")
        return

    if len(running) == 1:
        project = running[0]
    elif len(parts) == 3:
        proj_name = parts[2].strip()
        project = next((p for p in running if p['name'].lower() == proj_name.lower()), None)
        if not project:
            bot.reply_to(message, f"{not_found} Project '{proj_name}' not found or not running.")
            return
    else:
        markup = types.InlineKeyboardMarkup()
        for p in running:
            markup.row(types.InlineKeyboardButton(
                f"🟢 {p['name']}", callback_data=f"pip_install_{p['_id']}_{library}"
            ))
        bot.reply_to(message, f"{select} <b>Sᴇʟᴇᴄᴛ Pʀᴏᴊᴇᴄᴛ Fᴏʀ pip install {library}</b>", reply_markup=markup)
        return

    _do_pip_install(message, project, library)


def _do_pip_install(message, project, library):
    user_id    = message.from_user.id
    status_msg = bot.reply_to(message, f"📦 Iɴsᴛᴀʟʟɪɴɢ <code>{library}</code>... {load}")
    success, output = pip_install_in_container(docker_client, project['container_id'], library)
    db.log_pip_install(user_id, project['_id'], library, success)

    if success:
        bot.edit_message_text(
            f"📦 {verified} <b>Installed Successfully!</b>\n\n"
            f"{check} Library: <code>{library}</code>\n"
            f"{check} Project: <code>{project['name']}</code>\n\n"
            f"<pre>{html.escape(output[-500:])}</pre>",
            message.chat.id, status_msg.message_id
        )
        logger.log_action(user_id, "pip_install_success", {"library": library, "project": project['name']})
    else:
        bot.edit_message_text(
            f"📦 {err} <b>Iɴsᴛᴀʟʟ Fᴀɪʟᴇᴅ</b>\n\n<pre>{html.escape(output[-800:])}</pre>",
            message.chat.id, status_msg.message_id
        )
        logger.log_action(user_id, "pip_install_failed", {"library": library, "error": output})


# ════════════════════════════════════════════════════════════════════
#  /projects
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['projects'])
@check_maintenance
@check_banned
def projects_command(message, user_id=None):
    if user_id is None:
        user_id = message.from_user.id
        
    projects = db.get_user_projects(user_id)

    if not projects:
        bot.reply_to(message, f"{empty} 𝚈𝙾𝚄 𝙳𝙾𝙽'𝚃 𝙷𝙰𝚅𝙴 𝙰𝙽𝚈 𝙿𝚁𝙾𝙹𝙴𝙲𝚃𝚂 𝚈𝙴𝚃.\n\nUsᴇ /upload Tᴏ Dᴇᴘʟᴏʏ Yᴏᴜʀ Fɪʀsᴛ Pʀᴏᴊᴇᴄᴛ")
        return

    text   = f"{project_em} 𝐘𝐨𝐮𝐫 𝐏𝐫𝐨𝐣𝐞𝐜𝐭𝐬\n\n"
    markup = types.InlineKeyboardMarkup()

    for i_p, project in enumerate(projects, 1):
        status_emoji = "🟢" if project['status'] == 'running' else "🔴"
        source = project.get('source', 'zip_upload')
        src_icon = "🐙" if source and source.startswith('http') else "📦"
        text += f"{i_p}. {status_emoji} <b>{project['name']}</b> {src_icon}\n"
        text += f"   Status: {project['status'].title()} | Uptime: {project['usage'].get('uptime', 0)}h\n\n"
        markup.row(
            types.InlineKeyboardButton(f"• {project['name']}", callback_data=f"project_{project['_id']}"),
            types.InlineKeyboardButton("• Dᴇʟᴇᴛᴇ", callback_data=f"delete_{project['_id']}")
        )

    markup.row(types.InlineKeyboardButton("➕ Nᴇᴡ Pʀᴏᴊᴇᴄᴛ", callback_data="upload"))
    try:
        bot.send_photo(message.chat.id, PROJECTS_PHOTO, caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    logger.log_action(user_id, "view_projects", {})


@bot.message_handler(commands=['premium'])
@check_maintenance
@check_banned
def premium_command(message):
    user_id          = message.from_user.id
    is_premium_user  = db.is_premium(user_id) or is_owner(user_id)

    if is_premium_user:
        expiry = db.get_premium_expiry(user_id)
        expiry_str = expiry.strftime('%Y-%m-%d') if expiry else "Lifetime"
        days_left  = (expiry - datetime.now()).days if expiry else "∞"

        text = f"""
<b>Yᴏᴜ'ʀᴇ ᴀ Pʀᴇᴍɪᴜᴍ Usᴇʀ!</b> {verified}

{check} Exᴘɪʀʏ: <code>{expiry_str}</code> ({days_left} days left)

{benifits}   𝐘𝐨𝐮𝐫 𝐁𝐞𝐧𝐞𝐟𝐢𝐭𝐬
{check} 3 Pʀᴏᴊᴇᴄᴛs Rᴜɴɴɪɴɢ
{check} 500MB Uᴘʟᴏᴀᴅ Sɪᴢᴇ
{check} 2 CPU Cᴏʀᴇs
{check} 1GB RAM
{check} 30GB Sᴛᴏʀᴀɢᴇ
{check} 720 Hᴏᴜʀs/Mᴏɴᴛʜ
{check} Fᴀsᴛ Dᴇᴘʟᴏʏᴍᴇɴᴛ
{check} Aᴜᴛᴏ Rᴇsᴛᴀʀᴛ ᴏɴ Cʀᴀsʜ
{check} 24/7 Uᴘᴛɪᴍᴇ
{check} Pʀɪᴠᴀᴛᴇ Rᴇᴘᴏ Sᴜᴘᴘᴏʀᴛ

Tʜᴀɴᴋ Yᴏᴜ Fᴏʀ Yᴏᴜʀ Sᴜᴘᴘᴏʀᴛ! {thanks}
"""
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("• Sᴜᴘᴘᴏʀᴛ", url="https://t.me/TEAM_X_OG"))
    else:
        text = f"""
<b>Gᴇᴛ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss!</b> {premium}

{free} 𝐅𝐫𝐞𝐞 𝐓𝐢𝐞𝐫:
• 1 Pʀᴏᴊᴇᴄᴛs | 50MB | 0.25 CPU | 256MB RAM
• 3GB Sᴛᴏʀᴀɢᴇ | 200h/ᴍᴏɴᴛʜ | Aᴜᴛᴏ Sᴛᴏᴘ 12ʜ

{premium} 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐓𝐢𝐞𝐫:
{check} 3 Pʀᴏᴊᴇᴄᴛs
{check} 500MB Uᴘʟᴏᴀᴅ
{check} 2 CPU Cᴏʀᴇs + 1GB RAM
{check} 30GB Sᴛᴏʀᴀɢᴇ | 720ʜ/ᴍᴏɴᴛʜ
{check} 24/7 Uᴘᴛɪᴍᴇ + Aᴜᴛᴏ Rᴇsᴛᴀʀᴛ
{check} 🔒 Pʀɪᴠᴀᴛᴇ Rᴇᴘᴏ Dᴇᴘʟᴏʏ
{check} Pʀɪᴏʀɪᴛʏ Sᴜᴘᴘᴏʀᴛ

💰 <b>𝐏𝐚𝐲 𝐰𝐢𝐭𝐡 ₹ — Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ</b>
₹150  = 7 Dᴀʏs
₹249  = 20 Dᴀʏs + 2 Dᴀʏs Fʀᴇᴇ
₹349  = 35 Dᴀʏs + 5 Dᴀʏs Fʀᴇᴇ

<b>𝙲𝙾𝙽𝚃𝙰𝙲𝚃 @MR_ARMAN_08 {verified} 𝚃𝙾 𝙶𝙴𝚃 𝙿𝚁𝙴𝙼𝙸𝚄𝙼!</b>
"""
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("• Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ", url="https://t.me/m/IHKlKnQPMTU1", icon_custom_emoji_id="5258301131615912800", style="success"))
        markup.row(types.InlineKeyboardButton("• Sᴜᴘᴘᴏʀᴛ", url="https://t.me/TEAM_X_OG", icon_custom_emoji_id="5258301131615912800", style="success"))

    try:
        bot.send_video(message.chat.id, PREMIUM_VIDEO, caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    logger.log_action(user_id, "premium_info_viewed", {"is_premium": is_premium_user})


@bot.message_handler(commands=['help'])
@check_maintenance
@check_banned
def help_command(message):
    text = f"""
{help} 𝐇𝐞𝐥𝐩 & 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬

{project_em} 𝐏𝐫𝐨𝐣𝐞𝐜𝐭 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭
{check} /upload — Uᴘʟᴏᴀᴅ Nᴇᴡ Pʀᴏᴊᴇᴄᴛ (.ZIP)
{check} /projects — Vɪᴇᴡ & Mᴀɴᴀɢᴇ Pʀᴏᴊᴇᴄᴛs
{check} /github — Cʟᴏɴᴇ Fʀᴏᴍ GɪᴛHᴜʙ (Public/Private)
{check} /repos — Bʀᴏᴡsᴇ Yᴏᴜʀ GɪᴛHᴜʙ Rᴇᴘᴏs
{check} /logs — Vɪᴇᴡ Pʀᴏᴊᴇᴄᴛ Lᴏɢs
{check} /stop — Sᴛᴏᴘ Rᴜɴɴɪɴɢ Pʀᴏᴊᴇᴄᴛ
{check} /pip — Iɴsᴛᴀʟʟ Pʏᴛʜᴏɴ Lɪʙʀᴀʀʏ
{check} /update — Uᴘᴅᴀᴛᴇ Pʀᴏᴊᴇᴄᴛ Fʀᴏᴍ Rᴇᴘᴏ
{check} /exec — Rᴜɴ Cᴏᴍᴍᴀɴᴅ Iɴ Cᴏɴᴛᴀɪɴᴇʀ
{check} /replace — Rᴇᴘʟᴀᴄᴇ Fɪʟᴇ Iɴ Cᴏɴᴛᴀɪɴᴇʀ
{check} /env — Sᴇᴛ/Vɪᴇᴡ Eɴᴠ Vᴀʀɪᴀʙʟᴇs

🐙 𝐆𝐢𝐭𝐇𝐮𝐛 𝐈𝐧𝐭𝐞𝐠𝐫𝐚𝐭𝐢𝐨𝐧
{check} /connect — Lɪɴᴋ Yᴏᴜʀ GɪᴛHᴜʙ Aᴄᴄᴏᴜɴᴛ
{check} /repos — Lɪsᴛ & Dᴇᴘʟᴏʏ Yᴏᴜʀ Rᴇᴘᴏs
{check} /disconnect — Uɴʟɪɴᴋ GɪᴛHᴜʙ

{premium} 𝐏𝐫𝐞𝐦𝐢𝐮𝐦
{check} /premium — Pʀᴇᴍɪᴜᴍ Iɴғᴏ & Uᴘɢʀᴀᴅᴇ

{i} 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧
{check} /help — Tʜɪs Hᴇʟᴘ Mᴇssᴀɢᴇ
{check} /support — Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ
{check} /start — Sᴛᴀʀᴛ Oᴠᴇʀ

{req} 𝐔𝐩𝐥𝐨𝐚𝐝 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐦𝐞𝐧𝐭𝐬
• <code>Dockerfile</code> + <code>requirements.txt</code>

{security} 𝐒𝐞𝐜𝐮𝐫𝐢𝐭𝐲
Aʟʟ Fɪʟᴇs Aʀᴇ Sᴄᴀɴɴᴇᴅ Fᴏʀ Mᴀʟᴡᴀʀᴇ / DDoS / Mɪɴᴇʀs

{help} 𝐍𝐞𝐞𝐝 𝐇𝐞𝐥𝐩?
{support} 𝚂𝚄𝙿𝙿𝙾𝚁𝚃 @TEAM_X_OG {verified}
{dev} 𝙳𝙴𝚅𝙴𝙻𝙾𝙿𝙴𝚁 @MR_ARMAN_08 {verified}
"""
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("• Sᴜᴘᴘᴏʀᴛ", url="https://t.me/TEAM_X_OG", icon_custom_emoji_id="5258301131615912800", style="success"),
        types.InlineKeyboardButton("• Uᴘᴅᴀᴛᴇs", url="https://t.me/CrimeZone_Update", icon_custom_emoji_id="5258301131615912800", style="success")
    )
    try:
        bot.send_video(message.chat.id, HELP_VIDEO, caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=['support'])
@check_maintenance
@check_banned
def support_command(message):
    text = f"""
{help} 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 & 𝐂𝐨𝐧𝐭𝐚𝐜𝐭

{support} <b>Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ</b> @TEAM_X_OG {verified}
{updates} <b>Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ</b> @CrimeZone_Update {verified}
{dev} <b>Dᴇᴠᴇʟᴏᴘᴇʀ</b> @MR_ARMAN_08 {verified}

{premium} Nᴇᴇᴅ Pʀᴇᴍɪᴜᴍ? Cᴏɴᴛᴀᴄᴛ @MR_ARMAN_08
{issue} Rᴇᴘᴏʀᴛ Issᴜᴇs — Jᴏɪɴ @TEAM_X_OG
"""
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("• Sᴜᴘᴘᴏʀᴛ", url="https://t.me/TEAM_X_OG"),
        types.InlineKeyboardButton("• Uᴘᴅᴀᴛᴇs", url="https://t.me/CrimeZone_Update")
    )
    markup.row(types.InlineKeyboardButton("• Cᴏɴᴛᴀᴄᴛ Dᴇᴠ", url="https://t.me/m/IHKlKnQPMTU1"))
    try:
        bot.send_photo(message.chat.id, HELP_PHOTO_URL, caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=['logs'])
@check_maintenance
@check_banned
def logs_command(message):
    user_id  = message.from_user.id
    projects = db.get_user_projects(user_id)
    if not projects:
        bot.reply_to(message, f"{logs} Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴʏ Pʀᴏᴊᴇᴄᴛs Yᴇᴛ.")
        return
    if len(projects) == 1:
        show_project_logs_text(message, projects[0])
    else:
        text   = f"{select} <b>Sᴇʟᴇᴄᴛ A Pʀᴏᴊᴇᴄᴛ Tᴏ Vɪᴇᴡ Lᴏɢs</b>\n\n"
        markup = types.InlineKeyboardMarkup()
        for project in projects:
            se = "🟢" if project['status'] == 'running' else "🔴"
            markup.row(types.InlineKeyboardButton(f"{se} {project['name']}", callback_data=f"logs_{project['_id']}"))
        bot.send_message(message.chat.id, text, reply_markup=markup)


def show_project_logs_text(message, project):
    user_id = message.from_user.id
    if project['user_id'] != user_id and not is_admin(user_id):
        bot.reply_to(message, f"{r} Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aᴄᴄᴇss Tᴏ Tʜɪs Pʀᴏᴊᴇᴄᴛ.")
        return
    status_msg = bot.reply_to(message, f"{logs} Fᴇᴛᴄʜɪɴɢ Lᴏɢs...")
    try:
        build_logs   = project.get('build_logs', '')
        runtime_logs = docker_manager.get_container_logs(project['container_id'], lines=50) or ''
        log_text     = f"{logs} 𝐋𝐨𝐠𝐬 𝐅𝐨ʀ <b>{html.escape(project['name'])}</b>\n\n"
        truncated = False
        if build_logs:
            build_raw = chr(10).join(build_logs.split(chr(10))[-10:])
            if len(build_raw) > 800:
                build_raw = build_raw[:800]
                truncated = True
            log_text += f"<b>{build} Bᴜɪʟᴅ Lᴏɢs</b>\n<pre>{html.escape(build_raw)}</pre>\n\n"
        runtime_raw = runtime_logs
        if len(runtime_raw) > 2500:
            runtime_raw = runtime_raw[:2500]
            truncated = True
        log_text += f"<b>{logs} Rᴜɴᴛɪᴍᴇ Lᴏɢs</b>\n<pre>{html.escape(runtime_raw)}</pre>"
        if truncated: log_text += "\n\n... (Tʀᴜɴᴄᴀᴛᴇᴅ)"
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("↻ Rᴇғʀᴇsʜ", callback_data=f"logs_{project['_id']}"),
            types.InlineKeyboardButton("⎙ Dᴇᴛᴀɪʟs", callback_data=f"project_{project['_id']}")
        )
        bot.edit_message_text(log_text, message.chat.id, status_msg.message_id, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"{err} Eʀʀᴏʀ: {html.escape(str(e))}", message.chat.id, status_msg.message_id)


@bot.message_handler(commands=['stop'])
@check_maintenance
@check_banned
def stop_command(message):
    user_id  = message.from_user.id
    projects = db.get_user_projects(user_id)
    running  = [p for p in projects if p['status'] == 'running']
    if not running:
        bot.reply_to(message, f"{empty} Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴʏ Rᴜɴɴɪɴɢ Pʀᴏᴊᴇᴄᴛs.")
        return
    if len(running) == 1:
        confirm_stop_project(message, running[0]['_id'])
    else:
        markup = types.InlineKeyboardMarkup()
        for project in running:
            markup.row(types.InlineKeyboardButton(f"🟢 {project['name']}", callback_data=f"confirm_stop_{project['_id']}"))
        bot.send_message(message.chat.id, f"{select} <b>Sᴇʟᴇᴄᴛ A Pʀᴏᴊᴇᴄᴛ Tᴏ Sᴛᴏᴘ</b>", reply_markup=markup)


def confirm_stop_project(message, project_id):
    project = db.get_project(project_id)
    if not project:
        bot.reply_to(message, f"{not_found} Pʀᴏᴊᴇᴄᴛ Nᴏᴛ Fᴏᴜɴᴅ.")
        return
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Yᴇs, Sᴛᴏᴘ", callback_data=f"stop_{project_id}"),
        types.InlineKeyboardButton("∅ Cᴀɴᴄᴇʟ", callback_data="my_projects")
    )
    bot.send_message(message.chat.id,
        f"{warn} 𝐒𝐭𝐨𝐩 𝐏𝐫𝐨𝐣𝐞𝐜𝐭?\n\n{project_em} <b>{project['name']}</b>\n{status} Rᴜɴɴɪɴɢ\n\n𝚈𝙾𝚄 𝙲𝙰𝙽 𝚁𝙴𝚂𝚃𝙰𝚁𝚃 𝙸𝚃 𝙻𝙰𝚃𝙴𝚁.",
        reply_markup=markup
    )


# ════════════════════════════════════════════════════════════════════
#  ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id): return
    stats = db.get_stats()
    text = f"""
👑 <b>Admin Panel</b>

<b>📊 Bot Statistics:</b>
• Total Users: {stats['total_users']}
• Premium Users: {stats['premium_users']}
• Banned Users: {stats['banned_users']}
• GitHub Connected: {stats['github_connected']}
• Total Projects: {stats['total_projects']}
• Running Projects: {stats['running_projects']}

<b>💻 Server Stats:</b>
• CPU: {psutil.cpu_percent()}%
• RAM: {psutil.virtual_memory().percent}%
• Disk: {psutil.disk_usage('/').percent}%

<b>Admin Commands:</b>
/addpremium [id] [days] — Add premium
/removepremium [id] — Remove premium
/addadmin [id] — Add admin
/removeadmin [id] — Remove admin
/ban [id] [reason] — Ban user
/unban [id] — Unban user
/restrict [id] — Restrict user
/unrestrict [id] — Unrestrict user
/warn [id] [reason] — Warn user
/maintenance [on/off] — Maintenance mode
/broadcast [msg] — Broadcast message
/userinfo [id] — User information
/serverinfo — Server info
/allusers — List all users
/premiumusers — List premium users
/stopproject [id] — Stop any project
/deleteproject [id] — Delete any project
/setpremiumdays [id] [days] — Extend premium
"""
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 Users", callback_data="admin_users")
    )
    markup.row(
        types.InlineKeyboardButton("📦 Projects", callback_data="admin_projects"),
        types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['addpremium'])
def add_premium(message):
    if not is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        days    = int(parts[2]) if len(parts) > 2 else 30
        db.set_premium(user_id, True, days=days)
        db.users.update_one({'user_id': user_id}, {'$set': {'expiry_alert_sent': False}})
        bot.reply_to(message, f"✅ User {user_id} is now Premium for {days} days!")
        logger.log_action(message.from_user.id, "add_premium", {"target_user": user_id, "days": days})
        try:
            expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            bot.send_message(user_id, f"Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs Yᴏᴜ Nᴏᴡ Hᴀᴠᴇ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss! {premium}\n\n{check} Dᴜʀᴀᴛɪᴏɴ: <b>{days} days</b>\n{check} Exᴘɪʀᴇs: <code>{expiry_date}</code>\n\n/premium - Sᴇᴇ Yᴏᴜʀ Bᴇɴᴇғɪᴛs", parse_mode="HTML")
        except: pass
    except:
        bot.reply_to(message, "❌ Usage: /addpremium [user_id] [days=30]")


@bot.message_handler(commands=['setpremiumdays'])
def set_premium_days(message):
    if not is_admin(message.from_user.id): return
    try:
        parts   = message.text.split()
        user_id = int(parts[1])
        days    = int(parts[2])
        db.set_premium(user_id, True, days=days)
        db.users.update_one({'user_id': user_id}, {'$set': {'expiry_alert_sent': False}})
        expiry  = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        bot.reply_to(message, f"✅ Premium updated for {user_id} — expires {expiry}")
        try:
            bot.send_message(user_id, f"{premium} <b>Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Hᴀs Bᴇᴇɴ Exᴛᴇɴᴅᴇᴅ!</b>\n\n{check} New Expiry: <code>{expiry}</code>", parse_mode="HTML")
        except: pass
    except:
        bot.reply_to(message, "❌ Usage: /setpremiumdays [user_id] [days]")


@bot.message_handler(commands=['removepremium'])
def remove_premium(message):
    if not is_admin(message.from_user.id): return
    try:
        user_id = int(message.text.split()[1])
        db.set_premium(user_id, False)
        bot.reply_to(message, f"✅ Premium removed from user {user_id}")
        logger.log_action(message.from_user.id, "remove_premium", {"target_user": user_id})
        try:
            bot.send_message(user_id, f"{i} <b>Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Hᴀs Exᴘɪʀᴇᴅ.</b>\n\nCᴏɴᴛᴀᴄᴛ @MR_ARMAN_08 {verified} ᴛᴏ ʀᴇɴᴇᴡ.", parse_mode="HTML")
        except: pass
    except:
        bot.reply_to(message, "❌ Usage: /removepremium [user_id]")


@bot.message_handler(commands=['addadmin'])
def add_admin_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        user_id = int(message.text.split()[1])
        db.add_admin(user_id)
        bot.reply_to(message, f"✅ User {user_id} is now Admin!")
        try: bot.send_message(user_id, f"👑 You have been granted Admin access!")
        except: pass
    except:
        bot.reply_to(message, "❌ Usage: /addadmin [user_id]")


@bot.message_handler(commands=['removeadmin'])
def remove_admin_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        user_id = int(message.text.split()[1])
        db.remove_admin(user_id)
        bot.reply_to(message, f"✅ Admin removed from {user_id}")
    except:
        bot.reply_to(message, "❌ Usage: /removeadmin [user_id]")


@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message.from_user.id): return
    try:
        parts   = message.text.split(maxsplit=2)
        user_id = int(parts[1])
        reason  = parts[2] if len(parts) > 2 else "No reason specified"
        db.ban_user(user_id, reason)
        bot.reply_to(message, f"✅ User {user_id} banned!\nReason: {reason}")
        logger.log_action(message.from_user.id, "ban_user", {"target_user": user_id, "reason": reason})
        try: bot.send_message(user_id, f"{banned} Yᴏᴜ Hᴀᴠᴇ Bᴇᴇɴ Bᴀɴɴᴇᴅ!\nRᴇᴀsᴏɴ: {reason}")
        except: pass
    except:
        bot.reply_to(message, "❌ Usage: /ban [user_id] [reason]")


@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.from_user.id): return
    try:
        user_id = int(message.text.split()[1])
        db.unban_user(user_id)
        bot.reply_to(message, f"✅ User {user_id} unbanned!")
        try: bot.send_message(user_id, f"{verified} Yᴏᴜ Hᴀᴠᴇ Bᴇᴇɴ Uɴʙᴀɴɴᴇᴅ! Wᴇʟᴄᴏᴍᴇ Bᴀᴄᴋ!")
        except: pass
    except:
        bot.reply_to(message, "❌ Usage: /unban [user_id]")


@bot.message_handler(commands=['restrict'])
def restrict_user(message):
    if not is_admin(message.from_user.id): return
    try:
        user_id = int(message.text.split()[1])
        db.restrict_user(user_id, True)
        bot.reply_to(message, f"✅ User {user_id} restricted!")
        logger.log_action(message.from_user.id, "restrict_user", {"target_user": user_id})
    except:
        bot.reply_to(message, "❌ Usage: /restrict [user_id]")


@bot.message_handler(commands=['unrestrict'])
def unrestrict_user(message):
    if not is_admin(message.from_user.id): return
    try:
        user_id = int(message.text.split()[1])
        db.restrict_user(user_id, False)
        bot.reply_to(message, f"✅ User {user_id} unrestricted!")
    except:
        bot.reply_to(message, "❌ Usage: /unrestrict [user_id]")


@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not is_admin(message.from_user.id): return
    try:
        parts   = message.text.split(maxsplit=2)
        user_id = int(parts[1])
        reason  = parts[2] if len(parts) > 2 else "No reason specified"
        db.add_warning(user_id, reason)
        user     = db.get_user(user_id)
        warnings = user.get('warnings', 0) if user else 0
        bot.reply_to(message, f"⚠️ Warning issued to {user_id}!\nReason: {reason}\nTotal warnings: {warnings}/3")
        try:
            bot.send_message(user_id,
                f"{warn} <b>Yᴏᴜ Rᴇᴄᴇɪᴠᴇᴅ A Wᴀʀɴɪɴɢ!</b>\n\nRᴇᴀsᴏɴ: {reason}\nWᴀʀɴɪɴɢs: {warnings}/3\n\n3 ᴡᴀʀɴɪɴɢs = ᴘᴇʀᴍ ʙᴀɴ.",
                parse_mode="HTML"
            )
        except: pass
        logger.log_action(message.from_user.id, "warn_user", {"target_user": user_id, "reason": reason})
    except:
        bot.reply_to(message, "❌ Usage: /warn [user_id] [reason]")


@bot.message_handler(commands=['maintenance'])
def maintenance_mode_toggle(message):
    global maintenance_mode
    if not is_admin(message.from_user.id): return
    try:
        mode = message.text.split()[1].lower()
        if mode == 'on':
            maintenance_mode = True
            bot.reply_to(message, "🔧 Maintenance mode: ON")
        elif mode == 'off':
            maintenance_mode = False
            bot.reply_to(message, "✅ Maintenance mode: OFF")
        else:
            bot.reply_to(message, "❌ Usage: /maintenance [on/off]")
        logger.log_action(message.from_user.id, "maintenance_mode", {"mode": mode})
    except:
        bot.reply_to(message, "❌ Usage: /maintenance [on/off]")


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if not is_admin(message.from_user.id): return
    try:
        broadcast_text = message.text.split(maxsplit=1)[1]
        users          = db.get_all_users()
        success = failed_count = 0
        status_msg = bot.reply_to(message, f"📢 Broadcasting to {len(users)} users...")
        for user in users:
            try:
                bot.send_message(user['user_id'], broadcast_text, parse_mode="HTML")
                success += 1
                time.sleep(0.05)
            except:
                failed_count += 1
        bot.edit_message_text(f"✅ Broadcast done!\nSuccess: {success} | Failed: {failed_count}", message.chat.id, status_msg.message_id)
        logger.log_action(message.from_user.id, "broadcast", {"success": success, "failed": failed_count})
    except:
        bot.reply_to(message, "❌ Usage: /broadcast [message]")


@bot.message_handler(commands=['userinfo'])
def user_info(message):
    if not is_admin(message.from_user.id): return
    try:
        user_id  = int(message.text.split()[1])
        user     = db.get_user(user_id)
        if not user:
            bot.reply_to(message, f"{not_found} User not found!")
            return
        projects     = db.get_user_projects(user_id)
        is_prem      = db.is_premium(user_id)
        expiry       = db.get_premium_expiry(user_id)
        warnings     = db.get_user_warnings(user_id)
        gh_info      = db.get_github_info(user_id)
        expiry_str   = expiry.strftime('%Y-%m-%d') if expiry else "N/A"
        text = f"""
👤 <b>User Information</b>

<b>ID:</b> <code>{user_id}</code>
<b>Username:</b> @{user.get('username', 'N/A')}
<b>Status:</b> {'⭐ Premium' if is_prem else '🆓 Free'}
<b>Premium Expiry:</b> {expiry_str}
<b>Banned:</b> {'Yes' if db.is_banned(user_id) else 'No'}
<b>Restricted:</b> {'Yes' if db.is_restricted(user_id) else 'No'}
<b>Warnings:</b> {len(warnings)}/3
<b>GitHub:</b> {'@' + gh_info['github_username'] if gh_info else 'Not connected'}
<b>Projects:</b> {len(projects)}
<b>Joined:</b> {user.get('joined_at', 'N/A')}
"""
        bot.send_message(message.chat.id, text)
    except:
        bot.reply_to(message, "❌ Usage: /userinfo [user_id]")


@bot.message_handler(commands=['serverinfo'])
def server_info(message):
    if not is_admin(message.from_user.id): return
    vm   = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot = psutil.boot_time()
    uptime_h = int(time.time() - boot) // 3600
    try:
        containers = docker_client.containers.list()
        total_containers = len(containers)
    except:
        total_containers = 0

    text = f"""
💻 <b>Server Information</b>

<b>CPU:</b> {psutil.cpu_percent()}% ({psutil.cpu_count()} cores)
<b>RAM:</b> {vm.percent}% ({vm.used // (1024**2)}MB / {vm.total // (1024**2)}MB)
<b>Disk:</b> {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)
<b>Uptime:</b> {uptime_h}h
<b>Docker Containers:</b> {total_containers}
<b>Python:</b> {os.popen('python3 --version').read().strip()}
"""
    bot.reply_to(message, text)


@bot.message_handler(commands=['allusers'])
def all_users_cmd(message):
    if not is_admin(message.from_user.id): return
    users = db.get_all_users()
    text  = f"👥 <b>All Users ({len(users)})</b>\n\n"
    for u in users[:50]:
        icon = "⭐" if u.get('premium') else "🆓"
        ban  = " 🚫" if u.get('banned') else ""
        text += f"{icon} <code>{u['user_id']}</code> @{u.get('username','?')}{ban}\n"
    if len(users) > 50:
        text += f"\n...and {len(users) - 50} more."
    bot.reply_to(message, text)


@bot.message_handler(commands=['premiumusers'])
def premium_users_cmd(message):
    if not is_admin(message.from_user.id): return
    users = list(db.users.find({'premium': True}))
    text  = f"⭐ <b>Premium Users ({len(users)})</b>\n\n"
    for u in users:
        expiry = u.get('premium_expiry')
        exp_str = expiry.strftime('%Y-%m-%d') if expiry else "Lifetime"
        text += f"⭐ <code>{u['user_id']}</code> @{u.get('username','?')} — {exp_str}\n"
    bot.reply_to(message, text or "No premium users.")


@bot.message_handler(commands=['stopproject'])
def admin_stop_project(message):
    if not is_admin(message.from_user.id): return
    try:
        project_id = message.text.split()[1]
        project    = db.get_project(project_id)
        if not project:
            bot.reply_to(message, "❌ Project not found!")
            return
        docker_manager.stop_container(project['container_id'])
        db.update_project(project_id, {'status': 'stopped'})
        bot.reply_to(message, f"✅ Project '{project['name']}' stopped!")
        logger.log_action(message.from_user.id, "admin_stop_project", {"project_id": project_id})
    except:
        bot.reply_to(message, "❌ Usage: /stopproject [project_id]")


@bot.message_handler(commands=['deleteproject'])
def admin_delete_project(message):
    if not is_admin(message.from_user.id): return
    try:
        project_id = message.text.split()[1]
        project    = db.get_project(project_id)
        if not project:
            bot.reply_to(message, "❌ Project not found!")
            return
        docker_manager.remove_project(project['container_id'])
        db.delete_project(project_id)
        bot.reply_to(message, f"✅ Project '{project['name']}' deleted!")
        logger.log_action(message.from_user.id, "admin_delete_project", {"project_id": project_id})
    except:
        bot.reply_to(message, "❌ Usage: /deleteproject [project_id]")


# ════════════════════════════════════════════════════════════════════
#  CALLBACK HANDLER
# ════════════════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        data = call.data

        if data.startswith("vps_"):
            _handle_vps_callbacks(call)
            return

        if data == "upload":
            bot.answer_callback_query(call.id)
            upload_command(call.message)
        elif data == "my_projects":
            bot.answer_callback_query(call.id)
            projects_command(call.message, call.from_user.id)
        elif data == "premium":
            bot.answer_callback_query(call.id)
            premium_command(call.message)
        elif data == "help":
            bot.answer_callback_query(call.id)
            help_command(call.message)
        elif data == "cancel":
            bot.answer_callback_query(call.id)
            bot.delete_message(call.message.chat.id, call.message.message_id)

        elif data == "connect_github":
            bot.answer_callback_query(call.id)
            call.message.from_user = call.from_user
            connect_github(call.message)

        elif data == "github_disconnect":
            user_id = call.from_user.id
            db.remove_github_token(user_id)
            bot.answer_callback_query(call.id, "GitHub disconnected!")
            edit_message_safe(bot, f"🔴 <b>GitHub Disconnected.</b>\n\nUse /connect to re-link.", call.message.chat.id, call.message.message_id)

        elif data == "github_reconnect":
            user_id   = call.from_user.id
            oauth_url = github_auth.build_oauth_url(user_id)
            markup    = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("🐙 Re-connect GitHub", url=oauth_url))
            bot.answer_callback_query(call.id)
            edit_message_safe(bot, f"🐙 Tap below to re-authorize GitHub access.", call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif data.startswith("deploy_repo_"):
            full_name = data.replace("deploy_repo_", "").replace("__", "/")
            user_id   = call.from_user.id
            limits    = get_user_limits(user_id)
            bot.answer_callback_query(call.id, "Cloning repo...")
            fake_msg          = call.message
            fake_msg.text     = f"https://github.com/{full_name}"
            fake_msg.from_user = call.from_user
            process_github_clone(fake_msg, limits)

        elif data == "pip_list":
            bot.answer_callback_query(call.id)
            libs_text = get_safe_libraries_list()
            edit_message_safe(bot,
                f"📦 <b>Approved Safe Libraries</b>\n{libs_text}",
                call.message.chat.id, call.message.message_id
            )

        elif data.startswith("pip_install_"):
            parts     = data.split("_", 3)
            project_id = parts[2]
            library    = parts[3]
            project    = db.get_project(project_id)
            bot.answer_callback_query(call.id, f"Installing {library}...")
            if project:
                _do_pip_install(call.message, project, library)

        elif data.startswith("project_"):
            project_id = data.split("_")[1]
            show_project_details(call, project_id)
        elif data.startswith("delete_"):
            project_id = data.split("_")[1]
            confirm_delete_project(call, project_id)
        elif data.startswith("confirm_delete_"):
            project_id = data.split("_", 2)[2]
            delete_project(call, project_id)
        elif data.startswith("stop_"):
            project_id = data.split("_")[1]
            stop_project_callback(call, project_id)
        elif data.startswith("start_"):
            project_id = data.split("_")[1]
            start_project_callback(call, project_id)
        elif data.startswith("restart_"):
            project_id = data.split("_")[1]
            restart_project_callback(call, project_id)
        elif data.startswith("logs_"):
            project_id = data.split("_")[1]
            show_project_logs_callback(call, project_id)
        elif data.startswith("confirm_stop_"):
            project_id = data.split("_", 2)[2]
            confirm_stop_project_callback(call, project_id)

        elif data.startswith("update_project_"):
            project_id = data.replace("update_project_", "")
            project    = db.get_project(project_id)
            bot.answer_callback_query(call.id)
            if project:
                _confirm_update_project(call, project, edit_msg_id=call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Pʀᴏᴊᴇᴄᴛ ɴᴏᴛ ғᴏᴜɴᴅ!")
        elif data.startswith("do_update_"):
            project_id = data.replace("do_update_", "")
            _do_update_project(call, project_id)

        elif data.startswith("exec_pick_"):
            parts_exec = data.split("_", 3)
            project_id = parts_exec[2]
            cmd        = parts_exec[3] if len(parts_exec) > 3 else ""
            project    = db.get_project(project_id)
            bot.answer_callback_query(call.id, "Running...")
            if project:
                _do_exec(call.message, project, cmd)

        elif data.startswith("replace_pick_"):
            parts_r    = data.split("_", 3)
            project_id = parts_r[2]
            file_name  = parts_r[3] if len(parts_r) > 3 else ""
            project    = db.get_project(project_id)
            user_id    = call.from_user.id
            bot.answer_callback_query(call.id)
            if project:
                _replace_state[user_id] = {'file_name': file_name, 'project': project}
                prompt = bot.send_message(call.message.chat.id,
                    f"📁 <b>Rᴇᴘʟᴀᴄᴇ <code>{html.escape(file_name)}</code></b>\n\n"
                    f"Pʀᴏᴊᴇᴄᴛ: <b>{project['name']}</b>\n\n"
                    f"Sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ғɪʟᴇ ɴᴏᴡ. 📎",
                    parse_mode="HTML"
                )
                bot.register_next_step_handler(prompt, _process_replace_file, user_id)

        elif data.startswith("env_show_"):
            project_id = data.replace("env_show_", "")
            project    = db.get_project(project_id)
            bot.answer_callback_query(call.id)
            if project:
                _show_env(call.message, project)

        elif data.startswith("env_apply_"):
            parts_e    = data.split("_", 4)
            project_id = parts_e[2]
            env_key    = parts_e[3] if len(parts_e) > 3 else ""
            env_val    = parts_e[4] if len(parts_e) > 4 else ""
            project    = db.get_project(project_id)
            bot.answer_callback_query(call.id, "Applying...")
            if project:
                _apply_env(call, project, env_key, env_val)

        elif data == "admin_stats":
            if not is_admin(call.from_user.id):
                bot.answer_callback_query(call.id, "Dᴏɴ'ᴛ Cʀᴏss Yᴏᴜʀ Lɪᴍɪᴛ")
                return
            show_admin_stats(call)

    except Exception as e:
        try:
            bot.answer_callback_query(call.id, f"Error: {str(e)[:50]}")
        except Exception:
            pass
        logger.log_action(call.from_user.id, "callback_error", {"error": str(e), "data": call.data})


def show_project_details(call, project_id):
    project = db.get_project(project_id)
    if not project or (project['user_id'] != call.from_user.id and not is_admin(call.from_user.id)):
        bot.answer_callback_query(call.id, "Pʀᴏᴊᴇᴄᴛ Nᴏᴛ Fᴏᴜɴᴅ!")
        return

    se     = "🟢" if project['status'] == 'running' else "🔴"
    source = project.get('source', 'zip_upload')
    src_text = f"🐙 {source}" if source and source.startswith('http') else "📦 ZIP Upload"

    text = f"""
{project_em} 𝐏𝐫𝐨𝐣𝐞𝐜𝐭 𝐃𝐞𝐭𝐚𝐢𝐥𝐬

{check} <b>Nᴀᴍᴇ</b> {project['name']}
{check} <b>Sᴛᴀᴛᴜs</b> {se} {project['status'].title()}
{check} <b>Sᴏᴜʀᴄᴇ</b> {src_text}
{check} <b>Cᴏɴᴛᴀɪɴᴇʀ</b> <code>{project['container_id'][:12]}</code>

{usage} 𝐔𝐬𝐚𝐠𝐞
• CPU {project['usage'].get('cpu', 0)}%
• Mᴇᴍᴏʀʏ {project['usage'].get('memory', 0)}MB
• Uᴘᴛɪᴍᴇ {project['usage'].get('uptime', 0)}h

{date} <b>Cʀᴇᴀᴛᴇᴅ</b> {project['created_at'].strftime('%Y-%m-%d %H:%M')}
"""
    markup = types.InlineKeyboardMarkup()
    if project['status'] == 'running':
        markup.row(
            types.InlineKeyboardButton("■ Sᴛᴏᴘ", callback_data=f"stop_{project_id}"),
            types.InlineKeyboardButton("↻ Rᴇsᴛᴀʀᴛ", callback_data=f"restart_{project_id}")
        )
    else:
        markup.row(types.InlineKeyboardButton("▶️ Sᴛᴀʀᴛ", callback_data=f"start_{project_id}"))

    markup.row(
        types.InlineKeyboardButton("≡ Lᴏɢs", callback_data=f"logs_{project_id}"),
        types.InlineKeyboardButton("⊗ Dᴇʟᴇᴛᴇ", callback_data=f"delete_{project_id}")
    )
    markup.row(types.InlineKeyboardButton("« Back", callback_data="my_projects"))
    edit_message_safe(bot, text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)


def confirm_delete_project(call, project_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✖ Yᴇs, Dᴇʟᴇᴛᴇ", callback_data=f"confirm_delete_{project_id}"),
        types.InlineKeyboardButton("∅ Cᴀɴᴄᴇʟ", callback_data="my_projects")
    )
    edit_message_safe(bot, f"{warn} <b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ?</b>\n\nTʜɪs Wɪʟʟ Pᴇʀᴍᴀɴᴇɴᴛʟʏ Dᴇʟᴇᴛᴇ Tʜᴇ Pʀᴏᴊᴇᴄᴛ! {wipe_alert}",
        call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)


def delete_project(call, project_id):
    project = db.get_project(project_id)
    if not project or (project['user_id'] != call.from_user.id and not is_admin(call.from_user.id)):
        bot.answer_callback_query(call.id, "Pʀᴏᴊᴇᴄᴛ Nᴏᴛ Fᴏᴜɴᴅ!")
        return
    docker_manager.remove_project(project['container_id'])
    db.delete_project(project_id)
    edit_message_safe(bot, f"{deleted} Pʀᴏᴊᴇᴄᴛ '{project['name']}' Dᴇʟᴇᴛᴇᴅ! {check}", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Pʀᴏᴊᴇᴄᴛ Dᴇʟᴇᴛᴇᴅ!")
    logger.log_action(call.from_user.id, "project_deleted", {"project": project['name']})


def stop_project_callback(call, project_id):
    project = db.get_project(project_id)
    if not project or (project['user_id'] != call.from_user.id and not is_admin(call.from_user.id)):
        bot.answer_callback_query(call.id, "Dᴏɴ'ᴛ Cʀᴏss Yᴏᴜʀ Lɪᴍɪᴛ"); return
    if project['status'] != 'running':
        bot.answer_callback_query(call.id, "Nᴏᴛ Rᴜɴɴɪɴɢ!"); return
    if docker_manager.stop_container(project['container_id']):
        db.update_project(project_id, {'status': 'stopped'})
        bot.answer_callback_query(call.id, "Sᴛᴏᴘᴘᴇᴅ!")
        edit_message_safe(bot,
            f"{stoped} 𝐏𝐫𝐨𝐣𝐞𝐜𝐭 𝐒𝐭𝐨𝐩𝐩𝐞𝐝\n\n{project_em} {project['name']}\n\nUsᴇ /projects Tᴏ Rᴇsᴛᴀʀᴛ.",
            call.message.chat.id, call.message.message_id
        )
        logger.log_action(call.from_user.id, "project_stopped", {"project": project['name']})
    else:
        bot.answer_callback_query(call.id, "Fᴀɪʟᴇᴅ Tᴏ Sᴛᴏᴘ!")


def start_project_callback(call, project_id):
    project = db.get_project(project_id)
    if not project or (project['user_id'] != call.from_user.id and not is_admin(call.from_user.id)):
        bot.answer_callback_query(call.id, "Dᴏɴ'ᴛ Cʀᴏss Yᴏᴜʀ Lɪᴍɪᴛ"); return
    if project['status'] == 'running':
        bot.answer_callback_query(call.id, "Aʟʀᴇᴀᴅʏ Rᴜɴɴɪɴɢ!"); return
    if docker_manager.start_container(project['container_id']):
        db.update_project(project_id, {'status': 'running'})
        bot.answer_callback_query(call.id, "Sᴛᴀʀᴛᴇᴅ!")
        docker_manager.start_monitoring(project['user_id'], project['name'], project['limits'])
        show_project_details(call, project_id)
        logger.log_action(call.from_user.id, "project_started", {"project": project['name']})
    else:
        bot.answer_callback_query(call.id, "Fᴀɪʟᴇᴅ Tᴏ Sᴛᴀʀᴛ!")


def restart_project_callback(call, project_id):
    project = db.get_project(project_id)
    if not project or (project['user_id'] != call.from_user.id and not is_admin(call.from_user.id)):
        bot.answer_callback_query(call.id, "Dᴏɴ'ᴛ Cʀᴏss Yᴏᴜʀ Lɪᴍɪᴛ!"); return
    if docker_manager.restart_container(project['container_id']):
        bot.answer_callback_query(call.id, "Rᴇsᴛᴀʀᴛᴇᴅ!")
        show_project_details(call, project_id)
        logger.log_action(call.from_user.id, "project_restarted", {"project": project['name']})
    else:
        bot.answer_callback_query(call.id, "Fᴀɪʟᴇᴅ!")


def show_project_logs_callback(call, project_id):
    project = db.get_project(project_id)
    if not project or (project['user_id'] != call.from_user.id and not is_admin(call.from_user.id)):
        bot.answer_callback_query(call.id, "Dᴏɴ'ᴛ Cʀᴏss Yᴏᴜʀ Lɪᴍɪᴛ!"); return
    bot.answer_callback_query(call.id, "Lᴏᴀᴅɪɴɢ Lᴏɢs...")
    try:
        build_logs   = project.get('build_logs', '')
        runtime_logs = docker_manager.get_container_logs(project['container_id'], lines=50) or ''
        log_text     = f"{logs} <b>Lᴏɢs {html.escape(project['name'])}</b>\n\n"
        truncated = False
        if build_logs:
            build_raw = chr(10).join(build_logs.split(chr(10))[-10:])
            if len(build_raw) > 800:
                build_raw = build_raw[:800]
                truncated = True
            log_text += f"<b>{build} Bᴜɪʟᴅ Lᴏɢs</b>\n<pre>{html.escape(build_raw)}</pre>\n\n"
        runtime_raw = runtime_logs
        if len(runtime_raw) > 2500:
            runtime_raw = runtime_raw[:2500]
            truncated = True
        log_text += f"<b>{logs} Rᴜɴᴛɪᴍᴇ Lᴏɢs</b>\n<pre>{html.escape(runtime_raw)}</pre>"
        if truncated: log_text += "\n\n... (Tʀᴜɴᴄᴀᴛᴇᴅ)"
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("↻ Rᴇғʀᴇsʜ", callback_data=f"logs_{project_id}"),
            types.InlineKeyboardButton("⎙ Dᴇᴛᴀɪʟs", callback_data=f"project_{project_id}")
        )
        markup.row(types.InlineKeyboardButton("« Back", callback_data="my_projects"))
        edit_message_safe(bot, log_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        edit_message_safe(bot, f"{err} Eʀʀᴏʀ: {html.escape(str(e))}\n\nTry /logs Command", call.message.chat.id, call.message.message_id)


def confirm_stop_project_callback(call, project_id):
    project = db.get_project(project_id)
    if not project:
        bot.answer_callback_query(call.id, "❌ Nᴏᴛ Fᴏᴜɴᴅ!"); return
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✖ Yes, Stop", callback_data=f"stop_{project_id}"),
        types.InlineKeyboardButton("∅ Cancel", callback_data="my_projects")
    )
    edit_message_safe(bot,
        f"{alert} 𝐒𝐭𝐨𝐩 {project['name']}?\n\nYᴏᴜ Cᴀɴ Rᴇsᴛᴀʀᴛ Iᴛ Lᴀᴛᴇʀ.",
        call.message.chat.id, call.message.message_id, reply_markup=markup
    )
    bot.answer_callback_query(call.id)


def show_admin_stats(call):
    stats = db.get_stats()
    text  = f"""
📊 <b>Detailed Statistics</b>

<b>👥 Users:</b>
• Total: {stats['total_users']}
• Premium: {stats['premium_users']}
• Banned: {stats['banned_users']}
• Restricted: {stats.get('restricted_users', 0)}
• GitHub Connected: {stats['github_connected']}

<b>📦 Projects:</b>
• Total: {stats['total_projects']}
• Running: {stats['running_projects']}
• Stopped: {stats['total_projects'] - stats['running_projects']}

<b>💻 System:</b>
• CPU: {psutil.cpu_percent()}%
• RAM: {psutil.virtual_memory().percent}%
• Disk: {psutil.disk_usage('/').percent}%
• Uptime: {int(time.time() - psutil.boot_time()) // 3600}h
"""
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("« Back", callback_data="admin_panel"))
    edit_message_safe(bot, text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)


# ════════════════════════════════════════════════════════════════════
#  PREMIUM EXPIRY ALERT — background thread
# ════════════════════════════════════════════════════════════════════
def premium_expiry_checker():
    while True:
        try:
            expiring = db.get_expiring_premium_users(hours=24)
            for user in expiring:
                user_id = user['user_id']
                expiry  = user.get('premium_expiry')
                if expiry:
                    hours_left = int((expiry - datetime.now()).total_seconds() // 3600)
                    try:
                        bot.send_message(
                            user_id,
                            f"{warn} <b>Pʀᴇᴍɪᴜᴍ Exᴘɪʀɪɴɢ Sᴏᴏɴ!</b>\n\n"
                            f"{check} Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ ᴇxᴘɪʀᴇs ɪɴ <b>{hours_left}h</b>\n"
                            f"{check} Exᴘɪʀʏ Dᴀᴛᴇ: <code>{expiry.strftime('%Y-%m-%d %H:%M')}</code>\n\n"
                            f"Rᴇɴᴇᴡ ɴᴏᴡ ᴛᴏ ᴋᴇᴇᴘ ʏᴏᴜʀ ʙᴇɴᴇғɪᴛs!\n"
                            f"Cᴏɴᴛᴀᴄᴛ @MR_ARMAN_08 {verified}",
                            parse_mode="HTML"
                        )
                        db.mark_expiry_alert_sent(user_id)
                        logger.log_action(user_id, "premium_expiry_alert_sent", {"hours_left": hours_left})
                    except:
                        pass

            now = datetime.now()
            expired = list(db.users.find({
                'premium': True,
                'premium_expiry': {'$lt': now, '$ne': None}
            }))
            for user in expired:
                user_id = user['user_id']
                db.set_premium(user_id, False)
                try:
                    bot.send_message(
                        user_id,
                        f"{i} <b>Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Hᴀs Exᴘɪʀᴇᴅ.</b>\n\n"
                        f"Yᴏᴜ'ᴠᴇ ʙᴇᴇɴ ᴍᴏᴠᴇᴅ ᴛᴏ ᴛʜᴇ Fʀᴇᴇ ᴛɪᴇʀ.\n"
                        f"Rᴇɴᴇᴡ ᴠɪᴀ @MR_ARMAN_08 {verified}",
                        parse_mode="HTML"
                    )
                except:
                    pass

        except Exception as e:
            print(f"[Expiry Checker] Error: {e}")

        time.sleep(3600)

@bot.callback_query_handler(func=lambda call: call.data == "noop")
def noop(call):
    bot.answer_callback_query(call.id)
    

# ════════════════════════════════════════════════════════════════════
#  /update — Pull latest commits for repo-based projects
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['update'])
@check_maintenance
@check_banned
@check_restricted
@check_rate_limit
def update_command(message):
    user_id  = message.from_user.id
    projects = db.get_user_projects(user_id)

    repo_projects = [p for p in projects if p.get('source', '').startswith('https://github.com/')]

    if not repo_projects:
        bot.reply_to(message,
            f"{empty} <b>Nᴏ Rᴇᴘᴏ-Bᴀsᴇᴅ Pʀᴏᴊᴇᴄᴛs Fᴏᴜɴᴅ.</b>\n\n"
            f"Oɴʟʏ ᴘʀᴏᴊᴇᴄᴛs ᴅᴇᴘʟᴏʏᴇᴅ ᴠɪᴀ /github ᴏʀ /repos ᴄᴀɴ ʙᴇ ᴜᴘᴅᴀᴛᴇᴅ.\n"
            f"ZIP-ᴜᴘʟᴏᴀᴅᴇᴅ ᴘʀᴏᴊᴇᴄᴛs ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀ ʀᴇᴘᴏ ʟɪɴᴋᴇᴅ."
        )
        return

    if len(repo_projects) == 1:
        _confirm_update_project(message, repo_projects[0])
        return

    markup = types.InlineKeyboardMarkup()
    text   = f"{update_em if 'update_em' in dir() else '🔄'} <b>Sᴇʟᴇᴄᴛ Pʀᴏᴊᴇᴄᴛ Tᴏ Uᴘᴅᴀᴛᴇ</b>\n\n"
    for p in repo_projects:
        se = "🟢" if p['status'] == 'running' else "🔴"
        text += f"{se} <b>{p['name']}</b>\n<code>{p.get('source','')}</code>\n\n"
        markup.row(types.InlineKeyboardButton(
            f"{se} {p['name']}",
            callback_data=f"update_project_{p['_id']}"
        ))
    markup.row(types.InlineKeyboardButton("∅ Cancel", callback_data="cancel"))
    bot.reply_to(message, text, reply_markup=markup)
    logger.log_action(user_id, "update_command", {})


def _confirm_update_project(message_or_call, project, edit_msg_id=None):
    is_call = hasattr(message_or_call, 'from_user') and hasattr(message_or_call, 'data')
    chat_id = message_or_call.message.chat.id if is_call else message_or_call.chat.id

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✔ Update Now", callback_data=f"do_update_{project['_id']}"),
        types.InlineKeyboardButton("∅ Cancel",     callback_data="cancel")
    )
    text = (
        f"🔄 <b>Uᴘᴅᴀᴛᴇ Pʀᴏᴊᴇᴄᴛ</b>\n\n"
        f"{check} <b>Nᴀᴍᴇ</b> {project['name']}\n"
        f"{check} <b>Sᴏᴜʀᴄᴇ</b> <code>{project.get('source','')}</code>\n\n"
        f"Tʜɪs ᴡɪʟʟ ᴘᴜʟʟ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴄᴏᴍᴍɪᴛ ᴀɴᴅ ʀᴇʙᴜɪʟᴅ ᴛʜᴇ ᴄᴏɴᴛᴀɪɴᴇʀ."
    )
    if edit_msg_id:
        edit_message_safe(bot, text, chat_id, edit_msg_id, reply_markup=markup)
    else:
        bot.reply_to(message_or_call, text, reply_markup=markup)


def _do_update_project(call, project_id):
    """Pull latest commits, rebuild, and restart the container."""
    user_id = call.from_user.id
    project = db.get_project(project_id)
    if not project or (project['user_id'] != user_id and not is_admin(user_id)):
        bot.answer_callback_query(call.id, "Pʀᴏᴊᴇᴄᴛ Nᴏᴛ Fᴏᴜɴᴅ!")
        return

    repo_url = project.get('source', '')
    if not repo_url.startswith('https://github.com/'):
        bot.answer_callback_query(call.id, "Nᴏᴛ ᴀ Rᴇᴘᴏ Pʀᴏᴊᴇᴄᴛ!")
        return

    bot.answer_callback_query(call.id, "🔄 Sᴛᴀʀᴛɪɴɢ Uᴘᴅᴀᴛᴇ...")
    edit_message_safe(bot,
        f"🔄 <b>Uᴘᴅᴀᴛɪɴɢ <code>{project['name']}</code>...</b>\n\n{load} Fᴇᴛᴄʜɪɴɢ ʟᴀᴛᴇsᴛ ᴄᴏᴍᴍɪᴛs...",
        call.message.chat.id, call.message.message_id
    )

    def _run_update():
        try:
            import tempfile, shutil, subprocess

            limits = project.get('limits', get_user_limits(user_id))
            temp_dir  = tempfile.mkdtemp()
            clone_dir = os.path.join(temp_dir, 'repo')

            access_token = db.get_github_token(user_id)
            cloned = False
            if access_token:
                parts = repo_url.replace("https://github.com/", "").rstrip("/")
                ok, _ = github_auth.clone_private_repo(access_token, parts, clone_dir)
                if ok:
                    cloned = True

            if not cloned:
                result = subprocess.run(
                    ['git', 'clone', '--depth', '1', repo_url, clone_dir],
                    capture_output=True, text=True, timeout=300
                )
                if result.returncode != 0:
                    err_txt = result.stderr[:600]
                    if 'Authentication' in err_txt or 'access' in err_txt.lower() or 'Repository not found' in err_txt:
                        edit_message_safe(bot,
                            f"🔒 <b>Uᴘᴅᴀᴛᴇ Fᴀɪʟᴇᴅ — Pʀɪᴠᴀᴛᴇ Rᴇᴘᴏ</b>\n\n"
                            f"Tʜɪs ʀᴇᴘᴏ ɪs ᴘʀɪᴠᴀᴛᴇ ᴀɴᴅ ʏᴏᴜʀ GɪᴛHᴜʙ ᴛᴏᴋᴇɴ ɪs ᴍɪssɪɴɢ ᴏʀ ᴇxᴘɪʀᴇᴅ.\n\n"
                            f"{check} Usᴇ /connect ᴛᴏ ʀᴇ-ʟɪɴᴋ GɪᴛHᴜʙ.",
                            call.message.chat.id, call.message.message_id
                        )
                    else:
                        edit_message_safe(bot,
                            f"{err} <b>Cʟᴏɴᴇ Fᴀɪʟᴇᴅ</b>\n\n<code>{html.escape(err_txt)}</code>",
                            call.message.chat.id, call.message.message_id
                        )
                    shutil.rmtree(temp_dir)
                    return
                cloned = True

            result_log = subprocess.run(
                ['git', '-C', clone_dir, 'log', '--oneline', '-1'],
                capture_output=True, text=True
            )
            latest_commit = result_log.stdout.strip()
            last_commit   = project.get('last_commit', '')
            if latest_commit and latest_commit == last_commit:
                shutil.rmtree(temp_dir)
                edit_message_safe(bot,
                    f"✅ <b>Nᴏ Uᴘᴅᴀᴛᴇs Fᴏᴜɴᴅ</b>\n\n"
                    f"<code>{project['name']}</code> ɪs ᴀʟʀᴇᴀᴅʏ ᴜᴘ-ᴛᴏ-ᴅᴀᴛᴇ.\n"
                    f"{check} Lᴀᴛᴇsᴛ ᴄᴏᴍᴍɪᴛ: <code>{html.escape(latest_commit)}</code>",
                    call.message.chat.id, call.message.message_id
                )
                return

            edit_message_safe(bot,
                f"🔄 <b>Uᴘᴅᴀᴛɪɴɢ...</b>\n\n{load} Rᴇʙᴜɪʟᴅɪɴɢ ᴄᴏɴᴛᴀɪɴᴇʀ...\n"
                f"{check} Nᴇᴡ ᴄᴏᴍᴍɪᴛ: <code>{html.escape(latest_commit)}</code>",
                call.message.chat.id, call.message.message_id
            )

            try:
                docker_manager.stop_container(project['container_id'])
                docker_manager.remove_project(project['container_id'])
            except Exception:
                pass

            result_deploy = docker_manager.deploy_project(user_id, project['name'], clone_dir, limits)
            shutil.rmtree(temp_dir)

            if result_deploy['success']:
                db.update_project(project_id, {
                    'container_id': result_deploy['container_id'],
                    'status': 'running',
                    'build_logs': result_deploy.get('build_logs', ''),
                    'last_commit': latest_commit,
                    'updated_at': datetime.now()
                })
                docker_manager.start_monitoring(user_id, project['name'], limits)
                edit_message_safe(bot,
                    f"✅ <b>Uᴘᴅᴀᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                    f"{check} Pʀᴏᴊᴇᴄᴛ: <code>{project['name']}</code>\n"
                    f"{check} Cᴏᴍᴍɪᴛ: <code>{html.escape(latest_commit)}</code>\n"
                    f"{check} Cᴏɴᴛᴀɪɴᴇʀ: <code>{result_deploy['container_id'][:12]}</code>\n\n"
                    f"Pʀᴏᴊᴇᴄᴛ ɪs ɴᴏᴡ ʀᴜɴɴɪɴɢ ᴏɴ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴄᴏᴅᴇ! 🚀",
                    call.message.chat.id, call.message.message_id
                )
                logger.log_action(user_id, "project_updated", {"project": project['name'], "commit": latest_commit})
            else:
                edit_message_safe(bot,
                    f"{err} <b>Rᴇʙᴜɪʟᴅ Fᴀɪʟᴇᴅ</b>\n\n<code>{html.escape(result_deploy['error'][:800])}</code>",
                    call.message.chat.id, call.message.message_id
                )
        except subprocess.TimeoutExpired:
            edit_message_safe(bot,
                f"{timeout if 'timeout' in dir() else '⏱'} <b>Uᴘᴅᴀᴛᴇ Tɪᴍᴇᴅ Oᴜᴛ.</b> Rᴇᴘᴏ ᴍᴀʏ ʙᴇ ᴛᴏᴏ ʟᴀʀɢᴇ.",
                call.message.chat.id, call.message.message_id
            )
        except Exception as ex:
            edit_message_safe(bot,
                f"{err} <b>Uᴘᴅᴀᴛᴇ Eʀʀᴏʀ</b>\n\n<code>{html.escape(str(ex))}</code>",
                call.message.chat.id, call.message.message_id
            )

    threading.Thread(target=_run_update, daemon=True).start()


# ════════════════════════════════════════════════════════════════════
#  /exec — Execute command inside container (extremely secured)
# ════════════════════════════════════════════════════════════════════

EXEC_BLACKLIST = [
    'curl', 'wget', 'nc', 'netcat', 'ncat', 'socat', 'ssh', 'scp', 'ftp', 'rsync',
    'python -c', 'python3 -c', 'perl -e', 'ruby -e',
    'rm -rf /', 'mkfs', 'dd if=', 'shred',
    'sudo', 'su ', 'chmod 777', 'chown root', 'passwd',
    'fork bomb', ':(){ :|:& };:', 'nohup', 'screen', 'tmux',
    'minerd', 'xmrig', 'cpuminer', 'cryptonight',
    'bash -i', 'sh -i', '/dev/tcp', '/dev/udp', 'exec 3<>/dev/tcp',
    'apt install', 'apt-get install', 'yum install', 'dnf install', 'apk add',
    'docker', 'dockerd', '--privileged', '--cap-add',
    '/proc/sysrq', '/sys/kernel',
]

EXEC_ALLOWED_SHELLS = ['sh', 'bash']

def _is_safe_exec_command(cmd: str) -> tuple[bool, str]:
    cmd_lower = cmd.lower().strip()
    for bad in EXEC_BLACKLIST:
        if bad in cmd_lower:
            return False, f"Command contains blocked pattern: `{bad}`"
    dangerous_ops = ['&&', '||', '`', '$(',  '|&', '>(', '<(']
    for op in dangerous_ops:
        if op in cmd:
            return False, f"Shell operator `{op}` is not allowed."

    import re
    if re.search(r'>\s*/(?:etc|proc|sys|dev)', cmd_lower):
        return False, "Redirection to system paths is blocked."
    return True, ""


@bot.message_handler(commands=['exec'])
@check_maintenance
@check_banned
@check_restricted
@check_rate_limit
def exec_command(message):
    user_id = message.from_user.id
    parts   = message.text.strip().split(maxsplit=1)

    if len(parts) < 2:
        bot.reply_to(message,
            f"💻 <b>Eᴜxᴇᴄᴜᴛᴇ Cᴏᴍᴍᴀɴᴅ</b>\n\n"
            f"<b>Usᴀɢᴇ:</b> <code>/exec [command]</code>\n"
            f"<b>Exᴀᴍᴘʟᴇ:</b> <code>/exec python3 --version</code>\n\n"
            f"{warn} Cᴏᴍᴍᴀɴᴅs ᴀʀᴇ ᴇxᴇᴄᴜᴛᴇᴅ ɪɴsɪᴅᴇ ʏᴏᴜʀ ᴄᴏɴᴛᴀɪɴᴇʀ ᴏɴʟʏ.\n"
            f"Dᴀɴɢᴇʀᴏᴜs ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ʙʟᴏᴄᴋᴇᴅ."
        )
        return

    cmd = parts[1]
    safe, reason = _is_safe_exec_command(cmd)
    if not safe:
        bot.reply_to(message,
            f"🚫 <b>Cᴏᴍᴍᴀɴᴅ Bʟᴏᴄᴋᴇᴅ</b>\n\n{reason}\n\n"
            f"Fᴏʀ ʏᴏᴜʀ sᴀғᴇᴛʏ ᴀɴᴅ ᴛʜᴇ VPS sᴇᴄᴜʀɪᴛʏ, ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ."
        )
        logger.log_action(user_id, "exec_blocked", {"cmd": cmd, "reason": reason})
        return

    projects = db.get_user_projects(user_id)
    running  = [p for p in projects if p['status'] == 'running']

    if not running:
        bot.reply_to(message, f"{empty} Nᴏ Rᴜɴɴɪɴɢ Pʀᴏᴊᴇᴄᴛs. Sᴛᴀʀᴛ ᴏɴᴇ ғɪʀsᴛ.")
        return

    if len(running) == 1:
        _do_exec(message, running[0], cmd)
    else:
        markup = types.InlineKeyboardMarkup()
        for p in running:
            markup.row(types.InlineKeyboardButton(
                f"🟢 {p['name']}",
                callback_data=f"exec_pick_{p['_id']}_{cmd[:50]}"
            ))
        bot.reply_to(message, f"💻 <b>Sᴇʟᴇᴄᴛ Pʀᴏᴊᴇᴄᴛ</b> ᴛᴏ ʀᴜɴ:\n<code>{html.escape(cmd)}</code>", reply_markup=markup)


def _do_exec(message, project, cmd):
    user_id    = message.from_user.id
    status_msg = bot.reply_to(message, f"💻 Exᴇᴄᴜᴛɪɴɢ... {load}")
    try:
        container  = docker_client.containers.get(project['container_id'])
        exec_result = container.exec_run(
            cmd=['sh', '-c', cmd],
            user='nobody',
            workdir='/app',
            demux=True,
            environment={'HOME': '/tmp'},
        )
        stdout = exec_result.output[0] or b''
        stderr = exec_result.output[1] or b''
        output = (stdout + stderr).decode('utf-8', errors='replace')
        exit_code = exec_result.exit_code

        if len(output) > 3500:
            output = output[-3500:] + "\n... (ᴛʀᴜɴᴄᴀᴛᴇᴅ)"

        icon = "✅" if exit_code == 0 else "⚠️"
        result_text = (
            f"💻 <b>Exec Result</b> {icon}\n\n"
            f"{check} <b>Pʀᴏᴊᴇᴄᴛ</b> <code>{project['name']}</code>\n"
            f"{check} <b>Cᴏᴍᴍᴀɴᴅ</b> <code>{html.escape(cmd)}</code>\n"
            f"{check} <b>Exɪᴛ Cᴏᴅᴇ</b> <code>{exit_code}</code>\n\n"
            f"<pre>{html.escape(output) if output.strip() else '(no output)'}</pre>"
        )
        bot.edit_message_text(result_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
        logger.log_action(user_id, "exec_command", {"project": project['name'], "cmd": cmd, "exit_code": exit_code})
    except docker_sdk.errors.NotFound:
        bot.edit_message_text(f"{err} Cᴏɴᴛᴀɪɴᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ. ɪs ᴛʜᴇ ᴘʀᴏᴊᴇᴄᴛ ʀᴜɴɴɪɴɢ?", message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"{err} Exᴇᴄ Eʀʀᴏʀ: {html.escape(str(e))}", message.chat.id, status_msg.message_id)


# ════════════════════════════════════════════════════════════════════
#  /replace — Replace a file inside a running container
# ════════════════════════════════════════════════════════════════════

_replace_state: dict = {}

@bot.message_handler(commands=['replace'])
@check_maintenance
@check_banned
@check_restricted
@check_rate_limit
def replace_command(message):
    user_id = message.from_user.id
    parts   = message.text.strip().split(maxsplit=1)

    if len(parts) < 2:
        bot.reply_to(message,
            f"📁 <b>Rᴇᴘʟᴀᴄᴇ Fɪʟᴇ Iɴ Cᴏɴᴛᴀɪɴᴇʀ</b>\n\n"
            f"<b>Usᴀɢᴇ:</b> <code>/replace filename.py</code>\n"
            f"Tʜᴇɴ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ᴛʜᴇ ɴᴇᴡ ғɪʟᴇ.\n\n"
            f"{check} Tʜᴇ ғɪʟᴇ ɪs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴇɴᴀᴍᴇᴅ ᴛᴏ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ ɴᴀᴍᴇ.\n"
            f"{check} Tʜᴇ ᴄᴏɴᴛᴀɪɴᴇʀ ɪs ʀᴇsᴛᴀʀᴛᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀғᴛᴇʀ ʀᴇᴘʟᴀᴄᴇ."
        )
        return

    file_name = parts[1].strip()
    if '/' in file_name or '..' in file_name or file_name.startswith('.'):
        bot.reply_to(message, f"🚫 Iɴᴠᴀʟɪᴅ ғɪʟᴇ ɴᴀᴍᴇ. Sɪᴍᴘʟᴇ ᴛᴏᴘ-ʟᴇᴠᴇʟ ɴᴀᴍᴇs ᴏɴʟʏ.")
        return

    projects = db.get_user_projects(user_id)
    running  = [p for p in projects if p['status'] == 'running']

    if not running:
        bot.reply_to(message, f"{empty} Nᴏ Rᴜɴɴɪɴɢ Pʀᴏᴊᴇᴄᴛs.")
        return

    if len(running) == 1:
        _replace_state[user_id] = {'file_name': file_name, 'project': running[0]}
        prompt = bot.reply_to(message,
            f"📁 <b>Rᴇᴘʟᴀᴄᴇ <code>{html.escape(file_name)}</code></b>\n\n"
            f"Pʀᴏᴊᴇᴄᴛ: <b>{running[0]['name']}</b>\n\n"
            f"Nᴏᴡ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ғɪʟᴇ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴛʜɪs ᴍᴇssᴀɢᴇ. 📎"
        )
        bot.register_next_step_handler(prompt, _process_replace_file, user_id)
    else:
        markup = types.InlineKeyboardMarkup()
        for p in running:
            markup.row(types.InlineKeyboardButton(
                f"🟢 {p['name']}",
                callback_data=f"replace_pick_{p['_id']}_{file_name}"
            ))
        bot.reply_to(message, f"📁 <b>Sᴇʟᴇᴄᴛ Pʀᴏᴊᴇᴄᴛ</b> ᴛᴏ ʀᴇᴘʟᴀᴄᴇ <code>{html.escape(file_name)}</code>", reply_markup=markup)


def _process_replace_file(message, user_id):
    state = _replace_state.pop(user_id, None)
    if not state:
        bot.reply_to(message, f"{err} Session expired. Please use /replace again.")
        return

    if not message.document:
        bot.reply_to(message, f"{err} Nᴏ ғɪʟᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ. Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ғɪʟᴇ.")
        return

    file_name = state['file_name']
    project   = state['project']

    status_msg = bot.reply_to(message, f"📁 Rᴇᴘʟᴀᴄɪɴɢ <code>{html.escape(file_name)}</code>... {load}")
    try:

        file_info = bot.get_file(message.document.file_id)
        file_data = bot.download_file(file_info.file_path)

        import tempfile as _tmpfile
        tmp = _tmpfile.NamedTemporaryFile(delete=False, suffix='_' + file_name)
        tmp.write(file_data)
        tmp.close()

        container = docker_client.containers.get(project['container_id'])

        import tarfile, io
        tar_buf = io.BytesIO()
        with tarfile.open(fileobj=tar_buf, mode='w') as tar:
            tarinfo        = tarfile.TarInfo(name=file_name)
            tarinfo.size   = len(file_data)
            tarinfo.mode   = 0o644
            tar.addfile(tarinfo, io.BytesIO(file_data))
        tar_buf.seek(0)

        container.put_archive('/app', tar_buf)
        os.unlink(tmp.name)

        container.restart(timeout=10)
        db.update_project(str(project['_id']), {'status': 'running'})

        bot.edit_message_text(
            f"✅ <b>Fɪʟᴇ Rᴇᴘʟᴀᴄᴇᴅ!</b>\n\n"
            f"{check} Fɪʟᴇ: <code>{html.escape(file_name)}</code>\n"
            f"{check} Pʀᴏᴊᴇᴄᴛ: <code>{project['name']}</code>\n\n"
            f"Cᴏɴᴛᴀɪɴᴇʀ ʜᴀs ʙᴇᴇɴ ʀᴇsᴛᴀʀᴛᴇᴅ ᴡɪᴛʜ ᴛʜᴇ ɴᴇᴡ ғɪʟᴇ. 🚀",
            message.chat.id, status_msg.message_id, parse_mode="HTML"
        )
        logger.log_action(user_id, "file_replaced", {"project": project['name'], "file": file_name})
    except docker_sdk.errors.NotFound:
        bot.edit_message_text(f"{err} Cᴏɴᴛᴀɪɴᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.", message.chat.id, status_msg.message_id)
    except Exception as ex:
        bot.edit_message_text(f"{err} <b>Rᴇᴘʟᴀᴄᴇ Eʀʀᴏʀ</b>\n\n<code>{html.escape(str(ex))}</code>",
            message.chat.id, status_msg.message_id, parse_mode="HTML")


# ════════════════════════════════════════════════════════════════════
#  /env — Set/view/delete environment variables in container
# ════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['env'])
@check_maintenance
@check_banned
@check_restricted
@check_rate_limit
def env_command(message):
    user_id = message.from_user.id
    parts   = message.text.strip().split(maxsplit=1)

    projects = db.get_user_projects(user_id)
    running  = [p for p in projects if p['status'] == 'running']

    if not running:
        bot.reply_to(message, f"{empty} Nᴏ Rᴜɴɴɪɴɢ Pʀᴏᴊᴇᴄᴛs.")
        return

    if len(parts) < 2:
        if len(running) == 1:
            _show_env(message, running[0])
        else:
            markup = types.InlineKeyboardMarkup()
            for p in running:
                markup.row(types.InlineKeyboardButton(f"🟢 {p['name']}", callback_data=f"env_show_{p['_id']}"))
            bot.reply_to(message,
                f"⚙️ <b>Eɴᴠ Vᴀʀɪᴀʙʟᴇs</b>\n\n"
                f"<b>Usᴀɢᴇ:</b> <code>/env KEY=value</code>\n"
                f"<b>Dᴇʟᴇᴛᴇ:</b> <code>/env KEY=</code>\n\n"
                f"Sᴇʟᴇᴄᴛ ᴀ ᴘʀᴏᴊᴇᴄᴛ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ᴇɴᴠ ᴠᴀʀs:",
                reply_markup=markup
            )
        return

    env_str = parts[1].strip()
    if '=' not in env_str:
        bot.reply_to(message,
            f"⚙️ <b>Eɴᴠ Vᴀʀɪᴀʙʟᴇs</b>\n\n"
            f"<b>Usᴀɢᴇ:</b> <code>/env KEY=value</code>\n"
            f"<b>Dᴇʟᴇᴛᴇ:</b> <code>/env KEY=</code>\n"
            f"<b>Vɪᴇᴡ:</b> <code>/env</code>"
        )
        return

    eq_idx   = env_str.index('=')
    env_key  = env_str[:eq_idx].strip().upper()
    env_val  = env_str[eq_idx+1:].strip()

    import re
    if not re.match(r'^[A-Z_][A-Z0-9_]*$', env_key):
        bot.reply_to(message, f"🚫 Iɴᴠᴀʟɪᴅ ᴋᴇʏ ɴᴀᴍᴇ. Usᴇ ᴜᴘᴘᴇʀᴄᴀsᴇ ʟᴇᴛᴛᴇʀs, ᴅɪɢɪᴛs, ᴜɴᴅᴇʀsᴄᴏʀᴇ.")
        return

    BLOCKED_ENV_KEYS = {'PATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH', 'HOME', 'USER', 'SHELL'}
    if env_key in BLOCKED_ENV_KEYS:
        bot.reply_to(message, f"🚫 <code>{env_key}</code> ɪs ᴀ ᴘʀᴏᴛᴇᴄᴛᴇᴅ ᴇɴᴠ ᴋᴇʏ ᴀɴᴅ ᴄᴀɴɴᴏᴛ ʙᴇ ᴍᴏᴅɪғɪᴇᴅ.")
        return

    if len(running) == 1:
        _apply_env(message, running[0], env_key, env_val)
    else:
        action = "delete" if env_val == "" else "set"
        markup = types.InlineKeyboardMarkup()
        for p in running:
            markup.row(types.InlineKeyboardButton(
                f"🟢 {p['name']}",
                callback_data=f"env_apply_{p['_id']}_{env_key}_{env_val[:30]}"
            ))
        bot.reply_to(message,
            f"⚙️ <b>Sᴇʟᴇᴄᴛ Pʀᴏᴊᴇᴄᴛ</b>\n\n"
            f"Action: <b>{'Delete' if action=='delete' else 'Set'}</b> <code>{env_key}</code>{'=' + env_val if action=='set' else ''}",
            reply_markup=markup
        )


def _show_env(message, project):
    env_vars = project.get('env_vars', {})
    if not env_vars:
        bot.reply_to(message,
            f"⚙️ <b>Eɴᴠ Vᴀʀs: {project['name']}</b>\n\n"
            f"Nᴏ ᴄᴜsᴛᴏᴍ ᴇɴᴠ ᴠᴀʀɪᴀʙʟᴇs sᴇᴛ.\n\n"
            f"Usᴇ <code>/env KEY=value</code> ᴛᴏ ᴀᴅᴅ ᴏɴᴇ."
        )
        return
    lines = "\n".join(f"• <code>{k}</code> = <code>{v}</code>" for k, v in env_vars.items())
    bot.reply_to(message,
        f"⚙️ <b>Eɴᴠ Vᴀʀs: {project['name']}</b>\n\n{lines}\n\n"
        f"{i} Usᴇ <code>/env KEY=</code> ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀ ᴠᴀʀɪᴀʙʟᴇ."
    )


def _apply_env(message_or_call, project, env_key, env_val):
    is_call = hasattr(message_or_call, 'data')
    chat_id = message_or_call.message.chat.id if is_call else message_or_call.chat.id
    user_id = (message_or_call.from_user.id if is_call else message_or_call.from_user.id)

    def _send(text):
        if is_call:
            bot.send_message(chat_id, text, parse_mode="HTML")
        else:
            bot.reply_to(message_or_call, text)

    try:
        container = docker_client.containers.get(project['container_id'])
        env_vars  = project.get('env_vars', {})

        if env_val == "":
            env_vars.pop(env_key, None)
            action_text = f"🗑 <b>Dᴇʟᴇᴛᴇᴅ</b> <code>{env_key}</code>"
        else:
            env_vars[env_key] = env_val
            action_text = f"✅ <b>Sᴇᴛ</b> <code>{env_key}</code> = <code>{html.escape(env_val)}</code>"

        db.update_project(str(project['_id']), {'env_vars': env_vars})

        import io, tarfile
        env_content = "\n".join(f"{k}={v}" for k, v in env_vars.items()) + "\n"
        tar_buf = io.BytesIO()
        with tarfile.open(fileobj=tar_buf, mode='w') as tar:
            data      = env_content.encode()
            tarinfo   = tarfile.TarInfo(name='.env')
            tarinfo.size = len(data)
            tar.addfile(tarinfo, io.BytesIO(data))
        tar_buf.seek(0)
        container.put_archive('/app', tar_buf)
        container.restart(timeout=10)

        _send(
            f"⚙️ <b>Eɴᴠ Uᴘᴅᴀᴛᴇᴅ</b>\n\n"
            f"{action_text}\n"
            f"{check} Pʀᴏᴊᴇᴄᴛ: <code>{project['name']}</code>\n\n"
            f"Cᴏɴᴛᴀɪɴᴇʀ ʀᴇsᴛᴀʀᴛᴇᴅ ᴡɪᴛʜ ᴜᴘᴅᴀᴛᴇᴅ ᴇɴᴠ ✅"
        )
        logger.log_action(user_id, "env_updated", {"project": project['name'], "key": env_key, "deleted": env_val == ""})
    except docker_sdk.errors.NotFound:
        _send(f"{err} Cᴏɴᴛᴀɪɴᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
    except Exception as ex:
        _send(f"{err} Eɴᴠ Eʀʀᴏʀ: {html.escape(str(ex))}")


# ════════════════════════════════════════════════════════════════════
#  /vps  —  Mini VPS Feature
# ════════════════════════════════════════════════════════════════════

def _vps_tier_for_user(user_id):
    if is_owner(user_id):    return "owner"
    if db.is_premium(user_id): return "premium"
    return "free"


def _format_time_left(expires_at):
    if not expires_at:
        return "Unknown"
    now = datetime.now()
    diff = expires_at - now
    if diff.total_seconds() <= 0:
        return "Expired"
    total_secs = int(diff.total_seconds())
    days  = total_secs // 86400
    hours = (total_secs % 86400) // 3600
    mins  = (total_secs % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"


def _vps_main_menu(user_id):
    vps  = db.get_vps(user_id)
    tier = _vps_tier_for_user(user_id)

    from vps_manager import VPS_TIERS
    tier_cfg = VPS_TIERS.get(tier, VPS_TIERS["free"])

    markup = types.InlineKeyboardMarkup()

    if vps and vps.get("status") == "running":
        expires_at = vps.get("expires_at")
        time_left  = _format_time_left(expires_at)
        stats = vps_manager.get_vps_stats(user_id)
        cpu   = stats.get("cpu_pct", 0) if stats else 0
        mem   = f"{stats.get('mem_used',0)}MB/{stats.get('mem_limit',0)}MB" if stats else "N/A"

        text = (
            f"🖥️ <b>Aapka Mini VPS</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 <b>Status:</b> Running\n"
            f"⏱️ <b>Time Left:</b> <code>{time_left}</code>\n"
            f"🏷️ <b>Tier:</b> {tier_cfg['label']}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>🔐 SSH Credentials:</b>\n"
            f"<code>ssh {vps['username']}@{vps['host']} -p {vps['port']}</code>\n\n"
            f"👤 <b>User:</b> <code>{vps['username']}</code>\n"
            f"🔑 <b>Password:</b> <code>{vps['password']}</code>\n"
            f"🌐 <b>Host:</b> <code>{vps['host']}</code>\n"
            f"🔌 <b>Port:</b> <code>{vps['port']}</code>\n\n"
            f"📊 <b>Resources:</b>\n"
            f"  CPU: <code>{cpu}%</code>  |  RAM: <code>{mem}</code>\n\n"
            f"⚠️ <i>Sudo disabled for security. Root access nahi milega.</i>"
        )
        markup.row(
            types.InlineKeyboardButton("⏹ Stop", callback_data="vps_stop"),
            types.InlineKeyboardButton("🔄 Restart", callback_data="vps_restart"),
        )
        markup.row(
            types.InlineKeyboardButton("🔑 Creds Again", callback_data="vps_creds"),
            types.InlineKeyboardButton("🗑 Destroy", callback_data="vps_destroy_confirm"),
        )
        markup.row(types.InlineKeyboardButton("🔃 Refresh", callback_data="vps_refresh"))

    elif vps and vps.get("status") == "stopped":
        time_left = _format_time_left(vps.get("expires_at"))
        text = (
            f"🖥️ <b>Aapka Mini VPS</b>\n\n"
            f"🔴 <b>Status:</b> Stopped\n"
            f"⏱️ <b>Time Left:</b> <code>{time_left}</code>\n"
            f"🏷️ <b>Tier:</b> {tier_cfg['label']}\n\n"
            f"VPS band hai. Start karein?"
        )
        markup.row(
            types.InlineKeyboardButton("▶️ Start", callback_data="vps_start"),
            types.InlineKeyboardButton("🗑 Destroy", callback_data="vps_destroy_confirm"),
        )

    else:
        is_free_used = db.has_used_free_vps(user_id)
        is_premium   = db.is_premium(user_id) or is_owner(user_id)

        if is_premium:
            text = (
                f"🖥️ <b>Mini VPS — Premium</b>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⭐ <b>Tier:</b> {tier_cfg['label']}\n"
                f"⏱️ <b>Duration:</b> 30 Days\n"
                f"🧠 <b>RAM:</b> 512MB\n"
                f"⚡ <b>CPU:</b> 1 Core\n"
                f"💾 <b>Storage:</b> 10GB\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Create karo aapka dedicated SSH VPS!\n"
                f"<i>Sudo disabled | Python3, Node, Git available</i>"
            )
            markup.row(types.InlineKeyboardButton("🚀 Create VPS", callback_data="vps_create"))

        elif is_free_used:
            text = (
                f"🖥️ <b>Mini VPS — Free Trial</b>\n\n"
                f"❌ Aap already free trial le chuke hain.\n\n"
                f"💎 <b>Premium</b> lo aur pao:\n"
                f"• 30 days VPS\n"
                f"• 512MB RAM, 1 Core CPU\n"
                f"• 10GB Storage\n"
                f"• 24/7 always-on VPS"
            )
            markup.row(types.InlineKeyboardButton("💎 Get Premium", callback_data="premium"))

        else:
            text = (
                f"🖥️ <b>Mini VPS — Free Trial</b>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🆓 <b>Free Tier:</b>\n"
                f"⏱️ Duration: <b>24 Hours</b>\n"
                f"🧠 RAM: 256MB\n"
                f"⚡ CPU: 0.25 Core\n"
                f"💾 Storage: 2GB\n"
                f"⚠️ <b>Sirf ek baar milega!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💎 <b>Premium VPS:</b>\n"
                f"⏱️ 30 days | 512MB RAM | 1 Core | 10GB\n\n"
                f"<i>Sudo disabled | Python3, Node, Git available</i>"
            )
            markup.row(
                types.InlineKeyboardButton("🆓 Free 24h VPS", callback_data="vps_create_free"),
                types.InlineKeyboardButton("💎 Premium VPS", callback_data="premium"),
            )

    return text, markup


@bot.message_handler(commands=['vps'])
@check_maintenance
@check_banned
def vps_command(message):
    user_id = message.from_user.id
    db.register_user(user_id, message.from_user.username or "user")
    text, markup = _vps_main_menu(user_id)
    bot.reply_to(message, text, reply_markup=markup)

def _handle_vps_callbacks(call):
    user_id = call.from_user.id
    data    = call.data

    if data == "vps_create_free":
        if db.has_used_free_vps(user_id):
            bot.answer_callback_query(call.id, "❌ Free trial already use ho chuka hai!", show_alert=True)
            return
        bot.answer_callback_query(call.id, "⏳ VPS ban raha hai...")
        msg = bot.edit_message_text(
            "⏳ <b>VPS create ho raha hai...</b>\nKuch seconds wait karo.",
            call.message.chat.id, call.message.message_id
        )
        result = vps_manager.create_vps(user_id, tier="free")
        _send_vps_result(call, result, "free")

    elif data == "vps_create":
        tier = _vps_tier_for_user(user_id)
        if tier == "free":
            bot.answer_callback_query(call.id, "❌ Yeh feature premium users ke liye hai!", show_alert=True)
            return
        bot.answer_callback_query(call.id, "⏳ Premium VPS ban raha hai...")
        bot.edit_message_text(
            "⏳ <b>Premium VPS create ho raha hai...</b>\nKuch seconds wait karo.",
            call.message.chat.id, call.message.message_id
        )
        result = vps_manager.create_vps(user_id, tier=tier)
        _send_vps_result(call, result, tier)

    elif data == "vps_stop":
        r = vps_manager.stop_vps(user_id)
        if r["success"]:
            bot.answer_callback_query(call.id, "✅ VPS stopped!")
            text, markup = _vps_main_menu(user_id)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, f"❌ Error: {r['message']}", show_alert=True)

    elif data == "vps_start":
        r = vps_manager.start_vps(user_id)
        if r["success"]:
            bot.answer_callback_query(call.id, "✅ VPS started!")
            text, markup = _vps_main_menu(user_id)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        elif r["message"] == "expired":
            bot.answer_callback_query(call.id, "❌ VPS expire ho gaya tha. Naya banao.", show_alert=True)
            text, markup = _vps_main_menu(user_id)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, f"❌ {r['message']}", show_alert=True)

    elif data == "vps_restart":
        r = vps_manager.restart_vps(user_id)
        if r["success"]:
            bot.answer_callback_query(call.id, "🔄 VPS restarted!")
            text, markup = _vps_main_menu(user_id)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, f"❌ {r['message']}", show_alert=True)

    elif data == "vps_creds":
        vps = db.get_vps(user_id)
        if vps:
            bot.answer_callback_query(call.id, "✅ Credentials sent!")
            bot.send_message(
                call.message.chat.id,
                f"🔐 <b>Your VPS Credentials</b>\n\n"
                f"<code>ssh {vps['username']}@{vps['host']} -p {vps['port']}</code>\n\n"
                f"👤 <b>User:</b> <code>{vps['username']}</code>\n"
                f"🔑 <b>Password:</b> <code>{vps['password']}</code>\n"
                f"🌐 <b>Host:</b> <code>{vps['host']}</code>\n"
                f"🔌 <b>Port:</b> <code>{vps['port']}</code>\n\n"
                f"<i>⚠️ Kisi ke saath share mat karna!</i>"
            )
        else:
            bot.answer_callback_query(call.id, "❌ No VPS found.", show_alert=True)

    elif data == "vps_destroy_confirm":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🗑 Haan, Delete Karo", callback_data="vps_destroy"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="vps_refresh"),
        )
        bot.edit_message_text(
            "⚠️ <b>VPS Delete Karna Chahte Ho?</b>\n\n"
            "Yeh action permanent hai. Saara data delete ho jaega.\n"
            "Free users dobara free trial nahi le payenge.",
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )

    elif data == "vps_destroy":
        r = vps_manager.destroy_vps(user_id)
        if r["success"]:
            bot.answer_callback_query(call.id, "🗑 VPS deleted!")
            text, markup = _vps_main_menu(user_id)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, f"❌ {r['message']}", show_alert=True)

    elif data == "vps_refresh":
        bot.answer_callback_query(call.id, "🔃 Refreshed!")
        text, markup = _vps_main_menu(user_id)
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            pass


def _send_vps_result(call, result, tier):
    user_id = call.from_user.id
    if result["success"]:
        from vps_manager import VPS_TIERS
        tier_cfg   = VPS_TIERS.get(tier, VPS_TIERS["free"])
        time_label = f"{tier_cfg['duration_hours']}h" if tier_cfg['duration_hours'] < 720 else "30 days"

        text = (
            f"✅ <b>VPS Ready!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔐 <b>SSH Command:</b>\n"
            f"<code>ssh {result['username']}@{result['host']} -p {result['port']}</code>\n\n"
            f"👤 <b>Username:</b> <code>{result['username']}</code>\n"
            f"🔑 <b>Password:</b> <code>{result['password']}</code>\n"
            f"🌐 <b>Host:</b> <code>{result['host']}</code>\n"
            f"🔌 <b>Port:</b> <code>{result['port']}</code>\n"
            f"⏱️ <b>Valid For:</b> {time_label}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📦 <b>Available:</b> Python3, Node.js, Git, Nano, Vim\n"
            f"⚠️ <b>Sudo disabled</b> — security ke liye\n\n"
            f"<i>Kisi ke saath credentials share mat karna!</i>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("🖥 VPS Panel", callback_data="vps_refresh"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        logger.log_action(user_id, "vps_created", {"tier": tier, "port": result["port"]})

    elif result.get("message") == "already_running":
        text, markup = _vps_main_menu(user_id)
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    else:
        bot.edit_message_text(
            f"❌ <b>VPS Create Nahi Hua</b>\n\n<code>{result.get('message', 'Unknown error')}</code>",
            call.message.chat.id, call.message.message_id
        )


# ════════════════════════════════════════════════════════════════════
#  Admin VPS Commands ( Those Commands Not Mentioned In Admin_Help Message
# ════════════════════════════════════════════════════════════════════

@bot.message_handler(commands=['vpsList'])
def admin_vps_list(message):
    if not is_admin(message.from_user.id):
        return
    all_vps = vps_manager.admin_list_all()
    if not all_vps:
        bot.reply_to(message, "📋 Koi bhi active VPS nahi hai.")
        return
    lines = [f"📋 <b>All VPS ({len(all_vps)} total)</b>\n"]
    for v in all_vps:
        exp = v.get("expires_at")
        tl  = _format_time_left(exp) if exp else "N/A"
        lines.append(
            f"👤 <code>{v['user_id']}</code> | 🏷 {v.get('tier','?')} | "
            f"🔌 :{v.get('port','?')} | ⏱ {tl} | "
            f"🟢 {v.get('status','?')}"
        )
    bot.reply_to(message, "\n".join(lines))


@bot.message_handler(commands=['vpsRemove'])
def admin_vps_remove(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /vpsRemove &lt;user_id&gt;")
        return
    try:
        target = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ Invalid user_id.")
        return
    r = vps_manager.admin_destroy(target)
    if r["success"]:
        bot.reply_to(message, f"✅ User <code>{target}</code> ka VPS delete kar diya.")
        try:
            bot.send_message(target, "⚠️ <b>Aapka VPS admin ne remove kar diya hai.</b>")
        except:
            pass
    else:
        bot.reply_to(message, f"❌ Error: {r['message']}")


@bot.message_handler(commands=['vpsStop'])
def admin_vps_stop(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /vpsStop &lt;user_id&gt;")
        return
    try:
        target = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ Invalid user_id.")
        return
    r = vps_manager.stop_vps(target)
    if r["success"]:
        bot.reply_to(message, f"✅ User <code>{target}</code> ka VPS stop kar diya.")
        try:
            bot.send_message(target, "⏹️ <b>Aapka VPS admin ne stop kar diya hai.</b>")
        except:
            pass
    else:
        bot.reply_to(message, f"❌ Error: {r['message']}")


@bot.message_handler(commands=['vpsGive'])
def admin_vps_give(message):
    """Admin kisi user ko forcibly VPS de sakta hai."""
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /vpsGive &lt;user_id&gt; &lt;free|premium|owner&gt;")
        return
    try:
        target = int(parts[1])
        tier   = parts[2].lower()
    except:
        bot.reply_to(message, "❌ Invalid args.")
        return
    from vps_manager import VPS_TIERS
    if tier not in VPS_TIERS:
        bot.reply_to(message, f"❌ Invalid tier. Use: {', '.join(VPS_TIERS.keys())}")
        return
    r = vps_manager.create_vps(target, tier=tier)
    if r["success"]:
        bot.reply_to(message, f"✅ User <code>{target}</code> ko {tier} VPS de diya!\nPort: {r['port']}")
        try:
            bot.send_message(
                target,
                f"🎉 <b>Admin ne aapko VPS de diya!</b>\n\n"
                f"<code>ssh {r['username']}@{r['host']} -p {r['port']}</code>\n"
                f"🔑 Password: <code>{r['password']}</code>\n\n"
                f"/vps se manage karo."
            )
        except:
            pass
    else:
        bot.reply_to(message, f"❌ Error: {r['message']}")


@bot.message_handler(commands=['vpsStats'])
def admin_vps_stats(message):
    if not is_admin(message.from_user.id):
        return
    all_vps = vps_manager.admin_list_all()
    running = sum(1 for v in all_vps if v.get("status") == "running")
    stopped = sum(1 for v in all_vps if v.get("status") == "stopped")
    by_tier = {}
    for v in all_vps:
        t = v.get("tier", "unknown")
        by_tier[t] = by_tier.get(t, 0) + 1
    tier_text = "\n".join([f"  • {k}: {v}" for k, v in by_tier.items()])
    bot.reply_to(
        message,
        f"📊 <b>VPS Statistics</b>\n\n"
        f"Total: <code>{len(all_vps)}</code>\n"
        f"🟢 Running: <code>{running}</code>\n"
        f"🔴 Stopped: <code>{stopped}</code>\n\n"
        f"By Tier:\n{tier_text or '  None'}"
    )


# ─── Unknown command ────────────────────────────────────────────────
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"{unknown} 𝚄𝙽𝙺𝙽𝙾𝚆𝙽 𝙲𝙾𝙼𝙼𝙰𝙽𝙳. 𝚄𝚂𝙴 /help 𝙵𝙾𝚁 𝙰𝚅𝙰𝙸𝙻𝙰𝙱𝙻𝙴 𝙲𝙾𝙼𝙼𝙰𝙽𝙳𝚂.")


# ════════════════════════════════════════════════════════════════════
def main():
    __import__('builtins').print(__import__('base64').b64decode('CuKVlOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVlwrilZEgICAgICAgICAgICAgICAgICAgICAgICBUZWFtRGV2ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIOKVkQrilZEgICAgICAgICAgICAgaHR0cHM6Ly9HaXRIdWIuY29tL2p1c3Rmb3J0ZXN0aW5nbm90aGliZ2hlcmUvICAgIOKVkQrilZEgICAgICAgICAgICAgICAgICAgICAgVGVhbURldl9Ib3N0Qm90ICAgICAgICAgICAgICAgICAgICAgICAgIOKVkQrilaDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilaMK4pWRICBQcm9qZWN0IElkICAgICAtPiAyOCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICDilZEK4pWRICBQcm9qZWN0IE5hbWUgICAtPiBTY3JpcHQgSG9zdCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICDilZEK4pWRICBQcm9qZWN0IEFnZSAgICAtPiA0TW9udGgrIChVcGRhdGVkIE9uIDA3LzAzLzIwMjYpICAgICAgICAgICDilZEK4pWRICBJZGVhIEJ5ICAgICAgICAtPiBATVJfQVJNQU5fMDggICAgICAgICAgICAgICAgICAgICAgICAgICAgICDilZEK4pWRICBEZXYgICAgICAgICAgICAtPiBATVJfQVJNQU5fMDggICAgICAgICAgICAgICAgICAgICAgICAgICAgICDilZEK4pWRICBQb3dlcmVkIEJ5ICAgICAtPiBAVGVhbV9YX09nICggT24gVGVsZWdyYW0gKSAgICAgICAgICAgICAgICDilZEK4pWRICBVcGRhdGVzICAgICAgICAtPiBAQ3JpbWVab25lX1VwZGF0ZSAoIE9uIFRlbGVncmFtICkgICAgICAgICDilZEK4pWg4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWjCuKVkSAgU2V0dXAgR3VpZGVzICAgLT4gUmVhZCA+IFJFQURNRS5tZCBPciBWUFNfUkVBRE1FLm1kICAgICAgICAg4pWRCuKVkSAgVGhpcyBTY3JpcHQgUGFydCBPZiBodHRwczovL1RlYW1fWF9PZyBUZWFtICAgICAgICAgICAgICAgICAg4pWRCuKVkSAgQ29weXJpZ2h0IDIwMjYgVGVhbURldiB8IEBUZWFtX1hfT2cgICAgICAgICAgICAgICAgICAgICAgICDilZEK4pWg4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWjCuKVkSAg4oCiIFNvbWUgUXVpY2sgSGVscCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICDilZEK4pWRICAtIFVzZSBJbiBWUFMsIE90aGVyIFdheSBUaGlzIEJvdCBXb24ndCBXb3JrLiAgICAgICAgICAgICAgICDilZEK4pWRICAtIE5lZWQgSGVscD8gQ29udGFjdCBVcyBJbiBAVGVhbV9YX09nJ3MgR3JvdXAgICAgICAgICAgICAgICDilZEK4pWg4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWjCuKVkSAgQ29tcGF0aWJsZSBJbiBCb3RBcGkgOS41IEZ1bGx5ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg4pWRCuKVkSAgQnVpbGQgRm9yIEJvdEFwaSA5LjQgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg4pWRCuKVkSAgV2UnbGwgS2VlcCBVcGRhdGUgSWYgV2UgR290IDUwKyBTdGFycyBJbiBPbmUgTW9udGggICAgICAgICAg4pWRCuKVmuKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVnQo=').decode('utf-8'))
    print(f"Bot Started: @{BOT_USERNAME}")
    print(f"Bot Name: {BOT_NAME}")
    print(f"Owner ID: {OWNER_ID}")
    print("GitHub OAuth server: http://0.0.0.0:5000")

    threading.Thread(target=docker_manager.auto_monitor, daemon=True).start()
    threading.Thread(target=premium_expiry_checker, daemon=True).start()

    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == '__main__':
    main()
