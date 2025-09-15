"""
User management models that extend the core CRISP models.
These models provide additional functionality for user invitations,
authentication logging, and session management.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

# User and Organization choices
USER_ROLE_CHOICES = [
    ('viewer', 'Viewer'),
    ('publisher', 'Publisher'),
    ('BlueVisionAdmin', 'BlueVision Administrator'),
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
        extra_fields.setdefault('role', 'BlueVisionAdmin')
        
        return self.create_user(username, email, password, organization, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Supports role-based access control and trust-aware operations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    objects = CustomUserManager()
    
    # Organization relationship (using core.Organization model)
    organization = models.ForeignKey(
        'core.Organization', 
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
        return self.role in ['publisher', 'BlueVisionAdmin']

    def lock_account(self, duration_minutes=15):
        """Lock user account for specified duration"""
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])

    def unlock_account(self):
        """Unlock user account"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])

    def save(self, *args, **kwargs):
        """Override save to handle password hashing and set defaults."""
        # Set defaults for required fields if they're empty
        if not self.trusted_devices:
            self.trusted_devices = []
        if not self.preferences:
            self.preferences = {}
        if not self.metadata:
            self.metadata = {}
            
        super().save(*args, **kwargs)


# Import Organization model from core for convenience
from core.models.models import Organization


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
        related_name='user_mgmt_authentication_logs'
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
        related_name='user_management_sessions'
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


class TrustedDevice(models.Model):
    """
    Model for managing trusted devices per user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='trusted_devices_list'
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