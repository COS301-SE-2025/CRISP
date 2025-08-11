from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import json
import logging

# Import Trust system authentication service
try:
    from core_ut.user_management.services.auth_service import AuthenticationService
    TRUST_AUTH_AVAILABLE = True
except ImportError:
    TRUST_AUTH_AVAILABLE = False

# Import unified decorators
from core.middleware.unified_decorators import api_authentication_required, preserve_core_functionality

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Unified login view that works with both Core and Trust authentication systems.
    Preserves all existing Core functionality while adding Trust system features.
    """
    try:
        data = json.loads(request.body) if request.body else {}
        username = data.get('username')
        password = data.get('password')
        remember_device = data.get('remember_device', False)
        totp_code = data.get('totp_code')
        
        if not username or not password:
            return Response({
                'error': 'Username and password required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try Trust system authentication first if available
        if TRUST_AUTH_AVAILABLE:
            try:
                auth_service = AuthenticationService()
                auth_result = auth_service.authenticate_user(
                    username=username,
                    password=password,
                    request=request,
                    remember_device=remember_device,
                    totp_code=totp_code
                )
                
                if auth_result['success']:
                    # Trust system authentication successful
                    response_data = {
                        'success': True,
                        'message': auth_result['message'],
                        'tokens': auth_result['tokens'],
                        'user': auth_result['user'],
                        'trust_context': auth_result.get('trust_context', {}),
                        'permissions': auth_result.get('permissions', []),
                        'accessible_organizations': auth_result.get('accessible_organizations', []),
                        'authentication_method': 'trust_system'
                    }
                    
                    # Add additional flags for special cases
                    if auth_result.get('requires_2fa'):
                        response_data['requires_2fa'] = True
                        return Response(response_data, status=status.HTTP_200_OK)
                    
                    if auth_result.get('requires_device_trust'):
                        response_data['requires_device_trust'] = True
                    
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    # Trust system authentication failed
                    error_response = {
                        'success': False,
                        'error': 'Authentication failed',
                        'message': auth_result.get('message', 'Invalid credentials')
                    }
                    
                    # Add specific error flags
                    if auth_result.get('requires_2fa'):
                        error_response['requires_2fa'] = True
                        error_response['message'] = 'Two-factor authentication required'
                        return Response(error_response, status=status.HTTP_200_OK)  # Not an error, just needs 2FA
                    
                    return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
                    
            except Exception as e:
                logger.warning(f"Trust system authentication failed, falling back to Core system: {str(e)}")
        
        # Fallback to Core system authentication (Django's built-in)
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Check if user is active
            if not user.is_active:
                return Response({
                    'error': 'Account is inactive'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Create JWT tokens using Core system method
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Build user info with Core system compatibility
            user_info = {
                'id': str(user.id),  # Ensure string format for consistency
                'username': user.username,
                'email': user.email,
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'is_staff': user.is_staff,
                'is_admin': user.is_superuser,
                'role': 'BlueVisionAdmin' if user.is_superuser else ('staff' if user.is_staff else 'user'),
                'is_verified': True,  # Core system users are considered verified
                'two_factor_enabled': False  # Core system doesn't have 2FA by default
            }
            
            # Add organization info if available
            if hasattr(user, 'organization') and user.organization:
                user_info['organization'] = {
                    'id': str(user.organization.id),
                    'name': user.organization.name,
                    'domain': getattr(user.organization, 'domain', ''),
                    'is_publisher': getattr(user.organization, 'is_publisher', False)
                }
            elif hasattr(user, 'profile') and user.profile and user.profile.organization:
                user_info['organization'] = {
                    'id': str(user.profile.organization.id),
                    'name': user.profile.organization.name,
                    'domain': getattr(user.profile.organization, 'domain', ''),
                    'is_publisher': False
                }
            else:
                user_info['organization'] = None
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                },
                'user': user_info,
                'trust_context': {},  # Empty for Core system users
                'permissions': ['core_access'],  # Basic Core system permission
                'accessible_organizations': [],  # To be populated by middleware
                'authentication_method': 'core_system'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Invalid credentials',
                'message': 'Username or password is incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON',
            'message': 'Request body must contain valid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response({
            'error': 'Authentication system error',
            'message': 'An error occurred during authentication'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@preserve_core_functionality
def system_health(request):
    """
    System health check endpoint.
    Preserves Core system functionality while adding Trust system integration.
    """
    health_data = {
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': '2025-08-09T10:00:00Z',
        'authentication': {
            'trust_system_available': TRUST_AUTH_AVAILABLE,
            'core_system_available': True,
            'unified_auth_enabled': True
        }
    }
    
    # Add user context if authenticated
    if hasattr(request, 'user') and request.user.is_authenticated:
        health_data['user_authenticated'] = True
        health_data['authentication_method'] = (
            'trust_system' if hasattr(request.user, 'role') else 'core_system'
        )
    else:
        health_data['user_authenticated'] = False
    
    return Response(health_data)

@api_view(['GET'])
@api_authentication_required
@preserve_core_functionality
def alert_statistics(request):
    """
    Alert statistics endpoint with authentication required.
    Integrates with Trust system alerts if available.
    """
    try:
        # Try to get Trust system alert statistics
        if TRUST_AUTH_AVAILABLE:
            try:
                from core_ut.alerts.models_ut import Alert
                
                total_alerts = Alert.objects.count()
                critical_alerts = Alert.objects.filter(severity='critical').count()
                recent_alerts = list(
                    Alert.objects.order_by('-created_at')[:5].values(
                        'id', 'title', 'severity', 'status', 'created_at'
                    )
                )
                
                return Response({
                    'total_alerts': total_alerts,
                    'critical_alerts': critical_alerts,
                    'recent_alerts': recent_alerts,
                    'source': 'trust_system'
                })
                
            except ImportError:
                pass
        
        # Fallback to Core system (mock data for now)
        return Response({
            'total_alerts': 0,
            'critical_alerts': 0,
            'recent_alerts': [],
            'source': 'core_system'
        })
        
    except Exception as e:
        logger.error(f"Error getting alert statistics: {str(e)}")
        return Response({
            'error': 'Failed to retrieve alert statistics',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)