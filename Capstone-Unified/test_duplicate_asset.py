#!/usr/bin/env python3
"""
Test script to verify duplicate asset handling
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from core.models.models import AssetInventory, Organization
from core.user_management.models import CustomUser as User
from core.api.asset_api import asset_inventory_list
from django.test import RequestFactory
from rest_framework.request import Request

def test_duplicate_asset_handling():
    """Test that duplicate asset creation returns proper error"""
    print("🧪 Testing Duplicate Asset Handling...")
    
    # Get an existing asset
    existing_asset = AssetInventory.objects.first()
    if not existing_asset:
        print("❌ No assets found in database")
        return False
        
    print(f"✅ Found existing asset: {existing_asset.name} ({existing_asset.asset_value})")
    
    # Get a user from the same organization
    users = User.objects.filter(organization=existing_asset.organization)
    if not users.exists():
        print("❌ No users found in the same organization")
        return False
    
    test_user = users.first()
    print(f"✅ Using test user: {test_user.username}")
    
    # Create a fake request with duplicate asset data
    factory = RequestFactory()
    duplicate_data = {
        'name': 'Duplicate Test Asset',
        'asset_type': existing_asset.asset_type,
        'asset_value': existing_asset.asset_value,  # Same value as existing asset
        'description': 'This is a duplicate test',
        'criticality': 'medium',
        'alert_enabled': True
    }
    
    request = factory.post('/api/assets/inventory/', data=json.dumps(duplicate_data), content_type='application/json')
    request.user = test_user
    request.data = duplicate_data  # Add data attribute for DRF
    
    # Test the endpoint
    try:
        response = asset_inventory_list(request)
        print(f"✅ API response status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.data
            if 'duplicate' in data.get('message', '').lower() or 'already exists' in data.get('message', '').lower():
                print(f"✅ Proper error message returned: {data['message']}")
                return True
            else:
                print(f"❌ Unexpected error message: {data.get('message')}")
        else:
            print(f"❌ Expected 400 status, got {response.status_code}")
            print(f"Response: {response.data}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_duplicate_asset_handling()
    if success:
        print("\n🎉 Duplicate Asset Handling test passed!")
    else:
        print("\n❌ Duplicate Asset Handling test failed!")
    sys.exit(0 if success else 1)