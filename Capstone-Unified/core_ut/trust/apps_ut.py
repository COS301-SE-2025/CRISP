from django.apps import AppConfig


class TrustConfig(AppConfig):
    """
    Django application configuration for the CRISP Trust Management system.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.trust'
    verbose_name = 'CRISP Trust Management'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        This includes setting up observers and signal handlers.
        """
        # Import signal handlers to ensure they're connected
        try:
            from . import signals
            from .observers import trust_observers
        except ImportError:
            pass