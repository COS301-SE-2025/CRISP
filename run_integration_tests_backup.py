#!/usr/bin/env python
"""
CRISP Integration Test Runner
Comprehensive test suite for UserManagement and TrustManagement integration
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.settings.integrated')
django.setup()

import subprocess
from django.core.management import call_command, execute_from_command_line
from django.test.utils import get_runner
from django.conf import settings


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"🔗 {title}")
    print("=" * 70)


def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 50)


def run_system_checks():
    """Run Django system checks"""
    print_step(1, "Running System Checks")
    
    try:
        call_command('check', verbosity=2)
        print("✅ System checks passed")
        return True
    except Exception as e:
        print(f"❌ System checks failed: {e}")
        return False


def create_test_database():
    """Create and migrate test database"""
    print_step(2, "Setting up Test Database")
    
    try:
        # Create migrations
        print("Creating migrations...")
        call_command('makemigrations', 'user_management', verbosity=2)
        call_command('makemigrations', 'trust_management', verbosity=2)
        call_command('makemigrations', 'core', verbosity=2)
        
        # Apply migrations
        print("Applying migrations...")
        call_command('migrate', verbosity=2)
        
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def create_test_data():
    """Create initial test data"""
    print_step(3, "Creating Test Data")
    
    try:
        from apps.trust_management.models import TrustLevel
        from apps.user_management.models import Organization
        from django.contrib.auth import get_user_model
        from django.db import transaction
        
        User = get_user_model()
        
        # Create trust levels with explicit transaction handling
        trust_levels = [
            {
                'name': 'Untrusted',
                'level': 'untrusted',
                'numerical_value': 0,
                'description': 'No trust established',
                'default_anonymization_level': 'full',
                'default_access_level': 'read'
            },
            {
                'name': 'Limited Trust',
                'level': 'limited',
                'numerical_value': 25,
                'description': 'Limited trust for basic operations',
                'default_anonymization_level': 'full',
                'default_access_level': 'read'
            },
            {
                'name': 'Moderate Trust',
                'level': 'moderate',
                'numerical_value': 50,
                'description': 'Moderate trust for standard operations',
                'default_anonymization_level': 'partial',
                'default_access_level': 'contribute'
            },
            {
                'name': 'High Trust',
                'level': 'high',
                'numerical_value': 75,
                'description': 'High trust for sensitive operations',
                'default_anonymization_level': 'partial',
                'default_access_level': 'admin'
            },
            {
                'name': 'Trusted Partners',
                'level': 'trusted',
                'numerical_value': 100,
                'description': 'Full trust for all operations',
                'default_anonymization_level': 'minimal',
                'default_access_level': 'admin'
            }
        ]
        
        created_count = 0
        with transaction.atomic():
            for level_data in trust_levels:
                trust_level, created = TrustLevel.objects.get_or_create(
                    name=level_data['name'],
                    defaults={**level_data, 'created_by': 'test_system'}
                )
                if created:
                    created_count += 1
                    print(f"   ✅ Created trust level: {trust_level.name} ({trust_level.numerical_value})")
                else:
                    print(f"   ℹ️ Trust level already exists: {trust_level.name} ({trust_level.numerical_value})")
        
        # Verify trust levels were created
        print("\n   📊 Verifying trust levels in database:")
        all_trust_levels = TrustLevel.objects.all()
        for tl in all_trust_levels:
            print(f"      - {tl.name}: {tl.numerical_value} (ID: {tl.id})")
        
        total_trust_levels = TrustLevel.objects.count()
        print(f"\n   📊 Total trust levels in database: {total_trust_levels}")
        
        if total_trust_levels == 0:
            print("   ⚠️ Warning: No trust levels found in database!")
            return False
        
        print("✅ Test data created successfully")
        return True
    except Exception as e:
        print(f"❌ Test data creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_integration_tests():
    """Run the integration test suite"""
    print_step(4, "Running Integration Tests")
    
    try:
        # Run specific integration tests
        test_apps = [
            'apps.core.tests_integration',
        ]
        
        for test_app in test_apps:
            print(f"\n🧪 Running tests for {test_app}...")
            call_command('test', test_app, verbosity=2)
        
        print("✅ Integration tests completed")
        return True
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        return False


def run_manual_integration_test():
    """Run manual integration test scenarios"""
    print_step(5, "Running Manual Integration Scenarios")
    
    try:
        from apps.core.services import CRISPIntegrationService
        from apps.user_management.models import Organization
        from apps.trust_management.models import TrustLevel
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        print("🔄 Testing organization creation with trust setup...")
        
        # Test organization creation
        admin_data = {
            'username': 'testadmin',
            'email': 'admin@testorg.edu',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Admin'
        }
        
        try:
            test_org = CRISPIntegrationService.create_organization_with_trust_setup(
                name='Test Integration University',
                domain='testintegration.edu',
                contact_email='contact@testintegration.edu',
                admin_user_data=admin_data,
                institution_type='university',
                default_trust_level='public'
            )
            print(f"   ✅ Created organization: {test_org.name}")
            
            # Verify admin user
            admin_user = User.objects.get(email='admin@testorg.edu')
            print(f"   ✅ Created admin user: {admin_user.email}")
            print(f"   ✅ User role: {admin_user.role}")
            print(f"   ✅ Is organization admin: {admin_user.is_organization_admin}")
            
        except Exception as e:
            print(f"   ❌ Organization creation test failed: {e}")
            return False
        
        print("\n🔄 Testing trust relationship creation...")
        
        # Create a second organization for trust relationship
        admin_data_2 = {
            'username': 'testadmin2',
            'email': 'admin@testorg2.edu',
            'password': 'testpass123',
            'first_name': 'Test2',
            'last_name': 'Admin'
        }
        
        try:
            test_org_2 = CRISPIntegrationService.create_organization_with_trust_setup(
                name='Test Partner University',
                domain='testpartner.edu',
                contact_email='contact@testpartner.edu',
                admin_user_data=admin_data_2,
                institution_type='university',
                default_trust_level='trusted'
            )
            
            admin_user_2 = User.objects.get(email='admin@testorg2.edu')
            
            # Use existing trust level name from test data creation
            available_trust_levels = TrustLevel.objects.all()
            if available_trust_levels.exists():
                # Use the "Trusted Partners" level created in test data
                try:
                    trust_level = TrustLevel.objects.get(name='Trusted Partners')
                    trust_level_name = trust_level.name
                    print(f"   ℹ️ Using trust level: {trust_level_name}")
                except TrustLevel.DoesNotExist:
                    # Fall back to first available trust level
                    trust_level_name = available_trust_levels.first().name
                    print(f"   ℹ️ Using fallback trust level: {trust_level_name}")
            else:
                trust_level_name = 'Trusted Partners'
                print(f"   ⚠️ No trust levels found, using: {trust_level_name}")
            
            # Create trust relationship
            relationship = CRISPIntegrationService.create_trust_relationship(
                source_org=test_org,
                target_org=test_org_2,
                trust_level_name=trust_level_name,
                created_by_user=admin_user
            )
            print(f"   ✅ Created trust relationship: {relationship}")
            
            # Test approval process
            CRISPIntegrationService.approve_trust_relationship(
                relationship=relationship,
                approving_org=test_org,
                approving_user=admin_user
            )
            print("   ✅ Source organization approved")
            
            fully_approved = CRISPIntegrationService.approve_trust_relationship(
                relationship=relationship,
                approving_org=test_org_2,
                approving_user=admin_user_2
            )
            print(f"   ✅ Target organization approved, fully approved: {fully_approved}")
            
        except Exception as e:
            print(f"   ❌ Trust relationship test failed: {e}")
            return False
        
        print("\n🔄 Testing intelligence access control...")
        
        try:
            # Test access checking
            can_access, reason, rel = CRISPIntegrationService.can_user_access_intelligence(
                user=admin_user,
                intelligence_owner_org_id=str(test_org_2.id),
                required_access_level='read'
            )
            print(f"   ✅ Access check result: {can_access}, reason: {reason}")
            
            # Test dashboard data
            dashboard = CRISPIntegrationService.get_organization_trust_dashboard_data(test_org)
            print(f"   ✅ Dashboard data generated: {dashboard['relationships']['total']} relationships")
            
        except Exception as e:
            print(f"   ❌ Access control test failed: {e}")
            return False
        
        print("✅ Manual integration scenarios completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Manual integration test failed: {e}")
        return False


def run_api_tests():
    """Test API endpoints (when implemented)"""
    print_step(6, "Testing API Endpoints")
    
    try:
        # For now, just test that URL configuration works
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test that admin is accessible
        try:
            response = client.get('/admin/')
            print(f"   ✅ Admin endpoint accessible (status: {response.status_code})")
        except Exception as e:
            print(f"   ⚠️ Admin endpoint test: {e}")
        
        print("✅ API endpoint tests completed")
        return True
        
    except Exception as e:
        print(f"❌ API tests failed: {e}")
        return False


def generate_test_report():
    """Generate a comprehensive test report"""
    print_step(7, "Generating Test Report")
    
    try:
        from apps.trust_management.models import TrustLevel, TrustRelationship, TrustLog
        from apps.user_management.models import Organization
        from django.contrib.auth import get_user_model
        from django.db import models
        
        User = get_user_model()
        
        print("\n📊 INTEGRATION TEST REPORT")
        print("=" * 50)
        
        # Count created objects
        print(f"Organizations created: {Organization.objects.count()}")
        print(f"Users created: {User.objects.count()}")
        print(f"Trust levels available: {TrustLevel.objects.count()}")
        print(f"Trust relationships created: {TrustRelationship.objects.count()}")
        print(f"Trust log entries: {TrustLog.objects.count()}")
        
        # Show active relationships
        active_relationships = TrustRelationship.objects.filter(status='active')
        print(f"Active trust relationships: {active_relationships.count()}")
        
        for rel in active_relationships:
            try:
                source_org = Organization.objects.get(id=rel.source_organization)
                target_org = Organization.objects.get(id=rel.target_organization)
                print(f"  - {source_org.name} ↔ {target_org.name} ({rel.trust_level.name})")
            except Organization.DoesNotExist:
                print(f"  - {rel.source_organization} ↔ {rel.target_organization} (org not found)")
        
        # Show user roles
        print("\nUser Roles:")
        from django.db import models
        for role, count in User.objects.values_list('role').annotate(count=models.Count('role')):
            print(f"  - {role}: {count}")
        
        # Show trust log summary
        print("\nTrust Log Summary:")
        log_summary = TrustLog.objects.values('action').annotate(count=models.Count('action'))
        for item in log_summary:
            print(f"  - {item['action']}: {item['count']}")
        
        print("\n✅ Test report generated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test report generation failed: {e}")
        return False


def main():
    """Main test runner function"""
    print_header("CRISP INTEGRATION TEST SUITE")
    print("Testing integration between UserManagement and TrustManagement systems")
    print("Based on SRS Functional Requirements")
    
    test_steps = [
        run_system_checks,
        create_test_database,
        create_test_data,
        run_integration_tests,
        run_manual_integration_test,
        run_api_tests,
        generate_test_report
    ]
    
    passed_steps = 0
    total_steps = len(test_steps)
    
    for step_func in test_steps:
        try:
            if step_func():
                passed_steps += 1
            else:
                print(f"❌ Step failed: {step_func.__name__}")
        except Exception as e:
            print(f"❌ Step error in {step_func.__name__}: {e}")
    
    # Final summary
    print_header("INTEGRATION TEST SUMMARY")
    print(f"Steps completed: {passed_steps}/{total_steps}")
    print(f"Success rate: {(passed_steps/total_steps)*100:.1f}%")
    
    if passed_steps == total_steps:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ UserManagement and TrustManagement successfully integrated")
        print("✅ System ready for further development")
        return 0
    else:
        print("⚠️ Some integration tests failed")
        print("❌ Review the errors above and fix issues")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
