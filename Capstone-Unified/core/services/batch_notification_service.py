"""
Batch Notification Service for CRISP System
Accumulates feed changes and sends summary notifications instead of individual ones
"""

import time
from typing import Dict, Any, Optional
from threading import Timer, Lock
from django.utils import timezone
from core.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


class BatchNotificationService:
    """Service for batching notifications to prevent spam"""
    
    def __init__(self, batch_delay: int = 30):
        """
        Initialize batch notification service
        
        Args:
            batch_delay: Time in seconds to wait before sending batch notification
        """
        self.batch_delay = batch_delay
        self.notification_service = NotificationService()
        self._batches = {}  # feed_id -> batch_data
        self._timers = {}   # feed_id -> timer
        self._lock = Lock()
    
    def add_feed_change(self, threat_feed, new_indicators: int = 0, updated_indicators: int = 0):
        """
        Add a feed change to the batch
        
        Args:
            threat_feed: ThreatFeed object that was updated
            new_indicators: Number of new indicators added
            updated_indicators: Number of indicators updated
        """
        with self._lock:
            feed_id = str(threat_feed.id)
            
            # Initialize or update batch data
            if feed_id not in self._batches:
                self._batches[feed_id] = {
                    'threat_feed': threat_feed,
                    'new_indicators': 0,
                    'updated_indicators': 0,
                    'first_change_time': timezone.now(),
                    'last_change_time': timezone.now()
                }
            
            # Accumulate changes
            batch = self._batches[feed_id]
            batch['new_indicators'] += new_indicators
            batch['updated_indicators'] += updated_indicators
            batch['last_change_time'] = timezone.now()
            
            # Cancel existing timer if any
            if feed_id in self._timers:
                self._timers[feed_id].cancel()
            
            # Start new timer
            timer = Timer(self.batch_delay, self._send_batch_notification, args=[feed_id])
            self._timers[feed_id] = timer
            timer.start()
            
            logger.debug(f"Added feed change to batch: {threat_feed.name} (+{new_indicators} new, +{updated_indicators} updated)")
    
    def _send_batch_notification(self, feed_id: str):
        """
        Send the batched notification for a feed
        
        Args:
            feed_id: The feed ID to send notification for
        """
        with self._lock:
            if feed_id not in self._batches:
                return
            
            batch = self._batches[feed_id]
            
            try:
                # Create summary notification
                threat_feed = batch['threat_feed']
                new_count = batch['new_indicators']
                updated_count = batch['updated_indicators']
                
                # Only send notification if there were actual changes
                if new_count > 0 or updated_count > 0:
                    duration = timezone.now() - batch['first_change_time']
                    duration_str = self._format_duration(duration.total_seconds())
                    
                    notifications = self.notification_service.create_feed_update_notification(
                        threat_feed=threat_feed,
                        new_indicators_count=new_count,
                        updated_indicators_count=updated_count,
                        send_emails=True  # Send emails for summary notifications
                    )
                    
                    logger.info(f"Sent batch notification for {threat_feed.name}: "
                              f"{new_count} new, {updated_count} updated indicators over {duration_str}")
                    
                    # Log summary for debugging
                    total_changes = new_count + updated_count
                    logger.info(f"Feed update summary - {threat_feed.name}: "
                              f"{total_changes} total changes ({new_count} new, {updated_count} updated) "
                              f"processed over {duration_str}")
                
            except Exception as e:
                logger.error(f"Error sending batch notification for feed {feed_id}: {e}")
            
            finally:
                # Clean up
                if feed_id in self._batches:
                    del self._batches[feed_id]
                if feed_id in self._timers:
                    del self._timers[feed_id]
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''}"
    
    def force_send_all_batches(self):
        """Force send all pending batch notifications immediately"""
        with self._lock:
            feed_ids = list(self._batches.keys())
            
        for feed_id in feed_ids:
            if feed_id in self._timers:
                self._timers[feed_id].cancel()
            self._send_batch_notification(feed_id)
        
        logger.info(f"Force sent {len(feed_ids)} pending batch notifications")
    
    def get_pending_batches(self) -> Dict[str, Dict[str, Any]]:
        """Get information about pending batches"""
        with self._lock:
            return {
                feed_id: {
                    'feed_name': batch['threat_feed'].name,
                    'new_indicators': batch['new_indicators'],
                    'updated_indicators': batch['updated_indicators'],
                    'first_change_time': batch['first_change_time'].isoformat(),
                    'last_change_time': batch['last_change_time'].isoformat()
                }
                for feed_id, batch in self._batches.items()
            }


# Global instance
batch_notification_service = BatchNotificationService(batch_delay=30)  # 30 second delay