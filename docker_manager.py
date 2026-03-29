"""
Railway-compatible DockerManager replacement.
Uses subprocess instead of Docker containers.
"""

import subprocess
import os
import shutil
import signal
import json
import threading
import time
import psutil
from datetime import datetime

PROJECTS_DIR = os.environ.get("PROJECTS_DIR", "/tmp/projects")
LOGS_DIR     = os.environ.get("LOGS_DIR", "/tmp/logs")
PIDS_FILE    = os.environ.get("PIDS_FILE", "/tmp/pids.json")

SLEEP_REASON_AUTO   = "auto_stop_12h"
SLEEP_REASON_MANUAL = "manual_stop"
SLEEP_REASON_ABUSE  = "resource_abuse"


class DockerManager:
    def __init__(self, database):
        self.db                 = database
        self.monitoring_threads = {}
        self.notify_callback    = None
        self._lock              = threading.Lock()
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR,     exist_ok=True)
        self._pids = self._load_pids()

    def _load_pids(self):
        try:
            if os.path.exists(PIDS_FILE):
                with open(PIDS_FILE) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_pids(self):
        try:
            with open(PIDS_FILE, "w") as f:
                json.dump(self._pids, f)
        except Exception as e:
            print(f"[PID Save] {e}")

    def _notify(self, user_id, text):
        if self.notify_callback:
            try:
                self.notify_callback(user_id, text)
            except Exception as e:
                print(f"[Notify] {e}")

    def _is_running(self, pid):
        try:
            p = psutil.Process(pid)
            return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
        except Exception:
            return False

    def _find_main(self, path):
        for name in ["bot.py", "main.py", "app.py", "run.py", "index.py", "start.py"]:
            f = os.path.join(path, name)
            if os.path.exists(f):
                return f
        for fname in os.listdir(path):
            if fname.endswith(".py"):
                return os.path.join(path, fname)
        return None

    def _build_env(self, info):
        env = os.environ.copy()
        env.update(info.get("env_vars", {}))
        env_file = os.path.join(info["path"], ".env")
        if os.path.exists(env_file):
            with open(env_file, errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        env[k.strip()] = v.strip()
        return env

    def deploy_project(self, user_id, project_name, project_dir, limits):
        try:
            safe_name    = f"proj_{user_id}_{project_name}_{int(datetime.now().timestamp())}".lower().replace(" ", "_").replace("-", "_")
            project_path = os.path.join(PROJECTS_DIR, safe_name)

            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            shutil.copytree(project_dir, project_path)

            build_logs = []
            req_file   = os.path.join(project_path, "requirements.txt")
            if os.path.exists(req_file):
                result = subprocess.run(
                    ["pip", "install", "-r", req_file, "--quiet", "--no-warn-script-location"],
                    capture_output=True, text=True, timeout=300
                )
                build_logs.append(result.stdout[-1000:] if result.stdout else "")
                if result.returncode != 0:
                    return {"success": False, "error": f"pip install failed:\n{result.stderr[-1500:]}"}

            main_file = self._find_main(project_path)
            if not main_file:
                return {"success": False, "error": "No main Python file found (bot.py / main.py / app.py)"}

            log_path = os.path.join(LOGS_DIR, f"{safe_name}.log")
            info = {
                "pid": None, "path": project_path, "main": main_file,
                "log": log_path, "user_id": user_id,
                "project_name": project_name, "env_vars": {},
            }
            env = self._build_env(info)

            with open(log_path, "w") as log_f:
                proc = subprocess.Popen(
                    ["python3", "-u", main_file],
                    cwd=project_path, stdout=log_f, stderr=log_f,
                    start_new_session=True, env=env,
                )

            info["pid"] = proc.pid
            with self._lock:
                self._pids[safe_name] = info
                self._save_pids()

            return {"success": True, "container_id": safe_name, "build_logs": "\n".join(build_logs)}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "pip install timed out (>5 min)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_container(self, container_id):
        try:
            info = self._pids.get(container_id)
            if info and info.get("pid"):
                pid = info["pid"]
                if self._is_running(pid):
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                    except Exception:
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except Exception:
                            pass
            return True
        except Exception:
            return True

    def start_container(self, container_id):
        try:
            info = self._pids.get(container_id)
            if not info:
                return False
            env      = self._build_env(info)
            log_path = info["log"]
            with open(log_path, "a") as log_f:
                proc = subprocess.Popen(
                    ["python3", "-u", info["main"]],
                    cwd=info["path"], stdout=log_f, stderr=log_f,
                    start_new_session=True, env=env,
                )
            with self._lock:
                self._pids[container_id]["pid"] = proc.pid
                self._save_pids()
            return True
        except Exception as e:
            print(f"[Start] {e}")
            return False

    def restart_container(self, container_id):
        self.stop_container(container_id)
        time.sleep(2)
        return self.start_container(container_id)

    def remove_project(self, container_id):
        try:
            self.stop_container(container_id)
            time.sleep(1)
            with self._lock:
                info = self._pids.pop(container_id, None)
                self._save_pids()
            if info and os.path.exists(info["path"]):
                shutil.rmtree(info["path"], ignore_errors=True)
            log = info.get("log") if info else None
            if log and os.path.exists(log):
                try: os.remove(log)
                except: pass
        except Exception as e:
            print(f"[Remove] {e}")

    def get_container_stats(self, container_id):
        try:
            info = self._pids.get(container_id)
            if not info or not info.get("pid"):
                return None
            if not self._is_running(info["pid"]):
                return None
            p   = psutil.Process(info["pid"])
            cpu = p.cpu_percent(interval=0.1)
            mem = p.memory_info().rss / (1024 * 1024)
            return {"cpu": round(cpu, 2), "memory": round(mem, 2), "status": "running"}
        except Exception:
            return None

    def get_container_logs(self, container_id, lines=100):
        try:
            info = self._pids.get(container_id)
            if not info:
                return "(no logs — project info missing)"
            log_path = info.get("log")
            if not log_path or not os.path.exists(log_path):
                return "(no log file yet)"
            with open(log_path, errors="ignore") as f:
                all_lines = f.readlines()
            result = "".join(all_lines[-lines:])
            return result if result.strip() else "(no output yet — process may still be starting)"
        except Exception as e:
            return f"(could not fetch logs: {e})"

    def exec_in_project(self, container_id, cmd):
        info = self._pids.get(container_id)
        if not info:
            return -1, "", "Project info not found"
        try:
            result = subprocess.run(
                ["sh", "-c", cmd],
                cwd=info["path"], capture_output=True,
                text=True, timeout=30,
            )
            return result.returncode, result.stdout + result.stderr, None
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out (30s)"
        except Exception as e:
            return -1, "", str(e)

    def replace_file_in_project(self, container_id, file_name, file_data: bytes):
        info = self._pids.get(container_id)
        if not info:
            return False, "Project info not found"
        try:
            dest = os.path.join(info["path"], file_name)
            with open(dest, "wb") as f:
                f.write(file_data)
            self.restart_container(container_id)
            return True, None
        except Exception as e:
            return False, str(e)

    def update_env_in_project(self, container_id, env_vars: dict):
        info = self._pids.get(container_id)
        if not info:
            return False, "Project info not found"
        try:
            with self._lock:
                self._pids[container_id]["env_vars"] = env_vars
                self._save_pids()
            env_content = "\n".join(f"{k}={v}" for k, v in env_vars.items()) + "\n"
            env_file    = os.path.join(info["path"], ".env")
            with open(env_file, "w") as f:
                f.write(env_content)
            self.restart_container(container_id)
            return True, None
        except Exception as e:
            return False, str(e)

    def start_monitoring(self, user_id, project_name, limits):
        thread_key = f"{user_id}_{project_name}"
        existing   = self.monitoring_threads.get(thread_key)
        if existing and existing.is_alive():
            return
        self.monitoring_threads.pop(thread_key, None)

        def monitor():
            start_time      = time.time()
            warned_1h       = warned_30min = False

            while True:
                try:
                    projects = self.db.get_user_projects(user_id)
                    project  = next((p for p in projects if p["name"] == project_name), None)

                    if not project or project.get("status") == "stopped":
                        break

                    container_id = project["container_id"]
                    info         = self._pids.get(container_id)

                    if not info or not self._is_running(info.get("pid", 0)):
                        self.db.update_project(project["_id"], {
                            "status": "sleeping",
                            "stop_reason": "Process exited unexpectedly",
                            "sleep_at": datetime.now(),
                        })
                        self._notify(user_id,
                            f"⚠️ <b>Project Crashed!</b>\n\n"
                            f"📦 <b>{project_name}</b> stopped unexpectedly.\n\n"
                            f"Use /projects to restart it."
                        )
                        break

                    stats = self.get_container_stats(container_id)
                    if stats:
                        uptime_hours = (time.time() - start_time) / 3600
                        self.db.update_project(project["_id"], {
                            "usage": {
                                "cpu":    stats["cpu"],
                                "memory": stats["memory"],
                                "uptime": round(uptime_hours, 2),
                            },
                            "status": "running",
                        })

                        if limits.get("auto_stop") and uptime_hours >= limits["auto_stop"]:
                            self.stop_container(container_id)
                            self.db.update_project(project["_id"], {
                                "status": "sleeping",
                                "stop_reason": SLEEP_REASON_AUTO,
                                "sleep_at": datetime.now(),
                            })
                            self.db.record_run_started(user_id)
                            self._notify(user_id,
                                f"😴 <b>Project Put To Sleep</b>\n\n"
                                f"📦 <b>{project_name}</b> slept after 12 hours.\n\n"
                                f"⭐ Upgrade to /premium for 24/7 uptime!"
                            )
                            break

                        if limits.get("auto_stop"):
                            remaining = limits["auto_stop"] - uptime_hours
                            if remaining <= 1.0 and not warned_1h:
                                warned_1h = True
                                self._notify(user_id, f"⏰ <b>{project_name}</b> will sleep in ~1 hour.")
                            elif remaining <= 0.5 and not warned_30min:
                                warned_30min = True
                                self._notify(user_id, f"⏰ <b>{project_name}</b> will sleep in ~30 minutes.")

                    time.sleep(30)

                except Exception as e:
                    print(f"[Monitor] {e}")
                    time.sleep(30)

            self.monitoring_threads.pop(thread_key, None)

        t = threading.Thread(target=monitor, daemon=True, name=f"monitor_{thread_key}")
        t.start()
        self.monitoring_threads[thread_key] = t

    def auto_monitor(self):
        while True:
            try:
                for project in self.db.get_all_running_projects():
                    key      = f"{project['user_id']}_{project['name']}"
                    existing = self.monitoring_threads.get(key)
                    if not existing or not existing.is_alive():
                        self.start_monitoring(project["user_id"], project["name"], project["limits"])
                time.sleep(60)
            except Exception as e:
                print(f"[AutoMonitor] {e}")
                time.sleep(60)

    def cleanup_stopped_containers(self):
        pass
