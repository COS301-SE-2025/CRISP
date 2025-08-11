from django.apps import AppConfig


class AlertsConfig(AppConfig):
    """
    Django application configuration for CRISP Alerts system.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_ut.alerts' 
    label = 'alerts'         
    verbose_name = 'CRISP Alerts'
    
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
            print("Alerts admin_ut imported successfully")
        except ImportError:
            print("Alerts admin_ut.py not found (this is OK - alerts may not need admin)")
        except Exception as e:
            print(f"Error importing alerts admin_ut: {e}")
