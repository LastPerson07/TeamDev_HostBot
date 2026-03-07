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

import docker
import os
import secrets
import string
import threading
import time
from datetime import datetime, timedelta

VPS_TIERS = {
    "free": {
        "label": "Free Trial",
        "duration_hours": 12,
        "cpu_quota": 25000,
        "mem_limit": "256m",
        "storage": "2g",
        "one_time": True,
    },
    "premium": {
        "label": "Premium",
        "duration_hours": 720,
        "cpu_quota": 100000,
        "mem_limit": "512m",
        "storage": "10g",
        "one_time": False,
    },
    "owner": {
        "label": "Owner",
        "duration_hours": 999999,
        "cpu_quota": 200000,
        "mem_limit": "1g",
        "storage": "20g",
        "one_time": False,
    }
}

SSH_PORT_START = 32000
SSH_PORT_END   = 33000

VPS_BASE_IMAGE = "telegram-bot-vps-base"


class VpsManager:
    def __init__(self, database, host_ip: str):
        self.db       = database
        self.host_ip  = host_ip
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"[VPS] Docker not available: {e}")
            self.client = None
        self._expiry_thread = threading.Thread(target=self._expiry_loop, daemon=True)
        self._expiry_thread.start()

    def _find_free_port(self):
        used = set()
        try:
            for c in self.client.containers.list(all=True):
                ports = c.ports.get('22/tcp') or []
                for p in ports:
                    used.add(int(p['HostPort']))
        except:
            pass
        for port in range(SSH_PORT_START, SSH_PORT_END):
            if port not in used:
                return port
        raise RuntimeError("No free SSH ports available")

    def _gen_password(self, length=16):
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(chars) for _ in range(length))

    def create_vps(self, user_id: int, tier: str = "free") -> dict:
        if not self.client:
            return {"success": False, "message": "Docker unavailable on server."}

        cfg = VPS_TIERS.get(tier, VPS_TIERS["free"])
        existing = self.db.get_vps(user_id)

        if existing and existing.get("status") == "running":
            return {"success": False, "message": "already_running", "vps": existing}

        if cfg["one_time"] and self.db.has_used_free_vps(user_id):
            return {"success": False, "message": "free_used"}

        container_name = f"vps_{user_id}"

        try:
            old = self.client.containers.get(container_name)
            old.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception as e:
            print(f"[VPS] Cleanup error: {e}")

        password = self._gen_password()
        port     = self._find_free_port()
        expires  = datetime.now() + timedelta(hours=cfg["duration_hours"])

        try:
            container = self.client.containers.run(
                VPS_BASE_IMAGE,
                detach=True,
                name=container_name,
                ports={"22/tcp": port},
                mem_limit=cfg["mem_limit"],
                cpu_quota=cfg["cpu_quota"],
                cpu_period=100000,
                environment={
                    "VPS_PASSWORD": password,
                    "VPS_USER": "vpsuser",
                    "VPS_TIER": cfg["label"],
                    "VPS_EXPIRES": f"{cfg['duration_hours']}h" if cfg['duration_hours'] < 720 else "30 Days",
                },
                restart_policy={"Name": "unless-stopped"},
                labels={
                    "vps_user_id": str(user_id),
                    "vps_tier": tier,
                    "vps_expires": expires.isoformat(),
                }
            )

            time.sleep(3)

            vps_data = {
                "user_id":      user_id,
                "container_id": container.id,
                "container_name": container_name,
                "host":         self.host_ip,
                "port":         port,
                "username":     "vpsuser",
                "password":     password,
                "tier":         tier,
                "status":       "running",
                "created_at":   datetime.now(),
                "expires_at":   expires,
            }

            self.db.save_vps(vps_data)

            if cfg["one_time"]:
                self.db.mark_free_vps_used(user_id)

            return {"success": True, **vps_data}

        except docker.errors.ImageNotFound:
            return {
                "success": False,
                "message": "VPS base image not built yet. Admin ko contact karo."
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def stop_vps(self, user_id: int) -> dict:
        vps = self.db.get_vps(user_id)
        if not vps:
            return {"success": False, "message": "No VPS found."}
        try:
            c = self.client.containers.get(vps["container_name"])
            c.stop(timeout=10)
            self.db.update_vps_status(user_id, "stopped")
            return {"success": True}
        except docker.errors.NotFound:
            self.db.update_vps_status(user_id, "stopped")
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def start_vps(self, user_id: int) -> dict:
        vps = self.db.get_vps(user_id)
        if not vps:
            return {"success": False, "message": "No VPS found."}
        if datetime.now() > vps["expires_at"]:
            self.destroy_vps(user_id)
            return {"success": False, "message": "expired"}
        try:
            c = self.client.containers.get(vps["container_name"])
            c.start()
            self.db.update_vps_status(user_id, "running")
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def restart_vps(self, user_id: int) -> dict:
        vps = self.db.get_vps(user_id)
        if not vps:
            return {"success": False, "message": "No VPS found."}
        try:
            c = self.client.containers.get(vps["container_name"])
            c.restart(timeout=10)
            self.db.update_vps_status(user_id, "running")
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def destroy_vps(self, user_id: int, reason: str = "manual") -> dict:
        vps = self.db.get_vps(user_id)
        if not vps:
            return {"success": False, "message": "No VPS found."}
        try:
            c = self.client.containers.get(vps["container_name"])
            c.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception as e:
            return {"success": False, "message": str(e)}

        self.db.delete_vps(user_id)
        return {"success": True}

    def get_vps_stats(self, user_id: int) -> dict:
        vps = self.db.get_vps(user_id)
        if not vps:
            return None
        try:
            c = self.client.containers.get(vps["container_name"])
            stats = c.stats(stream=False)
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                        stats["precpu_stats"]["cpu_usage"]["total_usage"]
            sys_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                        stats["precpu_stats"]["system_cpu_usage"]
            num_cpus  = stats["cpu_stats"].get("online_cpus", 1)
            cpu_pct   = (cpu_delta / sys_delta) * num_cpus * 100.0 if sys_delta > 0 else 0

            mem_used  = stats["memory_stats"]["usage"]
            mem_limit = stats["memory_stats"]["limit"]
            mem_pct   = (mem_used / mem_limit) * 100

            return {
                "status":    c.status,
                "cpu_pct":   round(cpu_pct, 1),
                "mem_used":  mem_used // (1024 * 1024),
                "mem_limit": mem_limit // (1024 * 1024),
                "mem_pct":   round(mem_pct, 1),
            }
        except:
            return {"status": vps.get("status", "unknown"), "cpu_pct": 0, "mem_used": 0, "mem_limit": 0, "mem_pct": 0}

    def admin_list_all(self) -> list:
        return self.db.get_all_vps()

    def admin_destroy(self, user_id: int) -> dict:
        return self.destroy_vps(user_id, reason="admin_force")

    def _expiry_loop(self):
        while True:
            try:
                all_vps = self.db.get_all_vps()
                for vps in all_vps:
                    expires = vps.get("expires_at")
                    if not expires:
                        continue
                    if isinstance(expires, str):
                        expires = datetime.fromisoformat(expires)
                    if datetime.now() > expires and vps.get("status") == "running":
                        uid = vps["user_id"]
                        print(f"[VPS] Expiring VPS for user {uid}")
                        self.destroy_vps(uid, reason="expired")
                        if self.notify_callback:
                            try:
                                self.notify_callback(
                                    uid,
                                    "⏰ <b>Aapka VPS expire ho gaya!</b>\n\n"
                                    "Free trial khatam — Premium lo for 24/7 VPS.\n"
                                    "/vps se dobara dekho."
                                )
                            except:
                                pass
            except Exception as e:
                print(f"[VPS Expiry Loop] Error: {e}")
            time.sleep(60)

    notify_callback = None
