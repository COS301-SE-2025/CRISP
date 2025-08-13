"""
Trust Serializers - Trust relationship model serialization for API responses
"""

from rest_framework import serializers
from core.models.models import BilateralTrust, CommunityTrust, Organization, CustomUser

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

class BilateralTrustSerializer(serializers.ModelSerializer):
    """Serializer for BilateralTrust model"""
    
    requesting_organization = OrganizationBasicSerializer(read_only=True)
    responding_organization = OrganizationBasicSerializer(read_only=True)
    requested_by = UserBasicSerializer(read_only=True)
    accepted_by = UserBasicSerializer(read_only=True)
    rejected_by = UserBasicSerializer(read_only=True)
    revoked_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = BilateralTrust
        fields = [
            'id', 'requesting_organization', 'responding_organization',
            'status', 'trust_level', 'requested_at', 'responded_at',
            'request_message', 'response_message', 'requested_by',
            'accepted_by', 'rejected_by', 'revoked_by', 'revoked_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requested_at', 'responded_at', 'revoked_at',
            'created_at', 'updated_at'
        ]

class BilateralTrustCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bilateral trust requests"""
    
    responding_organization_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = BilateralTrust
        fields = ['responding_organization_id', 'trust_level', 'request_message']
    
    def validate_trust_level(self, value):
        """Validate trust level"""
        valid_levels = ['none', 'minimal', 'moderate', 'standard', 'full']
        if value not in valid_levels:
            raise serializers.ValidationError(f"Trust level must be one of: {', '.join(valid_levels)}")
        return value

class BilateralTrustResponseSerializer(serializers.Serializer):
    """Serializer for responding to bilateral trust requests"""
    
    action = serializers.ChoiceField(choices=['accept', 'reject'])
    trust_level = serializers.CharField(required=False)
    message = serializers.CharField(required=False, max_length=500)
    
    def validate(self, attrs):
        """Validate response data"""
        if attrs['action'] == 'accept' and not attrs.get('trust_level'):
            raise serializers.ValidationError("Trust level is required when accepting trust request")
        return attrs
    
    def validate_trust_level(self, value):
        """Validate trust level"""
        if value:
            valid_levels = ['none', 'minimal', 'moderate', 'standard', 'full']
            if value not in valid_levels:
                raise serializers.ValidationError(f"Trust level must be one of: {', '.join(valid_levels)}")
        return value

class BilateralTrustUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating bilateral trust levels"""
    
    class Meta:
        model = BilateralTrust
        fields = ['trust_level', 'response_message']
    
    def validate_trust_level(self, value):
        """Validate trust level"""
        valid_levels = ['none', 'minimal', 'moderate', 'standard', 'full']
        if value not in valid_levels:
            raise serializers.ValidationError(f"Trust level must be one of: {', '.join(valid_levels)}")
        return value

class CommunityTrustSerializer(serializers.ModelSerializer):
    """Serializer for CommunityTrust model"""
    
    class Meta:
        model = CommunityTrust
        fields = [
            'id', 'trust_type', 'description', 'trust_level',
            'status', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TrustRelationshipSerializer(serializers.Serializer):
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