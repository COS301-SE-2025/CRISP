import os
import sys
import django

# Add the project root to Python path for standalone execution
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, project_root)
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
    django.setup()

from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import MagicMock, patch

try:
    from ..models import CustomUser, Organization
except ImportError:
    # Fallback for standalone execution
    from core.models import CustomUser, Organization
try:
    from ..factories.user_factory import (
        UserFactory, StandardUserCreator, PublisherUserCreator, AdminUserCreator
    )
except ImportError:
    # Fallback for standalone execution
    from core.factories.user_factory import (
        UserFactory, StandardUserCreator, PublisherUserCreator, AdminUserCreator
    )
try:
    from ..serializers import (
        UserRegistrationSerializer, AdminUserCreateSerializer, AdminUserUpdateSerializer
    )
except ImportError:
    # Fallback for standalone execution
    from core.serializers import (
        UserRegistrationSerializer, AdminUserCreateSerializer, AdminUserUpdateSerializer
    )


class UserFactoryTestCase(TestCase):
    """Test user factory patterns"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin',
            is_verified=True
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_standard_user_creation(self):
        """Test creating standard user"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'organization': self.organization
        }
        
        user = UserFactory.create_user('viewer', user_data, self.admin_user)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'viewer')
        self.assertFalse(user.is_publisher)
        self.assertFalse(user.is_verified)  # Standard users need admin verification
    
    def test_publisher_user_creation(self):
        """Test creating publisher user"""
        user_data = {
            'username': 'publisher',
            'email': 'publisher@example.com',
            'password': 'PublisherPassword123!',
            'first_name': 'Publisher',
            'last_name': 'User',
            'organization': self.organization
        }
        
        user = UserFactory.create_user('publisher', user_data, self.admin_user)
        
        self.assertEqual(user.username, 'publisher')
        self.assertEqual(user.role, 'publisher')
        self.assertTrue(user.is_publisher)
        self.assertTrue(user.is_verified)  # Publishers are verified by default
    
    def test_admin_user_creation(self):
        """Test creating admin user"""
        user_data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'AdminPassword123!',
            'first_name': 'New',
            'last_name': 'Admin',
            'organization': self.organization,
            'role': 'BlueVisionAdmin'
        }
        
        user = UserFactory.create_user('BlueVisionAdmin', user_data, self.admin_user)
        
        self.assertEqual(user.username, 'newadmin')
        self.assertEqual(user.role, 'BlueVisionAdmin')
        self.assertTrue(user.is_publisher)
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_staff)
    
    def test_auto_password_generation(self):
        """Test user creation with auto-generated password"""
        user_data = {
            'username': 'autouser',
            'email': 'auto@example.com',
            'first_name': 'Auto',
            'last_name': 'User',
            'organization': self.organization
        }
        
        user, password = UserFactory.create_user_with_auto_password(
            'viewer', user_data, self.admin_user
        )
        
        self.assertEqual(user.username, 'autouser')
        self.assertIsNotNone(password)
        self.assertGreaterEqual(len(password), 12)
        # Verify user can login with generated password
        self.assertTrue(user.check_password(password))
    
    def test_unauthorized_user_creation(self):
        """Test unauthorized user creation"""
        regular_user = CustomUser.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='RegularPassword123!',
            organization=self.organization,
            role='viewer',
            is_verified=True
        )
        
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'organization': self.organization
        }
        
        with self.assertRaises(ValidationError):
            UserFactory.create_user('viewer', user_data, regular_user)
    
    def test_invalid_role_creation(self):
        """Test creating user with invalid role"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'organization': self.organization
        }
        
        with self.assertRaises(ValidationError):
            UserFactory.create_user('invalid_role', user_data, self.admin_user)


class UserCreatorTestCase(TestCase):
    """Test individual user creators"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_standard_user_creator(self):
        """Test StandardUserCreator"""
        creator = StandardUserCreator()
        
        user_data = {
            'username': 'standard',
            'email': 'standard@example.com',
            'password': 'StandardPassword123!',
            'organization': self.organization
        }
        
        user = creator.create_user(user_data)
        
        self.assertEqual(user.role, 'viewer')
        self.assertFalse(user.is_publisher)
    
    def test_publisher_user_creator(self):
        """Test PublisherUserCreator"""
        creator = PublisherUserCreator()
        
        user_data = {
            'username': 'publisher',
            'email': 'publisher@example.com',
            'password': 'PublisherPassword123!',
            'first_name': 'Publisher',
            'last_name': 'User',
            'organization': self.organization
        }
        
        user = creator.create_user(user_data)
        
        self.assertEqual(user.role, 'publisher')
        self.assertTrue(user.is_publisher)
        self.assertTrue(user.is_verified)
    
    def test_admin_user_creator(self):
        """Test AdminUserCreator"""
        system_admin = CustomUser.objects.create_user(
            username='sysadmin',
            email='sysadmin@example.com',
            password='SysAdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin',
            is_verified=True
        )
        
        creator = AdminUserCreator()
        
        user_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'AdminPassword123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'organization': self.organization,
            'role': 'BlueVisionAdmin',
            'created_by': system_admin
        }
        
        user = creator.create_user(user_data)
        
        self.assertEqual(user.role, 'BlueVisionAdmin')
        self.assertTrue(user.is_staff)
    
    def test_creator_validation_errors(self):
        """Test validation errors in creators"""
        creator = StandardUserCreator()
        
        # Missing required fields
        with self.assertRaises(ValidationError):
            creator.create_user({})
        
        # Invalid email
        with self.assertRaises(ValidationError):
            creator.create_user({
                'username': 'test',
                'email': 'invalid-email',
                'password': 'TestPassword123!',
                'organization': self.organization
            })
        
        # Duplicate username
        CustomUser.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='ExistingPassword123!',
            organization=self.organization
        )
        
        with self.assertRaises(ValidationError):
            creator.create_user({
                'username': 'existing',
                'email': 'new@example.com',
                'password': 'TestPassword123!',
                'organization': self.organization
            })


