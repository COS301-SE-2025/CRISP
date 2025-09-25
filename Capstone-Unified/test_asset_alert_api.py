#!/usr/bin/env python3
"""
Quick test script to verify asset alert API functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from core.models.models import CustomAlert, Organization
from core.user_management.models import CustomUser as User
from core.api.asset_api import custom_alert_detail
from django.test import RequestFactory
from rest_framework.request import Request

def test_asset_alert_api():
    """Test that our asset alert API endpoint works correctly"""
    print("🧪 Testing Asset Alert API...")
    
    # Get a sample alert
    sample_alert = CustomAlert.objects.first()
    if not sample_alert:
        print("❌ No alerts found in database")
        return False
        
    print(f"✅ Found sample alert: {sample_alert.alert_id} ({sample_alert.id})")
    
    # Get a user from the same organization
    users = User.objects.filter(organization=sample_alert.organization)
    if not users.exists():
        print("❌ No users found in the same organization")
        return False
    
    test_user = users.first()
    print(f"✅ Using test user: {test_user.username}")
    
    # Create a fake request
    factory = RequestFactory()
    request = factory.get(f'/api/assets/alerts/{sample_alert.id}/')
    request.user = test_user
    
    # Test the endpoint
    try:
        response = custom_alert_detail(request, sample_alert.id)
        print(f"✅ API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            if data.get('success'):
                print(f"✅ Alert details retrieved successfully")
                print(f"   Title: {data['data']['title']}")
                print(f"   Status: {data['data']['status']}")
                print(f"   Severity: {data['data']['severity']}")
                return True
            else:
                print(f"❌ API returned error: {data.get('message')}")
        else:
            print(f"❌ API returned error status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_asset_alert_api()
    if success:
        print("\n🎉 Asset Alert API test passed!")
    else:
        print("\n❌ Asset Alert API test failed!")
    sys.exit(0 if success else 1)