from django.apps import AppConfig


class TrustConfig(AppConfig):
    """
    Django application configuration for the CRISP Trust Management system.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_ut.trust'   
    label = 'trust'       
    verbose_name = 'CRISP Trust Management'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        This includes setting up observers and signal handlers.
        """
        # Import signal handlers to ensure they're connected
        try:
            from . import signals
            from .patterns.observer import trust_observers
        except ImportError:
            pass
        
        #Import admin registrations since admin file is named admin_ut.py
        try:
            from . import admin_ut
            print("Trust admin_ut imported successfully")
        except ImportError as e:
            print(f"Failed to import trust admin_ut: {e}")
        except Exception as e:
            print(f"Error importing trust admin_ut: {e}")
            import traceback
            traceback.print_exc()
