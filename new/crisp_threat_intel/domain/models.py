from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import logging
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

logger = logging.getLogger(__name__)


class Institution(models.Model):
    """
    Represents organizations that share/consume threat intelligence
    Enhanced with production-ready features from original implementation
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    identity_class = models.CharField(max_length=100, default='organization')
    sectors = models.JSONField(default=list, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    stix_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Enhanced fields for production use
    is_active = models.BooleanField(default=True)
    trust_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    country = models.CharField(max_length=3, blank=True, null=True, help_text="ISO 3166-1 alpha-3 country code")
    timezone = models.CharField(max_length=50, default='UTC')
    api_quota_daily = models.IntegerField(default=1000, help_text="Daily API request quota")
    api_quota_used_today = models.IntegerField(default=0)
    quota_reset_date = models.DateField(auto_now_add=True)
    
    # Security and compliance
    requires_mfa = models.BooleanField(default=False)
    allowed_ip_ranges = models.JSONField(default=list, blank=True, help_text="CIDR notation IP ranges")
    data_retention_days = models.IntegerField(default=90)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_institutions')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.stix_id:
            self.stix_id = f"identity--{str(uuid.uuid4())}"
        super().save(*args, **kwargs)
    
    def reset_daily_quota(self):
        """Reset daily API quota if needed"""
        from datetime import date
        today = date.today()
        if self.quota_reset_date < today:
            self.api_quota_used_today = 0
            self.quota_reset_date = today
            self.save(update_fields=['api_quota_used_today', 'quota_reset_date'])
    
    def can_make_api_request(self) -> bool:
        """Check if institution can make an API request"""
        self.reset_daily_quota()
        return self.api_quota_used_today < self.api_quota_daily
    
    def record_api_request(self):
        """Record an API request against quota"""
        self.api_quota_used_today += 1
        self.save(update_fields=['api_quota_used_today'])
    
    def get_trust_relationships(self) -> List['TrustRelationship']:
        """Get all trust relationships for this institution"""
        return TrustRelationship.objects.filter(
            models.Q(source_institution=self) | models.Q(target_institution=self),
            is_active=True
        )
    
    def get_trust_level_for(self, other_institution: 'Institution') -> float:
        """Get trust level for another institution"""
        try:
            trust_rel = TrustRelationship.objects.get(
                source_institution=self,
                target_institution=other_institution,
                is_active=True
            )
            return trust_rel.trust_level
        except TrustRelationship.DoesNotExist:
            return 0.0  # No trust by default
    
    def to_stix(self) -> Dict[str, Any]:
        """Convert to STIX Identity object"""
        return {
            'type': 'identity',
            'id': self.stix_id,
            'created': self.created_at.isoformat(),
            'modified': self.updated_at.isoformat(),
            'name': self.name,
            'description': self.description,
            'identity_class': self.identity_class,
            'sectors': self.sectors,
            'contact_information': self.contact_email,
            'x_crisp_website': self.website,
            'x_crisp_country': self.country,
            'x_crisp_trust_score': self.trust_score
        }

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['stix_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['trust_score']),
            models.Index(fields=['quota_reset_date']),
        ]


class User(models.Model):
    """
    Employees of institutions who interact with the system
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    django_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='crisp_user'
    )
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Administrator'),
        ('analyst', 'Threat Analyst'),
        ('contributor', 'Contributor'),
        ('viewer', 'Viewer')
    ], default='viewer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.django_user.username} ({self.institution.name})"

    class Meta:
        ordering = ['django_user__username']


