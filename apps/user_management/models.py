"""
Integrated User Management Models for CRISP
Combines user management with trust management requirements
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class Organization(models.Model):
    """Organization model that integrates with Trust Management"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField()
    
    # Institution-specific fields from SRS
    institution_type = models.CharField(
        max_length=100, 
        choices=[
            ('university', 'University'),
            ('college', 'College'),
            ('school', 'School'),
            ('research_institute', 'Research Institute'),
            ('other', 'Other Educational Institution')
        ],
        default='university'
    )
    
    # Trust-related fields
    trust_level_default = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('trusted', 'Trusted'),
            ('restricted', 'Restricted')
        ],
        default='public'
    )
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # BlueVision specific fields
    is_bluevision_client = models.BooleanField(default=True)
    client_since = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_active_users_count(self):
        """Get count of active users in this organization"""
        return self.users.filter(is_active=True).count()


class CustomUser(AbstractUser):
    """
    Extended user model with organization integration and role-based access
    Implements SRS requirements for user roles and authentication
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    # Organization relationship
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    
    # Role-based access control from SRS
    ROLE_CHOICES = [
        ('viewer', 'Institution User (Viewer)'),
        ('publisher', 'Institution Publisher'),
        ('system_admin', 'System Administrator'),
        ('bluevision_admin', 'BlueVision ITM Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    is_organization_admin = models.BooleanField(default=False)
    
    # Additional user fields
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Security fields
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Consent and terms
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_date = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']
    
    def __str__(self):
        return f"{self.email} ({self.organization.name if self.organization else 'No Org'})"
    
    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_publisher(self):
        """Check if user has publisher role"""
        return self.role in ['publisher', 'system_admin', 'bluevision_admin']
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role in ['system_admin', 'bluevision_admin']
    
    def can_publish_intelligence(self):
        """Check if user can publish threat intelligence"""
        return self.is_publisher() and self.is_active
    
    def can_manage_organization(self):
        """Check if user can manage their organization"""
        return self.is_organization_admin or self.is_admin()


class UserSession(models.Model):
    """Track user sessions for security and audit purposes"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session for {self.user.email} from {self.ip_address}"
    
    def is_expired(self):
        """Check if session is expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at


class AuthenticationLog(models.Model):
    """Log authentication events for security monitoring"""
    
    ACTION_CHOICES = [
        ('login_success', 'Successful Login'),
        ('login_failed', 'Failed Login'),
        ('logout', 'Logout'),
        ('password_reset', 'Password Reset'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='auth_logs', null=True, blank=True)
    email = models.EmailField()  # Store email even if user doesn't exist
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'authentication_logs'
        verbose_name = 'Authentication Log'
        verbose_name_plural = 'Authentication Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} for {self.email} at {self.created_at}"


class InvitationToken(models.Model):
    """Token-based user invitation system"""
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_invitations')
    
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=CustomUser.ROLE_CHOICES, default='viewer')
    
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='used_invitations', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invitation_tokens'
        verbose_name = 'Invitation Token'
        verbose_name_plural = 'Invitation Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation for {self.email} to {self.organization.name}"
    
    def is_expired(self):
        """Check if invitation is expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if invitation is still valid"""
        return not self.used and not self.is_expired()
