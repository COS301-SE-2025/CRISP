from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.user_management'
    verbose_name = 'User Management'
    
    def ready(self):
        """Initialize app when Django starts"""
        import core_ut.user_management.signals