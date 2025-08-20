"""
Django app configurations
"""
from django.apps import AppConfig


class CrispThreatIntelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crisp_threat_intel'
    verbose_name = 'CRISP Threat Intelligence Platform'
    
    def ready(self):
        """
        Initialize app when Django starts.
        Connect Observer pattern signals.
        """
        # Import and connect observer signals
        try:
            from core.patterns.observer.feed_observers import connect_feed_signals
            connect_feed_signals()
        except ImportError:
            pass