"""Serializers for feed consumption API"""
from rest_framework import serializers
from .models import ExternalFeedSource, FeedConsumptionLog

class ExternalFeedSourceSerializer(serializers.ModelSerializer):
    """Serializer for feed sources"""
    
    class Meta:
        model = ExternalFeedSource
        fields = [
            'id', 'name', 'description', 'discovery_url', 'api_root_url', 
            'collection_id', 'collection_name', 'categories', 'poll_interval', 
            'auth_type', 'last_poll_time', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'api_root_url', 'last_poll_time', 'created_at', 'updated_at']
        extra_kwargs = {
            'auth_credentials': {'write_only': True},
            'headers': {'write_only': True}
        }

class FeedConsumptionLogSerializer(serializers.ModelSerializer):
    """Serializer for consumption logs"""
    feed_source_name = serializers.CharField(source='feed_source.name', read_only=True)
    
    class Meta:
        model = FeedConsumptionLog
        fields = [
            'id', 'feed_source', 'feed_source_name', 'status', 'objects_processed',
            'objects_added', 'objects_updated', 'objects_failed', 
            'start_time', 'end_time', 'execution_time_seconds', 
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = fields

class CollectionSerializer(serializers.Serializer):
    """Serializer for TAXII collections"""
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    can_read = serializers.BooleanField()
    can_write = serializers.BooleanField()
    media_types = serializers.ListField(child=serializers.CharField(), required=False)

class ApiRootSerializer(serializers.Serializer):
    """Serializer for TAXII API roots"""
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    max_content_length = serializers.IntegerField(required=False)
    versions = serializers.ListField(child=serializers.CharField(), required=False)

class DiscoverySerializer(serializers.Serializer):
    """Serializer for TAXII discovery endpoint response"""
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    api_roots = serializers.ListField(child=serializers.CharField())
    default_api_root = serializers.CharField(allow_null=True, required=False)