class UserPermissionTestCase(TestCase):
    """Test user permission methods"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_can_publish_feeds(self):
        """Test can_publish_feeds method"""
        # Publisher should be able to publish
        publisher = CustomUser.objects.create_user(
            username='publisher',
            email='publisher@example.com',
            password='PublisherPassword123!',
            organization=self.organization,
            role='publisher',
            is_publisher=True
        )
        self.assertTrue(publisher.can_publish_feeds())
        
        # BlueVision Admin should be able to publish
        admin = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin',
            is_publisher=True
        )
        self.assertTrue(admin.can_publish_feeds())
        
        # Regular user should not be able to publish
        viewer = CustomUser.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='ViewerPassword123!',
            organization=self.organization,
            role='viewer',
            is_publisher=False
        )
        self.assertFalse(viewer.can_publish_feeds())
    
    def test_is_organization_admin(self):
        """Test is_organization_admin method"""
        admin = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin'
        )
        self.assertTrue(admin.is_organization_admin())
        
        system_admin = CustomUser.objects.create_user(
            username='sysadmin',
            email='sysadmin@example.com',
            password='SysAdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin'
        )
        self.assertTrue(system_admin.is_organization_admin())
        
        publisher = CustomUser.objects.create_user(
            username='publisher',
            email='publisher@example.com',
            password='PublisherPassword123!',
            organization=self.organization,
            role='publisher'
        )
        self.assertFalse(publisher.is_organization_admin())


class UserSerializerTestCase(TestCase):
    """Test user serializers"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_user_registration_serializer_valid(self):
        """Test valid user registration serializer"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewUserPassword123!',
            'password_confirm': 'NewUserPassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'organization_id': str(self.organization.id),
            'role': 'viewer'
        }
        
        with patch('core.models.Organization') as mock_org:
            mock_org.objects.get.return_value = self.organization
            
            serializer = UserRegistrationSerializer(data=data)
            self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_user_registration_serializer_password_mismatch(self):
        """Test user registration with password mismatch"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewUserPassword123!',
            'password_confirm': 'DifferentPassword123!',
            'organization_id': str(self.organization.id)
        }
        
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Passwords do not match', str(serializer.errors))
    
    def test_admin_user_create_serializer(self):
        """Test admin user creation serializer"""
        data = {
            'username': 'adminuser',
            'email': 'adminuser@example.com',
            'password': 'AdminUserPassword123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'organization_id': str(self.organization.id),
            'role': 'BlueVisionAdmin',
            'is_publisher': True,
            'is_verified': True
        }
        
        with patch('core.models.Organization') as mock_org:
            mock_org.objects.get.return_value = self.organization
            
            serializer = AdminUserCreateSerializer(data=data)
            self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_admin_user_update_serializer(self):
        """Test admin user update serializer"""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization
        )
        
        data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'is_verified': True
        }
        
        serializer = AdminUserUpdateSerializer(user, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class UserModelTestCase(TestCase):
    """Test CustomUser model methods"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_user_string_representation(self):
        """Test user string representation"""
        expected = f"{self.user.username} ({self.organization.name})"
        self.assertEqual(str(self.user), expected)
    
    def test_user_creation_defaults(self):
        """Test user creation defaults"""
        self.assertEqual(self.user.role, 'viewer')
        self.assertFalse(self.user.is_publisher)
        self.assertFalse(self.user.is_verified)
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertFalse(self.user.two_factor_enabled)
        self.assertEqual(self.user.trusted_devices, [])
    
    def test_user_account_lock_check(self):
        """Test account lock checking"""
        # Account should not be locked initially
        self.assertFalse(self.user.is_account_locked)
        
        # Lock account and check
        self.user.lock_account()
        self.assertTrue(self.user.is_account_locked)
    
    def test_user_role_hierarchy(self):
        """Test user role hierarchy"""
        roles = ['viewer', 'publisher', 'BlueVisionAdmin']
        
        for role in roles:
            user = CustomUser.objects.create_user(
                username=f'{role}_user',
                email=f'{role}@example.com',
                password=f'{role.title()}Password123!',
                organization=self.organization,
                role=role
            )
            self.assertEqual(user.role, role)


class UserBulkOperationsTestCase(TestCase):
    """Test bulk user operations"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.admin = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin',
            is_verified=True
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_bulk_user_creation(self):
        """Test creating multiple users"""
        users_data = [
            {
                'username': f'user{i}',
                'email': f'user{i}@example.com',
                'password': f'User{i}Password123!',
                'organization': self.organization
            }
            for i in range(5)
        ]
        
        created_users = []
        for user_data in users_data:
            user = UserFactory.create_user('viewer', user_data, self.admin)
            created_users.append(user)
        
        self.assertEqual(len(created_users), 5)
        for user in created_users:
            self.assertEqual(user.role, 'viewer')
    
    def test_bulk_user_verification(self):
        """Test bulk user verification"""
        # Create unverified users
        users = []
        for i in range(3):
            user = CustomUser.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password=f'User{i}Password123!',
                organization=self.organization,
                is_verified=False
            )
            users.append(user)
        
        # Bulk verify
        user_ids = [user.id for user in users]
        CustomUser.objects.filter(id__in=user_ids).update(is_verified=True)
        
        # Check verification
        for user in users:
            user.refresh_from_db()
            self.assertTrue(user.is_verified)
    
    def test_bulk_user_deactivation(self):
        """Test bulk user deactivation"""
        # Create active users
        users = []
        for i in range(3):
            user = CustomUser.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password=f'User{i}Password123!',
                organization=self.organization,
                is_active=True
            )
            users.append(user)
        
        # Bulk deactivate
        user_ids = [user.id for user in users]
        CustomUser.objects.filter(id__in=user_ids).update(is_active=False)
        
        # Check deactivation
        for user in users:
            user.refresh_from_db()
            self.assertFalse(user.is_active)


if __name__ == '__main__':
    import unittest
    unittest.main()