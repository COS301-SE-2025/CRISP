import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import json


USER_ROLE_CHOICES = [
    ('viewer', 'Viewer'),
    ('publisher', 'Publisher'),
    ('BlueVisionAdmin', 'BlueVision Administrator'),
]

ORGANIZATION_TYPE_CHOICES = [
    ('educational', 'Educational'),
    ('government', 'Government'),
    ('private', 'Private'),
]


class CustomUserManager(BaseUserManager):
    """Custom user manager for CustomUser model"""
    
    def create_user(self, username, email, password=None, organization=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, organization=organization, **extra_fields)
        
        if password:
            user.set_password(password)  # This properly hashes the password
        
        user.save(using=self._db)
        
        # Force reload to ensure password is properly set
        user.refresh_from_db()
        return user
    
    def create_superuser(self, username, email, password=None, organization=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        return self.create_user(username, email, password, organization, **extra_fields)


class Organization(models.Model):
    """
    Organization model representing institutions in the CRISP platform.
    Integrates with trust management system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the organization"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the organization"
    )
    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Organization's domain (e.g., university.edu)"
    )
    contact_email = models.EmailField(
        help_text="Primary contact email for the organization"
    )
    website = models.URLField(
        blank=True,
        help_text="Organization's website URL"
    )
    organization_type = models.CharField(
        max_length=100,
        choices=ORGANIZATION_TYPE_CHOICES,
        default='educational',
        help_text="Type of organization (educational, government, private)"
    )
    
    # Institution-specific fields for threat intelligence
    is_publisher = models.BooleanField(
        default=False,
        help_text="Whether this organization can publish threat intelligence"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this organization is verified"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this organization is active"
    )
    
    # Trust-related metadata
    trust_metadata = models.JSONField(default=dict, blank=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="User who created this organization"
    )

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_publisher']),
            models.Index(fields=['organization_type']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name:
            raise ValidationError("Organization name is required")
        if not self.domain:
            raise ValidationError("Organization domain is required")

    @property
    def user_count(self):
        """Get the number of users in this organization"""
        return self.users.filter(is_active=True).count()

    @property
    def publisher_count(self):
        """Get the number of publishers in this organization"""
        return self.users.filter(is_active=True, is_publisher=True).count()

    def can_publish_threat_intelligence(self):
        """Check if organization can publish threat intelligence"""
        return self.is_active and self.is_verified and self.is_publisher

    def get_trust_relationships(self):
        """Get trust relationships involving this organization"""
        from core.trust.models import TrustRelationship
        return TrustRelationship.objects.filter(
            models.Q(source_organization=str(self.id)) |
            models.Q(target_organization=str(self.id))
        )


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Supports role-based access control and trust-aware operations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    objects = CustomUserManager()
    
    # Organization relationship
    organization = models.ForeignKey(
        'Organization', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='users'
    )
    
    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=USER_ROLE_CHOICES,
        default='viewer',
        help_text="User's role in the system"
    )
    is_publisher = models.BooleanField(
        default=False,
        help_text="Whether user can publish threat intelligence"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether user account is verified"
    )
    
    # Security fields
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When account lock expires"
    )
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When password was last changed"
    )
    
    # Two-factor authentication
    two_factor_enabled = models.BooleanField(
        default=False,
        help_text="Whether two-factor authentication is enabled"
    )
    two_factor_secret = models.CharField(
        max_length=32,
        blank=True,
        help_text="Secret for two-factor authentication"
    )
    
    # Trusted devices
    trusted_devices = models.JSONField(
        default=list,
        blank=True,
        help_text="List of trusted device fingerprints"
    )
    
    # User preferences
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences and settings"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional user metadata"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['organization']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def clean(self):
        """Validate user data"""
        super().clean()
        errors = {}
        
        # Only validate organization if the user instance has been saved or organization is set
        # Skip organization requirement for superusers and BlueVisionAdmin
        if (self.pk or hasattr(self, '_organization_id') or self.organization_id) and not (self.is_superuser or self.role == 'BlueVisionAdmin'):
            try:
                if not self.organization:
                    errors['organization'] = ValidationError("User must belong to an organization")
            except self.organization.RelatedObjectDoesNotExist:
                errors['organization'] = ValidationError("User must belong to an organization")
        
        # Email validation
        if self.email:
            # Check for duplicate emails
            if CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists():
                errors['email'] = ValidationError("Email address is already in use")
            
            # Validate email format more strictly
            if '@' not in self.email or '.' not in self.email.split('@')[-1]:
                errors['email'] = ValidationError("Invalid email format")
        
        # Username validation
        if self.username:
            # Check for duplicate usernames
            if CustomUser.objects.filter(username=self.username).exclude(pk=self.pk).exists():
                errors['username'] = ValidationError("Username is already taken")
            
            # Additional username format validation
            if len(self.username) < 3:
                errors['username'] = ValidationError("Username must be at least 3 characters long")
        
        # Role validation
        valid_roles = ['viewer', 'publisher', 'BlueVisionAdmin']
        if self.role and self.role not in valid_roles:
            errors['role'] = ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        if errors:
            raise ValidationError(errors)

    @property
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False

    @property
    def is_bluevision_admin(self):
        """Check if user is a BlueVision administrator"""
        return self.role == 'BlueVisionAdmin'

    @property
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role in ['publisher', 'BlueVisionAdmin']

    @property
    def can_manage_trust_relationships(self):
        """Check if user can manage trust relationships"""
        # Allow override for testing
        if hasattr(self, '_can_manage_trust_relationships_override'):
            return self._can_manage_trust_relationships_override
        return self.role in ['publisher', 'BlueVisionAdmin']
    
    @can_manage_trust_relationships.setter
    def can_manage_trust_relationships(self, value):
        """Setter for testing purposes"""
        self._can_manage_trust_relationships_override = value

    def lock_account(self, duration_minutes=15):
        """Lock user account for specified duration"""
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])

    def unlock_account(self):
        """Unlock user account"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])

    def add_trusted_device(self, device_fingerprint, device_name=None):
        """Add a trusted device"""
        device_info = {
            'fingerprint': device_fingerprint,
            'name': device_name or 'Unknown Device',
            'added_at': timezone.now().isoformat()
        }
        
        # Remove if already exists
        self.trusted_devices = [
            d for d in self.trusted_devices 
            if d.get('fingerprint') != device_fingerprint
        ]
        
        # Add new device
        self.trusted_devices.append(device_info)
        self.save(update_fields=['trusted_devices'])

    def remove_trusted_device(self, device_fingerprint):
        """Remove a trusted device"""
        self.trusted_devices = [
            d for d in self.trusted_devices 
            if d.get('fingerprint') != device_fingerprint
        ]
        self.save(update_fields=['trusted_devices'])

    def is_device_trusted(self, device_fingerprint):
        """Check if device is trusted"""
        return any(
            d.get('fingerprint') == device_fingerprint 
            for d in self.trusted_devices
        )

    def can_access_organization_data(self, organization_id):
        """Check if user can access data from specified organization"""
        # Users can always access their own organization data
        if str(self.organization.id) == str(organization_id):
            return True
        
        # BlueVision admins can access all organization data
        if self.is_bluevision_admin:
            return True
        
        # Check trust relationships for other organizations
        from core.trust.services.trust_service import TrustService
        trust_service = TrustService()
        return trust_service.can_access_organization_data(
            str(self.organization.id), 
            str(organization_id)
        )

    def get_accessible_organizations(self):
        """Get list of organizations this user can access"""
        accessible = [self.organization]
        
        if self.is_bluevision_admin:
            accessible.extend(Organization.objects.exclude(id=self.organization.id))
        else:
            # Get organizations through trust relationships
            from core.trust.services.trust_service import TrustService
            trust_service = TrustService()
            trusted_org_ids = trust_service.get_accessible_organizations(
                str(self.organization.id)
            )
            accessible.extend(
                Organization.objects.filter(id__in=trusted_org_ids)
            )
        
        return accessible

    def save(self, *args, **kwargs):
        """Override save to handle password hashing and set defaults."""
        # Hash password if it's not already hashed
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.set_password(self.password)
        
        # Set defaults for required fields if they're empty
        if not self.trusted_devices:
            self.trusted_devices = {}
        if not self.preferences:
            self.preferences = {}
        if not self.metadata:
            self.metadata = {}
            
        # Set flag to skip signal processing during save
        self._signal_skip = True
        
        super().save(*args, **kwargs)
        
        # Remove flag after save
        if hasattr(self, '_signal_skip'):
            delattr(self, '_signal_skip')
    
    # ...rest of existing methods...

class AuthenticationLog(models.Model):
    """
    Comprehensive logging of authentication events for audit purposes.
    """
    ACTION_CHOICES = [
        ('login_success', 'Login Success'),
        ('login_failure', 'Login Failure'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('user_created', 'User Created'),
        ('user_modified', 'User Modified'),
        ('user_deactivated', 'User Deactivated'),
        ('two_factor_enabled', 'Two-Factor Enabled'),
        ('two_factor_disabled', 'Two-Factor Disabled'),
        ('trusted_device_added', 'Trusted Device Added'),
        ('trusted_device_removed', 'Trusted Device Removed'),
        ('token_refresh', 'Token Refresh'),
        ('session_expired', 'Session Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authentication_logs'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Type of authentication action"
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
    additional_data = models.JSONField(
        default=dict,
        help_text="Additional data about the authentication event"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Authentication Log'
        verbose_name_plural = 'Authentication Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['success', '-timestamp']),
        ]

    def __str__(self):
        username = self.user.username if self.user else 'Unknown'
        status = "SUCCESS" if self.success else "FAILURE"
        return f"{self.action} - {username} - {status} - {self.timestamp}"

    @classmethod
    def log_authentication_event(cls, user, action, ip_address=None, user_agent=None,
                                success=True, failure_reason=None, additional_data=None):
        """Convenience method to log authentication events"""
        return cls.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            additional_data=additional_data or {}
        )


class UserSession(models.Model):
    """
    Track active user sessions for security and management purposes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_token = models.TextField(
        help_text="JWT session token"
    )
    refresh_token = models.TextField(
        help_text="JWT refresh token"
    )
    device_info = models.JSONField(
        default=dict,
        help_text="Information about the device/browser"
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the session"
    )
    is_trusted_device = models.BooleanField(
        default=False,
        help_text="Whether this is a trusted device"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this session is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this session expires"
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )

    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

    @property
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at

    @property
    def time_remaining(self):
        """Get time remaining before session expires"""
        if self.is_expired:
            return timedelta(0)
        return self.expires_at - timezone.now()

    def deactivate(self):
        """Deactivate this session"""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def extend_session(self, duration=None):
        """Extend session expiration time"""
        if duration is None:
            from django.conf import settings
            duration = getattr(settings, 'SESSION_COOKIE_AGE', 3600)  # 1 hour default
        
        self.expires_at = timezone.now() + timedelta(seconds=duration)
        self.save(update_fields=['expires_at'])


class UserProfile(models.Model):
    """
    Extended user profile information and preferences.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.URLField(
        null=True,
        blank=True,
        help_text="URL to user's avatar image"
    )
    bio = models.TextField(
        blank=True,
        help_text="User's biography"
    )
    department = models.CharField(
        max_length=255,
        blank=True,
        help_text="User's department within organization"
    )
    job_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="User's job title"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="User's phone number"
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text="Whether to receive email notifications"
    )
    threat_alerts = models.BooleanField(
        default=True,
        help_text="Whether to receive threat intelligence alerts"
    )
    security_notifications = models.BooleanField(
        default=True,
        help_text="Whether to receive security notifications"
    )
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private'),
            ('organization', 'Organization Only'),
            ('trusted', 'Trusted Organizations'),
            ('public', 'Public'),
        ],
        default='organization',
        help_text="Who can see this profile"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} Profile"


class TrustedDevice(models.Model):
    """
    Model for managing trusted devices per user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    device_fingerprint = models.CharField(
        max_length=255,
        help_text="Unique device fingerprint"
    )
    device_name = models.CharField(
        max_length=255,
        help_text="Human-readable device name"
    )
    device_type = models.CharField(
        max_length=50,
        choices=[
            ('desktop', 'Desktop'),
            ('laptop', 'Laptop'),
            ('tablet', 'Tablet'),
            ('mobile', 'Mobile'),
            ('unknown', 'Unknown'),
        ],
        default='unknown',
        help_text="Type of device"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this device is currently trusted"
    )
    last_used = models.DateTimeField(
        auto_now=True,
        help_text="When this device was last used"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When trust for this device expires"
    )

    class Meta:
        verbose_name = 'Trusted Device'
        verbose_name_plural = 'Trusted Devices'
        unique_together = ['user', 'device_fingerprint']
        ordering = ['-last_used']

    def __str__(self):
        return f"{self.user.username} - {self.device_name}"

    @property
    def is_expired(self):
        """Check if device trust is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def revoke_trust(self):
        """Revoke trust for this device"""
        self.is_active = False
        self.save(update_fields=['is_active'])