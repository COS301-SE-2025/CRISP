"""
Debug SMTP2Go Connection Test
File: debug_smtp2go_test.py

Detailed debugging script to identify SMTP2Go connection issues.
"""

import requests
import json
from datetime import datetime


def test_smtp2go_endpoints():
    """Test different SMTP2Go endpoints to identify the issue"""
    
    api_key = "api-CE7DDEAC33DA4775B069E9C39789DED6"
    base_url = "https://api.smtp2go.com/v3/"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Smtp2go-Api-Key': api_key
    }
    
    print("SMTP2Go API Debugging")
    print("=" * 50)
    print(f"API Key: {api_key}")
    print(f"Base URL: {base_url}")
    print(f"Headers: {headers}")
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
                    "sender": "test@chronocode.co.za",
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


def test_alternative_api_format():
    """Test alternative API key format"""
    
    print("Testing Alternative API Key Formats")
    print("=" * 50)
    
    # Sometimes SMTP2Go expects different header formats
    api_key = "api-CE7DDEAC33DA4775B069E9C39789DED6"
    base_url = "https://api.smtp2go.com/v3/"
    
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


def test_direct_email_send():
    """Try sending email directly with proper format"""
    
    print(" Testing Direct Email Send")
    print("=" * 50)
    
    api_key = "api-CE7DDEAC33DA4775B069E9C39789DED6"
    
    # Use the most common header format for SMTP2Go
    headers = {
        'X-Smtp2go-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "to": ["datadefenders.sa@gmail.com"],
        "sender": "datadefenders@chronocode.co.za",
        "subject": " CRISP Debug Test - Data Defenders",
        "text_body": """
Debug Test Email from CRISP

This is a debug test to verify SMTP2Go integration.

If you receive this email, the API is working correctly!

API Key: api-CE7DDEAC33DA4775B069E9C39789DED6
Sender: datadefenders@chronocode.co.za
Timestamp: {}

Data Defenders Team
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')),
        "html_body": f"""
        <html>
        <body>
            <h2>🧪 CRISP Debug Test</h2>
            <p>This is a debug test to verify SMTP2Go integration.</p>
            <p><strong>If you receive this email, the API is working correctly!</strong></p>
            <ul>
                <li>API Key: api-CE7DDEAC33DA4775B069E9C39789DED6</li>
                <li>Sender: datadefenders@chronocode.co.za</li>
                <li>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
            </ul>
            <p>Data Defenders Team</p>
        </body>
        </html>
        """
    }
    
    try:
        print(" Sending debug email...")
        print(f" To: datadefenders.sa@gmail.com")
        print(f" From: datadefenders@chronocode.co.za")
        print()
        
        response = requests.post(
            "https://api.smtp2go.com/v3/email/send",
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
                print(" SUCCESS! Debug email sent!")
                print(" Check datadefenders.sa@gmail.com")
                return True
            else:
                print(" Email send failed in API response")
        else:
            print(f" HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
    
    return False


def check_api_key_validity():
    """Check if the API key format is correct"""
    
    print("🔑 API Key Validation")
    print("=" * 50)
    
    api_key = "api-CE7DDEAC33DA4775B069E9C39789DED6"
    
    print(f"API Key: {api_key}")
    print(f"Length: {len(api_key)} characters")
    print(f"Starts with 'api-': {api_key.startswith('api-')}")
    print(f"Format: {'Correct' if api_key.startswith('api-') and len(api_key) > 10 else 'Suspicious'}")
    print()
    
    # Check if it's a valid format
    if not api_key.startswith('api-'):
        print(" WARNING: API key should start with 'api-'")
        return False
    
    if len(api_key) < 20:
        print(" WARNING: API key seems too short")
        return False
    
    print(" API key format looks correct")
    return True


def main():
    """Main debugging function"""
    
    print("🛡️ CRISP SMTP2Go Debug Tool")
    print("=" * 60)
    print("🎯 Diagnosing connection issues with SMTP2Go API")
    print()
    
    # Step 1: Check API key format
    check_api_key_validity()
    print()
    
    # Step 2: Test different endpoints
    test_smtp2go_endpoints()
    print()
    
    # Step 3: Test alternative header formats
    working_headers = test_alternative_api_format()
    print()
    
    # Step 4: Try direct email send
    email_success = test_direct_email_send()
    print()
    
    # Summary
    print("📋 DEBUGGING SUMMARY")
    print("=" * 50)
    
    if email_success:
        print(" SUCCESS: Email was sent successfully!")
        print(" Your SMTP2Go integration is working!")
        print(" Check datadefenders.sa@gmail.com for the debug email")
    else:
        print(" ISSUE: Email sending failed")
        print()
        print(" TROUBLESHOOTING STEPS:")
        print("1. Verify your API key is active in SMTP2Go dashboard")
        print("2. Check if your account has sending permissions")
        print("3. Ensure 'datadefenders@chronocode.co.za' is verified")
        print("4. Try logging into SMTP2Go web interface to confirm account status")
        print("5. Contact SMTP2Go support if API key is correct but still fails")
        print()
        print(" SMTP2Go Dashboard: https://app.smtp2go.com/")


if __name__ == "__main__":
    main()