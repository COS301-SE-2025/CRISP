"""
Trust Group Management Views

REST API views for trust group and membership operations.
"""

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Q
from django.core.exceptions import ValidationError
from typing import Dict, Any
import django.db.models

from ..models import TrustGroup, TrustGroupMembership, TrustLevel
from ..serializers import (
    TrustGroupSerializer, TrustGroupMembershipSerializer,
    CreateTrustGroupSerializer, JoinTrustGroupSerializer,
    LeaveTrustGroupSerializer
)
from ..services.trust_group_service import TrustGroupService
from ..permissions import TrustGroupPermission, TrustGroupMembershipPermission
from ..validators import validate_trust_operation


class TrustGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trust groups.
    Provides CRUD operations and group-specific actions.
    """
    
    serializer_class = TrustGroupSerializer
    permission_classes = [TrustGroupPermission]
    
    def get_queryset(self):
        """
        Filter groups based on user's access and query parameters.
        """
        if not self.request.user.is_authenticated:
            return TrustGroup.objects.none()
        
        user_org = self.get_user_organization()
        if not user_org:
            return TrustGroup.objects.none()
        
        # Start with active groups
        queryset = TrustGroup.objects.filter(is_active=True)
        
        # Filter based on query parameters
        show_all = self.request.query_params.get('all', 'false').lower() == 'true'
        public_only = self.request.query_params.get('public_only', 'false').lower() == 'true'
        member_only = self.request.query_params.get('member_only', 'false').lower() == 'true'
        
        if public_only:
            # Show only public groups
            queryset = queryset.filter(is_public=True)
        elif member_only:
            # Show only groups where user's org is a member
            member_group_ids = TrustGroupMembership.objects.filter(
                organization=user_org,
                is_active=True
            ).values_list('trust_group_id', flat=True)
            queryset = queryset.filter(id__in=member_group_ids)
        elif not show_all:
            # Default: show public groups and groups where user is a member
            member_group_ids = TrustGroupMembership.objects.filter(
                organization=user_org,
                is_active=True
            ).values_list('trust_group_id', flat=True)
            queryset = queryset.filter(
                Q(is_public=True) | Q(id__in=member_group_ids)
            )
        
        # Filter by group type
        group_type = self.request.query_params.get('type')
        if group_type:
            queryset = queryset.filter(group_type=group_type)
        
        return queryset.select_related('default_trust_level').order_by('name')
    
    def get_user_organization(self) -> str:
        """Get the user's organization UUID."""
        if (hasattr(self.request.user, 'organization') and 
            self.request.user.organization):
            return str(self.request.user.organization.id)
        return None
    
    @action(detail=False, methods=['post'])
    def create_group(self, request: Request) -> Response:
        """
        Create a new trust group.
        """
        serializer = CreateTrustGroupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        # Validate the operation
        validation_result = validate_trust_operation(
            'create_group',
            name=data['name'],
            description=data['description'],
            creator_org=user_org,
            group_type=data['group_type'],
            default_trust_level_name=data.get('default_trust_level_name')
        )
        
        if not validation_result['valid']:
            return Response({
                'errors': validation_result['errors'],
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create the group
            group = TrustGroupService.create_trust_group(
                name=data['name'],
                description=data['description'],
                creator_org=user_org,
                group_type=data['group_type'],
                is_public=data['is_public'],
                requires_approval=data['requires_approval'],
                default_trust_level_name=data.get('default_trust_level_name', 'Standard Trust'),
                group_policies=data.get('group_policies', {})
            )
            
            response_serializer = TrustGroupSerializer(group)
            return Response({
                'group': response_serializer.data,
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to create group: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def join_group(self, request: Request) -> Response:
        """
        Join a trust group.
        """
        serializer = JoinTrustGroupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        # Validate the operation
        validation_result = validate_trust_operation(
            'join_group',
            group_id=str(data['group_id']),
            organization=user_org,
            membership_type=data['membership_type'],
            invited_by=str(data['invited_by']) if data.get('invited_by') else None
        )
        
        if not validation_result['valid']:
            return Response({
                'errors': validation_result['errors'],
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Join the group
            membership = TrustGroupService.join_trust_group(
                group_id=str(data['group_id']),
                organization=user_org,
                membership_type=data['membership_type'],
                invited_by=str(data['invited_by']) if data.get('invited_by') else None,
                user=str(request.user.id)
            )
            
            response_serializer = TrustGroupMembershipSerializer(membership)
            return Response({
                'membership': response_serializer.data,
                'message': 'Successfully joined group',
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to join group: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def leave_group(self, request: Request) -> Response:
        """
        Leave a trust group.
        """
        serializer = LeaveTrustGroupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        # Validate the operation
        validation_result = validate_trust_operation(
            'leave_group',
            group_id=str(data['group_id']),
            organization=user_org,
            reason=data.get('reason')
        )
        
        if not validation_result['valid']:
            return Response({
                'errors': validation_result['errors'],
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Leave the group
            success = TrustGroupService.leave_trust_group(
                group_id=str(data['group_id']),
                organization=user_org,
                user=str(request.user.id),
                reason=data.get('reason')
            )
            
            if success:
                return Response({
                    'message': 'Successfully left group',
                    'warnings': validation_result.get('warnings', [])
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to leave group'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to leave group: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def members(self, request: Request, pk=None) -> Response:
        """
        Get members of a trust group.
        """
        try:
            group = self.get_object()
            user_org = self.get_user_organization()
            
            # Check if user can view members
            can_view = (group.is_public or 
                       group.can_administer(user_org) or
                       TrustGroupMembership.objects.filter(
                           trust_group=group,
                           organization=user_org,
                           is_active=True
                       ).exists())
            
            if not can_view:
                return Response({
                    'error': 'Insufficient permissions to view group members'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get members
            include_inactive = request.query_params.get('include_inactive', 'false').lower() == 'true'
            members = TrustGroupService.get_group_members(
                group_id=str(group.id),
                include_inactive=include_inactive
            )
            
            serializer = TrustGroupMembershipSerializer(members, many=True)
            return Response({
                'members': serializer.data,
                'count': len(members)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to get group members: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def promote_member(self, request: Request, pk=None) -> Response:
        """
        Promote a group member to a different membership type.
        """
        try:
            group = self.get_object()
            user_org = self.get_user_organization()
            
            # Check if user can administer the group
            if not group.can_administer(user_org):
                return Response({
                    'error': 'Insufficient permissions to promote members'
                }, status=status.HTTP_403_FORBIDDEN)
            
            organization = request.data.get('organization')
            new_membership_type = request.data.get('membership_type')
            
            if not organization or not new_membership_type:
                return Response({
                    'error': 'organization and membership_type are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Promote the member
            success = TrustGroupService.promote_member(
                group_id=str(group.id),
                organization=organization,
                promoting_org=user_org,
                new_membership_type=new_membership_type,
                user=str(request.user.id)
            )
            
            if success:
                return Response({
                    'message': f'Member promoted to {new_membership_type}'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to promote member'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to promote member: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request: Request, pk=None) -> Response:
        """
        Get statistics about intelligence shared within the group.
        """
        try:
            group = self.get_object()
            user_org = self.get_user_organization()
            
            # Check if user can view statistics
            can_view = (group.is_public or 
                       TrustGroupMembership.objects.filter(
                           trust_group=group,
                           organization=user_org,
                           is_active=True
                       ).exists())
            
            if not can_view:
                return Response({
                    'error': 'Insufficient permissions to view group statistics'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get statistics
            stats = TrustGroupService.get_shared_intelligence_count(str(group.id))
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to get group statistics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def public_groups(self, request: Request) -> Response:
        """
        Get all public trust groups.
        """
        try:
            groups = TrustGroupService.get_public_trust_groups()
            serializer = TrustGroupSerializer(groups, many=True)
            
            return Response({
                'groups': serializer.data,
                'count': len(groups)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to get public groups: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_groups(self, request: Request) -> Response:
        """
        Get trust groups where the user's organization is a member.
        """
        try:
            user_org = self.get_user_organization()
            groups = TrustGroupService.get_trust_groups_for_organization(
                organization=user_org,
                include_inactive=False
            )
            
            serializer = TrustGroupSerializer(groups, many=True)
            
            return Response({
                'groups': serializer.data,
                'count': len(groups)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to get user groups: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrustGroupMembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trust group memberships.
    Provides detailed membership management operations.
    """
    
    serializer_class = TrustGroupMembershipSerializer
    permission_classes = [TrustGroupMembershipPermission]
    
    def get_queryset(self):
        """
        Filter memberships based on user's access.
        """
        if not self.request.user.is_authenticated:
            return TrustGroupMembership.objects.none()
        
        user_org = self.get_user_organization()
        if not user_org:
            return TrustGroupMembership.objects.none()
        
        # Show memberships for groups where user's org is a member or admin
        user_group_ids = TrustGroupMembership.objects.filter(
            organization=user_org,
            is_active=True
        ).values_list('trust_group_id', flat=True)
        
        admin_group_ids = TrustGroup.objects.filter(
            administrators__contains=[user_org]
        ).values_list('id', flat=True)
        
        visible_group_ids = set(user_group_ids) | set(admin_group_ids)
        
        queryset = TrustGroupMembership.objects.filter(
            trust_group_id__in=visible_group_ids
        ).select_related('trust_group')
        
        # Filter by group if specified
        group_id = self.request.query_params.get('group_id')
        if group_id:
            queryset = queryset.filter(trust_group_id=group_id)
        
        # Filter by active status
        include_inactive = self.request.query_params.get('include_inactive', 'false').lower() == 'true'
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-joined_at')
    
    def get_user_organization(self) -> str:
        """Get the user's organization UUID."""
        if (hasattr(self.request.user, 'organization') and 
            self.request.user.organization):
            return str(self.request.user.organization.id)
        return None