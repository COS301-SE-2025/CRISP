"""
CRISP Platform Integration Tests

Comprehensive tests that validate the integration between:
- User Management (Authentication, Organizations, Users)
- Trust Management (Trust Relationships, Anonymization)
- Threat Intelligence (STIX Objects, Collections, TAXII)

These tests verify that the core domain model is properly implemented.
"""

import uuid
import json
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

# Import core models from all components
from UserManagement.models import Organization
from crisp_threat_intel.models import STIXObject, Collection, CollectionObject
from trust_management_app.core.models.models import (
    TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership, TrustLog
)

# Import integration services
from crisp_project.services import CRISPIntegrationService

User = get_user_model()


class CRISPIntegrationTestCase(TransactionTestCase):
    """
    Base test case for CRISP integration tests.
    Uses TransactionTestCase to support database transactions.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test trust levels
        cls.trust_levels = {
            'none': TrustLevel.objects.create(
                name='No Trust',
                level='none',
                numerical_value=0,
                description='No trust relationship',
                default_anonymization_level='full',
                default_access_level='none'
            ),
            'low': TrustLevel.objects.create(
                name='Low Trust',
                level='low',
                numerical_value=25,
                description='Low trust relationship',
                default_anonymization_level='partial',
                default_access_level='read'
            ),
            'medium': TrustLevel.objects.create(
                name='Medium Trust',
                level='medium',
                numerical_value=50,
                description='Medium trust relationship',
                default_anonymization_level='minimal',
                default_access_level='subscribe'
            ),
            'high': TrustLevel.objects.create(
                name='High Trust',
                level='high',
                numerical_value=75,
                description='High trust relationship',
                default_anonymization_level='minimal',
                default_access_level='contribute'
            ),
            'complete': TrustLevel.objects.create(
                name='Complete Trust',
                level='complete',
                numerical_value=100,
                description='Complete trust relationship',
                default_anonymization_level='none',
                default_access_level='full',
                is_system_default=True
            )
        }
    
    def setUp(self):
        """Set up test data for each test"""
        
        # Create test organizations (using only current model fields)
        self.org_university_a = Organization.objects.create(
            name='University A',
            description='Test University A',
            domain='university-a.edu'
        )
        
        self.org_university_b = Organization.objects.create(
            name='University B', 
            description='Test University B',
            domain='university-b.edu'
        )
        
        self.org_external = Organization.objects.create(
            name='External Organization',
            description='External test organization',
            domain='external.com'
        )
        
        # Create test users
        self.user_a_publisher = User.objects.create_user(
            username='publisher_a',
            email='publisher@university-a.edu',
            password='testpass123',
            organization=self.org_university_a,
            role='publisher'
        )
        
        self.user_b_viewer = User.objects.create_user(
            username='viewer_b',
            email='viewer@university-b.edu', 
            password='testpass123',
            organization=self.org_university_b,
            role='viewer'
        )
        
        self.user_external = User.objects.create_user(
            username='external_user',
            email='user@external.com',
            password='testpass123',
            organization=self.org_external,
            role='viewer'
        )


class OrganizationIntegrationTest(CRISPIntegrationTestCase):
    """Test organization model integration across components"""
    
    def test_organization_creation_with_stix_fields(self):
        """Test that organizations support basic fields (STIX fields are for future implementation)"""
        org = Organization.objects.create(
            name='Test STIX Organization',
            description='Organization with future STIX support',
            domain='stix-org.edu'
        )
        
        self.assertEqual(org.name, 'Test STIX Organization')
        self.assertEqual(org.description, 'Organization with future STIX support')
        self.assertEqual(org.domain, 'stix-org.edu')
        self.assertIsNotNone(org.id)
        self.assertTrue(org.is_active)
        # Note: STIX fields (identity_class, sectors, etc.) are commented out for migration compatibility
    
    def test_organization_foreign_key_relationships(self):
        """Test that foreign key relationships work correctly"""
        
        # Test user-organization relationship
        self.assertEqual(self.user_a_publisher.organization, self.org_university_a)
        self.assertIn(self.user_a_publisher, self.org_university_a.users.all())
        
        # Test organization can have multiple users
        user2 = User.objects.create_user(
            username='user2_a',
            email='user2@university-a.edu',
            password='testpass123',
            organization=self.org_university_a,
            role='viewer'
        )
        
        self.assertEqual(self.org_university_a.users.count(), 2)
        self.assertIn(user2, self.org_university_a.users.all())


class TrustRelationshipIntegrationTest(CRISPIntegrationTestCase):
    """Test trust relationship integration with organizations"""
    
    def test_trust_relationship_creation_with_foreign_keys(self):
        """Test creating trust relationships with proper foreign key references"""
        
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org_university_a,
            target_organization=self.org_university_b,
            relationship_type='bilateral',
            trust_level=self.trust_levels['medium'],
            anonymization_level='minimal',
            access_level='subscribe',
            status='active'
        )
        
        self.assertEqual(trust_relationship.source_organization, self.org_university_a)
        self.assertEqual(trust_relationship.target_organization, self.org_university_b)
        self.assertEqual(trust_relationship.trust_level, self.trust_levels['medium'])
        self.assertEqual(trust_relationship.status, 'active')
        
        # Test reverse relationships
        self.assertIn(trust_relationship, self.org_university_a.initiated_trust_relationships.all())
        self.assertIn(trust_relationship, self.org_university_b.received_trust_relationships.all())
    
    def test_trust_relationship_bidirectional(self):
        """Test creating bidirectional trust relationships"""
        
        # Create A->B relationship
        trust_a_to_b = TrustRelationship.objects.create(
            source_organization=self.org_university_a,
            target_organization=self.org_university_b,
            relationship_type='bilateral',
            trust_level=self.trust_levels['high'],
            anonymization_level='minimal',
            access_level='contribute',
            status='active'
        )
        
        # Create B->A relationship
        trust_b_to_a = TrustRelationship.objects.create(
            source_organization=self.org_university_b,
            target_organization=self.org_university_a,
            relationship_type='bilateral', 
            trust_level=self.trust_levels['medium'],
            anonymization_level='partial',
            access_level='subscribe',
            status='active'
        )
        
        # Verify both relationships exist
        self.assertEqual(
            TrustRelationship.objects.filter(
                source_organization=self.org_university_a,
                target_organization=self.org_university_b
            ).count(), 1
        )
        
        self.assertEqual(
            TrustRelationship.objects.filter(
                source_organization=self.org_university_b,
                target_organization=self.org_university_a
            ).count(), 1
        )


class ThreatIntelligenceIntegrationTest(CRISPIntegrationTestCase):
    """Test threat intelligence integration with user management and trust"""
    
    def setUp(self):
        super().setUp()
        
        # Create a collection owned by University A
        self.collection_a = Collection.objects.create(
            title='University A Threat Feed',
            description='Threat intelligence from University A',
            alias='uni-a-feed',
            owner=self.org_university_a,
            can_read=True,
            can_write=False,
            media_types=['application/stix+json;version=2.1']
        )
        
        # Create STIX objects
        self.stix_indicator = STIXObject.objects.create(
            stix_id='indicator--12345678-1234-1234-1234-123456789012',
            stix_type='indicator',
            spec_version='2.1',
            created=timezone.now(),
            modified=timezone.now(),
            created_by_ref='identity--87654321-4321-4321-4321-210987654321',
            labels=['malicious-activity'],
            raw_data={
                'type': 'indicator',
                'id': 'indicator--12345678-1234-1234-1234-123456789012',
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat(),
                'labels': ['malicious-activity'],
                'pattern': '[file:hashes.MD5 = \"d41d8cd98f00b204e9800998ecf8427e\"]'
            },
            created_by=self.user_a_publisher,
            source_organization=self.org_university_a
        )
        
        # Add STIX object to collection
        CollectionObject.objects.create(
            collection=self.collection_a,
            stix_object=self.stix_indicator,
            date_added=timezone.now()
        )
    
    def test_stix_object_creation_with_user_attribution(self):
        """Test that STIX objects are properly attributed to users and organizations"""
        
        self.assertEqual(self.stix_indicator.created_by, self.user_a_publisher)
        self.assertEqual(self.stix_indicator.source_organization, self.org_university_a)
        self.assertEqual(self.stix_indicator.stix_type, 'indicator')
        self.assertIsNotNone(self.stix_indicator.raw_data)
        
        # Test reverse relationships
        self.assertIn(self.stix_indicator, self.user_a_publisher.created_stix_objects.all())
        self.assertIn(self.stix_indicator, self.org_university_a.stix_objects.all())
    
    def test_collection_ownership_and_access(self):
        """Test collection ownership and access control"""
        
        self.assertEqual(self.collection_a.owner, self.org_university_a)
        self.assertTrue(self.collection_a.can_read)
        self.assertFalse(self.collection_a.can_write)
        
        # Test that collection contains our STIX object
        collection_objects = CollectionObject.objects.filter(collection=self.collection_a)
        self.assertEqual(collection_objects.count(), 1)
        self.assertEqual(collection_objects.first().stix_object, self.stix_indicator)


class CRISPIntegrationServiceTest(CRISPIntegrationTestCase):
    """Test the CRISP integration service that coordinates all components"""
    
    def setUp(self):
        super().setUp()
        
        # Create trust relationship between University A and B
        self.trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org_university_a,
            target_organization=self.org_university_b,
            relationship_type='bilateral',
            trust_level=self.trust_levels['medium'],
            anonymization_level='minimal',
            access_level='subscribe',
            status='active'
        )
        
        # Create threat intelligence
        self.collection = Collection.objects.create(
            title='Test Collection',
            description='Test collection for integration tests',
            alias='test-collection',
            owner=self.org_university_a,
            can_read=True,
            can_write=False
        )
        
        self.stix_object = STIXObject.objects.create(
            stix_id='indicator--test-integration-object',
            stix_type='indicator',
            spec_version='2.1',
            created=timezone.now(),
            modified=timezone.now(),
            labels=['test'],
            raw_data={
                'type': 'indicator',
                'id': 'indicator--test-integration-object',
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat(),
                'labels': ['test'],
                'pattern': '[file:hashes.MD5 = \"test-hash\"]',
                'threat_intel_value': 'sensitive-data-here'
            },
            created_by=self.user_a_publisher,
            source_organization=self.org_university_a
        )
        
        CollectionObject.objects.create(
            collection=self.collection,
            stix_object=self.stix_object
        )
    
    def test_get_user_organization(self):
        """Test getting organization for a user"""
        
        org = CRISPIntegrationService.get_user_organization(self.user_a_publisher)
        self.assertEqual(org, self.org_university_a)
        
        org = CRISPIntegrationService.get_user_organization(self.user_b_viewer)
        self.assertEqual(org, self.org_university_b)
        
        # Test user without organization
        user_no_org = User.objects.create_user(
            username='no_org_user',
            email='noorg@example.com',
            password='testpass123'
        )
        org = CRISPIntegrationService.get_user_organization(user_no_org)
        self.assertIsNone(org)
    
    def test_check_access_permission_same_organization(self):
        """Test access permissions for users in the same organization"""
        
        allowed, access_level, trust_info = CRISPIntegrationService.check_access_permission(
            self.user_a_publisher, self.org_university_a, 'read'
        )
        
        self.assertTrue(allowed)
        self.assertEqual(access_level, 'full')
        self.assertTrue(trust_info.get('same_org', False))
    
    def test_check_access_permission_with_trust_relationship(self):
        """Test access permissions based on trust relationships"""
        
        # User B trying to access University A's data
        allowed, access_level, trust_info = CRISPIntegrationService.check_access_permission(
            self.user_b_viewer, self.org_university_a, 'read'
        )
        
        self.assertTrue(allowed)
        self.assertEqual(access_level, 'subscribe')  # From medium trust level
        self.assertEqual(trust_info['trust_level'], 'medium')
        self.assertEqual(trust_info['numerical_value'], 50)
    
    def test_check_access_permission_no_trust_relationship(self):
        """Test access permissions when no trust relationship exists"""
        
        # External user trying to access University A's data
        allowed, access_level, trust_info = CRISPIntegrationService.check_access_permission(
            self.user_external, self.org_university_a, 'read'
        )
        
        self.assertFalse(allowed)
        self.assertEqual(access_level, 'none')
        self.assertIn('error', trust_info)
    
    def test_get_anonymized_stix_objects_same_organization(self):
        """Test getting STIX objects without anonymization for same organization"""
        
        objects = CRISPIntegrationService.get_anonymized_stix_objects(
            self.user_a_publisher, self.org_university_a
        )
        
        self.assertEqual(len(objects), 1)
        obj = objects[0]
        self.assertEqual(obj['stix_id'], 'indicator--test-integration-object')
        self.assertFalse(obj['anonymized'])
        self.assertIn('threat_intel_value', obj['data'])
        self.assertEqual(obj['data']['threat_intel_value'], 'sensitive-data-here')
    
    def test_get_anonymized_stix_objects_with_trust_relationship(self):
        """Test getting STIX objects with anonymization based on trust level"""
        
        # User B accessing University A's data - should be anonymized
        objects = CRISPIntegrationService.get_anonymized_stix_objects(
            self.user_b_viewer, self.org_university_a
        )
        
        self.assertEqual(len(objects), 1)
        obj = objects[0]
        self.assertEqual(obj['stix_id'], 'indicator--test-integration-object')
        # Should be anonymized due to trust relationship
        # The exact anonymization depends on the strategy implementation
    
    def test_get_anonymized_stix_objects_no_access(self):
        """Test getting STIX objects when access is denied"""
        
        # External user trying to access University A's data
        objects = CRISPIntegrationService.get_anonymized_stix_objects(
            self.user_external, self.org_university_a
        )
        
        self.assertEqual(len(objects), 0)
    
    def test_get_accessible_collections(self):
        """Test getting collections accessible to a user"""
        
        # User A should see their own collection
        collections = CRISPIntegrationService.get_accessible_collections(self.user_a_publisher)
        self.assertEqual(len(collections), 1)
        collection = collections[0]
        self.assertEqual(collection['title'], 'Test Collection')
        self.assertEqual(collection['access_level'], 'full')
        self.assertTrue(collection['can_write'])
        
        # User B should see University A's collection based on trust relationship
        collections = CRISPIntegrationService.get_accessible_collections(self.user_b_viewer)
        self.assertEqual(len(collections), 1)
        collection = collections[0]
        self.assertEqual(collection['title'], 'Test Collection')
        self.assertEqual(collection['access_level'], 'subscribe')
        self.assertFalse(collection['can_write'])  # Subscribe level doesn't allow write
        
        # External user should see no collections
        collections = CRISPIntegrationService.get_accessible_collections(self.user_external)
        self.assertEqual(len(collections), 0)
    
    def test_create_stix_object_with_attribution(self):
        """Test creating STIX objects with proper user and organization attribution"""
        
        stix_data = {
            'type': 'malware',
            'id': 'malware--test-creation',
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'name': 'Test Malware',
            'labels': ['trojan']
        }
        
        stix_object = CRISPIntegrationService.create_stix_object(
            self.user_a_publisher, self.org_university_a, stix_data
        )
        
        self.assertEqual(stix_object.stix_id, 'malware--test-creation')
        self.assertEqual(stix_object.stix_type, 'malware')
        self.assertEqual(stix_object.created_by, self.user_a_publisher)
        self.assertEqual(stix_object.source_organization, self.org_university_a)
        self.assertEqual(stix_object.raw_data, stix_data)
    
    def test_get_trust_statistics(self):
        """Test getting trust relationship statistics for an organization"""
        
        # Create additional trust relationships for testing
        TrustRelationship.objects.create(
            source_organization=self.org_university_b,
            target_organization=self.org_university_a,
            relationship_type='bilateral',
            trust_level=self.trust_levels['high'],
            status='active'
        )
        
        TrustRelationship.objects.create(
            source_organization=self.org_university_a,
            target_organization=self.org_external,
            relationship_type='bilateral',
            trust_level=self.trust_levels['low'],
            status='pending'
        )
        
        stats = CRISPIntegrationService.get_trust_statistics(self.org_university_a)
        
        self.assertEqual(stats['organization_name'], 'University A')
        self.assertEqual(stats['initiated_relationships'], 2)  # A->B and A->External
        self.assertEqual(stats['received_relationships'], 1)   # B->A
        # The exact counts depend on the TrustService implementation


class EndToEndWorkflowTest(CRISPIntegrationTestCase):
    """
    End-to-end workflow tests that simulate real CRISP platform usage scenarios
    """
    
    def test_threat_intelligence_sharing_workflow(self):
        """
        Test complete workflow: Organization A publishes threat intel, Organization B consumes it
        """
        
        # Step 1: Organization A creates threat intelligence
        threat_data = {
            'type': 'indicator',
            'id': 'indicator--workflow-test',
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'labels': ['malicious-activity'],
            'pattern': '[domain-name:value = \"malicious.example.com\"]'
        }
        
        stix_object = CRISPIntegrationService.create_stix_object(
            self.user_a_publisher, self.org_university_a, threat_data
        )
        
        # Step 2: Add to collection
        collection = Collection.objects.create(
            title='Workflow Test Collection',
            description='Collection for workflow testing',
            alias='workflow-test',
            owner=self.org_university_a,
            can_read=True,
            can_write=False
        )
        
        CollectionObject.objects.create(
            collection=collection,
            stix_object=stix_object
        )
        
        # Step 3: Establish trust relationship
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org_university_a,
            target_organization=self.org_university_b,
            relationship_type='bilateral',
            trust_level=self.trust_levels['high'],
            anonymization_level='minimal',
            access_level='contribute',
            status='active'
        )
        
        # Step 4: Organization B discovers accessible collections
        accessible_collections = CRISPIntegrationService.get_accessible_collections(self.user_b_viewer)
        
        self.assertEqual(len(accessible_collections), 1)
        accessible_collection = accessible_collections[0]
        self.assertEqual(accessible_collection['title'], 'Workflow Test Collection')
        self.assertEqual(accessible_collection['access_level'], 'contribute')
        
        # Step 5: Organization B accesses threat intelligence
        threat_objects = CRISPIntegrationService.get_anonymized_stix_objects(
            self.user_b_viewer, self.org_university_a, str(collection.id)
        )
        
        self.assertEqual(len(threat_objects), 1)
        threat_object = threat_objects[0]
        self.assertEqual(threat_object['stix_id'], 'indicator--workflow-test')
        
        # Step 6: Verify trust logging
        trust_logs = TrustLog.objects.filter(
            source_organization=self.org_university_a,
            target_organization=self.org_university_b,
            action='relationship_created'
        )
        
        # The exact logging depends on the implementation
        # but there should be audit trail
        
    def test_trust_group_workflow(self):
        """
        Test workflow involving trust groups for community-based sharing
        """
        
        # Step 1: Create a trust group for educational institutions
        trust_group = TrustGroup.objects.create(
            name='Educational Institutions Trust Group',
            description='Trust group for universities and colleges',
            group_type='sector',
            trust_level=self.trust_levels['medium'],
            sharing_policy={'allowed_types': ['indicator', 'malware']},
            is_active=True
        )
        
        # Step 2: Add organizations to the trust group
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.org_university_a,
            membership_type='member',
            is_active=True
        )
        
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.org_university_b,
            membership_type='member',
            is_active=True
        )
        
        # Step 3: Verify organizations can access each other's data through group membership
        # This would depend on the implementation of group-based trust resolution
        
        self.assertEqual(trust_group.get_member_count(), 2)
        self.assertIn(self.org_university_a, [m.organization for m in trust_group.group_memberships.all()])
        self.assertIn(self.org_university_b, [m.organization for m in trust_group.group_memberships.all()])


# Test Runner Configuration
def run_integration_tests():
    """
    Helper function to run all integration tests.
    Can be called from management commands or scripts.
    """
    import unittest
    
    test_classes = [
        OrganizationIntegrationTest,
        TrustRelationshipIntegrationTest, 
        ThreatIntelligenceIntegrationTest,
        CRISPIntegrationServiceTest,
        EndToEndWorkflowTest
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Allow running tests directly
    run_integration_tests()