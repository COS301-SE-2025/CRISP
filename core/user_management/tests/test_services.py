from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from ..services.user_service import UserService
from ..services.organization_service import OrganizationService
from ..services.access_control_service import AccessControlService
from ..factories.user_factory import UserFactory, OrganizationFactory


User = get_user_model()


class UserServiceTest(TestCase):
    """Test cases for UserService"""
    
    def setUp(self):
        self.user_service = UserService()
        self.organization = OrganizationFactory()
        self.admin_user = UserFactory(
            role='BlueVisionAdmin',
            organization=self.organization
        )
    
    def test_create_user(self):
        """Test creating a user through service"""
        user_data = {
            'username': 'newuser@example.com',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'viewer',
            'organization_id': str(self.organization.id)
        }
        
        user = self.user_service.create_user(
            creating_user=self.admin_user,
            user_data=user_data
        )
        
        self.assertEqual(user.username, 'newuser@example.com')
        self.assertEqual(user.role, 'viewer')
        self.assertEqual(user.organization, self.organization)
    
    def test_get_user_details(self):
        """Test getting user details"""
        user = UserFactory(organization=self.organization)
        
        details = self.user_service.get_user_details(
            requesting_user=self.admin_user,
            user_id=str(user.id)
        )
        
        self.assertEqual(details['id'], str(user.id))
        self.assertEqual(details['username'], user.username)
        self.assertEqual(details['role'], user.role)


class OrganizationServiceTest(TestCase):
    """Test cases for OrganizationService"""
    
    def setUp(self):
        self.org_service = OrganizationService()
        self.admin_user = UserFactory(role='BlueVisionAdmin')
    
    def test_create_organization(self):
        """Test creating organization through service"""
        org_data = {
            'name': 'New Organization',
            'domain': 'neworg.com',
            'contact_email': 'contact@neworg.com',
            'organization_type': 'private',
            'primary_user': {
                'username': 'admin@neworg.com',
                'email': 'admin@neworg.com',
                'password': 'adminpass123',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        }
        
        organization, primary_user = self.org_service.create_organization(
            creating_user=self.admin_user,
            org_data=org_data
        )
        
        self.assertEqual(organization.name, 'New Organization')
        self.assertEqual(primary_user.username, 'admin@neworg.com')
        self.assertEqual(primary_user.role, 'publisher')
        self.assertEqual(primary_user.organization, organization)


class AccessControlServiceTest(TestCase):
    """Test cases for AccessControlService"""
    
    def setUp(self):
        self.access_control = AccessControlService()
        self.organization = OrganizationFactory()
        
        self.viewer = UserFactory(
            role='viewer',
            organization=self.organization
        )
        self.publisher = UserFactory(
            role='publisher',
            organization=self.organization
        )
        self.admin = UserFactory(
            role='BlueVisionAdmin',
            organization=self.organization
        )
    
    def test_viewer_permissions(self):
        """Test viewer role permissions"""
        # Viewers can view their own organization data
        self.assertTrue(
            self.access_control.has_permission(
                self.viewer, 'can_view_organization_data'
            )
        )
        
        # Viewers cannot create users
        self.assertFalse(
            self.access_control.has_permission(
                self.viewer, 'can_create_organization_users'
            )
        )
    
    def test_publisher_permissions(self):
        """Test publisher role permissions"""
        # Publishers can create users in their organization
        self.assertTrue(
            self.access_control.has_permission(
                self.publisher, 'can_create_organization_users'
            )
        )
        
        # Publishers can manage trust relationships
        self.assertTrue(
            self.access_control.has_permission(
                self.publisher, 'can_manage_trust_relationships'
            )
        )
        
        # Publishers cannot view system analytics
        self.assertFalse(
            self.access_control.has_permission(
                self.publisher, 'can_view_system_analytics'
            )
        )
    
    def test_admin_permissions(self):
        """Test admin role permissions"""
        # Admins can do everything
        self.assertTrue(
            self.access_control.has_permission(
                self.admin, 'can_view_system_analytics'
            )
        )
        
        self.assertTrue(
            self.access_control.has_permission(
                self.admin, 'can_manage_all_users'
            )
        )
        
        self.assertTrue(
            self.access_control.has_permission(
                self.admin, 'can_create_organizations'
            )
        )
    
    def test_role_hierarchy(self):
        """Test that higher roles inherit lower role permissions"""
        # Publisher should have all viewer permissions
        viewer_permissions = self.access_control.get_user_permissions(self.viewer)
        publisher_permissions = self.access_control.get_user_permissions(self.publisher)
        
        for permission in viewer_permissions:
            self.assertIn(permission, publisher_permissions)
        
        # Admin should have all publisher permissions
        admin_permissions = self.access_control.get_user_permissions(self.admin)
        
        for permission in publisher_permissions:
            self.assertIn(permission, admin_permissions)