from django.apps import AppConfig


class AlertsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.alerts'
    verbose_name = 'CRISP Alert Management'
    
    def ready(self):
        """Import signal handlers when app is ready"""
        try:
            # Import the feed notification observer to register signals
            from core.services import feed_notification_observer
            print("✅ Feed notification observer loaded successfully")
        except ImportError as e:
            print(f"❌ Failed to load feed notification observer: {e}")