import uuid
from django.db import models
from django.contrib.auth.models import User
from core.models import Organization

class AuditLog(models.Model):
    """
    Audit log for tracking all intelligence sharing activities.
    """
    ACTION_TYPES = (
        # TAXII API actions
        ('discovery', 'Discovery'),
        ('api_root', 'API Root'),
        ('list_collections', 'List Collections'),
        ('get_collection', 'Get Collection'),
        ('get_collection_objects', 'Get Collection Objects'),
        ('add_collection_objects', 'Add Collection Objects'),
        ('get_object', 'Get Object'),
        ('get_manifest', 'Get Manifest'),
        
        # Intelligence management actions
        ('create_stix_object', 'Create STIX Object'),
        ('update_stix_object', 'Update STIX Object'),
        ('delete_stix_object', 'Delete STIX Object'),
        ('anonymize_object', 'Anonymize Object'),
        
        # Collection management actions
        ('create_collection', 'Create Collection'),
        ('update_collection', 'Update Collection'),
        ('delete_collection', 'Delete Collection'),
        
        # Trust management actions
        ('create_trust_relationship', 'Create Trust Relationship'),
        ('update_trust_relationship', 'Update Trust Relationship'),
        ('delete_trust_relationship', 'Delete Trust Relationship'),
        
        # Feed management actions
        ('create_feed', 'Create Feed'),
        ('update_feed', 'Update Feed'),
        ('delete_feed', 'Delete Feed'),
        ('publish_feed', 'Publish Feed'),
        
        # User actions
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('password_change', 'Password Change'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    object_id = models.CharField(max_length=255, blank=True, null=True)  # ID of affected object
    details = models.JSONField(default=dict)  # Additional details
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['organization']),
            models.Index(fields=['action_type']),
            models.Index(fields=['object_id']),
        ]
        
    def __str__(self):
        return f"{self.timestamp} - {self.action_type} by {self.user}"


class SharingActivityLog(models.Model):
    """
    Detailed log of intelligence sharing activities between organizations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    audit_log = models.ForeignKey(AuditLog, on_delete=models.CASCADE, related_name='sharing_details')
    source_organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, related_name='shared_from')
    target_organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, related_name='shared_to')
    stix_object_id = models.CharField(max_length=255)
    stix_object_type = models.CharField(max_length=50)
    collection_id = models.UUIDField()
    anonymization_applied = models.BooleanField(default=False)
    anonymization_strategy = models.CharField(max_length=50, blank=True, null=True)
    trust_level = models.FloatField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['source_organization']),
            models.Index(fields=['target_organization']),
            models.Index(fields=['stix_object_id']),
            models.Index(fields=['stix_object_type']),
            models.Index(fields=['collection_id']),
        ]
        
    def __str__(self):
        return f"{self.timestamp} - {self.source_organization} shared {self.stix_object_type} with {self.target_organization}"