class ThreatFeed(models.Model):
    """
    Collections of threat data owned by institutions
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('error', 'Error')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='threat_feeds')
    query_parameters = models.JSONField(default=dict)
    update_interval = models.IntegerField(default=3600)  # seconds
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_published_time = models.DateTimeField(null=True, blank=True)
    next_publish_time = models.DateTimeField(null=True, blank=True)
    publish_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    last_bundle_id = models.CharField(max_length=255, blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_threat_feeds')

    # Observer pattern support
    _observers = []

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

    def add_observer(self, observer):
        """Add an observer to this threat feed"""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove an observer from this threat feed"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, event_type: str, data: Dict[str, Any]):
        """Notify all observers of a feed update"""
        for observer in self._observers:
            observer.update(self, event_type, data)

    def publish(self) -> Dict[str, Any]:
        """Publish the feed's content as a STIX bundle"""
        try:
            # Generate bundle from feed content
            bundle_data = self._generate_bundle()
            
            # Update feed metadata
            self.last_bundle_id = bundle_data['id']
            self.last_published_time = timezone.now()
            self.publish_count += 1
            self.save()
            
            # Notify observers
            self.notify_observers('published', {
                'bundle_id': self.last_bundle_id,
                'published_at': self.last_published_time,
                'object_count': len(bundle_data.get('objects', []))
            })
            
            # Schedule next publish if active
            if self.status == 'active':
                self.schedule_next_publish()
                
            return {
                'published_at': self.last_published_time,
                'bundle_id': self.last_bundle_id,
                'object_count': len(bundle_data.get('objects', [])),
                'status': 'success'
            }
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            self.save()
            
            # Notify observers of error
            self.notify_observers('error', {
                'error': str(e),
                'error_count': self.error_count
            })
            raise

    def schedule_next_publish(self):
        """Schedule next publish time based on interval"""
        if self.last_published_time:
            self.next_publish_time = self.last_published_time + timedelta(seconds=self.update_interval)
        else:
            self.next_publish_time = timezone.now() + timedelta(seconds=self.update_interval)
        self.save()

    def _generate_bundle(self) -> Dict[str, Any]:
        """Generate STIX bundle from feed content"""
        # This will be implemented by the service layer
        return {
            'id': f"bundle--{uuid.uuid4()}",
            'type': 'bundle',
            'objects': []
        }


class Indicator(models.Model):
    """
    Indicators of compromise that might signal a threat
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stix_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    pattern = models.TextField()  # STIX pattern
    labels = models.JSONField(default=list)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    confidence = models.IntegerField(default=0)  # 0-100 scale
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_by_ref = models.CharField(max_length=255, blank=True, null=True)
    revoked = models.BooleanField(default=False)
    external_references = models.JSONField(default=list)
    object_marking_refs = models.JSONField(default=list)
    granular_markings = models.JSONField(default=list)
    
    # System metadata
    threat_feed = models.ForeignKey(ThreatFeed, on_delete=models.CASCADE, related_name='indicators')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_indicators')
    anonymized = models.BooleanField(default=False)
    anonymization_strategy = models.CharField(max_length=50, blank=True, null=True)
    original_object_ref = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.stix_id})"

    def save(self, *args, **kwargs):
        if not self.stix_id:
            self.stix_id = f"indicator--{str(uuid.uuid4())}"
        if not self.created:
            self.created = timezone.now()
        self.modified = timezone.now()
        super().save(*args, **kwargs)

    def to_stix(self) -> Dict[str, Any]:
        """Convert to STIX format"""
        return {
            'type': 'indicator',
            'id': self.stix_id,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'name': self.name,
            'description': self.description,
            'pattern': self.pattern,
            'labels': self.labels,
            'valid_from': self.valid_from.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'confidence': self.confidence,
            'created_by_ref': self.created_by_ref,
            'revoked': self.revoked,
            'external_references': self.external_references,
            'object_marking_refs': self.object_marking_refs,
            'granular_markings': self.granular_markings
        }

    class Meta:
        indexes = [
            models.Index(fields=['stix_id']),
            models.Index(fields=['created']),
            models.Index(fields=['modified']),
            models.Index(fields=['valid_from']),
            models.Index(fields=['anonymized']),
        ]


class TTPData(models.Model):
    """
    Tactics, Techniques, and Procedures used by threat actors
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stix_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    kill_chain_phases = models.JSONField(default=list)
    x_mitre_platforms = models.JSONField(default=list)
    x_mitre_tactics = models.JSONField(default=list)
    x_mitre_techniques = models.JSONField(default=list)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_by_ref = models.CharField(max_length=255, blank=True, null=True)
    revoked = models.BooleanField(default=False)
    external_references = models.JSONField(default=list)
    object_marking_refs = models.JSONField(default=list)
    granular_markings = models.JSONField(default=list)
    
    # System metadata
    threat_feed = models.ForeignKey(ThreatFeed, on_delete=models.CASCADE, related_name='ttp_data')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_ttp_data')
    anonymized = models.BooleanField(default=False)
    anonymization_strategy = models.CharField(max_length=50, blank=True, null=True)
    original_object_ref = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.stix_id})"

    def save(self, *args, **kwargs):
        if not self.stix_id:
            self.stix_id = f"attack-pattern--{str(uuid.uuid4())}"
        if not self.created:
            self.created = timezone.now()
        self.modified = timezone.now()
        super().save(*args, **kwargs)

    def to_stix(self) -> Dict[str, Any]:
        """Convert to STIX format"""
        return {
            'type': 'attack-pattern',
            'id': self.stix_id,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'name': self.name,
            'description': self.description,
            'kill_chain_phases': self.kill_chain_phases,
            'x_mitre_platforms': self.x_mitre_platforms,
            'x_mitre_tactics': self.x_mitre_tactics,
            'x_mitre_techniques': self.x_mitre_techniques,
            'created_by_ref': self.created_by_ref,
            'revoked': self.revoked,
            'external_references': self.external_references,
            'object_marking_refs': self.object_marking_refs,
            'granular_markings': self.granular_markings
        }

    class Meta:
        indexes = [
            models.Index(fields=['stix_id']),
            models.Index(fields=['created']),
            models.Index(fields=['modified']),
            models.Index(fields=['anonymized']),
        ]


