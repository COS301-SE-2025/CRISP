from django.db import models
from django.contrib.auth.models import User
import uuid
import json
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'patterns', 'strategy'))

try:
    from core.patterns.strategy.enums import AnonymizationLevel
    from core.patterns.strategy.context import AnonymizationContext  
    from core.patterns.strategy.exceptions import AnonymizationError
except ImportError:
    # Fallback for development
    from enum import Enum
    
    class AnonymizationLevel(Enum):
        NONE = "none"
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        FULL = "full"
    
    class AnonymizationContext:
        def execute_anonymization(self, data, data_type, level):
            return f"[ANON:{level}]{data}"
        
        def anonymize_stix_object(self, stix_data, level):
            """Fallback STIX object anonymization"""
            import copy
            import json
            result = copy.deepcopy(stix_data)
            result['x_crisp_anonymized'] = True
            result['x_crisp_anonymization_level'] = level.value if hasattr(level, 'value') else str(level)
            result['x_crisp_trust_level'] = 0.5  # Default fallback trust level
            result['x_crisp_source_org'] = 'Unknown Organization'
            result['x_crisp_original_id'] = result.get('id', 'unknown')
            if 'pattern' in result:
                result['pattern'] = f"[ANON:{level}]{result['pattern']}"
            return json.dumps(result)
    
    class AnonymizationError(Exception):
        pass
import logging

logger = logging.getLogger(__name__)


class Organization(models.Model):
    """
    Organization model represents educational institutions or other organizations
    that participate in threat intelligence sharing.
    """
    TYPE_CHOICES = [
        ('university', 'University'),
        ('college', 'College'),
        ('school', 'School'),
        ('government', 'Government'),
        ('commercial', 'Commercial'),
        ('research', 'Research Institution'),
        ('ngo', 'Non-Governmental Organization'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    identity_class = models.CharField(max_length=100, default='organization')
    organization_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='university')
    sectors = models.JSONField(default=list, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
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
    original_data = models.JSONField(null=True, blank=True)  # Store original data before anonymization
    
    # System metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_stix_objects')
    source_organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='stix_objects')
    anonymized = models.BooleanField(default=False)
    anonymization_strategy = models.CharField(max_length=50, blank=True, null=True)
    anonymization_trust_level = models.FloatField(null=True, blank=True)
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
    
    def apply_anonymization(self, requesting_org, anonymization_level=None):
        """
        Apply anonymization to this STIX object based on requesting organization.
        """
        if self.source_organization == requesting_org:
            return self.raw_data  # No anonymization for same org
            
        if anonymization_level is None:
            # Determine anonymization level based on trust
            from .utils import get_anonymization_level
            anonymization_level = get_anonymization_level(self.source_organization, requesting_org)
        
        try:
            # Use the advanced anonymization context
            context = AnonymizationContext()
            anonymized_json = context.anonymize_stix_object(self.raw_data, anonymization_level)
            
            # Parse back to dictionary since the method returns JSON string
            anonymized_data = json.loads(anonymized_json)
            
            # Add anonymization metadata
            anonymized_data['x_crisp_anonymized'] = True
            anonymized_data['x_crisp_anonymization_level'] = anonymization_level.value
            anonymized_data['x_crisp_source_org'] = self.source_organization.name
            anonymized_data['x_crisp_original_id'] = self.stix_id
            
            return anonymized_data
            
        except AnonymizationError as e:
            logger.error(f"Anonymization failed for object {self.stix_id}: {e}")
            raise
    
    def get_trust_level(self, requesting_org):
        """Get trust level between source and requesting organization"""
        from .utils import get_trust_level
        return get_trust_level(self.source_organization, requesting_org)
    
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
    media_types = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Collection ownership and trust settings
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='owned_collections')
    default_anonymization_level = models.CharField(
        max_length=20,
        choices=[(level.value, level.value.title()) for level in AnonymizationLevel],
        default=AnonymizationLevel.MEDIUM.value
    )
    
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
        ordering = ['-created_at']
    
    def generate_bundle(self, requesting_org=None, filters=None):
        """
        Generate anonymized bundle for requesting organization using advanced anonymization.
        """
        from .utils import generate_bundle_from_collection
        return generate_bundle_from_collection(
            self, 
            filters=filters, 
            requesting_organization=requesting_org
        )


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




