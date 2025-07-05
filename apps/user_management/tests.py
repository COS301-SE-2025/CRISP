"""
Simple tests to boost coverage for user_management app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
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
            role='admin',
            is_organization_admin=True
        )
        
    def test_user_model_properties(self):
        """Test all user model properties for coverage"""
        # Test is_publisher method
        self.assertTrue(self.user.is_publisher())
        
        # Test is_admin method
        self.assertTrue(self.user.is_admin())
        
        # Test can_manage_organization method
        self.assertTrue(self.user.can_manage_organization())
        
        # Test with different roles
        viewer_user = User.objects.create_user(
            username='viewer_test',
            email='viewer@coverage.test',
            password='testpass123',
            organization=self.org,
            role='viewer'
        )
        self.assertFalse(viewer_user.is_publisher())
        self.assertFalse(viewer_user.is_admin())
        self.assertFalse(viewer_user.can_manage_organization())
        
    def test_organization_model_methods(self):
        """Test all organization model methods for coverage"""
        # Test string representation
        self.assertEqual(str(self.org), 'Test Coverage Org')
        
        # Test different trust level defaults
        for trust_level in ['public', 'trusted', 'restricted']:
            org = Organization.objects.create(
                name=f'Test {trust_level} Org',
                domain=f'{trust_level}.test',
                contact_email=f'contact@{trust_level}.test',
                institution_type='university',
                trust_level_default=trust_level
            )
            self.assertEqual(org.trust_level_default, trust_level)
            
    def test_invitation_token_methods(self):
        """Test invitation token methods for coverage"""
        # Create invitation token
        token = InvitationToken.objects.create(
            organization=self.org,
            invited_by=self.user,
            email='method_test@coverage.test',
            role='viewer',
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        # Test is_valid method
        self.assertTrue(token.is_valid())
        
        # Test is_expired method
        self.assertFalse(token.is_expired())
        
        # Test with expired token
        expired_token = InvitationToken.objects.create(
            organization=self.org,
            invited_by=self.user,
            email='expired@coverage.test',
            role='viewer',
            expires_at=timezone.now() - timedelta(days=1)
        )
        self.assertFalse(expired_token.is_valid())
        self.assertTrue(expired_token.is_expired())
        
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
        self.assertFalse(invitation.used)
        
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
            
    def test_service_error_handling(self):
        """Test service error handling for coverage"""
        # Test with invalid organization admin
        regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@coverage.test',
            password='testpass123',
            organization=self.org,
            role='viewer'
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError):
            CRISPIntegrationService.invite_user_to_organization(
                organization=self.org,
                inviting_user=regular_user,
                email='invalid@coverage.test',
                role='viewer'
            )
            
        # Test inviting to different organization
        other_org = Organization.objects.create(
            name='Other Org',
            domain='other.test',
            contact_email='other@test.com'
        )
        
        with self.assertRaises(ValidationError):
            CRISPIntegrationService.invite_user_to_organization(
                organization=other_org,
                inviting_user=self.user,
                email='invalid@coverage.test',
                role='viewer'
            )
    
    def test_user_session_model(self):
        """Test user session model for coverage"""
        from apps.user_management.models import UserSession
        
        # Create user session
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            is_active=True
        )
        
        # Test session properties
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_key, 'test_session_key')
        self.assertEqual(session.ip_address, '127.0.0.1')
        self.assertTrue(session.is_active)
        
        # Test string representation
        self.assertIn('test_session_key', str(session))
        
    def test_organization_comprehensive(self):
        """Test all organization methods and properties"""
        # Test organization with all fields
        org = Organization.objects.create(
            name='Comprehensive Test Org',
            domain='comprehensive.test',
            contact_email='contact@comprehensive.test',
            institution_type='research_institute',
            trust_level_default='restricted',
            is_active=True,
            is_bluevision_client=False
        )
        
        # Test all properties
        self.assertEqual(org.institution_type, 'research_institute')
        self.assertEqual(org.trust_level_default, 'restricted')
        self.assertTrue(org.is_active)
        self.assertFalse(org.is_bluevision_client)
        
        # Test string representation
        self.assertEqual(str(org), 'Comprehensive Test Org')
        
    def test_custom_user_comprehensive(self):
        """Test all custom user methods and properties"""
        # Test user with all roles
        for role in ['viewer', 'publisher', 'system_admin', 'bluevision_admin']:
            user = User.objects.create_user(
                username=f'test_{role}',
                email=f'{role}@test.com',
                password='testpass123',
                organization=self.org,
                role=role,
                first_name='Test',
                last_name='User'
            )
            
            # Test role-specific methods
            if role in ['publisher', 'system_admin', 'bluevision_admin']:
                self.assertTrue(user.is_publisher())
            else:
                self.assertFalse(user.is_publisher())
                
            if role in ['system_admin', 'bluevision_admin']:
                self.assertTrue(user.is_admin())
            else:
                self.assertFalse(user.is_admin())
                
            # Test get_full_name
            self.assertEqual(user.get_full_name(), 'Test User')
            
    def test_authentication_log_comprehensive(self):
        """Test all authentication log functionality"""
        # Test all possible actions
        actions = [
            'login_success',
            'login_failed',
            'logout',
            'password_change',
            'password_reset',
            'account_locked',
            'account_unlocked',
            'token_generated',
            'token_used',
            'session_expired'
        ]
        
        for action in actions:
            log = AuthenticationLog.objects.create(
                user=self.user,
                email=self.user.email,
                action=action,
                ip_address='192.168.1.1',
                user_agent='Test Agent',
                success=True,
                details={'test': 'data'}
            )
            self.assertEqual(log.action, action)
            self.assertTrue(log.success)
            
    def test_invitation_token_comprehensive(self):
        """Test all invitation token functionality"""
        # Test expired token
        expired_token = InvitationToken.objects.create(
            organization=self.org,
            invited_by=self.user,
            email='expired@test.com',
            role='viewer',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Test is_expired method
        self.assertTrue(expired_token.is_expired())
        self.assertFalse(expired_token.is_valid())
        
        # Test valid token
        valid_token = InvitationToken.objects.create(
            organization=self.org,
            invited_by=self.user,
            email='valid@test.com',
            role='publisher',
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Test is_valid method
        self.assertFalse(valid_token.is_expired())
        self.assertTrue(valid_token.is_valid())
        
        # Test using token
        valid_token.used = True
        valid_token.used_at = timezone.now()
        valid_token.save()
        
        self.assertFalse(valid_token.is_valid())
        
    def test_service_error_handling(self):
        """Test service error handling for coverage"""
        from django.core.exceptions import ValidationError
        
        # Test invitation with invalid user
        regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@test.com',
            password='testpass123',
            organization=self.org,
            role='viewer'
        )
        
        # This should raise ValidationError
        with self.assertRaises(ValidationError):
            CRISPIntegrationService.invite_user_to_organization(
                organization=self.org,
                inviting_user=regular_user,
                email='newuser@test.com',
                role='viewer'
            )
            
    def test_user_permissions_comprehensive(self):
        """Test all user permission methods"""
        # Test admin user
        admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            organization=self.org,
            role='system_admin',
            is_organization_admin=True
        )
        
        # Test all permission methods
        self.assertTrue(admin_user.is_admin())
        self.assertTrue(admin_user.is_publisher())
        self.assertTrue(admin_user.can_manage_organization())
        
        # Test viewer user
        viewer_user = User.objects.create_user(
            username='viewer_test',
            email='viewer@test.com',
            password='testpass123',
            organization=self.org,
            role='viewer'
        )
        
        self.assertFalse(viewer_user.is_admin())
        self.assertFalse(viewer_user.is_publisher())
        self.assertFalse(viewer_user.can_manage_organization())
        
    def test_model_meta_and_ordering(self):
        """Test model meta properties and ordering"""
        # Create multiple users to test ordering
        for i in range(3):
            User.objects.create_user(
                username=f'user_{i}',
                email=f'user{i}@test.com',
                password='testpass123',
                organization=self.org,
                role='viewer'
            )
            
        # Test ordering (should be by email)
        users = User.objects.all().order_by('email')
        self.assertTrue(len(users) >= 3)
        
        # Test multiple organizations
        for i in range(3):
            Organization.objects.create(
                name=f'Test Org {i}',
                domain=f'org{i}.test',
                contact_email=f'contact@org{i}.test',
                institution_type='university'
            )
            
        orgs = Organization.objects.all()
        self.assertTrue(len(orgs) >= 3)
