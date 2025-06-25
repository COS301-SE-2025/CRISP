from django.db import models
from django.utils import timezone
from core.patterns.observer.threat_feed import ThreatFeed

class Indicator(models.Model):
    """
    Model representing an Indicator of Compromise (IoC).
    """
    TYPE_CHOICES = [
        ('ip', 'IP Address'),
        ('domain', 'Domain Name'),
        ('url', 'URL'),
        ('file_hash', 'File Hash'),
        ('email', 'Email Address'),
        ('user_agent', 'User Agent'),
        ('other', 'Other'),
    ]
    
    HASH_TYPE_CHOICES = [
        ('md5', 'MD5'),
        ('sha1', 'SHA-1'),
        ('sha256', 'SHA-256'),
        ('other', 'Other'),
    ]
    
    threat_feed = models.ForeignKey(ThreatFeed, on_delete=models.CASCADE, related_name='indicators')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    value = models.TextField()
    hash_type = models.CharField(max_length=10, choices=HASH_TYPE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    first_seen = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    stix_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    confidence = models.IntegerField(default=50)
    description = models.TextField(blank=True, null=True)
    is_anonymized = models.BooleanField(default=False)

    # Stored only for owner institution
    original_value = models.TextField(null=True, blank=True)  
    
    class Meta:
        db_table = 'indicators'
        indexes = [
            models.Index(fields=['type', 'value']),
            models.Index(fields=['stix_id']),
        ]
        
    def __str__(self):
        return f"{self.get_type_display()}: {self.value}"

    def to_stix(self):
        """Convert to STIX Indicator object"""
        # This will be implemented using the Factory pattern
        pass