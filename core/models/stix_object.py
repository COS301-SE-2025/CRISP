from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json
from django.utils import timezone

# Import Organization model directly to avoid circular import
# Organization will be imported at runtime

# Get the custom user model
User = get_user_model()


class STIXObject(models.Model):
    """
    Base model for STIX objects with complete STIX 2.1 compliance.
    Integrated from crisp_threat_intel into core for unified threat intelligence handling.
    """
    TYPE_CHOICES = (
        ('indicator', 'Indicator'),
        ('malware', 'Malware'),
        ('attack-pattern', 'Attack Pattern'),
        ('threat-actor', 'Threat Actor'),
        ('identity', 'Identity'),
        ('relationship', 'Relationship'),
        ('tool', 'Tool'),
        ('vulnerability', 'Vulnerability'),
        ('observed-data', 'Observed Data'),
        ('report', 'Report'),
        ('course-of-action', 'Course of Action'),
        ('campaign', 'Campaign'),
        ('intrusion-set', 'Intrusion Set'),
        ('infrastructure', 'Infrastructure'),
        ('location', 'Location'),
        ('note', 'Note'),
        ('opinion', 'Opinion'),
        ('marking-definition', 'Marking Definition'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stix_id = models.CharField(max_length=255, unique=True)
    stix_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    spec_version = models.CharField(max_length=20, default="2.1")
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_by_ref = models.CharField(max_length=255, blank=True, null=True)
    revoked = models.BooleanField(default=False)
    labels = models.JSONField(default=list)
    confidence = models.IntegerField(default=0)
    external_references = models.JSONField(default=list)
    object_marking_refs = models.JSONField(default=list)
    granular_markings = models.JSONField(default=list)
    raw_data = models.JSONField()  # Complete raw STIX object storage
    
    # System metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_stix_objects')
    source_organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='stix_objects')
    
    # Anonymization support
    anonymized = models.BooleanField(default=False)
    anonymization_strategy = models.CharField(max_length=50, blank=True, null=True)
    original_object_ref = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.stix_type}: {self.stix_id}"
    
    def save(self, *args, **kwargs):
        if not self.stix_id:
            self.stix_id = f"{self.stix_type}--{str(uuid.uuid4())}"
        # Set created/modified timestamps if not provided
        if not self.created:
            self.created = timezone.now()
        self.modified = timezone.now()
        super().save(*args, **kwargs)
    
    def to_stix(self):
        """
        Convert database record back to STIX dictionary.
        """
        return self.raw_data
    
    def to_json(self):
        """
        Return STIX object as JSON string.
        """
        return json.dumps(self.raw_data)
    
    class Meta:
        db_table = 'core_stixobject'
        indexes = [
            models.Index(fields=['stix_type']),
            models.Index(fields=['created']),
            models.Index(fields=['modified']),
            models.Index(fields=['created_by_ref']),
            models.Index(fields=['anonymized']),
        ]


class Collection(models.Model):
    """
    TAXII Collection for organizing shared threat intelligence.
    Integrated from crisp_threat_intel into core for unified threat intelligence handling.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    alias = models.SlugField(max_length=50, unique=True)
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    media_types = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Collection ownership and trust settings
    owner = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='owned_collections')
    default_anonymization = models.CharField(max_length=50, default='partial')
    
    # Many-to-many relationship with STIX objects
    stix_objects = models.ManyToManyField(
        STIXObject,
        through='CollectionObject',
        through_fields=('collection', 'stix_object'),
        related_name='collections'
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'core_collection'
        ordering = ['-created_at']


class CollectionObject(models.Model):
    """
    Through model for Collection-STIXObject many-to-many relationship.
    Allows additional metadata about the relationship.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    stix_object = models.ForeignKey(STIXObject, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    version_at_addition = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.version_at_addition:
            self.version_at_addition = self.stix_object.modified
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'core_collectionobject'
        unique_together = [['collection', 'stix_object']]
        ordering = ['-added_at']


class Feed(models.Model):
    """
    Threat intelligence feed that implements the Observer pattern.
    Integrated from crisp_threat_intel into core for unified threat intelligence handling.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='feeds')
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # TAXII integration fields
    taxii_collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Observer pattern support
    _observers = models.JSONField(default=list, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.owner.name})"
    
    def attach(self, observer):
        """Attach an observer to this feed"""
        if observer not in self._observers:
            self._observers.append(observer)
            self.save(update_fields=['_observers'])
    
    def detach(self, observer):
        """Detach an observer from this feed"""
        if observer in self._observers:
            self._observers.remove(observer)
            self.save(update_fields=['_observers'])
    
    def notify(self, event_data):
        """Notify all observers of an event"""
        # This would typically trigger async tasks to notify observers
        # Implementation depends on the specific observer pattern requirements
        pass
    
    class Meta:
        db_table = 'core_feed'
        ordering = ['-created_at']


class Identity(models.Model):
    """
    STIX Identity objects representing organizations, individuals, or groups.
    Integrated from crisp_threat_intel into core for unified threat intelligence handling.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stix_object = models.OneToOneField(STIXObject, on_delete=models.CASCADE, related_name='identity_details')
    name = models.CharField(max_length=255)
    identity_class = models.CharField(max_length=100)
    sectors = models.JSONField(default=list)
    contact_information = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'core_identity'
        verbose_name_plural = 'Identities'