"""
Trust Serializers - Trust relationship model serialization for API responses
"""

from rest_framework import serializers
from core.models.models import TrustRelationship, TrustGroup, TrustLevel, Organization, CustomUser

class OrganizationBasicSerializer(serializers.ModelSerializer):
    """Basic organization serializer for trust relationships"""
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'domain', 'organization_type']
        read_only_fields = ['id']

class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for trust relationships"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'role']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name()

class TrustRelationshipSerializer(serializers.ModelSerializer):
    """Serializer for TrustRelationship model"""
    
    source_organization = OrganizationBasicSerializer(read_only=True)
    target_organization = OrganizationBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    last_modified_by = UserBasicSerializer(read_only=True)
    revoked_by = UserBasicSerializer(read_only=True)
    trust_level = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = TrustRelationship
        fields = [
            'id', 'source_organization', 'target_organization',
            'relationship_type', 'trust_level', 'status', 'is_bilateral', 'is_active',
            'valid_from', 'valid_until', 'sharing_preferences',
            'anonymization_level', 'access_level', 'approved_by_source', 
            'approved_by_target', 'created_by', 'last_modified_by', 
            'revoked_by', 'revoked_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'revoked_at', 'created_at', 'updated_at'
        ]

class TrustRelationshipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating trust relationships"""
    
    target_organization_id = serializers.UUIDField(write_only=True)
    trust_level_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = TrustRelationship
        fields = [
            'target_organization_id', 'trust_level_id', 'relationship_type',
            'is_bilateral', 'anonymization_level', 'access_level', 'notes'
        ]
    
    def validate_relationship_type(self, value):
        """Validate relationship type"""
        valid_types = ['bilateral', 'community', 'hierarchical', 'federation']
        if value not in valid_types:
            raise serializers.ValidationError(f"Relationship type must be one of: {', '.join(valid_types)}")
        return value

class TrustRelationshipResponseSerializer(serializers.Serializer):
    """Serializer for responding to trust requests"""
    
    action = serializers.ChoiceField(choices=['approve', 'deny'])
    trust_level_id = serializers.UUIDField(required=False)
    message = serializers.CharField(required=False, max_length=500)
    
    def validate(self, attrs):
        """Validate response data"""
        if attrs['action'] == 'approve' and not attrs.get('trust_level_id'):
            raise serializers.ValidationError("Trust level is required when approving trust request")
        return attrs

class TrustRelationshipUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating trust relationships"""
    
    trust_level_id = serializers.UUIDField(required=False)
    
    class Meta:
        model = TrustRelationship
        fields = [
            'trust_level_id', 'anonymization_level', 'access_level', 
            'is_bilateral', 'notes', 'sharing_preferences'
        ]

class TrustGroupSerializer(serializers.ModelSerializer):
    """Serializer for TrustGroup model"""
    
    default_trust_level = serializers.StringRelatedField(read_only=True)
    member_count = serializers.ReadOnlyField()
    
    class Meta:
        model = TrustGroup
        fields = [
            'id', 'name', 'description', 'group_type', 'is_public',
            'requires_approval', 'default_trust_level', 'group_policies',
            'is_active', 'created_by', 'administrators', 'member_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'member_count']

class TrustLevelSerializer(serializers.ModelSerializer):
    """Serializer for TrustLevel model"""
    
    class Meta:
        model = TrustLevel
        fields = [
            'id', 'name', 'level', 'description', 'numerical_value',
            'default_anonymization_level', 'default_access_level',
            'sharing_policies', 'is_active', 'is_system_default',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TrustRelationshipSummarySerializer(serializers.Serializer):
    """Serializer for trust relationship summary"""
    
    organization = OrganizationBasicSerializer(read_only=True)
    trust_level = serializers.CharField(read_only=True)
    relationship_type = serializers.CharField(read_only=True)  # 'bilateral' or 'community'
    status = serializers.CharField(read_only=True)
    established_at = serializers.DateTimeField(read_only=True)

class TrustLevelSummarySerializer(serializers.Serializer):
    """Serializer for trust level summary statistics"""
    
    trust_level = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()

class TrustDashboardSerializer(serializers.Serializer):
    """Serializer for trust dashboard data"""
    
    total_relationships = serializers.IntegerField()
    active_relationships = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    outgoing_requests = serializers.IntegerField()
    incoming_requests = serializers.IntegerField()
    trust_level_distribution = TrustLevelSummarySerializer(many=True)
    recent_activities = serializers.ListField(child=serializers.DictField())
    trusted_organizations = OrganizationBasicSerializer(many=True)

class TrustMetricsSerializer(serializers.Serializer):
    """Serializer for trust metrics"""
    
    organization = OrganizationBasicSerializer()
    trust_score = serializers.FloatField()
    relationship_count = serializers.IntegerField()
    average_trust_level = serializers.FloatField()
    trust_diversity = serializers.FloatField()
    last_activity = serializers.DateTimeField()

class TrustHistorySerializer(serializers.Serializer):
    """Serializer for trust relationship history"""
    
    timestamp = serializers.DateTimeField()
    action = serializers.CharField()
    old_trust_level = serializers.CharField(allow_null=True)
    new_trust_level = serializers.CharField(allow_null=True)
    performed_by = UserBasicSerializer()
    message = serializers.CharField(allow_null=True)
    
class TrustValidationSerializer(serializers.Serializer):
    """Serializer for trust validation operations"""
    
    organization_id = serializers.UUIDField()
    required_trust_level = serializers.CharField()
    current_trust_level = serializers.CharField()
    is_valid = serializers.BooleanField()
    validation_message = serializers.CharField()

class TrustRecommendationSerializer(serializers.Serializer):
    """Serializer for trust recommendations"""
    
    organization = OrganizationBasicSerializer()
    recommended_trust_level = serializers.CharField()
    confidence_score = serializers.FloatField()
    reasoning = serializers.CharField()
    factors = serializers.ListField(child=serializers.DictField())
    
class TrustNetworkSerializer(serializers.Serializer):
    """Serializer for trust network visualization data"""
    
    nodes = serializers.ListField(child=serializers.DictField())
    edges = serializers.ListField(child=serializers.DictField())
    metrics = serializers.DictField()
    
class TrustAccessLogSerializer(serializers.Serializer):
    """Serializer for trust access logging"""
    
    timestamp = serializers.DateTimeField()
    accessing_organization = OrganizationBasicSerializer()
    accessed_organization = OrganizationBasicSerializer()
    resource_type = serializers.CharField()
    resource_id = serializers.CharField()
    access_granted = serializers.BooleanField()
    trust_level_used = serializers.CharField()
    anonymization_applied = serializers.CharField()