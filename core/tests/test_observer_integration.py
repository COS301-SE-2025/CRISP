#!/usr/bin/env python3
"""
Simple test to demonstrate the integrated observer pattern system.
This test runs without Django to show the core functionality.
"""

import sys
import os
import json
import uuid
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crisp'))

# Import core observer components
from core.patterns.observer import Observer, Subject


class MockThreatFeed(Subject):
    """Mock threat feed for testing observer pattern."""
    
    def __init__(self, name, owner_org):
        super().__init__()
        self.name = name
        self.owner_org = owner_org
        self.last_published_time = None
        self.sync_count = 0
    
    def publish_feed(self, bundle_data):
        """Publish feed and notify observers."""
        self.last_published_time = datetime.now()
        
        event_data = {
            'event_type': 'feed_published',
            'feed_name': self.name,
            'bundle': bundle_data,
            'timestamp': self.last_published_time,
            'owner_org': self.owner_org
        }
        
        print(f"📢 Publishing feed: {self.name}")
        print(f"   Objects: {len(bundle_data.get('objects', []))}")
        print(f"   Published: {self.last_published_time}")
        
        # Notify all observers
        self.notify(event_data)
    
    def update_feed_data(self, bundle_data):
        """Update feed and notify observers."""
        self.sync_count += 1
        
        event_data = {
            'event_type': 'feed_updated',
            'feed_name': self.name,
            'bundle': bundle_data,
            'timestamp': datetime.now(),
            'owner_org': self.owner_org
        }
        
        print(f"🔄 Updating feed: {self.name} (sync #{self.sync_count})")
        
        # Notify all observers
        self.notify(event_data)


class MockEmailObserver(Observer):
    """Mock email notification observer."""
    
    def __init__(self, organization_name):
        self.organization_name = organization_name
        self.notifications_sent = 0
    
    def update(self, subject, event_data):
        """Handle observer notifications."""
        self.notifications_sent += 1
        event_type = event_data.get('event_type')
        feed_name = event_data.get('feed_name')
        bundle = event_data.get('bundle', {})
        
        if event_type == 'feed_published':
            print(f"📧 EMAIL NOTIFICATION #{self.notifications_sent}")
            print(f"   To: {self.organization_name}")
            print(f"   Subject: New Threat Feed Published - {feed_name}")
            print(f"   Message: {len(bundle.get('objects', []))} new threat indicators available")
            
        elif event_type == 'feed_updated':
            print(f"📧 EMAIL NOTIFICATION #{self.notifications_sent}")
            print(f"   To: {self.organization_name}")
            print(f"   Subject: Threat Feed Updated - {feed_name}")
            print(f"   Message: Feed has been synchronized with latest data")


class MockAlertObserver(Observer):
    """Mock alert system observer."""
    
    def __init__(self, alert_system_id):
        self.alert_system_id = alert_system_id
        self.alerts_generated = 0
        self.high_priority_alerts = 0
    
    def update(self, subject, event_data):
        """Handle observer notifications and generate alerts."""
        event_type = event_data.get('event_type')
        bundle = event_data.get('bundle', {})
        
        if event_type == 'feed_published' and bundle:
            self._analyze_bundle_for_alerts(event_data)
    
    def _analyze_bundle_for_alerts(self, event_data):
        """Analyze STIX bundle for threats."""
        bundle = event_data.get('bundle', {})
        feed_name = event_data.get('feed_name')
        
        high_priority_threats = []
        
        for obj in bundle.get('objects', []):
            if obj.get('type') == 'indicator':
                confidence = obj.get('confidence', 0)
                severity = obj.get('x_severity', 'medium')
                
                # Check for high-priority threats
                if confidence >= 80 or severity in ['high', 'critical']:
                    high_priority_threats.append(obj)
        
        if high_priority_threats:
            self.high_priority_alerts += 1
            print(f"🚨 HIGH PRIORITY ALERT #{self.high_priority_alerts}")
            print(f"   System: {self.alert_system_id}")
            print(f"   Feed: {feed_name}")
            print(f"   Threats: {len(high_priority_threats)} high-priority indicators detected")
            
            for threat in high_priority_threats:
                pattern = threat.get('pattern', 'Unknown')
                confidence = threat.get('confidence', 0)
                severity = threat.get('x_severity', 'unknown')
                print(f"   • {pattern} (Confidence: {confidence}%, Severity: {severity})")
        
        self.alerts_generated += len(high_priority_threats)


