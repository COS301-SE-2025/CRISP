"""
Test cases for the integrated observer pattern system.
Tests the integration between core observer pattern and Django signals.
"""

import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from crisp_threat_intel.models import Organization, ThreatFeed
from crisp_threat_intel.observers.feed_observers import (
    DjangoEmailNotificationObserver,
    DjangoAlertSystemObserver,
    observer_registry,
    feed_updated,
    feed_published,
    feed_error
)


class IntegratedObserverTestCase(TestCase):
    """Test the integrated observer pattern system."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test University",
            organization_type="university",
            contact_email="security@test.edu"
        )
        
        self.threat_feed = ThreatFeed.objects.create(
            name="Test Threat Feed",
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
    
    @patch('crisp_threat_intel.observers.feed_observers.send_mail')
    def test_email_observer_feed_published(self, mock_send_mail):
        """Test email observer handling feed published events."""
        observer = DjangoEmailNotificationObserver(self.organization)
        
        # Simulate feed published event
        observer.update(
            self.threat_feed,
            event_type='feed_published',
            bundle=self.test_bundle,
            timestamp=timezone.now()
        )
        
        # Verify email was sent
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        
        self.assertIn("Feed Published", args[0])  # Subject
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
        with patch('crisp_threat_intel.observers.feed_observers.feed_published.send') as mock_signal:
            # Test publish_feed method
            self.threat_feed.publish_feed(self.test_bundle)
            
            # Verify signal was sent
            mock_signal.assert_called_once()
            call_args = mock_signal.call_args
            
            self.assertEqual(call_args[1]['feed'], self.threat_feed)
            self.assertEqual(call_args[1]['bundle'], self.test_bundle)
    
    def test_threat_feed_update_data(self):
        """Test ThreatFeed update_feed_data method."""
        with patch('crisp_threat_intel.observers.feed_observers.feed_updated.send') as mock_signal:
            # Test update_feed_data method
            self.threat_feed.update_feed_data(self.test_bundle)
            
            # Verify signal was sent
            mock_signal.assert_called_once()
            call_args = mock_signal.call_args
            
            self.assertEqual(call_args[1]['feed'], self.threat_feed)
            self.assertEqual(call_args[1]['bundle'], self.test_bundle)
            
            # Verify feed metadata was updated
            self.threat_feed.refresh_from_db()
            self.assertIsNotNone(self.threat_feed.last_sync)
            self.assertEqual(self.threat_feed.sync_count, 1)
    
    def test_threat_feed_error_handling(self):
        """Test ThreatFeed error handling and notification."""
        with patch('crisp_threat_intel.observers.feed_observers.feed_error.send') as mock_signal:
            # Simulate an error during feed processing
            with patch.object(self.threat_feed, 'save', side_effect=Exception("Database error")):
                try:
                    self.threat_feed.publish_feed(self.test_bundle)
                except Exception:
                    pass  # Expected to raise
            
            # Verify error signal was sent
            mock_signal.assert_called_once()
            call_args = mock_signal.call_args
            
            self.assertEqual(call_args[1]['feed'], self.threat_feed)
            self.assertIn("error", call_args[1])
    
    def test_observer_registry(self):
        """Test observer registry functionality."""
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
        """Test Django signal handlers with integrated observers."""
        # Mock the observer methods to track calls
        with patch('crisp_threat_intel.observers.feed_observers.DjangoEmailNotificationObserver.update') as mock_email, \
             patch('crisp_threat_intel.observers.feed_observers.DjangoAlertSystemObserver.update') as mock_alert:
            
            # Trigger feed_published signal
            feed_published.send(
                sender=ThreatFeed,
                feed=self.threat_feed,
                bundle=self.test_bundle
            )
            
            # Verify both observers were called
            mock_email.assert_called_once()
            mock_alert.assert_called_once()
            
            # Verify call arguments
            email_call_args = mock_email.call_args
            alert_call_args = mock_alert.call_args
            
            self.assertEqual(email_call_args[0][0], self.threat_feed)  # subject
            self.assertEqual(email_call_args[1]['event_type'], 'feed_published')
            self.assertEqual(email_call_args[1]['bundle'], self.test_bundle)
            
            self.assertEqual(alert_call_args[0][0], self.threat_feed)  # subject
            self.assertEqual(alert_call_args[1]['event_type'], 'feed_published')
            self.assertEqual(alert_call_args[1]['bundle'], self.test_bundle)
    
    def test_high_priority_alert_generation(self):
        """Test high-priority alert generation."""
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
        observer_registry._observers.clear()
        observer_registry._email_observers.clear()
        observer_registry._alert_observers.clear()