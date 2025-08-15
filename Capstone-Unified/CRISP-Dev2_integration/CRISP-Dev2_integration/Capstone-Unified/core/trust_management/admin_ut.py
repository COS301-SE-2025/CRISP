"""
Django Admin Configuration for Trust Management

Provides a comprehensive admin interface for managing trust relationships,
groups, levels, and audit logs.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    TrustLevel,
    TrustGroup,
    TrustGroupMembership,
    TrustRelationship,
    TrustLog,
    SharingPolicy,
)


@admin.register(TrustLevel)
class TrustLevelAdmin(admin.ModelAdmin):
    """Admin interface for Trust Levels."""
    
    list_display = [
        'name', 'level', 'numerical_value', 'default_anonymization_level',
        'default_access_level', 'is_active', 'is_system_default', 'created_at'
    ]
    list_filter = ['level', 'is_active', 'is_system_default', 'default_anonymization_level']
    search_fields = ['name', 'description']
    ordering = ['numerical_value']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'level', 'numerical_value', 'description')
        }),
        ('Default Settings', {
            'fields': ('default_anonymization_level', 'default_access_level')
        }),
        ('Configuration', {
            'fields': ('sharing_policies', 'is_active', 'is_system_default')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class TrustGroupMembershipInline(admin.TabularInline):
    """Inline admin for Trust Group Memberships."""
    
    model = TrustGroupMembership
    extra = 0
    fields = ['organization', 'membership_type', 'is_active', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(TrustGroup)
class TrustGroupAdmin(admin.ModelAdmin):
    """Admin interface for Trust Groups."""
    
    list_display = [
        'name', 'group_type', 'is_public', 'requires_approval',
        'member_count', 'is_active', 'created_at'
    ]
    list_filter = ['group_type', 'is_public', 'requires_approval', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'member_count']
    inlines = [TrustGroupMembershipInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'group_type')
        }),
        ('Access Control', {
            'fields': ('is_public', 'requires_approval', 'default_trust_level')
        }),
        ('Administration', {
            'fields': ('administrators', 'group_policies', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'member_count'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        """Display member count."""
        return obj.get_member_count()
    member_count.short_description = 'Members'


@admin.register(TrustRelationship)
class TrustRelationshipAdmin(admin.ModelAdmin):
    """Admin interface for Trust Relationships."""
    
    list_display = [
        'relationship_summary', 'trust_level', 'relationship_type',
        'status', 'is_effective', 'created_at'
    ]
    list_filter = [
        'relationship_type', 'status', 'trust_level', 'is_bilateral',
        'is_active', 'approved_by_source', 'approved_by_target'
    ]
    search_fields = ['source_organization', 'target_organization', 'notes']
    ordering = ['-created_at']
    readonly_fields = [
        'created_at', 'updated_at', 'activated_at', 'revoked_at',
        'is_effective', 'is_fully_approved', 'is_expired'
    ]
    
    fieldsets = (
        ('Organizations', {
            'fields': ('source_organization', 'target_organization')
        }),
        ('Trust Configuration', {
            'fields': (
                'trust_level', 'relationship_type', 'trust_group',
                'anonymization_level', 'access_level'
            )
        }),
        ('Status', {
            'fields': (
                'status', 'is_bilateral', 'is_active',
                'is_effective', 'is_fully_approved', 'is_expired'
            )
        }),
        ('Approvals', {
            'fields': (
                'approved_by_source', 'approved_by_source_user',
                'approved_by_target', 'approved_by_target_user'
            )
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Additional Information', {
            'fields': ('sharing_preferences', 'metadata', 'notes'),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by', 'created_at', 'last_modified_by', 'updated_at',
                'activated_at', 'revoked_by', 'revoked_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def relationship_summary(self, obj):
        """Display relationship summary."""
        arrow = '↔' if obj.is_bilateral else '→'
        return f"{obj.source_organization} {arrow} {obj.target_organization}"
    relationship_summary.short_description = 'Relationship'
    
    def is_effective(self, obj):
        """Display if relationship is effective."""
        try:
            effective = obj.is_effective
            if effective:
                return format_html('<span style="color: green;">✓ Effective</span>')
            else:
                return format_html('<span style="color: red;">✗ Not Effective</span>')
        except Exception:
            return 'Unknown'
    is_effective.short_description = 'Effective'


@admin.register(TrustGroupMembership)
class TrustGroupMembershipAdmin(admin.ModelAdmin):
    """Admin interface for Trust Group Memberships."""
    
    list_display = [
        'organization', 'trust_group', 'membership_type',
        'is_active', 'joined_at', 'invited_by'
    ]
    list_filter = ['membership_type', 'is_active', 'trust_group']
    search_fields = ['organization', 'trust_group__name']
    ordering = ['-joined_at']
    readonly_fields = ['joined_at', 'left_at']
    
    fieldsets = (
        ('Membership Information', {
            'fields': ('trust_group', 'organization', 'membership_type')
        }),
        ('Status', {
            'fields': ('is_active', 'joined_at', 'left_at')
        }),
        ('Administration', {
            'fields': ('invited_by', 'approved_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TrustLog)
class TrustLogAdmin(admin.ModelAdmin):
    """Admin interface for Trust Logs (read-only)."""
    
    list_display = [
        'timestamp', 'action', 'source_organization',
        'target_organization', 'user', 'success'
    ]
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['source_organization', 'target_organization', 'user']
    ordering = ['-timestamp']
    readonly_fields = [
        'action', 'source_organization', 'target_organization',
        'trust_relationship', 'trust_group', 'user', 'ip_address',
        'user_agent', 'success', 'failure_reason', 'details', 'timestamp'
    ]
    
    def has_add_permission(self, request):
        """Disable adding trust logs through admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing trust logs through admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting trust logs through admin."""
        return False


@admin.register(SharingPolicy)
class SharingPolicyAdmin(admin.ModelAdmin):
    """Admin interface for Sharing Policies."""
    
    list_display = [
        'name', 'max_tlp_level', 'require_anonymization',
        'allow_attribution', 'is_active', 'created_at'
    ]
    list_filter = ['max_tlp_level', 'require_anonymization', 'allow_attribution', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('STIX Object Filtering', {
            'fields': ('allowed_stix_types', 'blocked_stix_types')
        }),
        ('Indicator Filtering', {
            'fields': ('allowed_indicator_types', 'blocked_indicator_types')
        }),
        ('Security Constraints', {
            'fields': (
                'max_tlp_level', 'max_age_days', 'require_anonymization',
                'allow_attribution'
            )
        }),
        ('Anonymization Rules', {
            'fields': ('anonymization_rules',),
            'classes': ('collapse',)
        }),
        ('Additional Constraints', {
            'fields': ('additional_constraints',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Customize admin site
admin.site.site_header = "CRISP Trust Management Administration"
admin.site.site_title = "CRISP Trust Admin"
admin.site.index_title = "Trust Management System"