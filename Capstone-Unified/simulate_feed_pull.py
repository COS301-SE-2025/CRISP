#!/usr/bin/env python3
"""
Simulate a successful feed pull to test batch notifications
"""
import os
import sys
import django
import time

sys.path.append('/mnt/c/Users/Liamv/Documents/GitHub/CRISP/Capstone-Unified')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from core.models.models import ThreatFeed, Indicator
from django.utils import timezone

def simulate_feed_pull():
    """Simulate a realistic feed pull with multiple indicators"""
    print("🎯 Simulating threat feed pull...")
    
    # Get the AlienVault feed
    feed = ThreatFeed.objects.filter(name__icontains="AlienVault").first()
    if not feed:
        print("❌ AlienVault feed not found")
        return
    
    print(f"📡 Simulating pull for: {feed.name}")
    print("🔄 Creating indicators (should trigger batch notification)...")
    
    # Simulate realistic indicators that might come from OTX
    indicators_data = [
        {"value": "malicious-domain-1.com", "type": "domain"},
        {"value": "192.168.1.100", "type": "ipv4-addr"},
        {"value": "bad-site.org", "type": "domain"},
        {"value": "evil.example.net", "type": "domain"},
        {"value": "10.0.0.50", "type": "ipv4-addr"},
        {"value": "suspicious-url.com/malware", "type": "url"},
        {"value": "threat.badguy.com", "type": "domain"},
    ]
    
    for i, ind_data in enumerate(indicators_data):
        timestamp = int(time.time() * 1000)  # Unique timestamp
        Indicator.objects.create(
            value=f"{ind_data['value']}-{timestamp}-{i}",
            type=ind_data['type'],
            threat_feed=feed,
            description=f"Simulated OTX indicator {i+1}",
            confidence=85,
            first_seen=timezone.now(),
            last_seen=timezone.now(),
            stix_id=f"indicator--sim-{timestamp}-{i}"
        )
        print(f"   ✅ Added {ind_data['type']}: {ind_data['value']}")
        time.sleep(0.2)  # Small delay like real processing
    
    print(f"\n✅ Simulated pull complete!")
    print(f"   📊 Added {len(indicators_data)} indicators")
    print(f"   ⏰ Should get 1 summary notification in ~30 seconds")
    print(f"   🌐 Check your browser for toast notification!")

if __name__ == "__main__":
    simulate_feed_pull()