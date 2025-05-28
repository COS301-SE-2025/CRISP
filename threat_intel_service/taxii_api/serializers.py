"""
Serializers for TAXII API endpoints.
"""
from rest_framework import serializers
from core.models import Collection, STIXObject, CollectionObject, Organization


class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for TAXII Collection object.
    """
    id = serializers.UUIDField(format='hex_verbose', read_only=True)
    
    class Meta:
        model = Collection
        fields = ['id', 'title', 'description', 'alias', 'can_read', 'can_write', 'media_types']
        read_only_fields = ['id']


class STIXObjectSerializer(serializers.ModelSerializer):
    """
    Serializer for STIX Object in TAXII API.
    """
    id = serializers.CharField(source='stix_id', read_only=True)
    
    class Meta:
        model = STIXObject
        fields = ['id', 'stix_type', 'spec_version', 'created', 'modified']
        read_only_fields = ['id', 'stix_type', 'spec_version', 'created', 'modified']


class TAXIIManifestSerializer(serializers.Serializer):
    """
    Serializer for TAXII Manifest resource.
    """
    id = serializers.CharField()
    date_added = serializers.DateTimeField()
    version = serializers.CharField()
    media_type = serializers.CharField(default='application/stix+json;version=2.1')


class TAXIIDiscoverySerializer(serializers.Serializer):
    """
    Serializer for TAXII Discovery resource.
    """
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    contact = serializers.CharField(required=False, allow_blank=True)
    default = serializers.URLField()
    api_roots = serializers.ListField(child=serializers.URLField())


class TAXIIApiRootSerializer(serializers.Serializer):
    """
    Serializer for TAXII API Root resource.
    """
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    versions = serializers.ListField(child=serializers.CharField())
    max_content_length = serializers.IntegerField()


class TAXIICollectionSerializer(serializers.Serializer):
    """
    Serializer for TAXII Collection resource.
    """
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    can_read = serializers.BooleanField()
    can_write = serializers.BooleanField()
    media_types = serializers.ListField(child=serializers.CharField())


class TAXIICollectionsSerializer(serializers.Serializer):
    """
    Serializer for TAXII Collections resource.
    """
    collections = serializers.ListField(child=TAXIICollectionSerializer())


class TAXIIErrorSerializer(serializers.Serializer):
    """
    Serializer for TAXII Error message.
    """
    title = serializers.CharField()
    description = serializers.CharField(required=False)
    error_id = serializers.CharField(required=False)
    error_code = serializers.CharField(required=False)
    http_status = serializers.IntegerField(required=False)
    external_details = serializers.URLField(required=False)
    details = serializers.DictField(required=False)


class TAXIIStatusSerializer(serializers.Serializer):
    """
    Serializer for TAXII Status resource.
    """
    id = serializers.CharField()
    status = serializers.CharField()
    request_timestamp = serializers.DateTimeField()
    total_count = serializers.IntegerField()
    success_count = serializers.IntegerField()
    successes = serializers.ListField(child=serializers.CharField(), required=False)
    failure_count = serializers.IntegerField()
    failures = serializers.ListField(child=serializers.DictField(), required=False)
    pending_count = serializers.IntegerField()
    pendings = serializers.ListField(child=serializers.CharField(), required=False)