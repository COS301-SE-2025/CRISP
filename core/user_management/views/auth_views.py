from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ..services.auth_service import AuthenticationService
from ..services.user_service import UserService
from ..services.trust_aware_service import TrustAwareService
import logging
import json
import uuid
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)

# Add this custom JSON encoder class
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

@method_decorator(csrf_exempt, name='dispatch')
class AuthenticationViewSet(viewsets.ViewSet):
    """Authentication viewset for login/logout operations"""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Default permission
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthenticationService()
        self.user_service = UserService()
        self.trust_service = TrustAwareService()
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Handle user login"""
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            totp_code = request.data.get('totp_code')
            remember_device = request.data.get('remember_device', False)
            
            if not username or not password:
                return Response(
                    {'success': False, 'message': 'Username and password are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.auth_service.authenticate_user(
                username=username,
                password=password,
                request=request,
                totp_code=totp_code,
                remember_device=remember_device
            )
            
            if result.get('success'):
                # User data is already formatted by the auth service
                return Response({
                    'success': True,
                    'tokens': {
                        'access': str(result.get('tokens').get('access')),
                        'refresh': str(result.get('tokens').get('refresh'))
                    },
                    'user': result.get('user')
                }, status=status.HTTP_200_OK)
            else:
                # Handle different failure types
                if result.get('requires_2fa'):
                    return Response(result, status=status.HTTP_200_OK)
                elif result.get('requires_device_trust'):
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {'success': False, 'message': result.get('message', 'Authentication failed')}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
        except Exception as e:
            logger.error(f"Login exception: {str(e)}")
            return Response(
                {'success': False, 'message': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """
        Refresh access token and return updated trust context.
        
        Expected payload:
        {
            "refresh_token": "string"
        }
        """
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response({
                    'success': False,
                    'message': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            refresh_result = self.auth_service.refresh_token(refresh_token, request)
            
            if refresh_result['success']:
                return Response({
                    'success': True,
                    'data': {
                        'tokens': refresh_result['tokens'],
                        'session_id': refresh_result['session_id'],
                        'user': refresh_result['user'],
                        'trust_context': refresh_result['trust_context'],
                        'permissions': refresh_result['permissions'],
                        'accessible_organizations': refresh_result['accessible_organizations']
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': refresh_result['message']
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Token refresh failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Logout user and invalidate session(s).
        
        Expected payload:
        {
            "session_id": "string" (optional, to logout specific session)
        }
        """
        try:
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': 'User not authenticated'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            session_id = request.data.get('session_id')
            
            logout_result = self.auth_service.logout_user(
                user=request.user,
                session_id=session_id,
                request=request
            )
            
            if logout_result['success']:
                return Response({
                    'success': True,
                    'message': logout_result['message']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': logout_result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Logout failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def verify(self, request):
        """
        Verify current token and return user context.
        """
        try:
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': 'Token is invalid or expired'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get fresh user data with trust context
            user = request.user
            trust_context = self.trust_service._get_user_trust_context(user)
            permissions = list(self.auth_service.access_control.get_user_permissions(user))
            accessible_orgs = self.auth_service._format_accessible_organizations(user)
            
            return Response({
                'success': True,
                'data': {
                    'user': self.auth_service._format_user_info(user),
                    'trust_context': trust_context,
                    'permissions': permissions,
                    'accessible_organizations': accessible_orgs,
                    'token_valid': True
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Token verification failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def sessions(self, request):
        """
        Get active sessions for the current user.
        """
        try:
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': 'Authentication required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            sessions = self.auth_service.get_user_sessions(request.user)
            
            return Response({
                'success': True,
                'data': {
                    'sessions': sessions,
                    'total_count': len(sessions)
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Get sessions error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve sessions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def revoke_session(self, request):
        """
        Revoke a specific session.
        
        Expected payload:
        {
            "session_id": "string"
        }
        """
        try:
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': 'Authentication required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            session_id = request.data.get('session_id')
            
            if not session_id:
                return Response({
                    'success': False,
                    'message': 'Session ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success = self.auth_service.revoke_session(request.user, session_id)
            
            if success:
                return Response({
                    'success': True,
                    'message': 'Session revoked successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Session not found or already revoked'
                }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Revoke session error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to revoke session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password.
        
        Expected payload:
        {
            "current_password": "string",
            "new_password": "string",
            "new_password_confirm": "string"
        }
        """
        try:
            # Debug logging
            logger.info(f"Change password request from user: {request.user}")
            logger.info(f"Request data: {request.data}")
            logger.info(f"User authenticated: {request.user.is_authenticated}")
            
            if not request.user.is_authenticated:
                logger.warning("Change password failed: User not authenticated")
                return Response({
                    'success': False,
                    'message': 'Authentication required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            new_password_confirm = request.data.get('new_password_confirm')
            
            logger.info(f"Password fields - current: {'Present' if current_password else 'Missing'}, new: {'Present' if new_password else 'Missing'}, confirm: {'Present' if new_password_confirm else 'Missing'}")
            
            if not all([current_password, new_password, new_password_confirm]):
                logger.warning("Change password failed: Missing required fields")
                return Response({
                    'success': False,
                    'message': 'All password fields are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if new_password != new_password_confirm:
                logger.warning("Change password failed: Password confirmation mismatch")
                return Response({
                    'success': False,
                    'message': 'New passwords do not match'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Calling user service to change password for user: {request.user.id}")
            success = self.user_service.change_user_password(
                requesting_user=request.user,
                user_id=str(request.user.id),
                new_password=new_password,
                current_password=current_password
            )
            
            if success:
                logger.info("Password change successful")
                return Response({
                    'success': True,
                    'message': 'Password changed successfully'
                }, status=status.HTTP_200_OK)
            else:
                logger.warning("Password change failed in service layer")
                return Response({
                    'success': False,
                    'message': 'Failed to change password'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Change password error: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get dashboard data with trust-aware information.
        """
        try:
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': 'Authentication required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            dashboard_data = self.trust_service.get_user_dashboard_data(request.user)
            
            return Response({
                'success': True,
                'data': dashboard_data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Dashboard error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to load dashboard data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)