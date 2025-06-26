"""
Email Notification Observer with SMTP2Go Integration
File: core/patterns/observer/email_notification_observer.py

This observer sends email notifications via SMTP2Go when threat feeds are updated.
"""

import logging
from typing import Dict, Any, List, Optional
from django.utils import timezone
from .observer import Observer
from .subject import Subject
from ..services.smtp2go_service import SMTP2GoService

logger = logging.getLogger(__name__)


class EmailNotificationObserver(Observer):
    """
    Observer that sends email notifications via SMTP2Go for threat feed updates.
    """
    
    def __init__(self, observer_id: str, smtp2go_service: SMTP2GoService = None):
        """
        Initialize the EmailNotificationObserver.
        
        Args:
            observer_id: Unique identifier for this observer
            smtp2go_service: SMTP2Go service instance (optional, will create default if None)
        """
        self.observer_id = observer_id
        self.smtp2go_service = smtp2go_service or SMTP2GoService()
        self._notification_count = 0
        self._last_notification = None
        
        # Email notification rules and settings
        self.notification_settings = {
            'enabled': True,
            'batch_notifications': True,  # Group multiple notifications
            'batch_interval_minutes': 5,  # Send batch every 5 minutes
            'max_batch_size': 10,  # Maximum notifications per batch
            'priority_threshold': 'medium',  # Only send for medium+ priority
            'email_templates': {
                'alert': True,
                'feed_update': True,
                'bulk_activity': True
            }
        }
        
        # Store pending notifications for batching
        self._pending_notifications = []
        self._last_batch_sent = None
        
        # Recipient management
        self.recipient_groups = {
            'security_team': [],
            'administrators': [],
            'analysts': [],
            'all_users': []
        }
    
    def update(self, subject: Subject, event_type: str = None, event_data: Dict[str, Any] = None) -> None:
        """
        Handle notifications from threat feed subjects and send emails.
        
        Args:
            subject: The threat feed subject that triggered the notification
            event_type: Type of event that occurred
            event_data: Additional data about the event
        """
        if not self.notification_settings['enabled']:
            logger.debug(f"Email notifications disabled for observer {self.observer_id}")
            return
        
        self._notification_count += 1
        self._last_notification = timezone.now()
        
        logger.info(f"EmailNotificationObserver {self.observer_id} processing event: {event_type}")
        
        try:
            # Determine if we should send notification for this event
            if self._should_send_notification(event_type, event_data):
                notification = self._create_notification(subject, event_type, event_data)
                
                if self.notification_settings['batch_notifications']:
                    self._add_to_batch(notification)
                    self._check_batch_sending()
                else:
                    self._send_immediate_notification(notification)
            
        except Exception as e:
            logger.error(f"Error processing email notification for {self.observer_id}: {str(e)}")
    
    def _should_send_notification(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Determine if a notification should be sent for this event.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            True if notification should be sent
        """
        # Check if this event type is enabled
        if not self.notification_settings['email_templates'].get(self._get_template_type(event_type), True):
            return False
        
        # Check priority threshold for alerts
        if event_type in ['indicator_added', 'ttp_added'] and 'priority' in event_data:
            priority = event_data.get('priority', 'low')
            threshold = self.notification_settings['priority_threshold']
            
            priority_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            
            if priority_levels.get(priority, 0) < priority_levels.get(threshold, 0):
                return False
        
        return True
    
    def _get_template_type(self, event_type: str) -> str:
        """
        Get email template type for event.
        
        Args:
            event_type: Type of event
            
        Returns:
            Template type
        """
        if event_type in ['high_severity_indicator', 'critical_ttp', 'system_error']:
            return 'alert'
        elif event_type in ['bulk_indicator_activity', 'bulk_ttp_activity']:
            return 'bulk_activity'
        else:
            return 'feed_update'
    
    def _create_notification(self, subject: Subject, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a notification object.
        
        Args:
            subject: The subject that triggered the notification
            event_type: Type of event
            event_data: Event data
            
        Returns:
            Notification dictionary
        """
        return {
            'notification_id': f"{self.observer_id}_{self._notification_count}_{int(timezone.now().timestamp())}",
            'subject_info': {
                'feed_id': getattr(subject, 'feed_id', 'unknown'),
                'feed_name': getattr(subject, 'feed_name', 'Unknown Feed')
            },
            'event_type': event_type,
            'event_data': event_data,
            'template_type': self._get_template_type(event_type),
            'created_at': timezone.now(),
            'priority': self._determine_priority(event_type, event_data)
        }
    
    def _determine_priority(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """
        Determine notification priority.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            Priority level
        """
        # Extract priority from event data if available
        if 'priority' in event_data:
            return event_data['priority']
        
        # Default priorities based on event type
        priority_map = {
            'high_severity_indicator': 'high',
            'critical_ttp': 'high',
            'bulk_indicator_activity': 'medium',
            'system_error': 'critical',
            'feed_published': 'low',
            'feed_updated': 'low',
            'indicator_added': 'medium',
            'ttp_added': 'medium'
        }
        
        return priority_map.get(event_type, 'low')
    
    def _add_to_batch(self, notification: Dict[str, Any]) -> None:
        """
        Add notification to pending batch.
        
        Args:
            notification: Notification to add to batch
        """
        self._pending_notifications.append(notification)
        logger.debug(f"Added notification to batch. Pending: {len(self._pending_notifications)}")
        
        # Check if batch is full
        if len(self._pending_notifications) >= self.notification_settings['max_batch_size']:
            self._send_batch_notifications()
    
    def _check_batch_sending(self) -> None:
        """Check if it's time to send batch notifications."""
        if not self._pending_notifications:
            return
        
        now = timezone.now()
        
        # Send if interval has passed or this is the first notification
        if (self._last_batch_sent is None or 
            (now - self._last_batch_sent).total_seconds() >= 
            self.notification_settings['batch_interval_minutes'] * 60):
            self._send_batch_notifications()
    
    def _send_batch_notifications(self) -> None:
        """Send all pending notifications as a batch."""
        if not self._pending_notifications:
            return
        
        logger.info(f"Sending batch of {len(self._pending_notifications)} notifications")
        
        try:
            # Group notifications by priority and type
            grouped_notifications = self._group_notifications(self._pending_notifications)
            
            # Send emails for each group
            for group_key, notifications in grouped_notifications.items():
                self._send_grouped_notifications(group_key, notifications)
            
            # Clear pending notifications
            self._pending_notifications.clear()
            self._last_batch_sent = timezone.now()
            
        except Exception as e:
            logger.error(f"Error sending batch notifications: {str(e)}")
    
    def _group_notifications(self, notifications: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group notifications by priority and type.
        
        Args:
            notifications: List of notifications to group
            
        Returns:
            Dictionary of grouped notifications
        """
        groups = {}
        
        for notification in notifications:
            priority = notification['priority']
            template_type = notification['template_type']
            group_key = f"{priority}_{template_type}"
            
            if group_key not in groups:
                groups[group_key] = []
            
            groups[group_key].append(notification)
        
        return groups
    
    def _send_grouped_notifications(self, group_key: str, notifications: List[Dict[str, Any]]) -> None:
        """
        Send a group of similar notifications.
        
        Args:
            group_key: Key identifying the group
            notifications: List of notifications in the group
        """
        priority, template_type = group_key.split('_', 1)
        
        # Get recipients based on priority and type
        recipients = self._get_recipients_for_notification(priority, template_type)
        
        if not recipients:
            logger.warning(f"No recipients found for notification group {group_key}")
            return
        
        try:
            if template_type == 'alert':
                self._send_alert_batch_email(recipients, notifications)
            elif template_type == 'bulk_activity':
                self._send_bulk_activity_email(recipients, notifications)
            else:
                self._send_feed_update_email(recipients, notifications)
                
        except Exception as e:
            logger.error(f"Error sending grouped notifications for {group_key}: {str(e)}")
    
    def _send_immediate_notification(self, notification: Dict[str, Any]) -> None:
        """
        Send a single notification immediately.
        
        Args:
            notification: Notification to send
        """
        template_type = notification['template_type']
        priority = notification['priority']
        
        recipients = self._get_recipients_for_notification(priority, template_type)
        
        if not recipients:
            logger.warning(f"No recipients found for immediate notification {notification['notification_id']}")
            return
        
        try:
            if template_type == 'alert':
                # Convert to alert format for SMTP2Go service
                alert_data = self._convert_notification_to_alert(notification)
                result = self.smtp2go_service.send_threat_alert_email(recipients, alert_data)
            else:
                # Convert to feed notification format
                feed_data = self._convert_notification_to_feed_data(notification)
                result = self.smtp2go_service.send_feed_notification_email(recipients, feed_data)
            
            if result['success']:
                logger.info(f"Email notification sent successfully: {notification['notification_id']}")
            else:
                logger.error(f"Failed to send email notification: {result['message']}")
                
        except Exception as e:
            logger.error(f"Error sending immediate notification: {str(e)}")
    
    def _send_alert_batch_email(self, recipients: List[str], notifications: List[Dict[str, Any]]) -> None:
        """
        Send a batch of alert notifications.
        
        Args:
            recipients: List of recipient email addresses
            notifications: List of alert notifications
        """
        # For multiple alerts, create a summary email
        if len(notifications) == 1:
            alert_data = self._convert_notification_to_alert(notifications[0])
            result = self.smtp2go_service.send_threat_alert_email(recipients, alert_data)
        else:
            # Create batch alert summary
            batch_alert_data = self._create_batch_alert_summary(notifications)
            result = self.smtp2go_service.send_threat_alert_email(recipients, batch_alert_data)
        
        if result['success']:
            logger.info(f"Batch alert email sent to {len(recipients)} recipients")
        else:
            logger.error(f"Failed to send batch alert email: {result['message']}")
    
    def _send_bulk_activity_email(self, recipients: List[str], notifications: List[Dict[str, Any]]) -> None:
        """
        Send bulk activity notification email.
        
        Args:
            recipients: List of recipient email addresses
            notifications: List of bulk activity notifications
        """
        # Create summary of bulk activities
        summary_data = self._create_bulk_activity_summary(notifications)
        result = self.smtp2go_service.send_feed_notification_email(recipients, summary_data)
        
        if result['success']:
            logger.info(f"Bulk activity email sent to {len(recipients)} recipients")
        else:
            logger.error(f"Failed to send bulk activity email: {result['message']}")
    
    def _send_feed_update_email(self, recipients: List[str], notifications: List[Dict[str, Any]]) -> None:
        """
        Send feed update notification email.
        
        Args:
            recipients: List of recipient email addresses
            notifications: List of feed update notifications
        """
        # Create summary of feed updates
        summary_data = self._create_feed_update_summary(notifications)
        result = self.smtp2go_service.send_feed_notification_email(recipients, summary_data)
        
        if result['success']:
            logger.info(f"Feed update email sent to {len(recipients)} recipients")
        else:
            logger.error(f"Failed to send feed update email: {result['message']}")
    
    def _convert_notification_to_alert(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert notification to alert format for SMTP2Go service.
        
        Args:
            notification: Notification to convert
            
        Returns:
            Alert data for SMTP2Go service
        """
        return {
            'alert_id': notification['notification_id'],
            'alert_type': notification['event_type'],
            'priority': notification['priority'],
            'generated_at': notification['created_at'],
            'data': {
                'feed_id': notification['subject_info']['feed_id'],
                'feed_name': notification['subject_info']['feed_name'],
                **notification['event_data']
            }
        }
    
    def _convert_notification_to_feed_data(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert notification to feed data format.
        
        Args:
            notification: Notification to convert
            
        Returns:
            Feed data for SMTP2Go service
        """
        return {
            'notification_type': notification['event_type'],
            'feed_name': notification['subject_info']['feed_name'],
            'timestamp': notification['created_at'],
            **notification['event_data']
        }
    
    def _create_batch_alert_summary(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary alert for multiple notifications.
        
        Args:
            notifications: List of notifications to summarize
            
        Returns:
            Batch alert data
        """
        highest_priority = max(notifications, key=lambda n: self._get_priority_value(n['priority']))
        
        # Count different types of alerts
        alert_counts = {}
        feed_names = set()
        
        for notification in notifications:
            event_type = notification['event_type']
            alert_counts[event_type] = alert_counts.get(event_type, 0) + 1
            feed_names.add(notification['subject_info']['feed_name'])
        
        return {
            'alert_id': f"batch_{self.observer_id}_{int(timezone.now().timestamp())}",
            'alert_type': 'multiple_alerts',
            'priority': highest_priority['priority'],
            'generated_at': timezone.now(),
            'data': {
                'alert_count': len(notifications),
                'alert_types': alert_counts,
                'affected_feeds': list(feed_names),
                'summary': f"{len(notifications)} alerts from {len(feed_names)} feed(s)"
            }
        }
    
    def _create_bulk_activity_summary(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create summary for bulk activity notifications.
        
        Args:
            notifications: List of bulk activity notifications
            
        Returns:
            Bulk activity summary data
        """
        total_indicators = sum(
            n['event_data'].get('indicator_count', 0) for n in notifications
        )
        
        feed_names = set(n['subject_info']['feed_name'] for n in notifications)
        
        return {
            'notification_type': 'bulk_activity_summary',
            'feed_name': f"{len(feed_names)} feed(s)",
            'timestamp': timezone.now(),
            'total_indicators': total_indicators,
            'activity_count': len(notifications),
            'affected_feeds': list(feed_names)
        }
    
    def _create_feed_update_summary(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create summary for feed update notifications.
        
        Args:
            notifications: List of feed update notifications
            
        Returns:
            Feed update summary data
        """
        feed_names = set(n['subject_info']['feed_name'] for n in notifications)
        
        return {
            'notification_type': 'feed_updates_summary',
            'feed_name': f"{len(feed_names)} feed(s)",
            'timestamp': timezone.now(),
            'update_count': len(notifications),
            'affected_feeds': list(feed_names)
        }
    
    def _get_priority_value(self, priority: str) -> int:
        """Get numeric value for priority comparison."""
        priority_values = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        return priority_values.get(priority, 0)
    
    def _get_recipients_for_notification(self, priority: str, template_type: str) -> List[str]:
        """
        Get recipients for a notification based on priority and type.
        
        Args:
            priority: Notification priority
            template_type: Type of notification template
            
        Returns:
            List of recipient email addresses
        """
        # Determine recipient groups based on priority and type
        if priority in ['critical', 'high']:
            # High priority notifications go to security team and administrators
            recipients = self.recipient_groups['security_team'] + self.recipient_groups['administrators']
        elif priority == 'medium':
            # Medium priority goes to security team and analysts
            recipients = self.recipient_groups['security_team'] + self.recipient_groups['analysts']
        else:
            # Low priority goes to analysts only
            recipients = self.recipient_groups['analysts']
        
        # Remove duplicates and return
        return list(set(recipients))
    
    def add_recipients(self, group: str, emails: List[str]) -> None:
        """
        Add recipients to a notification group.
        
        Args:
            group: Recipient group name
            emails: List of email addresses to add
        """
        if group in self.recipient_groups:
            self.recipient_groups[group].extend(emails)
            self.recipient_groups[group] = list(set(self.recipient_groups[group]))  # Remove duplicates
            logger.info(f"Added {len(emails)} recipients to group {group}")
        else:
            logger.warning(f"Unknown recipient group: {group}")
    
    def remove_recipients(self, group: str, emails: List[str]) -> None:
        """
        Remove recipients from a notification group.
        
        Args:
            group: Recipient group name
            emails: List of email addresses to remove
        """
        if group in self.recipient_groups:
            for email in emails:
                if email in self.recipient_groups[group]:
                    self.recipient_groups[group].remove(email)
            logger.info(f"Removed {len(emails)} recipients from group {group}")
        else:
            logger.warning(f"Unknown recipient group: {group}")
    
    def get_observer_id(self) -> str:
        """Get unique identifier for this observer."""
        return f"email_notification_observer_{self.observer_id}"
    
    def update_notification_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update notification settings.
        
        Args:
            settings: New settings to apply
        """
        self.notification_settings.update(settings)
        logger.info(f"Updated notification settings for observer {self.observer_id}")
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """
        Get notification statistics.
        
        Returns:
            Dictionary with notification statistics
        """
        return {
            'total_notifications': self._notification_count,
            'last_notification': self._last_notification,
            'pending_batch_count': len(self._pending_notifications),
            'last_batch_sent': self._last_batch_sent,
            'settings': self.notification_settings.copy(),
            'recipient_counts': {
                group: len(emails) for group, emails in self.recipient_groups.items()
            }
        }
    
    def force_send_pending(self) -> None:
        """Force send all pending batch notifications."""
        if self._pending_notifications:
            logger.info(f"Force sending {len(self._pending_notifications)} pending notifications")
            self._send_batch_notifications()
    
    def test_email_service(self) -> Dict[str, Any]:
        """
        Test the email service connection.
        
        Returns:
            Test result dictionary
        """
        return self.smtp2go_service.test_connection()
    
    def __str__(self) -> str:
        return f"EmailNotificationObserver(id={self.observer_id}, notifications={self._notification_count})"