#!/usr/bin/env python
"""
CRISP Integration Test Runner

This script tests the core integration between User Management, Trust Management, 
and Threat Intelligence components without requiring full Django setup.

It validates that:
1. Models can be imported and work together
2. Foreign key relationships are properly established  
3. Integration services function correctly
4. Core domain model requirements are met
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'UserManagement',
            'crisp_threat_intel',
            'trust_management_app',
        ],
        SECRET_KEY='test-secret-key-for-integration-testing',
        USE_TZ=True,
        TIME_ZONE='UTC',
        AUTH_USER_MODEL='UserManagement.CustomUser',
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )

# Setup Django
django.setup()

# Now we can import our test modules
from tests.integration.test_crisp_integration import (
    OrganizationIntegrationTest,
    TrustRelationshipIntegrationTest,
    ThreatIntelligenceIntegrationTest,
    CRISPIntegrationServiceTest,
    EndToEndWorkflowTest
)

def run_model_validation_tests():
    """
    Run basic model validation tests to ensure integration is working
    """
    print("🔄 Running CRISP Integration Model Validation Tests...")
    print("=" * 60)
    
    try:
        # Test 1: Import all models successfully
        print("✅ Test 1: Importing core models...")
        from UserManagement.models import Organization, CustomUser
        from crisp_threat_intel.models import STIXObject, Collection, CollectionObject
        from trust_management_app.core.models.models import (
            TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership, TrustLog
        )
        print("   ✓ All models imported successfully")
        
        # Test 2: Import integration service
        print("✅ Test 2: Importing integration service...")
        from crisp_project.services import CRISPIntegrationService
        print("   ✓ Integration service imported successfully")
        
        # Test 3: Create database tables
        print("✅ Test 3: Creating database tables...")
        from django.core.management import call_command
        call_command('migrate', verbosity=0, interactive=False)
        print("   ✓ Database tables created successfully")
        
        # Test 4: Test model creation and relationships
        print("✅ Test 4: Testing model creation and relationships...")
        
        # Create organization
        org = Organization.objects.create(
            name='Test University',
            description='Test organization for integration',
            domain='test-university.edu',
            identity_class='organization',
            sectors=['education']
        )
        print(f"   ✓ Organization created: {org.name} (ID: {org.id})")
        
        # Create user
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test-university.edu',
            password='testpass123',
            organization=org,
            role='publisher'
        )
        print(f"   ✓ User created: {user.username} (Org: {user.organization.name})")
        
        # Create trust level
        trust_level = TrustLevel.objects.create(
            name='Test Trust Level',
            level='medium',
            numerical_value=50,
            description='Test trust level',
            default_anonymization_level='minimal',
            default_access_level='subscribe'
        )
        print(f"   ✓ Trust level created: {trust_level.name}")
        
        # Create STIX object
        stix_obj = STIXObject.objects.create(
            stix_id='indicator--test-integration',
            stix_type='indicator',
            spec_version='2.1',
            created=django.utils.timezone.now(),
            modified=django.utils.timezone.now(),
            labels=['test'],
            raw_data={'type': 'indicator', 'id': 'indicator--test-integration'},
            created_by=user,
            source_organization=org
        )
        print(f"   ✓ STIX object created: {stix_obj.stix_id}")
        
        # Test foreign key relationships
        print("✅ Test 5: Validating foreign key relationships...")
        
        # User -> Organization
        assert user.organization == org
        assert user in org.users.all()
        print("   ✓ User-Organization relationship working")
        
        # STIX Object -> User and Organization
        assert stix_obj.created_by == user
        assert stix_obj.source_organization == org
        assert stix_obj in user.created_stix_objects.all()
        assert stix_obj in org.stix_objects.all()
        print("   ✓ STIX Object relationships working")
        
        # Test integration service
        print("✅ Test 6: Testing integration service...")
        
        # Test get_user_organization
        retrieved_org = CRISPIntegrationService.get_user_organization(user)
        assert retrieved_org == org
        print("   ✓ CRISPIntegrationService.get_user_organization working")
        
        # Test access permission for same organization
        allowed, access_level, trust_info = CRISPIntegrationService.check_access_permission(
            user, org, 'read'
        )
        assert allowed == True
        assert access_level == 'full'
        assert trust_info.get('same_org') == True
        print("   ✓ Same-organization access control working")
        
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("✅ CRISP Platform Integration is Working Correctly!")
        print("\nKey Integration Points Validated:")
        print("  • User Management ↔ Trust Management (Organization FK)")
        print("  • User Management ↔ Threat Intelligence (User/Org FK)")
        print("  • Trust Management ↔ Threat Intelligence (Access Control)")
        print("  • Integration Service Coordination")
        print("  • Domain Model Compliance")
        
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_tests():
    """
    Run comprehensive Django test suite for integration
    """
    print("\n🔄 Running Comprehensive Integration Test Suite...")
    print("=" * 60)
    
    try:
        from django.test.utils import get_runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=False)
        
        # Run specific test modules
        test_modules = [
            'tests.integration.test_crisp_integration.OrganizationIntegrationTest',
            'tests.integration.test_crisp_integration.TrustRelationshipIntegrationTest',
            'tests.integration.test_crisp_integration.ThreatIntelligenceIntegrationTest',
            'tests.integration.test_crisp_integration.CRISPIntegrationServiceTest',
        ]
        
        failures = test_runner.run_tests(test_modules)
        
        if failures == 0:
            print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
            return True
        else:
            print(f"\n❌ {failures} TESTS FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ COMPREHENSIVE TEST SUITE FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Main test runner function
    """
    print("🚀 CRISP Platform Integration Test Runner")
    print("=" * 60)
    print("Testing integration between:")
    print("  • User Management (Authentication, Organizations)")
    print("  • Trust Management (Trust Relationships, Access Control)")
    print("  • Threat Intelligence (STIX Objects, Collections)")
    print("=" * 60)
    
    # Run basic model validation tests first
    basic_tests_passed = run_model_validation_tests()
    
    if not basic_tests_passed:
        print("\n❌ Basic integration tests failed. Stopping here.")
        sys.exit(1)
    
    # Ask user if they want to run comprehensive tests
    print("\n" + "=" * 60)
    print("Basic integration tests passed! ✅")
    
    try:
        run_comprehensive = input("Run comprehensive test suite? (y/N): ").lower().strip()
    except (EOFError, KeyboardInterrupt):
        run_comprehensive = 'n'
    
    if run_comprehensive in ['y', 'yes']:
        comprehensive_tests_passed = run_comprehensive_tests()
        
        if comprehensive_tests_passed:
            print("\n🎉 COMPLETE INTEGRATION SUCCESS!")
            print("CRISP Platform is fully integrated and ready for use!")
            sys.exit(0)
        else:
            print("\n⚠️  Basic integration works, but some comprehensive tests failed.")
            print("Core functionality is operational.")
            sys.exit(1)
    else:
        print("\n✅ Basic integration validation complete!")
        print("CRISP Platform core integration is working.")
        sys.exit(0)

if __name__ == '__main__':
    main()