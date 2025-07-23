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
from ..models import CustomUser, AuthenticationLog
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
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['login', 'register', 'forgot_password', 'validate_reset_token', 'reset_password']:
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]
    
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
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new user.
        
        Expected payload:
        {
            "username": "string",
            "password": "string",
            "password_confirm": "string", 
            "email": "string",
            "first_name": "string",
            "last_name": "string",
            "organization": "string",
            "role": "string"
        }
        """
        try:
            # Extract registration data
            username = request.data.get('username')
            password = request.data.get('password')
            password_confirm = request.data.get('password_confirm')
            email = request.data.get('email')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            organization = request.data.get('organization')
            role = request.data.get('role', 'viewer')
            
            # For anonymous registration, only allow viewer role
            if not request.user.is_authenticated:
                role = 'viewer'
            
            # Validate required fields
            if not all([username, password, password_confirm, email, first_name, last_name, organization]):
                return Response({
                    'success': False,
                    'message': 'All fields are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate password confirmation
            if password != password_confirm:
                return Response({
                    'success': False,
                    'message': 'Passwords do not match'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find or create organization by name
            try:
                from ..models import Organization
                org, created = Organization.objects.get_or_create(
                    name=organization,
                    defaults={
                        'domain': organization.lower().replace(' ', '') + '.local',
                        'contact_email': email,
                        'organization_type': 'educational',
                        'is_active': True,
                        'is_verified': False,
                        'created_by': username
                    }
                )
                
                # Create user using UserService with correct parameter order
                user_data = {
                    'username': username,
                    'password': password,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'organization_id': str(org.id),
                    'role': role,
                    'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown')
                }
                
                # Call with correct parameter order: creating_user, user_data
                user = self.user_service.create_user(
                    creating_user=request.user if request.user.is_authenticated else None,
                    user_data=user_data
                )
                
                result = {
                    'success': True,
                    'user_info': {
                        'id': str(user.id),
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                        'organization': user.organization.name if user.organization else None
                    }
                }
                
            except Exception as e:
                logger.error(f"User creation error: {str(e)}")
                result = {
                    'success': False,
                    'message': f'User creation failed: {str(e)}'
                }
            
            if result['success']:
                # Authenticate the newly created user
                auth_result = self.auth_service.authenticate_user(
                    username=username,
                    password=password,
                    request=request
                )
                
                if auth_result.get('success'):
                    return Response({
                        'success': True,
                        'message': 'User registered successfully',
                        'user': auth_result.get('user'),
                        'token': str(auth_result.get('tokens').get('access')),
                        'refresh_token': str(auth_result.get('tokens').get('refresh'))
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': True,
                        'message': 'User created but authentication failed',
                        'user': result.get('user_info')
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': result.get('message', 'Registration failed')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Registration failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def forgot_password(self, request):
        """
        Request password reset email.
        
        Expected payload:
        {
            "email": "user@example.com"
        }
        """
        try:
            email = request.data.get('email')
            
            if not email:
                return Response({
                    'success': False,
                    'message': 'Email address is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find user by email
            try:
                user = CustomUser.objects.get(email=email, is_active=True)
            except CustomUser.DoesNotExist:
                # For security, don't reveal if email exists or not
                return Response({
                    'success': True,
                    'message': 'If an account with this email exists, password reset instructions have been sent.'
                }, status=status.HTTP_200_OK)
            
            # Generate password reset token
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset URL pointing to React frontend
            frontend_url = "http://localhost:5173"  # React frontend URL
            reset_url = f"{frontend_url}/reset-password?token={uid}-{token}"
            
            # Send email (you'll need to implement the email service)
            try:
                from core.notifications.services.gmail_smtp_service import GmailSMTPService
                email_service = GmailSMTPService()
                
                subject = "CRISP - Password Reset Request"
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                        <h1 style="color: white; margin: 0;">CRISP Password Reset</h1>
                    </div>
                    
                    <div style="padding: 30px; background-color: #f8f9fa;">
                        <p>Hello {user.first_name or user.username},</p>
                        
                        <p>We received a request to reset your password for your CRISP account. If you didn't make this request, you can safely ignore this email.</p>
                        
                        <p>To reset your password, click the button below:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" 
                               style="background: linear-gradient(135deg, #667eea, #764ba2); 
                                      color: white; 
                                      padding: 12px 30px; 
                                      text-decoration: none; 
                                      border-radius: 8px; 
                                      display: inline-block;
                                      font-weight: bold;">
                                Reset My Password
                            </a>
                        </div>
                        
                        <p style="color: #666; font-size: 14px;">
                            If the button doesn't work, you can also copy and paste this link into your browser:
                        </p>
                        <p style="word-break: break-all; background-color: #e9ecef; padding: 10px; border-radius: 4px; font-size: 12px;">
                            {reset_url}
                        </p>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 30px;">
                            This link will expire in 24 hours for security reasons.
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="color: #999; font-size: 12px;">
                            If you're having trouble, please contact our support team.
                        </p>
                    </div>
                </body>
                </html>
                """
                
                email_service.send_email(
                    to_emails=[email],
                    subject=subject,
                    html_content=html_content
                )
                
                logger.info(f"Password reset email sent to {email}")
                
            except Exception as e:
                logger.error(f"Failed to send password reset email to {email}: {str(e)}")
                return Response({
                    'success': False,
                    'message': 'Failed to send password reset email. Please try again later.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'success': True,
                'message': 'Password reset instructions have been sent to your email address.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Forgot password error: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while processing your request'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_reset_token(self, request):
        """
        Validate password reset token.
        
        Expected payload:
        {
            "token": "uid-token"
        }
        """
        try:
            token_string = request.data.get('token')
            
            if not token_string or '-' not in token_string:
                return Response({
                    'success': False,
                    'message': 'Invalid token format'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                uid, token = token_string.split('-', 1)
                
                from django.utils.http import urlsafe_base64_decode
                from django.utils.encoding import force_str
                
                user_id = force_str(urlsafe_base64_decode(uid))
                user = CustomUser.objects.get(pk=user_id, is_active=True)
                
                from django.contrib.auth.tokens import default_token_generator
                
                if default_token_generator.check_token(user, token):
                    return Response({
                        'success': True,
                        'message': 'Token is valid'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'message': 'Invalid or expired token'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except (ValueError, CustomUser.DoesNotExist):
                return Response({
                    'success': False,
                    'message': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Token validation failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request):
        """
        Reset password using valid token.
        
        Expected payload:
        {
            "token": "uid-token",
            "new_password": "newpassword123"
        }
        """
        try:
            token_string = request.data.get('token')
            new_password = request.data.get('new_password')
            
            if not token_string or not new_password:
                return Response({
                    'success': False,
                    'message': 'Token and new password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if '-' not in token_string:
                return Response({
                    'success': False,
                    'message': 'Invalid token format'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                uid, token = token_string.split('-', 1)
                
                from django.utils.http import urlsafe_base64_decode
                from django.utils.encoding import force_str
                from django.contrib.auth.tokens import default_token_generator
                
                user_id = force_str(urlsafe_base64_decode(uid))
                user = CustomUser.objects.get(pk=user_id, is_active=True)
                
                if not default_token_generator.check_token(user, token):
                    return Response({
                        'success': False,
                        'message': 'Invalid or expired token'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate password strength
                from django.contrib.auth.password_validation import validate_password
                from django.core.exceptions import ValidationError
                
                try:
                    validate_password(new_password, user)
                except ValidationError as e:
                    return Response({
                        'success': False,
                        'message': ', '.join(e.messages)
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Reset password
                user.set_password(new_password)
                user.failed_login_attempts = 0  # Reset failed attempts
                user.save(update_fields=['password', 'failed_login_attempts'])
                
                # Log password reset
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='password_reset',
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                    user_agent=request.META.get('HTTP_USER_AGENT', 'API'),
                    success=True,
                    additional_data={'reset_method': 'email_token'}
                )
                
                logger.info(f"Password reset successful for user {user.username}")
                
                return Response({
                    'success': True,
                    'message': 'Password has been reset successfully'
                }, status=status.HTTP_200_OK)
                
            except (ValueError, CustomUser.DoesNotExist):
                return Response({
                    'success': False,
                    'message': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Password reset failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)