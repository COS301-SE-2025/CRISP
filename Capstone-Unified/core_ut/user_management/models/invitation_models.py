"""
User Invitation Models
File: core/user_management/models/invitation_models.py

Models for managing user invitations to organizations.
"""

import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class UserInvitation(models.Model):
    """
    Model to track user invitations to organizations (SRS R1.2.2)
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('publisher', 'Publisher'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, help_text="Email address of the invitee")
    organization = models.ForeignKey(
        'ut_user_management.Organization', 
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text="Organization extending the invitation"
    )
    inviter = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        help_text="User who sent the invitation"
    )
    invited_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        help_text="Role the invitee will have in the organization"
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        help_text="Secure token for invitation acceptance"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the invitation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this invitation expires"
    )
    accepted_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the invitation was accepted"
    )
    accepted_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='accepted_invitations',
        help_text="User who accepted the invitation"
    )
    message = models.TextField(
        blank=True,
        help_text="Optional message from the inviter"
    )
    
    class Meta:
        db_table = 'user_invitations'
        verbose_name = 'User Invitation'
        verbose_name_plural = 'User Invitations'
        unique_together = [('email', 'organization', 'status')]  # Prevent duplicate pending invitations
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.organization.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Set expiration date if not provided (7 days from creation)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if the invitation has expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_pending(self):
        """Check if the invitation is still pending"""
        return self.status == 'pending' and not self.is_expired
    
    def expire(self):
        """Mark invitation as expired"""
        self.status = 'expired'
        self.save(update_fields=['status'])
    
    def cancel(self):
        """Cancel the invitation"""
        self.status = 'cancelled'
        self.save(update_fields=['status'])
    
    def accept(self, user):
        """Accept the invitation"""
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.accepted_by = user
        self.save(update_fields=['status', 'accepted_at', 'accepted_by'])


class PasswordResetToken(models.Model):
    """
    Model to track password reset tokens (SRS R1.1.3)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        help_text="User requesting password reset"
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        help_text="Secure reset token"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this token expires"
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the token was used"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address that requested the reset"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent of the request"
    )
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        indexes = [
            models.Index(fields=['user', 'expires_at']),
            models.Index(fields=['token']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Password reset token for {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Set expiration date if not provided (24 hours from creation)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_used(self):
        """Check if the token has been used"""
        return self.used_at is not None
    
    @property
    def is_valid(self):
        """Check if the token is valid (not expired and not used)"""
        return not self.is_expired and not self.is_used
    
    def mark_as_used(self):
        """Mark the token as used"""
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])