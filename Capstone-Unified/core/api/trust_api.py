"""
Trust Management API - Trust relationship and trust level management endpoints
Handles bilateral trust, community trust, and trust level operations
"""

import logging
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from core.models.models import TrustRelationship, Organization, TrustLevel
from core.trust_management.models import TrustGroup
from core.user_management.models import CustomUser
from core.services.trust_service import TrustService
from core.services.access_control_service import AccessControlService
from core.serializers.trust_serializer import (
    TrustRelationshipSerializer, TrustGroupSerializer, TrustLevelSerializer,
    TrustRelationshipSummarySerializer, TrustRelationshipCreateSerializer
)

logger = logging.getLogger(__name__)

class TrustPagination(PageNumberPagination):
    """Custom pagination for trust relationships"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_bilateral_trusts(request):
    """
    List bilateral trust relationships
    
    GET /api/trust/bilateral/
    Query params:
        - page: page number
        - page_size: items per page
        - organization: filter by organization ID
        - status: filter by trust status
        - trust_level: filter by trust level
    """
    try:
        access_control = AccessControlService()
        
        # Check permissions
        if not access_control.can_view_trust_relationships(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view trust relationships'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get base queryset based on user permissions
        if request.user.role == 'BlueVisionAdmin':
            # BlueVision admins can see all trust relationships
            queryset = TrustRelationship.objects.all()
        else:
            # Other users can only see relationships involving their organization
            user_org = request.user.organization
            if not user_org:
                return Response({
                    'success': True,
                    'trusts': [],
                    'total_count': 0
                }, status=status.HTTP_200_OK)
            
            queryset = TrustRelationship.objects.filter(
                Q(source_organization=user_org) | Q(target_organization=user_org)
            )
        
        # Apply filters
        organization_id = request.GET.get('organization')
        if organization_id:
            queryset = queryset.filter(
                Q(source_organization_id=organization_id) | 
                Q(target_organization_id=organization_id)
            )
        
        trust_status = request.GET.get('status')
        if trust_status:
            queryset = queryset.filter(status=trust_status)
        
        trust_level = request.GET.get('trust_level')
        if trust_level:
            queryset = queryset.filter(trust_level=trust_level)
        
        # Order by created_at descending
        queryset = queryset.select_related(
            'source_organization', 'target_organization', 'trust_level'
        ).order_by('-created_at')
        
        # Paginate results
        paginator = TrustPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = TrustRelationshipSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'trusts': serializer.data
            })
        
        serializer = TrustRelationshipSerializer(queryset, many=True)
        return Response({
            'success': True,
            'trusts': serializer.data,
            'total_count': queryset.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing bilateral trusts: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to list trust relationships'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_bilateral_trust(request):
    """
    Request bilateral trust with another organization
    
    POST /api/trust/bilateral/request/
    Body: {
        "responding_organization_id": "uuid",
        "trust_level": "string",
        "message": "string"
    }
    """
    try:
        trust_service = TrustService()
        access_control = AccessControlService()
        
        # Check permissions
        if not access_control.can_manage_trust_relationships(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to manage trust relationships'
            }, status=status.HTTP_403_FORBIDDEN)
        
        responding_org_id = request.data.get('responding_organization_id')
        trust_level = request.data.get('trust_level', 'minimal')
        message = request.data.get('message', '')
        
        # Check if user has an organization
        if not request.user.organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization to create trust relationships'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not responding_org_id:
            return Response({
                'success': False,
                'message': 'responding_organization_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get responding organization
        try:
            responding_org = Organization.objects.get(id=responding_org_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Responding organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get trust level object - try both level and name fields
        try:
            trust_level_obj = TrustLevel.objects.get(level=trust_level)
        except TrustLevel.DoesNotExist:
            try:
                # Fallback: try by name field
                trust_level_obj = TrustLevel.objects.get(name=trust_level)
            except TrustLevel.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'Trust level "{trust_level}" not found'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create trust relationship
        try:
            trust_relationship = trust_service.create_trust_relationship(
                source_org_id=request.user.organization.id,
                target_org_id=responding_org_id,
                trust_level_id=trust_level_obj.id,
                created_by_user=request.user,
                relationship_type='bilateral'
            )
            
            serializer = TrustRelationshipSerializer(trust_relationship)
            
            return Response({
                'success': True,
                'message': f'Trust relationship request sent to {responding_org.name}',
                'trust': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating trust relationship: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to create trust relationship'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error requesting bilateral trust: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to request trust relationship'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_bilateral_trust(request, trust_id):
    """
    Respond to bilateral trust request
    
    POST /api/trust/bilateral/{trust_id}/respond/
    Body: {
        "action": "accept|reject",
        "trust_level": "string",
        "message": "string"
    }
    """
    try:
        trust_service = TrustService()
        access_control = AccessControlService()
        
        # Get trust relationship
        try:
            trust_relationship = TrustRelationship.objects.select_related(
                'source_organization', 'target_organization', 'trust_level'
            ).get(id=trust_id)
        except TrustRelationship.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust relationship not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_respond_to_trust_request(request.user, trust_relationship):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to respond to this trust request'
            }, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get('action')
        trust_level = request.data.get('trust_level')
        message = request.data.get('message', '')
        
        if action not in ['accept', 'reject']:
            return Response({
                'success': False,
                'message': 'Action must be either "accept" or "reject"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'accept':
            result = trust_service.accept_bilateral_trust(
                trust_id=trust_id,
                trust_level=trust_level,
                message=message,
                accepted_by=request.user
            )
        else:
            result = trust_service.reject_bilateral_trust(
                trust_id=trust_id,
                message=message,
                rejected_by=request.user
            )
        
        if result['success']:
            trust_relationship.refresh_from_db()
            serializer = TrustRelationshipSerializer(trust_relationship)
            
            return Response({
                'success': True,
                'message': result['message'],
                'trust': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error responding to bilateral trust {trust_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to respond to trust request'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_bilateral_trust(request, trust_id):
    """
    Update bilateral trust level, status, and/or notes
    
    PUT /api/trust/bilateral/{trust_id}/update/
    Body: {
        "trust_level": "string (optional)",
        "status": "string (optional: pending, active, suspended, revoked, expired)",
        "notes": "string (optional)",
        "message": "string (optional - used for logging)"
    }
    """
    try:
        trust_service = TrustService()
        access_control = AccessControlService()
        
        # Get trust relationship
        try:
            trust_relationship = TrustRelationship.objects.get(id=trust_id)
        except TrustRelationship.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust relationship not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_modify_trust_relationship(request.user, trust_relationship):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to modify this trust relationship'
            }, status=status.HTTP_403_FORBIDDEN)
        
        trust_level = request.data.get('trust_level')
        trust_status = request.data.get('status')
        notes = request.data.get('notes')
        message = request.data.get('message', '')
        
        # At least one field must be provided to update
        if not any([trust_level, trust_status, notes is not None]):
            return Response({
                'success': False,
                'message': 'At least one field (trust_level, status, or notes) must be provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = trust_service.update_bilateral_trust(
            trust_id=trust_id,
            trust_level=trust_level,
            status=trust_status,
            notes=notes,
            message=message,
            updated_by=request.user
        )
        
        if result['success']:
            trust_relationship.refresh_from_db()
            serializer = TrustRelationshipSerializer(trust_relationship)
            
            return Response({
                'success': True,
                'message': result['message'],
                'trust': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error updating bilateral trust {trust_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to update trust relationship'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_bilateral_trust(request, trust_id):
    """
    Revoke bilateral trust relationship
    
    DELETE /api/trust/bilateral/{trust_id}/
    Body: {
        "message": "string"
    }
    """
    try:
        trust_service = TrustService()
        access_control = AccessControlService()
        
        # Get trust relationship
        try:
            trust_relationship = TrustRelationship.objects.get(id=trust_id)
        except TrustRelationship.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust relationship not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_revoke_trust_relationship(request.user, trust_relationship):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to revoke this trust relationship'
            }, status=status.HTTP_403_FORBIDDEN)
        
        message = request.data.get('message', '')
        
        result = trust_service.revoke_bilateral_trust(
            trust_id=trust_id,
            message=message,
            revoked_by=request.user
        )
        
        if result['success']:
            return Response({
                'success': True,
                'message': result['message']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error revoking bilateral trust {trust_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to revoke trust relationship'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trust_level(request, organization_id):
    """
    Get trust level with another organization
    
    GET /api/trust/level/{organization_id}/
    """
    try:
        trust_service = TrustService()
        
        # Get organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user has organization
        if not request.user.organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get trust level
        trust_level = trust_service.get_trust_level(
            org1=request.user.organization,
            org2=organization
        )
        
        return Response({
            'success': True,
            'trust_level': trust_level,
            'organization': {
                'id': str(organization.id),
                'name': organization.name,
                'domain': organization.domain
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting trust level for organization {organization_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get trust level'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_community_trusts(request):
    """
    List community trust relationships
    
    GET /api/trust/community/
    Query params:
        - page: page number
        - page_size: items per page
        - trust_type: filter by trust type
        - status: filter by status
    """
    try:
        access_control = AccessControlService()
        
        # Check permissions
        if not access_control.can_view_community_trusts(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view community trusts'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get queryset
        queryset = TrustGroup.objects.all()
        
        # Apply filters
        group_type = request.GET.get('group_type')
        if group_type:
            queryset = queryset.filter(group_type=group_type)
        
        is_active = request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Order by created_at descending
        queryset = queryset.order_by('-created_at')
        
        # Paginate results
        paginator = TrustPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = TrustGroupSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'community_trusts': serializer.data
            })
        
        serializer = TrustGroupSerializer(queryset, many=True)
        return Response({
            'success': True,
            'community_trusts': serializer.data,
            'total_count': queryset.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing community trusts: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to list community trusts'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trust_dashboard(request):
    """
    Get trust relationship dashboard data for current user's organization
    
    GET /api/trust/dashboard/
    """
    try:
        trust_service = TrustService()
        
        if not request.user.organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get dashboard data
        dashboard_data = trust_service.get_trust_dashboard_data(request.user.organization)
        
        return Response({
            'success': True,
            'dashboard': dashboard_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting trust dashboard: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get trust dashboard data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_trust_levels(request):
    """
    List all available trust levels
    
    GET /api/trust/levels/
    """
    try:
        # Get all active trust levels ordered by numerical value
        trust_levels = TrustLevel.objects.filter(is_active=True).order_by('numerical_value')
        
        serializer = TrustLevelSerializer(trust_levels, many=True)
        
        return Response({
            'success': True,
            'trust_levels': serializer.data,
            'count': trust_levels.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing trust levels: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to list trust levels'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)