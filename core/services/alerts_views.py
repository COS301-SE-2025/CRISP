"""
Alerts API Views for CRISP
Handles Gmail SMTP alerts and notifications
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
import logging

from .gmail_smtp_service import GmailSMTPService

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_alerts_list(request):
    """
    Get list of alerts/notifications for the user
    """
    try:
        # For now, return empty list - this can be expanded to return actual alerts from database
        alerts = []
        
        return Response({
            'success': True,
            'data': alerts
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to fetch alerts'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_threat_alert(request):
    """
    Send a threat alert email via Gmail SMTP
    """
    try:
        alert_data = request.data
        recipient_emails = alert_data.get('recipient_emails', [])
        
        if not recipient_emails:
            return Response(
                {'error': 'recipient_emails is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize Gmail service
        gmail_service = GmailSMTPService()
        
        # Send the alert
        result = gmail_service.send_threat_alert_email(recipient_emails, alert_data)
        
        if result['success']:
            logger.info(f"Threat alert sent successfully to {len(recipient_emails)} recipients")
            return Response(result, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send threat alert: {result['message']}")
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error sending threat alert: {str(e)}")
        return Response(
            {'error': f'Failed to send threat alert: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_feed_notification(request):
    """
    Send a feed notification email via Gmail SMTP
    """
    try:
        notification_data = request.data
        recipient_emails = notification_data.get('recipient_emails', [])
        
        if not recipient_emails:
            return Response(
                {'error': 'recipient_emails is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize Gmail service
        gmail_service = GmailSMTPService()
        
        # Send the notification
        result = gmail_service.send_feed_notification_email(recipient_emails, notification_data)
        
        if result['success']:
            logger.info(f"Feed notification sent successfully to {len(recipient_emails)} recipients")
            return Response(result, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send feed notification: {result['message']}")
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error sending feed notification: {str(e)}")
        return Response(
            {'error': f'Failed to send feed notification: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_gmail_connection(request):
    """
    Test the Gmail SMTP connection
    """
    try:
        # Initialize Gmail service
        gmail_service = GmailSMTPService()
        
        # Test connection
        result = gmail_service.test_connection()
        
        if result['success']:
            logger.info("Gmail SMTP connection test successful")
            return Response(result, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Gmail SMTP connection test failed: {result['message']}")
            return Response(result, status=status.HTTP_200_OK)  # Still return 200 but with error info
            
    except Exception as e:
        logger.error(f"Error testing Gmail connection: {str(e)}")
        return Response(
            {'error': f'Failed to test Gmail connection: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_email_statistics(request):
    """
    Get email statistics for the current user/organization
    """
    try:
        # For now, return mock statistics
        # In a full implementation, this would query a database for actual stats
        stats = {
            'total_emails_sent': 0,
            'threat_alerts_sent': 0,
            'feed_notifications_sent': 0,
            'last_email_sent': None,
            'gmail_connection_status': 'unknown',
            'configuration_status': {
                'smtp_configured': bool(getattr(settings, 'EMAIL_HOST_USER', None)),
                'sender_name_configured': bool(getattr(settings, 'CRISP_SENDER_NAME', None)),
                'sender_email_configured': bool(getattr(settings, 'CRISP_SENDER_EMAIL', None)),
            }
        }
        
        # Test Gmail connection to get current status
        try:
            gmail_service = GmailSMTPService()
            connection_result = gmail_service.test_connection()
            stats['gmail_connection_status'] = connection_result['status']
        except Exception as e:
            stats['gmail_connection_status'] = 'error'
            logger.warning(f"Could not test Gmail connection for statistics: {str(e)}")
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting email statistics: {str(e)}")
        return Response(
            {'error': f'Failed to get email statistics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_email(request):
    """
    Send a test email to verify Gmail integration is working
    """
    try:
        recipient_email = request.data.get('recipient_email')
        
        if not recipient_email:
            return Response(
                {'error': 'recipient_email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize Gmail service
        gmail_service = GmailSMTPService()
        
        # Prepare test email data
        test_alert_data = {
            'alert_type': 'test_email',
            'priority': 'info',
            'generated_at': timezone.now(),
            'alert_id': f'test-{timezone.now().timestamp()}',
            'data': {
                'message': 'This is a test email to verify Gmail SMTP integration',
                'sender': request.user.username if hasattr(request, 'user') else 'System'
            }
        }
        
        # Send the test email
        result = gmail_service.send_threat_alert_email([recipient_email], test_alert_data)
        
        if result['success']:
            logger.info(f"Test email sent successfully to {recipient_email}")
            return Response({
                'success': True,
                'message': f'Test email sent successfully to {recipient_email}',
                'details': result
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send test email: {result['message']}")
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return Response(
            {'error': f'Failed to send test email: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )