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


import os
import threading
import requests
from flask import Flask, request, redirect, jsonify

GITHUB_CLIENT_ID     = os.environ.get("GITHUB_CLIENT_ID", "Ov23liz6u0fps68CsNrp")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "5aaea2e99f5fde63353f482534f21c38e6c5c5fc")
GITHUB_REDIRECT_URI  = "https://auth.teamdev.sbs/callback"
AUTH_BASE_URL        = "https://auth.teamdev.sbs"

_pending_states: dict[str, int] = {}
_db   = None
_bot  = None

app = Flask(__name__)


def init(db_instance, bot_instance):
    global _db, _bot
    _db  = db_instance
    _bot = bot_instance


def build_oauth_url(user_id: int) -> str:
    import secrets
    state = f"{user_id}_{secrets.token_hex(16)}"
    _pending_states[state] = user_id
    scope = "repo,read:user"
    return (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        f"&scope={scope}"
        f"&state={state}"
    )

BASE_STYLE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — TeamDev Host</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:       #05070f;
    --surface:  #0c1020;
    --border:   #1a2540;
    --accent:   #4fffb0;
    --accent2:  #00c6ff;
    --red:      #ff4f6b;
    --text:     #c8d8f0;
    --muted:    #4a6080;
    --mono:     'Share Tech Mono', monospace;
    --sans:     'Syne', sans-serif;
  }}

  html, body {{
    min-height: 100vh;
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    overflow-x: hidden;
  }}

  /* ── Animated grid background ── */
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(79,255,176,.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(79,255,176,.035) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }}

  /* ── Glowing orbs ── */
  .orb {{
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    opacity: .18;
    pointer-events: none;
    z-index: 0;
    animation: drift 12s ease-in-out infinite alternate;
  }}
  .orb-1 {{ width:420px; height:420px; background:var(--accent2); top:-100px; right:-80px; animation-delay:0s; }}
  .orb-2 {{ width:340px; height:340px; background:var(--accent);  bottom:-80px; left:-80px; animation-delay:-5s; }}

  @keyframes drift {{
    from {{ transform: translate(0,0) scale(1); }}
    to   {{ transform: translate(30px,20px) scale(1.08); }}
  }}

  /* ── Layout ── */
  .wrapper {{
    position: relative;
    z-index: 1;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    gap: 32px;
  }}

  /* ── Brand header ── */
  .brand {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }}
  .brand-logo {{
    width: 64px; height: 64px;
    border-radius: 16px;
    background: linear-gradient(135deg, var(--accent2), var(--accent));
    display: flex; align-items: center; justify-content: center;
    font-size: 28px;
    box-shadow: 0 0 40px rgba(0,198,255,.35);
    animation: pulse-logo 3s ease-in-out infinite;
  }}
  @keyframes pulse-logo {{
    0%,100% {{ box-shadow: 0 0 30px rgba(0,198,255,.3); }}
    50%      {{ box-shadow: 0 0 55px rgba(0,198,255,.6); }}
  }}
  .brand-name {{
    font-size: 13px;
    font-family: var(--mono);
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
  }}

  /* ── Card ── */
  .card {{
    width: 100%;
    max-width: 480px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 40px 36px;
    position: relative;
    overflow: hidden;
    animation: card-in .6s cubic-bezier(.22,1,.36,1) both;
  }}
  @keyframes card-in {{
    from {{ opacity:0; transform: translateY(30px) scale(.97); }}
    to   {{ opacity:1; transform: translateY(0)    scale(1);   }}
  }}
  .card::before {{
    content:'';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent2), var(--accent), transparent);
    animation: shimmer 3s linear infinite;
    background-size: 200% 100%;
  }}
  @keyframes shimmer {{
    from {{ background-position: -200% 0; }}
    to   {{ background-position: 200% 0; }}
  }}

  /* ── Status icon ── */
  .status-icon {{
    width: 72px; height: 72px;
    border-radius: 50%;
    margin: 0 auto 24px;
    display: flex; align-items: center; justify-content: center;
    font-size: 32px;
    animation: icon-pop .5s cubic-bezier(.34,1.56,.64,1) .3s both;
  }}
  @keyframes icon-pop {{
    from {{ transform: scale(0); opacity:0; }}
    to   {{ transform: scale(1); opacity:1; }}
  }}
  .status-icon.success {{
    background: rgba(79,255,176,.12);
    border: 1.5px solid rgba(79,255,176,.4);
    box-shadow: 0 0 30px rgba(79,255,176,.2);
  }}
  .status-icon.error {{
    background: rgba(255,79,107,.12);
    border: 1.5px solid rgba(255,79,107,.4);
    box-shadow: 0 0 30px rgba(255,79,107,.2);
  }}

  /* ── Typography ── */
  h1 {{
    font-size: 22px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 8px;
    letter-spacing: -.3px;
  }}
  h1 .highlight {{ color: var(--accent); }}
  h1 .highlight-red {{ color: var(--red); }}

  .subtitle {{
    text-align: center;
    color: var(--muted);
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 24px;
  }}

  /* ── Info row ── */
  .info-box {{
    background: rgba(255,255,255,.03);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 24px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  .info-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--mono);
    font-size: 13px;
  }}
  .info-row .label {{
    color: var(--muted);
    min-width: 80px;
  }}
  .info-row .value {{
    color: var(--accent2);
    font-weight: 600;
  }}
  .dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 6px var(--accent);
    animation: blink 1.4s ease-in-out infinite;
    flex-shrink: 0;
  }}
  @keyframes blink {{
    0%,100% {{ opacity:1; }} 50% {{ opacity:.2; }}
  }}

  /* ── Buttons ── */
  .btn-group {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 8px;
  }}
  .btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 13px 24px;
    border-radius: 12px;
    font-family: var(--sans);
    font-size: 14px;
    font-weight: 700;
    text-decoration: none;
    letter-spacing: .3px;
    transition: transform .15s, box-shadow .15s, background .15s;
    cursor: pointer;
  }}
  .btn:hover {{ transform: translateY(-2px); }}
  .btn:active {{ transform: translateY(0); }}

  .btn-primary {{
    background: linear-gradient(135deg, var(--accent2), var(--accent));
    color: #05070f;
    box-shadow: 0 4px 20px rgba(0,198,255,.25);
  }}
  .btn-primary:hover {{ box-shadow: 0 6px 28px rgba(0,198,255,.45); }}

  .btn-telegram {{
    background: rgba(41,182,246,.12);
    border: 1px solid rgba(41,182,246,.3);
    color: #29b6f6;
  }}
  .btn-telegram:hover {{ background: rgba(41,182,246,.2); border-color: rgba(41,182,246,.6); }}

  .btn-ghost {{
    background: rgba(255,255,255,.04);
    border: 1px solid var(--border);
    color: var(--muted);
  }}
  .btn-ghost:hover {{ background: rgba(255,255,255,.08); color: var(--text); }}

  /* ── Divider ── */
  .divider {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 4px 0;
    color: var(--muted);
    font-size: 11px;
    font-family: var(--mono);
    letter-spacing: 1px;
  }}
  .divider::before, .divider::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center;
    font-size: 12px;
    font-family: var(--mono);
    color: var(--muted);
    line-height: 1.7;
  }}
  .footer a {{ color: var(--accent2); text-decoration: none; }}
  .footer a:hover {{ color: var(--accent); }}

  /* ── Telegram SVG icon ── */
  .tg-icon {{
    width: 18px; height: 18px; flex-shrink: 0;
  }}

  /* ── GitHub icon ── */
  .gh-icon {{
    width: 18px; height: 18px; flex-shrink: 0;
  }}

  /* ── Tag ── */
  .tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 11px;
    font-family: var(--mono);
    letter-spacing: .5px;
    background: rgba(79,255,176,.1);
    border: 1px solid rgba(79,255,176,.25);
    color: var(--accent);
    margin-bottom: 16px;
  }}

  @media (max-width: 480px) {{
    .card {{ padding: 28px 20px; }}
    h1 {{ font-size: 18px; }}
  }}
