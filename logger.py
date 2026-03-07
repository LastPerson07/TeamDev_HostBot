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

from datetime import datetime
import traceback

class BotLogger:
    def __init__(self, bot, log_channel_id):
        self.bot = bot
        self.log_channel_id = log_channel_id
    
    def log_action(self, user_id, action, details):
        if not self.log_channel_id:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            log_message = f"""
📋 <b>Action Log</b>

<b>User ID:</b> <code>{user_id}</code>
<b>Action:</b> <code>{action}</code>
<b>Time:</b> <code>{timestamp}</code>

<b>Details:</b>
<pre>{self._format_details(details)}</pre>
"""
            
            self.bot.send_message(self.log_channel_id, log_message)
        except Exception as e:
            print(f"Logging error: {e}")
    
    def log_error(self, user_id, error, context):
        if not self.log_channel_id:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            error_message = f"""
❌ <b>Error Log</b>

<b>User ID:</b> <code>{user_id}</code>
<b>Time:</b> <code>{timestamp}</code>
<b>Context:</b> <code>{context}</code>

<b>Error:</b>
<pre>{str(error)}</pre>

<b>Traceback:</b>
<pre>{traceback.format_exc()}</pre>
"""
            
            self.bot.send_message(self.log_channel_id, error_message)
        except Exception as e:
            print(f"Error logging error: {e}")
    
    def log_security_alert(self, user_id, alert_type, details):
        if not self.log_channel_id:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            alert_message = f"""
🚨 <b>Security Alert</b>

<b>Alert Type:</b> <code>{alert_type}</code>
<b>User ID:</b> <code>{user_id}</code>
<b>Time:</b> <code>{timestamp}</code>

<b>Details:</b>
<pre>{self._format_details(details)}</pre>
"""
            
            self.bot.send_message(self.log_channel_id, alert_message)
        except Exception as e:
            print(f"Security logging error: {e}")
    
    def log_admin_action(self, admin_id, action, target_user, details):
        if not self.log_channel_id:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            admin_message = f"""
👑 <b>Admin Action</b>

<b>Admin ID:</b> <code>{admin_id}</code>
<b>Action:</b> <code>{action}</code>
<b>Target User:</b> <code>{target_user}</code>
<b>Time:</b> <code>{timestamp}</code>

<b>Details:</b>
<pre>{self._format_details(details)}</pre>
"""
            
            self.bot.send_message(self.log_channel_id, admin_message)
        except Exception as e:
            print(f"Admin logging error: {e}")
    
    def _format_details(self, details):
        if isinstance(details, dict):
            return '\n'.join([f"{k}: {v}" for k, v in details.items()])
        return str(details)
