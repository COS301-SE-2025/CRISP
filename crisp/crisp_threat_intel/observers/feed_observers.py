"""
Observer Pattern Implementation for Feed Updates
Following CRISP design specification precisely.
Uses Django signals for loose coupling.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Define Django signals for Observer pattern
feed_updated = Signal()
feed_published = Signal()
feed_error = Signal()


class Observer(ABC):
    """
    Abstract base class for observers.
    Defines the interface for all observers.
    """
    
    @abstractmethod
    def update(self, subject, **kwargs):
        """
        Update method called when the subject notifies observers.
        
        Args:
            subject: The object that triggered the update
            **kwargs: Additional context data
        """
        pass


class Subject(ABC):
    """
    Abstract base class for subjects in the Observer pattern.
    In Django, this is implemented using signals.
    """
    
    @abstractmethod
    def notify_observers(self, **kwargs):
        """
        Notify all observers about an event.
        
        Args:
            **kwargs: Event data to pass to observers
        """
        pass


class InstitutionObserver(Observer):
    """
    Observer that notifies institutions about feed updates.
    Implements notifications to organization members.
    """
    
    def __init__(self, organization):
        """
        Initialize observer for a specific organization.
        
        Args:
            organization: Organization to notify
        """
        self.organization = organization
    
    def update(self, subject, **kwargs):
        """
        Handle feed update notifications for institutions.
        
        Args:
            subject: The feed that was updated
            **kwargs: Additional context (bundle, event_type, etc.)
        """
        event_type = kwargs.get('event_type', 'unknown')
        bundle = kwargs.get('bundle')
        
        logger.info(f"Institution observer notified: {self.organization.name} - {event_type}")
        
        # Send notification to organization members
        if event_type == 'feed_published':
            self._notify_feed_published(subject, bundle)
        elif event_type == 'feed_updated':
            self._notify_feed_updated(subject, bundle)
        elif event_type == 'feed_error':
            self._notify_feed_error(subject, kwargs.get('error'))
    
    def _notify_feed_published(self, feed, bundle):
        """
        Notify organization about a published feed.
        
        Args:
            feed: The published feed
            bundle: The STIX bundle that was published
        """
        try:
            # Get organization contact email
            if self.organization.contact_email:
                subject_line = f"Feed Published: {feed.name}"
                message = f"""
                A new threat intelligence feed has been published:
                
                Feed: {feed.name}
                Collection: {feed.collection.title}
                Objects: {len(bundle.get('objects', []))}
                Published: {feed.last_published_time}
                
                Visit the platform to access the latest threat intelligence.
                """
                
                send_mail(
                    subject_line,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.organization.contact_email],
                    fail_silently=True
                )
                
                logger.info(f"Email notification sent to {self.organization.name}")
        
        except Exception as e:
            logger.error(f"Failed to send email notification to {self.organization.name}: {e}")
    
    def _notify_feed_updated(self, feed, bundle):
        """
        Notify organization about an updated feed.
        
        Args:
            feed: The updated feed
            bundle: The updated STIX bundle
        """
        logger.info(f"Feed updated notification for {self.organization.name}: {feed.name}")
    
    def _notify_feed_error(self, feed, error):
        """
        Notify organization about a feed error.
        
        Args:
            feed: The feed with error
            error: Error details
        """
        logger.warning(f"Feed error notification for {self.organization.name}: {feed.name} - {error}")


class AlertSystemObserver(Observer):
    """
    Observer that triggers alerts based on feed updates.
    Implements smart alerting based on threat intelligence.
    """
    
    def __init__(self, alert_config=None):
        """
        Initialize alert system observer.
        
        Args:
            alert_config: Configuration for alert thresholds and rules
        """
        self.alert_config = alert_config or {}
    
    def update(self, subject, **kwargs):
        """
        Handle feed updates and trigger alerts if needed.
        
        Args:
            subject: The feed that was updated
            **kwargs: Additional context (bundle, event_type, etc.)
        """
        event_type = kwargs.get('event_type', 'unknown')
        bundle = kwargs.get('bundle')
        
        logger.info(f"Alert system observer notified: {subject.name} - {event_type}")
        
        if event_type == 'feed_published' and bundle:
            self._analyze_bundle_for_alerts(subject, bundle)
    
    def _analyze_bundle_for_alerts(self, feed, bundle):
        """
        Analyze STIX bundle for high-priority threats and trigger alerts.
        
        Args:
            feed: The feed that was published
            bundle: The STIX bundle to analyze
        """
        high_priority_indicators = []
        
        for obj in bundle.get('objects', []):
            if obj.get('type') == 'indicator':
                # Check for high-confidence indicators
                if obj.get('confidence', 0) >= self.alert_config.get('min_confidence', 80):
                    high_priority_indicators.append(obj)
                
                # Check for specific threat labels
                threat_labels = self.alert_config.get('alert_labels', ['malicious-activity'])
                obj_labels = obj.get('labels', [])
                if any(label in obj_labels for label in threat_labels):
                    high_priority_indicators.append(obj)
        
        if high_priority_indicators:
            self._trigger_alert(feed, high_priority_indicators)
    
    def _trigger_alert(self, feed, indicators):
        """
        Trigger alert for high-priority indicators.
        
        Args:
            feed: The feed containing the indicators
            indicators: List of high-priority indicators
        """
        logger.warning(f"HIGH PRIORITY ALERT: {len(indicators)} threats detected in feed {feed.name}")
        
        # In a real implementation, this would integrate with:
        # - SIEM systems
        # - Notification services
        # - Security orchestration platforms
        
        for indicator in indicators:
            logger.warning(f"Threat detected: {indicator.get('pattern', 'Unknown')} "
                         f"(Confidence: {indicator.get('confidence', 0)})")


# Django signal receivers for implementing Observer pattern
@receiver(feed_updated)
def handle_feed_updated(sender, **kwargs):
    """
    Handle feed updated signal.
    
    Args:
        sender: The model class that sent the signal
        **kwargs: Signal data including feed and bundle
    """
    feed = kwargs.get('feed')
    bundle = kwargs.get('bundle')
    
    if not feed:
        return
    
    # Notify institution observer
    institution_observer = InstitutionObserver(feed.collection.owner)
    institution_observer.update(feed, event_type='feed_updated', bundle=bundle)
    
    # Notify alert system observer
    alert_observer = AlertSystemObserver()
    alert_observer.update(feed, event_type='feed_updated', bundle=bundle)


@receiver(feed_published)
def handle_feed_published(sender, **kwargs):
    """
    Handle feed published signal.
    
    Args:
        sender: The model class that sent the signal
        **kwargs: Signal data including feed and bundle
    """
    feed = kwargs.get('feed')
    bundle = kwargs.get('bundle')
    
    if not feed:
        return
    
    # Notify institution observer
    institution_observer = InstitutionObserver(feed.collection.owner)
    institution_observer.update(feed, event_type='feed_published', bundle=bundle)
    
    # Notify alert system observer
    alert_observer = AlertSystemObserver({
        'min_confidence': 75,
        'alert_labels': ['malicious-activity', 'suspicious-activity']
    })
    alert_observer.update(feed, event_type='feed_published', bundle=bundle)


@receiver(feed_error)
def handle_feed_error(sender, **kwargs):
    """
    Handle feed error signal.
    
    Args:
        sender: The model class that sent the signal
        **kwargs: Signal data including feed and error
    """
    feed = kwargs.get('feed')
    error = kwargs.get('error')
    
    if not feed:
        return
    
    # Notify institution observer
    institution_observer = InstitutionObserver(feed.collection.owner)
    institution_observer.update(feed, event_type='feed_error', error=error)


# Helper function to connect signals from models
def connect_feed_signals():
    """
    Connect Django signals for the Observer pattern.
    This should be called in apps.py ready() method.
    """
    from django.db.models.signals import post_save
    from crisp_threat_intel.models import Feed
    
    def feed_post_save(sender, instance, created, **kwargs):
        """Handle feed model changes."""
        if not created:  # Only for updates, not creation
            feed_updated.send(sender=sender, feed=instance)
    
    post_save.connect(feed_post_save, sender=Feed)
    logger.info("Connected feed observer signals")