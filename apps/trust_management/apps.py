from django.apps import AppConfig


class TrustManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.trust_management'
    verbose_name = 'Trust Management'

    def ready(self):
        # Import signal handlers for trust events
        pass
