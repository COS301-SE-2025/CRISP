"""
Trust Management Django Admin Configuration

Admin interface for managing trust relationships, groups, and related models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership,
    TrustLog, SharingPolicy
)


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
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'level', 'description', 'numerical_value')
        }),
        ('Default Settings', {
            'fields': ('default_anonymization_level', 'default_access_level')
        }),
        ('Policies', {
            'fields': ('sharing_policies',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_system_default')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('numerical_value')


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
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'group_type')
        }),
        ('Settings', {
            'fields': ('is_public', 'requires_approval', 'default_trust_level')
        }),
        ('Policies', {
            'fields': ('group_policies',)
        }),
        ('Administration', {
            'fields': ('administrators',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'member_count'),
            'classes': ('collapse',)
        })
    )
    
    def member_count(self, obj):
        """Display the number of active members."""
        count = obj.get_member_count()
        url = reverse('admin:TrustManagement_trustgroupmembership_changelist')
        return format_html(
            '<a href="{}?trust_group__id__exact={}">{} members</a>',
            url, obj.id, count
        )
    member_count.short_description = 'Members'


@admin.register(TrustRelationship)
class TrustRelationshipAdmin(admin.ModelAdmin):
    """Admin configuration for TrustRelationship model."""
    
    list_display = [
        'relationship_summary', 'trust_level', 'status', 'relationship_type',
        'is_effective', 'is_fully_approved', 'created_at'
    ]
    list_filter = [
        'status', 'relationship_type', 'is_bilateral', 'is_active',
        'trust_level', 'created_at'
    ]
    search_fields = ['source_organization', 'target_organization', 'notes']
    ordering = ['-created_at']
    readonly_fields = [
        'created_at', 'updated_at', 'activated_at', 'revoked_at',
        'is_effective', 'is_expired', 'is_fully_approved'
    ]
    
    fieldsets = (
        ('Organizations', {
            'fields': ('source_organization', 'target_organization')
        }),
        ('Trust Configuration', {
            'fields': ('relationship_type', 'trust_level', 'trust_group')
        }),
        ('Access Control', {
            'fields': ('anonymization_level', 'access_level')
        }),
        ('Approval Status', {
            'fields': (
                'approved_by_source', 'approved_by_source_user',
                'approved_by_target', 'approved_by_target_user'
            )
        }),
        ('Temporal Settings', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Configuration', {
            'fields': ('sharing_preferences', 'metadata')
        }),
        ('Status', {
            'fields': ('status', 'is_bilateral', 'is_active')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by', 'created_at', 'last_modified_by', 'updated_at',
                'activated_at', 'revoked_by', 'revoked_at'
            ),
            'classes': ('collapse',)
        }),
        ('Computed Properties', {
            'fields': (
                'is_effective', 'is_expired', 'is_fully_approved'
            ),
            'classes': ('collapse',)
        })
    )
    
    def relationship_summary(self, obj):
        """Display a summary of the relationship."""
        return f"{obj.source_organization[:8]}... → {obj.target_organization[:8]}..."
    relationship_summary.short_description = 'Relationship'
    
    def is_effective(self, obj):
        """Display if relationship is effective with styling."""
        effective = obj.is_effective
        color = 'green' if effective else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, 'Yes' if effective else 'No'
        )
    is_effective.short_description = 'Effective'
    
    def is_fully_approved(self, obj):
        """Display approval status with styling."""
        approved = obj.is_fully_approved
        color = 'green' if approved else 'orange'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, 'Yes' if approved else 'No'
        )
    is_fully_approved.short_description = 'Approved'


@admin.register(TrustGroupMembership)
class TrustGroupMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for TrustGroupMembership model."""
    
    list_display = [
        'organization', 'trust_group', 'membership_type',
        'is_active', 'joined_at', 'invited_by'
    ]
    list_filter = ['membership_type', 'is_active', 'joined_at', 'trust_group']
    search_fields = ['organization', 'trust_group__name']
    ordering = ['-joined_at']
    readonly_fields = ['joined_at', 'left_at']
    
    fieldsets = (
        ('Membership', {
            'fields': ('trust_group', 'organization', 'membership_type')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timeline', {
            'fields': ('joined_at', 'left_at')
        }),
        ('Management', {
            'fields': ('invited_by', 'approved_by')
        })
    )


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
    
    fieldsets = (
        ('Action', {
            'fields': ('action', 'success', 'failure_reason')
        }),
        ('Organizations', {
            'fields': ('source_organization', 'target_organization')
        }),
        ('Related Objects', {
            'fields': ('trust_relationship', 'trust_group')
        }),
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Details', {
            'fields': ('details',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        })
    )
    
    def source_organization_short(self, obj):
        """Display shortened source organization ID."""
        if obj.source_organization:
            return f"{obj.source_organization[:8]}..."
        return '-'
    source_organization_short.short_description = 'Source Org'
    
    def target_organization_short(self, obj):
        """Display shortened target organization ID."""
        if obj.target_organization:
            return f"{obj.target_organization[:8]}..."
        return '-'
    target_organization_short.short_description = 'Target Org'
    
    def has_add_permission(self, request):
        """Disable adding logs through admin (they should be created automatically)."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing logs (they should be immutable)."""
        return False


@admin.register(SharingPolicy)
class SharingPolicyAdmin(admin.ModelAdmin):
    """Admin configuration for SharingPolicy model."""
    
    list_display = [
        'name', 'max_tlp_level', 'require_anonymization',
        'allow_attribution', 'is_active', 'created_at'
    ]
    list_filter = [
        'max_tlp_level', 'require_anonymization', 'allow_attribution',
        'is_active', 'created_at'
    ]
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('STIX Type Filtering', {
            'fields': ('allowed_stix_types', 'blocked_stix_types')
        }),
        ('TLP and Age Constraints', {
            'fields': ('max_tlp_level', 'max_age_days')
        }),
        ('Anonymization', {
            'fields': ('require_anonymization', 'anonymization_rules')
        }),
        ('Attribution', {
            'fields': ('allow_attribution',)
        }),
        ('Additional Constraints', {
            'fields': ('additional_constraints',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# Customize admin site header and title
admin.site.site_header = 'CRISP Trust Management Administration'
admin.site.site_title = 'CRISP Trust Admin'
admin.site.index_title = 'Trust Management Administration'