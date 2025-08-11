from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    """
    Django application configuration for CRISP User Management system.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_ut.user_management' 
    label = 'ut_user_management'   
    verbose_name = 'CRISP User Management'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        """
        try:
            from . import signals
        except ImportError:
            pass
        
        try:
            from . import admin_ut
            print("User Management admin_ut imported successfully")
        except ImportError as e:
            print(f"Failed to import user_management admin_ut: {e}")
        except Exception as e:
            print(f"Error importing user_management admin_ut: {e}")
            import traceback
            traceback.print_exc()