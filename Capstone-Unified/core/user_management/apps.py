from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.user_management'
    label = 'user_management'  # This sets the app label for model references
    verbose_name = 'CRISP User Management'