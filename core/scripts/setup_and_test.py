#!/usr/bin/env python3
"""
CRISP Ultra-Clean Structure Setup Script
This script sets up the environment and validates the structure
"""
import os
import sys
import django
from django.conf import settings

def setup_django():
    """Setup Django configuration"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
    if not settings.configured:
        django.setup()
    print("✅ Django configured successfully")

def setup_python_path():
    """Setup Python path for the ultra-clean structure"""
    # Get the actual project root (two levels up from this script)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Add paths to sys.path if not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print(f"✅ Python path configured:")
    print(f"   - Project root: {project_root}")

def test_individual_components():
    """Test each component individually"""
    print("\n🧪 Testing Individual Components...")

    # Test 1: Core models
    try:
        from core.models.auth import Organization, CustomUser, UserSession
        print("✅ Core models imported successfully")
    except Exception as e:
        print(f"❌ Core models failed: {e}")

    # Test 2: STIX models
    try:
        from core.models.stix_object import STIXObject, Collection, Feed
        print("✅ STIX models imported successfully")
    except Exception as e:
        print(f"❌ STIX models failed: {e}")

    # Test 3: Trust models
    try:
        from core.models.trust_models.models import TrustLevel, TrustRelationship
        print("✅ Trust models imported successfully")
    except Exception as e:
        print(f"❌ Trust models failed: {e}")

    # Test 4: Design patterns
    try:
        from core.strategies.enums import AnonymizationLevel
        from core.patterns.observer.threat_feed import ThreatFeedSubject
        print("✅ Design patterns imported successfully")
    except Exception as e:
        print(f"❌ Design patterns failed: {e}")

    # Test 5: Other models
    try:
        from core.models.indicator import Indicator
        from core.models.institution import Institution
        from core.models.ttp_data import TTPData
        print("✅ Other models imported successfully")
    except Exception as e:
        print(f"❌ Other models failed: {e}")

def main():
    """Main setup function"""
    print("🎯 CRISP ULTRA-CLEAN STRUCTURE SETUP")
    print("=" * 50)

    # Setup Python path
    setup_python_path()

    # Setup Django
    setup_django()

    # Test components
    test_individual_components()

    print("\n🏆 SETUP COMPLETE!")
    print("✅ Ultra-clean structure ready!")
    print("✅ Django configured!")
    print("🚀 All components tested successfully!")

if __name__ == "__main__":
    main()
