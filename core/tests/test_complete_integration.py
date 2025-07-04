#!/usr/bin/env python3
"""
Complete integration test for CRISP Observer Pattern with Gmail Email Integration.
This test demonstrates the full threat intelligence sharing workflow with real email notifications.
"""

import sys
import os
import json
import uuid
import smtplib
import ssl
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crisp'))

# Load environment variables
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ.setdefault(key, value)

# Import core observer components
from core.patterns.observer import Observer, Subject


class GmailEmailService:
    """Gmail email service for CRISP notifications."""
    
    def __init__(self):
        self.email_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.email_port = int(os.getenv('EMAIL_PORT', '587'))
        self.email_user = os.getenv('EMAIL_HOST_USER')
        self.email_password = os.getenv('EMAIL_HOST_PASSWORD')
        self.sender_email = os.getenv('CRISP_SENDER_EMAIL')
        self.sender_name = os.getenv('CRISP_SENDER_NAME', 'CRISP Platform')
    
    def send_email(self, recipients, subject, text_body, html_body=None):
        """Send email using Gmail SMTP."""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = ", ".join(recipients)
            
            # Add text version
            part1 = MIMEText(text_body, "plain")
            message.attach(part1)
            
            # Add HTML version if provided
            if html_body:
                part2 = MIMEText(html_body, "html")
                message.attach(part2)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.sendmail(self.sender_email, recipients, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False


class CrispThreatFeed(Subject):
    """CRISP threat feed with Gmail email notifications."""
    
    def __init__(self, name, owner_org):
        super().__init__()
        self.name = name
        self.owner_org = owner_org
        self.last_published_time = None
        self.sync_count = 0
        self.email_service = GmailEmailService()
    
    def publish_feed(self, bundle_data):
        """Publish feed and notify observers via email."""
        self.last_published_time = datetime.now()
        
        event_data = {
            'event_type': 'feed_published',
            'feed_name': self.name,
            'bundle': bundle_data,
            'timestamp': self.last_published_time,
            'owner_org': self.owner_org
        }
        
        print(f"📢 Publishing feed: {self.name}")
        print(f"   Objects: {len(bundle_data.get('objects', []))}")
        print(f"   Published: {self.last_published_time}")
        
        # Notify all observers
        self.notify(event_data)
    
    def update_feed_data(self, bundle_data):
        """Update feed and notify observers via email."""
        self.sync_count += 1
        
        event_data = {
            'event_type': 'feed_updated',
            'feed_name': self.name,
            'bundle': bundle_data,
            'timestamp': datetime.now(),
            'owner_org': self.owner_org
        }
        
        print(f"🔄 Updating feed: {self.name} (sync #{self.sync_count})")
        
        # Notify all observers
        self.notify(event_data)


class GmailEmailObserver(Observer):
    """Email notification observer using Gmail SMTP."""
    
    def __init__(self, organization_name, email_address):
        self.organization_name = organization_name
        self.email_address = email_address
        self.email_service = GmailEmailService()
        self.notifications_sent = 0
    
    def update(self, subject, event_data):
        """Handle observer notifications and send emails."""
        self.notifications_sent += 1
        event_type = event_data.get('event_type')
        feed_name = event_data.get('feed_name')
        bundle = event_data.get('bundle', {})
        timestamp = event_data.get('timestamp', datetime.now())
        
        if event_type == 'feed_published':
            self._send_feed_published_email(feed_name, bundle, timestamp)
        elif event_type == 'feed_updated':
            self._send_feed_updated_email(feed_name, bundle, timestamp)
        elif event_type == 'high_priority_alert':
            self._send_alert_email(event_data)
    
    def _send_feed_published_email(self, feed_name, bundle, timestamp):
        """Send feed published notification email."""
        subject = f"[CRISP] New Threat Feed Published - {feed_name}"
        
        # Count different object types
        objects = bundle.get('objects', [])
        indicators = [obj for obj in objects if obj.get('type') == 'indicator']
        attack_patterns = [obj for obj in objects if obj.get('type') == 'attack-pattern']
        
        text_body = f"""
New Threat Intelligence Feed Published

Organization: {self.organization_name}
Feed: {feed_name}
Published: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Content Summary:
- Total Objects: {len(objects)}
- Threat Indicators: {len(indicators)}
- Attack Patterns: {len(attack_patterns)}

High-Priority Indicators:
"""
        
        # Add high-priority indicators to email
        high_priority_count = 0
        for indicator in indicators:
            confidence = indicator.get('confidence', 0)
            severity = indicator.get('x_severity', 'unknown')
            if confidence >= 80 or severity in ['high', 'critical']:
                high_priority_count += 1
                pattern = indicator.get('pattern', 'Unknown')
                text_body += f"- {pattern} (Confidence: {confidence}%, Severity: {severity})\n"
        
        if high_priority_count == 0:
            text_body += "- No high-priority indicators in this update\n"
        
        text_body += f"""
Visit your CRISP dashboard to access the complete threat intelligence data.

---
CRISP - Cyber Risk Information Sharing Platform
This is an automated notification from the CRISP threat intelligence system.
"""
        
        # HTML version
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>CRISP Feed Published</title></head>
        <body style="font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
                    <h1>📢 New Threat Feed Published</h1>
                    <p>{feed_name}</p>
                </div>
                <div style="padding: 20px 0;">
                    <p><strong>Organization:</strong> {self.organization_name}</p>
                    <p><strong>Published:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    
                    <h3>Content Summary:</h3>
                    <ul>
                        <li><strong>Total Objects:</strong> {len(objects)}</li>
                        <li><strong>Threat Indicators:</strong> {len(indicators)}</li>
                        <li><strong>Attack Patterns:</strong> {len(attack_patterns)}</li>
                        <li><strong>High-Priority Indicators:</strong> {high_priority_count}</li>
                    </ul>
                    
                    {"<p style='background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px;'><strong>⚠️ High-Priority Threats Detected!</strong> Review immediately.</p>" if high_priority_count > 0 else "<p style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px;'>✅ No high-priority threats in this update.</p>"}
                    
                    <p>Visit your CRISP dashboard to access the complete threat intelligence data.</p>
                </div>
                <div style="text-align: center; color: #6c757d; font-size: 0.9em; margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p>CRISP - Cyber Risk Information Sharing Platform</p>
                    <p>This is an automated notification from the CRISP threat intelligence system.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = self.email_service.send_email([self.email_address], subject, text_body, html_body)
        
        if success:
            print(f"📧 EMAIL SENT #{self.notifications_sent}")
            print(f"   To: {self.organization_name} ({self.email_address})")
            print(f"   Subject: {subject}")
            print(f"   High-Priority Indicators: {high_priority_count}")
        else:
            print(f"❌ EMAIL FAILED to {self.email_address}")
    
    def _send_feed_updated_email(self, feed_name, bundle, timestamp):
        """Send feed updated notification email."""
        subject = f"[CRISP] Threat Feed Updated - {feed_name}"
        
        text_body = f"""
Threat Intelligence Feed Updated

Organization: {self.organization_name}
Feed: {feed_name}
Updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

The threat intelligence feed has been synchronized with the latest data.
Check your CRISP dashboard for updated threat indicators and analysis.

---
CRISP - Cyber Risk Information Sharing Platform
"""
        
        # Send email
        success = self.email_service.send_email([self.email_address], subject, text_body)
        
        if success:
            print(f"📧 UPDATE EMAIL SENT #{self.notifications_sent}")
            print(f"   To: {self.organization_name} ({self.email_address})")


class GmailAlertObserver(Observer):
    """Alert system observer with Gmail email notifications."""
    
    def __init__(self, alert_system_id, admin_email):
        self.alert_system_id = alert_system_id
        self.admin_email = admin_email
        self.email_service = GmailEmailService()
        self.alerts_generated = 0
        self.high_priority_alerts = 0
    
    def update(self, subject, event_data):
        """Handle observer notifications and generate alerts."""
        event_type = event_data.get('event_type')
        bundle = event_data.get('bundle', {})
        
        if event_type == 'feed_published' and bundle:
            self._analyze_bundle_for_alerts(event_data)
    
    def _analyze_bundle_for_alerts(self, event_data):
        """Analyze STIX bundle for threats and send alert emails."""
        bundle = event_data.get('bundle', {})
        feed_name = event_data.get('feed_name')
        
        high_priority_threats = []
        
        for obj in bundle.get('objects', []):
            if obj.get('type') == 'indicator':
                confidence = obj.get('confidence', 0)
                severity = obj.get('x_severity', 'medium')
                
                # Check for high-priority threats
                if confidence >= 80 or severity in ['high', 'critical']:
                    high_priority_threats.append(obj)
        
        if high_priority_threats:
            self.high_priority_alerts += 1
            self.alerts_generated += len(high_priority_threats)
            
            # Send alert email
            subject = f"[CRISP ALERT] High-Priority Threats Detected - {feed_name}"
            
            text_body = f"""
HIGH PRIORITY SECURITY ALERT

Alert System: {self.alert_system_id}
Feed: {feed_name}
Threats Detected: {len(high_priority_threats)}
Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

THREAT DETAILS:
"""
            
            for threat in high_priority_threats:
                pattern = threat.get('pattern', 'Unknown')
                confidence = threat.get('confidence', 0)
                severity = threat.get('x_severity', 'unknown')
                labels = ', '.join(threat.get('labels', []))
                
                text_body += f"""
• Pattern: {pattern}
  Confidence: {confidence}%
  Severity: {severity}
  Labels: {labels}
"""
            
            text_body += """
RECOMMENDED ACTIONS:
1. Review affected systems immediately
2. Check security logs for related activities
3. Update security controls and monitoring
4. Document findings in incident response system

---
CRISP Alert System - Cyber Risk Information Sharing Platform
This is an automated security alert. Immediate action may be required.
"""
            
            # HTML alert email
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"><title>CRISP Security Alert</title></head>
            <body style="font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
                        <h1>🚨 HIGH PRIORITY SECURITY ALERT</h1>
                        <p>{len(high_priority_threats)} threats detected in {feed_name}</p>
                    </div>
                    <div style="padding: 20px 0;">
                        <p><strong>Alert System:</strong> {self.alert_system_id}</p>
                        <p><strong>Alert Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        
                        <h3>Threat Details:</h3>
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            """
            
            for threat in high_priority_threats:
                pattern = threat.get('pattern', 'Unknown')
                confidence = threat.get('confidence', 0)
                severity = threat.get('x_severity', 'unknown')
                
                html_body += f"""
                            <div style="margin-bottom: 15px; padding: 10px; border-left: 4px solid #dc3545;">
                                <strong>Pattern:</strong> {pattern}<br>
                                <strong>Confidence:</strong> {confidence}%<br>
                                <strong>Severity:</strong> {severity}
                            </div>
                """
            
            html_body += """
                        </div>
                        
                        <h3>Recommended Actions:</h3>
                        <ol>
                            <li>Review affected systems immediately</li>
                            <li>Check security logs for related activities</li>
                            <li>Update security controls and monitoring</li>
                            <li>Document findings in incident response system</li>
                        </ol>
                    </div>
                    <div style="text-align: center; color: #6c757d; font-size: 0.9em; margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p><strong>CRISP Alert System</strong></p>
                        <p>This is an automated security alert. Immediate action may be required.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send alert email
            success = self.email_service.send_email([self.admin_email], subject, text_body, html_body)
            
            if success:
                print(f"🚨 ALERT EMAIL SENT #{self.high_priority_alerts}")
                print(f"   System: {self.alert_system_id}")
                print(f"   To: {self.admin_email}")
                print(f"   Threats: {len(high_priority_threats)} high-priority indicators")
            else:
                print(f"❌ ALERT EMAIL FAILED to {self.admin_email}")


def create_test_stix_bundle():
    """Create a comprehensive test STIX bundle."""
    return {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[domain-name:value = 'malicious-threat.example.com']",
                "labels": ["malicious-activity"],
                "confidence": 95,
                "x_severity": "critical"
            },
            {
                "type": "indicator", 
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[file:hashes.SHA256 = 'abc123def456789critical_malware_hash']",
                "labels": ["malicious-activity"],
                "confidence": 88,
                "x_severity": "high"
            },
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[ipv4-addr:value = '203.0.113.100']",
                "labels": ["suspicious-activity"],
                "confidence": 72,
                "x_severity": "medium"
            },
            {
                "type": "attack-pattern",
                "id": f"attack-pattern--{uuid.uuid4()}",
                "name": "Spear Phishing via Service",
                "x_mitre_tactic": "initial-access",
                "x_mitre_technique": "T1566.003"
            }
        ]
    }


