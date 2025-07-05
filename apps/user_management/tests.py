"""
Simple tests to boost coverage for user_management app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.user_management.models import Organization, InvitationToken, AuthenticationLog
from apps.core.services import CRISPIntegrationService
import uuid


User = get_user_model()


class UserManagementCoverageTest(TestCase):
    """Test to boost coverage for user management components"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name='Test Coverage Org',
            domain='coverage.test',
            contact_email='contact@coverage.test',
            institution_type='university'
        )
        
        self.user = User.objects.create_user(
            username='coverage_user',
            email='coverage@coverage.test',
            password='testpass123',
            organization=self.org,
            role='admin'
        )
        
    def test_organization_model_methods(self):
        """Test organization model methods"""
        # Test string representation
        self.assertEqual(str(self.org), 'Test Coverage Org')
        
        # Test organization fields
        self.assertEqual(self.org.institution_type, 'university')
        self.assertEqual(self.org.trust_level_default, 'public')
        self.assertTrue(self.org.is_active)
        self.assertTrue(self.org.is_bluevision_client)
        
    def test_custom_user_model_methods(self):
        """Test custom user model methods"""
        # Test user properties
        self.assertEqual(self.user.organization, self.org)
        self.assertEqual(self.user.role, 'admin')
        self.assertFalse(self.user.is_organization_admin)
        
        # Test user methods
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(self.user.get_full_name(), '')  # Empty string since no first/last name set
        
    def test_invitation_token_model(self):
        """Test invitation token model"""
        # Create invitation token
        token = InvitationToken.objects.create(
            organization=self.org,
            invited_by=self.user,
            email='invited@coverage.test',
            role='viewer'
        )
        
        # Test token properties
        self.assertEqual(token.organization, self.org)
        self.assertEqual(token.invited_by, self.user)
        self.assertEqual(token.email, 'invited@coverage.test')
        self.assertEqual(token.role, 'viewer')
        self.assertFalse(token.is_used)
        
        # Test token string representation
        self.assertIn('invited@coverage.test', str(token))
        
    def test_authentication_log_model(self):
        """Test authentication log model"""
        # Create authentication log
        log = AuthenticationLog.objects.create(
            user=self.user,
            email=self.user.email,
            action='login_success',
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            success=True
        )
        
        # Test log properties
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.email, self.user.email)
        self.assertEqual(log.action, 'login_success')
        self.assertTrue(log.success)
        
        # Test log string representation
        self.assertIn('login_success', str(log))
        
    def test_integration_service_methods(self):
        """Test integration service methods for coverage"""
        # Test organization creation
        admin_data = {
            'username': 'test_admin',
            'email': 'admin@test.coverage',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Admin'
        }
        
        org = CRISPIntegrationService.create_organization_with_trust_setup(
            name='Integration Test Org',
            domain='integration.test',
            contact_email='contact@integration.test',
            admin_user_data=admin_data,
            institution_type='university'
        )
        
        # Verify organization was created
        self.assertEqual(org.name, 'Integration Test Org')
        self.assertEqual(org.domain, 'integration.test')
        
        # Verify admin user was created
        admin_user = User.objects.get(email='admin@test.coverage')
        self.assertEqual(admin_user.organization, org)
        self.assertEqual(admin_user.role, 'publisher')
        
    def test_user_invitation_workflow(self):
        """Test user invitation workflow"""
        # Create invitation
        invitation = CRISPIntegrationService.invite_user_to_organization(
            organization=self.org,
            inviting_user=self.user,
            email='newuser@coverage.test',
            role='viewer'
        )
        
        # Verify invitation
        self.assertEqual(invitation.organization, self.org)
        self.assertEqual(invitation.invited_by, self.user)
        self.assertEqual(invitation.email, 'newuser@coverage.test')
        self.assertEqual(invitation.role, 'viewer')
        self.assertFalse(invitation.is_used)
        
    def test_model_edge_cases(self):
        """Test model edge cases for coverage"""
        # Test organization with different types
        org_types = ['college', 'school', 'research_institute', 'other']
        for org_type in org_types:
            org = Organization.objects.create(
                name=f'Test {org_type} Org',
                domain=f'{org_type}.test',
                contact_email=f'contact@{org_type}.test',
                institution_type=org_type
            )
            self.assertEqual(org.institution_type, org_type)
            
        # Test user with different roles
        user_roles = ['viewer', 'publisher', 'admin']
        for role in user_roles:
            user = User.objects.create_user(
                username=f'{role}_user',
                email=f'{role}@coverage.test',
                password='testpass123',
                organization=self.org,
                role=role
            )
            self.assertEqual(user.role, role)
            
    def test_authentication_log_actions(self):
        """Test different authentication log actions"""
        actions = ['login_success', 'login_failed', 'logout', 'password_reset', 'account_locked', 'account_unlocked']
        
        for action in actions:
            log = AuthenticationLog.objects.create(
                user=self.user,
                email=self.user.email,
                action=action,
                ip_address='127.0.0.1',
                user_agent='Test Agent',
                success=(action in ['login_success', 'logout', 'password_reset', 'account_unlocked'])
            )
            self.assertEqual(log.action, action)
            
    def test_trust_level_defaults(self):
        """Test trust level defaults"""
        trust_levels = ['public', 'trusted', 'restricted']
        
        for level in trust_levels:
            org = Organization.objects.create(
                name=f'Test {level} Org',
                domain=f'{level}.test',
                contact_email=f'contact@{level}.test',
                trust_level_default=level
            )
            self.assertEqual(org.trust_level_default, level)
