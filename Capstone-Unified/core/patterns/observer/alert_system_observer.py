import logging
from typing import Dict, Any, List, Optional
from django.utils import timezone
from . import Observer, Subject

logger = logging.getLogger(__name__)


class AlertSystemObserver(Observer):
    """
    Observer that triggers alerts based on threat feed updates.
    Monitors threat feeds and generates alerts for high-priority threats.
    """
    
    def __init__(self, alert_system_id: str, alert_handler=None):
        """
        Initialize the AlertSystemObserver.
        
        Args:
            alert_system_id: Unique identifier for the alert system
            alert_handler: Optional custom alert handler function
        """
        self.alert_system_id = alert_system_id
        self.alert_handler = alert_handler
        self._alert_count = 0
        self._last_alert = None
        
        # Alert thresholds and rules
        self.alert_rules = {
            'high_severity_indicators': {
                'enabled': True,
                'severity_threshold': 'high',
                'confidence_threshold': 0.8
            },
            'critical_ttps': {
                'enabled': True,
                'critical_tactics': ['initial-access', 'execution', 'persistence']
            },
            'bulk_indicator_additions': {
                'enabled': True,
                'threshold': 10,  # Alert if more than 10 indicators added at once
                'time_window': 300  # Within 5 minutes
            },
            'new_feed_publications': {
                'enabled': True,
                'trusted_sources_only': True
            }
        }
        
        # Track recent activities for bulk detection
        self._recent_activities = []
    
    def update(self, subject: Subject, event_type: str = None, event_data: Dict[str, Any] = None) -> None:
        """
        Handle notifications from threat feed subjects and generate alerts.
        
        Args:
            subject: The threat feed subject that triggered the notification
            event_type: Type of event that occurred
            event_data: Additional data about the event
        """
        logger.info(f"AlertSystem {self.alert_system_id} processing event: {event_type}")
        
        try:
            # Record activity for bulk detection
            self._record_activity(event_type, event_data)
            
            # Process different event types
            if event_type == 'indicator_added':
                self._handle_indicator_alert(subject, event_data)
            elif event_type == 'ttp_added':
                self._handle_ttp_alert(subject, event_data)
            elif event_type == 'feed_published':
                self._handle_feed_publication_alert(subject, event_data)
            elif event_type == 'feed_updated':
                self._handle_feed_update_alert(subject, event_data)
            
            # Check for bulk activities
            self._check_bulk_activities()
            
        except Exception as e:
            logger.error(f"Error processing alert for {self.alert_system_id}: {str(e)}")
            self._generate_alert('system_error', {
                'error': str(e),
                'event_type': event_type,
                'feed_id': event_data.get('feed_id') if event_data else None
            }, 'high')
    
    def _handle_indicator_alert(self, subject: Subject, event_data: Dict[str, Any]) -> None:
        """
        Handle alerts for new indicators.
        
        Args:
            subject: The threat feed subject
            event_data: Event data containing indicator information
        """
        if not self.alert_rules['high_severity_indicators']['enabled']:
            return
        
        indicator = event_data.get('indicator', {})
        severity = indicator.get('severity', '').lower()
        confidence = indicator.get('confidence', 0)
        
        # Check if indicator meets alert criteria
        severity_threshold = self.alert_rules['high_severity_indicators']['severity_threshold']
        confidence_threshold = self.alert_rules['high_severity_indicators']['confidence_threshold']
        
        if (severity == 'critical' or 
            (severity == severity_threshold and confidence >= confidence_threshold)):
            
            alert_data = {
                'feed_id': event_data.get('feed_id'),
                'feed_name': event_data.get('feed_name'),
                'indicator_type': indicator.get('type'),
                'indicator_value': indicator.get('value'),
                'severity': severity,
                'confidence': confidence,
                'description': indicator.get('description', ''),
                'timestamp': event_data.get('timestamp')
            }
            
            alert_priority = 'critical' if severity == 'critical' else 'high'
            self._generate_alert('high_severity_indicator', alert_data, alert_priority)
    
    def _handle_ttp_alert(self, subject: Subject, event_data: Dict[str, Any]) -> None:
        """
        Handle alerts for new TTPs.
        
        Args:
            subject: The threat feed subject
            event_data: Event data containing TTP information
        """
        if not self.alert_rules['critical_ttps']['enabled']:
            return
        
        ttp = event_data.get('ttp', {})
        tactic = ttp.get('tactic', '').lower()
        
        # Check if TTP involves critical tactics
        critical_tactics = self.alert_rules['critical_ttps']['critical_tactics']
        
        if tactic in critical_tactics:
            alert_data = {
                'feed_id': event_data.get('feed_id'),
                'feed_name': event_data.get('feed_name'),
                'ttp_name': ttp.get('name'),
                'tactic': tactic,
                'technique': ttp.get('technique'),
                'mitre_technique': ttp.get('mitre_technique'),
                'description': ttp.get('description', ''),
                'timestamp': event_data.get('timestamp')
            }
            
            self._generate_alert('critical_ttp', alert_data, 'high')
    
    def _handle_feed_publication_alert(self, subject: Subject, event_data: Dict[str, Any]) -> None:
        """
        Handle alerts for feed publications.
        
        Args:
            subject: The threat feed subject
            event_data: Event data containing publication information
        """
        if not self.alert_rules['new_feed_publications']['enabled']:
            return
        
       
        alert_data = {
            'feed_id': event_data.get('feed_id'),
            'feed_name': event_data.get('feed_name'),
            'published_at': event_data.get('published_at'),
            'timestamp': event_data.get('timestamp')
        }
        
        self._generate_alert('feed_published', alert_data, 'info')
    
    def _handle_feed_update_alert(self, subject: Subject, event_data: Dict[str, Any]) -> None:
        """
        Handle alerts for feed updates.
        
        Args:
            subject: The threat feed subject
            event_data: Event data containing update information
        """
        updates = event_data.get('updates', {})
        
        # Generate alert only for significant updates
        if len(updates) > 0:
            alert_data = {
                'feed_id': event_data.get('feed_id'),
                'feed_name': event_data.get('feed_name'),
                'updates': updates,
                'timestamp': event_data.get('timestamp')
            }
            
            self._generate_alert('feed_updated', alert_data, 'low')
    
    def _record_activity(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Record activity for bulk detection.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        now = timezone.now()
        
        # Clean old activities (outside time window)
        time_window = self.alert_rules['bulk_indicator_additions']['time_window']
        cutoff_time = now.timestamp() - time_window
        
        self._recent_activities = [
            activity for activity in self._recent_activities
            if activity['timestamp'] > cutoff_time
        ]
        
        # Add new activity
        self._recent_activities.append({
            'event_type': event_type,
            'feed_id': event_data.get('feed_id') if event_data else None,
            'timestamp': now.timestamp()
        })
    
    def _check_bulk_activities(self) -> None:
        """Check for bulk activities that should trigger alerts."""
        if not self.alert_rules['bulk_indicator_additions']['enabled']:
            return
        
        threshold = self.alert_rules['bulk_indicator_additions']['threshold']
        
        # Count recent indicator additions
        indicator_additions = [
            activity for activity in self._recent_activities
            if activity['event_type'] == 'indicator_added'
        ]
        
        if len(indicator_additions) >= threshold:
            # Group by feed
            feed_counts = {}
            for activity in indicator_additions:
                feed_id = activity['feed_id']
                if feed_id:
                    feed_counts[feed_id] = feed_counts.get(feed_id, 0) + 1
            
            # Generate alerts for feeds with high activity
            for feed_id, count in feed_counts.items():
                if count >= threshold:
                    alert_data = {
                        'feed_id': feed_id,
                        'indicator_count': count,
                        'time_window_minutes': self.alert_rules['bulk_indicator_additions']['time_window'] // 60,
                        'timestamp': timezone.now()
                    }
                    
                    self._generate_alert('bulk_indicator_activity', alert_data, 'medium')
    
    def _generate_alert(self, alert_type: str, alert_data: Dict[str, Any], priority: str) -> None:
        """
        Generate an alert.
        
        Args:
            alert_type: Type of alert
            alert_data: Alert data
            priority: Alert priority (critical, high, medium, low, info)
        """
        self._alert_count += 1
        self._last_alert = timezone.now()
        
        alert = {
            'alert_id': f"{self.alert_system_id}_{self._alert_count}_{int(self._last_alert.timestamp())}",
            'alert_system_id': self.alert_system_id,
            'alert_type': alert_type,
            'priority': priority,
            'data': alert_data,
            'generated_at': self._last_alert,
            'status': 'new'
        }
        
        logger.warning(f"ALERT GENERATED: {alert_type} (Priority: {priority}) - {alert['alert_id']}")
        
        try:
            if self.alert_handler:
                # Use custom alert handler
                self.alert_handler(alert)
            else:
                # Default alert handling
                self._default_alert_handling(alert)
        except Exception as e:
            logger.error(f"Error handling alert {alert['alert_id']}: {str(e)}")
    
    def _default_alert_handling(self, alert: Dict[str, Any]) -> None:
        """
        Default alert handling implementation.
        
        Args:
            alert: Alert data
        """
        # Log the alert
        logger.info(f"Processing alert {alert['alert_id']} with priority {alert['priority']}")
    
    def get_observer_id(self) -> str:
        """Get unique identifier for this observer."""
        return f"alert_system_observer_{self.alert_system_id}"
    
    def get_alert_system(self) -> Dict[str, Any]:
        """
        Get alert system information.
        
        Returns:
            Dictionary with alert system details
        """
        return {
            'id': self.alert_system_id,
            'total_alerts': self._alert_count,
            'last_alert': self._last_alert,
            'rules': self.alert_rules.copy()
        }
    
    def update_alert_rules(self, new_rules: Dict[str, Any]) -> None:
        """
        Update alert rules.
        
        Args:
            new_rules: New alert rules configuration
        """
        self.alert_rules.update(new_rules)
        logger.info(f"Updated alert rules for alert system {self.alert_system_id}")
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """
        Get alert statistics.
        
        Returns:
            Dictionary with alert statistics
        """
        return {
            'total_alerts': self._alert_count,
            'last_alert': self._last_alert,
            'recent_activities': len(self._recent_activities),
            'enabled_rules': {
                rule_name: rule_config['enabled']
                for rule_name, rule_config in self.alert_rules.items()
                if isinstance(rule_config, dict) and 'enabled' in rule_config
            }
        }
    
    def __str__(self) -> str:
        return f"AlertSystemObserver(id={self.alert_system_id}, alerts={self._alert_count})"