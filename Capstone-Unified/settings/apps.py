"""
Django app configurations
"""
import os
import sys
import subprocess
from django.apps import AppConfig


class CrispThreatIntelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings'
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

            # First, kill any existing Celery workers to prevent accumulation
            print("🔄 Cleaning up existing Celery workers...")
            try:
                # Kill any existing celery workers
                subprocess.run([
                    'pkill', '-f', 'celery.*worker'
                ], capture_output=True, timeout=5)

                # Give them a moment to shut down
                import time
                time.sleep(2)

            except subprocess.TimeoutExpired:
                print("⚠️  Timeout killing workers, continuing...")
            except Exception as cleanup_error:
                print(f"⚠️  Error during cleanup: {cleanup_error}")

            # Check if any workers are still running after cleanup
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )

            worker_count = 0
            for line in result.stdout.split('\n'):
                if 'celery -A settings worker' in line and 'python' in line and 'grep' not in line:
                    worker_count += 1

            if worker_count > 0:
                print(f"⚠️  Still found {worker_count} workers after cleanup - they may be persistent")

            # Start fresh workers
            print(f"🔄 Starting 2 fresh Celery workers...")

            for i in range(2):
                subprocess.Popen([
                    sys.executable, '-m', 'celery', '-A', 'settings',
                    'worker', '--loglevel=info', '--detach'
                ])

            print("✅ Celery workers started - threat feed processing ready!")

        except Exception as e:
            print(f"⚠️  Could not manage Celery workers: {e}")
            print("   Threat feed consumption may not work properly")