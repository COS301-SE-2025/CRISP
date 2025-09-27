"""
Django app configurations
"""
import os
import sys
import subprocess
from django.apps import AppConfig


class CrispThreatIntelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crisp_threat_intel'
    verbose_name = 'CRISP Threat Intelligence Platform'

    def ready(self):
        """
        Initialize app when Django starts.
        Connect Observer pattern signals and ensure Celery workers are running.
        """
        # Import and connect observer signals
        try:
            from core.patterns.observer.feed_observers import connect_feed_signals
            connect_feed_signals()
        except ImportError:
            pass

        # Auto-start Celery workers when Django server starts
        self._ensure_celery_workers()

    def _ensure_celery_workers(self):
        """Ensure Celery workers are running when Django starts"""
        try:
            # Only start workers when running the development server (not migrations, etc.)
            if 'runserver' not in sys.argv:
                return

            # Check if workers are already running
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )

            worker_count = 0
            for line in result.stdout.split('\n'):
                if 'celery -A settings worker' in line and 'python' in line:
                    worker_count += 1

            # Start workers if needed
            if worker_count < 2:
                print(f"🔄 Starting Celery workers (found {worker_count}, need 2)...")

                for i in range(2):
                    subprocess.Popen([
                        sys.executable, '-m', 'celery', '-A', 'settings',
                        'worker', '--loglevel=info', '--detach'
                    ])

                print("✅ Celery workers started - threat feed processing ready!")
            else:
                print(f"✅ Found {worker_count} Celery workers running")

        except Exception as e:
            print(f"⚠️  Could not start Celery workers: {e}")
            print("   Threat feed consumption may not work properly")