from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CrispUser, IndicatorOfCompromise, Organization, ThreatFeed
from django.utils.translation import gettext_lazy as _

class CrispUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'organization', 'is_admin')
    list_filter = ('role', 'is_staff', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        ('CRISP Information', {'fields': ('role', 'organization', 'phone_number', 'job_title', 
                                         'require_password_change', 'failed_login_attempts', 
                                         'is_locked')}),
    )
    
    # Method to display is_staff as "Admin"
    def is_admin(self, obj):
        return obj.is_staff
    is_admin.short_description = 'ADMIN STATUS'
    is_admin.boolean = True
    is_admin.admin_order_field = 'is_staff'  # For sorting


admin.site.register(CrispUser, CrispUserAdmin)