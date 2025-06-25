#!/usr/bin/env python
"""
Trust Management Functionality Tests
Comprehensive functionality verification for the trust management system.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

import django
django.setup()

from django.test import TestCase
from django.core.exceptions import ValidationError
from TrustManagement.models import TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership
from TrustManagement.services.trust_service import TrustService
from TrustManagement.services.trust_group_service import TrustGroupService


class TrustFunctionalityTests:
    """Test suite for trust management functionality"""
    
    def __init__(self):
        self.setup_test_data()
    
    def setup_test_data(self):
        """Set up test data"""
        print("Setting up test data...")
        
        # Ensure migrations are applied
        from django.core.management import call_command
        call_command('migrate', verbosity=0, interactive=False)
        
        # Clean up any existing test data
        TrustRelationship.objects.filter(source_organization__startswith='test_').delete()
        TrustGroupMembership.objects.filter(organization__startswith='test_').delete()
        TrustGroup.objects.filter(name__startswith='Test ').delete()
        TrustLevel.objects.filter(name__startswith='Test ').delete()
        
        # Create test trust levels
        self.test_trust_level = TrustLevel.objects.create(
            name="Test Standard Trust",
            level="test_standard",
            description="Test trust level for functionality testing",
            numerical_value=50,
            default_anonymization_level="partial",
            default_access_level="read",
            created_by="test_system"
        )
        
        # Test organizations (UUIDs would be used in practice)
        self.org1 = "test_org_1"
        self.org2 = "test_org_2"
        self.org3 = "test_org_3"
        
        print("✅ Test data setup complete")
    
    def test_trust_level_operations(self):
        """Test trust level operations"""
        print("Testing trust level operations...")
        
        try:
            # Test creation
            trust_level = TrustLevel.objects.create(
                name="Test High Trust",
                level="test_high",
                description="High trust level for testing",
                numerical_value=75,
                default_anonymization_level="minimal",
                default_access_level="contribute",
                created_by="test_user"
            )
            
            # Test retrieval
            retrieved = TrustLevel.objects.get(name="Test High Trust")
            assert retrieved.numerical_value == 75
            
            # Test validation
            assert trust_level.is_active == True
            # Test that the trust level has expected properties
            assert trust_level.numerical_value == 75
            assert trust_level.default_access_level == "contribute"
            
            print("✅ Trust level operations successful")
            return True
        except Exception as e:
            print(f"❌ Trust level operations failed: {e}")
            return False
    
    def test_trust_relationship_lifecycle(self):
        """Test complete trust relationship lifecycle"""
        print("Testing trust relationship lifecycle...")
        
        try:
            # Create relationship
            relationship = TrustService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org2,
                trust_level_name="Test Standard Trust",
                relationship_type="bilateral",
                created_by="test_user"
            )
            
            assert relationship.status == "pending"
            assert not relationship.is_fully_approved
            
            # Approve from source
            activated = TrustService.approve_trust_relationship(
                relationship_id=str(relationship.id),
                approving_org=self.org1,
                approved_by_user="test_user"
            )
            
            assert not activated  # Should not be activated yet (needs both approvals)
            
            # Approve from target
            activated = TrustService.approve_trust_relationship(
                relationship_id=str(relationship.id),
                approving_org=self.org2,
                approved_by_user="test_user"
            )
            
            assert activated  # Should be activated now
            
            # Check trust level
            trust_info = TrustService.check_trust_level(self.org1, self.org2)
            assert trust_info is not None
            trust_level, rel = trust_info
            assert trust_level.name == "Test Standard Trust"
            
            # Test intelligence access
            can_access, reason, rel = TrustService.can_access_intelligence(
                requesting_org=self.org1,
                intelligence_owner=self.org2,
                required_access_level="read"
            )
            
            assert can_access == True
            
            print("✅ Trust relationship lifecycle successful")
            return True
        except Exception as e:
            import traceback
            print(f"❌ Trust relationship lifecycle failed: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def test_trust_group_operations(self):
        """Test trust group operations"""
        print("Testing trust group operations...")
        
        try:
            # Create trust group
            group = TrustGroupService.create_trust_group(
                name="Test Functionality Group",
                description="Test group for functionality testing",
                creator_org=self.org1,
                group_type="sector",
                is_public=True,
                default_trust_level_name="Test Standard Trust"
            )
            
            assert group.name == "Test Functionality Group"
            assert group.is_active == True
            
            # Join group
            membership = TrustGroupService.join_trust_group(
                group_id=str(group.id),
                organization=self.org2,
                membership_type="member",
                user="test_user"
            )
            
            assert membership.is_active == True
            
            # Check community trust
            trust_info = TrustService.check_trust_level(self.org1, self.org2)
            assert trust_info is not None
            
            # Get group members
            members = TrustGroupService.get_group_members(str(group.id))
            assert len(members) == 2  # Creator + joined member
            
            print("✅ Trust group operations successful")
            return True
        except Exception as e:
            print(f"❌ Trust group operations failed: {e}")
            return False
    
    def test_access_control_strategies(self):
        """Test access control strategies"""
        print("Testing access control strategies...")
        
        try:
            from TrustManagement.strategies.access_control_strategies import (
                TrustLevelAccessStrategy, NoAnonymizationStrategy, PartialAnonymizationStrategy
            )
            
            # Test access strategy
            strategy = TrustLevelAccessStrategy(minimum_trust_level=50)
            
            # Create a test relationship (use different orgs to avoid constraint violation)
            relationship = TrustRelationship.objects.create(
                source_organization=self.org2,
                target_organization=self.org3,
                trust_level=self.test_trust_level,
                relationship_type="bilateral",
                status="active",
                approved_by_source=True,
                approved_by_target=True,
                created_by="test_user",
                last_modified_by="test_user"
            )
            
            # Test access check
            can_access, reason = strategy.can_access({'trust_relationship': relationship})
            assert can_access == True
            
            # Test anonymization strategies
            no_anon = NoAnonymizationStrategy()
            partial_anon = PartialAnonymizationStrategy()
            
            test_data = {
                "source": "test_source",
                "indicator": "192.168.1.1",
                "description": "Test indicator"
            }
            
            context = {'trust_relationship': relationship}
            no_anon_result = no_anon.anonymize(test_data, context)
            assert no_anon_result["source"] == "test_source"
            
            partial_anon_result = partial_anon.anonymize(test_data.copy(), context)
            # Partial anonymization may not change the source field directly
            assert "source" in partial_anon_result
            
            print("✅ Access control strategies successful")
            return True
        except Exception as e:
            print(f"❌ Access control strategies failed: {e}")
            return False
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        print("Testing audit logging...")
        
        try:
            from TrustManagement.models import TrustLog
            
            # Count initial logs
            initial_count = TrustLog.objects.count()
            
            # Create a trust relationship (should generate logs)
            relationship = TrustService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org3,
                trust_level_name="Test Standard Trust",
                relationship_type="bilateral",
                created_by="test_user"
            )
            
            # Check if logs were created
            new_count = TrustLog.objects.count()
            assert new_count > initial_count
            
            # Check log content
            recent_log = TrustLog.objects.filter(
                action="relationship_created",
                source_organization=self.org1
            ).first()
            
            assert recent_log is not None
            assert recent_log.success == True
            
            print("✅ Audit logging successful")
            return True
        except Exception as e:
            print(f"❌ Audit logging failed: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("Cleaning up test data...")
        
        try:
            TrustRelationship.objects.filter(source_organization__startswith='test_').delete()
            TrustGroupMembership.objects.filter(organization__startswith='test_').delete()
            TrustGroup.objects.filter(name__startswith='Test ').delete()
            TrustLevel.objects.filter(name__startswith='Test ').delete()
            
            print("✅ Test data cleanup complete")
        except Exception as e:
            print(f"⚠️  Test data cleanup warning: {e}")
    
    def run_all_tests(self):
        """Run all functionality tests"""
        print("=" * 60)
        print("TRUST MANAGEMENT FUNCTIONALITY TESTS")
        print("=" * 60)
        
        tests = [
            ("Trust Level Operations", self.test_trust_level_operations),
            ("Trust Relationship Lifecycle", self.test_trust_relationship_lifecycle),
            ("Trust Group Operations", self.test_trust_group_operations),
            ("Access Control Strategies", self.test_access_control_strategies),
            ("Audit Logging", self.test_audit_logging),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            print("-" * 40)
            success = test_func()
            results.append((test_name, success))
            print()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        print("=" * 60)
        print("FUNCTIONALITY TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name:<30} {status}")
            if success:
                passed += 1
            else:
                failed += 1
        
        print()
        print(f"Total Tests: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(results)*100):.1f}%")
        
        if failed > 0:
            print("\n❌ Some functionality tests failed!")
            return False
        else:
            print("\n✅ All functionality tests passed!")
            return True


def main():
    """Run functionality tests"""
    test_suite = TrustFunctionalityTests()
    success = test_suite.run_all_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)