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
        'get_stix_id',  # Use a custom method to display related stix_id
        'get_identity_class',  # Use a custom method to display related identity_class
        'created_at',
        'updated_at',
        'created_by'
    ]
    list_filter = [
        'stix_identity__identity_class',  # Filter by the related Identity's class
        'created_at',
        'updated_at'
    ]
    search_fields = ['name', 'description', 'stix_identity__stix_id', 'stix_identity__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'description')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
        ('STIX Identity Info', {
            'fields': ('get_stix_id_admin', 'get_identity_class_admin', 'get_identity_name_admin'), # Display related Identity info
        }),
    )

    def get_stix_id(self, obj):
        if hasattr(obj, 'stix_identity') and obj.stix_identity:
            return obj.stix_identity.stix_id
        return None
    get_stix_id.short_description = 'STIX ID'
    get_stix_id.admin_order_field = 'stix_identity__stix_id'

    def get_identity_class(self, obj):
        if hasattr(obj, 'stix_identity') and obj.stix_identity:
            return obj.stix_identity.identity_class
        return None
    get_identity_class.short_description = 'Identity Class'
    get_identity_class.admin_order_field = 'stix_identity__identity_class'

    # Methods for display in fieldsets if needed (cannot be directly in 'fields' if not model fields)
    def get_stix_id_admin(self, obj):
        return self.get_stix_id(obj)
    get_stix_id_admin.short_description = 'STIX ID'

    def get_identity_class_admin(self, obj):
        return self.get_identity_class(obj)
    get_identity_class_admin.short_description = 'Identity Class'

    def get_identity_name_admin(self, obj):
        if hasattr(obj, 'stix_identity') and obj.stix_identity:
            return obj.stix_identity.name
        return None
    get_identity_name_admin.short_description = 'Identity Name'


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
    list_display = ('name', 'collection', 'status', 'last_published', 'created_by', 'created_at')
    list_filter = ('status', 'created_at', 'collection')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'last_published')
    raw_id_fields = ('collection', 'created_by')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'collection', 'created_by')
        }),
        ('Configuration', {
            'fields': ('query_parameters', 'update_interval', 'status')
        }),
        ('Publication', {
            'fields': ('last_published', 'created_at', 'updated_at')
        }),
    )

# admin.site.register(Identity)  # Uncomment this line if you want to register the Identity model