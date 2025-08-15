#!/usr/bin/env python3
"""
Test script for organization creation functionality
Run this to test the organization add feature with mock data
"""

import os
import sys
import json
import requests
import time
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

class OrganizationTestClient:
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
    
    def create_organization(self, org_data):
        """Create a new organization"""
        url = f"{self.base_url}/api/v1/organizations/create_organization/"
        
        try:
            print(f"🚀 Creating organization: {org_data['name']}")
            response = self.session.post(url, json=org_data)
            
            print(f"📋 Response Status: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            
            try:
                result = response.json()
                print(f"📋 Response Body: {json.dumps(result, indent=2)}")
            except:
                print(f"📋 Response Text: {response.text}")
            
            if response.status_code == 201:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Successfully created organization: {org_data['name']}")
                    return True, result
                else:
                    print(f"❌ Organization creation failed: {result.get('message', 'Unknown error')}")
                    return False, result
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False, None
    
    def list_organizations(self):
        """List all organizations"""
        url = f"{self.base_url}/api/v1/organizations/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            result = response.json()
            print(f"📋 Found {len(result)} organizations")
            
            for org in result:
                status = "Active" if org.get('is_active') else "Inactive"
                print(f"  • {org.get('name')} ({org.get('organization_type')}) - {status}")
            
            return True, result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to list organizations: {e}")
            return False, None

def load_mock_data():
    """Load mock organization data"""
    script_dir = Path(__file__).parent
    mock_file = script_dir / "mock_organization_data.json"
    
    if not mock_file.exists():
        print(f"❌ Mock data file not found: {mock_file}")
        return None
    
    try:
        with open(mock_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded mock data with {len(data['educational_organizations']) + len(data['government_organizations']) + len(data['private_organizations'])} organizations")
        return data
    except Exception as e:
        print(f"❌ Failed to load mock data: {e}")
        return None

def main():
    print("🔧 CRISP Organization Creation Test")
    print("=" * 50)
    
    # Load mock data
    mock_data = load_mock_data()
    if not mock_data:
        return 1
    
    # Initialize client
    client = OrganizationTestClient()
    
    # Login (you'll need to update the password)
    print("\n🔐 Attempting login...")
    if not client.login():
        print("❌ Please update the login credentials in the script")
        return 1
    
    # List existing organizations
    print("\n📋 Current organizations:")
    client.list_organizations()
    
    # Test creating organizations
    print("\n🏗️ Testing organization creation...")
    
    # Test one organization from each type
    test_orgs = [
        mock_data['educational_organizations'][0],  # Cambridge University
        mock_data['government_organizations'][0],   # Department of Cybersecurity - UK
        mock_data['private_organizations'][0]       # CyberTech Solutions Ltd
    ]
    
    success_count = 0
    total_count = len(test_orgs)
    
    for org_data in test_orgs:
        print(f"\n{'='*30}")
        success, result = client.create_organization(org_data)
        if success:
            success_count += 1
        time.sleep(2)  # Wait between requests
    
    # Final report
    print(f"\n{'='*50}")
    print(f"📊 FINAL REPORT")
    print(f"✅ Successfully created: {success_count}/{total_count} organizations")
    print(f"❌ Failed: {total_count - success_count}/{total_count} organizations")
    
    # List organizations again to see changes
    print(f"\n📋 Updated organizations list:")
    client.list_organizations()
    
    if success_count == total_count:
        print(f"\n🎉 ALL TESTS PASSED! Organization creation is working correctly.")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)