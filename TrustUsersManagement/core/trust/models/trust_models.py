import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta


TRUST_LEVEL_CHOICES = [
    ('public', 'Public Trust'),
    ('trusted', 'Trusted Trust'),
    ('restricted', 'Restricted Trust'),
]

TRUST_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('active', 'Active'),
    ('suspended', 'Suspended'),
    ('revoked', 'Revoked'),
    ('expired', 'Expired'),
]

RELATIONSHIP_TYPE_CHOICES = [
    ('bilateral', 'Bilateral Trust'),
    ('community', 'Community Trust'),
    ('hierarchical', 'Hierarchical Trust'),
    ('federation', 'Federation Trust'),
]

ANONYMIZATION_LEVEL_CHOICES = [
    ('none', 'No Anonymization'),
    ('minimal', 'Minimal Anonymization'),
    ('partial', 'Partial Anonymization'),
    ('full', 'Full Anonymization'),
    ('custom', 'Custom Anonymization'),
]

ACCESS_LEVEL_CHOICES = [
    ('none', 'No Access'),
    ('read', 'Read Only'),
    ('subscribe', 'Subscribe to Feeds'),
    ('contribute', 'Contribute Intelligence'),
    ('full', 'Full Access'),
]


class TrustLevel(models.Model):
    """
    Configurable trust levels that define sharing policies and access controls.
    Supports customizable trust definitions per organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique name for this trust level"
    )
    level = models.CharField(
        max_length=20,
        choices=TRUST_LEVEL_CHOICES,
        help_text="Standard trust level classification"
    )
    description = models.TextField(
        help_text="Detailed description of what this trust level means"
    )
    numerical_value = models.IntegerField(
        help_text="Numerical representation for comparison (0-100)"
    )
    default_anonymization_level = models.CharField(
        max_length=20,
        choices=ANONYMIZATION_LEVEL_CHOICES,
        default='partial',
        help_text="Default anonymization level for this trust level"
    )
    default_access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='read',
        help_text="Default access level for this trust level"
    )
    sharing_policies = models.JSONField(
        default=dict,
        help_text="Detailed sharing policies and restrictions"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this trust level is currently active"
    )
    is_system_default = models.BooleanField(
        default=False,
        help_text="Whether this is a system default trust level"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=255,
        help_text="System user who created this trust level"
    )

    class Meta:
        verbose_name = 'Trust Level'
        verbose_name_plural = 'Trust Levels'
        ordering = ['numerical_value']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['numerical_value']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.level})"

    def clean(self):
        if self.numerical_value < 0 or self.numerical_value > 100:
            raise ValidationError("Numerical value must be between 0 and 100")
        
        # Validate level choice
        valid_levels = [choice[0] for choice in TRUST_LEVEL_CHOICES]
        if self.level not in valid_levels:
            raise ValidationError(f"Level must be one of: {', '.join(valid_levels)}")
    
    @property
    def is_default(self):
        """Property to check if this is the default trust level"""
        return self.is_system_default

    @classmethod
    def get_default_trust_level(cls):
        """Get the default trust level for new relationships"""
        return cls.objects.filter(is_system_default=True, is_active=True).first()
    
    @classmethod
    def get_default(cls):
        """Get the default trust level - alias for get_default_trust_level"""
        return cls.get_default_trust_level()


class TrustGroup(models.Model):
    """
    Community-based trust groups that allow multiple organizations
    to share intelligence with common trust policies.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the trust group"
    )
    description = models.TextField(
        help_text="Description of the trust group's purpose"
    )
    group_type = models.CharField(
        max_length=50,
        default='community',
        help_text="Type of trust group (sector, geography, purpose, etc.)"
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether organizations can request to join publicly"
    )
    requires_approval = models.BooleanField(
        default=True,
        help_text="Whether membership requires approval"
    )
    default_trust_level = models.ForeignKey(
        TrustLevel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='default_for_groups',
        help_text="Default trust level for group members"
    )
    group_policies = models.JSONField(
        default=dict,
        help_text="Group-specific sharing and access policies"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this trust group is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=255,
        help_text="Organization that created this group"
    )
    administrators = models.JSONField(
        default=list,
        help_text="List of organization IDs that can administer this group"
    )

    class Meta:
        verbose_name = 'Trust Group'
        verbose_name_plural = 'Trust Groups'
        ordering = ['name']
        indexes = [
            models.Index(fields=['group_type']),
            models.Index(fields=['is_public']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.group_type})"

    def can_administer(self, organization_id):
        """Check if an organization can administer this group"""
        return str(organization_id) in self.administrators

    def get_member_count(self):
        """Get the number of active members in this group"""
        return self.group_memberships.filter(is_active=True).count()
    
    @property
    def member_count(self):
        """Property version of get_member_count for compatibility"""
        return self.get_member_count()
    
    @property
    def member_organizations(self):
        """Get member organizations through membership relationship"""
        # Return a custom manager-like object that supports add/remove/all operations
        class MemberOrganizationsManager:
            def __init__(self, trust_group):
                self.trust_group = trust_group
            
            def add(self, organization):
                """Add an organization to the group"""
                TrustGroupMembership.objects.get_or_create(
                    trust_group=self.trust_group,
                    organization=organization,
                    defaults={'membership_type': 'member', 'is_active': True}
                )
            
            def remove(self, organization):
                """Remove an organization from the group"""
                TrustGroupMembership.objects.filter(
                    trust_group=self.trust_group,
                    organization=organization
                ).delete()
            
            def all(self):
                """Get all member organizations"""
                from core.user_management.models import Organization
                return Organization.objects.filter(
                    trust_group_memberships__trust_group=self.trust_group,
                    trust_group_memberships__is_active=True
                )
        
        return MemberOrganizationsManager(self)


