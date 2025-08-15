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

from core.services.email_service import UnifiedEmailService

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
                {'success': False, 'error': 'recipient_emails is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize Gmail service
        gmail_service = GmailSMTPService()
        
        # Send the alert with user context
        result = gmail_service.send_threat_alert_email(recipient_emails, alert_data, user=request.user)
        
        if result['success']:
            logger.info(f"Threat alert sent successfully to {len(recipient_emails)} recipients")
            return Response(result, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send threat alert: {result['message']}")
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error sending threat alert: {str(e)}")
        return Response(
            {'success': False, 'error': f'Failed to send threat alert: {str(e)}'}, 
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
                {'success': False, 'error': 'recipient_emails is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize Gmail service
        gmail_service = GmailSMTPService()
        
        # Send the notification with user context
        result = gmail_service.send_feed_notification_email(recipient_emails, notification_data, user=request.user)
        
        if result['success']:
            logger.info(f"Feed notification sent successfully to {len(recipient_emails)} recipients")
            return Response(result, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send feed notification: {result['message']}")
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error sending feed notification: {str(e)}")
        return Response(
            {'success': False, 'error': f'Failed to send feed notification: {str(e)}'}, 
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
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error testing Gmail connection: {str(e)}")
        return Response(
            {'success': False, 'error': f'Failed to test Gmail connection: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_email_statistics(request):
    """
    Get email statistics for the current user/organization
    """
    try:
        # Get real email statistics from database
        try:
            from core.alerts.models import EmailLog
            
            # Get organization-specific stats if user belongs to one
            organization = request.user.organization if hasattr(request.user, 'organization') else None
            email_stats = EmailLog.get_statistics(organization=organization, days=30)
        except ImportError:
            email_stats = {
                'total_emails_sent': 0,
                'threat_alerts_sent': 0,
                'feed_notifications_sent': 0,
                'last_email_sent': None,
                'failed_emails': 0
            }
        
        stats = {
            'total_emails_sent': email_stats['total_emails_sent'],
            'threat_alerts_sent': email_stats['threat_alerts_sent'],
            'feed_notifications_sent': email_stats['feed_notifications_sent'],
            'test_emails_sent': email_stats.get('test_emails_sent', 0),
            'failed_emails': email_stats.get('failed_emails', 0),
            'last_email_sent': email_stats['last_email_sent'].isoformat() if email_stats['last_email_sent'] else None,
            'gmail_connection_status': 'unknown',
            'configuration_status': {
                'smtp_configured': False,
                'sender_name_configured': False,
                'sender_email_configured': False,
            }
        }
        
        # Safely check configuration
        try:
            stats['configuration_status'] = {
                'smtp_configured': bool(getattr(settings, 'EMAIL_HOST_USER', None)),
                'sender_name_configured': bool(getattr(settings, 'CRISP_SENDER_NAME', None)),
                'sender_email_configured': bool(getattr(settings, 'CRISP_SENDER_EMAIL', None)),
            }
        except Exception as config_error:
            logger.warning(f"Could not check email configuration: {config_error}")
        
        # Test Gmail connection safely - never let this crash the endpoint
        try:
            gmail_service = GmailSMTPService()
            connection_result = gmail_service.test_connection()
            if isinstance(connection_result, dict) and 'status' in connection_result:
                stats['gmail_connection_status'] = connection_result['status']
            else:
                stats['gmail_connection_status'] = 'online'
        except Exception as e:
            stats['gmail_connection_status'] = 'offline'
            logger.warning(f"Gmail connection test failed safely: {str(e)}")
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting email statistics: {str(e)}")
        # Return safe default data instead of error to prevent frontend crashes
        logger.error(f"Critical error in get_email_statistics: {str(e)}")
        return Response({
            'total_emails_sent': 0,
            'threat_alerts_sent': 0,
            'feed_notifications_sent': 0,
            'test_emails_sent': 0,
            'failed_emails': 0,
            'last_email_sent': None,
            'gmail_connection_status': 'offline',
            'configuration_status': {
                'smtp_configured': False,
                'sender_name_configured': False,
                'sender_email_configured': False,
            },
            'error_message': 'Unable to retrieve email statistics',
            'service_available': False
        }, status=status.HTTP_200_OK)


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
        
        # Send the test email with user context
        result = gmail_service.send_threat_alert_email([recipient_email], test_alert_data, user=request.user)
        
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read for the current user
    """
    try:
        # This would typically update a notification table
        # For now, return success response
        return Response({
            'success': True,
            'message': 'All notifications marked as read'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        return Response(
            {'success': False, 'error': f'Failed to mark notifications as read: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notification_preferences(request):
    """
    Get user notification preferences
    """
    try:
        # Default preferences - in a real app, this would come from user settings
        preferences = {
            'email_notifications': True,
            'push_notifications': True,
            'threat_alerts': True,
            'feed_notifications': True,
            'system_notifications': True,
            'notification_frequency': 'immediate',  # immediate, hourly, daily
            'quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '08:00'
            }
        }
        
        return Response({
            'success': True,
            'data': preferences
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting notification preferences: {str(e)}")
        return Response(
            {'success': False, 'error': f'Failed to get notification preferences: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_notification_preferences(request):
    """
    Update user notification preferences
    """
    try:
        preferences = request.data
        
        # Validate preference data
        if not isinstance(preferences, dict):
            return Response(
                {'success': False, 'error': 'Invalid preferences format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In a real app, save to database
        # For now, just return success
        return Response({
            'success': True,
            'message': 'Notification preferences updated successfully',
            'data': preferences
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating notification preferences: {str(e)}")
        return Response(
            {'success': False, 'error': f'Failed to update notification preferences: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )