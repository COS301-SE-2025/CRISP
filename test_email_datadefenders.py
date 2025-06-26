"""
Debug SMTP2Go Connection Test
File: debug_smtp2go_test.py

Detailed debugging script to identify SMTP2Go connection issues.
Updated to use environment variables for security.
No external dependencies required - reads .env file manually.
"""

import requests
import json
import os
from datetime import datetime


def load_env_file(env_path='.env'):
    """Manually load environment variables from .env file"""
    env_vars = {}
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('\'"')  # Remove quotes if present
                    env_vars[key] = value
                    # Also set in os.environ for consistency
                    os.environ[key] = value
    except FileNotFoundError:
        print(f"❌ Error: .env file not found at {env_path}")
        print("   Make sure your .env file is in the same directory as this script")
        return None
    except Exception as e:
        print(f"❌ Error reading .env file: {str(e)}")
        return None
    
    return env_vars


def load_environment():
    """Load environment variables from .env file"""
    # First try to load from .env file
    env_vars = load_env_file()
    if env_vars is None:
        return None
    
    # Get required environment variables
    api_key = os.getenv('SMTP2GO_API_KEY')
    base_url = os.getenv('SMTP2GO_BASE_URL', 'https://api.smtp2go.com/v3/')
    sender_email = os.getenv('CRISP_SENDER_EMAIL')
    sender_name = os.getenv('CRISP_SENDER_NAME', 'CRISP')
    
    if not api_key:
        print("❌ SMTP2GO_API_KEY not found in environment variables")
        return None
    
    if not sender_email:
        print("❌ CRISP_SENDER_EMAIL not found in environment variables")
        return None
    
    return {
        'api_key': api_key,
        'base_url': base_url,
        'sender_email': sender_email,
        'sender_name': sender_name
    }


