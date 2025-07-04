from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import logout
from django.utils import timezone
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import TemplateView
import secrets
import hashlib
from datetime import timedelta

from ..models import CustomUser, AuthenticationLog, UserSession
from ..serializers import (
    UserLoginSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer,
    TokenRefreshSerializer, TrustedDeviceSerializer
)
from ..services.auth_service import AuthenticationService
from ..observers.auth_observers import auth_event_subject


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with enhanced user data"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['role'] = user.role
        token['organization'] = user.organization.name if user.organization else None
        token['is_publisher'] = user.is_publisher
        token['is_verified'] = user.is_verified
        
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token generation with enhanced security"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Handle login with comprehensive security checks"""
        auth_service = AuthenticationService()
        
        # Extract login data
        username = request.data.get('username')
        password = request.data.get('password')
        remember_device = request.data.get('remember_device', False)
        totp_code = request.data.get('totp_code')
        
        if not username or not password:
            return Response({
                'error': 'invalid_credentials',
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        auth_result = auth_service.authenticate_user(
            username=username,
            password=password,
            request=request,
            remember_device=remember_device,
            totp_code=totp_code
        )
        
        if not auth_result['success']:
            return Response({
                'error': 'authentication_failed',
                'message': auth_result['message'],
                'requires_2fa': auth_result.get('requires_2fa', False)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'success': True,
            'tokens': auth_result['tokens'],
            'user': {
                'id': str(auth_result['user'].id),
                'username': auth_result['user'].username,
                'email': auth_result['user'].email,
                'role': auth_result['user'].role,
                'organization': auth_result['user'].organization.name if auth_result['user'].organization else None,
                'is_publisher': auth_result['user'].is_publisher,
                'is_verified': auth_result['user'].is_verified
            },
            'session_id': auth_result['session_id']
        }, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh with security logging"""
    
    def post(self, request, *args, **kwargs):
        """Handle token refresh with logging"""
        auth_service = AuthenticationService()
        
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': 'invalid_request',
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Refresh token
        refresh_result = auth_service.refresh_token(refresh_token, request)
        
        if not refresh_result['success']:
            return Response({
                'error': 'token_refresh_failed',
                'message': refresh_result['message']
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'success': True,
            'tokens': refresh_result['tokens'],
            'session_id': refresh_result['session_id']
        }, status=status.HTTP_200_OK)


class CustomTokenVerifyView(TokenVerifyView):
    """Token verification with activity tracking"""
    
    def post(self, request, *args, **kwargs):
        """Verify token and return user info"""
        auth_service = AuthenticationService()
        
        token = request.data.get('token')
        if not token:
            return Response({
                'error': 'invalid_request',
                'message': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify token
        verification_result = auth_service.verify_token(token, request)
        
        if not verification_result['success']:
            return Response({
                'error': 'token_invalid',
                'message': verification_result['message']
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'success': True,
            'valid': True,
            'user': {
                'id': verification_result['user_id'],
                'username': verification_result['username'],
                'role': verification_result['role'],
                'organization': verification_result['organization'],
                'is_publisher': verification_result['is_publisher']
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """User logout with session management"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Logout user and invalidate session"""
        auth_service = AuthenticationService()
        
        session_id = request.data.get('session_id')
        
        # Logout user
        logout_result = auth_service.logout_user(
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
                'error': 'logout_failed',
                'message': logout_result['message']
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """User profile management"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Update user profile"""
        serializer = UserProfileUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Log profile update
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            
            AuthenticationLog.log_authentication_event(
                user=request.user,
                action='user_updated',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                additional_data={'fields_updated': list(request.data.keys())}
            )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class PasswordChangeView(APIView):
    """Password change functionality"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Change password
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            # Log password change
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            
            AuthenticationLog.log_authentication_event(
                user=request.user,
                action='password_changed',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            # Notify observers
            auth_event_subject.notify_observers(
                event_type='password_changed',
                user=request.user,
                event_data={
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'success': True
                }
            )
            
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class PasswordResetView(APIView):
    """Password reset request"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Request password reset"""
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = CustomUser.objects.get(email=email, is_active=True)
                
                # Generate reset token
                reset_token = secrets.token_urlsafe(32)
                user.password_reset_token = reset_token
                user.password_reset_expires = timezone.now() + timedelta(hours=1)
                user.save(update_fields=['password_reset_token', 'password_reset_expires'])
                
                # Log password reset request
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
                
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='password_reset',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True
                )
                
                # TODO: Send email with reset token
                # For now, return success without revealing if email exists
                
            except CustomUser.DoesNotExist:
                # Don't reveal if email exists
                pass
            
            return Response({
                'success': True,
                'message': 'If the email exists, a password reset link has been sent'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class PasswordResetConfirmView(APIView):
    """Password reset confirmation"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Confirm password reset"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = CustomUser.objects.get(
                    password_reset_token=token,
                    password_reset_expires__gt=timezone.now(),
                    is_active=True
                )
                
                # Reset password
                user.set_password(new_password)
                user.password_reset_token = None
                user.password_reset_expires = None
                user.save()
                
                # Log password reset confirmation
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
                
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='password_reset_confirm',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True
                )
                
                return Response({
                    'success': True,
                    'message': 'Password reset successfully'
                }, status=status.HTTP_200_OK)
                
            except CustomUser.DoesNotExist:
                return Response({
                    'error': 'invalid_token',
                    'message': 'Invalid or expired reset token'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class TrustedDeviceView(APIView):
    """Manage trusted devices"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's trusted devices"""
        return Response({
            'trusted_devices': request.user.trusted_devices
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Add or remove trusted device"""
        serializer = TrustedDeviceSerializer(data=request.data)
        
        if serializer.is_valid():
            device_fingerprint = serializer.validated_data['device_fingerprint']
            action = serializer.validated_data['action']
            
            if action == 'add':
                if device_fingerprint not in request.user.trusted_devices:
                    request.user.trusted_devices.append(device_fingerprint)
                    request.user.save(update_fields=['trusted_devices'])
                    
                    # Log trusted device addition
                    ip_address = self._get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
                    
                    auth_event_subject.notify_observers(
                        event_type='trusted_device_added',
                        user=request.user,
                        event_data={
                            'ip_address': ip_address,
                            'user_agent': user_agent,
                            'device_fingerprint': device_fingerprint,
                            'success': True
                        }
                    )
                
                return Response({
                    'success': True,
                    'message': 'Device added to trusted devices'
                }, status=status.HTTP_200_OK)
            
            elif action == 'remove':
                if device_fingerprint in request.user.trusted_devices:
                    request.user.trusted_devices.remove(device_fingerprint)
                    request.user.save(update_fields=['trusted_devices'])
                    
                    # Log trusted device removal
                    ip_address = self._get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
                    
                    auth_event_subject.notify_observers(
                        event_type='trusted_device_removed',
                        user=request.user,
                        event_data={
                            'ip_address': ip_address,
                            'user_agent': user_agent,
                            'device_fingerprint': device_fingerprint,
                            'success': True
                        }
                    )
                
                return Response({
                    'success': True,
                    'message': 'Device removed from trusted devices'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class LoginPageView(TemplateView):
    """Web-based login page"""
    template_name = 'auth/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'CRISP User Management - Login'
        return context


class ViewerDashboardView(TemplateView):
    """Viewer dashboard page"""
    template_name = 'viewer_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'CRISP Viewer Dashboard'
        return context


class DebugAuthView(TemplateView):
    """Debug authentication page"""
    template_name = 'debug_auth.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Debug Authentication'
        return context
