import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


USER_ROLE_CHOICES = [
    ('viewer', 'Viewer'),
    ('publisher', 'Publisher'),
    ('BlueVisionAdmin', 'BlueVision Admin'),
]

PERMISSION_CHOICES = [
    ('read', 'Read'),
    ('write', 'Write'),
    ('admin', 'Admin'),
]


class Organization(models.Model):
    """
    Organization model for CRISP platform
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Organization name"
    )
    description = models.TextField(
        blank=True,
        help_text="Organization description"
    )
    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Organization email domain"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether organization is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Extended User model following CRISP domain specifications.
    Integrates with existing Organization model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'UserManagement.Organization', 
        on_delete=models.CASCADE, 
        related_name='users',
        help_text="Organization this user belongs to"
    )
    role = models.CharField(
        max_length=50, 
        choices=USER_ROLE_CHOICES,
        default='viewer',
        help_text="User's role within the organization"
    )
    is_publisher = models.BooleanField(
        default=False,
        help_text="Whether user can publish threat intelligence feeds"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether user account has been verified by admin"
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    last_failed_login = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp of last failed login attempt"
    )
    account_locked_until = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Account locked until this timestamp"
    )
    password_reset_token = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Token for password reset"
    )
    password_reset_expires = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Expiration time for password reset token"
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        help_text="Whether two-factor authentication is enabled"
    )
    trusted_devices = models.JSONField(
        default=list,
        help_text="List of trusted device fingerprints"
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of last successful login"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CRISP User'
        verbose_name_plural = 'CRISP Users'
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.organization.name})"

    @property
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False

    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])

    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])

    def increment_failed_login(self):
        """Increment failed login attempts and lock if threshold reached"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        if self.failed_login_attempts >= 5:
            self.lock_account()
        
        self.save(update_fields=['failed_login_attempts', 'last_failed_login'])

    def reset_failed_login_attempts(self):
        """Reset failed login attempts on successful login"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.save(update_fields=['failed_login_attempts', 'last_failed_login'])

    def can_publish_feeds(self):
        """Check if user can publish threat intelligence feeds"""
        return self.is_publisher and self.role in ['publisher', 'BlueVisionAdmin']

    def is_organization_admin(self):
        """Check if user is admin within their organization"""
        return self.role == 'BlueVisionAdmin'


class UserSession(models.Model):
    """
    Track user sessions and JWT tokens for security.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='sessions'
    )
    session_token = models.CharField(
        max_length=500, 
        unique=True,
        help_text="JWT access token"
    )
    refresh_token = models.CharField(
        max_length=500, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="JWT refresh token"
    )
    device_info = models.JSONField(
        default=dict,
        help_text="Browser and device information"
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the session"
    )
    is_trusted_device = models.BooleanField(
        default=False,
        help_text="Whether this is a trusted device"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this session expires"
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether session is still active"
    )

    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Session for {self.user.username} from {self.ip_address}"

    @property
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at

    def deactivate(self):
        """Deactivate this session"""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def extend_session(self, hours=1):
        """Extend session expiration"""
        self.expires_at = timezone.now() + timedelta(hours=hours)
        self.save(update_fields=['expires_at'])


class AuthenticationLog(models.Model):
    """
    Comprehensive authentication activity logging.
    """
    ACTION_CHOICES = [
        ('login_success', 'Login Success'),
        ('login_failed', 'Login Failed'),
        ('logout', 'Logout'),
        ('password_reset', 'Password Reset'),
        ('password_reset_confirm', 'Password Reset Confirmed'),
        ('password_changed', 'Password Changed'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('token_refresh', 'Token Refresh'),
        ('trusted_device_added', 'Trusted Device Added'),
        ('trusted_device_removed', 'Trusted Device Removed'),
        ('session_expired', 'Session Expired'),
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='auth_logs', 
        null=True, 
        blank=True,
        help_text="User associated with this log entry"
    )
    username = models.CharField(
        max_length=150,
        help_text="Username (stored even if user is deleted)"
    )
    action = models.CharField(
        max_length=50, 
        choices=ACTION_CHOICES,
        help_text="Type of authentication action"
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address from which action was performed"
    )
    user_agent = models.TextField(
        help_text="Browser/client user agent string"
    )
    success = models.BooleanField(
        help_text="Whether the action was successful"
    )
    failure_reason = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Reason for failure if action was unsuccessful"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When this action occurred"
    )
    additional_data = models.JSONField(
        default=dict,
        help_text="Additional context data for the action"
    )

    class Meta:
        verbose_name = 'Authentication Log'
        verbose_name_plural = 'Authentication Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['success', '-timestamp']),
        ]

    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"{self.action} - {self.username} - {status} - {self.timestamp}"

    @classmethod
    def log_authentication_event(cls, user, action, ip_address, user_agent, 
                                success=True, failure_reason=None, additional_data=None):
        """
        Convenience method to log authentication events
        """
        return cls.objects.create(
            user=user,
            username=user.username if user else 'unknown',
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            additional_data=additional_data or {}
        )


class STIXObjectPermission(models.Model):
    """
    Permissions for STIX objects based on user roles and organization trust.
    Integrates with existing STIXObject model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='stix_permissions'
    )
    stix_object_id = models.UUIDField(
        help_text="ID of the STIX object (references crisp_threat_intel.STIXObject)"
    )
    permission_level = models.CharField(
        max_length=20, 
        choices=PERMISSION_CHOICES,
        help_text="Level of permission for this STIX object"
    )
    granted_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='granted_permissions',
        help_text="User who granted this permission"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this permission expires (null = never)"
    )

    class Meta:
        verbose_name = 'STIX Object Permission'
        verbose_name_plural = 'STIX Object Permissions'
        unique_together = ['user', 'stix_object_id']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.permission_level} - {self.stix_object_id}"

    @property
    def is_expired(self):
        """Check if permission is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False