</style>
</head>
<body>
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="wrapper">

  <div class="brand">
    <div class="brand-logo">🚀</div>
    <span class="brand-name">TeamDev Host</span>
  </div>

  {content}

  <div class="footer">
    Powered by <a href="https://t.me/TEAM_X_OG" target="_blank">@TEAM_X_OG</a> &nbsp;·&nbsp;
    Dev <a href="https://t.me/MR_ARMAN_08" target="_blank">@MR_ARMAN_08</a><br>
    <span style="opacity:.5;">auth.teamdev.sbs · secure oauth gateway</span>
  </div>

</div>
</body>
</html>
"""

TG_SVG = """<svg class="tg-icon" viewBox="0 0 24 24" fill="currentColor">
  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.248l-2.018 9.509c-.145.658-.537.818-1.084.508l-3-2.21-1.447 1.394c-.16.16-.295.295-.605.295l.213-3.053 5.56-5.023c.242-.213-.054-.333-.373-.12l-6.871 4.326-2.962-.924c-.643-.204-.657-.643.136-.953l11.57-4.461c.537-.194 1.006.131.881.712z"/>
</svg>"""

GH_SVG = """<svg class="gh-icon" viewBox="0 0 24 24" fill="currentColor">
  <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
</svg>"""


def render_page(title, content):
    return BASE_STYLE.format(title=title, content=content)


def success_page(github_username, github_avatar=None):
    avatar_html = ""
    if github_avatar:
        avatar_html = f'<img src="{github_avatar}" alt="avatar" style="width:44px;height:44px;border-radius:50%;border:2px solid rgba(79,255,176,.4);">'

    content = f"""
  <div class="card">
    <div class="status-icon success">✅</div>

    <div style="text-align:center; margin-bottom:4px;">
      <span class="tag">● AUTHENTICATED</span>
    </div>

    <h1>GitHub <span class="highlight">Connected</span></h1>
    <p class="subtitle">Your account has been linked successfully.<br>You can now deploy public & private repositories.</p>

    <div class="info-box">
      <div class="info-row">
        {avatar_html}
        <span class="label">Account</span>
        <span class="value">@{github_username}</span>
        <div class="dot" style="margin-left:auto;"></div>
      </div>
      <div class="info-row">
        <span style="font-size:16px;">🔒</span>
        <span class="label">Access</span>
        <span class="value">repo · read:user</span>
      </div>
      <div class="info-row">
        <span style="font-size:16px;">🛡</span>
        <span class="label">Status</span>
        <span class="value" style="color:var(--accent);">Active</span>
      </div>
    </div>

    <div class="btn-group">
      <a href="https://t.me/TEAM_X_OG" target="_blank" class="btn btn-telegram">
        {TG_SVG}
        Support — @TEAM_X_OG
      </a>
      <div class="divider">or</div>
      <a href="https://t.me/MR_ARMAN_08" target="_blank" class="btn btn-ghost">
        {TG_SVG}
        Developer — @MR_ARMAN_08
      </a>
    </div>

    <p style="text-align:center;font-size:12px;color:var(--muted);margin-top:16px;font-family:var(--mono);">
      ← Return to Telegram and use /repos to start deploying
    </p>
  </div>
