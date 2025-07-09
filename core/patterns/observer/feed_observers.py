"""
Observer Pattern Implementation for Feed Updates
Integrates core observer pattern with Django signals.
Uses unified observer system from core patterns.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core', 'patterns', 'observer'))

from typing import Dict, Any
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
from django.conf import settings
import logging

# Import core observer components
try:
    from core.patterns.observer.email_notification_observer import EmailNotificationObserver
    from core.patterns.observer.alert_system_observer import AlertSystemObserver
except ImportError:
    # Fallback classes for development
    class EmailNotificationObserver:
        def __init__(self, **kwargs):
            pass
        def update(self, subject, **kwargs):
            pass
    
    class AlertSystemObserver:
        def __init__(self, alert_system_id, **kwargs):
            self.alert_system_id = alert_system_id
        def update(self, subject, **kwargs):
            pass

logger = logging.getLogger(__name__)

# Define Django signals for Observer pattern
feed_updated = Signal()
feed_published = Signal()
feed_error = Signal()

# Observer pattern interfaces (for Django compatibility)
class ObserverInterface:
    """Interface for all observers in the Django integration."""
    
    def update(self, subject, **kwargs):
        """
        Update method called when the subject notifies observers.
        
        Args:
            subject: The object that triggered the update
            **kwargs: Additional context data
        """
        raise NotImplementedError("Subclasses must implement update method")


class SubjectInterface:
    """Interface for subjects in the Django integration."""
    
    def notify_observers(self, **kwargs):
        """
        Notify all observers about an event.
        
        Args:
            **kwargs: Event data to pass to observers
        """
        raise NotImplementedError("Subclasses must implement notify_observers method")


class DjangoEmailNotificationObserver(EmailNotificationObserver, ObserverInterface):
    """
    Django-integrated email notification observer.
    Bridges core EmailNotificationObserver with Django signals.
    """
    
    def __init__(self, organization=None, **kwargs):
        """
        Initialize Django email notification observer.
        
        Args:
            organization: Organization to notify
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.organization = organization
    
    def update(self, subject, **kwargs):
        """
        Handle Django signal notifications and forward to core observer.
        
        Args:
            subject: The subject that triggered the notification
            **kwargs: Additional context data
        """
        try:
            # Convert Django signal data to core observer format
            event_type = kwargs.get('event_type', 'unknown')
            bundle = kwargs.get('bundle')
            
            logger.info(f"Django email observer processing: {event_type}")
            
            # Convert to core observer event format
            event_data = {
                'event_type': event_type,
                'feed_id': getattr(subject, 'id', None),
                'feed_name': getattr(subject, 'name', 'Unknown Feed'),
                'timestamp': kwargs.get('timestamp'),
                'bundle': bundle
            }
            
            # Forward to core observer
            super().update(subject, event_data)
            
            # Django-specific handling
            if event_type == 'feed_published':
                self._handle_django_feed_published(subject, bundle)
            elif event_type == 'feed_updated':
                self._handle_django_feed_updated(subject, bundle)
            elif event_type == 'feed_error':
                self._handle_django_feed_error(subject, kwargs.get('error'))
                
        except Exception as e:
            logger.error(f"Error in Django email observer: {e}")
    
    def _handle_django_feed_published(self, feed, bundle):
        """Handle Django-specific feed published notifications."""
        if self.organization and self.organization.contact_email:
            try:
                subject_line = f"[CRISP] Threat Feed Update: {getattr(feed, 'name', 'Unknown')}"
                message = f"""
A new threat intelligence feed has been published:

Feed: {getattr(feed, 'name', 'Unknown')}
Objects: {len(bundle.get('objects', [])) if bundle else 0}
Published: {getattr(feed, 'last_published_time', 'Unknown')}

Visit the platform to access the latest threat intelligence.
                """
                
                logger.info(f"Sending email to {len([self.organization.contact_email])} recipients: {subject_line}")
                
                send_mail(
                    subject_line,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.organization.contact_email],
                    fail_silently=True
                )
                
                logger.info(f"Email sent successfully to {len([self.organization.contact_email])} recipients")
                logger.info(f"Email notification sent to {self.organization.name}")
                
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
    
    def _handle_django_feed_updated(self, feed, bundle):
        """Handle Django-specific feed updated notifications."""
        if self.organization:
            logger.info(f"Feed updated notification for {self.organization.name}: {getattr(feed, 'name', 'Unknown')}")
    
    def _handle_django_feed_error(self, feed, error):
        """Handle Django-specific feed error notifications."""
        if self.organization:
            logger.warning(f"Feed error notification for {self.organization.name}: {getattr(feed, 'name', 'Unknown')} - {error}")


