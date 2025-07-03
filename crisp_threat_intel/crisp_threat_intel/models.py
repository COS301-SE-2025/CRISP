from django.db import models
from django.contrib.auth.models import User
import uuid
import json
import logging
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger(__name__)


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
    Base model for STIX objects with complete STIX 2.1 compliance.
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
    source_organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='stix_objects')
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
    
    def apply_anonymization(self, trust_level: float) -> 'STIXObject':
        """
        Apply anonymization to this STIX object based on trust level.
        
        Args:
            trust_level: Trust level between organizations (0.0-1.0)
            
        Returns:
            New anonymized STIXObject instance
        """
        try:
            from .strategies.integrated_anonymization import IntegratedAnonymizationContext
            
            context = IntegratedAnonymizationContext()
            anonymized_raw_data = context.anonymize_stix_object(self.raw_data, trust_level)
            
            # Create new anonymized object
            anonymized_obj = STIXObject(
                stix_id=f"{self.stix_id}-anon-{str(uuid.uuid4())[:8]}",
                stix_type=self.stix_type,
                spec_version=self.spec_version,
                created=self.created,
                modified=timezone.now(),
                created_by_ref=self.created_by_ref,
                revoked=self.revoked,
                labels=self.labels,
                confidence=self.confidence,
                external_references=self.external_references,
                object_marking_refs=self.object_marking_refs,
                granular_markings=self.granular_markings,
                raw_data=anonymized_raw_data,
                source_organization=self.source_organization,
                anonymized=True,
                anonymization_strategy='integrated',
                original_object_ref=self.stix_id
            )
            
            return anonymized_obj
            
        except Exception as e:
            logger.error(f"Error applying anonymization: {e}")
            # Return copy of original object if anonymization fails
            return self
    
    class Meta:
        indexes = [
            models.Index(fields=['stix_type']),
            models.Index(fields=['created']),
            models.Index(fields=['modified']),
            models.Index(fields=['created_by_ref']),
            models.Index(fields=['anonymized']),
        ]


