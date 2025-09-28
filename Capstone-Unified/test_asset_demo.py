#!/usr/bin/env python
"""
Quick test script to validate asset demo data functionality
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append('/mnt/c/Users/jadyn/CRISP/Capstone-Unified')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from core.models.models import Organization, AssetInventory, CustomAlert, Indicator
from core.user_management.models import CustomUser
from core.services.asset_alert_service import AssetBasedAlertService

def test_asset_demo_data():
    print("🧪 Testing Asset Demo Data Creation")
    print("=" * 50)

    try:
        # Test organization creation
        print("Creating test organization...")
        org = Organization.objects.create(
            name="Test Organization",
            description="Test organization for demo",
            organization_type="educational",
            domain="test.edu",
            is_publisher=True,
            is_verified=True,
            is_active=True,
            trust_metadata={'test': True}
        )
        print(f"✅ Organization created: {org.name}")

        # Test user creation
        print("Creating test user...")
        user = CustomUser.objects.create_user(
            username="test_user",
            email="test@test.edu",
            password="test123!",
            organization=org,
            role="BlueVisionAdmin",
            metadata={'test': True}
        )
        print(f"✅ User created: {user.username}")

        # Test asset creation
        print("Creating test asset...")
        asset = AssetInventory.objects.create(
            name="Test Web Server",
            asset_type="domain",
            asset_value="web.test.edu",
            description="Test web server asset",
            criticality="high",
            organization=org,
            created_by=user,
            alert_enabled=True,
            metadata={'test': True}
        )
        print(f"✅ Asset created: {asset.name}")

        # Test indicator creation
        print("Creating test indicator...")
        indicator = Indicator.objects.create(
            type="domain-name",
            value="malicious.test.edu",
            pattern="[domain-name:value = 'malicious.test.edu']",
            confidence=85,
            is_active=True,
            metadata={'test': True}
        )
        print(f"✅ Indicator created: {indicator.value}")

        # Test alert service
        print("Testing alert service...")
        alert_service = AssetBasedAlertService()

        # Test statistics
        stats = alert_service.get_alert_statistics(org)
        print(f"✅ Statistics retrieved: {stats}")

        # Test correlation
        alerts = alert_service._process_indicators_for_organization([indicator], org)
        print(f"✅ Correlation test complete: {len(alerts)} alerts generated")

        # Cleanup test data
        print("Cleaning up test data...")
        CustomAlert.objects.filter(organization=org).delete()
        asset.delete()
        indicator.delete()
        user.delete()
        org.delete()
        print("✅ Test data cleaned up")

        print("\n🎉 All tests passed! Asset demo data functionality is working correctly.")
        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_asset_demo_data()
    sys.exit(0 if success else 1)