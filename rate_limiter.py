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

import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, database):
        self.db = database
        self.user_actions = defaultdict(list)
        self.rate_limits = {
            'upload': {'max': 3, 'window': 3600},
            'github': {'max': 5, 'window': 3600},
            'command': {'max': 10, 'window': 60},
        }
    
    def check_limit(self, user_id, action='command'):
        current_time = time.time()
        
        limit_config = self.rate_limits.get(action, self.rate_limits['command'])
        max_requests = limit_config['max']
        time_window = limit_config['window']
        
        key = f"{user_id}_{action}"
        self.user_actions[key] = [
            t for t in self.user_actions[key] 
            if current_time - t < time_window
        ]
        
        if len(self.user_actions[key]) >= max_requests:
            return False
        
        self.user_actions[key].append(current_time)
        return True
    
    def get_cooldown_remaining(self, user_id, action='command'):
        current_time = time.time()
        limit_config = self.rate_limits.get(action, self.rate_limits['command'])
        time_window = limit_config['window']
        
        key = f"{user_id}_{action}"
        if key not in self.user_actions or not self.user_actions[key]:
            return 0
        
        oldest_request = min(self.user_actions[key])
        time_passed = current_time - oldest_request
        
        if time_passed >= time_window:
            return 0
        
        return int(time_window - time_passed)
    
    def reset_limits(self, user_id):
        keys_to_remove = [k for k in self.user_actions.keys() if k.startswith(f"{user_id}_")]
        for key in keys_to_remove:
            del self.user_actions[key]
