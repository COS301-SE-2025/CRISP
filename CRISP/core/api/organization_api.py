"""
Organization Management API - Organization CRUD and management endpoints
Handles organization creation, updates, member management, and organization settings
"""

import logging
from django.db.models import Q, Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from core.models.models import Organization, CustomUser, TrustRelationship
from core.services.organization_service import OrganizationService
from core.services.access_control_service import AccessControlService
from core.serializers.organization_serializer import (
    OrganizationSerializer, OrganizationCreateSerializer, OrganizationUpdateSerializer,
    OrganizationDetailSerializer, OrganizationMemberSerializer
)

logger = logging.getLogger(__name__)

class OrganizationPagination(PageNumberPagination):
    """Custom pagination for organization lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_organizations(request):
    """
    List organizations with filtering and pagination
    
    GET /api/organizations/
    Query params:
        - page: page number
        - page_size: items per page
        - search: search in name, domain, description
        - organization_type: filter by organization type
        - is_active: filter by active status
    """
    try:
        access_control = AccessControlService()
        
        # Get base queryset based on user permissions
        if request.user.role == 'BlueVisionAdmin':
            # BlueVision admins can see all organizations
            queryset = Organization.objects.all()
        else:
            # Other users can see their own organization and trusted organizations
            accessible_orgs = access_control.get_accessible_organizations(request.user)
            queryset = Organization.objects.filter(id__in=[org.id for org in accessible_orgs])
        
        # Apply filters
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(domain__icontains=search) |
                Q(description__icontains=search)
            )
        
        organization_type = request.GET.get('organization_type')
        if organization_type:
            queryset = queryset.filter(organization_type=organization_type)
        
        is_active = request.GET.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Add member count annotation
        queryset = queryset.annotate(member_count=Count('users'))
        
        # Order by name
        queryset = queryset.order_by('name')
        
        # Paginate results
        paginator = OrganizationPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = OrganizationSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'organizations': serializer.data
            })
        
        serializer = OrganizationSerializer(queryset, many=True)
        return Response({
            'success': True,
            'organizations': serializer.data,
            'total_count': queryset.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to list organizations'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization(request, organization_id):
    """
    Get organization details by ID
    
    GET /api/organizations/{organization_id}/
    """
    try:
        access_control = AccessControlService()
        
        # Get organization
        try:
            organization = Organization.objects.annotate(
                member_count=Count('customuser')
            ).get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_view_organization(request.user, organization):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view this organization'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrganizationDetailSerializer(organization)
        return Response({
            'success': True,
            'organization': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting organization {organization_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get organization details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization(request):
    """
    Create a new organization (BlueVision admins only)
    
    POST /api/organizations/
    Body: {
        "name": "string",
        "domain": "string",
        "organization_type": "string",
        "description": "string",
        "contact_email": "string",
        "contact_phone": "string"
    }
    """
    try:
        access_control = AccessControlService()
        
        # Check permissions (only BlueVision admins can create organizations)
        if not access_control.can_create_organizations(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to create organizations'
            }, status=status.HTTP_403_FORBIDDEN)
        
        org_service = OrganizationService()
        
        # Extract primary user data
        primary_user_data = request.data.get('primary_user', {})
        
        # Create organization
        result = org_service.create_organization(
            name=request.data.get('name'),
            domain=request.data.get('domain'),
            organization_type=request.data.get('organization_type'),
            description=request.data.get('description', ''),
            contact_email=request.data.get('contact_email'),
            website=request.data.get('website', ''),
            primary_user_data=primary_user_data,
            created_by=request.user
        )
        
        if result['success']:
            organization = Organization.objects.get(id=result['organization_id'])
            serializer = OrganizationDetailSerializer(organization)
            
            return Response({
                'success': True,
                'message': result['message'],
                'organization': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to create organization'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_organization(request, organization_id):
    """
    Update organization details
    
    PUT /api/organizations/{organization_id}/
    Body: {
        "name": "string",
        "description": "string",
        "contact_email": "string",
        "contact_phone": "string",
        "is_active": boolean
    }
    """
    try:
        access_control = AccessControlService()
        
        # Get organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_modify_organization(request.user, organization):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to modify this organization'
            }, status=status.HTTP_403_FORBIDDEN)
        
        org_service = OrganizationService()
        result = org_service.update_organization(
            organization_id=organization_id,
            update_data=request.data,
            updated_by=request.user
        )
        
        if result['success']:
            organization.refresh_from_db()
            serializer = OrganizationDetailSerializer(organization)
            
            return Response({
                'success': True,
                'message': result['message'],
                'organization': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error updating organization {organization_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to update organization'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_organization(request, organization_id):
    """
    Delete/deactivate organization (BlueVision admins only)
    
    DELETE /api/organizations/{organization_id}/
    """
    try:
        access_control = AccessControlService()
        
        # Get organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions (only BlueVision admins)
        if not access_control.can_delete_organization(request.user, organization):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to delete this organization'
            }, status=status.HTTP_403_FORBIDDEN)
        
        org_service = OrganizationService()
        result = org_service.delete_organization(
            organization_id=organization_id,
            deleted_by=request.user
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
        logger.error(f"Error deleting organization {organization_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to delete organization'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_organization_members(request, organization_id):
    """
    List members of an organization
    
    GET /api/organizations/{organization_id}/members/
    Query params:
        - page: page number
        - page_size: items per page
        - role: filter by role
        - is_active: filter by active status
    """
    try:
        access_control = AccessControlService()
        
        # Get organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_view_organization_members(request.user, organization):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view organization members'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get members
        queryset = CustomUser.objects.filter(organization=organization)
        
        # Apply filters
        role = request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        is_active = request.GET.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Order by role and username
        queryset = queryset.order_by('role', 'username')
        
        # Paginate results
        paginator = OrganizationPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = OrganizationMemberSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'members': serializer.data,
                'organization': {
                    'id': str(organization.id),
                    'name': organization.name
                }
            })
        
        serializer = OrganizationMemberSerializer(queryset, many=True)
        return Response({
            'success': True,
            'members': serializer.data,
            'organization': {
                'id': str(organization.id),
                'name': organization.name
            },
            'total_count': queryset.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing organization members {organization_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to list organization members'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_statistics(request, organization_id):
    """
    Get organization statistics and metrics
    
    GET /api/organizations/{organization_id}/statistics/
    """
    try:
        access_control = AccessControlService()
        
        # Get organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_view_organization_statistics(request.user, organization):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view organization statistics'
            }, status=status.HTTP_403_FORBIDDEN)
        
        org_service = OrganizationService()
        statistics = org_service.get_organization_statistics(organization_id)
        
        return Response({
            'success': True,
            'statistics': statistics,
            'organization': {
                'id': str(organization.id),
                'name': organization.name
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting organization statistics {organization_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get organization statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_trust_relationships(request, organization_id):
    """
    Get trust relationships for an organization
    
    GET /api/organizations/{organization_id}/trust-relationships/
    """
    try:
        access_control = AccessControlService()
        
        # Get organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_view_organization_trust_relationships(request.user, organization):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view trust relationships'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get trust relationships
        trust_relationships_qs = TrustRelationship.objects.filter(
            Q(source_organization=organization) | Q(target_organization=organization)
        ).select_related('source_organization', 'target_organization', 'trust_level')
        
        trust_relationships = []
        for trust in trust_relationships_qs:
            # Determine the other organization
            if trust.source_organization.id == organization.id:
                other_org = trust.target_organization
                relationship_type = 'outgoing'
            else:
                other_org = trust.source_organization
                relationship_type = 'incoming'
            
            trust_relationships.append({
                'id': str(trust.id),
                'organization': {
                    'id': str(other_org.id),
                    'name': other_org.name,
                    'domain': other_org.domain,
                    'organization_type': other_org.organization_type
                },
                'trust_level': trust.trust_level.name if trust.trust_level else None,
                'status': trust.status,
                'relationship_type': relationship_type,
                'created_at': trust.created_at.isoformat(),
                'updated_at': trust.updated_at.isoformat()
            })
        
        return Response({
            'success': True,
            'trust_relationships': trust_relationships,
            'organization': {
                'id': str(organization.id),
                'name': organization.name
            },
            'total_count': len(trust_relationships)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting organization trust relationships {organization_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get trust relationships'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)