class TrustRelationship(models.Model):
    """
    Trust relationships between institutions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='outgoing_trust')
    target_institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='incoming_trust')
    trust_level = models.FloatField()  # 0.0 to 1.0
    established_at = models.DateTimeField(auto_now_add=True)
    established_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='established_trust')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.source_institution.name} -> {self.target_institution.name} ({self.trust_level})"

    class Meta:
        unique_together = ('source_institution', 'target_institution')
        indexes = [
            models.Index(fields=['source_institution', 'target_institution']),
            models.Index(fields=['trust_level']),
        ]


class FeedSubscription(models.Model):
    """
    Institution subscriptions to threat feeds
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='feed_subscriptions')
    threat_feed = models.ForeignKey(ThreatFeed, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.institution.name} -> {self.threat_feed.name}"

    class Meta:
        unique_together = ('institution', 'threat_feed')


class FeedFilter(models.Model):
    """
    Filters for feed subscriptions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.OneToOneField(FeedSubscription, on_delete=models.CASCADE, related_name='filter')
    indicator_types = models.JSONField(default=list)
    confidence_threshold = models.IntegerField(default=0)
    labels_include = models.JSONField(default=list)
    labels_exclude = models.JSONField(default=list)
    date_range_start = models.DateTimeField(null=True, blank=True)
    date_range_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Filter for {self.subscription}"


# Subject interface for Observer pattern
class Subject(ABC):
    """
    Abstract subject interface for Observer pattern
    """
    
    @abstractmethod
    def add_observer(self, observer):
        """Add an observer"""
        pass
    
    @abstractmethod
    def remove_observer(self, observer):
        """Remove an observer"""
        pass
    
    @abstractmethod
    def notify_observers(self, event_type: str, data: Dict[str, Any]):
        """Notify all observers"""
        pass


# Observer interface for Observer pattern
class Observer(ABC):
    """
    Abstract observer interface for Observer pattern
    """
    
    @abstractmethod
    def update(self, subject: Subject, event_type: str, data: Dict[str, Any]):
        """Update observer with new data"""
        pass


class STIXObject(models.Model):
    """
    Generic STIX object storage - critical for TAXII API implementation
    """
    STIX_TYPES = [
        ('indicator', 'Indicator'),
        ('malware', 'Malware'),
        ('attack-pattern', 'Attack Pattern'),
        ('tool', 'Tool'),
        ('vulnerability', 'Vulnerability'),
        ('intrusion-set', 'Intrusion Set'),
        ('campaign', 'Campaign'),
        ('threat-actor', 'Threat Actor'),
        ('course-of-action', 'Course of Action'),
        ('identity', 'Identity'),
        ('relationship', 'Relationship'),
        ('sighting', 'Sighting'),
        ('observed-data', 'Observed Data'),
        ('artifact', 'Artifact'),
        ('autonomous-system', 'Autonomous System'),
        ('directory', 'Directory'),
        ('domain-name', 'Domain Name'),
        ('email-addr', 'Email Address'),
        ('file', 'File'),
        ('ipv4-addr', 'IPv4 Address'),
        ('ipv6-addr', 'IPv6 Address'),
        ('mac-addr', 'MAC Address'),
        ('mutex', 'Mutex'),
        ('network-traffic', 'Network Traffic'),
        ('process', 'Process'),
        ('software', 'Software'),
        ('url', 'URL'),
        ('user-account', 'User Account'),
        ('windows-registry-key', 'Windows Registry Key'),
        ('x509-certificate', 'X.509 Certificate'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stix_id = models.CharField(max_length=255, unique=True, db_index=True)
    stix_type = models.CharField(max_length=50, choices=STIX_TYPES, db_index=True)
    stix_version = models.CharField(max_length=10, default='2.1')
    raw_data = models.JSONField()  # Complete STIX object as JSON
    
    # Extracted commonly queried fields for performance
    created_time = models.DateTimeField(db_index=True)
    modified_time = models.DateTimeField(db_index=True)
    created_by_ref = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    revoked = models.BooleanField(default=False, db_index=True)
    confidence = models.IntegerField(null=True, blank=True, db_index=True)
    
    # System metadata
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='stix_objects')
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE, related_name='objects', null=True, blank=True)
    threat_feed = models.ForeignKey(ThreatFeed, on_delete=models.CASCADE, related_name='stix_objects', null=True, blank=True)
    
    # Anonymization tracking
    is_anonymized = models.BooleanField(default=False, db_index=True)
    anonymization_level = models.CharField(max_length=20, blank=True, null=True)
    original_stix_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_stix_objects')
    
    def __str__(self):
        return f"{self.stix_type}: {self.stix_id}"
    
    def save(self, *args, **kwargs):
        # Extract commonly queried fields from raw_data
        if self.raw_data:
            self.created_time = timezone.datetime.fromisoformat(
                self.raw_data.get('created', timezone.now().isoformat()).replace('Z', '+00:00')
            )
            self.modified_time = timezone.datetime.fromisoformat(
                self.raw_data.get('modified', timezone.now().isoformat()).replace('Z', '+00:00')
            )
            self.created_by_ref = self.raw_data.get('created_by_ref', '')
            self.revoked = self.raw_data.get('revoked', False)
            self.confidence = self.raw_data.get('confidence')
            
        super().save(*args, **kwargs)
    
    def get_labels(self) -> List[str]:
        """Get labels from STIX object"""
        return self.raw_data.get('labels', [])
    
    def matches_filter(self, stix_filter: Dict[str, Any]) -> bool:
        """Check if object matches a TAXII filter"""
        # Implement TAXII filtering logic
        if 'type' in stix_filter and self.stix_type not in stix_filter['type']:
            return False
        
        if 'id' in stix_filter and self.stix_id not in stix_filter['id']:
            return False
        
        if 'added_after' in stix_filter:
            added_after = timezone.datetime.fromisoformat(stix_filter['added_after'].replace('Z', '+00:00'))
            if self.created_at <= added_after:
                return False
        
        return True
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stix_id']),
            models.Index(fields=['stix_type']),
            models.Index(fields=['created_time']),
            models.Index(fields=['modified_time']),
            models.Index(fields=['created_by_ref']),
            models.Index(fields=['revoked']),
            models.Index(fields=['confidence']),
            models.Index(fields=['is_anonymized']),
            models.Index(fields=['institution', 'created_at']),
            models.Index(fields=['collection', 'created_at']),
            models.Index(fields=['stix_type', 'created_at']),
        ]


class Collection(models.Model):
    """
    TAXII Collections for organizing STIX objects
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection_id = models.CharField(max_length=255, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    media_types = models.JSONField(default=list)  # Supported media types
    
    # Access control
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='collections')
    is_public = models.BooleanField(default=False)
    authorized_institutions = models.ManyToManyField(
        Institution, 
        through='CollectionAccess',
        related_name='accessible_collections',
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_collections')
    
    def __str__(self):
        return f"{self.title} ({self.collection_id})"
    
    def save(self, *args, **kwargs):
        if not self.collection_id:
            self.collection_id = str(uuid.uuid4())
        if not self.media_types:
            self.media_types = ['application/stix+json;version=2.1']
        super().save(*args, **kwargs)
    
    def can_access(self, institution: Institution, access_type: str = 'read') -> bool:
        """Check if institution can access this collection"""
        if self.institution == institution:
            return True  # Owner has full access
        
        if self.is_public and access_type == 'read':
            return True
        
        try:
            access = CollectionAccess.objects.get(
                collection=self,
                institution=institution,
                is_active=True
            )
            if access_type == 'read':
                return access.can_read
            elif access_type == 'write':
                return access.can_write
            return False
        except CollectionAccess.DoesNotExist:
            return False
    
    def get_object_count(self) -> int:
        """Get count of objects in collection"""
        return self.objects.count()
    
    def to_taxii_collection(self) -> Dict[str, Any]:
        """Convert to TAXII Collection format"""
        return {
            'id': self.collection_id,
            'title': self.title,
            'description': self.description,
            'can_read': self.can_read,
            'can_write': self.can_write,
            'media_types': self.media_types
        }
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['collection_id']),
            models.Index(fields=['institution']),
            models.Index(fields=['is_public']),
            models.Index(fields=['can_read']),
            models.Index(fields=['can_write']),
        ]


