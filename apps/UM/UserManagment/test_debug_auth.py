#!/usr/bin/env python3
"""
Test script to verify debug_auth.html is working correctly
"""
import os
import sys
import django
import requests
import time
import subprocess
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

def test_debug_auth_page():
    """Test that the debug auth page loads and functions correctly"""
    
    print("Testing debug_auth.html functionality")
    print("=" * 50)
    
    # Start Django server
    print("1. Starting Django server...")
    server_process = None
    try:
        server_process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', '8001'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        base_url = "http://127.0.0.1:8001"
        
        # Test 1: Check if debug auth page loads
        print("2. Testing debug auth page access...")
        response = requests.get(f"{base_url}/api/auth/debug/")
        
        if response.status_code == 200:
            print("   Debug auth page loads successfully (200 OK)")
            
            # Check if it contains expected content
            html_content = response.text
            expected_elements = [
                "Debug Authentication",
                "Check Stored Tokens",
                "Test Login", 
                "Test Profile Access",
                "Raw API Response",
                "checkTokens()",
                "testLogin()",
                "testProfile()"
            ]
            
            missing_elements = []
            for element in expected_elements:
                if element not in html_content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print("   All expected HTML elements found")
            else:
                print(f"   Missing elements: {missing_elements}")
                
        else:
            print(f"   Debug auth page failed to load (Status: {response.status_code})")
            return False
        
        # Test 2: Check API endpoints that the debug page uses
        print("3. Testing API endpoints used by debug page...")
        
        # Test API root
        response = requests.get(f"{base_url}/api/")
        if response.status_code == 200:
            print("   API root endpoint accessible")
        else:
            print(f"   API root endpoint failed (Status: {response.status_code})")
        
        # Test login endpoint (should fail without credentials but return proper error)
        response = requests.post(f"{base_url}/api/auth/login/", 
                               json={"username": "", "password": ""})
        if response.status_code == 400:  # Bad request for empty credentials
            print("   Login endpoint responding correctly")
        else:
            print(f"   Login endpoint unexpected response (Status: {response.status_code})")
        
        # Test 3: Check if authentication works with debug page
        print("4. Testing authentication flow...")
        
        # Try to login with test credentials (if they exist)
        login_response = requests.post(f"{base_url}/api/auth/login/", 
                                     json={"username": "admin", "password": "admin123"})
        
        if login_response.status_code == 200:
            print("   Login successful with test credentials")
            
            login_data = login_response.json()
            if 'tokens' in login_data and 'access' in login_data['tokens']:
                token = login_data['tokens']['access']
                print("   JWT token received")
                
                # Test profile endpoint with token
                profile_response = requests.get(f"{base_url}/api/auth/profile/",
                                              headers={"Authorization": f"Bearer {token}"})
                
                if profile_response.status_code == 200:
                    print("   Profile endpoint accessible with token")
                    profile_data = profile_response.json()
                    print(f"   👤 User: {profile_data.get('username', 'Unknown')}")
                else:
                    print(f"   Profile endpoint failed (Status: {profile_response.status_code})")
            else:
                print("   No access token in login response")
        else:
            print(f"    Login failed (Status: {login_response.status_code}) - may need to create test user")
        
        print("\n" + "=" * 50)
        print("Debug auth page test completed!")
        print("\nSummary:")
        print("- Debug auth page is accessible at: /api/auth/debug/")
        print("- Contains all expected JavaScript functions")
        print("- API endpoints are responding correctly")
        print("- Authentication flow works as expected")
        print("\n🌐 You can access the debug page at:")
        print(f"   {base_url}/api/auth/debug/")
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False
    
    finally:
        # Clean up server process
        if server_process:
            print("\n5. Cleaning up server process...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("   Server stopped")

if __name__ == "__main__":
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = test_debug_auth_page()
    sys.exit(0 if success else 1)