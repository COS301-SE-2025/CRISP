from typing import Dict, Any
from .interfaces import Observer, Subject
import logging
from django.core.mail import send_mail
from django.conf import settings


class InstitutionObserver(Observer):
    """
    Observer that notifies institutions about feed updates
    """
    
    def __init__(self, institution):
        self.institution = institution
        self.logger = logging.getLogger(__name__)
    
    def update(self, subject: Subject, event_type: str, data: Dict[str, Any]):
        """Handle feed update notifications"""
        if event_type == 'published':
            self._handle_feed_published(subject, data)
        elif event_type == 'error':
            self._handle_feed_error(subject, data)
        elif event_type == 'updated':
            self._handle_feed_updated(subject, data)
    
    def _handle_feed_published(self, threat_feed, data: Dict[str, Any]):
        """Handle feed publication notification"""
        self.logger.info(
            f"Institution {self.institution.name} notified: "
            f"Feed '{threat_feed.name}' published with {data.get('object_count', 0)} objects"
        )
        
        # Send email notification if configured
        if self.institution.contact_email:
            try:
                send_mail(
                    subject=f"Threat Feed Update: {threat_feed.name}",
                    message=f"The threat feed '{threat_feed.name}' has been updated with {data.get('object_count', 0)} new threat indicators.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.institution.contact_email],
                    fail_silently=True
                )
            except Exception as e:
                self.logger.error(f"Failed to send email notification: {e}")
    
    def _handle_feed_error(self, threat_feed, data: Dict[str, Any]):
        """Handle feed error notification"""
        self.logger.error(
            f"Institution {self.institution.name} notified: "
            f"Feed '{threat_feed.name}' encountered error: {data.get('error', 'Unknown error')}"
        )
    
    def _handle_feed_updated(self, threat_feed, data: Dict[str, Any]):
        """Handle general feed update notification"""
        self.logger.info(
            f"Institution {self.institution.name} notified: "
            f"Feed '{threat_feed.name}' has been updated"
        )


class AlertSystemObserver(Observer):
    """
    Observer that triggers alerts based on feed updates
    """
    
    def __init__(self, alert_config: Dict[str, Any] = None):
        self.alert_config = alert_config or {}
        self.logger = logging.getLogger(__name__)
    
    def update(self, subject: Subject, event_type: str, data: Dict[str, Any]):
        """Handle feed update notifications and trigger alerts"""
        if event_type == 'published':
            self._check_and_trigger_alerts(subject, data)
        elif event_type == 'error':
            self._handle_system_error(subject, data)
    
    def _check_and_trigger_alerts(self, threat_feed, data: Dict[str, Any]):
        """Check for alert conditions and trigger if necessary"""
        object_count = data.get('object_count', 0)
        
        # Alert on high-volume updates
        if object_count > self.alert_config.get('high_volume_threshold', 100):
            self._trigger_high_volume_alert(threat_feed, object_count)
        
        # Alert on critical indicators (would need to check indicator content)
        self._check_critical_indicators(threat_feed, data)
    
    def _trigger_high_volume_alert(self, threat_feed, object_count: int):
        """Trigger alert for high volume of new indicators"""
        self.logger.warning(
            f"HIGH VOLUME ALERT: Feed '{threat_feed.name}' published {object_count} objects "
            f"(threshold: {self.alert_config.get('high_volume_threshold', 100)})"
        )
        
        # Could integrate with external alerting systems here
        # e.g., Slack, PagerDuty, etc.
    
    def _check_critical_indicators(self, threat_feed, data: Dict[str, Any]):
        """Check for critical indicators that require immediate attention"""
        # This would analyze the actual indicators for critical patterns
        # For now, just log the check
        self.logger.info(f"Checking feed '{threat_feed.name}' for critical indicators")
    
    def _handle_system_error(self, threat_feed, data: Dict[str, Any]):
        """Handle system errors from feed processing"""
        error_count = data.get('error_count', 0)
        
        if error_count > self.alert_config.get('error_threshold', 5):
            self.logger.critical(
                f"SYSTEM ERROR ALERT: Feed '{threat_feed.name}' has {error_count} errors "
                f"(threshold: {self.alert_config.get('error_threshold', 5)})"
            )


class MetricsObserver(Observer):
    """
    Observer that collects metrics on feed activity
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            'total_publications': 0,
            'total_objects': 0,
            'total_errors': 0,
            'feed_activity': {}
        }
    
    def update(self, subject: Subject, event_type: str, data: Dict[str, Any]):
        """Collect metrics from feed updates"""
        feed_name = subject.name
        
        if event_type == 'published':
            self._record_publication_metrics(feed_name, data)
        elif event_type == 'error':
            self._record_error_metrics(feed_name, data)
    
    def _record_publication_metrics(self, feed_name: str, data: Dict[str, Any]):
        """Record metrics for successful publications"""
        self.metrics['total_publications'] += 1
        self.metrics['total_objects'] += data.get('object_count', 0)
        
        if feed_name not in self.metrics['feed_activity']:
            self.metrics['feed_activity'][feed_name] = {
                'publications': 0,
                'objects': 0,
                'errors': 0
            }
        
        self.metrics['feed_activity'][feed_name]['publications'] += 1
        self.metrics['feed_activity'][feed_name]['objects'] += data.get('object_count', 0)
        
        self.logger.info(f"Metrics updated for feed '{feed_name}': {data.get('object_count', 0)} objects published")
    
    def _record_error_metrics(self, feed_name: str, data: Dict[str, Any]):
        """Record metrics for errors"""
        self.metrics['total_errors'] += 1
        
        if feed_name not in self.metrics['feed_activity']:
            self.metrics['feed_activity'][feed_name] = {
                'publications': 0,
                'objects': 0,
                'errors': 0
            }
        
        self.metrics['feed_activity'][feed_name]['errors'] += 1
        
        self.logger.error(f"Error metrics updated for feed '{feed_name}'")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            'total_publications': 0,
            'total_objects': 0,
            'total_errors': 0,
            'feed_activity': {}
        }