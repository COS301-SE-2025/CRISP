"""
Notification Service for CRISP System
Handles creation and management of in-app notifications and email integration
"""

from typing import List, Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.alerts.models import Notification, FeedUpdateSubscription
from core.services.email_service import UnifiedEmailService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating and managing notifications"""
    
    def __init__(self):
        self.email_service = UnifiedEmailService()
    
    def create_feed_update_notification(self, 
                                      threat_feed, 
                                      new_indicators_count: int = 0,
                                      updated_indicators_count: int = 0,
                                      send_emails: bool = True) -> List[Notification]:
        """
        Create feed update notifications for subscribed users
        
        Args:
            threat_feed: ThreatFeed object that was updated
            new_indicators_count: Number of new indicators added
            updated_indicators_count: Number of indicators updated
            send_emails: Whether to send email notifications
            
        Returns:
            List of created notifications
        """
        try:
            # Get users who should receive this notification
            recipients = self._get_feed_update_recipients(threat_feed)
            
            if not recipients:
                logger.info(f"No recipients found for feed update: {threat_feed.name}")
                return []
            
            # Create in-app notifications
            notifications = Notification.create_feed_update_notification(
                feed=threat_feed,
                users=recipients,
                new_indicators_count=new_indicators_count,
                updated_indicators_count=updated_indicators_count
            )
            
            logger.info(f"Created {len(notifications)} feed update notifications for feed: {threat_feed.name}")
            
            # Send email notifications if enabled
            if send_emails:
                email_count = self._send_feed_update_emails(
                    threat_feed=threat_feed,
                    notifications=notifications,
                    new_indicators_count=new_indicators_count,
                    updated_indicators_count=updated_indicators_count
                )
                logger.info(f"Sent {email_count} feed update email notifications")
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error creating feed update notifications: {e}")
            return []
    
    def create_threat_alert_notification(self,
                                       title: str,
                                       message: str,
                                       recipients: List[User],
                                       priority: str = 'high',
                                       metadata: Dict = None,
                                       send_emails: bool = True) -> List[Notification]:
        """Create threat alert notifications"""
        try:
            notifications = []
            
            for user in recipients:
                notification = Notification.objects.create(
                    notification_type='threat_alert',
                    title=title,
                    message=message,
                    recipient=user,
                    organization=user.organization,
                    priority=priority,
                    metadata=metadata or {}
                )
                notifications.append(notification)
            
            # Send emails if enabled
            if send_emails:
                for notification in notifications:
                    try:
                        if self._should_send_email(notification.recipient, 'threat_alert'):
                            # Use existing email service
                            result = self.email_service.send_threat_alert_email(
                                user=notification.recipient,
                                alert_title=title,
                                alert_message=message,
                                priority=priority
                            )
                            
                            if result.get('success'):
                                notification.email_sent = True
                                notification.email_sent_at = timezone.now()
                                notification.save(update_fields=['email_sent', 'email_sent_at'])
                    except Exception as e:
                        logger.warning(f"Failed to send threat alert email to {notification.recipient.email}: {e}")
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error creating threat alert notifications: {e}")
            return []
    
    def _get_feed_update_recipients(self, threat_feed) -> List[User]:
        """Get users who should receive feed update notifications"""
        recipients = []
        
        try:
            # Get users with specific feed subscriptions
            feed_subscriptions = FeedUpdateSubscription.objects.filter(
                threat_feed=threat_feed,
                is_active=True,
                in_app_notifications=True
            ).select_related('user')
            
            for subscription in feed_subscriptions:
                recipients.append(subscription.user)
            
            # Get users with organization-wide subscriptions
            if threat_feed.owner:
                org_subscriptions = FeedUpdateSubscription.objects.filter(
                    organization=threat_feed.owner,
                    threat_feed__isnull=True,  # Organization-wide subscription
                    is_active=True,
                    in_app_notifications=True
                ).select_related('user')
                
                for subscription in org_subscriptions:
                    if subscription.user not in recipients:
                        recipients.append(subscription.user)
            
            # If no specific subscriptions, notify all users in the organization with notification preferences
            if not recipients and threat_feed.owner:
                from core.user_management.models import CustomUser
                org_users = CustomUser.objects.filter(
                    organization=threat_feed.owner,
                    is_active=True
                ).select_related('profile')
                
                for user in org_users:
                    # Check user notification preferences
                    if hasattr(user, 'profile') and user.profile.email_notifications:
                        recipients.append(user)
            
            return list(set(recipients))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting feed update recipients: {e}")
            return []
    
    def _send_feed_update_emails(self, 
                               threat_feed, 
                               notifications: List[Notification],
                               new_indicators_count: int,
                               updated_indicators_count: int) -> int:
        """Send email notifications for feed updates"""
        email_count = 0
        
        for notification in notifications:
            try:
                if self._should_send_email(notification.recipient, 'feed_update'):
                    # Use existing email service
                    result = self.email_service.send_feed_update_notification(
                        recipients=[notification.recipient.email],
                        feed_name=threat_feed.name,
                        update_summary={
                            'description': threat_feed.description or '',
                            'summary': f"Feed updated with {new_indicators_count} new indicators",
                            'new_indicators': new_indicators_count,
                            'new_ttps': 0,  # TTPs are handled separately
                            'updated_items': updated_indicators_count,
                            'source': 'External' if threat_feed.is_external else 'Internal',
                            'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')
                        },
                        user=notification.recipient
                    )
                    
                    if result.get('success'):
                        notification.email_sent = True
                        notification.email_sent_at = timezone.now()
                        notification.save(update_fields=['email_sent', 'email_sent_at'])
                        email_count += 1
                    else:
                        logger.warning(f"Failed to send feed update email to {notification.recipient.email}: {result.get('message')}")
                        
            except Exception as e:
                logger.warning(f"Error sending feed update email to {notification.recipient.email}: {e}")
        
        return email_count
    
    def _should_send_email(self, user: User, notification_type: str) -> bool:
        """Check if email should be sent to user based on preferences"""
        try:
            # Check user profile preferences
            if hasattr(user, 'profile'):
                profile = user.profile
                
                # General email notifications
                if not profile.email_notifications:
                    return False
                
                # Specific notification type preferences
                if notification_type == 'threat_alert' and not profile.threat_alerts:
                    return False
                
                if notification_type == 'security_alert' and not profile.security_notifications:
                    return False
            
            # Check feed-specific subscriptions
            if notification_type == 'feed_update':
                subscriptions = FeedUpdateSubscription.objects.filter(
                    user=user,
                    is_active=True,
                    email_notifications=True
                )
                return subscriptions.exists()
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking email preferences for {user.email}: {e}")
            return True  # Default to sending if uncertain
    
    def mark_notification_read(self, notification_id: str, user: User) -> bool:
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=user
            )
            notification.mark_as_read()
            return True
            
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {user.email}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {e}")
            return False
    
    def get_user_notifications(self, 
                             user: User, 
                             unread_only: bool = False,
                             limit: int = 50) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        try:
            if unread_only:
                notifications = Notification.get_unread_for_user(user)
            else:
                notifications = Notification.get_recent_for_user(user)
            
            notifications = notifications[:limit]
            
            return [
                {
                    'id': str(notification.id),
                    'type': notification.notification_type,
                    'title': notification.title,
                    'message': notification.message,
                    'priority': notification.priority,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'read_at': notification.read_at.isoformat() if notification.read_at else None,
                    'metadata': notification.metadata,
                }
                for notification in notifications
            ]
            
        except Exception as e:
            logger.error(f"Error getting notifications for user {user.email}: {e}")
            return []
    
    def create_subscription(self, 
                          user: User,
                          threat_feed=None,
                          organization=None,
                          email_notifications: bool = True,
                          in_app_notifications: bool = True,
                          notification_frequency: str = 'immediate') -> Optional[FeedUpdateSubscription]:
        """Create a feed update subscription"""
        try:
            subscription, created = FeedUpdateSubscription.objects.get_or_create(
                user=user,
                threat_feed=threat_feed,
                organization=organization,
                defaults={
                    'email_notifications': email_notifications,
                    'in_app_notifications': in_app_notifications,
                    'notification_frequency': notification_frequency,
                    'is_active': True
                }
            )
            
            if not created:
                # Update existing subscription
                subscription.email_notifications = email_notifications
                subscription.in_app_notifications = in_app_notifications
                subscription.notification_frequency = notification_frequency
                subscription.is_active = True
                subscription.save()
            
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating subscription for user {user.email}: {e}")
            return None