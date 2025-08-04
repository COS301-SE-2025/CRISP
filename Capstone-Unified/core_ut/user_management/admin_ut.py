from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.user_models import CustomUser, Organization, UserSession, AuthenticationLog


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'organization_type', 'is_publisher', 'is_verified', 'is_active', 'created_at']
    list_filter = ['organization_type', 'is_publisher', 'is_verified', 'is_active']
    search_fields = ['name', 'domain', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'domain', 'contact_email', 'website')
        }),
        ('Organization Type', {
            'fields': ('organization_type', 'is_publisher', 'is_verified', 'is_active')
        }),
        ('Metadata', {
            'fields': ('trust_metadata', 'created_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'organization', 'role', 'is_publisher', 'is_verified', 'is_active']
    list_filter = ['role', 'is_publisher', 'is_verified', 'is_active', 'organization', 'two_factor_enabled']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at', 'password_changed_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Organization & Role', {
            'fields': ('organization', 'role', 'is_publisher', 'is_verified')
        }),
        ('Security', {
            'fields': ('failed_login_attempts', 'account_locked_until', 'password_changed_at'),
            'classes': ('collapse',)
        }),
        ('Two-Factor Authentication', {
            'fields': ('two_factor_enabled', 'two_factor_secret'),
            'classes': ('collapse',)
        }),
        ('Trusted Devices & Preferences', {
            'fields': ('trusted_devices', 'preferences', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'organization', 'role')
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'is_active', 'is_trusted_device', 'created_at', 'expires_at']
    list_filter = ['is_active', 'is_trusted_device', 'created_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['id', 'created_at', 'last_activity']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'session_token', 'refresh_token')
        }),
        ('Device Info', {
            'fields': ('device_info', 'ip_address', 'is_trusted_device')
        }),
        ('Session Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuthenticationLog)
class AuthenticationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'success', 'timestamp']
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['id', 'timestamp']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'action', 'success')
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Details', {
            'fields': ('failure_reason', 'additional_data'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Authentication logs should not be manually added
        return False
    
    def has_change_permission(self, request, obj=None):
        # Authentication logs should not be modified
        return False