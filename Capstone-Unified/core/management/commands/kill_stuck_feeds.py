#!/usr/bin/env python
"""
Kill any stuck or long-running feed consumption processes
"""

import logging
import psutil
import os
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Kill stuck feed consumption processes'

    def handle(self, *args, **options):
        self.stdout.write("Looking for stuck feed consumption processes...")

        current_pid = os.getpid()
        django_processes = []

        # Find Django processes that might be stuck
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['pid'] == current_pid:
                    continue

                cmdline = ' '.join(proc.info['cmdline'] or [])

                # Look for Django processes that might be consuming feeds
                if ('runserver' in cmdline or 'django' in cmdline.lower()) and proc.info['pid'] != current_pid:
                    # Check if process has been running for more than 30 minutes
                    import time
                    uptime = time.time() - proc.info['create_time']
                    if uptime > 1800:  # 30 minutes
                        django_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline,
                            'uptime': uptime
                        })

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not django_processes:
            self.stdout.write("No long-running Django processes found.")
            return

        for proc_info in django_processes:
            uptime_minutes = proc_info['uptime'] / 60
            self.stdout.write(f"Found long-running process:")
            self.stdout.write(f"  PID: {proc_info['pid']}")
            self.stdout.write(f"  Uptime: {uptime_minutes:.1f} minutes")
            self.stdout.write(f"  Command: {proc_info['cmdline'][:100]}...")

            try:
                proc = psutil.Process(proc_info['pid'])
                proc.terminate()
                self.stdout.write(f"  ✅ Terminated process {proc_info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.stdout.write(f"  ❌ Could not terminate process {proc_info['pid']}: {e}")

        self.stdout.write("\nRecommendation: Restart the Docker containers to ensure clean state:")
        self.stdout.write("  docker-compose restart")