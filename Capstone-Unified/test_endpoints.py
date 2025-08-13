#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for CRISP system
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

def test_endpoint(method, url, headers=None, data=None, auth_token=None):
    """Test a single endpoint and return results"""
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        result = {
            "status_code": response.status_code,
            "success": 200 <= response.status_code < 300,
            "response_time": response.elapsed.total_seconds(),
            "headers": dict(response.headers),
            "size": len(response.content)
        }
        
        try:
            result["content"] = response.json()
        except:
            result["content"] = response.text[:500] + "..." if len(response.text) > 500 else response.text
            
        return result
        
    except Exception as e:
        return {"error": str(e), "success": False}

def get_auth_token():
    """Try to get authentication token"""
    login_data = {"username": "admin", "password": "admin123"}
    result = test_endpoint("POST", f"{BASE_URL}/api/v1/auth/login/", data=login_data)
    
    if result.get("success") and isinstance(result.get("content"), dict):
        content = result["content"]
        # Try different token formats
        if "tokens" in content and "access" in content["tokens"]:
            return content["tokens"]["access"]
        return content.get("access_token") or content.get("token")
    return None

def main():
    print("=" * 80)
    print("CRISP SYSTEM ENDPOINT TESTING REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Test server connectivity first
    print("1. SERVER CONNECTIVITY")
    print("-" * 40)
    
    django_test = test_endpoint("GET", BASE_URL)
    print(f"Django Backend ({BASE_URL}): {'✓ ONLINE' if django_test.get('success') else '✗ OFFLINE'}")
    if django_test.get("success"):
        print(f"   Response Time: {django_test.get('response_time', 0):.3f}s")
    
    react_test = test_endpoint("GET", FRONTEND_URL)
    print(f"React Frontend ({FRONTEND_URL}): {'✓ ONLINE' if react_test.get('success') else '✗ OFFLINE'}")
    if react_test.get("success"):
        print(f"   Response Time: {react_test.get('response_time', 0):.3f}s")
    print()
    
    # Try to get auth token
    print("2. AUTHENTICATION")
    print("-" * 40)
    auth_token = get_auth_token()
    print(f"Authentication Token: {'✓ OBTAINED' if auth_token else '✗ FAILED'}")
    if auth_token:
        print(f"   Token (first 20 chars): {auth_token[:20]}...")
    print()
    
    # Define all endpoints to test
    endpoints = [
        # Public endpoints
        {"method": "GET", "url": "/", "name": "Home Page", "auth_required": False},
        {"method": "GET", "url": "/api/status/", "name": "Core Status", "auth_required": False},
        {"method": "GET", "url": "/taxii2/", "name": "TAXII2 Root", "auth_required": False},
        
        # Authentication endpoints
        {"method": "POST", "url": "/api/v1/auth/login/", "name": "Auth Login", "auth_required": False, "data": {"username": "admin", "password": "admin123"}},
        
        # Admin endpoints
        {"method": "GET", "url": "/api/v1/admin/system_health/", "name": "System Health", "auth_required": False},
        {"method": "GET", "url": "/api/v1/admin/trust_overview/", "name": "Trust Overview", "auth_required": True},
        
        # Alert endpoints
        {"method": "GET", "url": "/api/v1/alerts/statistics/", "name": "Alert Statistics", "auth_required": False},
        {"method": "GET", "url": "/api/v1/alerts/test-connection/", "name": "Test Gmail Connection", "auth_required": True},
        {"method": "POST", "url": "/api/v1/alerts/test-email/", "name": "Send Alert Test Email", "auth_required": True},
        
        # User endpoints
        {"method": "GET", "url": "/api/v1/users/profile/", "name": "User Profile", "auth_required": True},
        {"method": "GET", "url": "/api/v1/users/statistics/", "name": "User Statistics", "auth_required": True},
        {"method": "GET", "url": "/api/v1/users/list/", "name": "List Users", "auth_required": True},
        
        # Organization endpoints
        {"method": "GET", "url": "/api/v1/organizations/list_organizations/", "name": "List Organizations", "auth_required": True},
        {"method": "GET", "url": "/api/v1/organizations/types/", "name": "Organization Types", "auth_required": True},
        {"method": "POST", "url": "/api/v1/organizations/create_organization/", "name": "Create Organization", "auth_required": True, "data": {"name": "Test Org", "organization_type": "GOVERNMENT"}},
        
        # Trust endpoints
        {"method": "GET", "url": "/api/v1/trust/groups/", "name": "Trust Groups", "auth_required": True},
        {"method": "GET", "url": "/api/v1/trust/levels/", "name": "Trust Levels", "auth_required": True},
        {"method": "GET", "url": "/api/v1/trust/metrics/", "name": "Trust Metrics", "auth_required": True},
        {"method": "GET", "url": "/api/v1/trust/relationships/", "name": "Trust Relationships", "auth_required": True},
        
        # Threat Feed endpoints (Core API)
        {"method": "GET", "url": "/api/threat-feeds/", "name": "Threat Feeds List (Core)", "auth_required": True},
        {"method": "GET", "url": "/api/threat-feeds/external/", "name": "External Threat Feeds", "auth_required": True},
        {"method": "GET", "url": "/api/threat-feeds/available_collections/", "name": "Available Collections", "auth_required": True},
        
        # Unified API endpoints
        {"method": "GET", "url": "/api/v1/", "name": "Unified API Root", "auth_required": False},
        {"method": "GET", "url": "/api/v1/dashboard/overview/", "name": "Dashboard Overview", "auth_required": True},
        {"method": "GET", "url": "/api/v1/threat-feeds/external/", "name": "Unified External Feeds", "auth_required": True},
        {"method": "GET", "url": "/api/v1/threat-feeds/collections/", "name": "Unified Collections", "auth_required": True},
        
        # Email endpoints
        {"method": "POST", "url": "/api/v1/email/send-test/", "name": "Send Test Email", "auth_required": True, "data": {"recipient": "test@example.com"}},
    ]
    
    print("3. ENDPOINT TESTING")
    print("-" * 40)
    
    results = []
    for i, endpoint in enumerate(endpoints, 1):
        url = BASE_URL + endpoint["url"]
        method = endpoint["method"]
        name = endpoint["name"]
        auth_required = endpoint.get("auth_required", False)
        data = endpoint.get("data", None)
        
        # Determine if we need auth token
        token = auth_token if auth_required else None
        
        print(f"{i:2d}. Testing {name} ({method} {endpoint['url']})")
        
        result = test_endpoint(method, url, data=data, auth_token=token)
        result["endpoint_name"] = name
        result["url"] = endpoint["url"]
        result["method"] = method
        result["auth_required"] = auth_required
        results.append(result)
        
        if result.get("success"):
            print(f"    ✓ SUCCESS (HTTP {result['status_code']}) - {result.get('response_time', 0):.3f}s")
            if isinstance(result.get("content"), dict) and len(str(result["content"])) < 200:
                print(f"    Response: {result['content']}")
        else:
            print(f"    ✗ FAILED (HTTP {result.get('status_code', 'ERROR')})")
            if result.get("content"):
                content_str = str(result["content"])[:200] + "..." if len(str(result["content"])) > 200 else str(result["content"])
                print(f"    Error: {content_str}")
        print()
    
    # Summary
    print("4. SUMMARY")
    print("-" * 40)
    
    successful = sum(1 for r in results if r.get("success"))
    total = len(results)
    success_rate = (successful / total * 100) if total > 0 else 0
    
    print(f"Total Endpoints Tested: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    # Categorize results
    auth_endpoints = [r for r in results if r.get("auth_required")]
    public_endpoints = [r for r in results if not r.get("auth_required")]
    
    print("Public Endpoints:")
    for r in public_endpoints:
        status = "✓" if r.get("success") else "✗"
        print(f"  {status} {r['endpoint_name']} - HTTP {r.get('status_code', 'ERROR')}")
    
    print("\nAuthenticated Endpoints:")
    for r in auth_endpoints:
        status = "✓" if r.get("success") else "✗"
        print(f"  {status} {r['endpoint_name']} - HTTP {r.get('status_code', 'ERROR')}")
    
    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)

if __name__ == "__main__":
    main()