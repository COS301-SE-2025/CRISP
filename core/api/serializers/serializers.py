"""
Trust Management Serializers

Django REST Framework serializers for trust management models.
"""

from rest_framework import serializers
from django.utils import timezone
from ...models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership,
    TrustLog, SharingPolicy
)


class TrustLevelSerializer(serializers.ModelSerializer):
    """Serializer for TrustLevel model."""
    
    class Meta:
        model = TrustLevel
        fields = [
            'id', 'name', 'level', 'description', 'numerical_value',
            'default_anonymization_level', 'default_access_level',
            'sharing_policies', 'is_active', 'is_system_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrustGroupSerializer(serializers.ModelSerializer):
    """Serializer for TrustGroup model."""
    
    default_trust_level_name = serializers.CharField(source='default_trust_level.name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TrustGroup
        fields = [
            'id', 'name', 'description', 'group_type', 'is_public',
            'requires_approval', 'default_trust_level', 'default_trust_level_name',
            'group_policies', 'is_active', 'created_at', 'updated_at',
            'created_by', 'administrators', 'member_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'member_count']
    
    def get_member_count(self, obj):
        """Get the number of active members in the group."""
        return obj.get_member_count()


class TrustRelationshipSerializer(serializers.ModelSerializer):
    """Serializer for TrustRelationship model."""
    
    trust_level_name = serializers.CharField(source='trust_level.name', read_only=True)
    trust_group_name = serializers.CharField(source='trust_group.name', read_only=True)
    is_effective = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    is_fully_approved = serializers.SerializerMethodField()
    effective_access_level = serializers.SerializerMethodField()
    effective_anonymization_level = serializers.SerializerMethodField()
    
    class Meta:
        model = TrustRelationship
        fields = [
            'id', 'source_organization', 'target_organization',
            'relationship_type', 'trust_level', 'trust_level_name',
            'trust_group', 'trust_group_name', 'status', 'is_bilateral',
            'is_active', 'valid_from', 'valid_until', 'sharing_preferences',
            'anonymization_level', 'access_level', 'approved_by_source',
            'approved_by_target', 'approved_by_source_user', 'approved_by_target_user',
            'metadata', 'notes', 'created_at', 'updated_at', 'activated_at',
            'revoked_at', 'created_by', 'last_modified_by', 'revoked_by',
            'is_effective', 'is_expired', 'is_fully_approved',
            'effective_access_level', 'effective_anonymization_level'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'activated_at', 'revoked_at',
            'is_effective', 'is_expired', 'is_fully_approved',
            'effective_access_level', 'effective_anonymization_level'
        ]
    
    def get_is_effective(self, obj):
        """Check if the relationship is currently effective."""
        return obj.is_effective
    
    def get_is_expired(self, obj):
        """Check if the relationship is expired."""
        return obj.is_expired
    
    def get_is_fully_approved(self, obj):
        """Check if the relationship is fully approved."""
        return obj.is_fully_approved
    
    def get_effective_access_level(self, obj):
        """Get the effective access level."""
        return obj.get_effective_access_level()
    
    def get_effective_anonymization_level(self, obj):
        """Get the effective anonymization level."""
        return obj.get_effective_anonymization_level()


class TrustGroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for TrustGroupMembership model."""
    
    trust_group_name = serializers.CharField(source='trust_group.name', read_only=True)
    
    class Meta:
        model = TrustGroupMembership
        fields = [
            'id', 'trust_group', 'trust_group_name', 'organization',
            'membership_type', 'is_active', 'joined_at', 'left_at',
            'invited_by', 'approved_by'
        ]
        read_only_fields = ['id', 'joined_at', 'left_at']


class TrustLogSerializer(serializers.ModelSerializer):
    """Serializer for TrustLog model."""
    
    class Meta:
        model = TrustLog
        fields = [
            'id', 'action', 'source_organization', 'target_organization',
            'trust_relationship', 'trust_group', 'user', 'ip_address',
            'user_agent', 'success', 'failure_reason', 'details', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class SharingPolicySerializer(serializers.ModelSerializer):
    """Serializer for SharingPolicy model."""
    
    class Meta:
        model = SharingPolicy
        fields = [
            'id', 'name', 'description', 'allowed_stix_types',
            'blocked_stix_types', 'max_tlp_level', 'max_age_days',
            'require_anonymization', 'anonymization_rules',
            'allow_attribution', 'additional_constraints',
            'is_active', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Input serializers for specific operations
class CreateTrustRelationshipSerializer(serializers.Serializer):
    """Serializer for creating trust relationships."""
    
    target_organization = serializers.UUIDField()
    trust_level_name = serializers.CharField(max_length=255)
    relationship_type = serializers.ChoiceField(
        choices=['bilateral', 'community', 'hierarchical', 'federation'],
        default='bilateral'
    )
    sharing_preferences = serializers.JSONField(required=False, default=dict)
    valid_until = serializers.DateTimeField(required=False)
    notes = serializers.CharField(max_length=2000, required=False, default='')


class ApproveTrustRelationshipSerializer(serializers.Serializer):
    """Serializer for approving trust relationships."""
    
    relationship_id = serializers.UUIDField()


class RevokeTrustRelationshipSerializer(serializers.Serializer):
    """Serializer for revoking trust relationships."""
    
    relationship_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=1000, required=False)


class CreateTrustGroupSerializer(serializers.Serializer):
    """Serializer for creating trust groups."""
    
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=2000)
    group_type = serializers.ChoiceField(
        choices=['community', 'sector', 'geography', 'purpose', 'federation'],
        default='community'
    )
    is_public = serializers.BooleanField(default=False)
    requires_approval = serializers.BooleanField(default=True)
    default_trust_level_name = serializers.CharField(max_length=255, required=False)
    group_policies = serializers.JSONField(required=False, default=dict)


class JoinTrustGroupSerializer(serializers.Serializer):
    """Serializer for joining trust groups."""
    
    group_id = serializers.UUIDField()
    membership_type = serializers.ChoiceField(
        choices=['member', 'administrator', 'moderator'],
        default='member'
    )
    invited_by = serializers.UUIDField(required=False)


class LeaveTrustGroupSerializer(serializers.Serializer):
    """Serializer for leaving trust groups."""
    
    group_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=1000, required=False)


class CheckTrustSerializer(serializers.Serializer):
    """Serializer for checking trust levels."""
    
    target_organization = serializers.UUIDField()


class TestIntelligenceAccessSerializer(serializers.Serializer):
    """Serializer for testing intelligence access."""
    
    intelligence_owner = serializers.UUIDField()
    required_access_level = serializers.ChoiceField(
        choices=['none', 'read', 'subscribe', 'contribute', 'full'],
        default='read'
    )
    resource_type = serializers.CharField(max_length=100, required=False)


class UpdateTrustLevelSerializer(serializers.Serializer):
    """Serializer for updating trust levels."""
    
    relationship_id = serializers.UUIDField()
    new_trust_level_name = serializers.CharField(max_length=255)
    reason = serializers.CharField(max_length=1000, required=False)