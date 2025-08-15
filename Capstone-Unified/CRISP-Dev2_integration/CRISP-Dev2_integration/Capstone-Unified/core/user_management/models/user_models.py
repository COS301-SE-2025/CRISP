"""
User management models that extend the core CRISP models.
These models provide additional functionality for user invitations,
authentication logging, and session management.
"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

# Import the main models from core to avoid conflicts
from core.models.models import CustomUser, Organization


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