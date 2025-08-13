"""
Serializers for ThreatFeed model.
"""
from rest_framework import serializers
from core.models.models import ThreatFeed

class ThreatFeedSerializer(serializers.ModelSerializer):
    """
    Serializer for ThreatFeed model.
    """
    class Meta:
        model = ThreatFeed
        fields = [
            'id', 'name', 'description', 'owner', 'created_at', 'updated_at',
            'is_public', 'is_active', 'taxii_collection_id', 'taxii_server_url',
            'taxii_api_root', 'taxii_username', 'last_sync', 'is_external'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync']
        extra_kwargs = {
            'taxii_password': {'write_only': True}
        }