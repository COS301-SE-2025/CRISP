from django.contrib import admin
from django.utils.html import format_html

EXTENDED_MODELS_AVAILABLE = True
try:
    from .models import (
        Institution, 
        Indicator, 
        ThreatFeed, 
        TTPData,
        Feed,
        Identity,
        CollectionObject,
        Collection,
        STIXObject
    )
except ImportError as e:
    print(f"Warning: Some models not available: {e}")
    EXTENDED_MODELS_AVAILABLE = False


# Admin site customization
admin.site.site_header = "CRISP Publication System Administration"
admin.site.site_title = "CRISP Publication Admin"
admin.site.index_title = "Threat Intelligence Management"


if EXTENDED_MODELS_AVAILABLE:
    
    @admin.register(Collection)
    class CollectionAdmin(admin.ModelAdmin):
        """Admin interface for Collection model"""
        list_display = ['title', 'created_at']
        list_filter = ['created_at']
        search_fields = ['title', 'description']
        readonly_fields = ['created_at', 'updated_at']

    @admin.register(Feed)
    class FeedAdmin(admin.ModelAdmin):
        """Admin interface for Feed model"""
        list_display = ['title', 'alias', 'created_at']
        list_filter = ['created_at']
        search_fields = ['title', 'alias', 'description']
        readonly_fields = ['created_at', 'updated_at']

    @admin.register(Identity)
    class IdentityAdmin(admin.ModelAdmin):
        """Admin interface for STIX Identity objects"""
        list_display = ['name', 'identity_class', 'created']
        list_filter = ['identity_class', 'created']
        search_fields = ['name', 'stix_id']
        readonly_fields = ['stix_id', 'created', 'modified']

    @admin.register(CollectionObject)
    class CollectionObjectAdmin(admin.ModelAdmin):
        """Admin interface for Collection Objects"""
        list_display = ['collection', 'stix_object']
        list_filter = ['collection']
        search_fields = ['collection__title', 'stix_object__stix_id']

    @admin.register(Institution)
    class InstitutionAdmin(admin.ModelAdmin):
        """Admin interface for Institution model (separate from Organization management)"""
        list_display = ['name', 'contact_email', 'contact_name', 'created_at']
        list_filter = ['created_at']
        search_fields = ['name', 'description', 'contact_email', 'contact_name']
        readonly_fields = ['created_at', 'updated_at']
        
        fieldsets = (
            ('Institution Information', {
                'fields': ('name', 'description')
            }),
            ('Contact Details', {
                'fields': ('contact_name', 'contact_email')
            }),
            ('Metadata', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )

    @admin.register(Indicator)
    class IndicatorAdmin(admin.ModelAdmin):
        """Admin interface for Indicator model"""
        list_display = ['get_value_preview', 'type', 'confidence', 'first_seen']
        list_filter = ['type', 'confidence']
        search_fields = ['value', 'description', 'stix_id']
        readonly_fields = ['stix_id', 'created_at', 'updated_at']
        
        def get_value_preview(self, obj):
            """Show truncated value for readability"""
            if obj.value and len(obj.value) > 50:
                return obj.value[:50] + '...'
            return obj.value or 'N/A'
        get_value_preview.short_description = 'Value'

    @admin.register(ThreatFeed)
    class ThreatFeedAdmin(admin.ModelAdmin):
        """Admin interface for Threat Feed model"""
        list_display = ['name', 'is_external', 'is_active', 'created_at']
        list_filter = ['is_external', 'is_active', 'created_at']
        search_fields = ['name', 'description']
        readonly_fields = ['created_at', 'updated_at']
    
    @admin.register(TTPData)
    class TTPDataAdmin(admin.ModelAdmin):
        """Admin interface for TTP (Tactics, Techniques, Procedures) data"""
        list_display = ['name', 'mitre_technique_id', 'mitre_tactic', 'threat_feed']
        list_filter = ['mitre_tactic', 'threat_feed']
        search_fields = ['name', 'description', 'mitre_technique_id']

    @admin.register(STIXObject)
    class STIXObjectAdmin(admin.ModelAdmin):
        """Admin interface for STIX Objects"""
        list_display = ['stix_id', 'stix_type', 'created_at']
        list_filter = ['stix_type', 'created_at']
        search_fields = ['stix_id']
        readonly_fields = ['created_at', 'updated_at']
