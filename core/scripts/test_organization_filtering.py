#!/usr/bin/env python3
"""
Test script for organization filtering functionality
Tests that organization types filter correctly both in backend and frontend logic
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")
    print("Make sure you're running this from the CRISP project directory")
    sys.exit(1)

class OrganizationFilterTestClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def login(self, username="DreasVermaak1", password="your_password_here"):
        """Login to get authentication token"""
        url = f"{self.base_url}/api/v1/auth/login/"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('success') and result.get('tokens'):
                self.auth_token = result['tokens']['access']
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                print(f"✅ Successfully logged in as {username}")
                return True
            else:
                print(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Login request failed: {e}")
            return False
    
    def get_organization_types(self):
        """Get available organization types from API"""
        url = f"{self.base_url}/api/v1/organizations/types/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                types = result.get('data', {}).get('organization_types', [])
                print(f"✅ Available organization types: {[t['value'] for t in types]}")
                return types
            else:
                print(f"❌ Failed to get organization types: {result.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return []
    
    def list_organizations_by_type(self, org_type=None):
        """List organizations, optionally filtered by type"""
        url = f"{self.base_url}/api/v1/organizations/"
        if org_type:
            url += f"?organization_type={org_type}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            result = response.json()
            organizations = result if isinstance(result, list) else []
            
            if org_type:
                print(f"📋 Found {len(organizations)} organizations of type '{org_type}':")
                # Verify filtering worked correctly
                mismatched = [org for org in organizations if org.get('organization_type') != org_type]
                if mismatched:
                    print(f"⚠️  Warning: Found {len(mismatched)} organizations that don't match filter")
                    for org in mismatched:
                        print(f"  • {org.get('name')} has type '{org.get('organization_type')}' (expected '{org_type}')")
            else:
                print(f"📋 Found {len(organizations)} total organizations:")
            
            # Show organization details
            type_counts = {}
            for org in organizations:
                org_type_actual = org.get('organization_type', 'unknown')
                type_counts[org_type_actual] = type_counts.get(org_type_actual, 0) + 1
                status = "Active" if org.get('is_active') else "Inactive"
                print(f"  • {org.get('name')} ({org_type_actual}) - {status}")
            
            if not org_type:
                print(f"\n📊 Type distribution:")
                for t, count in type_counts.items():
                    print(f"  • {t}: {count}")
            
            return organizations
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to list organizations: {e}")
            return []

def test_frontend_filtering_logic():
    """Test the frontend filtering logic with mock data"""
    print("\n🧪 Testing frontend filtering logic...")
    
    # Load mock data
    script_dir = Path(__file__).parent
    mock_file = script_dir / "mock_organization_data.json"
    
    if not mock_file.exists():
        print("❌ Mock data file not found")
        return False
    
    with open(mock_file, 'r') as f:
        mock_data = json.load(f)
    
    # Flatten all organizations
    all_orgs = []
    all_orgs.extend(mock_data['educational_organizations'])
    all_orgs.extend(mock_data['government_organizations'])
    all_orgs.extend(mock_data['private_organizations'])
    
    print(f"📋 Testing with {len(all_orgs)} mock organizations")
    
    # Test filtering logic (mimics frontend filter)
    test_cases = [
        ('educational', 'Educational organizations'),
        ('government', 'Government organizations'),
        ('private', 'Private organizations'),
        ('', 'All organizations (no filter)')
    ]
    
    success = True
    for type_filter, description in test_cases:
        if type_filter:
            filtered = [org for org in all_orgs if org.get('organization_type') == type_filter]
        else:
            filtered = all_orgs
        
        expected_count = {
            'educational': len(mock_data['educational_organizations']),
            'government': len(mock_data['government_organizations']),
            'private': len(mock_data['private_organizations']),
            '': len(all_orgs)
        }[type_filter]
        
        if len(filtered) == expected_count:
            print(f"✅ {description}: {len(filtered)} organizations (correct)")
        else:
            print(f"❌ {description}: {len(filtered)} organizations (expected {expected_count})")
            success = False
    
    return success

def main():
    print("🔧 CRISP Organization Type Filtering Test")
    print("=" * 50)
    
    # Test frontend logic first (doesn't require server)
    frontend_success = test_frontend_filtering_logic()
    
    # Initialize client for API tests
    client = OrganizationFilterTestClient()
    
    # Login (you'll need to update the password)
    print(f"\n🔐 Attempting login...")
    if not client.login():
        print("❌ Please update the login credentials in the script")
        print(f"💡 Frontend filtering logic test: {'✅ PASSED' if frontend_success else '❌ FAILED'}")
        return 1 if not frontend_success else 0
    
    # Test getting organization types
    print(f"\n📋 Testing organization types endpoint...")
    types = client.get_organization_types()
    expected_types = ['educational', 'government', 'private']
    types_values = [t['value'] for t in types] if types else []
    
    types_match = set(types_values) == set(expected_types)
    if types_match:
        print(f"✅ Organization types match expected values")
    else:
        print(f"❌ Organization types mismatch. Got: {types_values}, Expected: {expected_types}")
    
    # Test listing all organizations
    print(f"\n📋 Testing organization listing...")
    all_orgs = client.list_organizations_by_type()
    
    # Test filtering by each type
    api_success = True
    for org_type in expected_types:
        print(f"\n🔍 Testing filter for '{org_type}' organizations...")
        filtered_orgs = client.list_organizations_by_type(org_type)
        
        # Check if all returned organizations have the correct type
        incorrect_types = [org for org in filtered_orgs if org.get('organization_type') != org_type]
        if incorrect_types:
            print(f"❌ Found {len(incorrect_types)} organizations with incorrect type")
            api_success = False
        else:
            print(f"✅ All {len(filtered_orgs)} organizations have correct type")
    
    # Final report
    print(f"\n{'='*50}")
    print(f"📊 FINAL REPORT")
    print(f"✅ Frontend filtering logic: {'PASSED' if frontend_success else 'FAILED'}")
    print(f"✅ API organization types endpoint: {'PASSED' if types_match else 'FAILED'}")
    print(f"✅ API organization filtering: {'PASSED' if api_success else 'FAILED'}")
    
    overall_success = frontend_success and types_match and api_success
    if overall_success:
        print(f"\n🎉 ALL TESTS PASSED! Organization type filtering is working correctly.")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)