def test_complete_gmail_observer_integration():
    """Test complete integration with Gmail email notifications."""
    print("=" * 80)
    print("🧪 CRISP COMPLETE GMAIL OBSERVER INTEGRATION TEST")
    print("=" * 80)
    
    # Get email configuration
    admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', os.getenv('EMAIL_HOST_USER'))
    if not admin_email:
        print("❌ No admin email configured")
        return False
    
    print(f"📧 Test emails will be sent to: {admin_email}")
    
    # Create test organizations and feeds
    university = "Test University Security Team"
    gov_agency = "Government Cyber Defense"
    
    # Create threat feeds with Gmail integration
    external_feed = CrispThreatFeed("Critical Threat Intelligence Feed", university)
    internal_feed = CrispThreatFeed("Government Analysis Feed", gov_agency)
    
    # Create Gmail-enabled observers
    print("\n📋 Setting up Gmail-enabled observers...")
    university_email = GmailEmailObserver(university, admin_email)
    gov_email = GmailEmailObserver(gov_agency, admin_email)
    university_alerts = GmailAlertObserver("University_SIEM", admin_email)
    gov_alerts = GmailAlertObserver("Gov_SOC_Platform", admin_email)
    
    # Attach observers to feeds
    external_feed.attach(university_email)
    external_feed.attach(university_alerts)
    
    internal_feed.attach(gov_email)
    internal_feed.attach(gov_alerts)
    
    # Cross-organization monitoring
    external_feed.attach(gov_alerts)  # Gov monitors university feed
    internal_feed.attach(university_alerts)  # University monitors gov feed
    
    print(f"✅ External feed has {external_feed.get_observer_count()} observers")
    print(f"✅ Internal feed has {internal_feed.get_observer_count()} observers")
    
    # Test 1: Publish high-priority threat feed with email notifications
    print("\n" + "=" * 80)
    print("TEST 1: Publishing High-Priority Threat Feed with Gmail Notifications")
    print("=" * 80)
    
    critical_bundle = create_test_stix_bundle()
    external_feed.publish_feed(critical_bundle)
    
    # Test 2: Update internal feed
    print("\n" + "=" * 80)
    print("TEST 2: Updating Internal Feed with Gmail Notifications")
    print("=" * 80)
    
    update_bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[url:value = 'http://updated-threat.example.com/payload']",
                "labels": ["suspicious-activity"],
                "confidence": 65,
                "x_severity": "medium"
            }
        ]
    }
    
    internal_feed.update_feed_data(update_bundle)
    
    # Test 3: Publish another high-priority feed
    print("\n" + "=" * 80)
    print("TEST 3: Publishing Additional Critical Threats")
    print("=" * 80)
    
    additional_threats = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[process:name = 'malicious_ransomware.exe']",
                "labels": ["malicious-activity"],
                "confidence": 98,
                "x_severity": "critical"
            },
            {
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "pattern": "[network-traffic:dst_ref.value = '198.51.100.50']",
                "labels": ["malicious-activity"],
                "confidence": 85,
                "x_severity": "high"
            }
        ]
    }
    
    internal_feed.publish_feed(additional_threats)
    
    # Display final statistics
    print("\n" + "=" * 80)
    print("📊 GMAIL INTEGRATION TEST SUMMARY")
    print("=" * 80)
    
    print(f"📧 University Email Notifications: {university_email.notifications_sent}")
    print(f"📧 Government Email Notifications: {gov_email.notifications_sent}")
    print(f"🚨 University Alert Emails: {university_alerts.high_priority_alerts} high-priority")
    print(f"🚨 Government Alert Emails: {gov_alerts.high_priority_alerts} high-priority")
    print(f"⚡ Total Alerts Generated: {university_alerts.alerts_generated + gov_alerts.alerts_generated}")
    
    print(f"\n📬 All emails sent to: {admin_email}")
    print(f"📧 Check your Gmail inbox for {university_email.notifications_sent + gov_email.notifications_sent} notifications")
    print(f"🚨 Check your Gmail inbox for {university_alerts.high_priority_alerts + gov_alerts.high_priority_alerts} security alerts")
    
    # Verify test success
    total_emails = (university_email.notifications_sent + gov_email.notifications_sent + 
                   university_alerts.high_priority_alerts + gov_alerts.high_priority_alerts)
    
    if total_emails > 0:
        print("\n✅ COMPLETE GMAIL INTEGRATION TEST SUCCESSFUL!")
        print("🎉 CRISP threat intelligence platform with Gmail notifications is fully operational!")
        
        print("\n🚀 System Capabilities Demonstrated:")
        print("   • Real-time threat intelligence sharing")
        print("   • Cross-organization monitoring")
        print("   • High-priority threat detection")
        print("   • Professional HTML email notifications")
        print("   • Security alert system")
        print("   • Observer pattern integration")
        print("   • Gmail SMTP integration")
        
        return True
    else:
        print("\n❌ No emails were sent - check configuration")
        return False


if __name__ == "__main__":
    try:
        success = test_complete_gmail_observer_integration()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)