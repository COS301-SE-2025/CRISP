"""
Organization Serializers - Organization model serialization for API responses
"""

from rest_framework import serializers
from core.models.models import Organization, CustomUser

class OrganizationSerializer(serializers.ModelSerializer):
    """Basic organization serializer"""
    
    member_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'domain', 'organization_type', 'description',
            'is_active', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Detailed organization serializer with additional information"""
    
    member_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'domain', 'organization_type', 'description',
            'contact_email', 'website', 'is_active', 'member_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'domain', 'created_at', 'updated_at']

class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new organizations"""
    
    class Meta:
        model = Organization
        fields = [
            'name', 'domain', 'organization_type', 'description',
            'contact_email', 'website'
        ]
    
    def validate_domain(self, value):
        """Validate domain uniqueness"""
        if Organization.objects.filter(domain=value).exists():
            raise serializers.ValidationError("This domain is already registered")
        return value
    
    def validate_contact_email(self, value):
        """Validate contact email format"""
        if value and '@' not in value:
            raise serializers.ValidationError("Invalid email format")
        return value

class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating organizations"""
    
    class Meta:
        model = Organization
        fields = [
            'name', 'description', 'contact_email', 'website', 'is_active'
        ]
    
    def validate_contact_email(self, value):
        """Validate contact email format"""
        if value and '@' not in value:
            raise serializers.ValidationError("Invalid email format")
        return value

class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for organization members"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'is_verified', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()

class OrganizationSummarySerializer(serializers.ModelSerializer):
    """Minimal organization serializer for lists and references"""
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'domain', 'organization_type']
        read_only_fields = ['id']

class OrganizationStatisticsSerializer(serializers.Serializer):
    """Serializer for organization statistics"""
    
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    role_distribution = serializers.DictField()
    trust_relationships = serializers.IntegerField()
    active_trust_relationships = serializers.IntegerField()
    trust_level_distribution = serializers.DictField()
    recent_activities = serializers.ListField(child=serializers.DictField())
    data_sharing_stats = serializers.DictField()
    
class OrganizationTrustMetricsSerializer(serializers.Serializer):
    """Serializer for organization trust metrics"""
    
    trust_score = serializers.FloatField()
    trustworthiness_rating = serializers.CharField()
    relationship_count = serializers.IntegerField()
    average_trust_level = serializers.FloatField()
    trust_diversity = serializers.FloatField()
    reciprocity_rate = serializers.FloatField()
    last_trust_activity = serializers.DateTimeField(allow_null=True)

class OrganizationTypeSerializer(serializers.Serializer):
    """Serializer for organization type choices"""
    
    value = serializers.CharField()
    display = serializers.CharField()

class OrganizationSearchSerializer(serializers.Serializer):
    """Serializer for organization search results"""
    
    organizations = OrganizationSerializer(many=True)
    total_count = serializers.IntegerField()
    search_query = serializers.CharField()
    filters_applied = serializers.DictField()

class OrganizationActivitySerializer(serializers.Serializer):
    """Serializer for organization activity logs"""
    
    timestamp = serializers.DateTimeField()
    activity_type = serializers.CharField()
    description = serializers.CharField()
    user = serializers.CharField()
    metadata = serializers.DictField(required=False)

class OrganizationConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for organization configuration settings"""
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'data_sharing_policy', 'anonymization_level',
            'auto_accept_trust_requests', 'notification_preferences'
        ]
        read_only_fields = ['id', 'name']

class OrganizationInviteSerializer(serializers.Serializer):
    """Serializer for organization invite operations"""
    
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[
        ('viewer', 'Viewer'),
        ('analyst', 'Analyst'),
        ('admin', 'Admin'),
        ('publisher', 'Publisher')
    ])
    message = serializers.CharField(max_length=500, required=False)

class OrganizationTransferSerializer(serializers.Serializer):
    """Serializer for organization ownership transfer"""
    
    new_owner_id = serializers.UUIDField()
    transfer_reason = serializers.CharField(max_length=200)
    confirm_transfer = serializers.BooleanField()
    
    def validate_confirm_transfer(self, value):
        if not value:
            raise serializers.ValidationError("Transfer confirmation is required")
        return value