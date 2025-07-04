"""
Comprehensive Integration Tests for CRISP System
Tests the integration between UserManagement and TrustManagement
"""
import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.user_management.models import Organization, InvitationToken
from apps.trust_management.models import TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership, TrustLog
from apps.core.services import CRISPIntegrationService

User = get_user_model()


class CRISPIntegrationTestCase(TestCase):
    """Test integration between user management and trust management"""
    
    def setUp(self):
        """Set up test data"""
        # Create trust levels
        self.trust_level_public = TrustLevel.objects.create(
            name='Public Trust',
            level='public',
            numerical_value=25,
            description='Public trust level',
            default_anonymization_level='full',
            default_access_level='read',
            created_by='test_system'
        )
        
        self.trust_level_trusted = TrustLevel.objects.create(
            name='Trusted Partners',
            level='trusted',
            numerical_value=50,
            description='Trusted partner level',
            default_anonymization_level='partial',
            default_access_level='contribute',
            created_by='test_system'
        )
        
        self.trust_level_restricted = TrustLevel.objects.create(
            name='Restricted Access',
            level='restricted',
            numerical_value=75,
            description='Restricted access level',
            default_anonymization_level='minimal',
            default_access_level='admin',
            created_by='test_system'
        )
        
        # Create organizations
        self.org1 = Organization.objects.create(
            name='University Alpha',
            domain='alpha.edu',
            contact_email='admin@alpha.edu',
            institution_type='university',
            trust_level_default='public'
        )
        
        self.org2 = Organization.objects.create(
            name='University Beta',
            domain='beta.edu',
            contact_email='admin@beta.edu',
            institution_type='university',
            trust_level_default='trusted'
        )
        
        self.org3 = Organization.objects.create(
            name='College Gamma',
            domain='gamma.edu',
            contact_email='admin@gamma.edu',
            institution_type='college',
            trust_level_default='public'
        )
        
        # Create users
        self.admin_user1 = User.objects.create_user(
            username='admin1',
            email='admin1@alpha.edu',
            password='testpass123',
            organization=self.org1,
            role='publisher',
            is_organization_admin=True,
            first_name='Admin',
            last_name='Alpha'
        )
        
        self.admin_user2 = User.objects.create_user(
            username='admin2',
            email='admin2@beta.edu',
            password='testpass123',
            organization=self.org2,
            role='publisher',
            is_organization_admin=True,
            first_name='Admin',
            last_name='Beta'
        )
        
        self.viewer_user = User.objects.create_user(
            username='viewer1',
            email='viewer1@alpha.edu',
            password='testpass123',
            organization=self.org1,
            role='viewer',
            first_name='Viewer',
            last_name='Alpha'
        )
        
        self.system_admin = User.objects.create_user(
            username='sysadmin',
            email='sysadmin@bluevision.com',
            password='testpass123',
            role='system_admin',
            first_name='System',
            last_name='Admin'
        )
    
    def test_create_organization_with_trust_setup(self):
        """Test R1.3.1 - System Administrators register new client Institutions"""
        admin_data = {
            'username': 'newadmin',
            'email': 'admin@neworg.edu',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'Admin'
        }
        
        org = CRISPIntegrationService.create_organization_with_trust_setup(
            name='New University',
            domain='neworg.edu',
            contact_email='contact@neworg.edu',
            admin_user_data=admin_data,
            institution_type='university',
            default_trust_level='trusted'
        )
        
        # Verify organization was created
        self.assertEqual(org.name, 'New University')
        self.assertEqual(org.institution_type, 'university')
        self.assertEqual(org.trust_level_default, 'trusted')
        self.assertTrue(org.is_bluevision_client)
        
        # Verify admin user was created
        admin_user = User.objects.get(email='admin@neworg.edu')
        self.assertEqual(admin_user.organization, org)
        self.assertEqual(admin_user.role, 'publisher')
        self.assertTrue(admin_user.is_organization_admin)
        self.assertTrue(admin_user.terms_accepted)
        
        # Verify trust log was created
        log = TrustLog.objects.filter(
            action='organization_created',
            source_organization=org.id
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, 'newadmin')
    
    def test_user_invitation_system(self):
        """Test R1.2.2 - Institution Publishers invite users via email"""
        # Test successful invitation
        invitation = CRISPIntegrationService.invite_user_to_organization(
            organization=self.org1,
            inviting_user=self.admin_user1,
            email='newuser@alpha.edu',
            role='viewer'
        )
        
        self.assertEqual(invitation.organization, self.org1)
        self.assertEqual(invitation.invited_by, self.admin_user1)
        self.assertEqual(invitation.email, 'newuser@alpha.edu')
        self.assertEqual(invitation.role, 'viewer')
        self.assertTrue(invitation.is_valid())
        
        # Verify log was created
        log = TrustLog.objects.filter(
            action='user_invited',
            source_organization=self.org1.id
        ).first()
        self.assertIsNotNone(log)
        
        # Test permission validation
        with self.assertRaises(Exception):
            CRISPIntegrationService.invite_user_to_organization(
                organization=self.org2,  # Different organization
                inviting_user=self.admin_user1,
                email='test@beta.edu',
                role='viewer'
            )
        
        # Test non-admin user cannot invite
        with self.assertRaises(Exception):
            CRISPIntegrationService.invite_user_to_organization(
                organization=self.org1,
                inviting_user=self.viewer_user,  # Not admin
                email='test@alpha.edu',
                role='viewer'
            )
    
    def test_trust_relationship_creation(self):
        """Test R4.1.4 - Enable bilateral trust agreements"""
        # Create trust relationship
        relationship = CRISPIntegrationService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org2,
            trust_level_name='Trusted Partners',
            relationship_type='bilateral',
            created_by_user=self.admin_user1
        )
        
        self.assertEqual(relationship.source_organization, self.org1.id)
        self.assertEqual(relationship.target_organization, self.org2.id)
        self.assertEqual(relationship.trust_level.name, 'Trusted Partners')
        self.assertEqual(relationship.relationship_type, 'bilateral')
        self.assertEqual(relationship.status, 'pending')
        self.assertFalse(relationship.approved_by_source)
        self.assertFalse(relationship.approved_by_target)
        
        # Verify log was created
        log = TrustLog.objects.filter(
            action='relationship_created',
            trust_relationship=relationship
        ).first()
        self.assertIsNotNone(log)
        
        # Test duplicate relationship prevention
        with self.assertRaises(Exception):
            CRISPIntegrationService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org2,
                trust_level_name='Public Trust',
                created_by_user=self.admin_user1
            )
        
        # Test same organization validation
        with self.assertRaises(Exception):
            CRISPIntegrationService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org1,
                trust_level_name='Public Trust',
                created_by_user=self.admin_user1
            )
    
    def test_trust_relationship_approval(self):
        """Test bilateral approval process"""
        # Create trust relationship
        relationship = CRISPIntegrationService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org2,
            trust_level_name='Trusted Partners',
            created_by_user=self.admin_user1
        )
        
        # Source org approval
        approved = CRISPIntegrationService.approve_trust_relationship(
            relationship=relationship,
            approving_org=self.org1,
            approving_user=self.admin_user1
        )
        
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_source)
        self.assertFalse(relationship.approved_by_target)
        self.assertEqual(relationship.status, 'pending')
        self.assertFalse(approved)  # Not fully approved yet
        
        # Target org approval
        approved = CRISPIntegrationService.approve_trust_relationship(
            relationship=relationship,
            approving_org=self.org2,
            approving_user=self.admin_user2
        )
        
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_source)
        self.assertTrue(relationship.approved_by_target)
        self.assertEqual(relationship.status, 'active')
        self.assertTrue(approved)  # Fully approved
        
        # Verify approval logs
        approval_logs = TrustLog.objects.filter(
            action='relationship_approved',
            trust_relationship=relationship
        )
        self.assertEqual(approval_logs.count(), 2)
    
    def test_intelligence_access_control(self):
        """Test R4.2.1 - Filter shared intelligence based on trust relationships"""
        # Create and approve trust relationship
        relationship = CRISPIntegrationService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org2,
            trust_level_name='Trusted Partners',
            created_by_user=self.admin_user1
        )
        
        # Approve from both sides
        CRISPIntegrationService.approve_trust_relationship(
            relationship, self.org1, self.admin_user1
        )
        CRISPIntegrationService.approve_trust_relationship(
            relationship, self.org2, self.admin_user2
        )
        
        # Test access checking
        can_access, reason, rel = CRISPIntegrationService.can_user_access_intelligence(
            user=self.viewer_user,  # From org1
            intelligence_owner_org_id=str(self.org2.id),  # Accessing org2's intelligence
            required_access_level='read'
        )
        
        self.assertTrue(can_access)
        self.assertIn('Access granted', reason)
        self.assertEqual(rel, relationship)
        
        # Test insufficient access level
        can_access, reason, rel = CRISPIntegrationService.can_user_access_intelligence(
            user=self.viewer_user,
            intelligence_owner_org_id=str(self.org2.id),
            required_access_level='admin'  # Requires higher access
        )
        
        self.assertFalse(can_access)
        self.assertIn('Insufficient access level', reason)
        
        # Test no relationship
        can_access, reason, rel = CRISPIntegrationService.can_user_access_intelligence(
            user=self.viewer_user,
            intelligence_owner_org_id=str(self.org3.id),  # No relationship with org3
            required_access_level='read'
        )
        
        self.assertFalse(can_access)
        self.assertIn('No trust relationship', reason)
        self.assertIsNone(rel)
    
    def test_user_accessible_intelligence_sources(self):
        """Test getting accessible intelligence sources for a user"""
        # Create multiple trust relationships
        rel1 = CRISPIntegrationService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org2,
            trust_level_name='Trusted Partners',
            created_by_user=self.admin_user1
        )
        
        rel2 = CRISPIntegrationService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org3,
            trust_level_name='Public Trust',
            created_by_user=self.admin_user1
        )
        
        # Approve relationships
        for rel in [rel1, rel2]:
            rel.approved_by_source = True
            rel.approved_by_target = True
            rel.status = 'active'
            rel.save()
        
        # Get accessible sources
        sources = CRISPIntegrationService.get_user_accessible_intelligence_sources(
            user=self.viewer_user
        )
        
        self.assertEqual(len(sources), 2)
        
        # Check organization names are in sources
        org_names = [source['organization'].name for source in sources]
        self.assertIn('University Beta', org_names)
        self.assertIn('College Gamma', org_names)
        
        # Check trust levels
        trust_levels = [source['trust_level'] for source in sources]
        self.assertIn('trusted', trust_levels)
        self.assertIn('public', trust_levels)
    
    def test_organization_trust_dashboard(self):
        """Test trust dashboard data generation"""
        # Create trust relationships and groups
        rel1 = CRISPIntegrationService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org2,
            trust_level_name='Trusted Partners',
            created_by_user=self.admin_user1
        )
        rel1.status = 'active'
        rel1.approved_by_source = True
        rel1.approved_by_target = True
        rel1.save()
        
        rel2 = CRISPIntegrationService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org3,
            trust_level_name='Public Trust',
            created_by_user=self.admin_user1
        )
        
        # Create trust group
        trust_group = TrustGroup.objects.create(
            name='Educational Sector',
            description='Universities and colleges',
            group_type='sector',
            default_trust_level=self.trust_level_public,
            created_by='test_system',
            administrators=[str(self.org1.id)]
        )
        
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.org1.id,
            membership_type='administrator'
        )
        
        # Get dashboard data
        dashboard_data = CRISPIntegrationService.get_organization_trust_dashboard_data(
            self.org1
        )
        
        self.assertEqual(dashboard_data['organization'], self.org1)
        self.assertEqual(dashboard_data['relationships']['total'], 2)
        self.assertEqual(dashboard_data['relationships']['active'], 1)
        self.assertEqual(dashboard_data['relationships']['pending'], 1)
        self.assertEqual(dashboard_data['trust_groups']['total'], 1)
        self.assertEqual(len(dashboard_data['partners']), 1)  # Only active relationships
        
        # Check trust level breakdown
        by_trust_level = dashboard_data['relationships']['by_trust_level']
        self.assertEqual(by_trust_level['trusted'], 1)
        self.assertEqual(by_trust_level['public'], 0)  # Pending relationship not counted
    
    def test_user_role_permissions(self):
        """Test user role-based permissions"""
        # Test publisher permissions
        self.assertTrue(self.admin_user1.is_publisher())
        self.assertTrue(self.admin_user1.can_publish_intelligence())
        self.assertTrue(self.admin_user1.can_manage_organization())
        
        # Test viewer permissions
        self.assertFalse(self.viewer_user.is_publisher())
        self.assertFalse(self.viewer_user.can_publish_intelligence())
        self.assertFalse(self.viewer_user.can_manage_organization())
        
        # Test system admin permissions
        self.assertTrue(self.system_admin.is_admin())
        self.assertTrue(self.system_admin.is_publisher())
        self.assertTrue(self.system_admin.can_publish_intelligence())
    
    def test_audit_logging(self):
        """Test comprehensive audit logging"""
        initial_log_count = TrustLog.objects.count()
        
        # Perform various operations that should create logs
        CRISPIntegrationService.create_organization_with_trust_setup(
            name='Audit Test Org',
            domain='audit.edu',
            contact_email='admin@audit.edu',
            admin_user_data={
                'username': 'auditadmin',
                'email': 'admin@audit.edu',
                'password': 'testpass123'
            }
        )
        
        # Check that log was created
        new_log_count = TrustLog.objects.count()
        self.assertGreater(new_log_count, initial_log_count)
        
        # Check log details
        latest_log = TrustLog.objects.latest('created_at')
        self.assertEqual(latest_log.action, 'organization_created')
        self.assertEqual(latest_log.user, 'auditadmin')
        self.assertIn('organization_name', latest_log.details)


