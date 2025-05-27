from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from .models import ExternalFeedSource, FeedConsumptionLog
from .tasks import manual_feed_refresh

class ExternalFeedSourceForm(forms.ModelForm):
    """Form for ExternalFeedSource with JSON validation"""
    class Meta:
        model = ExternalFeedSource
        fields = '__all__'
        widgets = {
            'auth_credentials': forms.JSONField.widget,
            'headers': forms.JSONField.widget,
            'categories': forms.JSONField.widget,
        }

@admin.register(ExternalFeedSource)
class ExternalFeedSourceAdmin(admin.ModelAdmin):
    form = ExternalFeedSourceForm
    list_display = ('name', 'discovery_url', 'collection_name', 'poll_interval', 'auth_type', 
                   'is_active', 'last_poll_time', 'refresh_button')
    list_filter = ('is_active', 'poll_interval', 'auth_type', 'created_at')
    search_fields = ('name', 'discovery_url', 'collection_name')
    readonly_fields = ('created_at', 'updated_at', 'collection_name', 'api_root_url')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('TAXII Connection', {
            'fields': ('discovery_url', 'api_root_url', 'collection_id', 'collection_name')
        }),
        ('Configuration', {
            'fields': ('categories', 'poll_interval', 'last_poll_time')
        }),
        ('Authentication', {
            'fields': ('auth_type', 'auth_credentials', 'headers'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('added_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
        
    def refresh_button(self, obj):
        """Button to manually refresh a feed"""
        if obj.collection_id:
            return format_html(
                '<a class="button" href="{}">Refresh Now</a>',
                reverse('admin_refresh_feed', args=[obj.pk])
            )
        return "No collection set"
    
    refresh_button.short_description = "Manual Refresh"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:feed_id>/refresh/',
                self.admin_site.admin_view(self.refresh_feed),
                name='admin_refresh_feed',
            )
        ]
        return custom_urls + urls
    
    def refresh_feed(self, request, feed_id):
        """Handle manual feed refresh"""
        # Start a Celery task to refresh the feed
        task = manual_feed_refresh.delay(str(feed_id))
        
        # Set a message for the user
        self.message_user(request, f"Feed refresh has been started. Task ID: {task.id}")
        
        # Redirect back to the feed detail page
        return HttpResponseRedirect(reverse('admin:feed_consumption_externalfeedsource_change', args=[feed_id]))

@admin.register(FeedConsumptionLog)
class FeedConsumptionLogAdmin(admin.ModelAdmin):
    list_display = ('feed_source', 'status', 'objects_processed', 'objects_added', 
                   'objects_updated', 'objects_failed', 'execution_time_display', 'created_at')
    list_filter = ('status', 'feed_source', 'created_at')
    search_fields = ('feed_source__name', 'error_message')
    readonly_fields = ('feed_source', 'status', 'objects_processed', 'objects_added', 'objects_updated',
                      'objects_failed', 'start_time', 'end_time', 'execution_time_seconds',
                      'error_message', 'details', 'created_at', 'updated_at')
    
    def execution_time_display(self, obj):
        """Format execution time for display"""
        if obj.execution_time_seconds is not None:
            return f"{obj.execution_time_seconds:.2f} seconds"
        return "-"
    
    execution_time_display.short_description = "Execution Time"
    
    def has_add_permission(self, request):
        """Disable manual creation of logs"""
        return False
