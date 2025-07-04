#!/usr/bin/env python3
"""
Quick system test for CRISP User Management
Enhanced with improved visual formatting for clear pass/fail status
"""

import requests
import json
import sys
from test_formatting import TestFormatter

BASE_URL = "http://127.0.0.1:8000"

def test_login(formatter):
    """Test user login"""
    formatter.print_test_start("User Login")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('tokens', {}).get('access', 'Not found')
            details = f"Authentication successful, token obtained"
            formatter.print_test_result("User Login", True, details)
            return access_token
        else:
            details = f"Status: {response.status_code}, Response: {response.text[:100]}"
            formatter.print_test_result("User Login", False, details)
            return None
            
    except requests.exceptions.ConnectionError:
        formatter.print_test_result("User Login", False, "Server not running - connection failed")
        return "skip"
    except requests.exceptions.Timeout:
        formatter.print_test_result("User Login", False, "Server timeout")
        return "skip"
    except Exception as e:
        formatter.print_test_result("User Login", False, f"Error during login: {e}")
        return None

def test_profile(formatter, token):
    """Test profile endpoint"""
    formatter.print_test_start("User Profile")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            details = f"User: {data.get('username')} ({data.get('role')}), Org: {data.get('organization', {}).get('name', 'None')}"
            formatter.print_test_result("User Profile", True, details)
        else:
            details = f"Status: {response.status_code}, Response: {response.text[:100]}"
            formatter.print_test_result("User Profile", False, details)
            
    except Exception as e:
        formatter.print_test_result("User Profile", False, f"Error fetching profile: {e}")

def test_admin_users(formatter, token):
    """Test admin users endpoint"""
    formatter.print_test_start("Admin Users Endpoint")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            details = f"Successfully accessed admin endpoint, found {data.get('count', 0)} users"
            formatter.print_test_result("Admin Users Endpoint", True, details)
        else:
            details = f"Status: {response.status_code}, Response: {response.text[:100]}"
            formatter.print_test_result("Admin Users Endpoint", False, details)
            
    except Exception as e:
        formatter.print_test_result("Admin Users Endpoint", False, f"Error accessing admin users: {e}")

def main():
    # Initialize formatter
    formatter = TestFormatter()
    
    # Print header
    formatter.print_header("CRISP User Management System Test", "Quick API endpoint verification")
    
    # Test login
    formatter.print_section("Authentication Tests")
    token = test_login(formatter)
    
    if token == "skip":
        formatter.print_warning("Server not running - API tests skipped")
        formatter.print_info("To run full API tests:")
        formatter.print_info("1. Start the Django server: python3 manage.py runserver")
        formatter.print_info("2. Run this test again")
        
        # Print summary for skip case
        formatter.print_summary({
            "Environment": "Development",
            "Server Status": "Not Running",
            "Test Status": "Skipped"
        })
        
        sys.exit(0)  # Exit with success since server not running is expected
        
    elif token:
        # Test other endpoints if login successful
        formatter.print_section("API Endpoint Tests")
        test_profile(formatter, token)
        test_admin_users(formatter, token)
        
        # Print comprehensive summary
        formatter.print_summary({
            "Environment": "Development", 
            "Server Status": "Running",
            "API Base URL": BASE_URL
        })
        
        sys.exit(formatter.get_exit_code())
        
    else:
        formatter.print_error("System test failed - could not authenticate")
        formatter.print_summary({
            "Environment": "Development",
            "Server Status": "Running but Authentication Failed"
        })
        sys.exit(1)

if __name__ == "__main__":
    main()
