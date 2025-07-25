"""
Simplified Django admin configuration that only includes working models
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Organization, STIXObject, Collection, CollectionObject, Feed, Identity
# Import only models that have existing tables
try:
    from .models import Institution, Indicator, ThreatFeed
    EXTENDED_MODELS_AVAILABLE = True
except:
    EXTENDED_MODELS_AVAILABLE = False
import json


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization_type', 'contact_email', 'created_at']
    list_filter = ['organization_type', 'created_at']
    search_fields = ['name', 'description', 'contact_email']
    readonly_fields = ['stix_id', 'created_at', 'updated_at']


@admin.register(STIXObject)
class STIXObjectAdmin(admin.ModelAdmin):
    list_display = [
        'stix_id', 'stix_type', 'get_name', 'source_organization', 
        'anonymized', 'anonymization_strategy', 'created'
    ]
    list_filter = ['stix_type', 'source_organization', 'anonymized', 'created_at']
    search_fields = ['stix_id', 'labels']
    readonly_fields = ['stix_id', 'created_at', 'updated_at', 'get_anonymization_info']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'stix_id', 'stix_type', 'source_organization', 'anonymized',
                'anonymization_strategy', 'anonymization_trust_level'
            )
        }),
        ('Anonymization Details', {
            'fields': ('get_anonymization_info',),
            'classes': ('collapse',),
        }),
        ('Raw Data', {
            'fields': ('raw_data', 'original_data'),
            'classes': ('collapse',),
        }),
    )
    
    def get_name(self, obj):
        """Extract name from raw_data"""
        return obj.raw_data.get('name', 'Unnamed')
    get_name.short_description = 'Name'
    
    def get_anonymization_info(self, obj):
        """Show anonymization information"""
        if not obj.anonymized:
            return 'Object not anonymized'
        
        # Check for anonymization markers
        markers = []
        for key, value in obj.raw_data.items():
            if key.startswith('x_crisp_'):
                markers.append(f"{key}: {value}")
        
        markers_html = '<br>'.join(markers) if markers else 'No anonymization markers'
        
        html = f"""
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
            <strong>Anonymized:</strong> {'Yes' if obj.anonymized else 'No'}<br>
            <strong>Strategy:</strong> {obj.anonymization_strategy or 'Not set'}<br>
            <strong>Trust Level:</strong> {obj.anonymization_trust_level or 'Not set'}<br>
            <strong>Markers:</strong><br>{markers_html}
        </div>
        """
        return mark_safe(html)
    get_anonymization_info.short_description = 'Anonymization Info'


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'alias', 'owner', 'can_read', 'can_write', 'get_object_count', 'created_at']
    list_filter = ['owner', 'can_read', 'can_write', 'created_at']
    search_fields = ['title', 'description', 'alias']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_object_count(self, obj):
        """Get number of STIX objects in collection"""
        return obj.stix_objects.count()
    get_object_count.short_description = 'Objects'


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'collection', 'status', 'last_published_time', 'publish_count']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['last_published_time', 'publish_count', 'error_count', 'created_at', 'updated_at']


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ['name', 'identity_class', 'organization', 'created']
    list_filter = ['identity_class', 'created']
    search_fields = ['name', 'stix_id']
    readonly_fields = ['stix_id', 'created', 'modified']


@admin.register(CollectionObject)
class CollectionObjectAdmin(admin.ModelAdmin):
    list_display = ['collection', 'stix_object', 'date_added']
    list_filter = ['date_added']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('collection', 'stix_object')


# Simple indicator model that works with existing tables
class SimpleIndicator:
    """Simple indicator representation from STIX objects"""
    def __init__(self, stix_object):
        self.stix_object = stix_object
        self.pattern = stix_object.raw_data.get('pattern', '')
        self.name = stix_object.raw_data.get('name', 'Unnamed Indicator')
        self.labels = stix_object.raw_data.get('labels', [])
        self.created = stix_object.created
        self.source = stix_object.source_organization.name

# Custom admin view for indicators
class SimpleIndicatorAdmin(admin.ModelAdmin):
    """Show indicators from STIX objects"""
    
    def changelist_view(self, request, extra_context=None):
        # Get all indicator-type STIX objects
        indicators = STIXObject.objects.filter(stix_type='indicator').select_related('source_organization')
        
        indicator_list = []
        for stix_obj in indicators:
            indicator_list.append({
                'id': stix_obj.id,
                'name': stix_obj.raw_data.get('name', 'Unnamed'),
                'pattern': stix_obj.raw_data.get('pattern', '')[:100] + ('...' if len(stix_obj.raw_data.get('pattern', '')) > 100 else ''),
                'labels': ', '.join(stix_obj.raw_data.get('labels', [])),
                'source': stix_obj.source_organization.name,
                'anonymized': stix_obj.anonymized,
                'created': stix_obj.created
            })
        
        extra_context = extra_context or {}
        extra_context['indicators'] = indicator_list
        extra_context['title'] = 'Threat Intelligence Indicators'
        
        from django.shortcuts import render
        return render(request, 'admin/simple_indicators.html', extra_context)

# Register Institution and Indicator admins if tables exist
if EXTENDED_MODELS_AVAILABLE:
    @admin.register(Institution)
    class InstitutionAdmin(admin.ModelAdmin):
        list_display = ['name', 'contact_email', 'contact_name', 'created_at']
        list_filter = ['created_at']
        search_fields = ['name', 'description', 'contact_email', 'contact_name']
        readonly_fields = ['created_at', 'updated_at']

    @admin.register(Indicator)
    class IndicatorAdmin(admin.ModelAdmin):
        list_display = ['get_value_preview', 'type', 'confidence', 'is_anonymized', 'first_seen']
        list_filter = ['type', 'is_anonymized', 'confidence']
        search_fields = ['value', 'description', 'stix_id']
        readonly_fields = ['stix_id', 'created_at', 'updated_at']
        
        def get_value_preview(self, obj):
            if len(obj.value) > 50:
                return obj.value[:50] + '...'
            return obj.value
        get_value_preview.short_description = 'Value'

    @admin.register(ThreatFeed)
    class ThreatFeedAdmin(admin.ModelAdmin):
        list_display = ['name', 'is_external', 'is_active', 'last_sync', 'sync_count']
        list_filter = ['is_external', 'is_active', 'created_at']
        search_fields = ['name', 'description']
        readonly_fields = ['sync_count', 'last_sync', 'created_at', 'updated_at']