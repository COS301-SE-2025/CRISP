"""
Authentication API - JWT token-based authentication endpoints
Handles login, logout, token refresh, and user authentication
"""

import logging
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.user_management.models import AuthenticationLog
from core.user_management.models import CustomUser
from core.services.auth_service import AuthenticationService
from core.services.audit_service import AuditService
from core.serializers.auth_serializer import UserSerializer

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['user_id'] = str(user.id)
        token['username'] = user.username
        token['role'] = user.role
        token['organization_id'] = str(user.organization.id) if user.organization else None
        
        return token
    
    def validate(self, attrs):
        # Perform standard validation
        data = super().validate(attrs)
        
        # Add user data to response
        user = self.user
        data['user'] = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'organization': {
                'id': str(user.organization.id),
                'name': user.organization.name,
                'domain': user.organization.domain
            } if user.organization else None,
            'is_verified': user.is_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with logging"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Log authentication attempt
        username = request.data.get('username')
        if response.status_code == 200:
            try:
                user = CustomUser.objects.get(username=username)
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='login',
                    success=True,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                # Update last login
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                logger.info(f"Successful login for user: {username}")
            except CustomUser.DoesNotExist:
                pass
        else:
            # Log failed login attempt
            AuthenticationLog.log_authentication_event(
                username=username,
                action='login',
                success=False,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                failure_reason='Invalid credentials'
            )
            logger.warning(f"Failed login attempt for username: {username}")
        
        return response

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user account
    
    POST /api/auth/register/
    Body: {
        "username": "string",
        "email": "string", 
        "password": "string",
        "first_name": "string",
        "last_name": "string"
    }
    """
    try:
        auth_service = AuthenticationService()
        result = auth_service.register_user(
            username=request.data.get('username'),
            email=request.data.get('email'),
            password=request.data.get('password'),
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', ''),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        if result['success']:
            return Response({
                'success': True,
                'message': result['message'],
                'user_id': result['user_id']
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Registration failed due to server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user by blacklisting refresh token
    
    POST /api/auth/logout/
    Body: {
        "refresh_token": "string"
    }
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log logout
        AuthenticationLog.log_authentication_event(
            user=request.user,
            action='logout',
            success=True,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        logger.info(f"User logged out: {request.user.username}")
        
        return Response({
            'success': True,
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get current user profile
    
    GET /api/auth/profile/
    """
    try:
        user = request.user
        serializer = UserSerializer(user)
        
        return Response({
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to fetch profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update current user profile
    
    PUT /api/auth/profile/
    Body: {
        "first_name": "string",
        "last_name": "string",
        "email": "string"
    }
    """
    try:
        user = request.user
        audit_service = AuditService()
        
        # Track changes
        original_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }
        
        # Update fields
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'email' in request.data:
            # Verify email uniqueness
            if CustomUser.objects.filter(email=request.data['email']).exclude(id=user.id).exists():
                return Response({
                    'success': False,
                    'message': 'Email address is already in use'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.email = request.data['email']
        
        user.save()
        
        # Log profile update
        audit_service.log_user_action(
            user=user,
            action='profile_updated',
            success=True,
            additional_data={
                'original_data': original_data,
                'updated_fields': list(request.data.keys())
            }
        )
        
        serializer = UserSerializer(user)
        logger.info(f"Profile updated for user: {user.username}")
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to update profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password
    
    POST /api/auth/change-password/
    Body: {
        "current_password": "string",
        "new_password": "string"
    }
    """
    try:
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'success': False,
                'message': 'Both current and new passwords are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not user.check_password(current_password):
            # Log failed password change
            AuthenticationLog.log_authentication_event(
                user=user,
                action='password_change',
                success=False,
                failure_reason='Invalid current password',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response({
                'success': False,
                'message': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Change password
        user.set_password(new_password)
        user.save()
        
        # Log successful password change
        AuthenticationLog.log_authentication_event(
            user=user,
            action='password_change',
            success=True,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        logger.info(f"Password changed for user: {user.username}")
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to change password'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Request password reset
    
    POST /api/auth/forgot-password/
    Body: {
        "email": "string"
    }
    """
    try:
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'message': 'Email address is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        auth_service = AuthenticationService()
        result = auth_service.request_password_reset(
            email=email,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Always return success to prevent email enumeration
        return Response({
            'success': True,
            'message': 'If an account with this email exists, a password reset link has been sent'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to process password reset request'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password with token
    
    POST /api/auth/reset-password/
    Body: {
        "token": "string",
        "new_password": "string"
    }
    """
    try:
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not token or not new_password:
            return Response({
                'success': False,
                'message': 'Token and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        auth_service = AuthenticationService()
        result = auth_service.reset_password(
            token=token,
            new_password=new_password,
            ip_address=request.META.get('REMOTE_ADDR')
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
        logger.error(f"Reset password error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to reset password'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify JWT token validity
    
    GET /api/auth/verify-token/
    """
    try:
        return Response({
            'success': True,
            'user': {
                'id': str(request.user.id),
                'username': request.user.username,
                'role': request.user.role,
                'organization': {
                    'id': str(request.user.organization.id),
                    'name': request.user.organization.name
                } if request.user.organization else None
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Token verification failed'
        }, status=status.HTTP_401_UNAUTHORIZED)