from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError, PermissionDenied
from ..services.user_service import UserService
from ..services.access_control_service import AccessControlService
from ..models import CustomUser
import logging

logger = logging.getLogger(__name__)


class UserViewSet(GenericViewSet):
    """
    User management API endpoints with trust-aware access control.
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()
        self.access_control = AccessControlService()
    
    @action(detail=False, methods=['post'])
    def create_user(self, request):
        """
        Create a new user with role-based validation.
        
        Expected payload:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "first_name": "string",
            "last_name": "string",
            "role": "viewer|publisher|BlueVisionAdmin",
            "organization_id": "uuid"
        }
        """
        try:
            if not self.access_control.has_permission(request.user, 'can_create_organization_users'):
                return Response({
                    'success': False,
                    'message': 'No permission to create users'
                }, status=status.HTTP_403_FORBIDDEN)
            
            user_data = request.data.copy()
            user_data['ip_address'] = self._get_client_ip(request)
            user_data['user_agent'] = request.META.get('HTTP_USER_AGENT', 'API')
            
            user = self.user_service.create_user(
                creating_user=request.user,
                user_data=user_data
            )
            
            user_details = self.user_service.get_user_details(request.user, str(user.id))
            
            return Response({
                'success': True,
                'data': {
                    'user': user_details,
                    'message': f'User {user.username} created successfully'
                }
            }, status=status.HTTP_201_CREATED)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Create user error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to create user'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def get_user(self, request, pk=None):
        """Get detailed user information."""
        try:
            user_details = self.user_service.get_user_details(request.user, pk)
            
            return Response({
                'success': True,
                'data': {
                    'user': user_details
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve user'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['put', 'patch'])
    def update_user(self, request, pk=None):
        """
        Update user information.
        
        Expected payload:
        {
            "first_name": "string",
            "last_name": "string", 
            "email": "string",
            "role": "string",
            "is_verified": boolean,
            "is_active": boolean
        }
        """
        try:
            update_data = request.data.copy()
            update_data['updated_from_ip'] = self._get_client_ip(request)
            update_data['user_agent'] = request.META.get('HTTP_USER_AGENT', 'API')
            
            updated_user = self.user_service.update_user(
                updating_user=request.user,
                user_id=pk,
                update_data=update_data
            )
            
            user_details = self.user_service.get_user_details(request.user, str(updated_user.id))
            
            return Response({
                'success': True,
                'data': {
                    'user': user_details,
                    'message': 'User updated successfully'
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Update user error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to update user'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def list_users(self, request):
        """
        List users with filtering and organization scope.
        
        Query parameters:
        - organization_id: Filter by organization
        - role: Filter by role
        - is_active: Filter by active status
        - search: Search by username, name, or email
        """
        try:
            filters = {
                'role': request.query_params.get('role'),
                'is_active': request.query_params.get('is_active'),
                'is_verified': request.query_params.get('is_verified'),
                'search': request.query_params.get('search')
            }
            
            # Remove None values
            filters = {k: v for k, v in filters.items() if v is not None}
            
            # Convert string booleans
            for bool_field in ['is_active', 'is_verified']:
                if bool_field in filters:
                    filters[bool_field] = filters[bool_field].lower() == 'true'
            
            organization_id = request.query_params.get('organization_id')
            
            users = self.user_service.list_users(
                requesting_user=request.user,
                filters=filters,
                organization_id=organization_id
            )
            
            return Response({
                'success': True,
                'data': {
                    'users': users,
                    'total_count': len(users),
                    'filters_applied': filters
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"List users error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve users'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def deactivate_user(self, request, pk=None):
        """
        Deactivate a user account.
        
        Expected payload:
        {
            "reason": "string"
        }
        """
        try:
            reason = request.data.get('reason', '')
            
            deactivated_user = self.user_service.deactivate_user(
                deactivating_user=request.user,
                user_id=pk,
                reason=reason
            )
            
            return Response({
                'success': True,
                'data': {
                    'message': f'User {deactivated_user.username} deactivated successfully',
                    'user_id': str(deactivated_user.id),
                    'reason': reason
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Deactivate user error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to deactivate user'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reactivate_user(self, request, pk=None):
        """
        Reactivate a user account.
        
        Expected payload:
        {
            "reason": "string"
        }
        """
        try:
            reason = request.data.get('reason', '')
            
            # Use update_user to reactivate
            update_data = {
                'is_active': True,
                'updated_from_ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'API')
            }
            
            reactivated_user = self.user_service.update_user(
                updating_user=request.user,
                user_id=pk,
                update_data=update_data
            )
            
            return Response({
                'success': True,
                'data': {
                    'message': f'User {reactivated_user.username} reactivated successfully',
                    'user_id': str(reactivated_user.id),
                    'reason': reason
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Reactivate user error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to reactivate user'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """Get or update current user's profile."""
        if request.method == 'GET':
            return self._get_profile(request)
        else:
            return self._update_profile(request)
    
    def _get_profile(self, request):
        """Get current user's profile."""
        try:
            # Check if user is authenticated
            if not request.user or not request.user.is_authenticated:
                logger.error("Profile request from unauthenticated user")
                return Response({
                    'success': False,
                    'message': 'Authentication required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user has an ID
            if not hasattr(request.user, 'id') or not request.user.id:
                logger.error(f"Profile request from user without ID: {request.user}")
                return Response({
                    'success': False,
                    'message': 'Invalid user session'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Getting profile for user: {request.user.username} (ID: {request.user.id})")
            
            # Simple fallback if service fails
            try:
                user_details = self.user_service.get_user_details(
                    requesting_user=request.user,
                    user_id=str(request.user.id)
                )
            except Exception as service_error:
                logger.error(f"UserService failed, creating basic profile: {str(service_error)}")
                # Fallback to basic user data
                user_details = {
                    'id': str(request.user.id),
                    'username': request.user.username,
                    'first_name': request.user.first_name or '',
                    'last_name': request.user.last_name or '',
                    'email': request.user.email or '',
                    'role': getattr(request.user, 'role', 'viewer'),
                    'is_active': request.user.is_active,
                    'date_joined': request.user.date_joined.isoformat() if request.user.date_joined else '',
                    'organization': {
                        'id': str(request.user.organization.id) if hasattr(request.user, 'organization') and request.user.organization else None,
                        'name': request.user.organization.name if hasattr(request.user, 'organization') and request.user.organization else 'No Organization',
                        'domain': request.user.organization.domain if hasattr(request.user, 'organization') and request.user.organization else 'unknown'
                    } if hasattr(request.user, 'organization') and request.user.organization else None,
                    'profile': None
                }
            
            return Response({
                'success': True,
                'data': {
                    'profile': user_details
                }
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            logger.error(f"Permission denied for profile request: {str(e)}")
            return Response({
                'success': False,
                'message': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        except ValidationError as e:
            logger.error(f"Validation error in profile request: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Get profile error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve profile'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_profile(self, request):
        """Update current user's profile."""
        try:
            update_data = request.data.copy()
            logger.info(f"Profile update data received: {update_data}")
            
            # Handle full_name field - split into first_name and last_name
            if 'full_name' in update_data:
                full_name = update_data['full_name'].strip()
                if full_name:
                    # Split full name into first and last name
                    name_parts = full_name.split()
                    if len(name_parts) >= 2:
                        update_data['first_name'] = name_parts[0]
                        update_data['last_name'] = ' '.join(name_parts[1:])
                    elif len(name_parts) == 1:
                        update_data['first_name'] = name_parts[0]
                        update_data['last_name'] = ''
                    else:
                        update_data['first_name'] = ''
                        update_data['last_name'] = ''
                else:
                    update_data['first_name'] = ''
                    update_data['last_name'] = ''
                # Remove the full_name field as it's not a database field
                del update_data['full_name']
                logger.info(f"Parsed full_name '{full_name}' into first_name: '{update_data.get('first_name')}', last_name: '{update_data.get('last_name')}'")
            
            # Clean up any empty or invalid UUID fields
            uuid_fields = ['organization', 'organization_id']
            invalid_org_values = ['', 'No Organization', 'null', 'undefined', None]
            
            for field in uuid_fields:
                if field in update_data:
                    value = update_data[field]
                    if value in invalid_org_values:
                        logger.info(f"Removing invalid UUID field '{field}': {value}")
                        del update_data[field]
            
            update_data['updated_from_ip'] = self._get_client_ip(request)
            update_data['user_agent'] = request.META.get('HTTP_USER_AGENT', 'API')
            
            updated_user = self.user_service.update_user(
                updating_user=request.user,
                user_id=str(request.user.id),
                update_data=update_data
            )
            
            user_details = self.user_service.get_user_details(
                requesting_user=request.user,
                user_id=str(updated_user.id)
            )
            
            return Response({
                'success': True,
                'data': {
                    'profile': user_details,
                    'message': 'Profile updated successfully'
                }
            }, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            logger.error(f"Validation error in profile update: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except PermissionDenied as e:
            logger.error(f"Permission denied in profile update: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Update profile error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update profile'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['delete'])
    def delete_user(self, request, pk=None):
        """
        Permanently delete a user account.
        
        Expected payload:
        {
            "reason": "string",
            "confirm": true
        }
        """
        try:
            reason = request.data.get('reason', '')
            confirm = request.data.get('confirm', False)
            
            if not confirm:
                return Response({
                    'success': False,
                    'message': 'Confirmation required to delete user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success = self.user_service.delete_user_permanently(
                deleting_user=request.user,
                user_id=pk,
                reason=reason
            )
            
            if success:
                return Response({
                    'success': True,
                    'data': {
                        'message': 'User deleted successfully',
                        'user_id': pk,
                        'reason': reason
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to delete user'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Delete user error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to delete user'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['patch'])
    def change_username(self, request, pk=None):
        """
        Change a user's username.
        
        Expected payload:
        {
            "new_username": "string"
        }
        """
        try:
            new_username = request.data.get('new_username')
            
            if not new_username:
                return Response({
                    'success': False,
                    'message': 'New username is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            updated_user = self.user_service.change_username(
                requesting_user=request.user,
                user_id=pk,
                new_username=new_username
            )
            
            user_details = self.user_service.get_user_details(request.user, str(updated_user.id))
            
            return Response({
                'success': True,
                'data': {
                    'user': user_details,
                    'message': f'Username changed to {new_username} successfully'
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Change username error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to change username'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user statistics for accessible organizations."""
        try:
            organization_id = request.query_params.get('organization_id')
            
            stats = self.user_service.get_user_statistics(
                requesting_user=request.user,
                organization_id=organization_id
            )
            
            return Response({
                'success': True,
                'data': {
                    'statistics': stats
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Get statistics error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip