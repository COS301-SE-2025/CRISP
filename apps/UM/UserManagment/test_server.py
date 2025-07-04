#!/usr/bin/env python3
"""
Quick server connectivity test
"""

import requests
import sys

def test_server_connectivity():
    """Test if Django server is running"""
    try:
        print("Testing server connectivity...")
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        print(f"✅ Server is accessible (status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is Django running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server_connectivity()
    sys.exit(0 if success else 1)
