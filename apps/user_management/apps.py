from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user_management'
    verbose_name = 'User Management'

    def ready(self):
        # Import signal handlers
        pass
