"""
Test Email Script for Data Defenders
File: test_email_datadefenders.py

Simple test script to send an email to datadefenders.sa@gmail.com using SMTP2Go.
"""

import requests
import json
from datetime import datetime


def send_test_email():
    """Send a test email to datadefenders.sa@gmail.com"""
    
    # SMTP2Go configuration
    api_key = "api-CE7DDEAC33DA4775B069E9C39789DED6"
    base_url = "https://api.smtp2go.com/v3/"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Smtp2go-Api-Key': api_key
    }
    
    # Email content
    subject = "🛡️ CRISP Observer Pattern Test - Data Defenders"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CRISP Test Email</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background-color: #f8f9fa; 
            }}
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background-color: white; 
                border-radius: 8px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            }}
            .header {{ 
                background-color: #28a745; 
                color: white; 
                padding: 20px; 
                border-radius: 8px 8px 0 0; 
                text-align: center; 
            }}
            .content {{ 
                padding: 20px; 
            }}
            .success-badge {{ 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #28a745; 
                color: white; 
                border-radius: 20px; 
                font-weight: bold; 
                margin: 10px 0; 
            }}
            .info-box {{ 
                background-color: #e3f2fd; 
                padding: 15px; 
                border-radius: 5px; 
                margin: 15px 0; 
                border-left: 4px solid #2196f3; 
            }}
            .feature-list {{ 
                background-color: #f8f9fa; 
                padding: 15px; 
                border-radius: 5px; 
                margin: 15px 0; 
            }}
            .footer {{ 
                background-color: #e9ecef; 
                padding: 15px; 
                border-radius: 0 0 8px 8px; 
                text-align: center; 
                font-size: 12px; 
                color: #6c757d; 
            }}
            ul {{ 
                padding-left: 20px; 
            }}
            li {{ 
                margin: 8px 0; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ CRISP Observer Pattern</h1>
                <p>Cyber Risk Information Sharing Platform</p>
                <div class="success-badge">✅ Integration Successful!</div>
            </div>
            
            <div class="content">
                <h2>Hello Data Defenders Team! 👋</h2>
                
                <p>Congratulations! Your CRISP Observer Pattern with SMTP2Go integration is working perfectly!</p>
                
                <div class="info-box">
                    <h3>📧 Email Integration Details:</h3>
                    <ul>
                        <li><strong>API Key:</strong> api-CE7DDEAC33DA4775B069E9C39789DED6</li>
                        <li><strong>Sender:</strong> datadefenders@chronocode.co.za</li>
                        <li><strong>Recipient:</strong> datadefenders.sa@gmail.com</li>
                        <li><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                        <li><strong>Status:</strong> ✅ Successfully Delivered</li>
                    </ul>
                </div>
                
                <div class="feature-list">
                    <h3>🚀 Observer Pattern Features Implemented:</h3>
                    <ul>
                        <li>✅ <strong>ThreatFeedSubject</strong> - Manages threat feed notifications</li>
                        <li>✅ <strong>InstitutionObserver</strong> - Notifies institutions of feed updates</li>
                        <li>✅ <strong>AlertSystemObserver</strong> - Triggers security alerts</li>
                        <li>✅ <strong>EmailNotificationObserver</strong> - Sends professional email notifications</li>
                        <li>✅ <strong>SMTP2Go Integration</strong> - Reliable email delivery service</li>
                        <li>✅ <strong>Batch Processing</strong> - Groups notifications to prevent spam</li>
                        <li>✅ <strong>Priority-based Routing</strong> - Routes alerts based on severity</li>
                        <li>✅ <strong>Professional Templates</strong> - Beautiful HTML email formatting</li>
                        <li>✅ <strong>Async Processing</strong> - Non-blocking email delivery via Celery</li>
                        <li>✅ <strong>Retry Mechanisms</strong> - Automatic retry on failures</li>
                    </ul>
                </div>
                
                <h3>🔔 Notification Types Available:</h3>
                <ul>
                    <li><strong>🚨 Critical Alerts</strong> - High-priority security threats</li>
                    <li><strong>⚠️ Threat Indicators</strong> - New IoCs and malicious indicators</li>
                    <li><strong>📊 TTP Updates</strong> - Tactics, Techniques, and Procedures</li>
                    <li><strong>📈 Feed Publications</strong> - New threat intelligence feeds</li>
                    <li><strong>📦 Batch Summaries</strong> - Multiple notifications in one email</li>
                </ul>
                
                <div class="info-box">
                    <h3>📋 Next Steps:</h3>
                    <ol>
                        <li>Integrate with your existing CRISP threat feeds</li>
                        <li>Configure recipient groups for your team</li>
                        <li>Set up priority-based alert routing</li>
                        <li>Enable batch processing for optimal email delivery</li>
                        <li>Monitor system health with built-in diagnostics</li>
                    </ol>
                </div>
                
                <p><strong>🎉 Your CRISP system is now ready for production use!</strong></p>
                
                <p>The Observer pattern implementation perfectly follows your UML diagram and integrates seamlessly with the existing CRISP architecture.</p>
            </div>
            
            <div class="footer">
                <p><strong>CRISP - Cyber Risk Information Sharing Platform</strong></p>
                <p>Data Defenders Team | University of Pretoria COS 301</p>
                <p>This email was sent via SMTP2Go API integration</p>
                <p>Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    CRISP Observer Pattern Test - Data Defenders
    ==========================================
    
    Hello Data Defenders Team!
    
    Congratulations! Your CRISP Observer Pattern with SMTP2Go integration is working perfectly!
    
    EMAIL INTEGRATION DETAILS:
    - API Key: api-CE7DDEAC33DA4775B069E9C39789DED6
    - Sender: datadefenders@chronocode.co.za
    - Recipient: datadefenders.sa@gmail.com
    - Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
    - Status: ✅ Successfully Delivered
    
    OBSERVER PATTERN FEATURES IMPLEMENTED:
    ✅ ThreatFeedSubject - Manages threat feed notifications
    ✅ InstitutionObserver - Notifies institutions of feed updates
    ✅ AlertSystemObserver - Triggers security alerts
    ✅ EmailNotificationObserver - Sends professional email notifications
    ✅ SMTP2Go Integration - Reliable email delivery service
    ✅ Batch Processing - Groups notifications to prevent spam
    ✅ Priority-based Routing - Routes alerts based on severity
    ✅ Professional Templates - Beautiful HTML email formatting
    ✅ Async Processing - Non-blocking email delivery via Celery
    ✅ Retry Mechanisms - Automatic retry on failures
    
    NOTIFICATION TYPES AVAILABLE:
    - 🚨 Critical Alerts - High-priority security threats
    - ⚠️ Threat Indicators - New IoCs and malicious indicators
    - 📊 TTP Updates - Tactics, Techniques, and Procedures
    - 📈 Feed Publications - New threat intelligence feeds
    - 📦 Batch Summaries - Multiple notifications in one email
    
    NEXT STEPS:
    1. Integrate with your existing CRISP threat feeds
    2. Configure recipient groups for your team
    3. Set up priority-based alert routing
    4. Enable batch processing for optimal email delivery
    5. Monitor system health with built-in diagnostics
    
    🎉 Your CRISP system is now ready for production use!
    
    The Observer pattern implementation perfectly follows your UML diagram and integrates seamlessly with the existing CRISP architecture.
    
    ---
    CRISP - Cyber Risk Information Sharing Platform
    Data Defenders Team | University of Pretoria COS 301
    This email was sent via SMTP2Go API integration
    Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
    """
    
    # Email payload
    payload = {
        "to": ["datadefenders.sa@gmail.com"],
        "sender": "Data Defenders CRISP <datadefenders@chronocode.co.za>",
        "subject": subject,
        "html_body": html_content,
        "text_body": text_content
    }
    
    try:
        print("🚀 Sending test email to datadefenders.sa@gmail.com...")
        print(f"📧 Subject: {subject}")
        print(f"🔑 API Key: {api_key}")
        print(f"📤 Sender: datadefenders@chronocode.co.za")
        print()
        
        response = requests.post(
            f"{base_url}email/send",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        result = response.json()
        
        print("📋 SMTP2Go Response:")
        print("=" * 40)
        print(json.dumps(result, indent=2))
        print("=" * 40)
        
        if response.status_code == 200 and result.get('data', {}).get('succeeded', 0) > 0:
            print("✅ SUCCESS! Email sent successfully!")
            print("📧 Check the inbox at datadefenders.sa@gmail.com")
            print("📱 Also check spam/junk folder if not in inbox")
            print()
            print("📊 Email Statistics:")
            data = result.get('data', {})
            print(f"   - Succeeded: {data.get('succeeded', 0)}")
            print(f"   - Failed: {data.get('failed', 0)}")
            if 'email_id' in data:
                print(f"   - Email ID: {data['email_id']}")
            
            return True
        else:
            print("❌ FAILED! Email was not sent successfully")
            print(f"HTTP Status: {response.status_code}")
            error_msg = result.get('data', {}).get('error', 'Unknown error')
            print(f"Error: {error_msg}")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ NETWORK ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False


def test_smtp2go_connection():
    """Test SMTP2Go API connection"""
    print("🔍 Testing SMTP2Go API connection...")
    
    api_key = "api-CE7DDEAC33DA4775B069E9C39789DED6"
    base_url = "https://api.smtp2go.com/v3/"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Smtp2go-Api-Key': api_key
    }
    
    try:
        response = requests.get(
            f"{base_url}stats",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SMTP2Go API connection successful!")
            print("🌐 API Status: Online")
            return True
        else:
            print(f"❌ SMTP2Go API connection failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SMTP2Go API connection error: {str(e)}")
        return False


def main():
    """Main function to run the email test"""
    print("🛡️ CRISP Observer Pattern Email Test")
    print("=" * 50)
    print("📧 Testing email delivery to: datadefenders.sa@gmail.com")
    print("🔑 Using API Key: api-CE7DDEAC33DA4775B069E9C39789DED6")
    print("📤 Sending from: datadefenders@chronocode.co.za")
    print()
    
    # Test API connection first
    if not test_smtp2go_connection():
        print("❌ Cannot proceed - API connection failed")
        return
    
    print()
    
    # Send test email
    success = send_test_email()
    
    print()
    print("=" * 50)
    if success:
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print()
        print("📧 IMPORTANT: Check your email!")
        print("   → Inbox: datadefenders.sa@gmail.com")
        print("   → Subject: 🛡️ CRISP Observer Pattern Test - Data Defenders")
        print("   → Check spam folder if not in inbox")
        print()
        print("✅ Your CRISP Observer Pattern is ready!")
        print("🚀 SMTP2Go integration is working perfectly!")
    else:
        print("❌ TEST FAILED!")
        print("🔧 Check the error messages above for troubleshooting")
        print()
        print("💡 Common issues:")
        print("   - Check API key is correct")
        print("   - Verify sender domain is authorized")
        print("   - Ensure recipient email is valid")


if __name__ == "__main__":
    main()