class TrustRelationship(models.Model):
    """
    Model for managing trust relationships between organizations.
    This determines the level of anonymization applied when sharing data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='outgoing_trust_relationships'
    )
    target_organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='incoming_trust_relationships'
    )
    trust_level = models.FloatField(
        default=0.5,
        help_text="Trust level between 0.0 (no trust) and 1.0 (full trust)"
    )
    anonymization_strategy = models.CharField(
        max_length=50, 
        default='integrated',
        help_text="Anonymization strategy to use for this relationship"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_trust_relationships'
    )
    
    class Meta:
        unique_together = ('source_organization', 'target_organization')
        indexes = [
            models.Index(fields=['source_organization', 'target_organization']),
            models.Index(fields=['trust_level']),
        ]
    
    def __str__(self):
        return f"{self.source_organization.name} → {self.target_organization.name} (trust: {self.trust_level})"
    
    @classmethod
    def get_trust_level(cls, source_org: Organization, target_org: Organization) -> float:
        """
        Get trust level between two organizations.
        
        Args:
            source_org: Source organization
            target_org: Target organization
            
        Returns:
            Trust level (0.0-1.0), defaults to 0.3 if no relationship exists
        """
        try:
            relationship = cls.objects.get(
                source_organization=source_org,
                target_organization=target_org
            )
            return relationship.trust_level
        except cls.DoesNotExist:
            # Default to low trust if no relationship exists
            return 0.3


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
    media_types = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Collection ownership and trust settings
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='owned_collections')
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

    def generate_bundle(self, requesting_organization: Organization = None) -> dict:
        """
        Generate a STIX bundle from this collection with appropriate anonymization.
        
        Args:
            requesting_organization: Organization requesting the bundle
            
        Returns:
            STIX bundle dictionary with anonymized objects
        """
        from .strategies.integrated_anonymization import IntegratedAnonymizationContext
        
        # Get all STIX objects in this collection
        stix_objects = self.stix_objects.all()
        
        # Determine trust level
        if requesting_organization and requesting_organization != self.owner:
            trust_level = TrustRelationship.get_trust_level(self.owner, requesting_organization)
        else:
            trust_level = 1.0  # Full trust for owner organization
        
        # Create anonymization context
        context = IntegratedAnonymizationContext()
        
        # Generate bundle
        bundle = {
            'type': 'bundle',
            'id': f'bundle--{str(uuid.uuid4())}',
            'objects': []
        }
        
        # Anonymize objects based on trust level
        for stix_obj in stix_objects:
            if trust_level >= 0.8:
                # High trust - no anonymization
                bundle['objects'].append(stix_obj.raw_data)
            else:
                # Apply anonymization
                anonymized_data = context.anonymize_stix_object(stix_obj.raw_data, trust_level)
                bundle['objects'].append(anonymized_data)
        
        # Add bundle metadata
        bundle['x_crisp_collection_id'] = str(self.id)
        bundle['x_crisp_owner'] = self.owner.name
        bundle['x_crisp_trust_level'] = trust_level
        bundle['x_crisp_generated_at'] = timezone.now().isoformat()
        
        return bundle
    
    def get_objects_for_organization(self, requesting_organization: Organization) -> list:
        """
        Get anonymized objects from this collection for a specific organization.
        
        Args:
            requesting_organization: Organization requesting the objects
            
        Returns:
            List of anonymized STIX objects
        """
        trust_level = TrustRelationship.get_trust_level(self.owner, requesting_organization)
        
        from .strategies.integrated_anonymization import IntegratedAnonymizationContext
        context = IntegratedAnonymizationContext()
        
        anonymized_objects = []
        for stix_obj in self.stix_objects.all():
            if trust_level >= 0.8:
                anonymized_objects.append(stix_obj.raw_data)
            else:
                anonymized_data = context.anonymize_stix_object(stix_obj.raw_data, trust_level)
                anonymized_objects.append(anonymized_data)
        
        return anonymized_objects

    class Meta:
        ordering = ['-created_at']


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
    Implements the Observer pattern as a Subject for feed updates.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('error', 'Error')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE, related_name='feeds')
    query_parameters = models.JSONField(default=dict)
    update_interval = models.IntegerField(default=3600)  # Default: hourly in seconds
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_published_time = models.DateTimeField(null=True, blank=True)
    next_publish_time = models.DateTimeField(null=True, blank=True)
    publish_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    last_bundle_id = models.CharField(max_length=255, blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_feeds'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

    def publish(self):
        """
        Publish the feed's content as a STIX bundle.
        This method works exactly like the original implementation.
        """
        try:
            from .utils import generate_bundle_from_collection
            
            # Generate bundle from collection
            bundle = generate_bundle_from_collection(self.collection)
            
            # Update feed metadata
            self.last_bundle_id = bundle['id']
            self.last_published_time = timezone.now()
            self.publish_count += 1
            self.save()
            
            # Schedule next publish if active
            if self.status == 'active':
                self.schedule_next_publish()
                
            # Notify observers (Observer pattern implementation)
            self.notify_observers(bundle)
                
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

    def schedule_next_publish(self):
        """Schedule next publish time based on interval"""
        if self.last_published_time:
            self.next_publish_time = self.last_published_time + timedelta(seconds=self.update_interval)
        else:
            self.next_publish_time = timezone.now() + timedelta(seconds=self.update_interval)
        self.save()

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
    
    def notify_observers(self, bundle):
        """
        Notify all observers about feed update (Observer pattern implementation).
        Uses Django signals for loose coupling.
        """
        from django.dispatch import Signal
        
        # Define feed_updated signal
        feed_updated = Signal()
        
        # Send signal to notify observers
        feed_updated.send(
            sender=self.__class__,
            feed=self,
            bundle=bundle
        )


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
        return json.loads(self.raw_data)