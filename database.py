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

from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import hashlib

class Database:
    def __init__(self, mongodb_uri):
        self.client = MongoClient(mongodb_uri)
        self.db = self.client['telegram_host_bot']
        self.users = self.db['users']
        self.projects = self.db['projects']
        self.logs = self.db['logs']
        self.warnings = self.db['warnings']
        self.github_tokens = self.db['github_tokens']
        self.pip_installs = self.db['pip_installs']
        self.websites = self.db['websites']

        self.vps = self.db['vps']

        self.users.create_index('user_id', unique=True)
        self.projects.create_index('user_id')
        self.projects.create_index('container_id')
        self.github_tokens.create_index('user_id', unique=True)
        self.vps.create_index('user_id', unique=True)

    def register_user(self, user_id, username):
        user = self.users.find_one({'user_id': user_id})
        if not user:
            self.users.insert_one({
                'user_id': user_id, 'username': username,
                'premium': False, 'premium_expiry': None,
                'banned': False, 'restricted': False,
                'joined_at': datetime.now(), 'device_fingerprint': None,
                'warnings': 0, 'force_sub_verified': False,
                'last_project_deleted_at': None,
                'last_run_started_at': None,
            })
        else:
            self.users.update_one({'user_id': user_id}, {'$set': {'username': username}})

    def get_user(self, user_id):
        return self.users.find_one({'user_id': user_id})

    def get_all_users(self):
        return list(self.users.find({}))

    def set_force_sub_verified(self, user_id, status):
        self.users.update_one({'user_id': user_id}, {'$set': {'force_sub_verified': status}}, upsert=True)

    def is_force_sub_verified(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        return bool(user and user.get('force_sub_verified', False))

    def is_premium(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        if not user or not user.get('premium', False): return False
        expiry = user.get('premium_expiry')
        if expiry and datetime.now() > expiry:
            self.users.update_one({'user_id': user_id}, {'$set': {'premium': False, 'premium_expiry': None}})
            return False
        return True

    def set_premium(self, user_id, status, days=None):
        update = {'premium': status}
        if status and days: update['premium_expiry'] = datetime.now() + timedelta(days=days)
        elif not status: update['premium_expiry'] = None
        self.users.update_one({'user_id': user_id}, {'$set': update}, upsert=True)

    def get_premium_expiry(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        return user.get('premium_expiry') if user else None

    def get_expiring_premium_users(self, hours=24):
        now = datetime.now()
        soon = now + timedelta(hours=hours)
        return list(self.users.find({'premium': True, 'premium_expiry': {'$gte': now, '$lte': soon}, 'expiry_alert_sent': {'$ne': True}}))

    def mark_expiry_alert_sent(self, user_id):
        self.users.update_one({'user_id': user_id}, {'$set': {'expiry_alert_sent': True}})

    def is_banned(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        return user and user.get('banned', False)

    def ban_user(self, user_id, reason):
        self.users.update_one({'user_id': user_id}, {'$set': {'banned': True, 'ban_reason': reason, 'ban_date': datetime.now()}})

    def unban_user(self, user_id):
        self.users.update_one({'user_id': user_id}, {'$set': {'banned': False}})

    def is_restricted(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        return user and user.get('restricted', False)

    def restrict_user(self, user_id, status):
        self.users.update_one({'user_id': user_id}, {'$set': {'restricted': status}})

    def is_admin(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        return user and user.get('is_admin', False)

    def add_admin(self, user_id):
        self.users.update_one({'user_id': user_id}, {'$set': {'is_admin': True}}, upsert=True)

    def remove_admin(self, user_id):
        self.users.update_one({'user_id': user_id}, {'$set': {'is_admin': False}})

    def get_all_admins(self):
        return list(self.users.find({'is_admin': True}))

    def set_last_deleted_at(self, user_id):
        self.users.update_one({'user_id': user_id}, {'$set': {'last_project_deleted_at': datetime.now()}})

    def get_delete_cooldown_remaining(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        if not user: return 0
        last_del = user.get('last_project_deleted_at')
        if not last_del: return 0
        cooldown_secs = 30 * 60
        elapsed = (datetime.now() - last_del).total_seconds()
        remaining = cooldown_secs - elapsed
        return max(0, int(remaining))

    def record_run_started(self, user_id):
        self.users.update_one({'user_id': user_id}, {'$set': {'last_run_started_at': datetime.now()}}, upsert=True)

    def get_next_run_allowed_at(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        if not user: return None
        last_run = user.get('last_run_started_at')
        if not last_run: return None
        next_allowed = last_run + timedelta(hours=48)
        if datetime.now() >= next_allowed: return None
        return next_allowed

    def can_start_run(self, user_id):
        next_allowed = self.get_next_run_allowed_at(user_id)
        if next_allowed is None: return True, None
        return False, next_allowed

    def save_github_token(self, user_id, access_token, github_username, github_user_id):
        self.github_tokens.update_one(
            {'user_id': user_id},
            {'$set': {'user_id': user_id, 'access_token': access_token,
                      'github_username': github_username, 'github_user_id': github_user_id,
                      'connected_at': datetime.now()}},
            upsert=True
        )

    def get_github_token(self, user_id):
        doc = self.github_tokens.find_one({'user_id': user_id})
        return doc.get('access_token') if doc else None

    def get_github_info(self, user_id):
        return self.github_tokens.find_one({'user_id': user_id})

    def remove_github_token(self, user_id):
        self.github_tokens.delete_one({'user_id': user_id})

    def is_github_connected(self, user_id):
        return self.github_tokens.find_one({'user_id': user_id}) is not None

    def check_duplicate_device(self, user_id, message):
        fingerprint_data = f"{message.from_user.first_name}_{message.from_user.last_name}_{message.from_user.language_code}"
        fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
        existing = self.users.find_one({'device_fingerprint': fingerprint, 'user_id': {'$ne': user_id}})
        if existing:
            self.log_action(user_id, "duplicate_account_detected", {"original_user": existing['user_id'], "duplicate_user": user_id})
            return True
        self.users.update_one({'user_id': user_id}, {'$set': {'device_fingerprint': fingerprint}}, upsert=True)
        return False

    def add_project(self, project_data):
        return self.projects.insert_one(project_data).inserted_id

    def get_project(self, project_id):
        if isinstance(project_id, str): project_id = ObjectId(project_id)
        return self.projects.find_one({'_id': project_id})

    def get_user_projects(self, user_id):
        return list(self.projects.find({'user_id': user_id}))

    def count_user_projects(self, user_id):
        return self.projects.count_documents({'user_id': user_id})

    def update_project(self, project_id, update_data):
        if isinstance(project_id, str): project_id = ObjectId(project_id)
        self.projects.update_one({'_id': project_id}, {'$set': update_data})

    def delete_project(self, project_id):
        if isinstance(project_id, str): project_id = ObjectId(project_id)
        self.projects.delete_one({'_id': project_id})

    def project_name_exists(self, user_id, name):
        return self.projects.find_one({'user_id': user_id, 'name': name}) is not None

    def get_all_running_projects(self):
        return list(self.projects.find({'status': 'running'}))

    def log_pip_install(self, user_id, project_id, library, success):
        self.pip_installs.insert_one({'user_id': user_id, 'project_id': str(project_id), 'library': library, 'success': success, 'timestamp': datetime.now()})

    def add_warning(self, user_id, reason):
        self.warnings.insert_one({'user_id': user_id, 'reason': reason, 'timestamp': datetime.now()})
        self.users.update_one({'user_id': user_id}, {'$inc': {'warnings': 1}})
        user = self.users.find_one({'user_id': user_id})
        total = user.get('warnings', 0) if user else 0
        if total >= 3:
            self.ban_user(user_id, "Too many warnings")
            self.log_action(user_id, "auto_banned", {"reason": "Too many warnings", "total_warnings": total})
        elif total == 2:

            self.log_action(user_id, "warning_issued", {"reason": reason, "total_warnings": total, "alert": "1 more warning will trigger auto-ban"})
        else:
            self.log_action(user_id, "warning_issued", {"reason": reason, "total_warnings": total})

    def get_user_warnings(self, user_id):
        return list(self.warnings.find({'user_id': user_id}))

    def log_action(self, user_id, action, details):
        self.logs.insert_one({'user_id': user_id, 'action': action, 'details': details, 'timestamp': datetime.now()})

    def get_stats(self):
        return {
            'total_users': self.users.count_documents({}),
            'premium_users': self.users.count_documents({'premium': True}),
            'banned_users': self.users.count_documents({'banned': True}),
            'restricted_users': self.users.count_documents({'restricted': True}),
            'total_projects': self.projects.count_documents({}),
            'running_projects': self.projects.count_documents({'status': 'running'}),
            'github_connected': self.github_tokens.count_documents({}),
            'active_vps': self.vps.count_documents({'status': 'running'})
        }

    def save_vps(self, vps_data: dict):
        self.vps.update_one(
            {'user_id': vps_data['user_id']},
            {'$set': vps_data},
            upsert=True
        )

    def get_vps(self, user_id: int):
        return self.vps.find_one({'user_id': user_id})

    def get_all_vps(self):
        return list(self.vps.find({}))

    def update_vps_status(self, user_id: int, status: str):
        self.vps.update_one({'user_id': user_id}, {'$set': {'status': status}})

    def delete_vps(self, user_id: int):
        self.vps.delete_one({'user_id': user_id})

    def has_used_free_vps(self, user_id: int) -> bool:
        user = self.users.find_one({'user_id': user_id})
        return bool(user and user.get('free_vps_used', False))

    def mark_free_vps_used(self, user_id: int):
        self.users.update_one({'user_id': user_id}, {'$set': {'free_vps_used': True}}, upsert=True)
