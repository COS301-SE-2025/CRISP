#!/usr/bin/env python3
"""
Test viewer user login functionality
"""

import os
import sys
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')
django.setup()

from UserManagement.models import CustomUser, Organization


def test_viewer_login_api():
    """Test viewer login via API"""
    print("🔐 Testing Viewer User Login via API...")
    
    # Check if we have any viewer users
    viewers = CustomUser.objects.filter(role='viewer', is_active=True, is_verified=True)
    
    if not viewers.exists():
        print("    No active viewer users found. Creating test viewer...")
        
        # Create test organization if needed
        org, created = Organization.objects.get_or_create(
            name='Test Viewer Organization',
            defaults={
                'domain': 'testviewer.example.com',
                'description': 'Organization for viewer testing'
            }
        )
        
        # Create test viewer
        viewer = CustomUser.objects.create_user(
            username='test_viewer',
            email='viewer@testviewer.example.com',
            password='ViewerTestPass123!',
            organization=org,
            role='viewer',
            is_verified=True,
            is_active=True
        )
        print(f"   Created test viewer: {viewer.username}")
    else:
        viewer = viewers.first()
        print(f"   ℹ️  Using existing viewer: {viewer.username}")
    
    # Test API login
    login_url = 'http://127.0.0.1:8000/api/auth/login/'
    login_data = {
        'username': viewer.username,
        'password': 'ViewerTestPass123!' if viewer.username == 'test_viewer' else input(f"Enter password for {viewer.username}: ")
    }
    
    try:
        print(f"   🔄 Testing login for user: {viewer.username}")
        print(f"   🌐 POST {login_url}")
        
        response = requests.post(
            login_url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   Login successful!")
            print(f"   Access token received: {data.get('access', 'N/A')[:50]}...")
            print(f"   🔄 Refresh token received: {data.get('refresh', 'N/A')[:50]}...")
            
            # Test accessing protected endpoint
            if 'access' in data:
                profile_url = 'http://127.0.0.1:8000/api/auth/profile/'
                headers = {
                    'Authorization': f'Bearer {data["access"]}',
                    'Content-Type': 'application/json'
                }
                
                print(f"   🔄 Testing profile access...")
                profile_response = requests.get(profile_url, headers=headers, timeout=10)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("   Profile access successful!")
                    print(f"   👤 User: {profile_data.get('username')}")
                    print(f"   🏢 Organization: {profile_data.get('organization', {}).get('name')}")
                    print(f"   Role: {profile_data.get('role')}")
                else:
                    print(f"   Profile access failed: {profile_response.status_code}")
                    print(f"   Response: {profile_response.text}")
            
            return True
            
        else:
            print(f"   Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   Connection failed - is the Django server running?")
        print("   Start server with: python3 manage.py runserver")
        return False
    except Exception as e:
        print(f"   Error during login test: {str(e)}")
        return False


def create_simple_login_form():
    """Create a simple HTML login form for testing"""
    print("Creating simple login form...")
    
    login_html = """
<!DOCTYPE html>
<html>
<head>
    <title>CRISP User Management - Login</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 400px; 
            margin: 100px auto; 
            padding: 20px;
            background-color: #f5f5f5;
        }
        .login-form { 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h2 { 
            text-align: center; 
            color: #333; 
            margin-bottom: 30px;
        }
        input { 
            width: 100%; 
            padding: 12px; 
            margin: 10px 0; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            box-sizing: border-box;
        }
        button { 
            width: 100%; 
            padding: 12px; 
            background: #007cba; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 16px;
        }
        button:hover { 
            background: #005a87; 
        }
        .result { 
            margin-top: 20px; 
            padding: 10px; 
            border-radius: 4px; 
            display: none;
        }
        .success { 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb;
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb;
        }
        .info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="login-form">
        <h2>🛡️ CRISP User Management</h2>
        
        <div class="info">
            <strong>Test Credentials:</strong><br>
            Username: test_viewer<br>
            Password: ViewerTestPass123!
        </div>
        
        <form id="loginForm">
            <input type="text" id="username" placeholder="Username" required>
            <input type="password" id="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        
        <div id="result" class="result"></div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('result');
            
            try {
                const response = await fetch('/api/auth/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.className = 'result success';
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <strong>Login Successful!</strong><br>
                        Welcome ${data.user?.username || username}!<br>
                        Role: ${data.user?.role || 'N/A'}<br>
                        Organization: ${data.user?.organization || 'N/A'}<br>
                        <br>
                        <strong>Access Token:</strong><br>
                        <small>${data.access || 'N/A'}</small>
                    `;
                    
                    // Store token for future requests
                    localStorage.setItem('access_token', data.access);
                    localStorage.setItem('refresh_token', data.refresh);
                    
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <strong>Login Failed</strong><br>
                        ${data.detail || data.non_field_errors || 'Invalid credentials'}
                    `;
                }
            } catch (error) {
                resultDiv.className = 'result error';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `
                    <strong>Error</strong><br>
                    ${error.message}
                `;
            }
        });
    </script>
</body>
</html>
"""
    
    # Create templates directory if it doesn't exist
    templates_dir = "/mnt/c/Users/Client/Documents/GitHub/CRISP/UserManagment/UserManagement/templates"
    auth_dir = f"{templates_dir}/auth"
    
    os.makedirs(auth_dir, exist_ok=True)
    
    # Write login form
    login_file = f"{auth_dir}/login.html"
    with open(login_file, 'w') as f:
        f.write(login_html)
    
    print(f"   Created login form: {login_file}")
    print(f"   🌐 Access at: http://127.0.0.1:8000/auth/login/")
    
    return login_file


def show_curl_examples():
    """Show curl examples for API login"""
    print("📚 API Login Examples:")
    print("-" * 40)
    
    print("1. Login with curl:")
    print("""
curl -X POST http://127.0.0.1:8000/api/auth/login/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "test_viewer",
    "password": "ViewerTestPass123!"
  }'
""")
    
    print("2. Get user profile (after login):")
    print("""
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
""")
    
    print("3. Example successful response:")
    print("""{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid",
    "username": "test_viewer",
    "role": "viewer",
    "organization": "Test Viewer Organization"
  }
}""")


def main():
    """Main function"""
    print("CRISP User Management - Viewer Login Test")
    print("=" * 50)
    
    # Test API login
    login_success = test_viewer_login_api()
    
    print("\n" + "=" * 50)
    
    # Create login form
    create_simple_login_form()
    
    print("\n" + "=" * 50)
    
    # Show examples
    show_curl_examples()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    if login_success:
        print("Viewer login via API works correctly")
    else:
        print("Viewer login via API failed")
    
    print("Simple login form created")
    print("API examples provided")
    
    print("\nNEXT STEPS:")
    print("1. Ensure Django server is running: python3 manage.py runserver")
    print("2. Test login via curl command above")
    print("3. Or access login form at: http://127.0.0.1:8000/auth/login/")


if __name__ == '__main__':
    main()