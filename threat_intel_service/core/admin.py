"""
Django admin configuration for core models.
"""
from django.contrib import admin
from .models import Organization, STIXObject, Collection, CollectionObject, Feed, Identity


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin configuration for Organization model."""
    list_display = [
        'name',
        'get_stix_id',
        'get_identity_class',
        'created_at',
        'updated_at',
        'created_by'
    ]
    list_filter = [
        'stix_identity__identity_class',
        'created_at',
        'updated_at'
    ]
    search_fields = ['name', 'description', 'stix_identity__stix_id', 'stix_identity__name']

    # Add/Modify readonly_fields here:
    readonly_fields = [
        'id', # Usually good to make the UUID id readonly
        'created_at', 
        'updated_at',
        'get_stix_id_admin', # Add your methods here
        'get_identity_class_admin',
        'get_identity_name_admin'
    ]

    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'description')
        }),
        ('Metadata', {
            # 'created_by' should be a ForeignKey, it's editable unless made readonly
            'fields': ('created_by', 'created_at', 'updated_at') 
        }),
        ('STIX Identity Info', {
            # These will now be displayed as readonly fields using your methods
            'fields': ('get_stix_id_admin', 'get_identity_class_admin', 'get_identity_name_admin'),
        }),
    )

    def get_stix_id(self, obj):
        # This method is for list_display
        if hasattr(obj, 'stix_identity') and obj.stix_identity:
            return obj.stix_identity.stix_id
        return None
    get_stix_id.short_description = 'STIX ID'
    get_stix_id.admin_order_field = 'stix_identity__stix_id'

    def get_identity_class(self, obj):
        # This method is for list_display
        if hasattr(obj, 'stix_identity') and obj.stix_identity:
            return obj.stix_identity.identity_class
        return None
    get_identity_class.short_description = 'Identity Class'
    get_identity_class.admin_order_field = 'stix_identity__identity_class'

    # Methods for display in fieldsets (must be in readonly_fields)
    def get_stix_id_admin(self, obj):
        return self.get_stix_id(obj) # You can reuse the list_display method
    get_stix_id_admin.short_description = 'STIX ID (from Identity)' # Differentiate if needed

    def get_identity_class_admin(self, obj):
        return self.get_identity_class(obj) # You can reuse
    get_identity_class_admin.short_description = 'Identity Class (from Identity)'

    def get_identity_name_admin(self, obj):
        if hasattr(obj, 'stix_identity') and obj.stix_identity:
            return obj.stix_identity.name
        return None
    get_identity_name_admin.short_description = 'Identity Name (from Identity)'


@admin.register(STIXObject)
class STIXObjectAdmin(admin.ModelAdmin):
    """Admin configuration for STIXObject model."""
    list_display = ('stix_id', 'stix_type', 'created', 'modified', 'source_organization', 'anonymized')
    list_filter = ('stix_type', 'created_at', 'source_organization', 'anonymized')
    search_fields = ('stix_id', 'raw_data')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('created_by', 'source_organization')
    fieldsets = (
        ('STIX Data', {
            'fields': ('stix_id', 'stix_type', 'spec_version', 'created', 'modified')
        }),
        ('Content', {
            'fields': ('raw_data',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'source_organization', 'created_at', 'updated_at')
        }),
        ('Anonymization', {
            'fields': ('anonymized', 'anonymization_strategy', 'original_object_ref')
        }),
    )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Admin configuration for Collection model."""
    list_display = ('title', 'alias', 'owner', 'can_read', 'can_write', 'created_at')
    list_filter = ('owner', 'can_read', 'can_write', 'created_at')
    search_fields = ('title', 'description', 'alias')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'alias', 'owner')
        }),
        ('Access Control', {
            'fields': ('can_read', 'can_write', 'default_anonymization')
        }),
        ('Technical Details', {
            'fields': ('media_types', 'created_at', 'updated_at')
        }),
    )


@admin.register(CollectionObject)
class CollectionObjectAdmin(admin.ModelAdmin):
    """Admin configuration for CollectionObject model."""
    list_display = ('id', 'collection', 'stix_object', 'date_added')
    list_filter = ('date_added', 'collection')
    search_fields = ('collection__title', 'stix_object__stix_id')
    raw_id_fields = ('collection', 'stix_object')
    readonly_fields = ('date_added',)


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    """Admin configuration for Feed model."""
    list_display = ('name', 'get_collection', 'status', 'last_published_time', 'get_created_by')
    list_filter = ('status',)
    search_fields = ('name', 'description', 'collection__title')
    raw_id_fields = ('collection', 'created_by')
    readonly_fields = ('id', 'last_published_time', 'next_publish_time', 
                      'publish_count', 'error_count', 'last_bundle_id', 
                      'last_error', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'description')
        }),
        ('Relationships', {
            'fields': ('collection', 'created_by')
        }),
        ('Configuration', {
            'fields': ('query_parameters', 'update_interval', 'status')
        }),
        ('Publication Stats', {
            'fields': ('last_published_time', 'next_publish_time', 'publish_count', 
                      'error_count', 'last_bundle_id', 'last_error')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_collection(self, obj):
        return obj.collection.title if obj.collection else None
    get_collection.short_description = 'Collection'
    get_collection.admin_order_field = 'collection__title'

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None
    get_created_by.short_description = 'Created By'
    get_created_by.admin_order_field = 'created_by__username'

# admin.site.register(Identity)  # Uncomment this line if you want to register the Identity model