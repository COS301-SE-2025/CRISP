from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Django app configuration for the unified CRISP core module.
    Integrates user management, threat intelligence, and trust management.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'CRISP Core Platform'
    
    def ready(self):
        """
        Perform initialization when Django starts.
        Import signal handlers and observers.
        """
        # Import signal handlers and observers
        try:
            import core.user_management.signals
            import core.observers.feed_observers
            import core.signals
        except ImportError:
            pass  # Signals are optional during migrations