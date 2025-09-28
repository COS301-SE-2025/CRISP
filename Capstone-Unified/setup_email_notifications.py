#!/usr/bin/env python3
"""
Setup email notifications for threat feed updates
"""
import os
import sys
import django

sys.path.append('/mnt/c/Users/Liamv/Documents/GitHub/CRISP/Capstone-Unified')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models.models import Organization, ThreatFeed
from core.alerts.models import FeedUpdateSubscription

User = get_user_model()

def setup_notifications():
    """Setup email notifications for all users and feeds"""
    print("🔔 Setting up email notifications...")
    
    # Get all users
    users = User.objects.filter(is_active=True)
    print(f"👤 Found {users.count()} active users")
    
    # Get all organizations
    organizations = Organization.objects.all()
    print(f"🏢 Found {organizations.count()} organizations")
    
    # Get all threat feeds
    feeds = ThreatFeed.objects.filter(is_active=True)
    print(f"📡 Found {feeds.count()} active threat feeds")
    
    subscription_count = 0
    
    for user in users:
        print(f"\n👤 Setting up notifications for: {user.username} ({user.email})")
        
        # Create organization-wide subscription for user's organization
        if user.organization:
            subscription, created = FeedUpdateSubscription.objects.get_or_create(
                user=user,
                organization=user.organization,
                threat_feed=None,  # Organization-wide
                defaults={
                    'email_notifications': True,
                    'in_app_notifications': True,
                    'notification_frequency': 'immediate',
                    'is_active': True
                }
            )
            
            if created:
                print(f"   ✅ Created organization-wide subscription for {user.organization.name}")
                subscription_count += 1
            else:
                print(f"   ℹ️  Organization subscription already exists for {user.organization.name}")
                # Update existing subscription to ensure email notifications are enabled
                if not subscription.email_notifications:
                    subscription.email_notifications = True
                    subscription.is_active = True
                    subscription.save()
                    print(f"   🔄 Updated subscription to enable email notifications")
        
        # Optionally create specific feed subscriptions for external feeds
        external_feeds = feeds.filter(is_external=True)
        for feed in external_feeds:
            subscription, created = FeedUpdateSubscription.objects.get_or_create(
                user=user,
                threat_feed=feed,
                organization=None,
                defaults={
                    'email_notifications': True,
                    'in_app_notifications': True,
                    'notification_frequency': 'immediate',
                    'is_active': True
                }
            )
            
            if created:
                print(f"   ✅ Created specific subscription for feed: {feed.name}")
                subscription_count += 1
            else:
                # Update existing subscription to ensure email notifications are enabled
                if not subscription.email_notifications:
                    subscription.email_notifications = True
                    subscription.is_active = True
                    subscription.save()
                    print(f"   🔄 Updated feed subscription to enable email notifications")
    
    print(f"\n✅ Setup complete!")
    print(f"   📊 Created {subscription_count} new subscriptions")
    
    # Show summary
    total_subscriptions = FeedUpdateSubscription.objects.filter(
        is_active=True,
        email_notifications=True
    ).count()
    print(f"   🔔 Total active email subscriptions: {total_subscriptions}")
    
    # Test with AlienVault feed
    alienvault_feed = ThreatFeed.objects.filter(name__icontains="AlienVault").first()
    if alienvault_feed:
        subscribers = FeedUpdateSubscription.objects.filter(
            models.Q(threat_feed=alienvault_feed) | 
            models.Q(organization=alienvault_feed.owner, threat_feed__isnull=True),
            is_active=True,
            email_notifications=True
        ).select_related('user')
        
        print(f"\n📡 AlienVault feed subscribers:")
        for sub in subscribers:
            print(f"   📧 {sub.user.username} ({sub.user.email})")
    
    return subscription_count

if __name__ == "__main__":
    from django.db import models
    setup_notifications()