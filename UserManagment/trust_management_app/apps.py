from django.apps import AppConfig


class TrustManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trust_management_app'
    verbose_name = 'CRISP Trust Management'
    
    def ready(self):
        """Initialize trust management signals and observers"""
        import trust_management_app.signals
        import trust_management_app.observers.trust_observers