"""
    return render_page("Connected", content)


def error_page(reason="Invalid or expired request."):
    content = f"""
  <div class="card">
    <div class="status-icon error">❌</div>

    <div style="text-align:center; margin-bottom:4px;">
      <span class="tag" style="background:rgba(255,79,107,.1);border-color:rgba(255,79,107,.3);color:var(--red);">● AUTH FAILED</span>
    </div>

    <h1>Auth <span class="highlight-red">Failed</span></h1>
    <p class="subtitle">Something went wrong during authentication.<br>Please try again from Telegram.</p>

    <div class="info-box" style="border-color:rgba(255,79,107,.2);">
      <div class="info-row">
        <span style="font-size:16px;">⚠️</span>
        <span class="label">Reason</span>
        <span class="value" style="color:var(--red);">{reason}</span>
      </div>
    </div>

    <div class="btn-group">
      <a href="https://t.me/TEAM_X_OG" target="_blank" class="btn btn-telegram">
        {TG_SVG}
        Get Help — @TEAM_X_OG
      </a>
      <div class="divider">or</div>
      <a href="https://t.me/MR_ARMAN_08" target="_blank" class="btn btn-ghost">
        {TG_SVG}
        Contact Dev — @MR_ARMAN_08
      </a>
    </div>

    <p style="text-align:center;font-size:12px;color:var(--muted);margin-top:16px;font-family:var(--mono);">
      ← Go back to Telegram and send /connect to retry
    </p>
  </div>
