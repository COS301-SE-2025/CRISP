#!/usr/bin/env python3
"""
Example script to create a Live IOC-Based Alert
Run this with: python manage.py shell < create_ioc_alert_example.py
"""

from django.utils import timezone
from core.models.models import CustomAlert, Indicator, AssetInventory, Organization
from core.user_management.models import CustomUser

def create_ioc_alert():
    """
    Create a sample IOC-based alert
    """
    
    # Get or create an organization
    try:
        org = Organization.objects.first()
        if not org:
            print("No organizations found. Creating demo organization...")
            org = Organization.objects.create(
                name="Demo Organization",
                description="Demo organization for IOC alerts"
            )
    except Exception as e:
        print(f"Error getting organization: {e}")
        return
    
    # Create an IOC-based alert
    try:
        alert = CustomAlert.objects.create(
            title="Malicious IP Address Detected",
            description="A known malicious IP address (192.168.1.100) has been detected in network traffic. This IP is associated with APT29 activities and has been flagged as high-risk.",
            alert_type="ioc_matched",
            severity="high",
            organization=org,
            confidence_score=85,
            metadata={
                "detection_source": "Network Monitoring",
                "threat_actor": "APT29",
                "attack_technique": "T1071.001 - Application Layer Protocol: Web Protocols",
                "affected_systems": ["web-server-01", "database-02"],
                "ioc_details": {
                    "type": "ip",
                    "value": "192.168.1.100",
                    "confidence": 85,
                    "first_seen": timezone.now().isoformat(),
                    "source": "Threat Intelligence Feed"
                }
            }
        )
        
        print(f"✅ Created IOC Alert: {alert.title}")
        print(f"   Alert ID: {alert.id}")
        print(f"   Severity: {alert.severity}")
        print(f"   Created: {alert.created_at}")
        
        # Optionally link to indicators if they exist
        try:
            malicious_ip = Indicator.objects.filter(
                type="ip",
                value__contains="192.168.1.100"
            ).first()
            
            if malicious_ip:
                alert.source_indicators.add(malicious_ip)
                print(f"   ✅ Linked to indicator: {malicious_ip.value}")
        except Exception as e:
            print(f"   ⚠️ Could not link indicator: {e}")
        
        # Optionally link to assets if they exist
        try:
            affected_assets = AssetInventory.objects.filter(
                name__in=["web-server-01", "database-02"]
            )
            
            if affected_assets.exists():
                alert.matched_assets.add(*affected_assets)
                print(f"   ✅ Linked to {affected_assets.count()} assets")
        except Exception as e:
            print(f"   ⚠️ Could not link assets: {e}")
        
        return alert
        
    except Exception as e:
        print(f"❌ Error creating alert: {e}")
        return None

def create_multiple_sample_alerts():
    """
    Create multiple sample IOC alerts for demonstration
    """
    
    sample_alerts = [
        {
            "title": "Suspicious Domain Activity",
            "description": "Multiple requests detected to known phishing domain evil-site.com. This domain is associated with credential harvesting campaigns.",
            "alert_type": "threat_detected",
            "severity": "medium",
            "metadata": {
                "ioc_type": "domain",
                "ioc_value": "evil-site.com",
                "detection_count": 15,
                "affected_users": ["user1@company.com", "user2@company.com"]
            }
        },
        {
            "title": "Malware Hash Detected",
            "description": "Known malware file hash detected in email attachment. SHA256: 4f79697ec8b3c4b4f5b46a7b6e9a8c4d2f3e1a9b8c7d6e5f4a3b2c1d9e8f7a6b5c4",
            "alert_type": "asset_compromised",
            "severity": "critical",
            "metadata": {
                "ioc_type": "file_hash",
                "ioc_value": "4f79697ec8b3c4b4f5b46a7b6e9a8c4d2f3e1a9b8c7d6e5f4a3b2c1d9e8f7a6b5c4",
                "malware_family": "TrickBot",
                "delivery_method": "Email Attachment"
            }
        },
        {
            "title": "Command & Control Communication",
            "description": "Outbound communication detected to known C2 server. Immediate investigation required.",
            "alert_type": "infrastructure_targeted",
            "severity": "critical",
            "metadata": {
                "ioc_type": "ip",
                "ioc_value": "203.0.113.45",
                "c2_protocol": "HTTPS",
                "data_exfiltration_risk": "High"
            }
        }
    ]
    
    created_alerts = []
    org = Organization.objects.first()
    
    for alert_data in sample_alerts:
        try:
            alert = CustomAlert.objects.create(
                title=alert_data["title"],
                description=alert_data["description"],
                alert_type=alert_data["alert_type"],
                severity=alert_data["severity"],
                organization=org,
                confidence_score=80,
                metadata=alert_data["metadata"]
            )
            created_alerts.append(alert)
            print(f"✅ Created: {alert.title}")
            
        except Exception as e:
            print(f"❌ Error creating alert '{alert_data['title']}': {e}")
    
    return created_alerts

if __name__ == "__main__":
    print("🚨 Creating IOC-Based Alerts for SOC Dashboard...")
    print("=" * 50)
    
    # Create single alert
    alert = create_ioc_alert()
    
    print("\n" + "=" * 50)
    print("📊 Creating multiple sample alerts...")
    
    # Create multiple sample alerts
    alerts = create_multiple_sample_alerts()
    
    print(f"\n✅ Successfully created {len(alerts) + (1 if alert else 0)} IOC alerts!")
    print("\n🔍 You can now view these alerts in the SOC Dashboard under the 'IOC Alerts' tab.")
    print("📍 Navigate to: SOC Dashboard > IOC Alerts tab")