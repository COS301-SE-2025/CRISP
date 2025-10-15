"""
User Management API - User administration and management endpoints
Handles user CRUD operations, invitations, and organization management
"""

import logging
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from core.models.models import Organization
from core.user_management.models.invitation_models import UserInvitation
from core.user_management.models import CustomUser
from core.services.user_service import UserService
from core.services.invitation_service import UserInvitationService
from core.services.access_control_service import AccessControlService
from core.serializers.auth_serializer import UserSerializer, UserCreateSerializer, UserUpdateSerializer

logger = logging.getLogger(__name__)

class UserPagination(PageNumberPagination):
    """Custom pagination for user lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    List users with filtering and pagination
    
    GET /api/users/
    Query params:
        - page: page number
        - page_size: items per page (max 100)
        - search: search in username, email, first_name, last_name
        - role: filter by role
        - organization: filter by organization ID
        - is_active: filter by active status
    """
    try:
        # Build cache key from query params
        cache_key = f"users_list_{request.user.id}_{request.GET.urlencode()}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)
        
        access_control = AccessControlService()
        
        # Check if user can list users
        if not access_control.can_manage_users(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to list users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get base queryset based on user permissions - OPTIMIZED with select_related
        if request.user.role == 'BlueVisionAdmin':
            # BlueVision admins can see all users
            queryset = CustomUser.objects.select_related('organization').all()
        else:
            # Other users can only see users in their accessible organizations
            accessible_orgs = access_control.get_accessible_organizations(request.user)
            queryset = CustomUser.objects.select_related('organization').filter(organization__in=accessible_orgs)
        
        # Apply filters
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        role = request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        organization_id = request.GET.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        
        is_active = request.GET.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Order by created_at descending
        queryset = queryset.order_by('-created_at')
        
        # Paginate results
        paginator = UserPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = UserSerializer(page, many=True)
            response_data = {
                'success': True,
                'users': serializer.data
            }
            # Cache for 2 minutes
            cache.set(cache_key, response_data, 120)
            return paginator.get_paginated_response(response_data)
        
        serializer = UserSerializer(queryset, many=True)
        response_data = {
            'success': True,
            'users': serializer.data,
            'total_count': queryset.count()
        }
        # Cache for 2 minutes
        cache.set(cache_key, response_data, 120)
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to list users'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):
    """
    Get user details by ID
    
    GET /api/users/{user_id}/
    """
    try:
        access_control = AccessControlService()
        
        # Get user
        try:
            user = CustomUser.objects.select_related('organization').get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_view_user(request.user, user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view this user'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(user)
        return Response({
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get user details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    """
    Create a new user (admin only)
    
    POST /api/users/
    Body: {
        "username": "string",
        "email": "string",
        "password": "string",
        "password_confirm": "string",
        "first_name": "string",
        "last_name": "string",
        "role": "string",
        "organization_id": "uuid"
    }
    """
    try:
        access_control = AccessControlService()
        
        # Check permissions
        if not access_control.can_create_users(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to create users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_service = UserService()
        
        # Validate organization access
        organization_id = request.data.get('organization_id')
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
                if not access_control.can_manage_organization(request.user, organization):
                    return Response({
                        'success': False,
                        'message': 'Insufficient permissions for this organization'
                    }, status=status.HTTP_403_FORBIDDEN)
            except Organization.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Organization not found'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = user_service.create_user(
                username=request.data.get('username'),
                email=request.data.get('email'),
                password=request.data.get('password'),
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', ''),
                role=request.data.get('role', 'viewer'),
                organization_id=organization_id,
                created_by=request.user
            )
            
            # Optionally send welcome email if requested
            send_email = request.data.get('send_email', True)  # Default to True
            if send_email and user.organization:
                try:
                    from core.services.email_service import UnifiedEmailService
                    email_service = UnifiedEmailService()
                    
                    # Generate a temporary token for account setup
                    import secrets
                    setup_token = secrets.token_urlsafe(32)
                    
                    # Send welcome email (reusing invitation email template)
                    email_result = email_service.send_user_invitation_email(
                        email=user.email,
                        organization=user.organization,
                        inviter=request.user,
                        invitation_token=setup_token
                    )
                    
                    logger.info(f"Welcome email sent to {user.email}: {email_result.get('success', False)}")
                except Exception as e:
                    logger.warning(f"Failed to send welcome email to {user.email}: {e}")
            
            serializer = UserSerializer(user)
            
            return Response({
                'success': True,
                'message': 'User created successfully',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Handle database constraint errors and other exceptions
            error_message = str(e)
            if 'duplicate key value violates unique constraint' in error_message:
                if 'username' in error_message:
                    error_message = 'Username already exists. Please choose a different username.'
                elif 'email' in error_message:
                    error_message = 'Email address already exists. Please use a different email.'
                else:
                    error_message = 'A user with this information already exists.'
            
            return Response({
                'success': False,
                'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to create user'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    """
    Update user details
    
    PUT /api/users/{user_id}/update/
    Body: {
        "first_name": "string",
        "last_name": "string",
        "email": "string",
        "role": "string",
        "organization_id": "uuid",
        "is_active": boolean,
        "is_verified": boolean
    }
    """
    try:
        access_control = AccessControlService()
        
        # Get user
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_modify_user(request.user, user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to modify this user'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_service = UserService()
        result = user_service.update_user(
            user_id=user_id,
            update_data=request.data,
            updated_by=request.user
        )
        
        if result['success']:
            user.refresh_from_db()
            serializer = UserSerializer(user)
            
            return Response({
                'success': True,
                'message': result['message'],
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to update user'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_permanently(request, user_id):
    """
    Permanently delete a user and all related data (BlueVision admins only)
    
    DELETE /api/users/{user_id}/delete-permanently/
    Body: {
        "reason": "string",
        "confirm": true
    }
    """
    try:
        access_control = AccessControlService()
        
        # Get user
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions (only BlueVision admins)
        if not access_control.can_delete_user(request.user, user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to permanently delete this user'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Require confirmation
        if not request.data.get('confirm', False):
            return Response({
                'success': False,
                'message': 'Permanent deletion requires confirmation. Set "confirm": true in request body.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent self-deletion
        if user.id == request.user.id:
            return Response({
                'success': False,
                'message': 'Cannot permanently delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_service = UserService()
        reason = request.data.get('reason', '')
        
        result = user_service.delete_user_permanently(
            user_id=user_id,
            deleted_by=request.user,
            reason=reason
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
        logger.error(f"Error permanently deleting user {user_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to permanently delete user'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_user(request):
    """
    Send user invitation
    
    POST /api/users/invite/
    Body: {
        "email": "string",
        "organization_id": "uuid",
        "role": "string",
        "message": "string"
    }
    """
    try:
        access_control = AccessControlService()
        invitation_service = UserInvitationService()
        
        email = request.data.get('email')
        organization_id = request.data.get('organization_id')
        role = request.data.get('role', 'viewer')
        message = request.data.get('message', '')
        
        if not email or not organization_id:
            return Response({
                'success': False,
                'message': 'Email and organization_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_invite_to_organization(request.user, organization):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to invite users to this organization'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Send invitation
        result = invitation_service.send_invitation(
            inviter=request.user,
            organization=organization,
            email=email,
            role=role,
            message=message
        )
        
        if result['success']:
            return Response({
                'success': True,
                'message': result['message'],
                'invitation_id': result.get('invitation_id'),
                'expires_at': result.get('expires_at')
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error sending invitation: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to send invitation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_invitations(request):
    """
    List invitations for organizations user can manage
    
    GET /api/users/invitations/
    Query params:
        - organization_id: filter by organization
        - status: filter by invitation status
    """
    try:
        access_control = AccessControlService()
        invitation_service = UserInvitationService()
        
        # Get accessible organizations
        if request.user.role == 'BlueVisionAdmin':
            accessible_orgs = Organization.objects.all()
        else:
            accessible_orgs = access_control.get_manageable_organizations(request.user)
        
        if not accessible_orgs:
            return Response({
                'success': True,
                'invitations': [],
                'total_count': 0
            }, status=status.HTTP_200_OK)
        
        # Filter by organization if specified
        organization_id = request.GET.get('organization_id')
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
                if organization not in accessible_orgs:
                    return Response({
                        'success': False,
                        'message': 'Insufficient permissions for this organization'
                    }, status=status.HTTP_403_FORBIDDEN)
                result = invitation_service.list_organization_invitations(
                    requesting_user=request.user,
                    organization_id=organization_id,
                    status=request.GET.get('status')
                )
            except Organization.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Organization not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Get invitations for all accessible organizations
            all_invitations = []
            for org in accessible_orgs:
                result = invitation_service.list_organization_invitations(
                    requesting_user=request.user,
                    organization_id=str(org.id),
                    status=request.GET.get('status')
                )
                if result['success']:
                    all_invitations.extend(result['invitations'])
            
            result = {
                'success': True,
                'invitations': sorted(all_invitations, key=lambda x: x['created_at'], reverse=True),
                'total_count': len(all_invitations)
            }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing invitations: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to list invitations'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_invitation(request, invitation_id):
    """
    Cancel pending invitation
    
    DELETE /api/users/invitations/{invitation_id}/
    """
    try:
        invitation_service = UserInvitationService()
        
        result = invitation_service.cancel_invitation(
            cancelling_user=request.user,
            invitation_id=invitation_id
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
        logger.error(f"Error cancelling invitation {invitation_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to cancel invitation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactivate_user(request, user_id):
    """
    Reactivate a deactivated user
    
    POST /api/users/{user_id}/reactivate/
    Body: {
        "reason": "string"
    }
    """
    try:
        access_control = AccessControlService()
        
        # Get user
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_modify_user(request.user, user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to reactivate this user'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_service = UserService()
        reason = request.data.get('reason', '')
        
        result = user_service.reactivate_user(
            user_id=user_id,
            reactivated_by=request.user,
            reason=reason
        )
        
        if result['success']:
            user.refresh_from_db()
            serializer = UserSerializer(user)
            
            return Response({
                'success': True,
                'message': result['message'],
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error reactivating user {user_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to reactivate user'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_user(request, user_id):
    """
    Deactivate a user (soft delete without full deletion)
    
    POST /api/users/{user_id}/deactivate/
    Body: {
        "reason": "string"
    }
    """
    try:
        access_control = AccessControlService()
        
        # Get user
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not access_control.can_modify_user(request.user, user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to deactivate this user'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Prevent self-deactivation
        if user.id == request.user.id:
            return Response({
                'success': False,
                'message': 'Cannot deactivate your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is already inactive
        if not user.is_active:
            return Response({
                'success': False,
                'message': 'User is already deactivated'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_service = UserService()
        reason = request.data.get('reason', '')
        
        # Use the existing delete_user method which does soft delete
        result = user_service.delete_user(
            user_id=user_id,
            deleted_by=request.user,
            reason=reason
        )
        
        if result['success']:
            user.refresh_from_db()
            serializer = UserSerializer(user)
            
            return Response({
                'success': True,
                'message': f"User '{user.username}' has been deactivated successfully",
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to deactivate user'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)