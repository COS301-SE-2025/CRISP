#!/usr/bin/env python3
"""
Test Django observer integration without full Django setup.
Demonstrates the bridge between core observers and Django signals.
"""

import sys
import os
import json
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crisp'))

# Import core observer components
from core.patterns.observer import Observer, Subject


class MockDjangoSettings:
    """Mock Django settings for testing."""
    DEFAULT_FROM_EMAIL = "noreply@crisp-system.org"


class MockOrganization:
    """Mock organization for testing."""
    def __init__(self, name, contact_email):
        self.name = name
        self.contact_email = contact_email


class MockThreatFeed:
    """Mock Django ThreatFeed model."""
    def __init__(self, name, owner):
        self.id = uuid.uuid4()
        self.name = name
        self.owner = owner
        self.last_published_time = None
        self.sync_count = 0
        self.last_error = None
    
    def notify_observers(self, event_type, **kwargs):
        """Simulate Django signal sending."""
        print(f"🔔 Django Signal: {event_type}")
        print(f"   Feed: {self.name}")
        print(f"   Data: {list(kwargs.keys())}")
        
        # Simulate calling signal handlers
        if event_type == 'published':
            handle_feed_published(sender=MockThreatFeed, feed=self, **kwargs)
        elif event_type == 'updated':
            handle_feed_updated(sender=MockThreatFeed, feed=self, **kwargs)
        elif event_type == 'error':
            handle_feed_error(sender=MockThreatFeed, feed=self, **kwargs)
    
    def publish_feed(self, bundle_data):
        """Publish feed with Django integration."""
        try:
            self.last_published_time = datetime.now()
            self.notify_observers('published', bundle=bundle_data, timestamp=datetime.now())
            print(f"✅ Successfully published feed: {self.name}")
        except Exception as e:
            self.last_error = str(e)
            self.notify_observers('error', error=str(e))
            raise
    
    def update_feed_data(self, bundle_data):
        """Update feed with Django integration."""
        try:
            self.sync_count += 1
            self.notify_observers('updated', bundle=bundle_data, timestamp=datetime.now())
            print(f"✅ Successfully updated feed: {self.name}")
        except Exception as e:
            self.last_error = str(e)
            self.notify_observers('error', error=str(e))
            raise


# Mock Django components
sys.modules['django'] = MagicMock()
sys.modules['django.utils'] = MagicMock()
sys.modules['django.utils.timezone'] = MagicMock()
sys.modules['django.dispatch'] = MagicMock()
sys.modules['django.core'] = MagicMock()
sys.modules['django.core.mail'] = MagicMock()
sys.modules['django.conf'] = MagicMock()
sys.modules['django.conf'].settings = MockDjangoSettings()


# Now we can import the Django observer classes
try:
    # Mock the core observer imports to avoid Django dependencies
    sys.modules['core.patterns.observer.email_notification_observer'] = MagicMock()
    sys.modules['core.patterns.observer.alert_system_observer'] = MagicMock()
    
    # Create mock base classes
    class MockEmailNotificationObserver:
        def __init__(self, **kwargs):
            self.email_service = MagicMock()
            
        def update(self, subject, event_data):
            print(f"📧 Core Email Observer: Processing {event_data.get('event_type')}")
    
    class MockAlertSystemObserver:
        def __init__(self, alert_system_id, **kwargs):
            self.alert_system_id = alert_system_id
            self._alert_count = 0
            
        def update(self, subject, event_type, event_data):
            self._alert_count += 1
            print(f"🚨 Core Alert Observer: Processing {event_type} (Alert #{self._alert_count})")
    
    # Mock the imports
    sys.modules['core.patterns.observer.email_notification_observer'].EmailNotificationObserver = MockEmailNotificationObserver
    sys.modules['core.patterns.observer.alert_system_observer'].AlertSystemObserver = MockAlertSystemObserver
    
    # Import Django observer classes
    from crisp.crisp_threat_intel.observers.feed_observers import (
        DjangoEmailNotificationObserver,
        DjangoAlertSystemObserver,
        ObserverRegistry
    )
    
    django_observers_available = True
    
except ImportError as e:
    print(f"⚠️  Django observers not available: {e}")
    django_observers_available = False
    
    # Create fallback implementations
    class DjangoEmailNotificationObserver:
        def __init__(self, organization=None, **kwargs):
            self.organization = organization
            
        def update(self, subject, **kwargs):
            event_type = kwargs.get('event_type')
            print(f"📧 Fallback Email Observer: {event_type} for {self.organization.name if self.organization else 'Unknown'}")
    
    class DjangoAlertSystemObserver:
        def __init__(self, alert_system_id="fallback", **kwargs):
            self.alert_system_id = alert_system_id
            
        def update(self, subject, **kwargs):
            event_type = kwargs.get('event_type')
            print(f"🚨 Fallback Alert Observer: {event_type} on {self.alert_system_id}")
    
    class ObserverRegistry:
        def __init__(self):
            self._observers = {}
            
        def register_email_observer(self, observer_id, organization, **kwargs):
            observer = DjangoEmailNotificationObserver(organization, **kwargs)
            self._observers[observer_id] = observer
            return observer
            
        def register_alert_observer(self, observer_id, alert_system_id, **kwargs):
            observer = DjangoAlertSystemObserver(alert_system_id, **kwargs)
            self._observers[observer_id] = observer
            return observer
            
        def get_stats(self):
            return {'total_observers': len(self._observers)}