"""
    return render_page("Error", content)


def index_page():
    content = f"""
  <div class="card">
    <div class="status-icon success" style="font-size:28px;">🚀</div>

    <div style="text-align:center; margin-bottom:4px;">
      <span class="tag">● ONLINE</span>
    </div>

    <h1>TeamDev <span class="highlight">Host Bot</span></h1>
    <p class="subtitle">GitHub OAuth Gateway for Telegram Bot Hosting.<br>Authorize your GitHub account to deploy public & private repos.</p>

    <div class="info-box">
      <div class="info-row">
        <div class="dot"></div>
        <span class="label">Service</span>
        <span class="value">GitHub OAuth 2.0</span>
      </div>
      <div class="info-row">
        <div class="dot"></div>
        <span class="label">Status</span>
        <span class="value" style="color:var(--accent);">Running</span>
      </div>
      <div class="info-row">
        <div class="dot"></div>
        <span class="label">Endpoint</span>
        <span class="value">auth.teamdev.sbs</span>
      </div>
    </div>

    <div class="btn-group">
      <a href="https://t.me/TEAM_X_OG" target="_blank" class="btn btn-primary">
        {TG_SVG}
        Join Support — @TEAM_X_OG
      </a>
      <div class="divider">contact</div>
      <a href="https://t.me/MR_ARMAN_08" target="_blank" class="btn btn-ghost">
        {TG_SVG}
        Developer — @MR_ARMAN_08
      </a>
    </div>
  </div>
"""
    return render_page("TeamDev Host", content)


@app.route("/")
def index():
    return index_page()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "TeamDev GitHub Auth"})

from emoji import *

@app.route("/callback")
def github_callback():
    code  = request.args.get("code")
    state = request.args.get("state")

    if not code or not state or state not in _pending_states:
        return error_page("Invalid or expired auth request."), 400

    user_id = _pending_states.pop(state)

    resp = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id":     GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code":          code,
            "redirect_uri":  GITHUB_REDIRECT_URI,
        },
        timeout=15
    )

    token_data   = resp.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return error_page("Could not retrieve access token from GitHub."), 400

    user_resp = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"token {access_token}",
            "Accept":        "application/vnd.github.v3+json"
        },
        timeout=15
    )
    github_user     = user_resp.json()
    github_username = github_user.get("login", "unknown")
    github_user_id  = github_user.get("id", 0)
    github_avatar   = github_user.get("avatar_url", "")

    if _db:
        _db.save_github_token(user_id, access_token, github_username, github_user_id)

    if _bot:
        try:
            _bot.send_message(
                user_id,
                f"{i} <b>GitHub Connected Successfully!</b>\n\n"
                f"{alert} <b>Account:</b> <code>@{github_username}</code> {verified}\n\n"
                f"You can now use /repos to browse and deploy your repositories!",
                parse_mode="HTML"
            )
        except Exception:
            pass

    return success_page(github_username, github_avatar)

def get_user_repos(access_token: str, page: int = 1) -> list:
    resp = requests.get(
        "https://api.github.com/user/repos",
        headers={
            "Authorization": f"token {access_token}",
            "Accept":        "application/vnd.github.v3+json"
        },
        params={"per_page": 30, "page": page, "sort": "updated", "affiliation": "owner"},
        timeout=15
    )
    if resp.status_code == 200:
        return resp.json()
    return []


def clone_private_repo(access_token: str, repo_full_name: str, dest_dir: str) -> tuple[bool, str]:
    import subprocess
    auth_url = f"https://oauth2:{access_token}@github.com/{repo_full_name}.git"
    result   = subprocess.run(
        ["git", "clone", "--depth", "1", auth_url, dest_dir],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode == 0:
        return True, ""
    return False, result.stderr


def start_server():
    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    thread.start()
