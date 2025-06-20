"""
Django integration utilities for CRISP threat intelligence platform
"""

from django.apps import AppConfig
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import migrations, models
import uuid


class CrispThreatIntelConfig(AppConfig):
    """Django app configuration for CRISP threat intelligence"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crisp_threat_intel'
    verbose_name = 'CRISP Threat Intelligence Platform'
    
    def ready(self):
        """Initialize the app when Django starts"""
        # Import signal handlers
        from .signals import setup_signal_handlers
        setup_signal_handlers()


def setup_signal_handlers():
    """Set up Django signal handlers for the CRISP platform"""
    from django.db.models.signals import post_save, post_delete
    from django.dispatch import receiver
    from ..domain.models import ThreatFeed, Indicator, TTPData
    
    @receiver(post_save, sender=Indicator)
    def indicator_saved_handler(sender, instance, created, **kwargs):
        """Handle indicator save events"""
        if created:
            # Notify threat feed observers
            instance.threat_feed.notify_observers('indicator_added', {
                'indicator_id': str(instance.id),
                'indicator_name': instance.name
            })
    
    @receiver(post_save, sender=TTPData)
    def ttp_saved_handler(sender, instance, created, **kwargs):
        """Handle TTP save events"""
        if created:
            # Notify threat feed observers
            instance.threat_feed.notify_observers('ttp_added', {
                'ttp_id': str(instance.id),
                'ttp_name': instance.name
            })
    
    @receiver(post_delete, sender=Indicator)
    def indicator_deleted_handler(sender, instance, **kwargs):
        """Handle indicator deletion events"""
        # This could trigger cleanup or notification logic
        pass
    
    @receiver(post_delete, sender=TTPData)
    def ttp_deleted_handler(sender, instance, **kwargs):
        """Handle TTP deletion events"""
        # This could trigger cleanup or notification logic
        pass


class CreateCrispTablesCommand(BaseCommand):
    """Django management command to create CRISP database tables"""
    
    help = 'Create database tables for CRISP threat intelligence platform'
    
    def handle(self, *args, **options):
        """Handle the command execution"""
        from django.core.management import call_command
        
        self.stdout.write(self.style.SUCCESS('Creating CRISP database tables...'))
        
        try:
            # Run migrations
            call_command('makemigrations', 'crisp_threat_intel')
            call_command('migrate')
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created CRISP database tables')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create tables: {e}')
            )


class Migration(migrations.Migration):
    """Base migration for CRISP threat intelligence models"""
    
    initial = True
    
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]
    
    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('identity_class', models.CharField(default='organization', max_length=100)),
                ('sectors', models.JSONField(blank=True, default=list, null=True)),
                ('contact_email', models.EmailField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('stix_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='created_institutions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('admin', 'Administrator'), ('analyst', 'Threat Analyst'), ('contributor', 'Contributor'), ('viewer', 'Viewer')], default='viewer', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('django_user', models.OneToOneField(on_delete=models.CASCADE, related_name='crisp_user', to=settings.AUTH_USER_MODEL)),
                ('institution', models.ForeignKey(on_delete=models.CASCADE, related_name='users', to='crisp_threat_intel.institution')),
            ],
            options={
                'ordering': ['django_user__username'],
            },
        ),
        migrations.CreateModel(
            name='ThreatFeed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('query_parameters', models.JSONField(default=dict)),
                ('update_interval', models.IntegerField(default=3600)),
                ('status', models.CharField(choices=[('active', 'Active'), ('paused', 'Paused'), ('error', 'Error')], default='active', max_length=20)),
                ('last_published_time', models.DateTimeField(blank=True, null=True)),
                ('next_publish_time', models.DateTimeField(blank=True, null=True)),
                ('publish_count', models.IntegerField(default=0)),
                ('error_count', models.IntegerField(default=0)),
                ('last_bundle_id', models.CharField(blank=True, max_length=255, null=True)),
                ('last_error', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=models.SET_NULL, related_name='created_threat_feeds', to='crisp_threat_intel.user')),
                ('institution', models.ForeignKey(on_delete=models.CASCADE, related_name='threat_feeds', to='crisp_threat_intel.institution')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        # Add more model definitions here...
    ]


def get_crisp_settings():
    """Get CRISP-specific Django settings"""
    return getattr(settings, 'CRISP_SETTINGS', {
        'DEFAULT_TRUST_LEVEL': 0.5,
        'DEFAULT_ANONYMIZATION_STRATEGY': 'partial',
        'ENABLE_AUDIT_LOGGING': True,
        'MAX_FEED_UPDATE_INTERVAL': 86400,  # 24 hours
        'MIN_FEED_UPDATE_INTERVAL': 300,    # 5 minutes
        'DEFAULT_CONFIDENCE_THRESHOLD': 50,
        'ENABLE_OBSERVER_NOTIFICATIONS': True,
        'STIX_VERSION': '2.1',
        'TAXII_VERSION': '2.1'
    })


def validate_crisp_settings():
    """Validate CRISP Django settings"""
    crisp_settings = get_crisp_settings()
    errors = []
    
    # Validate trust level
    default_trust = crisp_settings.get('DEFAULT_TRUST_LEVEL', 0.5)
    if not isinstance(default_trust, (int, float)) or not 0.0 <= default_trust <= 1.0:
        errors.append("DEFAULT_TRUST_LEVEL must be a number between 0.0 and 1.0")
    
    # Validate update intervals
    max_interval = crisp_settings.get('MAX_FEED_UPDATE_INTERVAL', 86400)
    min_interval = crisp_settings.get('MIN_FEED_UPDATE_INTERVAL', 300)
    
    if not isinstance(max_interval, int) or max_interval <= 0:
        errors.append("MAX_FEED_UPDATE_INTERVAL must be a positive integer")
    
    if not isinstance(min_interval, int) or min_interval <= 0:
        errors.append("MIN_FEED_UPDATE_INTERVAL must be a positive integer")
    
    if min_interval >= max_interval:
        errors.append("MIN_FEED_UPDATE_INTERVAL must be less than MAX_FEED_UPDATE_INTERVAL")
    
    # Validate confidence threshold
    confidence_threshold = crisp_settings.get('DEFAULT_CONFIDENCE_THRESHOLD', 50)
    if not isinstance(confidence_threshold, int) or not 0 <= confidence_threshold <= 100:
        errors.append("DEFAULT_CONFIDENCE_THRESHOLD must be an integer between 0 and 100")
    
    return errors


def setup_crisp_middleware():
    """Set up CRISP-specific Django middleware"""
    from django.utils.deprecation import MiddlewareMixin
    
    class CrispAuditMiddleware(MiddlewareMixin):
        """Middleware for auditing CRISP operations"""
        
        def process_request(self, request):
            """Process incoming request"""
            # Add request ID for tracking
            request.crisp_request_id = str(uuid.uuid4())
            return None
        
        def process_response(self, request, response):
            """Process outgoing response"""
            # Log API calls if enabled
            crisp_settings = get_crisp_settings()
            if crisp_settings.get('ENABLE_AUDIT_LOGGING', True):
                self._log_api_call(request, response)
            
            return response
        
        def _log_api_call(self, request, response):
            """Log API call for audit purposes"""
            # This would integrate with the audit logging system
            pass
    
    return CrispAuditMiddleware


def get_crisp_admin_config():
    """Get Django admin configuration for CRISP models"""
    from django.contrib import admin
    
    class CrispAdminConfig:
        """Admin configuration for CRISP models"""
        
        @staticmethod
        def register_models():
            """Register CRISP models with Django admin"""
            from ..domain.models import Institution, User, ThreatFeed, Indicator, TTPData
            
            @admin.register(Institution)
            class InstitutionAdmin(admin.ModelAdmin):
                list_display = ['name', 'sectors', 'contact_email', 'created_at']
                list_filter = ['sectors', 'created_at']
                search_fields = ['name', 'description', 'contact_email']
                readonly_fields = ['id', 'created_at', 'updated_at']
            
            @admin.register(ThreatFeed)
            class ThreatFeedAdmin(admin.ModelAdmin):
                list_display = ['name', 'institution', 'status', 'publish_count', 'error_count', 'created_at']
                list_filter = ['status', 'institution', 'created_at']
                search_fields = ['name', 'description']
                readonly_fields = ['id', 'created_at', 'updated_at', 'publish_count', 'error_count']
            
            @admin.register(Indicator)
            class IndicatorAdmin(admin.ModelAdmin):
                list_display = ['name', 'threat_feed', 'confidence', 'revoked', 'created']
                list_filter = ['threat_feed', 'labels', 'confidence', 'revoked', 'created']
                search_fields = ['name', 'description', 'pattern']
                readonly_fields = ['id', 'stix_id', 'created_at', 'updated_at']
            
            @admin.register(TTPData)
            class TTPDataAdmin(admin.ModelAdmin):
                list_display = ['name', 'threat_feed', 'x_mitre_tactics', 'created']
                list_filter = ['threat_feed', 'x_mitre_tactics', 'x_mitre_platforms', 'created']
                search_fields = ['name', 'description']
                readonly_fields = ['id', 'stix_id', 'created_at', 'updated_at']
    
    return CrispAdminConfig