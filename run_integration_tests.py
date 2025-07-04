#!/usr/bin/env python
"""
CRISP Integration Test Runner

This script runs comprehensive integration tests for the CRISP platform,
verifying that UserManagement and TrustManagement systems work together properly.
"""

import os
import sys
import django
import logging
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.settings.integrated')

# Setup Django
django.setup()

from django.core.management import call_command, execute_from_command_line
from django.test.utils import get_runner
from django.conf import settings


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"CRISP Integration Tests: {title}")
    print("=" * 70)


def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\nStep {step_num}: {description}")
    print("-" * 50)


def run_system_checks():
    """Run Django system checks"""
    print_step(1, "Running System Checks")
    
    try:
        call_command('check', verbosity=2)
        print("[SUCCESS] System checks passed")
        return True
    except Exception as e:
        print(f"[ERROR] System checks failed: {e}")
        return False


def create_test_database():
    """Create and migrate test database"""
    print_step(2, "Setting up Test Database")
    
    try:
        # Run migrations
        call_command('migrate', verbosity=2)
        print("[SUCCESS] Database setup completed")
        return True
    except Exception as e:
        print(f"[ERROR] Database setup failed: {e}")
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
                    defaults={
                        **level_data, 
                        'created_by': 'test_system',
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
                    print(f"   [SUCCESS] Created trust level: {trust_level.name} ({trust_level.numerical_value})")
                else:
                    # Ensure existing trust levels are active
                    if not trust_level.is_active:
                        trust_level.is_active = True
                        trust_level.save()
                        print(f"   [SUCCESS] Activated trust level: {trust_level.name} ({trust_level.numerical_value})")
                    else:
                        print(f"   [INFO] Trust level already exists: {trust_level.name} ({trust_level.numerical_value})")
        
        # Verify trust levels were created
        print("\n   [INFO] Verifying trust levels in database:")
        all_trust_levels = TrustLevel.objects.all()
        for tl in all_trust_levels:
            print(f"      - {tl.name}: {tl.numerical_value} (ID: {tl.id})")
        
        total_trust_levels = TrustLevel.objects.count()
        print(f"\n   [INFO] Total trust levels in database: {total_trust_levels}")
        
        if total_trust_levels == 0:
            print("   [WARNING] No trust levels found in database!")
            return False
        
        print("[SUCCESS] Test data created successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Test data creation failed: {e}")
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
            print(f"\n[INFO] Running tests for {test_app}...")
            call_command('test', test_app, verbosity=2)
        
        print("[SUCCESS] Integration tests completed")
        return True
    except Exception as e:
        print(f"[ERROR] Integration tests failed: {e}")
        import traceback
        traceback.print_exc()
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
        
        print("[INFO] Testing organization creation with trust setup...")
        
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
            print(f"   [SUCCESS] Created organization: {test_org.name}")
            
            # Verify admin user
            admin_user = User.objects.get(email='admin@testorg.edu')
            print(f"   [SUCCESS] Created admin user: {admin_user.email}")
            print(f"   [SUCCESS] User role: {admin_user.role}")
            print(f"   [SUCCESS] Is organization admin: {admin_user.is_organization_admin}")
            
        except Exception as e:
            print(f"   [ERROR] Organization creation test failed: {e}")
            return False
        
        print("\n[INFO] Testing trust relationship creation...")
        
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
            print(f"   [DEBUG] Checking for active trust levels...")
            all_trust_levels = TrustLevel.objects.all()
            active_trust_levels = TrustLevel.objects.filter(is_active=True)
            
            print(f"   [DEBUG] Total trust levels: {all_trust_levels.count()}")
            print(f"   [DEBUG] Active trust levels: {active_trust_levels.count()}")
            
            for tl in all_trust_levels:
                print(f"   [DEBUG] - {tl.name}: active={tl.is_active}, value={tl.numerical_value}")
            
            try:
                # Try to get the "Trusted Partners" level we created
                trust_level = TrustLevel.objects.get(name='Trusted Partners', is_active=True)
                trust_level_name = trust_level.name
                print(f"   [INFO] Using trust level: {trust_level_name}")
            except TrustLevel.DoesNotExist:
                # Fall back to any active trust level
                if active_trust_levels.exists():
                    trust_level_name = active_trust_levels.first().name
                    print(f"   [INFO] Using fallback trust level: {trust_level_name}")
                else:
                    print(f"   [ERROR] No active trust levels found!")
                    return False
            
            # Create trust relationship
            relationship = CRISPIntegrationService.create_trust_relationship(
                source_org=test_org,
                target_org=test_org_2,
                trust_level_name=trust_level_name,
                created_by_user=admin_user
            )
            
            print(f"   [SUCCESS] Created trust relationship: {relationship.id}")
            print(f"   [SUCCESS] Trust level: {relationship.trust_level.name}")
            
        except Exception as e:
            print(f"   [ERROR] Trust relationship creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("[SUCCESS] Manual integration scenarios completed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Manual integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_api_tests():
    """Run basic API endpoint tests"""
    print_step(6, "Running API Tests")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test basic endpoints
        endpoints = [
            ('/', 'Home page'),
            ('/admin/', 'Admin interface'),
        ]
        
        for url, description in endpoints:
            try:
                response = client.get(url)
                print(f"   [INFO] {description} ({url}): Status {response.status_code}")
            except Exception as e:
                print(f"   [WARNING] {description} ({url}): Error {e}")
        
        print("[SUCCESS] API tests completed")
        return True
        
    except Exception as e:
        print(f"[ERROR] API tests failed: {e}")
        return False


def generate_test_report():
    """Generate a test report"""
    print_step(7, "Generating Test Report")
    
    try:
        from apps.user_management.models import Organization
        from apps.trust_management.models import TrustLevel, TrustRelationship, TrustLog
        from django.contrib.auth import get_user_model
        from django.db import models
        
        User = get_user_model()
        
        print("\n[INFO] Integration Test Report")
        print("=" * 40)
        
        # Show counts
        print(f"Organizations: {Organization.objects.count()}")
        print(f"Users: {User.objects.count()}")
        print(f"Trust Levels: {TrustLevel.objects.count()}")
        print(f"Trust Relationships: {TrustRelationship.objects.count()}")
        print(f"Trust Logs: {TrustLog.objects.count()}")
        
        # Show user roles
        print("\nUser Roles:")
        for role, count in User.objects.values_list('role').annotate(count=models.Count('role')):
            print(f"  - {role}: {count}")
        
        # Show trust log summary
        print("\nTrust Log Summary:")
        from django.db import models
        log_summary = TrustLog.objects.values('action').annotate(count=models.Count('action'))
        for entry in log_summary:
            print(f"  - {entry['action']}: {entry['count']}")
        
        # Show organization summary
        print("\nOrganization Summary:")
        for org in Organization.objects.all():
            user_count = User.objects.filter(organization=org).count()
            print(f"  - {org.name}: {user_count} users")
        
        print("\n[SUCCESS] Test report generated")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    print_header("CRISP Integration Test Suite")
    
    # Log file setup
    log_file = project_root / 'integration.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    print(f"[INFO] Starting integration tests...")
    print(f"[INFO] Log file: {log_file}")
    print(f"[INFO] Database: {settings.DATABASES['default']['NAME']}")
    
    # Run all test phases
    test_phases = [
        ("System Checks", run_system_checks),
        ("Database Setup", create_test_database),
        ("Test Data Creation", create_test_data),
        ("Integration Tests", run_integration_tests),
        ("Manual Integration Tests", run_manual_integration_test),
        ("API Tests", run_api_tests),
        ("Test Report", generate_test_report),
    ]
    
    results = {}
    
    for phase_name, phase_func in test_phases:
        print(f"\n[INFO] Running {phase_name}...")
        try:
            result = phase_func()
            results[phase_name] = result
            if result:
                print(f"[SUCCESS] {phase_name} completed successfully")
            else:
                print(f"[ERROR] {phase_name} failed")
        except Exception as e:
            print(f"[ERROR] {phase_name} failed with exception: {e}")
            results[phase_name] = False
    
    # Print final summary
    print_header("Test Summary")
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"Tests completed: {success_count}/{total_count}")
    
    for phase_name, result in results.items():
        status = "[SUCCESS]" if result else "[FAILED]"
        print(f"{status} {phase_name}")
    
    if success_count == total_count:
        print("\n[SUCCESS] All integration tests passed!")
        return 0
    else:
        print(f"\n[ERROR] {total_count - success_count} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
