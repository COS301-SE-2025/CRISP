"""
Observer Pattern Integration Example
File: core/examples/observer_pattern_demo.py

This demonstrates how to integrate the Observer pattern with CRISP threat feeds.
"""

import logging
from typing import Dict, Any, List
from django.utils import timezone
from core.patterns.observer import (
    ThreatFeedSubject, 
    InstitutionObserver, 
    AlertSystemObserver,
    EmailNotificationObserver
)
from core.services.smtp2go_service import SMTP2GoService

logger = logging.getLogger(__name__)


class CRISPObserverManager:
    """
    Manager class for CRISP Observer pattern implementation.
    Handles creation and management of observers for threat feeds.
    """
    
    def __init__(self):
        self.threat_feeds: Dict[str, ThreatFeedSubject] = {}
        self.observers: Dict[str, Any] = {}
        self.smtp2go_service = SMTP2GoService()
    
    def create_threat_feed_subject(self, feed_id: str, feed_name: str) -> ThreatFeedSubject:
        """
        Create a new threat feed subject.
        
        Args:
            feed_id: Unique identifier for the feed
            feed_name: Name of the feed
            
        Returns:
            ThreatFeedSubject instance
        """
        if feed_id in self.threat_feeds:
            logger.warning(f"ThreatFeed {feed_id} already exists")
            return self.threat_feeds[feed_id]
        
        threat_feed = ThreatFeedSubject(feed_id, feed_name)
        self.threat_feeds[feed_id] = threat_feed
        
        logger.info(f"Created ThreatFeedSubject: {feed_id}")
        return threat_feed
    
    def create_institution_observer(self, institution_id: str, institution_name: str, 
                                  notification_handler=None) -> InstitutionObserver:
        """
        Create an institution observer.
        
        Args:
            institution_id: Unique identifier for the institution
            institution_name: Name of the institution
            notification_handler: Optional custom notification handler
            
        Returns:
            InstitutionObserver instance
        """
        observer_id = f"institution_{institution_id}"
        
        if observer_id in self.observers:
            logger.warning(f"InstitutionObserver {observer_id} already exists")
            return self.observers[observer_id]
        
        observer = InstitutionObserver(institution_id, institution_name, notification_handler)
        self.observers[observer_id] = observer
        
        logger.info(f"Created InstitutionObserver: {observer_id}")
        return observer
    
    def create_alert_system_observer(self, alert_system_id: str, 
                                   alert_handler=None) -> AlertSystemObserver:
        """
        Create an alert system observer.
        
        Args:
            alert_system_id: Unique identifier for the alert system
            alert_handler: Optional custom alert handler
            
        Returns:
            AlertSystemObserver instance
        """
        observer_id = f"alert_system_{alert_system_id}"
        
        if observer_id in self.observers:
            logger.warning(f"AlertSystemObserver {observer_id} already exists")
            return self.observers[observer_id]
        
        observer = AlertSystemObserver(alert_system_id, alert_handler)
        self.observers[observer_id] = observer
        
        logger.info(f"Created AlertSystemObserver: {observer_id}")
        return observer
    
    def create_email_notification_observer(self, observer_id: str, 
                                         recipient_groups: Dict[str, List[str]] = None) -> EmailNotificationObserver:
        """
        Create an email notification observer.
        
        Args:
            observer_id: Unique identifier for the observer
            recipient_groups: Dictionary of recipient groups and their email lists
            
        Returns:
            EmailNotificationObserver instance
        """
        full_observer_id = f"email_{observer_id}"
        
        if full_observer_id in self.observers:
            logger.warning(f"EmailNotificationObserver {full_observer_id} already exists")
            return self.observers[full_observer_id]
        
        observer = EmailNotificationObserver(observer_id, self.smtp2go_service)
        
        # Add recipient groups if provided
        if recipient_groups:
            for group, emails in recipient_groups.items():
                observer.add_recipients(group, emails)
        
        self.observers[full_observer_id] = observer
        
        logger.info(f"Created EmailNotificationObserver: {full_observer_id}")
        return observer
    
    def subscribe_observer_to_feed(self, observer_id: str, feed_id: str) -> bool:
        """
        Subscribe an observer to a threat feed.
        
        Args:
            observer_id: ID of the observer to subscribe
            feed_id: ID of the feed to subscribe to
            
        Returns:
            True if subscription successful
        """
        if observer_id not in self.observers:
            logger.error(f"Observer {observer_id} not found")
            return False
        
        if feed_id not in self.threat_feeds:
            logger.error(f"ThreatFeed {feed_id} not found")
            return False
        
        observer = self.observers[observer_id]
        threat_feed = self.threat_feeds[feed_id]
        
        threat_feed.attach(observer)
        logger.info(f"Subscribed observer {observer_id} to feed {feed_id}")
        return True
    
    def unsubscribe_observer_from_feed(self, observer_id: str, feed_id: str) -> bool:
        """
        Unsubscribe an observer from a threat feed.
        
        Args:
            observer_id: ID of the observer to unsubscribe
            feed_id: ID of the feed to unsubscribe from
            
        Returns:
            True if unsubscription successful
        """
        if observer_id not in self.observers:
            logger.error(f"Observer {observer_id} not found")
            return False
        
        if feed_id not in self.threat_feeds:
            logger.error(f"ThreatFeed {feed_id} not found")
            return False
        
        observer = self.observers[observer_id]
        threat_feed = self.threat_feeds[feed_id]
        
        threat_feed.detach(observer)
        logger.info(f"Unsubscribed observer {observer_id} from feed {feed_id}")
        return True
    
    def simulate_threat_feed_activity(self, feed_id: str) -> None:
        """
        Simulate threat feed activity for demonstration.
        
        Args:
            feed_id: ID of the feed to simulate activity for
        """
        if feed_id not in self.threat_feeds:
            logger.error(f"ThreatFeed {feed_id} not found")
            return
        
        threat_feed = self.threat_feeds[feed_id]
        
        # Simulate adding indicators
        logger.info(f"Simulating threat feed activity for {feed_id}")
        
        # Add high severity indicator
        threat_feed.add_indicator({
            'id': 'indicator_001',
            'type': 'ip_address',
            'value': '192.168.100.50',
            'severity': 'high',
            'confidence': 0.95,
            'description': 'Malicious IP observed in botnet traffic'
        })
        
        # Add critical TTP
        threat_feed.add_ttp_data({
            'id': 'ttp_001',
            'name': 'Credential Dumping',
            'tactic': 'credential-access',
            'technique': 'T1003',
            'mitre_technique': 'T1003.001',
            'description': 'Adversaries may attempt to dump credentials'
        })
        
        # Simulate bulk activity
        for i in range(15):
            threat_feed.add_indicator({
                'id': f'bulk_indicator_{i}',
                'type': 'domain',
                'value': f'malicious-{i}.example.com',
                'severity': 'medium',
                'confidence': 0.7
            })
        
        # Publish the feed
        threat_feed.publish()
        
        logger.info(f"Completed simulation for feed {feed_id}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status.
        
        Returns:
            Dictionary with system status information
        """
        return {
            'threat_feeds': {
                feed_id: {
                    'name': feed.feed_name,
                    'observers': feed.get_observer_count(),
                    'last_notification': feed.get_last_notification_time()
                }
                for feed_id, feed in self.threat_feeds.items()
            },
            'observers': {
                observer_id: {
                    'type': type(observer).__name__,
                    'stats': getattr(observer, 'get_notification_stats', lambda: {})() or 
                            getattr(observer, 'get_alert_stats', lambda: {})()
                }
                for observer_id, observer in self.observers.items()
            },
            'smtp2go_status': self.smtp2go_service.test_connection()
        }


def demo_observer_pattern():
    """
    Demonstration of the Observer pattern in CRISP.
    """
    print("=== CRISP Observer Pattern Demonstration ===\n")
    
    # Create manager
    manager = CRISPObserverManager()
    
    # Create threat feed
    threat_feed = manager.create_threat_feed_subject("feed_001", "AlienVault OTX Feed")
    
    # Create observers
    institution_observer = manager.create_institution_observer(
        "inst_001", "University of Example"
    )
    
    alert_observer = manager.create_alert_system_observer("alert_001")
    
    email_observer = manager.create_email_notification_observer(
        "email_001",
        recipient_groups={
            'security_team': ['security@example.edu', 'soc@example.edu'],
            'administrators': ['admin@example.edu'],
            'analysts': ['analyst1@example.edu', 'analyst2@example.edu']
        }
    )
    
    # Subscribe observers to feed
    manager.subscribe_observer_to_feed("institution_inst_001", "feed_001")
    manager.subscribe_observer_to_feed("alert_system_alert_001", "feed_001")
    manager.subscribe_observer_to_feed("email_email_001", "feed_001")
    
    print("Created observers and subscriptions")
    print(f"Feed has {threat_feed.get_observer_count()} observers\n")
    
    # Simulate activity
    print("Simulating threat feed activity...")
    manager.simulate_threat_feed_activity("feed_001")
    
    # Show system status
    print("\nSystem Status:")
    status = manager.get_system_status()
    
    for feed_id, feed_info in status['threat_feeds'].items():
        print(f"Feed {feed_id}: {feed_info['name']} ({feed_info['observers']} observers)")
    
    for observer_id, observer_info in status['observers'].items():
        print(f"Observer {observer_id}: {observer_info['type']}")
        if 'total_notifications' in observer_info['stats']:
            print(f"  - Notifications: {observer_info['stats']['total_notifications']}")
        if 'total_alerts' in observer_info['stats']:
            print(f"  - Alerts: {observer_info['stats']['total_alerts']}")
    
    print(f"\nSMTP2Go Status: {status['smtp2go_status']['status']}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demonstration
    demo_observer_pattern()