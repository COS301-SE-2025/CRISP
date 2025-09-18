"""
Feed Notification Observer
Integrates with the observer pattern to trigger notifications when feeds are updated
"""

from typing import Dict, Any
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from core.models.models import ThreatFeed, Indicator
from core.services.notification_service import NotificationService
from core.patterns.observer.feed_observers import feed_updated, feed_published
import logging

logger = logging.getLogger(__name__)


class FeedNotificationObserver:
    """Observer that creates notifications when feeds are updated"""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def update(self, subject, **kwargs):
        """Called when feed updates occur"""
        try:
            event_type = kwargs.get('event_type', 'unknown')
            feed = kwargs.get('feed')
            
            if not feed:
                logger.warning("Feed notification observer called without feed object")
                return
            
            if event_type == 'feed_updated':
                self._handle_feed_update(feed, kwargs)
            elif event_type == 'feed_published':
                self._handle_feed_published(feed, kwargs)
            else:
                logger.info(f"Unhandled feed event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error in feed notification observer: {e}")
    
    def _handle_feed_update(self, feed, event_data: Dict[str, Any]):
        """Handle feed update notifications"""
        try:
            new_indicators = event_data.get('new_indicators_count', 0)
            updated_indicators = event_data.get('updated_indicators_count', 0)
            
            # Only create notifications if there are actual changes
            if new_indicators > 0 or updated_indicators > 0:
                notifications = self.notification_service.create_feed_update_notification(
                    threat_feed=feed,
                    new_indicators_count=new_indicators,
                    updated_indicators_count=updated_indicators,
                    send_emails=True
                )
                
                logger.info(f"Created {len(notifications)} notifications for feed update: {feed.name}")
            else:
                logger.debug(f"No notifications created for feed {feed.name} - no changes detected")
                
        except Exception as e:
            logger.error(f"Error handling feed update notification for {feed.name}: {e}")
    
    def _handle_feed_published(self, feed, event_data: Dict[str, Any]):
        """Handle feed publication notifications"""
        try:
            # Create notifications for feed publication
            notifications = self.notification_service.create_feed_update_notification(
                threat_feed=feed,
                new_indicators_count=event_data.get('indicators_count', 0),
                updated_indicators_count=0,
                send_emails=True
            )
            
            logger.info(f"Created {len(notifications)} notifications for feed publication: {feed.name}")
            
        except Exception as e:
            logger.error(f"Error handling feed publication notification for {feed.name}: {e}")


# Global observer instance
feed_notification_observer = FeedNotificationObserver()


# Django signal handlers for automatic feed update detection
@receiver(post_save, sender=Indicator)
def indicator_saved_handler(sender, instance, created, **kwargs):
    """Handle indicator creation/update to trigger feed notifications"""
    try:
        if instance.threat_feed:
            # Determine if this is a new or updated indicator
            new_count = 1 if created else 0
            updated_count = 0 if created else 1
            
            # Trigger feed update notification
            feed_updated.send(
                sender=instance.threat_feed,
                feed=instance.threat_feed,
                event_type='feed_updated',
                new_indicators_count=new_count,
                updated_indicators_count=updated_count,
                indicator=instance
            )
            
            logger.debug(f"Triggered feed update notification for {instance.threat_feed.name}")
            
    except Exception as e:
        logger.error(f"Error in indicator saved handler: {e}")


@receiver(feed_updated)
def feed_updated_handler(sender, **kwargs):
    """Handle feed_updated signal"""
    try:
        feed_notification_observer.update(sender, **kwargs)
    except Exception as e:
        logger.error(f"Error in feed updated handler: {e}")


@receiver(feed_published) 
def feed_published_handler(sender, **kwargs):
    """Handle feed_published signal"""
    try:
        feed_notification_observer.update(sender, **kwargs)
    except Exception as e:
        logger.error(f"Error in feed published handler: {e}")


def trigger_manual_feed_notification(feed_id: str, 
                                   new_indicators_count: int = 0,
                                   updated_indicators_count: int = 0):
    """Manually trigger a feed update notification"""
    try:
        from core.models.models import ThreatFeed
        
        feed = ThreatFeed.objects.get(id=feed_id)
        
        notifications = feed_notification_observer.notification_service.create_feed_update_notification(
            threat_feed=feed,
            new_indicators_count=new_indicators_count,
            updated_indicators_count=updated_indicators_count,
            send_emails=True
        )
        
        logger.info(f"Manually triggered {len(notifications)} notifications for feed: {feed.name}")
        return notifications
        
    except Exception as e:
        logger.error(f"Error manually triggering feed notification: {e}")
        return []