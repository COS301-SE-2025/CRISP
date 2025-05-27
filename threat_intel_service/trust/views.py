from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.models import Organization
from trust.models import TrustRelationship, TrustGroup, TrustGroupMembership
from trust.serializers import (
    TrustRelationshipSerializer, TrustGroupSerializer, 
    TrustGroupMembershipSerializer
)
from audit.models import AuditLog

class TrustRelationshipViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing trust relationships between organizations.
    """
    queryset = TrustRelationship.objects.all()
    serializer_class = TrustRelationshipSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['source_organization', 'target_organization', 'trust_level_name']
    search_fields = ['source_organization__name', 'target_organization__name', 'notes']
    ordering_fields = ['created_at', 'trust_level']
    ordering = ['-trust_level']
    
    def get_organization(self, request):
        """
        Get the organization associated with the authenticated user.
        """
        try:
            return Organization.objects.filter(
                id__in=request.user.groups.values_list('name', flat=True)
            ).first()
        except Organization.DoesNotExist:
            if settings.DEBUG:
                return Organization.objects.create(
                    name=f"{request.user.username}'s Organization",
                    identity_class="organization"
                )
            raise Exception("No organization found for authenticated user")
    
    def perform_create(self, serializer):
        """
        Set the source organization when creating a trust relationship.
        """
        organization = self.get_organization(self.request)
        serializer.save(source_organization=organization)
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='create_trust_relationship',
            object_id=str(serializer.instance.id),
            details={
                'target_organization': str(serializer.instance.target_organization.id),
                'trust_level_name': serializer.instance.trust_level_name
            }
        )
    
    def perform_update(self, serializer):
        """
        Ensure user can only update trust relationships for their organization.
        """
        organization = self.get_organization(self.request)
        
        # Check if user's organization is the source
        if serializer.instance.source_organization != organization:
            raise Exception("You can only update trust relationships for your organization")
            
        serializer.save()
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='update_trust_relationship',
            object_id=str(serializer.instance.id),
            details={
                'target_organization': str(serializer.instance.target_organization.id),
                'trust_level_name': serializer.instance.trust_level_name
            }
        )
    
    def perform_destroy(self, instance):
        """
        Ensure user can only delete trust relationships for their organization.
        """
        organization = self.get_organization(self.request)
        
        # Check if user's organization is the source
        if instance.source_organization != organization:
            raise Exception("You can only delete trust relationships for your organization")
            
        # Store data for logging
        relationship_id = str(instance.id)
        target_org = str(instance.target_organization.id)
        trust_level = instance.trust_level_name
        
        instance.delete()
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='delete_trust_relationship',
            object_id=relationship_id,
            details={
                'target_organization': target_org,
                'trust_level_name': trust_level
            }
        )
    
    def get_queryset(self):
        """
        Limit trust relationships to those involving the user's organization.
        """
        organization = self.get_organization(self.request)
        
        # Return relationships where user's organization is the source
        return TrustRelationship.objects.filter(source_organization=organization)
    
    @action(detail=False, methods=['get'])
    def trusted_organizations(self, request):
        """
        Get all organizations trusted by the user's organization.
        """
        organization = self.get_organization(request)
        
        # Get all trust relationships
        relationships = TrustRelationship.objects.filter(source_organization=organization)
        
        # Get target organizations with trust levels
        trusted_orgs = []
        for rel in relationships:
            trusted_orgs.append({
                'organization_id': str(rel.target_organization.id),
                'organization_name': rel.target_organization.name,
                'trust_level_name': rel.trust_level_name,
                'trust_level': rel.trust_level,
                'relationship_id': str(rel.id)
            })
            
        return Response(trusted_orgs)
    
    @action(detail=False, methods=['get'])
    def trusting_organizations(self, request):
        """
        Get all organizations that trust the user's organization.
        """
        organization = self.get_organization(request)
        
        # Get all trust relationships
        relationships = TrustRelationship.objects.filter(target_organization=organization)
        
        # Get source organizations with trust levels
        trusting_orgs = []
        for rel in relationships:
            trusting_orgs.append({
                'organization_id': str(rel.source_organization.id),
                'organization_name': rel.source_organization.name,
                'trust_level_name': rel.trust_level_name,
                'trust_level': rel.trust_level,
                'relationship_id': str(rel.id)
            })
            
        return Response(trusting_orgs)


class TrustGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing trust groups.
    """
    queryset = TrustGroup.objects.all()
    serializer_class = TrustGroupSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['default_trust_level_name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_organization(self, request):
        """
        Get the organization associated with the authenticated user.
        """
        try:
            return Organization.objects.filter(
                id__in=request.user.groups.values_list('name', flat=True)
            ).first()
        except Organization.DoesNotExist:
            if settings.DEBUG:
                return Organization.objects.create(
                    name=f"{request.user.username}'s Organization",
                    identity_class="organization"
                )
            raise Exception("No organization found for authenticated user")
    
    def perform_create(self, serializer):
        """
        Log the creation of a trust group.
        """
        serializer.save()
        
        # Log the action
        organization = self.get_organization(self.request)
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='create_trust_group',
            object_id=str(serializer.instance.id),
            details={
                'name': serializer.instance.name,
                'default_trust_level': serializer.instance.default_trust_level_name
            }
        )
    
    def perform_update(self, serializer):
        """
        Log the update of a trust group.
        """
        serializer.save()
        
        # Log the action
        organization = self.get_organization(self.request)
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='update_trust_group',
            object_id=str(serializer.instance.id),
            details={
                'name': serializer.instance.name,
                'default_trust_level': serializer.instance.default_trust_level_name
            }
        )
    
    def perform_destroy(self, instance):
        """
        Log the deletion of a trust group.
        """
        # Store data for logging
        group_id = str(instance.id)
        name = instance.name
        
        instance.delete()
        
        # Log the action
        organization = self.get_organization(self.request)
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='delete_trust_group',
            object_id=group_id,
            details={
                'name': name
            }
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        Get all members of a trust group.
        """
        group = self.get_object()
        
        # Get all memberships
        memberships = TrustGroupMembership.objects.filter(trust_group=group)
        
        # Get organizations
        members = []
        for membership in memberships:
            members.append({
                'organization_id': str(membership.organization.id),
                'organization_name': membership.organization.name,
                'membership_id': str(membership.id),
                'joined_at': membership.created_at
            })
            
        return Response(members)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """
        Add a member to a trust group.
        """
        group = self.get_object()
        
        # Get the organization to add
        org_id = request.data.get('organization_id')
        if not org_id:
            return Response(
                {"error": "organization_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            organization = Organization.objects.get(id=org_id)
            
            # Check if already a member
            existing = TrustGroupMembership.objects.filter(
                trust_group=group,
                organization=organization
            ).exists()
            
            if existing:
                return Response(
                    {"message": "Organization is already a member of this group"},
                    status=status.HTTP_200_OK
                )
                
            # Add to group
            membership = TrustGroupMembership.objects.create(
                trust_group=group,
                organization=organization
            )
            
            # Log the action
            user_org = self.get_organization(request)
            AuditLog.objects.create(
                user=request.user,
                organization=user_org,
                action_type='add_trust_group_member',
                object_id=str(group.id),
                details={
                    'group_name': group.name,
                    'organization_id': str(organization.id),
                    'organization_name': organization.name
                }
            )
            
            return Response(
                {"message": "Organization added to group", "membership_id": str(membership.id)},
                status=status.HTTP_201_CREATED
            )
            
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """
        Remove a member from a trust group.
        """
        group = self.get_object()
        
        # Get the organization to remove
        org_id = request.data.get('organization_id')
        if not org_id:
            return Response(
                {"error": "organization_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            organization = Organization.objects.get(id=org_id)
            
            # Check if a member
            try:
                membership = TrustGroupMembership.objects.get(
                    trust_group=group,
                    organization=organization
                )
                
                # Remove from group
                membership.delete()
                
                # Log the action
                user_org = self.get_organization(request)
                AuditLog.objects.create(
                    user=request.user,
                    organization=user_org,
                    action_type='remove_trust_group_member',
                    object_id=str(group.id),
                    details={
                        'group_name': group.name,
                        'organization_id': str(organization.id),
                        'organization_name': organization.name
                    }
                )
                
                return Response(
                    {"message": "Organization removed from group"},
                    status=status.HTTP_200_OK
                )
                
            except TrustGroupMembership.DoesNotExist:
                return Response(
                    {"error": "Organization is not a member of this group"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def apply_trust(self, request, pk=None):
        """
        Apply trust relationships to all members of the group.
        """
        group = self.get_object()
        user_org = self.get_organization(request)
        
        # Get all memberships
        memberships = TrustGroupMembership.objects.filter(trust_group=group)
        
        # Set up trust relationships
        created_count = 0
        updated_count = 0
        
        for membership in memberships:
            target_org = membership.organization
            
            # Skip if this is the user's organization
            if target_org == user_org:
                continue
                
            # Check if relationship already exists
            existing = TrustRelationship.objects.filter(
                source_organization=user_org,
                target_organization=target_org
            ).first()
            
            if existing:
                # Update existing relationship
                existing.trust_level_name = group.default_trust_level_name
                existing.trust_level = group.default_trust_level
                existing.save()
                updated_count += 1
            else:
                # Create new relationship
                TrustRelationship.objects.create(
                    source_organization=user_org,
                    target_organization=target_org,
                    trust_level_name=group.default_trust_level_name,
                    trust_level=group.default_trust_level
                )
                created_count += 1
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            organization=user_org,
            action_type='apply_trust_group',
            object_id=str(group.id),
            details={
                'group_name': group.name,
                'created_count': created_count,
                'updated_count': updated_count,
                'default_trust_level': group.default_trust_level_name
            }
        )
        
        return Response({
            "message": f"Trust relationships applied. Created: {created_count}, Updated: {updated_count}",
            "created_count": created_count,
            "updated_count": updated_count
        })


class TrustGroupMembershipViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing trust group memberships.
    """
    queryset = TrustGroupMembership.objects.all()
    serializer_class = TrustGroupMembershipSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['trust_group', 'organization']
    ordering_fields = ['created_at']
    ordering = ['-created_at']