class DjangoAlertSystemObserver(AlertSystemObserver, ObserverInterface):
    """
    Django-integrated alert system observer.
    Bridges core AlertSystemObserver with Django signals.
    """
    
    def __init__(self, alert_system_id="django_alert_system", **kwargs):
        """
        Initialize Django alert system observer.
        
        Args:
            alert_system_id: Unique identifier for the alert system
            **kwargs: Additional configuration
        """
        # Extract alert_config before passing kwargs to parent
        self.alert_config = kwargs.pop('alert_config', {})
        super().__init__(alert_system_id, **kwargs)
    
    def update(self, subject, **kwargs):
        """
        Handle Django signal notifications and forward to core observer.
        
        Args:
            subject: The subject that triggered the notification
            **kwargs: Additional context data
        """
        try:
            # Convert Django signal data to core observer format
            event_type = kwargs.get('event_type', 'unknown')
            bundle = kwargs.get('bundle')
            
            logger.info(f"Django alert observer processing: {event_type}")
            
            # Convert to core observer event format
            event_data = {
                'feed_id': getattr(subject, 'id', None),
                'feed_name': getattr(subject, 'name', 'Unknown Feed'),
                'timestamp': kwargs.get('timestamp'),
                'bundle': bundle
            }
            
            # Add Django-specific data processing
            if event_type == 'feed_published' and bundle:
                processed_data = self._process_django_bundle(bundle)
                event_data.update(processed_data)
                
                # Check for high-severity indicators that need immediate alerts
                self._check_high_severity_alerts(processed_data)
            
            # Forward to core observer (fix method signature)
            super().update(subject, event_data)
            
        except Exception as e:
            logger.error(f"Error in Django alert observer: {e}")
    
    def _process_django_bundle(self, bundle):
        """Process Django STIX bundle for alert analysis."""
        if not bundle or not isinstance(bundle, dict):
            return {}
        
        indicators = []
        ttps = []
        
        for obj in bundle.get('objects', []):
            if obj.get('type') == 'indicator':
                indicators.append({
                    'type': obj.get('type'),
                    'value': obj.get('pattern', 'Unknown'),
                    'severity': obj.get('x_severity', 'medium'),
                    'confidence': obj.get('confidence', 50)
                })
            elif obj.get('type') == 'attack-pattern':
                ttps.append({
                    'name': obj.get('name', 'Unknown'),
                    'tactic': obj.get('x_mitre_tactic', 'unknown'),
                    'technique': obj.get('x_mitre_technique', 'unknown'),
                    'severity': obj.get('x_severity', 'medium')
                })
        
        return {
            'indicators': indicators,
            'ttps': ttps,
            'indicators_count': len(indicators),
            'ttps_count': len(ttps)
        }
    
    def _check_high_severity_alerts(self, processed_data):
        """Check for high severity indicators and generate alerts."""
        indicators = processed_data.get('indicators', [])
        
        for indicator in indicators:
            severity = indicator.get('severity', '').lower()
            confidence = indicator.get('confidence', 0)
            
            # Generate alerts for critical or high-confidence indicators
            if (severity == 'critical' or 
                (severity == 'high' and confidence >= self.alert_config.get('min_confidence', 75))):
                
                alert_type = 'high_severity_indicator'
                alert_priority = 'critical' if severity == 'critical' else 'high'
                
                self._generate_alert(alert_type, indicator, alert_priority)
    
    def _generate_alert(self, alert_type, alert_data, priority):
        """Generate an alert for high-priority events."""
        logger.info(f"AlertSystem {self.alert_system_id} critical_alerts processing event: feed_published")
        
        alert = {
            'alert_type': alert_type,
            'data': alert_data,
            'priority': priority,
            'system_id': self.alert_system_id,
            'timestamp': logger.info
        }
        
        logger.warning(f"ALERT GENERATED: {alert_type} (Priority: {priority})")
        return alert


# Django signal receivers for implementing unified Observer pattern
@receiver(feed_updated)
def handle_feed_updated(sender, **kwargs):
    """
    Handle feed updated signal with unified observer system.
    
    Args:
        sender: The model class that sent the signal
        **kwargs: Signal data including feed and bundle
    """
    feed = kwargs.get('feed')
    bundle = kwargs.get('bundle')
    
    if not feed:
        return
    
    try:
        # Get organization from feed
        organization = getattr(feed, 'collection', None)
        if organization:
            organization = getattr(organization, 'owner', None)
        else:
            # For ThreatFeed models, get owner directly
            organization = getattr(feed, 'owner', None)
        
        if organization:
            # Notify Django email observer
            email_observer = DjangoEmailNotificationObserver(organization)
            email_observer.update(feed, event_type='feed_updated', bundle=bundle)
        
        # Notify Django alert system observer
        alert_observer = DjangoAlertSystemObserver(
            alert_system_id="feed_update_alerts",
            alert_config={
                'min_confidence': 70,
                'alert_labels': ['malicious-activity', 'suspicious-activity']
            }
        )
        alert_observer.update(feed, event_type='feed_updated', bundle=bundle)
        
    except Exception as e:
        logger.error(f"Error handling feed updated signal: {e}")


