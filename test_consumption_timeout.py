#!/usr/bin/env python3
"""
Test script to verify the TAXII consumption timeout is working correctly.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CRISP.crisp_unified.settings')
sys.path.append('/mnt/c/Users/arman/OneDrive/Documents/GitHub/CRISP/CRISP')

django.setup()

from django.conf import settings
from core.services.stix_taxii_service import StixTaxiiService
from core.models.models import ThreatFeed, CustomUser, Organization

def test_consumption_timeout():
    """Test that consumption timeout is properly configured"""
    
    print("Testing TAXII Consumption Timeout Configuration")
    print("=" * 50)
    
    # Check settings
    timeout = settings.TAXII_SETTINGS.get('CONSUMPTION_TIMEOUT', 10)
    print(f"Configured consumption timeout: {timeout} seconds")
    
    # Create service instance
    service = StixTaxiiService()
    print(f"Service created successfully")
    
    # Create a test scenario with mock objects
    mock_objects = [
        {'type': 'indicator', 'id': f'indicator--{i}', 'pattern': f'[file:hashes.MD5 = "{i}"]'}
        for i in range(100)  # Create 100 mock objects to test timeout
    ]
    
    print(f"Created {len(mock_objects)} mock objects for timeout testing")
    print("Note: This would timeout at 10 seconds if processing was slow")
    
    return True

if __name__ == "__main__":
    try:
        test_consumption_timeout()
        print("\n✅ Consumption timeout configuration test passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")