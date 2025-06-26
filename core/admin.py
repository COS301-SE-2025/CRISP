"""
CRISP Core Admin Configuration

Unified admin interface for all CRISP components integrated into core.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db.models import Count
from django.contrib.admin import SimpleListFilter

# Core models
from core.models.threat_feed import ThreatFeed
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData
from core.models.stix_object import STIXObject, Collection, Feed, Identity

# User management models
from core.models.auth import CustomUser, UserSession, AuthenticationLog, STIXObjectPermission, Organization

# Trust management models
from core.models.trust_models.models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership,
    TrustLog, SharingPolicy
)


# === USER MANAGEMENT ADMIN ===

class AccountStatusFilter(SimpleListFilter):
    """Filter for account status"""
    title = 'Account Status'
    parameter_name = 'account_status'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('locked', 'Locked'),
            ('unverified', 'Unverified'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True, is_verified=True, account_locked_until__isnull=True)
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)
        elif self.value() == 'locked':
            return queryset.filter(account_locked_until__gt=timezone.now())
        elif self.value() == 'unverified':
            return queryset.filter(is_verified=False)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for Organization"""
    
    list_display = [
        'name', 'domain', 'user_count', 'is_active', 'created_at_display'
    ]
    
    list_filter = [
        'is_active', 'created_at'
    ]
    
    search_fields = [
        'name', 'domain', 'description'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'user_count_display'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'domain')
        }),
        ('STIX Identity', {
            'fields': ('identity_class', 'sectors', 'contact_email', 'website', 'stix_id')
        }),
        ('Details', {
            'fields': ('description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Statistics', {
            'fields': ('user_count_display',)
        })
    )
    
    def user_count(self, obj):
        """Display user count for organization"""
        return obj.users.count()
    user_count.short_description = 'Users'
    
    def user_count_display(self, obj):
        """Display detailed user count"""
        if obj.id:
            total = obj.users.count()
            active = obj.users.filter(is_active=True).count()
            verified = obj.users.filter(is_verified=True).count()
            return f"Total: {total}, Active: {active}, Verified: {verified}"
        return "Save organization first"
    user_count_display.short_description = 'User Statistics'
    
    def created_at_display(self, obj):
        """Display creation time"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = 'Created'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        return super().get_queryset(request).annotate(
            user_count=Count('users')
        )


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin interface for CustomUser"""
    
    list_display = [
        'username', 'email', 'organization', 'role', 'is_verified',
        'account_status_display', 'last_login_display'
    ]
    
    list_filter = [
        AccountStatusFilter, 'role', 'is_verified', 'is_publisher',
        'organization', 'date_joined'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 'organization__name'
    ]
    
    readonly_fields = [
        'id', 'date_joined', 'last_login', 'password', 'last_login_ip',
        'failed_login_attempts', 'last_failed_login', 'account_locked_until'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name')
        }),
        ('Organization & Role', {
            'fields': ('organization', 'role', 'is_publisher')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')
        }),
        ('Security', {
            'fields': (
                'two_factor_enabled', 'trusted_devices', 'last_login_ip',
                'failed_login_attempts', 'last_failed_login', 'account_locked_until'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        })
    )
    
    def account_status_display(self, obj):
        """Display account status with styling"""
        if not obj.is_active:
            return format_html('<span style="color: red;">Inactive</span>')
        elif obj.is_account_locked:
            return format_html('<span style="color: orange;">Locked</span>')
        elif not obj.is_verified:
            return format_html('<span style="color: blue;">Unverified</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')
    account_status_display.short_description = 'Status'
    
    def last_login_display(self, obj):
        """Display last login time"""
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M')
        return 'Never'
    last_login_display.short_description = 'Last Login'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('organization')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for UserSession"""
    
    list_display = [
        'user', 'session_token_short', 'ip_address', 'is_active', 
        'is_trusted_device', 'created_at_display', 'expires_at_display'
    ]
    
    list_filter = [
        'is_active', 'is_trusted_device', 'created_at', 'expires_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'ip_address', 'device_info'
    ]
    
    readonly_fields = [
        'session_token', 'refresh_token', 'created_at', 'expires_at', 'last_activity'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'session_token', 'refresh_token', 'ip_address')
        }),
        ('Device Info', {
            'fields': ('device_info', 'is_trusted_device')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'last_activity')
        })
    )
    
    def session_token_short(self, obj):
        """Display shortened session token"""
        return f"{obj.session_token[:8]}..." if obj.session_token else "None"
    session_token_short.short_description = 'Session Token'
    
    def created_at_display(self, obj):
        """Display creation time"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = 'Created'
    
    def expires_at_display(self, obj):
        """Display expiration time"""
        return obj.expires_at.strftime('%Y-%m-%d %H:%M:%S')
    expires_at_display.short_description = 'Expires'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')


@admin.register(AuthenticationLog)
class AuthenticationLogAdmin(admin.ModelAdmin):
    """Admin interface for AuthenticationLog"""
    
    list_display = [
        'user', 'action', 'success', 'ip_address', 'timestamp_display'
    ]
    
    list_filter = [
        'action', 'success', 'timestamp'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'ip_address', 'user_agent', 'failure_reason'
    ]
    
    readonly_fields = [
        'user', 'action', 'timestamp', 'ip_address', 'user_agent', 
        'success', 'failure_reason', 'additional_data'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'action', 'timestamp')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Result', {
            'fields': ('success', 'failure_reason')
        }),
        ('Additional Data', {
            'fields': ('additional_data',)
        })
    )
    
    def timestamp_display(self, obj):
        """Display timestamp"""
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_display.short_description = 'Time'
    
    def has_add_permission(self, request):
        """Disable adding logs manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing logs"""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')


