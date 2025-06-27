"""
CRISP Alert System Email Integration Test
File: test_email_datadefenders.py

Tests the alert system observer pattern with real email notifications.
Tests EmailNotificationService and AlertSystemObserver classes.
"""

import requests
import json
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from core.patterns.observer.alert_system_observer import AlertSystemObserver
    from core.patterns.observer.email_notification_observer import EmailNotificationService
    OBSERVER_CLASSES_AVAILABLE = True
except ImportError as e:
    print(f"Observer classes not available: {e}")
    OBSERVER_CLASSES_AVAILABLE = False


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
    # Try to load from crisp/config/security/env file first
    env_vars = load_env_file('crisp/config/security/env')
    if env_vars is None:
        # Fall back to .env file
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


class TestEmailNotificationService(unittest.TestCase):
    """Test cases for EmailNotificationService"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = load_environment()
        
    def test_smtp2go_connection(self):
        """Test SMTP2Go API connection and authentication"""
        if not self.config:
            self.skipTest("Environment configuration not available")
        
        headers = {
            'X-Smtp2go-Api-Key': self.config['api_key'],
            'Content-Type': 'application/json'
        }
        
        # Test the email send endpoint
        response = requests.post(
            f"{self.config['base_url']}email/send",
            json={
                "to": ["test@example.com"],
                "sender": self.config['sender_email'],
                "subject": "Test",
                "text_body": "Test"
            },
            headers=headers,
            timeout=10
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn('data', result)
        
    def test_email_service_initialization(self):
        """Test EmailNotificationService initialization"""
        if not OBSERVER_CLASSES_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        service = EmailNotificationService()
        self.assertIsNotNone(service.api_key)
        self.assertIsNotNone(service.from_address)
        
    def test_send_threat_alert_email(self):
        """Test sending actual threat alert email to datadefenders.sa@gmail.com"""
        if not self.config:
            self.skipTest("Environment configuration not available")
            
        result = send_real_alert_email(self.config)
        self.assertTrue(result['success'])
        self.assertIn('email_id', result['details'])


class TestAlertSystemObserver(unittest.TestCase):
    """Test cases for AlertSystemObserver"""
    
    def test_observer_initialization(self):
        """Test AlertSystemObserver initialization"""
        if not OBSERVER_CLASSES_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        observer = AlertSystemObserver("test-system")
        self.assertEqual(observer.alert_system_id, "test-system")
        self.assertIsNotNone(observer.alert_rules)
        
    def test_alert_generation(self):
        """Test alert generation for high-priority threats"""
        if not OBSERVER_CLASSES_AVAILABLE:
            self.skipTest("Observer classes not available")
            
        observer = AlertSystemObserver("test-system")
        
        # Mock threat data
        event_data = {
            'feed_id': 'test-feed',
            'indicator': {
                'type': 'ip',
                'value': '192.168.1.100',
                'severity': 'high',
                'confidence': 0.9
            }
        }
        
        # Mock subject
        mock_subject = Mock()
        
        # Test alert processing
        observer.update(mock_subject, 'indicator_added', event_data)
        
        # Verify alert was processed
        self.assertGreater(observer._alert_count, 0)


def send_real_alert_email(config):
    """Send actual alert email to datadefenders.sa@gmail.com"""
    headers = {
        'X-Smtp2go-Api-Key': config['api_key'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        "to": ["datadefenders.sa@gmail.com"],
        "sender": f"{config['sender_name']} <{config['sender_email']}>",
        "subject": "[CRISP Alert - HIGH] Threat Intelligence Alert",
        "text_body": f"""
CRISP THREAT ALERT - HIGH PRIORITY
{'='*50}

Threat: Suspicious IP Activity Detected
Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

THREAT DETAILS:
- Type: IP Address
- Value: 192.168.1.100
- Severity: HIGH
- Confidence: 90%
- Source: OTX Threat Feed

RECOMMENDED ACTIONS:
1. Review affected systems immediately
2. Check security logs for related activities
3. Contact security team if suspicious activity found
4. Document any findings in incident response system

---
CRISP - Cyber Risk Information Sharing Platform
This is an automated security alert from the demo system.
        """,
        "html_body": f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 20px; text-align: center;">
                    <h1>🚨 CRISP Threat Alert</h1>
                    <div style="display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; background-color: #dc3545; color: white;">HIGH PRIORITY</div>
                </div>
                <div style="padding: 30px;">
                    <h2>Suspicious IP Activity Detected</h2>
                    <p><strong>Detected:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h3>Threat Details</h3>
                        <ul>
                            <li><strong>Type:</strong> IP Address</li>
                            <li><strong>Value:</strong> 192.168.1.100</li>
                            <li><strong>Severity:</strong> HIGH</li>
                            <li><strong>Confidence:</strong> 90%</li>
                            <li><strong>Source:</strong> OTX Threat Feed</li>
                        </ul>
                    </div>
                    
                    <p><strong>Recommended Actions:</strong></p>
                    <ul>
                        <li>Review affected systems immediately</li>
                        <li>Check security logs for related activities</li>
                        <li>Contact security team if suspicious activity found</li>
                        <li>Document any findings in incident response system</li>
                    </ul>
                </div>
                <div style="background: #343a40; color: white; padding: 15px; text-align: center; font-size: 0.9em;">
                    <p>CRISP - Cyber Risk Information Sharing Platform</p>
                    <p>This is an automated security alert from the demo system.</p>
                </div>
            </div>
        </body>
        </html>
        """
    }
    
    try:
        response = requests.post(
            f"{config['base_url']}email/send",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('data', {}).get('succeeded', 0) > 0:
                return {
                    'success': True,
                    'message': 'Alert email sent successfully to datadefenders.sa@gmail.com',
                    'details': {
                        'email_id': result.get('data', {}).get('email_id'),
                        'api_response': 'SMTP2Go API returned success',
                        'sent_at': datetime.now().isoformat(),
                        'recipient': 'datadefenders.sa@gmail.com',
                        'sender': f"{config['sender_name']} <{config['sender_email']}>",
                        'subject': '[CRISP Alert - HIGH] Threat Intelligence Alert'
                    }
                }
            else:
                return {'success': False, 'message': 'Email send failed in API response'}
        else:
            return {'success': False, 'message': f'HTTP Error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Exception occurred: {str(e)}'}


def run_alert_system_tests():
    """Run all alert system tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEmailNotificationService))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertSystemObserver))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    return {
        'total': result.testsRun,
        'passed': result.testsRun - len(result.failures) - len(result.errors),
        'failed': len(result.failures) + len(result.errors),
        'coverage': f"{((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.0f}%" if result.testsRun > 0 else "0%"
    }


def main():
    """Main function - can run tests or send email"""
    print("🛡️ CRISP Alert System Test Suite")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'send_email':
        # Send real alert email
        config = load_environment()
        if config:
            result = send_real_alert_email(config)
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({'success': False, 'message': 'Failed to load configuration'}))
    elif len(sys.argv) > 1 and sys.argv[1] == 'run_tests':
        # Run tests and return results
        test_results = run_alert_system_tests()
        print(json.dumps(test_results, indent=2))
    else:
        # Default behavior - run both
        print("Running Alert System Tests...")
        test_results = run_alert_system_tests()
        print(f"Test Results: {test_results}")
        
        print("\nTesting email functionality...")
        config = load_environment()
        if config:
            email_result = send_real_alert_email(config)
            print(f"Email Result: {email_result}")


if __name__ == "__main__":
    main()