class IntegrationAPITestCase(TestCase):
    """Test integration through API endpoints (when implemented)"""
    
    def setUp(self):
        """Set up test data for API tests"""
        # Create basic test data
        self.trust_level = TrustLevel.objects.create(
            name='API Test Level',
            level='public',
            numerical_value=25,
            description='Test trust level',
            default_anonymization_level='full',
            default_access_level='read',
            created_by='test_system'
        )
        
        self.org = Organization.objects.create(
            name='API Test University',
            domain='apitest.edu',
            contact_email='admin@apitest.edu'
        )
        
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@apitest.edu',
            password='testpass123',
            organization=self.org,
            role='publisher',
            is_organization_admin=True
        )
    
    def test_placeholder_api_structure(self):
        """Placeholder test for API structure (to be expanded when views are implemented)"""
        # This test ensures the basic model structure is working
        self.assertEqual(self.org.name, 'API Test University')
        self.assertEqual(self.user.organization, self.org)
        self.assertTrue(self.user.can_manage_organization())


class EndToEndIntegrationTestCase(TestCase):
    """End-to-end integration tests simulating real workflows"""
    
    def setUp(self):
        """Set up comprehensive test scenario"""
        # Create trust levels
        self.public_trust = TrustLevel.objects.create(
            name='Public Sharing',
            level='public',
            numerical_value=25,
            description='Public trust level',
            default_anonymization_level='full',
            default_access_level='read',
            created_by='system'
        )
        
        self.trusted_trust = TrustLevel.objects.create(
            name='Trusted Partnership',
            level='trusted',
            numerical_value=60,
            description='Trusted partner level',
            default_anonymization_level='partial',
            default_access_level='contribute',
            created_by='system'
        )
        
        # Create BlueVision admin
        self.bluevision_admin = User.objects.create_user(
            username='bluevision_admin',
            email='admin@bluevision.com',
            password='adminpass123',
            role='bluevision_admin',
            first_name='BlueVision',
            last_name='Administrator'
        )
    
    def test_complete_organization_onboarding_workflow(self):
        """Test complete workflow from organization creation to trust establishment"""
        # Step 1: BlueVision admin creates new client organization
        university_data = {
            'username': 'university_admin',
            'email': 'admin@university.edu',
            'password': 'university123',
            'first_name': 'University',
            'last_name': 'Administrator'
        }
        
        university = CRISPIntegrationService.create_organization_with_trust_setup(
            name='Test University',
            domain='university.edu',
            contact_email='contact@university.edu',
            admin_user_data=university_data,
            institution_type='university',
            default_trust_level='public'
        )
        
        college_data = {
            'username': 'college_admin',
            'email': 'admin@college.edu',
            'password': 'college123',
            'first_name': 'College',
            'last_name': 'Administrator'
        }
        
        college = CRISPIntegrationService.create_organization_with_trust_setup(
            name='Test College',
            domain='college.edu',
            contact_email='contact@college.edu',
            admin_user_data=college_data,
            institution_type='college',
            default_trust_level='trusted'
        )
        
        # Get the created admin users
        university_admin = User.objects.get(email='admin@university.edu')
        college_admin = User.objects.get(email='admin@college.edu')
        
        # Step 2: University admin invites users
        invitation = CRISPIntegrationService.invite_user_to_organization(
            organization=university,
            inviting_user=university_admin,
            email='analyst@university.edu',
            role='viewer'
        )
        
        self.assertTrue(invitation.is_valid())
        
        # Step 3: University admin initiates trust relationship with college
        relationship = CRISPIntegrationService.create_trust_relationship(
            source_org=university,
            target_org=college,
            trust_level_name='Trusted Partnership',
            relationship_type='bilateral',
            created_by_user=university_admin
        )
        
        self.assertEqual(relationship.status, 'pending')
        
        # Step 4: College admin approves the relationship
        CRISPIntegrationService.approve_trust_relationship(
            relationship=relationship,
            approving_org=university,
            approving_user=university_admin
        )
        
        CRISPIntegrationService.approve_trust_relationship(
            relationship=relationship,
            approving_org=college,
            approving_user=college_admin
        )
        
        relationship.refresh_from_db()
        self.assertEqual(relationship.status, 'active')
        self.assertTrue(relationship.is_effective())
        
        # Step 5: Test intelligence access
        can_access, reason, rel = CRISPIntegrationService.can_user_access_intelligence(
            user=university_admin,
            intelligence_owner_org_id=str(college.id),
            required_access_level='read'
        )
        
        self.assertTrue(can_access)
        self.assertIn('Access granted', reason)
        
        # Step 6: Verify comprehensive dashboard data
        dashboard = CRISPIntegrationService.get_organization_trust_dashboard_data(university)
        
        self.assertEqual(dashboard['relationships']['total'], 1)
        self.assertEqual(dashboard['relationships']['active'], 1)
        self.assertEqual(len(dashboard['partners']), 1)
        self.assertEqual(dashboard['partners'][0].name, 'Test College')
        
        # Step 7: Verify audit trail
        logs = TrustLog.objects.filter(
            source_organization=university.id
        ).order_by('created_at')
        
        # Should have logs for: org creation, user invitation, relationship creation, approvals
        self.assertGreaterEqual(logs.count(), 3)
        
        action_types = [log.action for log in logs]
        self.assertIn('organization_created', action_types)
        self.assertIn('user_invited', action_types)
        self.assertIn('relationship_created', action_types)
    
    def test_multi_organization_trust_network(self):
        """Test complex trust network with multiple organizations"""
        # Create multiple organizations
        orgs = []
        admins = []
        
        for i in range(4):
            admin_data = {
                'username': f'admin{i}',
                'email': f'admin{i}@org{i}.edu',
                'password': f'pass{i}123',
                'first_name': f'Admin{i}',
                'last_name': 'User'
            }
            
            org = CRISPIntegrationService.create_organization_with_trust_setup(
                name=f'Organization {i}',
                domain=f'org{i}.edu',
                contact_email=f'contact@org{i}.edu',
                admin_user_data=admin_data,
                institution_type='university'
            )
            
            orgs.append(org)
            admins.append(User.objects.get(email=f'admin{i}@org{i}.edu'))
        
        # Create trust relationships: 0->1, 1->2, 2->3, 0->3 (network)
        relationships = []
        
        # Org 0 -> Org 1
        rel1 = CRISPIntegrationService.create_trust_relationship(
            source_org=orgs[0], target_org=orgs[1],
            trust_level_name='Public Sharing',
            created_by_user=admins[0]
        )
        
        # Org 1 -> Org 2
        rel2 = CRISPIntegrationService.create_trust_relationship(
            source_org=orgs[1], target_org=orgs[2],
            trust_level_name='Trusted Partnership',
            created_by_user=admins[1]
        )
        
        # Org 2 -> Org 3
        rel3 = CRISPIntegrationService.create_trust_relationship(
            source_org=orgs[2], target_org=orgs[3],
            trust_level_name='Public Sharing',
            created_by_user=admins[2]
        )
        
        # Org 0 -> Org 3 (direct)
        rel4 = CRISPIntegrationService.create_trust_relationship(
            source_org=orgs[0], target_org=orgs[3],
            trust_level_name='Trusted Partnership',
            created_by_user=admins[0]
        )
        
        relationships = [rel1, rel2, rel3, rel4]
        
        # Approve all relationships
        for rel in relationships:
            source_idx = next(i for i, org in enumerate(orgs) if org.id == rel.source_organization)
            target_idx = next(i for i, org in enumerate(orgs) if org.id == rel.target_organization)
            
            CRISPIntegrationService.approve_trust_relationship(
                relationship=rel, approving_org=orgs[source_idx], approving_user=admins[source_idx]
            )
            CRISPIntegrationService.approve_trust_relationship(
                relationship=rel, approving_org=orgs[target_idx], approving_user=admins[target_idx]
            )
        
        # Test access patterns
        # Org 0 should have direct access to Org 1 and Org 3
        sources_0 = CRISPIntegrationService.get_user_accessible_intelligence_sources(admins[0])
        accessible_org_names_0 = [source['organization'].name for source in sources_0]
        
        self.assertIn('Organization 1', accessible_org_names_0)
        self.assertIn('Organization 3', accessible_org_names_0)
        self.assertEqual(len(accessible_org_names_0), 2)  # Direct relationships only
        
        # Test dashboard for org with multiple relationships
        dashboard_0 = CRISPIntegrationService.get_organization_trust_dashboard_data(orgs[0])
        self.assertEqual(dashboard_0['relationships']['total'], 2)
        self.assertEqual(dashboard_0['relationships']['active'], 2)
        
        # Verify all relationships are logged
        total_logs = TrustLog.objects.filter(action='relationship_created').count()
        self.assertEqual(total_logs, 4)  # One for each relationship