def test_smtp2go_endpoints(config):
    """Test different SMTP2Go endpoints to identify the issue"""
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Content-Type': 'application/json',
        'X-Smtp2go-Api-Key': api_key
    }
    
    print("SMTP2Go API Debugging")
    print("=" * 50)
    print(f"API Key: {api_key[:10]}...{api_key[-4:]} (masked)")
    print(f"Base URL: {base_url}")
    print(f"Sender Email: {config['sender_email']}")
    print()
    
    # Test different endpoints
    endpoints = [
        ("stats", "GET", "Account statistics"),
        ("email/send", "POST", "Email sending endpoint"),
        ("", "GET", "API root"),
        ("account", "GET", "Account information"),
        ("stats/overall", "GET", "Overall stats")
    ]
    
    for endpoint, method, description in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"Testing: {description}")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:
                # For POST, use minimal payload
                test_payload = {
                    "to": ["test@example.com"],
                    "sender": config['sender_email'],
                    "subject": "Test",
                    "text_body": "Test"
                }
                response = requests.post(url, json=test_payload, headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
            except:
                print(f"   Response (text): {response.text[:200]}...")
            
            if response.status_code == 200:
                print("   SUCCESS")
            elif response.status_code == 404:
                print("   NOT FOUND (404)")
            elif response.status_code == 401:
                print("   UNAUTHORIZED (401) - Check API key")
            elif response.status_code == 403:
                print("   FORBIDDEN (403) - Permission denied")
            else:
                print(f"   OTHER ERROR ({response.status_code})")
                
        except requests.exceptions.Timeout:
            print("   TIMEOUT")
        except requests.exceptions.ConnectionError:
            print("   CONNECTION ERROR")
        except Exception as e:
            print(f"   EXCEPTION: {str(e)}")
        
        print()


def test_alternative_api_format(config):
    """Test alternative API key format"""
    
    print("Testing Alternative API Key Formats")
    print("=" * 50)
    
    # Sometimes SMTP2Go expects different header formats
    api_key = config['api_key']
    base_url = config['base_url']
    
    alternative_headers = [
        {
            'X-Smtp2go-Api-Key': api_key,
            'Content-Type': 'application/json'
        },
        {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        },
        {
            'Api-Key': api_key,
            'Content-Type': 'application/json'
        }
    ]
    
    for i, headers in enumerate(alternative_headers, 1):
        print(f"🧪 Test {i}: {list(headers.keys())}")
        
        try:
            response = requests.get(
                f"{base_url}stats",
                headers=headers,
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("    SUCCESS - This header format works!")
                try:
                    data = response.json()
                    print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
                except:
                    pass
                return headers
            else:
                print(f"    Failed with {response.status_code}")
                
        except Exception as e:
            print(f"    Exception: {str(e)}")
        
        print()
    
    return None


def test_direct_email_send(config):
    """Try sending email directly with proper format"""
    
    print("📧 Testing Direct Email Send")
    print("=" * 50)
    
    api_key = config['api_key']
    sender_email = config['sender_email']
    sender_name = config['sender_name']
    
    # Use the most common header format for SMTP2Go
    headers = {
        'X-Smtp2go-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Target email for testing (you can change this)
    test_email = "datadefenders.sa@gmail.com"
    
    payload = {
        "to": [test_email],
        "sender": sender_email,
        "subject": "🧪 CRISP Debug Test - Data Defenders",
        "text_body": f"""
Debug Test Email from CRISP

This is a debug test to verify SMTP2Go integration.

If you receive this email, the API is working correctly!

Sender: {sender_name} <{sender_email}>
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Data Defenders Team
        """,
        "html_body": f"""
        <html>
        <body>
            <h2>🧪 CRISP Debug Test</h2>
            <p>This is a debug test to verify SMTP2Go integration.</p>
            <p><strong>If you receive this email, the API is working correctly!</strong></p>
            <ul>
                <li>Sender: {sender_name} &lt;{sender_email}&gt;</li>
                <li>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
            </ul>
            <p>Data Defenders Team</p>
        </body>
        </html>
        """
    }
    
    try:
        print("📨 Sending debug email...")
        print(f"   To: {test_email}")
        print(f"   From: {sender_name} <{sender_email}>")
        print()
        
        response = requests.post(
            f"{config['base_url']}email/send",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print("📋 Full Response:")
        print("-" * 30)
        
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
        except:
            print("Raw response:")
            print(response.text)
        
        print("-" * 30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('data', {}).get('succeeded', 0) > 0:
                print("✅ SUCCESS! Debug email sent!")
                print(f"   Check {test_email}")
                return True
            else:
                print("❌ Email send failed in API response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
    
    return False


def check_api_key_validity(config):
    """Check if the API key format is correct"""
    
    print("🔑 API Key Validation")
    print("=" * 50)
    
    api_key = config['api_key']
    
    print(f"API Key: {api_key[:10]}...{api_key[-4:]} (masked)")
    print(f"Length: {len(api_key)} characters")
    print(f"Starts with 'api-': {api_key.startswith('api-')}")
    print(f"Format: {'Correct' if api_key.startswith('api-') and len(api_key) > 10 else 'Suspicious'}")
    print()
    
    # Check if it's a valid format
    if not api_key.startswith('api-'):
        print("⚠️  WARNING: API key should start with 'api-'")
        return False
    
    if len(api_key) < 20:
        print("⚠️  WARNING: API key seems too short")
        return False
    
    print("✅ API key format looks correct")
    return True


def check_environment_setup():
    """Check if all required environment variables are set"""
    
    print("🌍 Environment Setup Check")
    print("=" * 50)
    
    required_vars = [
        'SMTP2GO_API_KEY',
        'CRISP_SENDER_EMAIL',
        'SMTP2GO_BASE_URL',
        'CRISP_SENDER_NAME'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'API_KEY' in var:
                print(f"✅ {var}: {value[:10]}...{value[-4:]} (masked)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    print()
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please ensure these are set in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True


def main():
    """Main debugging function"""
    
    print("🛡️ CRISP SMTP2Go Debug Tool")
    print("=" * 60)
    print("🎯 Diagnosing connection issues with SMTP2Go API")
    print("🔒 Using environment variables for security")
    print("📁 Reading .env file manually (no external dependencies)")
    print()
    
    try:
        # Load configuration
        config = load_environment()
        if config is None:
            print("❌ Failed to load configuration from .env file")
            return
        
        # Step 0: Check environment setup
        if not check_environment_setup():
            print("❌ Environment setup failed. Please check your .env file.")
            return
        
        print()
        
        # Step 1: Check API key format
        check_api_key_validity(config)
        print()
        
        # Step 2: Test different endpoints
        test_smtp2go_endpoints(config)
        print()
        
        # Step 3: Test alternative header formats
        working_headers = test_alternative_api_format(config)
        print()
        
        # Step 4: Try direct email send
        email_success = test_direct_email_send(config)
        print()
        
        # Summary
        print("📋 DEBUGGING SUMMARY")
        print("=" * 50)
        
        if email_success:
            print("✅ SUCCESS: Email was sent successfully!")
            print("   Your SMTP2Go integration is working!")
            print("   Check datadefenders.sa@gmail.com for the debug email")
        else:
            print("❌ ISSUE: Email sending failed")
            print()
            print("🔧 TROUBLESHOOTING STEPS:")
            print("1. Verify your API key is active in SMTP2Go dashboard")
            print("2. Check if your account has sending permissions")
            print(f"3. Ensure '{config['sender_email']}' is verified")
            print("4. Try logging into SMTP2Go web interface to confirm account status")
            print("5. Contact SMTP2Go support if API key is correct but still fails")
            print()
            print("🌐 SMTP2Go Dashboard: https://app.smtp2go.com/")
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()