@receiver(feed_published)
def handle_feed_published(sender, **kwargs):
    """
    Handle feed published signal with unified observer system.
    
    Args:
        sender: The model class that sent the signal
        **kwargs: Signal data including feed and bundle
    """
    feed = kwargs.get('feed')
    bundle = kwargs.get('bundle')
    
    if not feed:
        return
    
    try:
        # Get organization from feed (handle both Feed and ThreatFeed models)
        organization = getattr(feed, 'collection', None)
        if organization:
            organization = getattr(organization, 'owner', None)
        else:
            # For ThreatFeed models, get owner directly
            organization = getattr(feed, 'owner', None)
        
        if organization:
            # Notify Django email observer
            email_observer = DjangoEmailNotificationObserver(organization)
            email_observer.update(feed, event_type='feed_published', bundle=bundle)
        
        # Notify Django alert system observer with high-priority settings
        alert_observer = DjangoAlertSystemObserver(
            alert_system_id="feed_publication_alerts",
            alert_config={
                'min_confidence': 75,
                'alert_labels': ['malicious-activity', 'suspicious-activity', 'critical-threat']
            }
        )
        alert_observer.update(feed, event_type='feed_published', bundle=bundle)
        
    except Exception as e:
        logger.error(f"Error handling feed published signal: {e}")


@receiver(feed_error)
def handle_feed_error(sender, **kwargs):
    """
    Handle feed error signal with unified observer system.
    
    Args:
        sender: The model class that sent the signal
        **kwargs: Signal data including feed and error
    """
    feed = kwargs.get('feed')
    error = kwargs.get('error')
    
    if not feed:
        return
    
    try:
        # Get organization from feed (handle both Feed and ThreatFeed models)
        organization = getattr(feed, 'collection', None)
        if organization:
            organization = getattr(organization, 'owner', None)
        else:
            # For ThreatFeed models, get owner directly
            organization = getattr(feed, 'owner', None)
        
        if organization:
            # Notify Django email observer
            email_observer = DjangoEmailNotificationObserver(organization)
            email_observer.update(feed, event_type='feed_error', error=error)
        
        # Notify Django alert system observer for error handling
        alert_observer = DjangoAlertSystemObserver(
            alert_system_id="feed_error_alerts",
            alert_config={'error_alerts_enabled': True}
        )
        alert_observer.update(feed, event_type='feed_error', error=error)
        
    except Exception as e:
        logger.error(f"Error handling feed error signal: {e}")


# Helper function to connect signals from models
def connect_feed_signals():
    """
    Connect Django signals for the unified Observer pattern
    """
    try:
            from django.db.models.signals import post_save
            from core.models.models import Feed
            
            def feed_post_save(sender, instance, created, **kwargs):
                """Handle feed model changes."""
                if not created:  # Only for updates, not creation
                    feed_updated.send(sender=sender, feed=instance)
            
            post_save.connect(feed_post_save, sender=Feed)
            logger.info("Connected unified feed observer signals")    
    except ImportError as e:
        logger.warning(f"Could not connect feed signals - models not available: {e}")
    except Exception as e:
        logger.error(f"Error connecting feed signals: {e}")


# Observer registry for managing observers
class ObserverRegistry:
    """
    Registry for managing observers in the unified system
    """
    
    def __init__(self):
        self._observers = {}
        self._email_observers = {}
        self._alert_observers = {}
    
    def register_email_observer(self, observer_id: str, organization, **kwargs):
        """Register an email notification observer."""
        observer = DjangoEmailNotificationObserver(organization, **kwargs)
        self._email_observers[observer_id] = observer
        self._observers[observer_id] = observer
        logger.info(f"Registered email observer: {observer_id}")
        return observer
    
    def register_alert_observer(self, observer_id: str, alert_system_id: str, **kwargs):
        """Register an alert system observer."""
        observer = DjangoAlertSystemObserver(alert_system_id, **kwargs)
        self._alert_observers[observer_id] = observer
        self._observers[observer_id] = observer
        logger.info(f"Registered alert observer: {observer_id}")
        return observer
    
    def get_observer(self, observer_id: str):
        """Get an observer by ID."""
        return self._observers.get(observer_id)
    
    def notify_all(self, subject, **kwargs):
        """Notify all registered observers."""
        for observer_id, observer in self._observers.items():
            try:
                observer.update(subject, **kwargs)
            except Exception as e:
                logger.error(f"Error notifying observer {observer_id}: {e}")
    
    def get_stats(self):
        """Get registry statistics."""
        return {
            'total_observers': len(self._observers),
            'email_observers': len(self._email_observers),
            'alert_observers': len(self._alert_observers),
            'observers': list(self._observers.keys())
        }


# Global observer registry instance
observer_registry = ObserverRegistry()