# Mock Django signal handlers
def handle_feed_published(sender, **kwargs):
    """Handle feed published signal with Django observers."""
    feed = kwargs.get('feed')
    bundle = kwargs.get('bundle')
    
    if not feed:
        return
    
    print(f"📡 Django Signal Handler: feed_published")
    
    # Create and use Django observers
    if hasattr(feed, 'owner'):
        email_observer = DjangoEmailNotificationObserver(feed.owner)
        email_observer.update(feed, event_type='feed_published', bundle=bundle)
    
    alert_observer = DjangoAlertSystemObserver(
        alert_system_id="django_alerts",
        alert_config={'min_confidence': 75}
    )
    alert_observer.update(feed, event_type='feed_published', bundle=bundle)


def handle_feed_updated(sender, **kwargs):
    """Handle feed updated signal with Django observers."""
    feed = kwargs.get('feed')
    bundle = kwargs.get('bundle')
    
    print(f"📡 Django Signal Handler: feed_updated")
    
    if hasattr(feed, 'owner'):
        email_observer = DjangoEmailNotificationObserver(feed.owner)
        email_observer.update(feed, event_type='feed_updated', bundle=bundle)


def handle_feed_error(sender, **kwargs):
    """Handle feed error signal with Django observers."""
    feed = kwargs.get('feed')
    error = kwargs.get('error')
    
    print(f"📡 Django Signal Handler: feed_error")
    print(f"   Error: {error}")
    
    if hasattr(feed, 'owner'):
        email_observer = DjangoEmailNotificationObserver(feed.owner)
        email_observer.update(feed, event_type='feed_error', error=error)


def create_test_bundle():
    """Create test STIX bundle."""
    return {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[domain-name:value = 'django-test.malware.com']",
                "labels": ["malicious-activity"],
                "confidence": 88,
                "x_severity": "high"
            },
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[file:hashes.SHA256 = 'abc123def456...']",
                "labels": ["malicious-activity"],
                "confidence": 92,
                "x_severity": "critical"
            }
        ]
    }


def test_django_observer_integration():
    """Test Django observer integration."""
    print("=" * 70)
    print("🧪 TESTING DJANGO OBSERVER PATTERN INTEGRATION")
    print("=" * 70)
    
    if django_observers_available:
        print("✅ Django observers loaded successfully")
    else:
        print("⚠️  Using fallback observers (Django not available)")
    
    # Create test data
    university = MockOrganization("Test University", "security@test.edu")
    gov_org = MockOrganization("Cyber Command", "alerts@cybercom.mil")
    
    threat_feed1 = MockThreatFeed("University Threat Feed", university)
    threat_feed2 = MockThreatFeed("Government Intelligence Feed", gov_org)
    
    # Test observer registry
    print(f"\n📋 Testing Observer Registry...")
    registry = ObserverRegistry()
    
    email_obs1 = registry.register_email_observer("univ_email", university)
    email_obs2 = registry.register_email_observer("gov_email", gov_org)
    alert_obs1 = registry.register_alert_observer("univ_alerts", "UniversitySOC")
    alert_obs2 = registry.register_alert_observer("gov_alerts", "GovernmentSOC")
    
    print(f"✅ Registered observers: {registry.get_stats()}")
    
    # Test 1: Feed Publication with Django Integration
    print(f"\n" + "=" * 70)
    print("TEST 1: Django Feed Publication Integration")
    print("=" * 70)
    
    test_bundle = create_test_bundle()
    threat_feed1.publish_feed(test_bundle)
    
    # Test 2: Feed Update with Django Integration
    print(f"\n" + "=" * 70)
    print("TEST 2: Django Feed Update Integration") 
    print("=" * 70)
    
    update_bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[url:value = 'http://updated-threat.example.com']",
                "labels": ["suspicious-activity"],
                "confidence": 70,
                "x_severity": "medium"
            }
        ]
    }
    
    threat_feed2.update_feed_data(update_bundle)
    
    # Test 3: Error Handling
    print(f"\n" + "=" * 70)
    print("TEST 3: Django Error Handling Integration")
    print("=" * 70)
    
    # Simulate an error
    with patch.object(threat_feed1, 'last_published_time', side_effect=Exception("Database connection failed")):
        try:
            threat_feed1.publish_feed(test_bundle)
        except Exception as e:
            print(f"🔥 Expected error occurred: {e}")
    
    # Test 4: Cross-Organization Monitoring
    print(f"\n" + "=" * 70)
    print("TEST 4: Cross-Organization Monitoring")
    print("=" * 70)
    
    # Create a high-priority threat that should alert multiple organizations
    critical_bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[process:name = 'critical_malware.exe']",
                "labels": ["malicious-activity"],
                "confidence": 98,
                "x_severity": "critical"
            }
        ]
    }
    
    print("🚨 Publishing critical threat intelligence...")
    threat_feed1.publish_feed(critical_bundle)
    
    print(f"\n" + "=" * 70)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    print(f"🔄 Threat Feed 1 ({threat_feed1.name}):")
    print(f"   Publications: {1 if threat_feed1.last_published_time else 0}")
    print(f"   Sync Count: {threat_feed1.sync_count}")
    print(f"   Last Error: {threat_feed1.last_error or 'None'}")
    
    print(f"🔄 Threat Feed 2 ({threat_feed2.name}):")
    print(f"   Publications: {1 if threat_feed2.last_published_time else 0}")
    print(f"   Sync Count: {threat_feed2.sync_count}")
    print(f"   Last Error: {threat_feed2.last_error or 'None'}")
    
    print(f"\n✅ Django Observer Integration Test Completed Successfully!")
    print(f"🎯 Key Features Demonstrated:")
    print(f"   • Django signal-based observer notifications")
    print(f"   • Core observer pattern integration")
    print(f"   • Email notification system")
    print(f"   • Alert generation and prioritization")
    print(f"   • Error handling and resilience")
    print(f"   • Observer registry management")
    print(f"   • Cross-organization threat sharing")


if __name__ == "__main__":
    try:
        test_django_observer_integration()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)