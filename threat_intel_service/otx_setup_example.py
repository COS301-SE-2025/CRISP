#!/usr/bin/env python3
"""
Example script demonstrating OTX integration setup and usage.
This script shows how to configure and test the OTX threat intelligence integration.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append('/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/threat_intel_service')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threat_intel.settings')
django.setup()

from django.conf import settings
from core.otx_client import OTXClient, OTXAPIError
from core.otx_processor import OTXProcessor
from core.models import Organization, Collection
from core.tasks import fetch_otx_threat_feeds, test_otx_connection

def setup_otx_environment():
    """Set up OTX environment variables and test connection."""
    print("=== OTX Integration Setup ===\n")
    
    # Check if API key is set
    api_key = os.environ.get('OTX_API_KEY')
    if not api_key:
        print("❌ OTX_API_KEY environment variable not set!")
        print("Please set your OTX API key:")
        print("export OTX_API_KEY='your_api_key_here'")
        print("\nTo get an OTX API key:")
        print("1. Go to https://otx.alienvault.com/")
        print("2. Create an account or log in")
        print("3. Go to Settings > API Integration")
        print("4. Copy your API key")
        return False
    
    print(f"✅ OTX API key configured (ending in ...{api_key[-4:]})")
    
    # Test connection
    try:
        client = OTXClient(api_key)
        if client.test_connection():
            print("✅ OTX API connection successful")
            
            # Get user info
            user_info = client.get_user_info()
            print(f"   Connected as: {user_info.get('username', 'Unknown')}")
            print(f"   Member since: {user_info.get('member_since', 'Unknown')}")
            
            return True
        else:
            print("❌ OTX API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OTX connection: {e}")
        return False

def demonstrate_otx_client():
    """Demonstrate OTX client functionality."""
    print("\n=== OTX Client Demonstration ===\n")
    
    try:
        client = OTXClient()
        
        # Get recent pulses
        print("Fetching recent pulses...")
        pulses = client.get_pulses(limit=3)
        print(f"Retrieved {len(pulses)} pulses:")
        
        for i, pulse in enumerate(pulses, 1):
            print(f"\n{i}. {pulse.get('name', 'Unnamed pulse')}")
            print(f"   Created: {pulse.get('created', 'Unknown')}")
            print(f"   Author: {pulse.get('author_name', 'Unknown')}")
            print(f"   Indicators: {len(pulse.get('indicators', []))}")
            print(f"   Tags: {', '.join(pulse.get('tags', []))}")
            
            # Show some indicators
            indicators = pulse.get('indicators', [])[:3]
            if indicators:
                print("   Sample indicators:")
                for ind in indicators:
                    print(f"     - {ind.get('type', 'Unknown')}: {ind.get('indicator', 'N/A')}")
        
        # Get recent indicators
        print(f"\nFetching recent indicators...")
        indicators = client.get_recent_indicators(types=['IPv4', 'domain'], limit=5)
        print(f"Retrieved {len(indicators)} indicators:")
        
        for i, indicator in enumerate(indicators, 1):
            print(f"{i}. {indicator.get('type', 'Unknown')}: {indicator.get('indicator', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error demonstrating OTX client: {e}")

def demonstrate_otx_processing():
    """Demonstrate OTX data processing into STIX format."""
    print("\n=== OTX Processing Demonstration ===\n")
    
    try:
        # Get or create organization for OTX data
        org, created = Organization.objects.get_or_create(
            name='AlienVault OTX Demo',
            defaults={
                'description': 'Demo organization for OTX data processing',
                'identity_class': 'organization',
                'sectors': ['technology'],
            }
        )
        
        if created:
            print("✅ Created demo organization")
        else:
            print("ℹ️  Using existing demo organization")
        
        # Get or create collection
        collection, created = Collection.objects.get_or_create(
            alias='otx-demo',
            defaults={
                'title': 'OTX Demo Collection',
                'description': 'Demo collection for OTX threat intelligence',
                'can_read': True,
                'can_write': False,
                'media_types': ['application/stix+json;version=2.1'],
                'owner': org,
            }
        )
        
        if created:
            print("✅ Created demo collection")
        else:
            print("ℹ️  Using existing demo collection")
        
        # Initialize processor
        processor = OTXProcessor(organization=org, collection=collection)
        
        # Process recent pulses
        print("Processing recent OTX pulses...")
        results = processor.fetch_and_process_recent_pulses(days_back=7)
        
        if 'error' in results:
            print(f"❌ Processing failed: {results['error']}")
        else:
            print("✅ Processing completed successfully")
            print(f"   Total pulses: {results.get('total_pulses', 0)}")
            print(f"   Processed pulses: {results.get('processed_pulses', 0)}")
            print(f"   Created objects: {results.get('created_objects', 0)}")
            
            if results.get('errors'):
                print(f"   Errors: {len(results['errors'])}")
                for error in results['errors'][:3]:
                    print(f"     - {error}")
        
    except Exception as e:
        print(f"❌ Error demonstrating OTX processing: {e}")

def run_celery_task_demo():
    """Demonstrate Celery task execution."""
    print("\n=== Celery Task Demonstration ===\n")
    
    print("Note: This requires Celery to be running.")
    print("Start Celery with: celery -A threat_intel worker --loglevel=info")
    print("Start Celery Beat with: celery -A threat_intel beat --loglevel=info")
    
    try:
        # Test connection task
        print("Running OTX connection test task...")
        result = test_otx_connection.delay()
        task_result = result.get(timeout=30)
        
        if task_result.get('status') == 'success':
            print("✅ Connection test task successful")
            print(f"   User: {task_result.get('user', 'Unknown')}")
        else:
            print(f"❌ Connection test failed: {task_result.get('message')}")
        
        # Optionally run feed fetch task (commented out as it can take time)
        # print("Running OTX feed fetch task...")
        # result = fetch_otx_threat_feeds.delay()
        # task_result = result.get(timeout=300)  # 5 minute timeout
        # print(f"Feed fetch result: {task_result}")
        
    except Exception as e:
        print(f"❌ Error running Celery tasks: {e}")
        print("Make sure Celery worker is running!")

def show_configuration():
    """Show current OTX configuration."""
    print("\n=== Current OTX Configuration ===\n")
    
    print(f"OTX Enabled: {settings.OTX_SETTINGS.get('ENABLED', False)}")
    print(f"Fetch Interval: {settings.OTX_SETTINGS.get('FETCH_INTERVAL', 3600)} seconds")
    print(f"Batch Size: {settings.OTX_SETTINGS.get('BATCH_SIZE', 50)}")
    print(f"Max Age: {settings.OTX_SETTINGS.get('MAX_AGE_DAYS', 30)} days")
    print(f"Indicator Types: {', '.join(settings.OTX_SETTINGS.get('INDICATOR_TYPES', []))}")
    
    # Check Celery Beat schedule
    schedule = settings.CELERY_BEAT_SCHEDULE.get('fetch-otx-feeds', {})
    if schedule:
        print(f"Celery Schedule: Every {schedule.get('schedule', 'N/A')} seconds")
    else:
        print("Celery Schedule: Not configured")

def main():
    """Main demonstration function."""
    print("AlienVault OTX Integration Demo")
    print("=" * 50)
    
    # Setup and test connection
    if not setup_otx_environment():
        print("\n❌ OTX setup failed. Please configure your API key and try again.")
        return
    
    # Show current configuration
    show_configuration()
    
    # Demonstrate client functionality
    demonstrate_otx_client()
    
    # Demonstrate processing
    demonstrate_otx_processing()
    
    # Demonstrate Celery tasks (optional)
    print("\nWould you like to test Celery tasks? (y/n): ", end="")
    if input().lower().startswith('y'):
        run_celery_task_demo()
    
    print("\n✅ OTX integration demonstration completed!")
    print("\nNext steps:")
    print("1. Set up your OTX API key in environment variables")
    print("2. Run Django migrations: python manage.py migrate")
    print("3. Start Celery worker: celery -A threat_intel worker --loglevel=info")
    print("4. Start Celery Beat: celery -A threat_intel beat --loglevel=info")
    print("5. Test with: python manage.py test_otx")

if __name__ == "__main__":
    main()