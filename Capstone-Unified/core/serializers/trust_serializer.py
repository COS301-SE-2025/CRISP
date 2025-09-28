"""
Trust Serializers - Trust relationship and trust group serialization for API responses
"""

from rest_framework import serializers
from core.models.models import TrustRelationship, TrustLevel, Organization
from core.trust_management.models import TrustGroup, TrustGroupMembership

class TrustLevelSerializer(serializers.ModelSerializer):
    """Serializer for trust levels"""

    class Meta:
        model = TrustLevel
        fields = [
            'id', 'name', 'level', 'description', 'numerical_value',
            'default_anonymization_level', 'default_access_level',
            'sharing_policies', 'is_system_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrganizationSummarySerializer(serializers.ModelSerializer):
    """Minimal organization serializer for trust relationships"""

    class Meta:
        model = Organization
        fields = ['id', 'name', 'domain', 'organization_type']
        read_only_fields = ['id']

class TrustRelationshipSerializer(serializers.ModelSerializer):
    """Detailed trust relationship serializer"""

    source_organization = OrganizationSummarySerializer(read_only=True)
    target_organization = OrganizationSummarySerializer(read_only=True)
    trust_level = TrustLevelSerializer(read_only=True)

    class Meta:
        model = TrustRelationship
        fields = [
            'id', 'source_organization', 'target_organization', 'trust_level',
            'relationship_type', 'status', 'is_bilateral', 'is_active',
            'anonymization_level', 'access_level', 'sharing_preferences',
            'notes', 'created_at', 'updated_at', 'valid_until'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TrustRelationshipSummarySerializer(serializers.ModelSerializer):
    """Summary trust relationship serializer for lists"""

    source_organization_name = serializers.CharField(source='source_organization.name', read_only=True)
    target_organization_name = serializers.CharField(source='target_organization.name', read_only=True)
    trust_level_name = serializers.CharField(source='trust_level.name', read_only=True)

    class Meta:
        model = TrustRelationship
        fields = [
            'id', 'source_organization_name', 'target_organization_name',
            'trust_level_name', 'relationship_type', 'status', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TrustRelationshipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating trust relationships"""

    source_organization_id = serializers.UUIDField(write_only=True)
    target_organization_id = serializers.UUIDField(write_only=True)
    trust_level_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = TrustRelationship
        fields = [
            'source_organization_id', 'target_organization_id', 'trust_level_id',
            'relationship_type', 'is_bilateral', 'anonymization_level',
            'access_level', 'sharing_preferences', 'notes'
        ]

    def validate(self, data):
        """Validate trust relationship data"""
        # Check if organizations exist
        try:
            source_org = Organization.objects.get(id=data['source_organization_id'])
            target_org = Organization.objects.get(id=data['target_organization_id'])
        except Organization.DoesNotExist:
            raise serializers.ValidationError("One or both organizations do not exist")

        # Check if trust level exists
        try:
            trust_level = TrustLevel.objects.get(id=data['trust_level_id'])
        except TrustLevel.DoesNotExist:
            raise serializers.ValidationError("Trust level does not exist")

        # Prevent self-trust
        if source_org.id == target_org.id:
            raise serializers.ValidationError("Cannot create trust relationship with the same organization")

        # Check for existing relationship
        existing = TrustRelationship.objects.filter(
            source_organization=source_org,
            target_organization=target_org,
            is_active=True
        ).exists()

        if existing:
            raise serializers.ValidationError("Trust relationship already exists between these organizations")

        return data

class TrustGroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for trust group membership"""

    organization = OrganizationSummarySerializer(read_only=True)

    class Meta:
        model = TrustGroupMembership
        fields = [
            'id', 'organization', 'membership_type', 'is_active', 'joined_at',
            'left_at', 'invited_by', 'approved_by'
        ]
        read_only_fields = ['id', 'joined_at']

class TrustGroupSerializer(serializers.ModelSerializer):
    """Detailed trust group serializer"""

    members = TrustGroupMembershipSerializer(source='group_memberships', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    organization_count = serializers.SerializerMethodField()

    class Meta:
        model = TrustGroup
        fields = [
            'id', 'name', 'description', 'group_type', 'is_active',
            'is_public', 'requires_approval', 'group_policies', 
            'created_at', 'updated_at', 'created_by', 'members',
            'member_count', 'organization_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        """Get total member count"""
        return obj.group_memberships.filter(is_active=True).count()

    def get_organization_count(self, obj):
        """Get unique organization count"""
        return obj.group_memberships.filter(
            is_active=True
        ).values('organization').distinct().count()

class TrustGroupSummarySerializer(serializers.ModelSerializer):
    """Summary trust group serializer for lists"""

    member_count = serializers.SerializerMethodField()

    class Meta:
        model = TrustGroup
        fields = [
            'id', 'name', 'description', 'group_type', 'is_active',
            'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        """Get total member count"""
        return obj.trustgroupmembership_set.filter(is_active=True).count()

class TrustGroupCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating trust groups"""

    initial_members = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of organization IDs to add as initial members"
    )

    class Meta:
        model = TrustGroup
        fields = [
            'name', 'description', 'group_type', 'access_policy',
            'sharing_policy', 'governance_model', 'metadata', 'initial_members'
        ]

    def validate_name(self, value):
        """Validate trust group name uniqueness"""
        if TrustGroup.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("Trust group with this name already exists")
        return value

    def validate_initial_members(self, value):
        """Validate initial members exist"""
        if value:
            existing_orgs = Organization.objects.filter(
                id__in=value, is_active=True
            ).count()
            if existing_orgs != len(value):
                raise serializers.ValidationError("Some organizations do not exist or are inactive")
        return value