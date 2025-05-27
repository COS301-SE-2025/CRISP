from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone # Ensure timezone is imported

class Organization(models.Model):
    """
    Organization model represents educational institutions or other organizations
    that participate in threat intelligence sharing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    identity_class = models.CharField(max_length=100, default='organization')
    sectors = models.JSONField(default=list, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    stix_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_organizations')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class STIXObject(models.Model):
    """
    Base model for STIX objects with common fields.
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
    confidence = models.IntegerField(default=0)  # 0-100 scale
    external_references = models.JSONField(default=list)
    object_marking_refs = models.JSONField(default=list)
    granular_markings = models.JSONField(default=list)
    raw_data = models.JSONField()  # Complete raw STIX object
    
    # Metadata for our system
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_stix_objects')
    source_organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='stix_objects')
    anonymized = models.BooleanField(default=False)
    anonymization_strategy = models.CharField(max_length=50, blank=True, null=True)
    original_object_ref = models.CharField(max_length=255, blank=True, null=True)  # Reference to pre-anonymized object
    
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
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    alias = models.SlugField(max_length=50, unique=True)
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    media_types = models.JSONField(default=list)  # Supported media types
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Collection ownership and trust settings
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='owned_collections')
    default_anonymization = models.CharField(max_length=50, default='partial')
    
    # Add this relationship
    stix_objects = models.ManyToManyField(
        STIXObject,
        through='CollectionObject',
        through_fields=('collection', 'stix_object'),
        related_name='collections'
    )

    def __str__(self):
        return self.title

class CollectionObject(models.Model):
    """
    Association between STIX objects and TAXII collections.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection_objects')
    stix_object = models.ForeignKey(STIXObject, on_delete=models.CASCADE, related_name='collection_references')
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('collection', 'stix_object')
        indexes = [
            models.Index(fields=['collection', 'stix_object']),
            models.Index(fields=['date_added']),
        ]

class Feed(models.Model):
    """
    Represents a threat feed configuration for publishing.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='feeds')
    query_parameters = models.JSONField(default=dict)  # Filtering parameters
    update_interval = models.IntegerField(default=86400)  # Update interval in seconds (default: daily)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_published = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_feeds')
    
    # Add new fields for feed publishing
    last_bundle_id = models.CharField(max_length=255, blank=True, null=True)  # Track last published bundle
    last_published_time = models.DateTimeField(null=True, blank=True)
    publish_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

    def publish(self):
        """Publish the feed's content as a STIX bundle"""
        try:
            # Generate bundle from collection
            bundle = generate_bundle_from_collection(self.collection)
            
            # Update feed metadata
            self.last_bundle_id = bundle['id']
            self.last_published_time = timezone.now()
            self.publish_count += 1
            self.save()
            
            # Return publishing results
            return {
                'published_at': self.last_published_time,
                'bundle_id': self.last_bundle_id,
                'object_count': len(bundle.get('objects', [])),
                'status': 'success'
            }
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            self.save()
            raise

    def get_publication_status(self):
        """Get the current publication status"""
        return {
            'name': self.name,
            'status': self.status,
            'last_published': self.last_published_time,
            'publish_count': self.publish_count,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'collection': self.collection.title,
            'object_count': self.collection.stix_objects.count()
        }

class Identity(models.Model):
    """
    Model for STIX Identity objects representing organizations and their identities in STIX format.
    """
    stix_id = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    identity_class = models.CharField(max_length=100)
    organization = models.OneToOneField('Organization', on_delete=models.CASCADE, related_name='stix_identity')
    raw_data = models.TextField()  # JSON serialized STIX data
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Identities"
        ordering = ['-modified']

    def __str__(self):
        return f"{self.name} ({self.stix_id})"

    def to_stix(self):
        """Convert to STIX format"""
        import json
        return json.loads(self.raw_data)