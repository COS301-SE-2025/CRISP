from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from django.contrib.admin import SimpleListFilter

from .models import CustomUser, UserSession, AuthenticationLog, STIXObjectPermission, Organization


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


class OrganizationFilter(SimpleListFilter):
    """Filter by organization"""
    title = 'Organization'
    parameter_name = 'organization'
    
    def lookups(self, request, model_admin):
        # This would need to be updated to work with actual Organization model
        organizations = CustomUser.objects.values_list(
            'organization__name', flat=True
        ).distinct().order_by('organization__name')
        return [(org, org) for org in organizations if org]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(organization__name=self.value())


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser"""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'organization_name', 'role', 'account_status', 
        'last_login_display', 'created_at'
    ]
    
    list_filter = [
        AccountStatusFilter, 'role', 'is_publisher', 
        OrganizationFilter, 'two_factor_enabled', 
        'created_at', 'last_login'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name',
        'organization__name'
    ]
    
    readonly_fields = [
        'id', 'date_joined', 'created_at', 'updated_at',
        'last_login', 'failed_login_attempts', 'last_failed_login',
        'trusted_devices_display', 'auth_logs_link'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Organization & Role', {
            'fields': ('organization', 'role', 'is_publisher')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Security', {
            'fields': (
                'failed_login_attempts', 'last_failed_login', 'account_locked_until',
                'two_factor_enabled', 'trusted_devices_display',
                'password_reset_token', 'password_reset_expires'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
        ('Admin Links', {
            'fields': ('auth_logs_link',)
        })
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Organization & Role', {
            'fields': ('organization', 'role', 'is_publisher')
        }),
        ('Verification', {
            'fields': ('is_verified', 'is_active')
        })
    )
    
    def organization_name(self, obj):
        """Display organization name"""
        if obj.organization:
            return obj.organization.name
        return 'No Organization'
    organization_name.short_description = 'Organization'
    organization_name.admin_order_field = 'organization__name'
    
    def account_status(self, obj):
        """Display account status with color coding"""
        if not obj.is_active:
            return format_html(
                '<span style="color: red;">Inactive</span>'
            )
        elif not obj.is_verified:
            return format_html(
                '<span style="color: orange;">Unverified</span>'
            )
        elif obj.is_account_locked:
            return format_html(
                '<span style="color: red;">Locked</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">Active</span>'
            )
    account_status.short_description = 'Status'
    
    def last_login_display(self, obj):
        """Display last login in readable format"""
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M:%S')
        return 'Never'
    last_login_display.short_description = 'Last Login'
    last_login_display.admin_order_field = 'last_login'
    
    def trusted_devices_display(self, obj):
        """Display trusted devices count"""
        count = len(obj.trusted_devices)
        return f"{count} device(s)"
    trusted_devices_display.short_description = 'Trusted Devices'
    
    def auth_logs_link(self, obj):
        """Link to authentication logs"""
        if obj.id:
            url = reverse('admin:UserManagement_authenticationlog_changelist')
            return format_html(
                '<a href="{}?user__id__exact={}">View Authentication Logs</a>',
                url, obj.id
            )
        return 'Save user first'
    auth_logs_link.short_description = 'Authentication Logs'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('organization')
    
    def save_model(self, request, obj, form, change):
        """Custom save logic"""
        # Set creation metadata for new users
        if not change:
            obj._creation_request_data = {
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Django Admin'),
                'created_by': request.user.username if request.user.is_authenticated else 'system'
            }
        
        super().save_model(request, obj, form, change)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class SessionStatusFilter(SimpleListFilter):
    """Filter for session status"""
    title = 'Session Status'
    parameter_name = 'session_status'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('inactive', 'Inactive'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True, expires_at__gt=timezone.now())
        elif self.value() == 'expired':
            return queryset.filter(expires_at__lte=timezone.now())
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for UserSession"""
    
    list_display = [
        'user', 'ip_address', 'session_status', 'is_trusted_device',
        'created_at_display', 'expires_at_display', 'last_activity_display'
    ]
    
    list_filter = [
        SessionStatusFilter, 'is_trusted_device', 'is_active',
        'created_at', 'expires_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'ip_address'
    ]
    
    readonly_fields = [
        'id', 'session_token', 'refresh_token', 'device_info',
        'created_at', 'last_activity'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'ip_address')
        }),
        ('Session Info', {
            'fields': ('session_token', 'refresh_token', 'device_info', 'is_trusted_device')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_activity')
        })
    )
    
    def session_status(self, obj):
        """Display session status with color coding"""
        if not obj.is_active:
            return format_html(
                '<span style="color: red;">Inactive</span>'
            )
        elif obj.is_expired:
            return format_html(
                '<span style="color: orange;">Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">Active</span>'
            )
    session_status.short_description = 'Status'
    
    def created_at_display(self, obj):
        """Display creation time"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'
    
    def expires_at_display(self, obj):
        """Display expiration time"""
        return obj.expires_at.strftime('%Y-%m-%d %H:%M:%S')
    expires_at_display.short_description = 'Expires'
    expires_at_display.admin_order_field = 'expires_at'
    
    def last_activity_display(self, obj):
        """Display last activity time"""
        return obj.last_activity.strftime('%Y-%m-%d %H:%M:%S')
    last_activity_display.short_description = 'Last Activity'
    last_activity_display.admin_order_field = 'last_activity'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')
    
    actions = ['deactivate_sessions']
    
    def deactivate_sessions(self, request, queryset):
        """Admin action to deactivate sessions"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} session(s) were deactivated.'
        )
    deactivate_sessions.short_description = 'Deactivate selected sessions'


