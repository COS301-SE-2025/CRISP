#!/usr/bin/env python3

"""
Simple test script to validate indicator and TTP creation after field mapping fixes
"""

import os
import sys
import django
import uuid
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from core.models.models import ThreatFeed, Indicator, TTPData

def test_indicator_creation():
    """Test creating an indicator with correct field mapping"""
    print("Testing Indicator Creation...")
    
    try:
        # Create or get a threat feed
        threat_feed, created = ThreatFeed.objects.get_or_create(
            name="Test Feed",
            defaults={
                'description': 'Test threat feed for validation',
                'taxii_server_url': 'https://test.example.com',
                'is_external': True,
                'is_public': True
            }
        )
        
        # Test creating an indicator
        indicator = Indicator.objects.create(
            value="192.168.1.100",
            type="ip",  # Using correct field name
            threat_feed=threat_feed,
            confidence=85,
            first_seen=timezone.now() - timedelta(days=30),
            last_seen=timezone.now() - timedelta(days=1),
            stix_id=f"indicator--{uuid.uuid4()}"
        )
        
        print(f"✅ Successfully created indicator: {indicator}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create indicator: {e}")
        return False

def test_ttp_creation():
    """Test creating a TTP with correct field mapping"""
    print("Testing TTP Creation...")
    
    try:
        # Create or get a threat feed
        threat_feed, created = ThreatFeed.objects.get_or_create(
            name="Test Feed",
            defaults={
                'description': 'Test threat feed for validation',
                'taxii_server_url': 'https://test.example.com',
                'is_external': True,
                'is_public': True
            }
        )
        
        # Test creating a TTP
        ttp = TTPData.objects.create(
            name="Test Technique",
            description="Test technique for validation",
            mitre_technique_id="T1566.001",
            mitre_tactic="initial_access",
            threat_feed=threat_feed,
            stix_id=f"attack-pattern--{uuid.uuid4()}"
        )
        
        print(f"✅ Successfully created TTP: {ttp}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create TTP: {e}")
        return False

def main():
    """Run tests"""
    print("Running Field Mapping Validation Tests")
    print("=" * 50)
    
    indicator_success = test_indicator_creation()
    ttp_success = test_ttp_creation()
    
    print("=" * 50)
    if indicator_success and ttp_success:
        print("🎉 All tests passed! Field mapping fixes are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
    
    return indicator_success and ttp_success

if __name__ == '__main__':
    main()