# === THREAT INTELLIGENCE ADMIN ===

@admin.register(ThreatFeed)
class ThreatFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_external', 'is_public', 'last_sync')
    list_filter = ('is_external', 'is_public')
    search_fields = ('name', 'description')

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('type', 'value', 'threat_feed', 'confidence', 'created_at')
    list_filter = ('type', 'threat_feed', 'is_anonymized')
    search_fields = ('value', 'description')

@admin.register(TTPData)
class TTPDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'mitre_technique_id', 'mitre_tactic', 'threat_feed')
    list_filter = ('mitre_tactic', 'threat_feed', 'is_anonymized')
    search_fields = ('name', 'description', 'mitre_technique_id')

@admin.register(STIXObject)
class STIXObjectAdmin(admin.ModelAdmin):
    list_display = ('stix_id', 'stix_type', 'created', 'source_organization', 'anonymized')
    list_filter = ('stix_type', 'anonymized', 'created', 'source_organization')
    search_fields = ('stix_id', 'labels')
    readonly_fields = ('stix_id', 'created', 'modified', 'created_at', 'updated_at')

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'alias', 'owner', 'can_read', 'can_write', 'created_at')
    list_filter = ('can_read', 'can_write', 'owner', 'created_at')
    search_fields = ('title', 'description', 'alias')

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'is_active', 'created_at')
    list_filter = ('is_public', 'is_active', 'owner', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ('name', 'identity_class', 'stix_object')
    list_filter = ('identity_class',)
    search_fields = ('name', 'sectors')


# === TRUST MANAGEMENT ADMIN ===

@admin.register(TrustLevel)
class TrustLevelAdmin(admin.ModelAdmin):
    """Admin configuration for TrustLevel model."""
    
    list_display = [
        'name', 'level', 'numerical_value', 'default_access_level',
        'default_anonymization_level', 'is_active', 'is_system_default'
    ]
    list_filter = ['level', 'is_active', 'is_system_default', 'default_access_level']
    search_fields = ['name', 'description']
    ordering = ['numerical_value']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TrustGroup)
class TrustGroupAdmin(admin.ModelAdmin):
    """Admin configuration for TrustGroup model."""
    
    list_display = [
        'name', 'group_type', 'is_public', 'requires_approval',
        'default_trust_level', 'member_count', 'is_active', 'created_at'
    ]
    list_filter = ['group_type', 'is_public', 'requires_approval', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'member_count']
    
    def member_count(self, obj):
        """Display the number of active members."""
        return obj.get_member_count() if hasattr(obj, 'get_member_count') else 0
    member_count.short_description = 'Members'


@admin.register(TrustRelationship)
class TrustRelationshipAdmin(admin.ModelAdmin):
    """Admin configuration for TrustRelationship model."""
    
    list_display = [
        'relationship_summary', 'trust_level', 'status', 'relationship_type',
        'is_effective_display', 'created_at'
    ]
    list_filter = [
        'status', 'relationship_type', 'is_bilateral', 'is_active',
        'trust_level', 'created_at'
    ]
    search_fields = ['source_organization', 'target_organization', 'notes']
    ordering = ['-created_at']
    readonly_fields = [
        'created_at', 'updated_at', 'activated_at', 'revoked_at'
    ]
    
    def relationship_summary(self, obj):
        """Display a summary of the relationship."""
        source = str(obj.source_organization)[:8] if obj.source_organization else "Unknown"
        target = str(obj.target_organization)[:8] if obj.target_organization else "Unknown"
        return f"{source}... → {target}..."
    relationship_summary.short_description = 'Relationship'
    
    def is_effective_display(self, obj):
        """Display if relationship is effective with styling."""
        effective = getattr(obj, 'is_effective', False)
        color = 'green' if effective else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, 'Yes' if effective else 'No'
        )
    is_effective_display.short_description = 'Effective'


@admin.register(TrustLog)
class TrustLogAdmin(admin.ModelAdmin):
    """Admin configuration for TrustLog model."""
    
    list_display = [
        'action', 'source_organization_short', 'target_organization_short',
        'user', 'success', 'timestamp'
    ]
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['source_organization', 'target_organization', 'user', 'action']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    def source_organization_short(self, obj):
        """Display shortened source organization ID."""
        if obj.source_organization:
            return f"{str(obj.source_organization)[:8]}..."
        return '-'
    source_organization_short.short_description = 'Source Org'
    
    def target_organization_short(self, obj):
        """Display shortened target organization ID."""
        if obj.target_organization:
            return f"{str(obj.target_organization)[:8]}..."
        return '-'
    target_organization_short.short_description = 'Target Org'
    
    def has_add_permission(self, request):
        """Disable adding logs through admin (they should be created automatically)."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing logs (they should be immutable)."""
        return False


# Customize admin site
admin.site.site_header = 'CRISP Integrated Platform Administration'
admin.site.site_title = 'CRISP Admin'
admin.site.index_title = 'CRISP Platform Administration'