"""
Trust Management Models for CRISP Integration
Simplified models that integrate with User Management
"""
from django.db import models
import uuid


class TrustLevel(models.Model):
    """Trust levels for organization relationships"""
    
    name = models.CharField(max_length=100, unique=True)
    
    LEVEL_CHOICES = [
        ('public', 'Public'),
        ('trusted', 'Trusted'),
        ('restricted', 'Restricted'),
    ]
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    numerical_value = models.IntegerField(help_text="Numerical value (0-100) for comparison")
    
    description = models.TextField()
    
    # Anonymization settings
    ANONYMIZATION_CHOICES = [
        ('full', 'Full Anonymization'),
        ('partial', 'Partial Anonymization'),
        ('minimal', 'Minimal Anonymization'),
    ]
    
    default_anonymization_level = models.CharField(
        max_length=20,
        choices=ANONYMIZATION_CHOICES,
        default='full'
    )
    
    # Access settings
    ACCESS_CHOICES = [
        ('read', 'Read Only'),
        ('contribute', 'Contribute'),
        ('admin', 'Administrative'),
    ]
    
    default_access_level = models.CharField(
        max_length=20,
        choices=ACCESS_CHOICES,
        default='read'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_system_default = models.BooleanField(default=False)
    
    # Audit
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trust_levels'
        verbose_name = 'Trust Level'
        verbose_name_plural = 'Trust Levels'
        ordering = ['numerical_value']
    
    def __str__(self):
        return f"{self.name} ({self.level})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not (0 <= self.numerical_value <= 100):
            raise ValidationError('Numerical value must be between 0 and 100')


class TrustRelationship(models.Model):
    """Trust relationships between organizations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Organization references (using UUIDs to match Organization model)
    source_organization = models.UUIDField(help_text="UUID of source organization")
    target_organization = models.UUIDField(help_text="UUID of target organization")
    
    # Trust settings
    trust_level = models.ForeignKey(TrustLevel, on_delete=models.CASCADE)
    
    RELATIONSHIP_CHOICES = [
        ('bilateral', 'Bilateral'),
        ('community', 'Community'),
        ('hierarchical', 'Hierarchical'),
        ('federation', 'Federation'),
    ]
    
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default='bilateral'
    )
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Validity period
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Approval tracking
    approved_by_source = models.BooleanField(default=False)
    approved_by_target = models.BooleanField(default=False)
    
    # Audit fields
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=100)
    last_modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trust_relationships'
        verbose_name = 'Trust Relationship'
        verbose_name_plural = 'Trust Relationships'
        unique_together = ['source_organization', 'target_organization']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Trust: {self.source_organization} -> {self.target_organization} ({self.trust_level})"
    
    def is_effective(self):
        """Check if relationship is currently effective"""
        from django.utils import timezone
        now = timezone.now()
        
        return (
            self.status == 'active' and
            self.is_fully_approved() and
            self.valid_from <= now and
            (self.valid_until is None or self.valid_until >= now)
        )
    
    def is_fully_approved(self):
        """Check if relationship is approved by all parties"""
        if self.relationship_type == 'community':
            return self.approved_by_source
        return self.approved_by_source and self.approved_by_target
    
    def approve(self, approving_org=None, user=None):
        """Approve relationship from organization's side"""
        if str(approving_org) == str(self.source_organization):
            self.approved_by_source = True
        elif str(approving_org) == str(self.target_organization):
            self.approved_by_target = True
        
        if user:
            self.last_modified_by = user
        
        # Auto-activate if fully approved
        if self.is_fully_approved():
            self.status = 'active'
        
        self.save()


class TrustGroup(models.Model):
    """Trust groups for community-based relationships"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    GROUP_CHOICES = [
        ('sector', 'Sector-based'),
        ('region', 'Region-based'),
        ('community', 'Community'),
        ('custom', 'Custom'),
    ]
    
    group_type = models.CharField(max_length=20, choices=GROUP_CHOICES, default='community')
    
    # Access settings
    is_public = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    
    # Default trust settings
    default_trust_level = models.ForeignKey(TrustLevel, on_delete=models.CASCADE)
    
    # Administrators (stored as JSON list of organization UUIDs)
    administrators = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trust_groups'
        verbose_name = 'Trust Group'
        verbose_name_plural = 'Trust Groups'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.group_type})"
    
    def can_administer(self, organization_id):
        """Check if organization can administer this group"""
        return str(organization_id) in self.administrators


class TrustGroupMembership(models.Model):
    """Organization membership in trust groups"""
    
    trust_group = models.ForeignKey(TrustGroup, on_delete=models.CASCADE, related_name='memberships')
    organization = models.UUIDField(help_text="UUID of member organization")
    
    MEMBERSHIP_CHOICES = [
        ('member', 'Member'),
        ('administrator', 'Administrator'),
        ('moderator', 'Moderator'),
    ]
    
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='member')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    # Invitation tracking
    invited_by = models.UUIDField(null=True, blank=True, help_text="UUID of inviting organization")
    approved_by = models.UUIDField(null=True, blank=True, help_text="UUID of approving organization")
    
    class Meta:
        db_table = 'trust_group_memberships'
        verbose_name = 'Trust Group Membership'
        verbose_name_plural = 'Trust Group Memberships'
        unique_together = ['trust_group', 'organization']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.organization} in {self.trust_group.name}"


class TrustLog(models.Model):
    """Audit log for trust-related actions"""
    
    ACTION_CHOICES = [
        ('relationship_created', 'Relationship Created'),
        ('relationship_approved', 'Relationship Approved'),
        ('relationship_denied', 'Relationship Denied'),
        ('relationship_revoked', 'Relationship Revoked'),
        ('relationship_suspended', 'Relationship Suspended'),
        ('group_created', 'Group Created'),
        ('group_joined', 'Group Joined'),
        ('group_left', 'Group Left'),
        ('access_granted', 'Access Granted'),
        ('access_denied', 'Access Denied'),
        ('trust_level_changed', 'Trust Level Changed'),
    ]
    
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    
    # Related objects
    source_organization = models.UUIDField(null=True, blank=True)
    target_organization = models.UUIDField(null=True, blank=True)
    trust_relationship = models.ForeignKey(TrustRelationship, on_delete=models.CASCADE, null=True, blank=True)
    trust_group = models.ForeignKey(TrustGroup, on_delete=models.CASCADE, null=True, blank=True)
    
    # Request context
    user = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    # Result
    success = models.BooleanField(default=True)
    
    # Additional data
    details = models.JSONField(default=dict)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trust_logs'
        verbose_name = 'Trust Log'
        verbose_name_plural = 'Trust Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} by {self.user} at {self.created_at}"
