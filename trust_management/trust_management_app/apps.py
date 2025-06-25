from django.apps import AppConfig


class TrustManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TrustManagement'
    verbose_name = 'CRISP Trust Management'
    
    def ready(self):
        """Initialize trust management signals and observers"""
        import TrustManagement.signals
        import TrustManagement.observers.trust_observers