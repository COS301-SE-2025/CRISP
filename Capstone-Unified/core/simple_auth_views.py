from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import json

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        data = json.loads(request.body) if request.body else {}
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                },
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                    'is_admin': user.is_superuser,
                    'role': 'BlueVisionAdmin' if user.is_superuser else 'user'
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organizations_simple(request):
    """Get organizations list (simplified version)"""
    try:
        # Debug logging
        print(f"DEBUG: Organizations request from user: {request.user}")
        print(f"DEBUG: Authorization header: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
        
        # Return mock organizations for now
        mock_organizations = [
            {
                "id": "1",
                "name": "BlueVision Security",
                "organization_type": "security_vendor",
                "description": "Security vendor organization",
                "is_active": True,
                "created_date": timezone.now().isoformat()
            },
            {
                "id": "2", 
                "name": "University Research Lab",
                "organization_type": "educational",
                "description": "Educational research organization",
                "is_active": True,
                "created_date": timezone.now().isoformat()
            },
            {
                "id": "3",
                "name": "Financial Corp",
                "organization_type": "financial", 
                "description": "Financial services organization",
                "is_active": True,
                "created_date": timezone.now().isoformat()
            },
            {
                "id": "4",
                "name": "Tech Industries",
                "organization_type": "technology",
                "description": "Technology company",
                "is_active": True,
                "created_date": timezone.now().isoformat()
            }
        ]
        
        return Response({
            'success': True,
            'data': {
                'organizations': mock_organizations,
                'total_count': len(mock_organizations)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get organizations: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def system_health(request):
    return Response({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': '2025-08-09T10:00:00Z'
    })

@api_view(['GET'])
def alert_statistics(request):
    return Response({
        'total_alerts': 0,
        'critical_alerts': 0,
        'recent_alerts': []
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_email(request):
    """Send a test email to verify email configuration"""
    try:
        data = json.loads(request.body) if request.body else {}
        recipient_email = data.get('email', request.user.email)
        
        if not recipient_email:
            return Response({
                'success': False,
                'message': 'No email address provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send test email
        subject = 'CRISP System - Test Email'
        message = f'''
        This is a test email from the CRISP Threat Intelligence Platform.
        
        Sent to: {recipient_email}
        Sent at: {timezone.now()}
        From user: {request.user.username}
        
        If you received this email, your email configuration is working correctly.
        '''
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@crisp-system.example.com')
        
        send_mail(
            subject,
            message,
            from_email,
            [recipient_email],
            fail_silently=False,
        )
        
        return Response({
            'success': True,
            'message': f'Test email sent successfully to {recipient_email}'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to send test email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get or update current user profile"""
    try:
        user = request.user
        
        if request.method == 'GET':
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'job_title': 'Security Administrator',  # Default job title
                'organization': 'BlueVision Security',  # Default organization
                'organization_id': '1',
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'role': 'BlueVisionAdmin' if user.is_superuser else 'user'
            }
            
            return Response({
                'success': True,
                'data': {
                    'profile': user_data
                },
                'user': user_data  # Keep both formats for compatibility
            }, status=status.HTTP_200_OK)
            
        elif request.method == 'PUT':
            data = json.loads(request.body) if request.body else {}
            
            # Update user fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']
            
            user.save()
            
            # For now, store job_title in session or use default
            job_title = data.get('job_title', 'Security Administrator')
            
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'job_title': job_title,
                'organization': 'BlueVision Security',  # Default organization
                'organization_id': '1',
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'role': 'BlueVisionAdmin' if user.is_superuser else 'user'
            }
            
            return Response({
                'success': True,
                'data': {
                    'profile': user_data
                },
                'user': user_data,  # Keep both formats for compatibility
                'message': 'Profile updated successfully'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to process user profile: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_statistics(request):
    """Get user statistics"""
    try:
        # Basic user statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        
        return Response({
            'success': True,
            'statistics': {
                'total_users': total_users,
                'active_users': active_users,
                'staff_users': staff_users,
                'superusers': superusers,
                'inactive_users': total_users - active_users,
                'regular_users': total_users - staff_users,
                'current_user': {
                    'username': request.user.username,
                    'role': 'BlueVisionAdmin' if request.user.is_superuser else 'user',
                    'permissions': {
                        'is_staff': request.user.is_staff,
                        'is_superuser': request.user.is_superuser,
                        'can_manage_users': request.user.is_staff,
                        'can_view_statistics': request.user.is_staff
                    }
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get user statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_gmail_connection(request):
    """Test Gmail SMTP connection"""
    try:
        from django.core.mail import get_connection
        
        # Test the email connection
        connection = get_connection()
        connection.open()
        connection.close()
        
        return Response({
            'success': True,
            'message': 'Gmail connection successful',
            'email_backend': settings.EMAIL_BACKEND,
            'email_host': getattr(settings, 'EMAIL_HOST', 'Not configured'),
            'email_port': getattr(settings, 'EMAIL_PORT', 'Not configured'),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Gmail connection failed: {str(e)}',
            'error_type': type(e).__name__
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_alert_test_email(request):
    """Send test email for alerts system"""
    try:
        data = json.loads(request.body) if request.body else {}
        recipient_email = data.get('recipient_email') or data.get('email')
        
        if not recipient_email:
            return Response({
                'success': False,
                'message': 'No email address provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send test email
        subject = 'CRISP Alert System - Test Email'
        message = f'''
This is a test email from the CRISP Threat Intelligence Alert System.

Recipient: {recipient_email}
Sent at: {timezone.now()}
From user: {request.user.username}

If you received this email, your email configuration is working correctly.
The CRISP system can now send threat intelligence alerts and notifications.

Best regards,
CRISP Threat Intelligence Platform
        '''
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@crisp-system.example.com')
        
        send_mail(
            subject,
            message,
            from_email,
            [recipient_email],
            fail_silently=False,
        )
        
        return Response({
            'success': True,
            'message': f'Test email sent successfully to {recipient_email}',
            'recipient': recipient_email,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to send test email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)