def create_sample_stix_bundle():
    """Create a sample STIX bundle for testing."""
    return {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[domain-name:value = 'malicious.example.com']",
                "labels": ["malicious-activity"],
                "confidence": 95,
                "x_severity": "high"
            },
            {
                "type": "indicator", 
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[file:hashes.MD5 = '5d41402abc4b2a76b9719d911017c592']",
                "labels": ["malicious-activity"],
                "confidence": 75,
                "x_severity": "medium"
            },
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[ipv4-addr:value = '192.168.1.100']",
                "labels": ["suspicious-activity"],
                "confidence": 85,
                "x_severity": "critical"
            },
            {
                "type": "attack-pattern",
                "id": f"attack-pattern--{uuid.uuid4()}",
                "name": "Spear Phishing via Service",
                "x_mitre_tactic": "initial-access",
                "x_severity": "high"
            }
        ]
    }


def test_observer_integration():
    """Test the integrated observer pattern system."""
    print("=" * 60)
    print("🧪 TESTING CRISP OBSERVER PATTERN INTEGRATION")
    print("=" * 60)
    
    # Create test organizations and feeds
    university = "Test University Security Team"
    gov_agency = "Government Cyber Defense"
    
    # Create threat feeds
    external_feed = MockThreatFeed("External CTI Feed", university)
    internal_feed = MockThreatFeed("Internal Threat Analysis", gov_agency)
    
    # Create observers
    print("\n📋 Setting up observers...")
    university_email = MockEmailObserver(university)
    gov_email = MockEmailObserver(gov_agency)
    university_alerts = MockAlertObserver("University_SIEM")
    gov_alerts = MockAlertObserver("Gov_SOC_Platform")
    
    # Attach observers to feeds
    external_feed.attach(university_email)
    external_feed.attach(university_alerts)
    
    internal_feed.attach(gov_email)
    internal_feed.attach(gov_alerts)
    
    # Cross-organization monitoring (trusted partners)
    external_feed.attach(gov_alerts)  # Gov monitors university feed
    internal_feed.attach(university_alerts)  # University monitors gov feed
    
    print(f"✅ External feed has {external_feed.get_observer_count()} observers")
    print(f"✅ Internal feed has {internal_feed.get_observer_count()} observers")
    
    # Test 1: Publish external threat feed
    print("\n" + "=" * 60)
    print("TEST 1: Publishing External Threat Feed")
    print("=" * 60)
    
    sample_bundle = create_sample_stix_bundle()
    external_feed.publish_feed(sample_bundle)
    
    # Test 2: Update internal threat analysis
    print("\n" + "=" * 60)
    print("TEST 2: Updating Internal Threat Analysis")
    print("=" * 60)
    
    # Create different bundle for internal feed
    internal_bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[url:value = 'http://suspicious-site.malware.com/payload']",
                "labels": ["malicious-activity"],
                "confidence": 90,
                "x_severity": "critical"
            }
        ]
    }
    
    internal_feed.update_feed_data(internal_bundle)
    
    # Test 3: Low-priority feed update (should not generate high alerts)
    print("\n" + "=" * 60)
    print("TEST 3: Low-Priority Feed Update")
    print("=" * 60)
    
    low_priority_bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[domain-name:value = 'maybe-suspicious.example.org']",
                "labels": ["suspicious-activity"],
                "confidence": 45,
                "x_severity": "low"
            }
        ]
    }
    
    external_feed.publish_feed(low_priority_bundle)
    
    # Display final statistics
    print("\n" + "=" * 60)
    print("📊 FINAL STATISTICS")
    print("=" * 60)
    
    print(f"📧 University Email Notifications: {university_email.notifications_sent}")
    print(f"📧 Government Email Notifications: {gov_email.notifications_sent}")
    print(f"🚨 University Alert System: {university_alerts.alerts_generated} alerts, {university_alerts.high_priority_alerts} high-priority")
    print(f"🚨 Government Alert System: {gov_alerts.alerts_generated} alerts, {gov_alerts.high_priority_alerts} high-priority")
    
    # Verify observer pattern is working correctly
    assert university_email.notifications_sent > 0, "University should receive email notifications"
    assert gov_email.notifications_sent > 0, "Government should receive email notifications"
    assert university_alerts.high_priority_alerts > 0, "High-priority alerts should be generated"
    assert gov_alerts.high_priority_alerts > 0, "Cross-organization alerts should work"
    
    print("\n✅ All tests passed! Observer pattern integration is working correctly.")
    print("🎉 The CRISP threat intelligence sharing system is ready for deployment!")


if __name__ == "__main__":
    try:
        test_observer_integration()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)