class TrustNetwork(models.Model):
    """
    Represents trust networks/communities for group-based trust management.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    default_trust_level = models.FloatField(default=0.6)
    default_anonymization_level = models.CharField(
        max_length=20,
        choices=[(level.value, level.value.title()) for level in AnonymizationLevel],
        default=AnonymizationLevel.MEDIUM.value
    )
    members = models.ManyToManyField(
        Organization, 
        through='NetworkMembership',
        related_name='trust_networks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class NetworkMembership(models.Model):
    """
    Membership in trust networks.
    """
    MEMBERSHIP_LEVELS = [
        ('full', 'Full Member'),
        ('associate', 'Associate Member'),
        ('observer', 'Observer'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    network = models.ForeignKey(TrustNetwork, on_delete=models.CASCADE)
    membership_level = models.CharField(max_length=50, choices=MEMBERSHIP_LEVELS)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['organization', 'network']


class ThreatFeed(models.Model):
    """
    External threat feeds that can be consumed via TAXII or other protocols
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # TAXII configuration
    taxii_server_url = models.URLField(blank=True, null=True)
    taxii_api_root = models.CharField(max_length=255, blank=True, null=True)
    taxii_collection_id = models.CharField(max_length=255, blank=True, null=True)
    taxii_username = models.CharField(max_length=255, blank=True, null=True)
    taxii_password = models.CharField(max_length=255, blank=True, null=True)
    
    # Feed metadata
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='owned_threat_feeds')
    is_external = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    last_sync = models.DateTimeField(blank=True, null=True)
    sync_interval_hours = models.IntegerField(default=24)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    last_error = models.TextField(blank=True, null=True)
    sync_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Indicator(models.Model):
    """
    Threat indicators with anonymization support
    """
    INDICATOR_TYPES = [
        ('ip', 'IP Address'),
        ('domain', 'Domain'),
        ('url', 'URL'),
        ('file_hash', 'File Hash'),
        ('email', 'Email Address'),
        ('registry', 'Registry Key'),
        ('mutex', 'Mutex'),
        ('process', 'Process'),
    ]
    
    HASH_TYPES = [
        ('md5', 'MD5'),
        ('sha1', 'SHA1'),
        ('sha256', 'SHA256'),
        ('sha512', 'SHA512'),
    ]
    
    # Core indicator data
    value = models.TextField()
    type = models.CharField(max_length=50, choices=INDICATOR_TYPES)
    hash_type = models.CharField(max_length=10, choices=HASH_TYPES, blank=True, null=True)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    confidence = models.IntegerField(default=50)  # 0-100
    threat_feed = models.ForeignKey(ThreatFeed, on_delete=models.CASCADE, related_name='indicators')
    stix_id = models.CharField(max_length=255, unique=True)
    
    # Temporal data
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    
    # Anonymization
    is_anonymized = models.BooleanField(default=False)
    original_value = models.TextField(blank=True, null=True)
    anonymization_method = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.type}: {self.value}"
    
    class Meta:
        unique_together = ['value', 'type', 'threat_feed']
        ordering = ['-last_seen']


class TTPData(models.Model):
    """
    Tactics, Techniques, and Procedures data (MITRE ATT&CK)
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # MITRE ATT&CK mapping
    mitre_technique_id = models.CharField(max_length=20)  # e.g., T1566.001
    mitre_tactic = models.CharField(max_length=100)  # e.g., Initial Access
    mitre_subtechnique = models.CharField(max_length=255, blank=True, null=True)
    
    # Metadata
    threat_feed = models.ForeignKey(ThreatFeed, on_delete=models.CASCADE, related_name='ttps')
    stix_id = models.CharField(max_length=255, unique=True)
    
    # Anonymization
    is_anonymized = models.BooleanField(default=False)
    original_data = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.mitre_technique_id}: {self.name}"
    
    class Meta:
        unique_together = ['mitre_technique_id', 'threat_feed']
        ordering = ['mitre_technique_id']


class Institution(models.Model):
    """
    Institution records for academic/educational organizations
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    contact_email = models.EmailField()
    contact_name = models.CharField(max_length=255)
    
    # Link to organization
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class TrustLevel(models.Model):
    """
    Trust levels for anonymization and data sharing
    """
    TRUST_LEVELS = [
        ('complete', 'Complete Trust'),
        ('high', 'High Trust'), 
        ('medium', 'Medium Trust'),
        ('low', 'Low Trust'),
        ('none', 'No Trust'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    level = models.CharField(max_length=20, choices=TRUST_LEVELS)
    numerical_value = models.IntegerField()  # 0-100 scale
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.numerical_value}%)"
    
    class Meta:
        ordering = ['-numerical_value']


class TrustRelationship(models.Model):
    """
    Trust relationships between organizations
    """
    RELATIONSHIP_TYPES = [
        ('partnership', 'Partnership'),
        ('vendor', 'Vendor Relationship'),
        ('educational', 'Educational Partnership'),
        ('research', 'Research Collaboration'),
        ('institutional', 'Institutional Trust'),
        ('government', 'Government Agency'),
    ]
    
    source_organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='trust_relationships_as_source'
    )
    target_organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='trust_relationships_as_target'
    )
    trust_level = models.ForeignKey(TrustLevel, on_delete=models.CASCADE)
    
    relationship_type = models.CharField(max_length=50, choices=RELATIONSHIP_TYPES, default='partnership')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=255, default='System')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.source_organization.name} → {self.target_organization.name} ({self.trust_level.name})"
    
    class Meta:
        unique_together = ['source_organization', 'target_organization']
        ordering = ['-created_at']