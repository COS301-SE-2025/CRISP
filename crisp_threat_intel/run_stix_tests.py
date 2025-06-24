#!/usr/bin/env python3
"""
Comprehensive STIX Test Runner
Runs all STIX-related tests including version compatibility, validation, and integration tests.
"""

import os
import sys
import unittest
import time
from datetime import datetime

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')

import django
django.setup()


def run_stix_test_suite():
    """Run comprehensive STIX test suite."""
    print("="*80)
    print("CRISP THREAT INTELLIGENCE PLATFORM - COMPREHENSIVE STIX TEST SUITE")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test modules to run
    test_modules = [
        'tests.test_stix_version_compatibility',
        'tests.test_stix_object_creation', 
        'tests.test_stix_bundle_handling',
        'tests.test_comprehensive_stix_suite'
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for module_name in test_modules:
        print(f"🧪 Running {module_name}...")
        print("-" * 60)
        
        try:
            # Load test module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(module_name)
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            # Update counters
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            
            # Print module summary
            module_success = len(result.failures) == 0 and len(result.errors) == 0
            status = "✅ PASSED" if module_success else "❌ FAILED"
            print(f"\n{module_name}: {status}")
            print(f"  Tests run: {result.testsRun}")
            print(f"  Failures: {len(result.failures)}")
            print(f"  Errors: {len(result.errors)}")
            print()
            
        except Exception as e:
            print(f"❌ ERROR loading {module_name}: {e}")
            total_errors += 1
            print()
    
    # Final summary
    print("="*80)
    print("STIX TEST SUITE SUMMARY")
    print("="*80)
    print(f"Total Tests Run: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n✅ ALL STIX TESTS PASSED!")
        status_code = 0
    else:
        print(f"\n❌ {total_failures + total_errors} TESTS FAILED!")
        status_code = 1
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return status_code


def run_quick_stix_validation():
    """Run quick STIX validation test to ensure basic functionality works."""
    print("\n🔍 Running Quick STIX Validation Test...")
    print("-" * 60)
    
    try:
        from crisp_threat_intel.factories.stix_factory import STIXObjectFactory
        from crisp_threat_intel.validators.stix_validators import STIXValidator
        
        # Test STIX 2.0 and 2.1 object creation
        test_cases = [
            ('indicator', {'pattern': "[domain-name:value = 'test.com']", 'labels': ['malicious-activity']}, "2.0"),
            ('indicator', {'pattern': "[domain-name:value = 'test.com']", 'labels': ['malicious-activity']}, "2.1"),
            ('malware', {'name': 'Test Malware', 'labels': ['trojan']}, "2.0"),
            ('malware', {'name': 'Test Malware', 'malware_types': ['trojan'], 'is_family': False}, "2.1"),
        ]
        
        success_count = 0
        for obj_type, data, spec_version in test_cases:
            try:
                # Create object
                obj = STIXObjectFactory.create_object(obj_type, data, spec_version)
                
                # Validate object
                is_valid, errors = STIXValidator.validate_stix_object(obj, spec_version)
                
                if is_valid:
                    print(f"  ✅ {obj_type} (STIX {spec_version}): Created and validated")
                    success_count += 1
                else:
                    print(f"  ❌ {obj_type} (STIX {spec_version}): Validation failed - {errors}")
                    
            except Exception as e:
                print(f"  ❌ {obj_type} (STIX {spec_version}): Creation failed - {e}")
        
        print(f"\nQuick validation: {success_count}/{len(test_cases)} tests passed")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Quick validation failed: {e}")
        return False


def main():
    """Main function."""
    print("CRISP Threat Intelligence Platform - STIX Testing")
    print("Running comprehensive STIX 2.0/2.1 compatibility and validation tests...")
    print()
    
    # Run quick validation first
    quick_success = run_quick_stix_validation()
    
    if not quick_success:
        print("\n❌ Quick validation failed! Check STIX infrastructure.")
        return 1
    
    print("\n✅ Quick validation passed! Running full test suite...")
    
    # Run full test suite
    return run_stix_test_suite()


if __name__ == '__main__':
    sys.exit(main())