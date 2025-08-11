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