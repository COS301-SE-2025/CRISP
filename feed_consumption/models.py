from django.db import models
from django.contrib.auth.models import User
import uuid
import json
from django.utils import timezone

class ExternalFeedSource(models.Model):
    """Model for configuring external TAXII 2.1 feed sources"""
    
    class PollInterval(models.TextChoices):
        HOURLY = 'hourly', 'Hourly'
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
    
    class AuthType(models.TextChoices):
        NONE = 'none', 'None'
        BASIC = 'basic', 'Basic Authentication'
        API_KEY = 'api_key', 'API Key'
        JWT = 'jwt', 'JWT Token'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discovery_url = models.URLField(help_text="TAXII 2.1 discovery endpoint URL")
    api_root_url = models.URLField(blank=True, null=True, help_text="TAXII API Root URL (auto-populated from discovery)")
    collection_id = models.CharField(max_length=255, blank=True, null=True, help_text="Selected TAXII collection ID")
    collection_name = models.CharField(max_length=255, blank=True, null=True)
    categories = models.JSONField(default=list, help_text="List of categories like ['malware', 'indicators', 'ttps']")
    poll_interval = models.CharField(max_length=10, choices=PollInterval.choices, default=PollInterval.DAILY)
    auth_type = models.CharField(max_length=10, choices=AuthType.choices, default=AuthType.NONE)
    auth_credentials = models.JSONField(
        default=dict, 
        blank=True,
        null=False,  # Explicitly set not null to match test expectations
        help_text="Authentication credentials in JSON format"
    )
    headers = models.JSONField(default=dict, blank=True, help_text="Additional HTTP headers to include in API requests")
    last_poll_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='feed_sources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_poll_interval_display()})"
    
    @property
    def auth_config(self):
        """Return auth configuration based on auth_type"""
        if self.auth_type == self.AuthType.NONE:
            return None
        return self.auth_credentials
        
    def get_auth_config(self):
        """Return auth configuration with type information included
        
        This method is primarily for compatibility with tests
        """
        if self.auth_type == self.AuthType.NONE:
            return None
            
        config = dict(self.auth_credentials) if self.auth_credentials else {}
        config['type'] = self.auth_type
        return config
    
    def set_collection(self, collection_id, collection_name):
        """Set the active collection ID and name"""
        self.collection_id = collection_id
        self.collection_name = collection_name
        self.save(update_fields=['collection_id', 'collection_name'])
    
    def update_last_poll_time(self):
        """Update the last poll time to now"""
        self.last_poll_time = timezone.now()
        self.save(update_fields=['last_poll_time'])


class FeedConsumptionLog(models.Model):
    """Logs for feed consumption activities"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    # For compatibility with tests
    class ConsumptionStatus(models.TextChoices):
        SUCCESS = 'completed', 'Success'
        PARTIAL = 'partial', 'Partial Success'
        FAILURE = 'failed', 'Failure'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed_source = models.ForeignKey(ExternalFeedSource, on_delete=models.CASCADE, related_name='consumption_logs')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    objects_retrieved = models.IntegerField(default=0)  # Added for test compatibility
    objects_processed = models.IntegerField(default=0)
    objects_added = models.IntegerField(default=0)
    objects_updated = models.IntegerField(default=0)
    objects_failed = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)  # Set automatically on creation
    end_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(default='', blank=True)  # Default to empty string
    execution_time_seconds = models.FloatField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status_display = "Success" if self.status == "completed" else self.get_status_display()
        return f"{self.feed_source.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')} - {status_display}" if self.start_time else f"{self.feed_source.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def start(self):
        """Mark the consumption as started"""
        self.start_time = timezone.now()
        self.status = self.Status.IN_PROGRESS
        self.save(update_fields=['start_time', 'status'])
    
    def complete(self, objects_processed, objects_added, objects_updated, objects_failed=0, details=None):
        """Mark the consumption as completed"""
        self.end_time = timezone.now()
        self.status = self.Status.COMPLETED
        self.objects_processed = objects_processed
        self.objects_added = objects_added
        self.objects_updated = objects_updated
        self.objects_failed = objects_failed
        
        if details:
            self.details = details
        
        if self.start_time:
            self.execution_time_seconds = (self.end_time - self.start_time).total_seconds()
        
        self.save()
    
    def fail(self, error_message):
        """Mark the consumption as failed"""
        self.end_time = timezone.now()
        self.status = self.Status.FAILED
        self.error_message = error_message
        
        if self.start_time:
            self.execution_time_seconds = (self.end_time - self.start_time).total_seconds()
        
        self.save()
        
    def add_error(self, error_message):
        """Add an error message and update status based on processed objects
        
        This is primarily for compatibility with tests
        """
        if self.error_message:
            self.error_message = f"{self.error_message}\n{error_message}"
        else:
            self.error_message = error_message
            
        # Update status based on processed objects
        if self.objects_processed == 0:
            self.status = self.Status.FAILED
        else:
            self.status = 'partial'  # Map to ConsumptionStatus.PARTIAL
            
        self.save(update_fields=['error_message', 'status'])
