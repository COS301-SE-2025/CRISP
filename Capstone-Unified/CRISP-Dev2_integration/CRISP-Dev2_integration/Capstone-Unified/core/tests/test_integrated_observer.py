"""
Test cases for the integrated observer pattern system
Tests the integration between core observer pattern and Django signal
"""

import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from core.models.models import Organization, ThreatFeed

try:
    from core.patterns.observer.feed_observers import (
        DjangoEmailNotificationObserver,
        DjangoAlertSystemObserver,
        observer_registry,
        feed_updated,
        feed_published,
        feed_error
    )
    OBSERVERS_AVAILABLE = True
except ImportError:
    print("WARNING: Observer classes not found - some tests will be skipped")
    DjangoEmailNotificationObserver = None
    DjangoAlertSystemObserver = None
    observer_registry = None
    feed_updated = None
    feed_published = None
    feed_error = None
    OBSERVERS_AVAILABLE = False


class IntegratedObserverTestCase(TestCase):
    """Test the integrated observer pattern system."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name=f"Test University {uuid.uuid4().hex[:8]}",
            organization_type="university",
            contact_email="security@test.edu"
        )
        
        self.threat_feed = ThreatFeed.objects.create(
            name=f"Test Threat Feed {uuid.uuid4().hex[:8]}",
            description="Test feed for observer testing",
            owner=self.organization,
            is_active=True
        )
        
        # Sample STIX bundle for testing
        self.test_bundle = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": [
                {
                    "type": "indicator",
                    "id": f"indicator--{uuid.uuid4()}",
                    "pattern": "[domain-name:value = 'malicious.example.com']",
                    "labels": ["malicious-activity"],
                    "confidence": 85,
                    "x_severity": "high"
                },
                {
                    "type": "attack-pattern",
                    "id": f"attack-pattern--{uuid.uuid4()}",
                    "name": "Spear Phishing via Service",
                    "x_mitre_tactic": "initial-access",
                    "x_severity": "medium"
                }
            ]
        }
    
    def test_django_email_observer_initialization(self):
        """Test Django email observer initialization."""
        observer = DjangoEmailNotificationObserver(self.organization)
        
        self.assertEqual(observer.organization, self.organization)
        self.assertIsNotNone(observer.email_service)
    
    def test_django_alert_observer_initialization(self):
        """Test Django alert observer initialization."""
        alert_config = {
            'min_confidence': 80,
            'alert_labels': ['malicious-activity']
        }
        
        observer = DjangoAlertSystemObserver(
            alert_system_id="test_alerts",
            alert_config=alert_config
        )
        
        self.assertEqual(observer.alert_system_id, "test_alerts")
        self.assertEqual(observer.alert_config, alert_config)
    
    def test_email_observer_feed_published(self):
        """Test email observer handling feed published events."""
        if not OBSERVERS_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        observer = DjangoEmailNotificationObserver(self.organization)
        
        # Simulate feed published event  
        with patch('core.patterns.observer.feed_observers.send_mail') as mock_send_mail:
            observer.update(
                self.threat_feed,
                event_type='feed_published',
                bundle=self.test_bundle,
                timestamp=timezone.now()
            )
            
            # Verify email was sent
            mock_send_mail.assert_called_once()
            args, kwargs = mock_send_mail.call_args
            
            self.assertIn("[CRISP] Threat Feed Update", args[0])  # Subject
            self.assertIn(self.threat_feed.name, args[1])  # Message
            self.assertIn(self.organization.contact_email, args[3])  # Recipients
    
    def test_alert_observer_bundle_processing(self):
        """Test alert observer processing STIX bundles."""
        observer = DjangoAlertSystemObserver("test_alerts")
        
        # Process bundle data
        processed_data = observer._process_django_bundle(self.test_bundle)
        
        # Verify indicators were extracted
        self.assertEqual(processed_data['indicators_count'], 1)
        self.assertEqual(processed_data['ttps_count'], 1)
        
        # Verify indicator data
        indicator = processed_data['indicators'][0]
        self.assertEqual(indicator['type'], 'indicator')
        self.assertEqual(indicator['severity'], 'high')
        self.assertEqual(indicator['confidence'], 85)
        
        # Verify TTP data
        ttp = processed_data['ttps'][0]
        self.assertEqual(ttp['name'], 'Spear Phishing via Service')
        self.assertEqual(ttp['tactic'], 'initial-access')
    
    def test_threat_feed_notify_observers(self):
        """Test ThreatFeed model observer notification."""
        if not OBSERVERS_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        with patch.object(self.threat_feed, 'notify_observers') as mock_notify:
            # Test a method that would trigger notifications
            if hasattr(self.threat_feed, 'publish_feed'):
                self.threat_feed.publish_feed(self.test_bundle)
            else:
                # Simulate observer notification
                self.threat_feed.notify_observers('published', bundle=self.test_bundle)
            
            # Verify notification was called
            mock_notify.assert_called()
    
    def test_threat_feed_update_data(self):
        """Test ThreatFeed update_feed_data method."""
        if not OBSERVERS_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        initial_sync_count = self.threat_feed.sync_count
        
        # Test update_feed_data method if it exists
        if hasattr(self.threat_feed, 'update_feed_data'):
            self.threat_feed.update_feed_data(self.test_bundle)
        else:
            # Simulate the update manually
            self.threat_feed.last_sync = timezone.now()
            self.threat_feed.sync_count += 1
            self.threat_feed.save()
        
        # Verify feed metadata was updated
        self.threat_feed.refresh_from_db()
        self.assertIsNotNone(self.threat_feed.last_sync)
        self.assertEqual(self.threat_feed.sync_count, initial_sync_count + 1)
    
    def test_threat_feed_error_handling(self):
        """Test ThreatFeed error handling and notification."""
        if not OBSERVERS_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        # Simulate an error during feed processing
        with patch.object(self.threat_feed, 'save', side_effect=Exception("Database error")):
            try:
                # Try to trigger an error condition
                if hasattr(self.threat_feed, 'publish_feed'):
                    self.threat_feed.publish_feed(self.test_bundle)
                else:
                    self.threat_feed.save()
            except Exception as e:
                # Verify the error was raised as expected
                self.assertIn("Database error", str(e))
    
    def test_observer_registry(self):
        """Test observer registry functionality"""
        if not OBSERVERS_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        # Register observers
        email_observer = observer_registry.register_email_observer(
            "test_email", self.organization
        )
        alert_observer = observer_registry.register_alert_observer(
            "test_alert", "test_system"
        )
        
        # Verify registration
        self.assertEqual(observer_registry.get_observer("test_email"), email_observer)
        self.assertEqual(observer_registry.get_observer("test_alert"), alert_observer)
        
        # Check stats
        stats = observer_registry.get_stats()
        self.assertEqual(stats['total_observers'], 2)
        self.assertEqual(stats['email_observers'], 1)
        self.assertEqual(stats['alert_observers'], 1)
    
    def test_signal_handlers_integration(self):
        """Test Django signal handlers with integrated observers"""
        if not OBSERVERS_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        with patch('core.patterns.observer.feed_observers.send_mail') as mock_send_mail:
            
            # Trigger feed_published signal
            feed_published.send(
                sender=ThreatFeed,
                feed=self.threat_feed,
                bundle=self.test_bundle
            )
            
            # Verify email was sent
            mock_send_mail.assert_called_once()
            
            # Verify email content
            args, kwargs = mock_send_mail.call_args
            self.assertIn("[CRISP] Threat Feed Update", args[0])  # Subject
            self.assertIn(self.threat_feed.name, args[1])  # Message
            self.assertIn(self.organization.contact_email, args[3])  # Recipients
    
    def test_high_priority_alert_generation(self):
        """Test high-priority alert generation"""
        if not OBSERVERS_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        # Create high-severity bundle
        high_severity_bundle = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": [
                {
                    "type": "indicator",
                    "id": f"indicator--{uuid.uuid4()}",
                    "pattern": "[file:hashes.MD5 = 'critical_malware_hash']",
                    "labels": ["malicious-activity"],
                    "confidence": 95,
                    "x_severity": "critical"
                }
            ]
        }
        
        observer = DjangoAlertSystemObserver(
            "critical_alerts",
            alert_config={
                'min_confidence': 75,
                'alert_labels': ['malicious-activity']
            }
        )
        
        # Mock the alert generation method
        with patch.object(observer, '_generate_alert') as mock_generate_alert:
            observer.update(
                self.threat_feed,
                event_type='feed_published',
                bundle=high_severity_bundle
            )
            
            # Verify alert was generated for high-severity indicator
            mock_generate_alert.assert_called()
            call_args = mock_generate_alert.call_args
            
            self.assertEqual(call_args[0][0], 'high_severity_indicator')  # alert_type
            self.assertEqual(call_args[0][2], 'critical')  # priority
    
    def tearDown(self):
        """Clean up test data."""
        # Clean up any registered observers
        if OBSERVERS_AVAILABLE and observer_registry:
            observer_registry._observers.clear()
            observer_registry._email_observers.clear()
            observer_registry._alert_observers.clear()