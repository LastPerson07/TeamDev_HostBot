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
import time
import threading
from datetime import datetime, timedelta

SLEEP_REASON_AUTO   = "auto_stop_12h"
SLEEP_REASON_MANUAL = "manual_stop"
SLEEP_REASON_ABUSE  = "resource_abuse"

class DockerManager:
    def __init__(self, database):
        self.client = docker.from_env()
        self.db = database
        self.monitoring_threads = {}
        self.notify_callback = None

    def _notify(self, user_id, message_text):
        if self.notify_callback:
            try:
                self.notify_callback(user_id, message_text)
            except Exception as e:
                print(f"[Notify] Error notifying {user_id}: {e}")

    def deploy_project(self, user_id, project_name, project_dir, limits):
        try:
            dockerfile_path = None
            for root, dirs, files in os.walk(project_dir):
                if 'Dockerfile' in files:
                    dockerfile_path = root
                    break

            if not dockerfile_path:
                return {'success': False, 'error': 'Dockerfile not found in the uploaded files'}

            image_tag = f"user_{user_id}_{project_name}".lower().replace(' ', '_').replace('-', '_')
            print(f"[Deploy] Building image: {image_tag}")

            image, build_logs = self.client.images.build(
                path=dockerfile_path, tag=image_tag, rm=True, nocache=False
            )

            build_output = []
            for log in build_logs:
                if 'stream' in log:
                    build_output.append(log['stream'].strip())

            container = self.client.containers.run(
                image_tag,
                detach=True,
                name=f"{image_tag}_{int(time.time())}",
                cpu_quota=int(limits['cpu_cores'] * 100000),
                mem_limit=f"{limits['memory']}m",
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 5} if limits['restart_on_crash'] else None,
                network_mode='bridge',
                labels={
                    'user_id': str(user_id),
                    'project_name': project_name,
                    'tier': limits['tier']
                }
            )

            return {
                'success': True,
                'container_id': container.id,
                'image_tag': image_tag,
                'build_logs': '\n'.join(build_output[-20:])
            }

        except docker.errors.BuildError as e:
            error_msg = str(e)
            if hasattr(e, 'build_log'):
                error_lines = []
                for log in e.build_log:
                    if 'error' in str(log).lower():
                        error_lines.append(str(log))
                if error_lines:
                    error_msg = '\n'.join(error_lines[-3:])
            return {'success': False, 'error': f"Build failed: {error_msg}"}
        except docker.errors.APIError as e:
            return {'success': False, 'error': f"Docker API error: {str(e)}"}
        except Exception as e:
            return {'success': False, 'error': f"Deployment error: {str(e)}"}

    def stop_container(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
            return True
        except:
            return False

    def start_container(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            container.start()
            return True
        except:
            return False

    def restart_container(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=10)
            return True
        except:
            return False

    def remove_project(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            image_tag = container.image.tags[0] if container.image.tags else None
            try:
                container.stop(timeout=10)
            except:
                pass
            container.remove(force=True)
            if image_tag:
                try:
                    self.client.images.remove(image_tag, force=True)
                except:
                    pass
            return True
        except:
            return False

    def get_container_stats(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)

            cpu_delta    = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                           stats['precpu_stats']['system_cpu_usage']
            cpu_percent  = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0
            memory_usage = stats['memory_stats'].get('usage', 0) / (1024 * 1024)

            return {
                'cpu': round(cpu_percent, 2),
                'memory': round(memory_usage, 2),
                'status': container.status
            }
        except:
            return None

    def get_container_logs(self, container_id, lines=100):
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(
                tail=lines,
                stdout=True,
                stderr=True,
                timestamps=False
            ).decode('utf-8', errors='ignore')
            return logs if logs.strip() else '(no output yet — container may still be starting)'
        except docker.errors.NotFound:
            return '(container not found — it may have been removed)'
        except Exception as e:
            return f'(could not fetch logs: {str(e)})'  

    def start_monitoring(self, user_id, project_name, limits):
        thread_key = f"{user_id}_{project_name}"
        if thread_key in self.monitoring_threads:
            t = self.monitoring_threads[thread_key]
            if t.is_alive():
                return
        self.monitoring_threads.pop(thread_key, None)

        def monitor():
            start_time   = time.time()
            warned_1h       = False
            warned_30min    = False
            warned_high     = False
            warned_critical = False

            while True:
                try:

                    projects = self.db.get_user_projects(user_id)
                    project  = next((p for p in projects if p['name'] == project_name), None)

                    if not project:
                        print(f"[Monitor] Project {project_name} deleted, stopping monitor.")
                        break

                    if project.get('status') == 'stopped':
                        break

                    container_id = project['container_id']

                    try:
                        container = self.client.containers.get(container_id)
                        if container.status not in ('running',):
                            self.db.update_project(project['_id'], {
                                'status': 'sleeping',
                                'stop_reason': 'Container exited unexpectedly',
                                'sleep_at': datetime.now()
                            })
                            self._notify(user_id,
                                f"⚠️ <b>Project Crashed!</b>\n\n"
                                f"📦 <b>{project_name}</b> has stopped unexpectedly.\n\n"
                                f"Use /projects to restart it."
                            )
                            break
                    except docker.errors.NotFound:
                        self.db.update_project(project['_id'], {
                            'status': 'sleeping',
                            'stop_reason': 'Container not found',
                            'sleep_at': datetime.now()
                        })
                        break

                    stats = self.get_container_stats(container_id)
                    if stats:
                        uptime_hours = (time.time() - start_time) / 3600
                        self.db.update_project(project['_id'], {
                            'usage': {
                                'cpu': stats['cpu'],
                                'memory': stats['memory'],
                                'uptime': round(uptime_hours, 2)
                            },
                            'status': 'running'
                        })

                        if limits.get('auto_stop') and uptime_hours >= limits['auto_stop']:
                            self.stop_container(container_id)
                            self.db.update_project(project['_id'], {
                                'status': 'sleeping',
                                'stop_reason': SLEEP_REASON_AUTO,
                                'sleep_at': datetime.now()
                            })
                            self.db.record_run_started(user_id)
                            self._notify(user_id,
                                f"😴 <b>Project Put To Sleep</b>\n\n"
                                f"📦 <b>{project_name}</b> has been sleeping after <b>12 hours</b> of runtime.\n\n"
                                f"🆓 <b>Free tier limit reached.</b>\n\n"
                                f"▶️ You can <b>wake it up</b> anytime from /projects\n"
                                f"⏳ Or wait for your 2-day cycle to reset for a fresh 12h run.\n\n"
                                f"⭐ Upgrade to /premium for <b>24/7 uptime</b> with no sleep!"
                            )
                            break

                        if limits.get('auto_stop'):
                            remaining_hours = limits['auto_stop'] - uptime_hours
                            if remaining_hours <= 1.0 and not warned_1h:
                                warned_1h = True
                                self._notify(user_id,
                                    f"⏰ <b>Sleep Warning — 1 Hour Left</b>\n\n"
                                    f"📦 <b>{project_name}</b> will go to sleep in ~<b>1 hour</b>.\n\n"
                                    f"⭐ /premium for 24/7 uptime!"
                                )
                            elif remaining_hours <= 0.5 and not warned_30min:
                                warned_30min = True
                                self._notify(user_id,
                                    f"⏰ <b>Sleep Warning — 30 Minutes Left</b>\n\n"
                                    f"📦 <b>{project_name}</b> will sleep in ~<b>30 minutes</b>.\n\n"
                                    f"⭐ /premium for 24/7 uptime!"
                                )

                        if stats['cpu'] > 85 and not warned_high:
                            warned_high = True
                            self._notify(user_id,
                                f"⚠️ <b>High CPU Usage!</b>\n\n"
                                f"📦 <b>{project_name}</b> is using <b>{stats['cpu']}% CPU</b>.\n\n"
                                f"If this continues, the project may be stopped automatically."
                            )

                        if stats['cpu'] > 92 and not warned_critical:
                            warned_critical = True
                            user = self.db.get_user(user_id)
                            warnings_so_far = user.get('warnings', 0) if user else 0
                            self._notify(user_id,
                                f"🚨 <b>CRITICAL — Project About To Be Killed!</b>\n\n"
                                f"📦 <b>{project_name}</b> is using <b>{stats['cpu']}% CPU</b>.\n\n"
                                f"⛔ If usage doesn't drop immediately, your project will be <b>force stopped</b> "
                                f"and a warning will be added to your account.\n\n"
                                f"⚠️ Current warnings: <b>{warnings_so_far}/3</b> — 3 warnings = permanent ban.\n\n"
                                f"💡 Optimize your code or upgrade to /premium for higher limits."
                            )

                        if stats['cpu'] > 95 or stats['memory'] > limits['memory']:
                            self.stop_container(container_id)
                            self.db.update_project(project['_id'], {
                                'status': 'sleeping',
                                'stop_reason': SLEEP_REASON_ABUSE
                            })
                            self.db.add_warning(user_id, "Project killed: extreme resource usage")
                            user = self.db.get_user(user_id)
                            total_warnings = user.get('warnings', 0) if user else 0
                            if total_warnings >= 3:
                                warn_msg = "🚫 <b>Project Killed — You Have Been Banned!</b>\n\n"
                            elif total_warnings == 2:
                                warn_msg = "🚫 <b>Project Killed — 1 More Warning = Permanent Ban!</b>\n\n"
                            else:
                                warn_msg = "🚫 <b>Project Killed — Resource Abuse</b>\n\n"
                            self._notify(user_id,
                                f"{warn_msg}"
                                f"📦 <b>{project_name}</b> was stopped for extreme resource usage.\n"
                                f"CPU: {stats['cpu']}% | RAM: {stats['memory']}MB\n\n"
                                f"⚠️ Warnings: <b>{total_warnings}/3</b> — 3 warnings = permanent ban.\n\n"
                                f"💡 Optimize your code or upgrade to /premium for higher limits."
                            )
                            break

                    time.sleep(30)

                except Exception as e:
                    print(f"[Monitor] Error: {e}")
                    time.sleep(30)

            self.monitoring_threads.pop(thread_key, None)

        thread = threading.Thread(target=monitor, daemon=True, name=f"monitor_{thread_key}")
        thread.start()
        self.monitoring_threads[thread_key] = thread

    def auto_monitor(self):
        while True:
            try:
                running_projects = self.db.get_all_running_projects()
                for project in running_projects:
                    thread_key = f"{project['user_id']}_{project['name']}"
                    existing   = self.monitoring_threads.get(thread_key)
                    if not existing or not existing.is_alive():
                        self.start_monitoring(project['user_id'], project['name'], project['limits'])
                time.sleep(60)
            except Exception as e:
                print(f"[AutoMonitor] Error: {e}")
                time.sleep(60)

    def cleanup_stopped_containers(self):
        try:
            containers = self.client.containers.list(all=True, filters={'status': 'exited'})
            for container in containers:
                if 'user_id' in container.labels:
                    container.remove()
        except:
            pass
