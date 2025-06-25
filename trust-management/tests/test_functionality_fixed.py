"""
Trust Management Functionality Tests

These tests verify core functionality of the trust management system.
"""

import os
import sys
import uuid
import django
from pathlib import Path

# Setup Django before importing anything else
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrustManagement.settings')

django.setup()

from TrustManagement.models import TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership, TrustLog
from TrustManagement.services.trust_service import TrustService
from TrustManagement.services.trust_group_service import TrustGroupService


class TrustFunctionalityTest:
    """Test case for trust management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        print("Setting up test data...")
        
        # Create test trust levels
        self.test_trust_level = TrustLevel.objects.create(
            name="Test Standard Trust",
            level="medium",
            description="Standard trust level for functionality testing",
            numerical_value=50,
            default_anonymization_level="partial",
            default_access_level="subscribe",
            created_by="test_user"
        )
        
        self.high_trust_level = TrustLevel.objects.create(
            name="Test High Trust",
            level="high",
            description="High trust level for functionality testing",
            numerical_value=75,
            default_anonymization_level="minimal",
            default_access_level="contribute",
            created_by="test_user"
        )
        
        # Create test organizations
        self.org1 = str(uuid.uuid4())
        self.org2 = str(uuid.uuid4())
        self.org3 = str(uuid.uuid4())
        
        print("✅ Test data setup complete")
    
    def tearDown(self):
        """Clean up test data."""
        print("Cleaning up test data...")
        
        # Clean up in reverse order of dependencies
        TrustLog.objects.all().delete()
        TrustGroupMembership.objects.all().delete()
        TrustRelationship.objects.all().delete()
        TrustGroup.objects.all().delete()
        TrustLevel.objects.filter(name__startswith="Test").delete()
        
        print("✅ Test data cleanup complete")
    
    def test_trust_level_operations(self):
        """Test trust level operations"""
        print("Testing trust level operations...")
        
        try:
            # Test trust level creation and properties
            trust_level = TrustLevel.objects.get(name="Test Standard Trust")
            assert trust_level.level == "medium"
            assert trust_level.numerical_value == 50
            assert trust_level.default_anonymization_level == "partial"
            assert trust_level.default_access_level == "subscribe"
            
            # Test high trust level
            high_trust = TrustLevel.objects.get(name="Test High Trust")
            assert high_trust.level == "high"
            assert high_trust.numerical_value == 75
            assert high_trust.default_anonymization_level == "minimal"
            assert high_trust.default_access_level == "contribute"
            
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
            traceback.print_exc()
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
                default_trust_level_name="Test Standard Trust",
                created_by="test_user"
            )
            
            assert group.name == "Test Functionality Group"
            assert group.group_type == "sector"
            assert group.created_by == "test_user"
            
            # Check membership was created for creator
            membership = TrustGroupMembership.objects.get(
                trust_group=group,
                organization=self.org1
            )
            assert membership.membership_type == "administrator"
            assert membership.is_active == True
            
            # Join group with another organization
            membership_result = TrustGroupService.join_trust_group(
                group_id=str(group.id),
                organization=self.org2,
                membership_type="member",
                user="test_user"
            )
            
            assert membership_result is not None
            
            # Check membership was created
            membership = TrustGroupMembership.objects.get(
                trust_group=group,
                organization=self.org2
            )
            assert membership.membership_type == "member"
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
                'type': 'indicator',
                'pattern': "[network-traffic:src_ref.value = '192.168.1.100']",
                'x_attribution': 'Test Organization'
            }
            
            # Test no anonymization
            no_anon_result = no_anon.anonymize(test_data, {})
            assert 'x_attribution' in no_anon_result
            assert no_anon_result['x_attribution'] == 'Test Organization'
            
            # Test partial anonymization
            partial_result = partial_anon.anonymize(test_data, {})
            assert 'x_attribution' not in partial_result  # Should be removed
            assert 'xxx' in partial_result['pattern']  # IP should be anonymized
            
            print("✅ Access control strategies successful")
            return True
        except Exception as e:
            print(f"❌ Access control strategies failed: {e}")
            return False
    
    def test_audit_logging(self):
        """Test audit logging"""
        print("Testing audit logging...")
        
        try:
            initial_count = TrustLog.objects.count()
            
            # Perform operations that should be logged
            relationship = TrustService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org3,  # Use org3 to avoid conflicts
                trust_level_name="Test Standard Trust",
                relationship_type="bilateral",
                created_by="audit_test_user"
            )
            
            # Approve relationship (should generate more logs)
            TrustService.approve_trust_relationship(
                relationship_id=str(relationship.id),
                approving_org=self.org1,
                approved_by_user="audit_test_user"
            )
            
            # Check that logs were created
            final_count = TrustLog.objects.count()
            assert final_count > initial_count
            
            # Check log entries exist
            logs = TrustLog.objects.filter(user="audit_test_user")
            assert logs.count() > 0
            
            print("✅ Audit logging successful")
            return True
        except Exception as e:
            print(f"❌ Audit logging failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all functionality tests."""
        print("============================================================")
        print("TRUST MANAGEMENT FUNCTIONALITY TESTS")
        print("============================================================")
        print()
        
        tests = [
            ("Trust Level Operations", self.test_trust_level_operations),
            ("Trust Relationship Lifecycle", self.test_trust_relationship_lifecycle),
            ("Trust Group Operations", self.test_trust_group_operations),
            ("Access Control Strategies", self.test_access_control_strategies),
            ("Audit Logging", self.test_audit_logging),
        ]
        
        results = {}
        
        for test_name, test_method in tests:
            print(f"{test_name}:")
            print("----------------------------------------")
            success = test_method()
            results[test_name] = success
            print()
        
        print("============================================================")
        print("FUNCTIONALITY TEST SUMMARY")
        print("============================================================")
        
        passed = 0
        total = len(tests)
        
        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name:<30} {status}")
            if success:
                passed += 1
        
        print()
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print()
        
        if passed == total:
            print("✅ All functionality tests passed!")
            return True
        else:
            print("❌ Some functionality tests failed!")
            return False


def main():
    """Main test runner."""
    test = TrustFunctionalityTest()
    
    try:
        test.setUp()
        success = test.run_all_tests()
        return success
    finally:
        test.tearDown()


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)