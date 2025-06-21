"""
Django admin configuration for CRISP Threat Intelligence Platform
"""
from django.contrib import admin
from .models import Organization, STIXObject, Collection, CollectionObject, Feed, Identity


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'identity_class', 'contact_email', 'created_at']
    list_filter = ['identity_class', 'created_at']
    search_fields = ['name', 'description', 'contact_email']
    readonly_fields = ['stix_id', 'created_at', 'updated_at']


@admin.register(STIXObject)
class STIXObjectAdmin(admin.ModelAdmin):
    list_display = ['stix_id', 'stix_type', 'source_organization', 'created', 'anonymized']
    list_filter = ['stix_type', 'source_organization', 'anonymized', 'created_at']
    search_fields = ['stix_id', 'labels']
    readonly_fields = ['stix_id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('source_organization')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'alias', 'owner', 'can_read', 'can_write', 'created_at']
    list_filter = ['owner', 'can_read', 'can_write', 'created_at']
    search_fields = ['title', 'description', 'alias']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'collection', 'status', 'last_published_time', 'publish_count']
    list_filter = ['status', 'created_at', 'last_published_time']
    search_fields = ['name', 'description']
    readonly_fields = ['last_published_time', 'publish_count', 'error_count', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('collection')


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