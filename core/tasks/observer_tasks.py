"""
Celery Tasks for Observer Pattern Notifications
File: core/tasks/observer_tasks.py

Asynchronous tasks for handling observer notifications.
"""

from celery import shared_task
from typing import Dict, Any, List
import logging
from django.utils import timezone
from django.conf import settings

from core.services.smtp2go_service import SMTP2GoService
from core.patterns.observer import EmailNotificationObserver

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send email notification asynchronously.
    
    Args:
        notification_data: Dictionary containing notification information
        
    Returns:
        Result dictionary with success status
    """
    try:
        smtp2go_service = SMTP2GoService()
        
        notification_type = notification_data.get('type', 'unknown')
        recipients = notification_data.get('recipients', [])
        
        if not recipients:
            logger.warning("No recipients specified for email notification")
            return {'success': False, 'message': 'No recipients specified'}
        
        if notification_type == 'threat_alert':
            result = smtp2go_service.send_threat_alert_email(
                recipients,
                notification_data.get('alert_data', {})
            )
        elif notification_type == 'feed_notification':
            result = smtp2go_service.send_feed_notification_email(
                recipients,
                notification_data.get('feed_data', {})
            )
        else:
            logger.error(f"Unknown notification type: {notification_type}")
            return {'success': False, 'message': f'Unknown notification type: {notification_type}'}
        
        if result['success']:
            logger.info(f"Email notification sent successfully to {len(recipients)} recipients")
        else:
            logger.error(f"Failed to send email notification: {result['message']}")
        
        return result
        
    except Exception as exc:
        logger.error(f"Error sending email notification: {str(exc)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying email notification (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc)
        
        return {'success': False, 'message': f'Failed after {self.max_retries} retries: {str(exc)}'}


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def process_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process alert asynchronously.
    
    Args:
        alert_data: Dictionary containing alert information
        
    Returns:
        Result dictionary with processing status
    """
    try:
        alert_type = alert_data.get('alert_type', 'unknown')
        priority = alert_data.get('priority', 'low')
        
        logger.info(f"Processing alert: {alert_type} (Priority: {priority})")
        
        # Determine recipients based on priority
        recipients = []
        email_settings = getattr(settings, 'EMAIL_NOTIFICATIONS', {})
        default_recipients = email_settings.get('default_recipients', {})
        
        if priority in ['critical', 'high']:
            recipients.extend(default_recipients.get('security_team', []))
            recipients.extend(default_recipients.get('administrators', []))
        elif priority == 'medium':
            recipients.extend(default_recipients.get('security_team', []))
            recipients.extend(default_recipients.get('analysts', []))
        else:
            recipients.extend(default_recipients.get('analysts', []))
        
        # Remove duplicates
        recipients = list(set(recipients))
        
        if recipients:
            # Schedule email notification
            send_email_notification.delay({
                'type': 'threat_alert',
                'recipients': recipients,
                'alert_data': alert_data
            })
        
        # Additional alert processing logic here
        # e.g., update dashboards, trigger automated responses, etc.
        
        return {
            'success': True,
            'message': f'Alert processed successfully',
            'alert_id': alert_data.get('alert_id'),
            'recipients_notified': len(recipients)
        }
        
    except Exception as exc:
        logger.error(f"Error processing alert: {str(exc)}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying alert processing (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc)
        
        return {'success': False, 'message': f'Failed to process alert: {str(exc)}'}


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def batch_notifications(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process batch notifications asynchronously.
    
    Args:
        batch_data: Dictionary containing batch notification information
        
    Returns:
        Result dictionary with batch processing status
    """
    try:
        notifications = batch_data.get('notifications', [])
        batch_type = batch_data.get('batch_type', 'mixed')
        
        logger.info(f"Processing batch of {len(notifications)} notifications (Type: {batch_type})")
        
        if not notifications:
            return {'success': True, 'message': 'No notifications to process'}
        
        # Group notifications by recipient groups
        recipient_groups = {}
        
        for notification in notifications:
            recipients = notification.get('recipients', [])
            priority = notification.get('priority', 'low')
            
            group_key = f"{priority}_{hash(tuple(sorted(recipients)))}"
            
            if group_key not in recipient_groups:
                recipient_groups[group_key] = {
                    'recipients': recipients,
                    'priority': priority,
                    'notifications': []
                }
            
            recipient_groups[group_key]['notifications'].append(notification)
        
        # Process each recipient group
        results = []
        for group_key, group_data in recipient_groups.items():
            try:
                if batch_type == 'alerts':
                    result = _process_batch_alerts(group_data)
                elif batch_type == 'feed_updates':
                    result = _process_batch_feed_updates(group_data)
                else:
                    result = _process_mixed_batch(group_data)
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing batch group {group_key}: {str(e)}")
                results.append({'success': False, 'group': group_key, 'error': str(e)})
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        total = len(results)
        
        return {
            'success': successful == total,
            'message': f'Processed {successful}/{total} batch groups successfully',
            'total_notifications': len(notifications),
            'groups_processed': total,
            'groups_successful': successful,
            'results': results
        }
        
    except Exception as exc:
        logger.error(f"Error processing batch notifications: {str(exc)}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying batch processing (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc)
        
        return {'success': False, 'message': f'Failed to process batch: {str(exc)}'}


def _process_batch_alerts(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a batch of alert notifications."""
    notifications = group_data['notifications']
    recipients = group_data['recipients']
    
    if len(notifications) == 1:
        # Single alert
        alert_data = notifications[0].get('alert_data', {})
    else:
        # Create batch alert summary
        alert_data = _create_batch_alert_summary(notifications)
    
    # Send email
    send_email_notification.delay({
        'type': 'threat_alert',
        'recipients': recipients,
        'alert_data': alert_data
    })
    
    return {
        'success': True,
        'type': 'alerts',
        'count': len(notifications),
        'recipients': len(recipients)
    }


def _process_batch_feed_updates(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a batch of feed update notifications."""
    notifications = group_data['notifications']
    recipients = group_data['recipients']
    
    # Create summary of feed updates
    feed_data = _create_feed_update_summary(notifications)
    
    # Send email
    send_email_notification.delay({
        'type': 'feed_notification',
        'recipients': recipients,
        'feed_data': feed_data
    })
    
    return {
        'success': True,
        'type': 'feed_updates',
        'count': len(notifications),
        'recipients': len(recipients)
    }


def _process_mixed_batch(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a mixed batch of notifications."""
    notifications = group_data['notifications']
    recipients = group_data['recipients']
    
    # Separate alerts from feed updates
    alerts = [n for n in notifications if n.get('type') == 'alert']
    feed_updates = [n for n in notifications if n.get('type') == 'feed_update']
    
    emails_sent = 0
    
    # Process alerts if any
    if alerts:
        alert_data = _create_batch_alert_summary(alerts) if len(alerts) > 1 else alerts[0].get('alert_data', {})
        send_email_notification.delay({
            'type': 'threat_alert',
            'recipients': recipients,
            'alert_data': alert_data
        })
        emails_sent += 1
    
    # Process feed updates if any
    if feed_updates:
        feed_data = _create_feed_update_summary(feed_updates)
        send_email_notification.delay({
            'type': 'feed_notification',
            'recipients': recipients,
            'feed_data': feed_data
        })
        emails_sent += 1
    
    return {
        'success': True,
        'type': 'mixed',
        'alerts': len(alerts),
        'feed_updates': len(feed_updates),
        'emails_sent': emails_sent,
        'recipients': len(recipients)
    }


def _create_batch_alert_summary(alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a summary for multiple alerts."""
    if not alerts:
        return {}
    
    # Find highest priority
    priority_values = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    highest_priority = max(alerts, key=lambda a: priority_values.get(a.get('priority', 'low'), 0))
    
    # Count alert types
    alert_counts = {}
    feed_names = set()
    
    for alert in alerts:
        alert_data = alert.get('alert_data', {})
        alert_type = alert_data.get('alert_type', 'unknown')
        alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        feed_name = alert_data.get('data', {}).get('feed_name')
        if feed_name:
            feed_names.add(feed_name)
    
    return {
        'alert_id': f"batch_{int(timezone.now().timestamp())}",
        'alert_type': 'multiple_alerts',
        'priority': highest_priority.get('priority', 'medium'),
        'generated_at': timezone.now(),
        'data': {
            'alert_count': len(alerts),
            'alert_types': alert_counts,
            'affected_feeds': list(feed_names),
            'summary': f"{len(alerts)} alerts from {len(feed_names)} feed(s)"
        }
    }


def _create_feed_update_summary(feed_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a summary for feed updates."""
    feed_names = set()
    
    for update in feed_updates:
        feed_data = update.get('feed_data', {})
        feed_name = feed_data.get('feed_name')
        if feed_name:
            feed_names.add(feed_name)
    
    return {
        'notification_type': 'feed_updates_summary',
        'feed_name': f"{len(feed_names)} feed(s)",
        'timestamp': timezone.now(),
        'update_count': len(feed_updates),
        'affected_feeds': list(feed_names)
    }


@shared_task
def cleanup_old_notifications() -> Dict[str, Any]:
    """
    Cleanup old notification data periodically.
    
    Returns:
        Cleanup result dictionary
    """
    try:
        # This would clean up old notification logs, cached data, etc.
        # Implementation depends on your specific storage mechanism
        
        logger.info("Starting notification cleanup task")
        
        # Example cleanup logic
        cleanup_results = {
            'old_logs_cleaned': 0,
            'cached_data_cleared': 0,
            'expired_sessions_removed': 0
        }
        
        # Add actual cleanup logic here
        
        logger.info(f"Notification cleanup completed: {cleanup_results}")
        return {'success': True, 'results': cleanup_results}
        
    except Exception as e:
        logger.error(f"Error during notification cleanup: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def health_check_observers() -> Dict[str, Any]:
    """
    Health check for observer system.
    
    Returns:
        Health check result dictionary
    """
    try:
        # Test SMTP2Go connection
        smtp2go_service = SMTP2GoService()
        smtp2go_status = smtp2go_service.test_connection()
        
        # Check other observer system components
        health_status = {
            'smtp2go': smtp2go_status,
            'celery_workers': True,  # Would check actual worker status
            'notification_queues': True,  # Would check queue status
            'timestamp': timezone.now().isoformat()
        }
        
        overall_health = all(
            status.get('success', True) if isinstance(status, dict) else status
            for status in health_status.values()
            if status != health_status['timestamp']
        )
        
        logger.info(f"Observer system health check: {'HEALTHY' if overall_health else 'UNHEALTHY'}")
        
        return {
            'success': True,
            'healthy': overall_health,
            'details': health_status
        }
        
    except Exception as e:
        logger.error(f"Error during observer health check: {str(e)}")
        return {
            'success': False,
            'healthy': False,
            'error': str(e)
        }