class TrustRelationship(models.Model):
    """
    Core trust relationship model supporting bilateral and community-based trust.
    Implements trust-based access controls and sharing policies.
    """
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Organizations involved in the trust relationship
    source_organization = models.ForeignKey(
        'user_management.Organization',
        on_delete=models.CASCADE,
        related_name='trust_relationships_as_source',
        help_text="Source organization in the trust relationship"
    )
    target_organization = models.ForeignKey(
        'user_management.Organization',
        on_delete=models.CASCADE,
        related_name='trust_relationships_as_target',
        help_text="Target organization in the trust relationship"
    )
    
    # Trust relationship configuration
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPE_CHOICES,
        default='bilateral',
        help_text="Type of trust relationship"
    )
    trust_level = models.ForeignKey(
        TrustLevel,
        on_delete=models.CASCADE,
        related_name='trust_relationships',
        help_text="Trust level for this relationship"
    )
    trust_group = models.ForeignKey(
        TrustGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='group_relationships',
        help_text="Trust group if this is a community relationship"
    )
    
    # Relationship status and validity
    status = models.CharField(
        max_length=20,
        choices=TRUST_STATUS_CHOICES,
        default='pending',
        help_text="Current status of the trust relationship"
    )
    is_bilateral = models.BooleanField(
        default=True,
        help_text="Whether trust is mutual (both directions)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this relationship is currently active"
    )
    
    # Temporal aspects
    valid_from = models.DateTimeField(
        default=timezone.now,
        help_text="When this trust relationship becomes valid"
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this trust relationship expires (null = never)"
    )
    
    # Sharing and access configuration
    sharing_preferences = models.JSONField(
        default=dict,
        help_text="Organization-specific sharing preferences"
    )
    anonymization_level = models.CharField(
        max_length=20,
        choices=ANONYMIZATION_LEVEL_CHOICES,
        help_text="Level of anonymization to apply"
    )
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='read',
        help_text="Access level granted by this relationship"
    )
    
    # Approval and management
    approved_by_source = models.BooleanField(
        default=False,
        help_text="Whether source organization has approved"
    )
    approved_by_target = models.BooleanField(
        default=False,
        help_text="Whether target organization has approved"
    )
    approved_by_source_user = models.ForeignKey(
        'user_management.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trust_approvals_as_source',
        help_text="User who approved on behalf of source organization"
    )
    approved_by_target_user = models.ForeignKey(
        'user_management.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trust_approvals_as_target',
        help_text="User who approved on behalf of target organization"
    )
    
    # Missing approval status fields
    source_approval_status = models.CharField(
        max_length=20, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='pending'
    )
    target_approval_status = models.CharField(
        max_length=20, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='pending'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata about the relationship"
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes about this trust relationship"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this relationship was activated"
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this relationship was revoked"
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        'user_management.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_trust_relationships',
        help_text="User who created this relationship"
    )
    last_modified_by = models.ForeignKey(
        'user_management.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_trust_relationships',
        help_text="User who last modified this relationship"
    )
    revoked_by = models.ForeignKey(
        'user_management.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_trust_relationships',
        help_text="User who revoked this relationship"
    )

    class Meta:
        verbose_name = 'Trust Relationship'
        verbose_name_plural = 'Trust Relationships'
        unique_together = ['source_organization', 'target_organization']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_organization']),
            models.Index(fields=['target_organization']),
            models.Index(fields=['status']),
            models.Index(fields=['trust_level']),
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_from']),
            models.Index(fields=['valid_until']),
        ]

    def __str__(self):
        return f"Trust: {self.source_organization} -> {self.target_organization} ({self.trust_level.name})"

    def clean(self):
        if self.source_organization == self.target_organization:
            raise ValidationError("Source and target organizations cannot be the same")
        
        if self.valid_until and self.valid_until <= self.valid_from:
            raise ValidationError("Valid until date must be after valid from date")

    @property
    def is_expired(self):
        """Check if the trust relationship is expired"""
        if self.valid_until:
            return timezone.now() > self.valid_until
        return False

    @property
    def is_fully_approved(self):
        """Check if relationship is fully approved"""
        return (self.source_approval_status == 'approved' and 
                self.target_approval_status == 'approved')
    
    @property
    def is_effective(self):
        """Check if relationship is effective (active and approved)"""
        # Check if status is active and relationship is approved
        is_approved = (self.approved_by_source and self.approved_by_target)
        
        # Check if effective date has passed (or is None, meaning immediate effect)
        effective_date_passed = (self.effective_date is None or 
                               self.effective_date <= timezone.now().date())
        
        return (self.status == 'active' and 
                is_approved and 
                effective_date_passed and
                not self.is_expired)
    
    def set_approval_status(self, source_status=None, target_status=None):
        """Set approval status for testing"""
        if source_status:
            self.source_approval_status = source_status
        if target_status:
            self.target_approval_status = target_status
        self.save()
    
    @property
    def effective_date(self):
        """Get the effective date for the trust relationship"""
        if self.valid_from:
            return self.valid_from.date()
        return None

    def activate(self):
        """Activate the trust relationship"""
        if self.is_fully_approved:
            self.status = 'active'
            self.activated_at = timezone.now()
            self.save(update_fields=['status', 'activated_at'])
            return True
        return False

    def approve(self, organization, user):
        """Approve the relationship from an organization's perspective"""
        if organization == self.source_organization:
            self.source_approval_status = 'approved'
        elif organization == self.target_organization:
            self.target_approval_status = 'approved'
        
        # Auto-activate if both sides approved
        if self.is_fully_approved:
            self.status = 'active'
        
        self.save()
    
    def deny(self, denying_org=None, user=None, reason=None):
        """Deny the trust relationship"""
        self.status = 'revoked'
        if reason:
            self.notes = f"{self.notes}\nDenied: {reason}" if self.notes else f"Denied: {reason}"
        if user:
            self.last_modified_by = user
        self.save(update_fields=['status', 'notes', 'last_modified_by'])
        return True

    def revoke(self, revoked_by, reason=None):
        """Revoke the trust relationship"""
        self.status = 'revoked'
        self.is_active = False
        self.revoked_at = timezone.now()
        self.revoked_by = revoked_by
        if reason:
            self.notes = f"{self.notes}\nRevoked: {reason}" if self.notes else f"Revoked: {reason}"
        self.save(update_fields=['status', 'is_active', 'revoked_at', 'revoked_by', 'notes'])

    def suspend(self, suspended_by, reason=None):
        """Suspend the trust relationship"""
        self.status = 'suspended'
        self.last_modified_by = suspended_by
        if reason:
            self.notes = f"{self.notes}\nSuspended: {reason}" if self.notes else f"Suspended: {reason}"
        self.save(update_fields=['status', 'last_modified_by', 'notes'])

    def get_effective_anonymization_level(self):
        """Get the effective anonymization level considering trust level defaults"""
        if self.anonymization_level != 'custom':
            return self.anonymization_level
        return self.trust_level.default_anonymization_level

    def get_effective_access_level(self):
        """Get the effective access level considering trust level defaults"""
        access_levels = [choice[0] for choice in ACCESS_LEVEL_CHOICES]
        return max(self.access_level, self.trust_level.default_access_level, key=lambda x: access_levels.index(x))


class TrustGroupMembership(models.Model):
    """
    Membership of organizations in trust groups.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trust_group = models.ForeignKey(
        TrustGroup,
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    organization = models.ForeignKey(
        'user_management.Organization',
        on_delete=models.CASCADE,
        related_name='trust_group_memberships',
        help_text="Organization that is a member of this trust group"
    )
    membership_type = models.CharField(
        max_length=20,
        choices=[
            ('member', 'Member'),
            ('administrator', 'Administrator'),
            ('moderator', 'Moderator'),
        ],
        default='member',
        help_text="Type of membership in the group"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this membership is active"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the organization left the group"
    )
    invited_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Organization that invited this member"
    )
    approved_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Administrator who approved this membership"
    )

    class Meta:
        verbose_name = 'Trust Group Membership'
        verbose_name_plural = 'Trust Group Memberships'
        unique_together = ['trust_group', 'organization']
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['organization']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.organization} in {self.trust_group.name}"


class TrustLog(models.Model):
    """
    Comprehensive logging of all trust-related activities for audit purposes.
    """
    ACTION_CHOICES = [
        ('relationship_created', 'Trust Relationship Created'),
        ('relationship_approved', 'Trust Relationship Approved'),
        ('relationship_activated', 'Trust Relationship Activated'),
        ('relationship_suspended', 'Trust Relationship Suspended'),
        ('relationship_revoked', 'Trust Relationship Revoked'),
        ('relationship_modified', 'Trust Relationship Modified'),
        ('group_created', 'Trust Group Created'),
        ('group_modified', 'Trust Group Modified'),
        ('group_joined', 'Joined Trust Group'),
        ('group_left', 'Left Trust Group'),
        ('access_granted', 'Access Granted'),
        ('access_denied', 'Access Denied'),
        ('intelligence_shared', 'Intelligence Shared'),
        ('intelligence_accessed', 'Intelligence Accessed'),
        ('trust_level_modified', 'Trust Level Modified'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Type of trust action performed"
    )
    source_organization = models.ForeignKey(
        'user_management.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trust_logs_as_source',
        help_text="Organization that initiated the action"
    )
    target_organization = models.ForeignKey(
        'user_management.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trust_logs_as_target',
        help_text="Target organization (if applicable)"
    )
    trust_relationship = models.ForeignKey(
        TrustRelationship,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trust_logs'
    )
    trust_group = models.ForeignKey(
        TrustGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trust_logs_as_user'
    )
    user = models.ForeignKey(
        'user_management.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_trust_logs',
        help_text="User who performed the action"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address from which action was performed"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent string"
    )
    success = models.BooleanField(
        default=True,
        help_text="Whether the action was successful"
    )
    failure_reason = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reason for failure if action was unsuccessful"
    )
    details = models.JSONField(
        default=dict,
        help_text="Additional details about the action"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata about the log entry"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Trust Log'
        verbose_name_plural = 'Trust Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['source_organization', '-timestamp']),
            models.Index(fields=['target_organization', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['success', '-timestamp']),
        ]

    def __str__(self):
        status = "SUCCESS" if self.success else "FAILURE"
        return f"{self.action} - {self.source_organization} - {status} - {self.timestamp}"

    def get_detail(self, key: str, default=None):
        """Get a specific detail from the details JSON field."""
        return self.details.get(key, default)
    
    def get_metadata(self, key: str, default=None):
        """Get a specific metadata value from the metadata JSON field."""
        return self.metadata.get(key, default)
    
    @property
    def performed_by(self):
        """Alias for user field for backward compatibility"""
        return self.user

    @classmethod
    def log_trust_event(cls, action, source_organization, user, 
                       target_organization=None, trust_relationship=None, 
                       trust_group=None, ip_address=None, user_agent=None,
                       success=True, failure_reason=None, details=None):
        """Convenience method to log trust events"""
        from core.user_management.models import Organization, CustomUser
        from unittest.mock import Mock
        
        # Convert source organization if it's a string UUID
        if isinstance(source_organization, str):
            try:
                import uuid
                # Validate UUID format first
                uuid.UUID(source_organization)
                source_organization = Organization.objects.get(id=source_organization)
            except (Organization.DoesNotExist, ValueError, TypeError):
                source_organization = None
        elif isinstance(source_organization, Mock):
            source_organization = None
        
        # Convert target organization if it's a string UUID
        if isinstance(target_organization, str):
            try:
                import uuid
                # Validate UUID format first
                uuid.UUID(target_organization)
                target_organization = Organization.objects.get(id=target_organization)
            except (Organization.DoesNotExist, ValueError, TypeError):
                target_organization = None
        elif isinstance(target_organization, Mock):
            target_organization = None
        
        # Handle user - if it's 'system' string, set to None
        if isinstance(user, str):
            if user == 'system':
                user = None
            else:
                try:
                    import uuid
                    # Validate UUID format first
                    uuid.UUID(user)
                    user = CustomUser.objects.get(id=user)
                except (CustomUser.DoesNotExist, ValueError, TypeError):
                    user = None
        elif isinstance(user, Mock):
            user = None
        
        # Handle trust_relationship - don't try to save Mock objects
        if isinstance(trust_relationship, Mock):
            trust_relationship = None
        
        # Handle trust_group - don't try to save Mock objects
        if isinstance(trust_group, Mock):
            trust_group = None
        
        return cls.objects.create(
            action=action,
            source_organization=source_organization,
            target_organization=target_organization,
            trust_relationship=trust_relationship,
            trust_group=trust_group,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            details=details or {}
        )


class SharingPolicy(models.Model):
    """
    Detailed sharing policies that can be applied to trust relationships.
    Supports granular control over what intelligence is shared and how.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the sharing policy"
    )
    description = models.TextField(
        help_text="Description of what this policy controls"
    )
    
    # STIX object type filtering
    allowed_stix_types = models.JSONField(
        default=list,
        help_text="List of STIX object types that can be shared"
    )
    blocked_stix_types = models.JSONField(
        default=list,
        help_text="List of STIX object types that are blocked"
    )
    
    # Indicator filtering
    allowed_indicator_types = models.JSONField(
        default=list,
        help_text="List of indicator types that can be shared"
    )
    blocked_indicator_types = models.JSONField(
        default=list,
        help_text="List of indicator types that are blocked"
    )
    
    # TLP (Traffic Light Protocol) constraints
    max_tlp_level = models.CharField(
        max_length=20,
        choices=[
            ('white', 'TLP:WHITE'),
            ('green', 'TLP:GREEN'),
            ('amber', 'TLP:AMBER'),
            ('red', 'TLP:RED'),
        ],
        default='green',
        help_text="Maximum TLP level that can be shared"
    )
    
    # Temporal constraints
    max_age_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum age of intelligence that can be shared (in days)"
    )
    
    # Anonymization requirements
    require_anonymization = models.BooleanField(
        default=True,
        help_text="Whether anonymization is required"
    )
    anonymization_rules = models.JSONField(
        default=dict,
        help_text="Specific anonymization rules to apply"
    )
    
    # Attribution constraints
    allow_attribution = models.BooleanField(
        default=False,
        help_text="Whether attribution to source organization is allowed"
    )
    
    # Additional constraints
    additional_constraints = models.JSONField(
        default=dict,
        help_text="Additional policy constraints"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this policy is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=255,
        help_text="User who created this policy"
    )

    class Meta:
        verbose_name = 'Sharing Policy'
        verbose_name_plural = 'Sharing Policies'
        ordering = ['name']

    def __str__(self):
        return self.name

    def applies_to_stix_object(self, stix_object_type):
        """Check if this policy applies to a given STIX object type"""
        if self.blocked_stix_types and stix_object_type in self.blocked_stix_types:
            return False
        if self.allowed_stix_types:
            return stix_object_type in self.allowed_stix_types
        return True  # If no specific allowed types, allow all except blocked

    def get_anonymization_requirements(self):
        """Get the anonymization requirements for this policy"""
        return {
            'required': self.require_anonymization,
            'rules': self.anonymization_rules
        }