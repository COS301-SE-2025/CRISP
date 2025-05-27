from rest_framework import serializers
from trust.models import TrustRelationship, TrustGroup, TrustGroupMembership
from core.models import Organization

class TrustRelationshipSerializer(serializers.ModelSerializer):
    """
    Serializer for TrustRelationship model.
    """
    source_organization_name = serializers.ReadOnlyField(source='source_organization.name')
    target_organization_name = serializers.ReadOnlyField(source='target_organization.name')
    
    class Meta:
        model = TrustRelationship
        fields = ['id', 'source_organization', 'source_organization_name', 
                  'target_organization', 'target_organization_name',
                  'trust_level_name', 'trust_level', 'anonymization_strategy',
                  'created_at', 'updated_at', 'notes']
        read_only_fields = ['id', 'source_organization', 'source_organization_name',
                           'trust_level', 'anonymization_strategy',
                           'created_at', 'updated_at']
        
    def validate_target_organization(self, value):
        """
        Validate that the target organization is not the same as the source.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Get source organization
            source_org = Organization.objects.filter(
                id__in=request.user.groups.values_list('name', flat=True)
            ).first()
            
            if source_org and value == source_org:
                raise serializers.ValidationError(
                    "Target organization cannot be the same as source organization"
                )
        return value


class TrustGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for TrustGroup model.
    """
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TrustGroup
        fields = ['id', 'name', 'description', 'default_trust_level_name',
                  'default_trust_level', 'created_at', 'updated_at', 'member_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'default_trust_level', 'member_count']
        
    def get_member_count(self, obj):
        """
        Get the number of organizations in the trust group.
        """
        return TrustGroupMembership.objects.filter(trust_group=obj).count()


class TrustGroupMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for TrustGroupMembership model.
    """
    organization_name = serializers.ReadOnlyField(source='organization.name')
    trust_group_name = serializers.ReadOnlyField(source='trust_group.name')
    
    class Meta:
        model = TrustGroupMembership
        fields = ['id', 'trust_group', 'trust_group_name', 'organization',
                  'organization_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'organization_name', 'trust_group_name']