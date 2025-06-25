#!/usr/bin/env python
"""
Trust Management Comprehensive Test Suite
Tests integration scenarios and edge cases.
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
from django.db import transaction
from TrustManagement.models import *
from TrustManagement.services.trust_service import TrustService
from TrustManagement.services.trust_group_service import TrustGroupService
from TrustManagement.strategies.access_control_strategies import *


class ComprehensiveTestSuite:
    """Comprehensive test suite for trust management"""
    
    def __init__(self):
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Set up comprehensive test environment"""
        print("Setting up comprehensive test environment...")
        
        # Ensure migrations are applied
        from django.core.management import call_command
        call_command('migrate', verbosity=0, interactive=False)
        
        # Clean up any existing test data
        self.cleanup_all_test_data()
        
        # Create multiple trust levels
        self.trust_levels = {
            'no_trust': TrustLevel.objects.create(
                name="Test No Trust",
                level="no_trust",
                description="No trust level for testing",
                numerical_value=0,
                default_anonymization_level="full",
                default_access_level="none",
                created_by="test_system"
            ),
            'basic': TrustLevel.objects.create(
                name="Test Basic Trust",
                level="basic",
                description="Basic trust level for testing",
                numerical_value=25,
                default_anonymization_level="full",
                default_access_level="read",
                created_by="test_system"
            ),
            'standard': TrustLevel.objects.create(
                name="Test Standard Trust",
                level="standard",
                description="Standard trust level for testing",
                numerical_value=50,
                default_anonymization_level="partial",
                default_access_level="subscribe",
                created_by="test_system"
            ),
            'high': TrustLevel.objects.create(
                name="Test High Trust",
                level="high",
                description="High trust level for testing",
                numerical_value=75,
                default_anonymization_level="minimal",
                default_access_level="contribute",
                created_by="test_system"
            ),
            'complete': TrustLevel.objects.create(
                name="Test Complete Trust",
                level="complete",
                description="Complete trust level for testing",
                numerical_value=100,
                default_anonymization_level="none",
                default_access_level="full",
                created_by="test_system"
            )
        }
        
        # Create test organizations
        self.orgs = {
            'university_a': 'test_university_a',
            'university_b': 'test_university_b',
            'government_a': 'test_government_a',
            'private_a': 'test_private_a',
            'private_b': 'test_private_b',
            'research_lab': 'test_research_lab'
        }
        
        print("✅ Comprehensive test environment setup complete")
    
    def test_complex_trust_scenarios(self):
        """Test complex trust relationship scenarios"""
        print("Testing complex trust scenarios...")
        
        try:
            # Scenario 1: Multi-level trust chain
            rel1 = TrustService.create_trust_relationship(
                source_org=self.orgs['university_a'],
                target_org=self.orgs['government_a'],
                trust_level_name="Test High Trust",
                relationship_type="bilateral",
                created_by="test_admin"
            )
            
            rel2 = TrustService.create_trust_relationship(
                source_org=self.orgs['government_a'],
                target_org=self.orgs['private_a'],
                trust_level_name="Test Standard Trust",
                relationship_type="bilateral",
                created_by="test_admin"
            )
            
            # Approve relationships
            TrustService.approve_trust_relationship(str(rel1.id), self.orgs['university_a'], "test_user")
            TrustService.approve_trust_relationship(str(rel1.id), self.orgs['government_a'], "test_user")
            
            TrustService.approve_trust_relationship(str(rel2.id), self.orgs['government_a'], "test_user")
            TrustService.approve_trust_relationship(str(rel2.id), self.orgs['private_a'], "test_user")
            
            # Test direct trust
            trust_info = TrustService.check_trust_level(self.orgs['university_a'], self.orgs['government_a'])
            assert trust_info is not None
            
            # Test no transitive trust (university_a -> private_a)
            trust_info = TrustService.check_trust_level(self.orgs['university_a'], self.orgs['private_a'])
            assert trust_info is None
            
            print("✅ Complex trust scenarios successful")
            return True
        except Exception as e:
            print(f"❌ Complex trust scenarios failed: {e}")
            return False
    
    def test_community_trust_groups(self):
        """Test complex community trust group scenarios"""
        print("Testing community trust groups...")
        
        try:
            # Create educational sector group
            edu_group = TrustGroupService.create_trust_group(
                name="Test Educational Sector",
                description="Educational institutions trust group",
                creator_org=self.orgs['university_a'],
                group_type="sector",
                is_public=True,
                default_trust_level_name="Test Standard Trust"
            )
            
            # Create research collaboration group
            research_group = TrustGroupService.create_trust_group(
                name="Test Research Collaboration",
                description="Research collaboration trust group",
                creator_org=self.orgs['research_lab'],
                group_type="project",
                is_public=False,
                requires_approval=True,
                default_trust_level_name="Test High Trust"
            )
            
            # Join groups
            TrustGroupService.join_trust_group(
                group_id=str(edu_group.id),
                organization=self.orgs['university_b'],
                membership_type="member",
                user="test_user"
            )
            
            TrustGroupService.join_trust_group(
                group_id=str(research_group.id),
                organization=self.orgs['university_a'],
                membership_type="member",
                user="test_user"
            )
            
            # Test community trust between universities
            trust_info = TrustService.check_trust_level(self.orgs['university_a'], self.orgs['university_b'])
            assert trust_info is not None
            trust_level, relationship = trust_info
            assert relationship.relationship_type == "community"
            
            # Test research group trust
            trust_info = TrustService.check_trust_level(self.orgs['research_lab'], self.orgs['university_a'])
            assert trust_info is not None
            trust_level, relationship = trust_info
            assert trust_level.name == "Test High Trust"
            
            print("✅ Community trust groups successful")
            return True
        except Exception as e:
            print(f"❌ Community trust groups failed: {e}")
            return False
    
    def test_access_control_hierarchies(self):
        """Test complex access control scenarios"""
        print("Testing access control hierarchies...")
        
        try:
            # Create relationships with different trust levels
            relationships = []
            
            # High trust relationship
            rel_high = TrustService.create_trust_relationship(
                source_org=self.orgs['government_a'],
                target_org=self.orgs['private_a'],
                trust_level_name="Test High Trust",
                relationship_type="bilateral",
                created_by="test_admin"
            )
            TrustService.approve_trust_relationship(str(rel_high.id), self.orgs['government_a'], "test_user")
            TrustService.approve_trust_relationship(str(rel_high.id), self.orgs['private_a'], "test_user")
            
            # Basic trust relationship
            rel_basic = TrustService.create_trust_relationship(
                source_org=self.orgs['private_a'],
                target_org=self.orgs['private_b'],
                trust_level_name="Test Basic Trust",
                relationship_type="bilateral",
                created_by="test_admin"
            )
            TrustService.approve_trust_relationship(str(rel_basic.id), self.orgs['private_a'], "test_user")
            TrustService.approve_trust_relationship(str(rel_basic.id), self.orgs['private_b'], "test_user")
            
            # Test access levels
            can_access_read_high, _, _ = TrustService.can_access_intelligence(
                requesting_org=self.orgs['government_a'],
                intelligence_owner=self.orgs['private_a'],
                required_access_level="read"
            )
            assert can_access_read_high == True
            
            can_access_contribute_high, _, _ = TrustService.can_access_intelligence(
                requesting_org=self.orgs['government_a'],
                intelligence_owner=self.orgs['private_a'],
                required_access_level="contribute"
            )
            assert can_access_contribute_high == True
            
            can_access_contribute_basic, _, _ = TrustService.can_access_intelligence(
                requesting_org=self.orgs['private_a'],
                intelligence_owner=self.orgs['private_b'],
                required_access_level="contribute"
            )
            assert can_access_contribute_basic == False
            
            can_access_read_basic, _, _ = TrustService.can_access_intelligence(
                requesting_org=self.orgs['private_a'],
                intelligence_owner=self.orgs['private_b'],
                required_access_level="read"
            )
            assert can_access_read_basic == True
            
            print("✅ Access control hierarchies successful")
            return True
        except Exception as e:
            print(f"❌ Access control hierarchies failed: {e}")
            return False
    
    def test_temporal_trust_relationships(self):
        """Test temporal aspects of trust relationships"""
        print("Testing temporal trust relationships...")
        
        try:
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # Create time-bounded relationship
            future_expiry = timezone.now() + timedelta(days=30)
            past_expiry = timezone.now() - timedelta(days=1)
            
            # Valid relationship
            rel_valid = TrustService.create_trust_relationship(
                source_org=self.orgs['university_a'],
                target_org=self.orgs['research_lab'],
                trust_level_name="Test Standard Trust",
                relationship_type="bilateral",
                created_by="test_admin",
                valid_until=future_expiry
            )
            TrustService.approve_trust_relationship(str(rel_valid.id), self.orgs['university_a'], "test_user")
            TrustService.approve_trust_relationship(str(rel_valid.id), self.orgs['research_lab'], "test_user")
            
            # Test that valid relationship works
            trust_info = TrustService.check_trust_level(self.orgs['university_a'], self.orgs['research_lab'])
            assert trust_info is not None
            
            # Create expired relationship
            rel_expired = TrustRelationship.objects.create(
                source_organization=self.orgs['university_b'],
                target_organization=self.orgs['research_lab'],
                trust_level=self.trust_levels['standard'],
                relationship_type="bilateral",
                status="active",
                approved_by_source=True,
                approved_by_target=True,
                valid_until=past_expiry,
                created_by="test_admin",
                last_modified_by="test_admin"
            )
            
            # Test that expired relationship doesn't work
            trust_info = TrustService.check_trust_level(self.orgs['university_b'], self.orgs['research_lab'])
            if trust_info:
                # If trust_info is not None, the relationship should not be effective
                _, relationship = trust_info
                assert not relationship.is_effective
            
            print("✅ Temporal trust relationships successful")
            return True
        except Exception as e:
            print(f"❌ Temporal trust relationships failed: {e}")
            return False
    
    def test_anonymization_strategies(self):
        """Test comprehensive anonymization strategies"""
        print("Testing anonymization strategies...")
        
        try:
            # Test all anonymization strategies
            test_data = {
                "source": "Test Organization Alpha",
                "indicator": "192.168.1.100",
                "description": "Malicious IP address detected in network logs",
                "metadata": {
                    "detection_method": "IDS",
                    "confidence": "high",
                    "analyst": "john.doe@testorg.com"
                }
            }
            
            strategies = {
                "none": NoAnonymizationStrategy(),
                "minimal": MinimalAnonymizationStrategy(),
                "partial": PartialAnonymizationStrategy(),
                "full": FullAnonymizationStrategy(),
                "custom": CustomAnonymizationStrategy({
                    "remove_fields": ["analyst"],
                    "anonymize_fields": ["source"]
                })
            }
            
            for strategy_name, strategy in strategies.items():
                context = {"test_mode": True}
                result = strategy.anonymize(test_data.copy(), context)
                
                if strategy_name == "none":
                    assert result["source"] == "Test Organization Alpha"
                    assert "analyst" in result["metadata"]
                elif strategy_name == "full":
                    # For full anonymization, just check that source is different or redacted
                    assert result["source"] != "Test Organization Alpha"
                elif strategy_name == "partial":
                    assert result["source"] != "Test Organization Alpha"
                
            print("✅ Anonymization strategies successful")
            return True
        except Exception as e:
            print(f"❌ Anonymization strategies failed: {e}")
            return False
    
    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling"""
        print("Testing edge cases and error handling...")
        
        try:
            # Test duplicate relationship creation
            rel1 = TrustService.create_trust_relationship(
                source_org=self.orgs['university_a'],
                target_org=self.orgs['university_b'],
                trust_level_name="Test Standard Trust",
                relationship_type="bilateral",
                created_by="test_admin"
            )
            
            try:
                rel2 = TrustService.create_trust_relationship(
                    source_org=self.orgs['university_a'],
                    target_org=self.orgs['university_b'],
                    trust_level_name="Test Standard Trust",
                    relationship_type="bilateral",
                    created_by="test_admin"
                )
                # Should not reach here
                assert False, "Duplicate relationship should have failed"
            except ValidationError:
                pass  # Expected
            
            # Test self-relationship
            try:
                rel_self = TrustService.create_trust_relationship(
                    source_org=self.orgs['university_a'],
                    target_org=self.orgs['university_a'],
                    trust_level_name="Test Standard Trust",
                    relationship_type="bilateral",
                    created_by="test_admin"
                )
                assert False, "Self-relationship should have failed"
            except ValidationError:
                pass  # Expected
            
            # Test invalid trust level
            try:
                rel_invalid = TrustService.create_trust_relationship(
                    source_org=self.orgs['university_a'],
                    target_org=self.orgs['private_a'],
                    trust_level_name="Non-existent Trust Level",
                    relationship_type="bilateral",
                    created_by="test_admin"
                )
                assert False, "Invalid trust level should have failed"
            except ValidationError:
                pass  # Expected
            
            print("✅ Edge cases and error handling successful")
            return True
        except Exception as e:
            print(f"❌ Edge cases and error handling failed: {e}")
            return False
    
    def test_performance_and_scalability(self):
        """Test performance with multiple relationships"""
        print("Testing performance and scalability...")
        
        try:
            import time
            
            # Create multiple relationships
            start_time = time.time()
            
            relationships = []
            for i in range(10):
                rel = TrustService.create_trust_relationship(
                    source_org=f"test_perf_org_{i}",
                    target_org=f"test_perf_org_{i+10}",
                    trust_level_name="Test Standard Trust",
                    relationship_type="bilateral",
                    created_by="test_admin"
                )
                relationships.append(rel)
            
            creation_time = time.time() - start_time
            
            # Test bulk queries
            start_time = time.time()
            
            for i in range(10):
                trust_info = TrustService.check_trust_level(
                    f"test_perf_org_{i}",
                    f"test_perf_org_{i+10}"
                )
            
            query_time = time.time() - start_time
            
            # Performance should be reasonable
            assert creation_time < 10.0  # 10 relationships in under 10 seconds
            assert query_time < 5.0     # 10 queries in under 5 seconds
            
            print(f"✅ Performance test successful (creation: {creation_time:.2f}s, queries: {query_time:.2f}s)")
            return True
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    def cleanup_all_test_data(self):
        """Clean up all test data"""
        try:
            TrustRelationship.objects.filter(source_organization__startswith='test_').delete()
            TrustGroupMembership.objects.filter(organization__startswith='test_').delete()
            TrustGroup.objects.filter(name__startswith='Test ').delete()
            TrustLevel.objects.filter(name__startswith='Test ').delete()
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("=" * 60)
        print("TRUST MANAGEMENT COMPREHENSIVE TESTS")
        print("=" * 60)
        
        tests = [
            ("Complex Trust Scenarios", self.test_complex_trust_scenarios),
            ("Community Trust Groups", self.test_community_trust_groups),
            ("Access Control Hierarchies", self.test_access_control_hierarchies),
            ("Temporal Trust Relationships", self.test_temporal_trust_relationships),
            ("Anonymization Strategies", self.test_anonymization_strategies),
            ("Edge Cases & Error Handling", self.test_edge_cases_and_error_handling),
            ("Performance & Scalability", self.test_performance_and_scalability),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            print("-" * 40)
            success = test_func()
            results.append((test_name, success))
            print()
        
        # Cleanup
        self.cleanup_all_test_data()
        
        # Print summary
        print("=" * 60)
        print("COMPREHENSIVE TEST SUMMARY")
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
            print("\n❌ Some comprehensive tests failed!")
            return False
        else:
            print("\n✅ All comprehensive tests passed!")
            return True


def main():
    """Run comprehensive tests"""
    test_suite = ComprehensiveTestSuite()
    success = test_suite.run_all_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)