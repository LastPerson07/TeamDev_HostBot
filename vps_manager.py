"""
VPS Manager — stubbed out for Railway.
SSH-based VPS containers are not possible without Docker socket.
All methods return a clear "not available" message.
"""

VPS_TIERS = {
    "free":    {"label": "Free Trial",  "duration_hours": 24,     "one_time": True},
    "premium": {"label": "Premium",     "duration_hours": 720,    "one_time": False},
    "owner":   {"label": "Owner",       "duration_hours": 999999, "one_time": False},
}

_MSG = "VPS feature requires a dedicated VPS server and is not available on this hosting."


class VpsManager:
    def __init__(self, database, host_ip: str):
        self.db              = database
        self.host_ip         = host_ip
        self.notify_callback = None

    def create_vps(self, user_id, tier="free"):
        return {"success": False, "message": _MSG}

    def stop_vps(self, user_id):
        return {"success": False, "message": _MSG}

    def start_vps(self, user_id):
        return {"success": False, "message": _MSG}

    def restart_vps(self, user_id):
        return {"success": False, "message": _MSG}

    def destroy_vps(self, user_id, reason="manual"):
        return {"success": False, "message": _MSG}

    def get_vps_stats(self, user_id):
        return None

    def admin_list_all(self):
        return []

    def admin_destroy(self, user_id):
        return {"success": False, "message": _MSG}
