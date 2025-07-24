from rest_framework import serializers
from .models import Organization, CustomUser

class OrganizationUserSerializer(serializers.ModelSerializer):
    """Serializer for user information within an organization context."""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'is_active']

class OrganizationSerializer(serializers.ModelSerializer):
    """Basic serializer for Organization model."""
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'domain', 'organization_type', 
            'is_publisher', 'is_verified', 'is_active'
        ]

class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Organization model, including user list."""
    users = OrganizationUserSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'description', 'domain', 'contact_email', 
            'website', 'organization_type', 'is_publisher', 'is_verified', 
            'is_active', 'created_at', 'updated_at', 'users'
        ]
        read_only_fields = ['created_at', 'updated_at']