class CollectionAccess(models.Model):
    """
    Access control for collections
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ('collection', 'institution')
        indexes = [
            models.Index(fields=['collection', 'institution']),
            models.Index(fields=['is_active']),
        ]


class TrustGroup(models.Model):
    """
    Groups of institutions with shared trust levels
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    default_trust_level = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class TrustGroupMembership(models.Model):
    """
    Membership of institutions in trust groups
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trust_group = models.ForeignKey(TrustGroup, on_delete=models.CASCADE, related_name='memberships')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='trust_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('trust_group', 'institution')


class AuditLog(models.Model):
    """
    Comprehensive audit logging for security and compliance
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('access_denied', 'Access Denied'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('publish', 'Publish'),
        ('subscribe', 'Subscribe'),
        ('anonymize', 'Anonymize'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    resource_type = models.CharField(max_length=50, db_index=True)
    resource_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True, db_index=True)
    user_agent = models.TextField(blank=True, null=True)
    details = models.JSONField(default=dict)
    success = models.BooleanField(default=True, db_index=True)
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        user_info = f"{self.user.django_user.username}" if self.user else "Anonymous"
        return f"{self.timestamp}: {user_info} {self.action} {self.resource_type}"
    
    @classmethod
    def log_action(cls, user: User = None, institution: Institution = None, 
                   action: str = None, resource_type: str = None, 
                   resource_id: str = None, ip_address: str = None, 
                   user_agent: str = None, details: Dict = None, 
                   success: bool = True, error_message: str = None):
        """Convenience method for logging actions"""
        try:
            cls.objects.create(
                user=user,
                institution=institution,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                success=success,
                error_message=error_message
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['institution']),
            models.Index(fields=['action']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['resource_id']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['success']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['institution', 'timestamp']),
        ]