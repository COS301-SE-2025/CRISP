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
            'is_public', 'taxii_collection_id', 'taxii_server_url',
            'taxii_api_root', 'taxii_username', 'taxii_password', 'last_sync', 'is_external'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync']
        extra_kwargs = {
            'taxii_password': {'write_only': True},
            'owner': {'required': False}
        }

    def create(self, validated_data):
        # If no owner is provided, create or get a default organization
        if 'owner' not in validated_data:
            from core.models.models import Organization
            default_org, created = Organization.objects.get_or_create(
                name='Default Organization',
                defaults={
                    'description': 'Default organization for threat feeds',
                    'organization_type': 'educational'
                }
            )
            validated_data['owner'] = default_org
        return super().create(validated_data)