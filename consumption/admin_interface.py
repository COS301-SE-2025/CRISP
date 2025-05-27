from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import ExternalFeedSource, FeedConsumptionLog
from .tasks import manual_feed_refresh


class FeedConsumptionLogInline(admin.TabularInline):
    """Inline admin for feed consumption logs."""
    model = FeedConsumptionLog
    extra = 0
    fields = ['start_time', 'status', 'objects_retrieved', 'objects_processed', 'objects_failed']
    readonly_fields = ['start_time', 'status', 'objects_retrieved', 'objects_processed', 'objects_failed']
    ordering = ['-start_time']
    max_num = 10
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ExternalFeedSource)
class ExternalFeedSourceAdmin(admin.ModelAdmin):
    """Admin interface for external feed sources."""
    list_display = [
        'name', 
        'feed_categories', 
        'poll_interval', 
        'last_poll_status',
        'last_poll_time', 
        'is_active',
        'refresh_button'
    ]
    list_filter = ['categories', 'poll_interval', 'is_active']
    search_fields = ['name', 'discovery_url']
    readonly_fields = ['last_poll_time', 'created_at', 'updated_at', 'added_by']
    fieldsets = [
        (None, {
            'fields': ['name', 'is_active']
        }),
        ('Connection Details', {
            'fields': [
                'discovery_url', 
                'api_root', 
                'collection_id',
                'categories',
                'poll_interval',
                'rate_limit'
            ]
        }),
        ('Authentication', {
            'fields': ['auth_type', 'auth_credentials'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['last_poll_time', 'created_at', 'updated_at', 'added_by'],
            'classes': ['collapse']
        }),
    ]
    inlines = [FeedConsumptionLogInline]
    actions = ['refresh_feeds']
    
    def save_model(self, request, obj, form, change):
        """Override save_model to track user who added the feed."""
        if not change:  # If this is a new object
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
    
    def feed_categories(self, obj):
        """Display categories as comma-separated list."""
        return ', '.join(obj.categories) if obj.categories else 'None'
    feed_categories.short_description = 'Categories'
    
    def last_poll_status(self, obj):
        """Display status of the last consumption with color coding."""
        # Get the most recent log entry
        latest_log = obj.consumption_logs.order_by('-start_time').first()
        
        if not latest_log:
            return format_html('<span style="color: gray;">No polls yet</span>')
        
        if latest_log.status == FeedConsumptionLog.ConsumptionStatus.SUCCESS:
            return format_html('<span style="color: green;">Success</span>')
        elif latest_log.status == FeedConsumptionLog.ConsumptionStatus.PARTIAL:
            return format_html('<span style="color: orange;">Partial Success</span>')
        else:
            return format_html('<span style="color: red;">Failed</span>')
    last_poll_status.short_description = 'Last Poll Status'
    
    def refresh_button(self, obj):
        """Display a button to manually refresh the feed."""
        return format_html(
            '<a class="button" href="{}">Refresh Now</a>',
            reverse('admin:refresh_feed', args=[obj.pk])
        )
    refresh_button.short_description = 'Actions'
    
    def get_urls(self):
        """Add custom URLs for refresh action."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:feed_id>/refresh/',
                self.admin_site.admin_view(self.refresh_feed),
                name='refresh_feed',
            )
        ]
        return custom_urls + urls
    
    def refresh_feed(self, request, feed_id):
        """Handle refresh feed action."""
        try:
            feed = ExternalFeedSource.objects.get(pk=feed_id)
            # Schedule the Celery task
            manual_feed_refresh.delay(str(feed_id))
            self.message_user(
                request,
                f"Refresh task scheduled for {feed.name}. Check logs for results.",
                messages.SUCCESS
            )
        except ExternalFeedSource.DoesNotExist:
            self.message_user(
                request,
                "Feed not found.",
                messages.ERROR
            )
        
        # Redirect back to the changelist
        return HttpResponseRedirect(reverse('admin:feed_consumption_externalfeedsource_changelist'))
    
    def refresh_feeds(self, request, queryset):
        """Action to refresh multiple feeds."""
        count = 0
        for feed in queryset:
            if feed.is_active:
                manual_feed_refresh.delay(str(feed.id))
                count += 1
        
        self.message_user(
            request,
            f"Scheduled refresh for {count} feeds. Check logs for results.",
            messages.SUCCESS
        )
    refresh_feeds.short_description = "Refresh selected feeds"


@admin.register(FeedConsumptionLog)
class FeedConsumptionLogAdmin(admin.ModelAdmin):
    """Admin interface for feed consumption logs."""
    list_display = [
        'feed_name',
        'start_time',
        'end_time',
        'status',
        'objects_retrieved',
        'objects_processed',
        'objects_failed'
    ]
    list_filter = ['status', 'feed_source', 'start_time']
    readonly_fields = [
        'feed_source',
        'start_time',
        'end_time',
        'status',
        'objects_retrieved',
        'objects_processed',
        'objects_failed',
        'error_message'
    ]
    search_fields = ['feed_source__name', 'error_message']
    
    def feed_name(self, obj):
        """Display feed source name."""
        return obj.feed_source.name
    feed_name.short_description = 'Feed Source'
    
    def has_add_permission(self, request):
        """Disable adding logs manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing logs."""
        return False
