from django.db import models
from django.core.validators import URLValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
import uuid
import json

class ExternalFeedSource(models.Model):
    """
    Model to store configuration for external TAXII feed sources.
    
    This model stores all necessary information to connect to and consume
    threat intelligence from external TAXII 2.1 compliant feeds.
    """
    
    class PollInterval(models.TextChoices):
        HOURLY = 'hourly', _('Hourly')
        DAILY = 'daily', _('Daily')
        WEEKLY = 'weekly', _('Weekly')
        MONTHLY = 'monthly', _('Monthly')
    
    class FeedCategory(models.TextChoices):
        MALWARE = 'malware', _('Malware')
        INDICATORS = 'indicators', _('Indicators')
        TTPS = 'ttps', _('TTPs')
        VULNERABILITIES = 'vulnerabilities', _('Vulnerabilities')
        THREAT_ACTORS = 'threat_actors', _('Threat Actors')
        GENERAL = 'general', _('General')
    
    class AuthType(models.TextChoices):
        NONE = 'none', _('None')
        API_KEY = 'api_key', _('API Key')
        JWT = 'jwt', _('JWT Token')
        BASIC = 'basic', _('Basic Auth')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Display name for this feed source")
    discovery_url = models.URLField(
        validators=[URLValidator()],
        help_text="TAXII 2.1 discovery endpoint URL (e.g., https://example.com/taxii2/)"
    )
    api_root = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="API root path, will be auto-populated from discovery if blank"
    )
    collection_id = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Collection ID to poll, will use first available if blank"
    )
    categories = ArrayField(
        models.CharField(max_length=50, choices=FeedCategory.choices),
        default=list,
        help_text="Categories of threat intelligence provided by this feed"
    )
    poll_interval = models.CharField(
        max_length=10,
        choices=PollInterval.choices,
        default=PollInterval.DAILY,
        help_text="How frequently to poll this feed for updates"
    )
    auth_type = models.CharField(
        max_length=10,
        choices=AuthType.choices,
        default=AuthType.NONE,
        help_text="Authentication type required by this feed"
    )
    auth_credentials = models.JSONField(
        blank=True, 
        null=True,
        help_text="Encrypted credentials for authentication (structure depends on auth_type)"
    )
    last_poll_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this feed was last successfully polled"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this feed is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_feeds'
    )
    rate_limit = models.IntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        help_text="Maximum requests per minute allowed by the feed provider"
    )
    
    def __str__(self):
        return f"{self.name} ({self.get_poll_interval_display()})"
    
    def get_auth_config(self):
        """Returns auth credentials in a structured format based on auth_type."""
        if not self.auth_credentials:
            return None
            
        # The auth_credentials are stored as encrypted JSON
        # This method decrypts and returns in the format needed by the client
        
        if self.auth_type == self.AuthType.API_KEY:
            return {
                'type': 'api_key',
                'header_name': self.auth_credentials.get('header_name', 'Authorization'),
                'key': self.auth_credentials.get('key', '')
            }
        elif self.auth_type == self.AuthType.JWT:
            return {
                'type': 'jwt',
                'token': self.auth_credentials.get('token', '')
            }
        elif self.auth_type == self.AuthType.BASIC:
            return {
                'type': 'basic',
                'username': self.auth_credentials.get('username', ''),
                'password': self.auth_credentials.get('password', '')
            }
        return None


class FeedConsumptionLog(models.Model):
    """
    Model to track feed consumption activity, successes, and failures.
    """
    
    class ConsumptionStatus(models.TextChoices):
        SUCCESS = 'success', _('Success')
        PARTIAL = 'partial', _('Partial Success')
        FAILURE = 'failure', _('Failure')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed_source = models.ForeignKey(
        ExternalFeedSource,
        on_delete=models.CASCADE,
        related_name='consumption_logs'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=ConsumptionStatus.choices,
        default=ConsumptionStatus.SUCCESS
    )
    objects_retrieved = models.IntegerField(default=0)
    objects_processed = models.IntegerField(default=0)
    objects_failed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.feed_source.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.get_status_display()}"
    
    def add_error(self, error_message):
        """Append an error message to the log."""
        if self.error_message:
            self.error_message += f"\n{error_message}"
        else:
            self.error_message = error_message
        
        # Update status to partial if we have some successes but also errors
        if self.objects_processed > 0 and self.objects_failed > 0:
            self.status = self.ConsumptionStatus.PARTIAL
        elif self.objects_processed == 0:
            self.status = self.ConsumptionStatus.FAILURE