class ActionFilter(SimpleListFilter):
    """Filter by authentication action"""
    title = 'Action'
    parameter_name = 'action'
    
    def lookups(self, request, model_admin):
        actions = AuthenticationLog.objects.values_list(
            'action', flat=True
        ).distinct().order_by('action')
        return [(action, action.replace('_', ' ').title()) for action in actions]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(action=self.value())


class SuccessFilter(SimpleListFilter):
    """Filter by success status"""
    title = 'Success'
    parameter_name = 'success'
    
    def lookups(self, request, model_admin):
        return (
            ('success', 'Successful'),
            ('failed', 'Failed'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'success':
            return queryset.filter(success=True)
        elif self.value() == 'failed':
            return queryset.filter(success=False)


@admin.register(AuthenticationLog)
class AuthenticationLogAdmin(admin.ModelAdmin):
    """Admin interface for AuthenticationLog"""
    
    list_display = [
        'timestamp_display', 'username', 'action_display', 
        'success_display', 'ip_address', 'failure_reason'
    ]
    
    list_filter = [
        SuccessFilter, ActionFilter, 'timestamp'
    ]
    
    search_fields = [
        'username', 'ip_address', 'user_agent', 'failure_reason'
    ]
    
    readonly_fields = [
        'id', 'user', 'username', 'action', 'ip_address',
        'user_agent', 'success', 'failure_reason', 'timestamp',
        'additional_data'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'username', 'action')
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Result', {
            'fields': ('success', 'failure_reason')
        }),
        ('Additional Data', {
            'fields': ('additional_data',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        })
    )
    
    def timestamp_display(self, obj):
        """Display timestamp in readable format"""
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_display.short_description = 'Time'
    timestamp_display.admin_order_field = 'timestamp'
    
    def action_display(self, obj):
        """Display action with formatting"""
        return obj.action.replace('_', ' ').title()
    action_display.short_description = 'Action'
    action_display.admin_order_field = 'action'
    
    def success_display(self, obj):
        """Display success status with color coding"""
        if obj.success:
            return format_html(
                '<span style="color: green;">✓ Success</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Failed</span>'
            )
    success_display.short_description = 'Status'
    success_display.admin_order_field = 'success'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        """Disable adding authentication logs through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing authentication logs through admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup purposes"""
        return request.user.is_superuser


@admin.register(STIXObjectPermission)
class STIXObjectPermissionAdmin(admin.ModelAdmin):
    """Admin interface for STIXObjectPermission"""
    
    list_display = [
        'user', 'stix_object_id', 'permission_level',
        'granted_by', 'created_at_display', 'expires_at_display',
        'is_expired_display'
    ]
    
    list_filter = [
        'permission_level', 'created_at', 'expires_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'stix_object_id',
        'granted_by__username'
    ]
    
    readonly_fields = [
        'id', 'created_at'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'stix_object_id', 'permission_level')
        }),
        ('Granting Info', {
            'fields': ('granted_by', 'created_at')
        }),
        ('Expiration', {
            'fields': ('expires_at',)
        })
    )
    
    def created_at_display(self, obj):
        """Display creation time"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'
    
    def expires_at_display(self, obj):
        """Display expiration time"""
        if obj.expires_at:
            return obj.expires_at.strftime('%Y-%m-%d %H:%M:%S')
        return 'Never'
    expires_at_display.short_description = 'Expires'
    expires_at_display.admin_order_field = 'expires_at'
    
    def is_expired_display(self, obj):
        """Display expiration status"""
        if obj.is_expired:
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">Active</span>'
            )
    is_expired_display.short_description = 'Status'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user', 'granted_by')


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
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'domain', 'description', 'is_active'),
        }),
    )
    
    def user_count(self, obj):
        """Display user count for organization"""
        return obj.users.count()
    user_count.short_description = 'Users'
    user_count.admin_order_field = 'users__count'
    
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
    created_at_display.admin_order_field = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        return super().get_queryset(request).annotate(
            user_count=Count('users')
        )


# Admin site customization
admin.site.site_header = 'CRISP User Management Administration'
admin.site.site_title = 'CRISP User Management'
admin.site.index_title = 'User Management & Authentication'

# Register additional admin customizations
admin.site.site_url = '/'  # Link to main site