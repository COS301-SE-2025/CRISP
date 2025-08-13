from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_ut.user_management'
    verbose_name = 'User Management'
    
    def ready(self):
        """Initialize app when Django starts"""
        # Import admin to ensure models are registered
        try:
            from . import admin_ut
        except ImportError:
            pass
            
        # Import signals
        try:
            import core_ut.user_management.signals
        except ImportError:
            pass