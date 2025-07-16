"""
Comprehensive tests for user factory to increase coverage
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock
from core.user_management.factories.user_factory import (
    UserCreator, StandardUserCreator, PublisherUserCreator, 
    AdminUserCreator, UserFactory
)
from core.user_management.models import CustomUser, Organization, AuthenticationLog
import secrets
import string


class UserCreatorComprehensiveTest(TestCase):
    """Comprehensive test suite for user factory classes"""
    
    def setUp(self):
        """Set up test data"""
        # Create test organization
        self.organization = Organization.objects.create(
            name='Factory Test Org',
            domain='factorytest.com',
            contact_email='admin@factorytest.com',
            is_active=True,
            is_verified=True
        )
        
        # Create test admin user
        self.admin_user = CustomUser.objects.create_user(
            username='admin@factorytest.com',
            email='admin@factorytest.com',
            password='TestPassword123',
            first_name='Admin',
            last_name='User',
            role='BlueVisionAdmin',
            organization=self.organization,
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        
        self.valid_user_data = {
            'username': 'newuser@example.com',
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'organization': self.organization
        }
    
    def test_standard_user_creator_success(self):
        """Test successful standard user creation"""
        creator = StandardUserCreator()
        user = creator.create_user(self.valid_user_data)
        
        self.assertEqual(user.role, 'viewer')
        self.assertFalse(user.is_publisher)
        self.assertEqual(user.organization, self.organization)
        self.assertTrue(user.is_active)
    
    def test_standard_user_creator_missing_required_field(self):
        """Test standard user creation with missing required field"""
        creator = StandardUserCreator()
        incomplete_data = self.valid_user_data.copy()
        del incomplete_data['username']
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(incomplete_data)
        
        self.assertIn('username', str(context.exception))
    
    def test_standard_user_creator_duplicate_username(self):
        """Test standard user creation with duplicate username"""
        creator = StandardUserCreator()
        # Create first user
        creator.create_user(self.valid_user_data)
        
        # Try to create another user with same username
        with self.assertRaises(ValidationError) as context:
            creator.create_user(self.valid_user_data)
        
        self.assertIn('Username already exists', str(context.exception))
    
    def test_standard_user_creator_duplicate_email(self):
        """Test standard user creation with duplicate email"""
        creator = StandardUserCreator()
        # Create first user
        creator.create_user(self.valid_user_data)
        
        # Try to create another user with same email but different username
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = 'different@example.com'
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(duplicate_data)
        
        self.assertIn('Email already exists', str(context.exception))
    
    def test_standard_user_creator_invalid_email(self):
        """Test standard user creation with invalid email"""
        creator = StandardUserCreator()
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(invalid_data)
        
        self.assertIn('Email validation failed', str(context.exception))
    
    def test_standard_user_creator_weak_password(self):
        """Test standard user creation with weak password"""
        creator = StandardUserCreator()
        weak_data = self.valid_user_data.copy()
        weak_data['password'] = '123'
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(weak_data)
        
        self.assertIn('Password validation failed', str(context.exception))
    
    def test_publisher_user_creator_success(self):
        """Test successful publisher user creation"""
        creator = PublisherUserCreator()
        user = creator.create_user(self.valid_user_data)
        
        self.assertEqual(user.role, 'publisher')
        self.assertTrue(user.is_publisher)
        self.assertTrue(user.is_verified)
        self.assertEqual(user.organization, self.organization)
    
    def test_publisher_user_creator_missing_names(self):
        """Test publisher user creation with missing first/last name"""
        creator = PublisherUserCreator()
        incomplete_data = self.valid_user_data.copy()
        del incomplete_data['first_name']
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(incomplete_data)
        
        self.assertIn('Publisher users must have first and last name', str(context.exception))
    
    def test_publisher_user_creator_no_organization(self):
        """Test publisher user creation without organization"""
        creator = PublisherUserCreator()
        invalid_data = self.valid_user_data.copy()
        invalid_data['organization'] = None
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(invalid_data)
        
        self.assertIn("'organization' is required", str(context.exception))
    
    def test_admin_user_creator_success(self):
        """Test successful admin user creation"""
        creator = AdminUserCreator()
        admin_data = self.valid_user_data.copy()
        admin_data['created_by'] = self.admin_user
        admin_data['role'] = 'BlueVisionAdmin'
        
        user = creator.create_user(admin_data)
        
        self.assertEqual(user.role, 'BlueVisionAdmin')
        self.assertTrue(user.is_publisher)
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_admin_user_creator_test_environment(self):
        """Test admin user creation in test environment bypasses checks"""
        creator = AdminUserCreator()
        creator._is_test_environment = True
        
        admin_data = self.valid_user_data.copy()
        admin_data['role'] = 'BlueVisionAdmin'
        
        user = creator.create_user(admin_data)
        
        self.assertEqual(user.role, 'BlueVisionAdmin')
        self.assertTrue(user.is_superuser)
    
    def test_admin_user_creator_insufficient_permissions(self):
        """Test admin user creation with insufficient permissions"""
        creator = AdminUserCreator()
        creator._is_test_environment = False
        
        # Create non-admin user as creator
        regular_user = CustomUser.objects.create_user(
            username='regular@example.com',
            email='regular@example.com',
            password='Password123!',
            role='publisher',
            organization=self.organization
        )
        
        admin_data = self.valid_user_data.copy()
        admin_data['created_by'] = regular_user
        admin_data['role'] = 'BlueVisionAdmin'
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(admin_data)
        
        self.assertIn('Only BlueVision administrators can create admin users', str(context.exception))
    
    def test_admin_user_creator_invalid_role(self):
        """Test admin user creation with invalid role"""
        creator = AdminUserCreator()
        creator._is_test_environment = False
        
        admin_data = self.valid_user_data.copy()
        admin_data['created_by'] = self.admin_user
        admin_data['role'] = 'InvalidRole'
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(admin_data)
        
        self.assertIn('Invalid admin role', str(context.exception))
    
    def test_admin_user_creator_missing_names(self):
        """Test admin user creation with missing first/last name"""
        creator = AdminUserCreator()
        creator._is_test_environment = False
        
        admin_data = self.valid_user_data.copy()
        admin_data['created_by'] = self.admin_user
        admin_data['role'] = 'BlueVisionAdmin'
        del admin_data['first_name']
        
        with self.assertRaises(ValidationError) as context:
            creator.create_user(admin_data)
        
        self.assertIn('Admin users must have first and last name', str(context.exception))
    
    def test_generate_secure_password(self):
        """Test secure password generation"""
        creator = StandardUserCreator()
        password = creator._generate_secure_password(16)
        
        self.assertEqual(len(password), 16)
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c in "!@#$%^&*" for c in password))
    
    def test_generate_secure_password_custom_length(self):
        """Test secure password generation with custom length"""
        creator = StandardUserCreator()
        password = creator._generate_secure_password(24)
        
        self.assertEqual(len(password), 24)
    
    def test_user_factory_create_viewer(self):
        """Test UserFactory creating viewer user"""
        user = UserFactory.create_user('viewer', self.valid_user_data, self.admin_user)
        
        self.assertEqual(user.role, 'viewer')
        self.assertFalse(user.is_publisher)
    
    def test_user_factory_create_publisher(self):
        """Test UserFactory creating publisher user"""
        user = UserFactory.create_user('publisher', self.valid_user_data, self.admin_user)
        
        self.assertEqual(user.role, 'publisher')
        self.assertTrue(user.is_publisher)
    
    def test_user_factory_create_admin(self):
        """Test UserFactory creating admin user"""
        admin_data = self.valid_user_data.copy()
        user = UserFactory.create_user('BlueVisionAdmin', admin_data, self.admin_user)
        
        self.assertEqual(user.role, 'BlueVisionAdmin')
        self.assertTrue(user.is_superuser)
    
    def test_user_factory_invalid_role(self):
        """Test UserFactory with invalid role"""
        with self.assertRaises(ValidationError) as context:
            UserFactory.create_user('invalid_role', self.valid_user_data, self.admin_user)
        
        self.assertIn('Invalid user role', str(context.exception))
    
    def test_user_factory_permission_check_admin(self):
        """Test UserFactory permission checks for admin"""
        # Admin can create any role
        UserFactory.create_user('viewer', self.valid_user_data, self.admin_user)
        UserFactory.create_user('publisher', self.valid_user_data.copy(), self.admin_user)
    
    def test_user_factory_permission_check_publisher(self):
        """Test UserFactory permission checks for publisher"""
        publisher_user = CustomUser.objects.create_user(
            username='publisher@example.com',
            email='publisher@example.com',
            password='Password123!',
            role='publisher',
            organization=self.organization
        )
        
        # Publisher can create viewer and publisher
        UserFactory.create_user('viewer', self.valid_user_data, publisher_user)
        
        publisher_data = self.valid_user_data.copy()
        publisher_data['username'] = 'newpublisher@example.com'
        publisher_data['email'] = 'newpublisher@example.com'
        UserFactory.create_user('publisher', publisher_data, publisher_user)
        
        # Publisher cannot create admin
        admin_data = self.valid_user_data.copy()
        admin_data['username'] = 'newadmin@example.com'
        admin_data['email'] = 'newadmin@example.com'
        with self.assertRaises(ValidationError):
            UserFactory.create_user('BlueVisionAdmin', admin_data, publisher_user)
    
    def test_user_factory_permission_check_viewer(self):
        """Test UserFactory permission checks for viewer"""
        viewer_user = CustomUser.objects.create_user(
            username='viewer@example.com',
            email='viewer@example.com',
            password='Password123!',
            role='viewer',
            organization=self.organization
        )
        
        # Viewer cannot create any users
        with self.assertRaises(ValidationError) as context:
            UserFactory.create_user('viewer', self.valid_user_data, viewer_user)
        
        self.assertIn('Insufficient permissions', str(context.exception))
    
    def test_user_factory_create_with_auto_password(self):
        """Test UserFactory creating user with auto-generated password"""
        user, password = UserFactory.create_user_with_auto_password(
            'viewer', self.valid_user_data, self.admin_user
        )
        
        self.assertEqual(user.role, 'viewer')
        self.assertTrue(len(password) >= 16)
        self.assertTrue(user.check_password(password))
    
    def test_user_factory_create_test_user(self):
        """Test UserFactory creating test user"""
        user = UserFactory.create_test_user('viewer', self.valid_user_data)
        
        self.assertEqual(user.role, 'viewer')
    
    def test_user_factory_create_test_user_bypass_permissions(self):
        """Test UserFactory creating test user with permission bypass"""
        admin_data = self.valid_user_data.copy()
        user = UserFactory.create_test_user('BlueVisionAdmin', admin_data, bypass_permissions=True)
        
        self.assertEqual(user.role, 'BlueVisionAdmin')
        self.assertTrue(user.is_superuser)
    
    def test_user_factory_create_test_admin_missing_fields(self):
        """Test UserFactory creating test admin with missing fields"""
        incomplete_data = {'username': 'test'}
        
        with self.assertRaises(ValidationError):
            UserFactory._create_test_admin(incomplete_data)
    
    def test_user_factory_create_test_admin_weak_password(self):
        """Test UserFactory creating test admin with weak password"""
        admin_data = self.valid_user_data.copy()
        admin_data['password'] = '123'
        
        with self.assertRaises(ValidationError):
            UserFactory._create_test_admin(admin_data)
    
    @patch('core.user_management.factories.user_factory.AuthenticationLog.log_authentication_event')
    def test_authentication_logging(self, mock_log):
        """Test that user creation logs authentication events"""
        creator = StandardUserCreator()
        creator.create_user(self.valid_user_data)
        
        mock_log.assert_called_once()
        call_args = mock_log.call_args
        self.assertEqual(call_args[1]['action'], 'user_created')
        self.assertTrue(call_args[1]['success'])
    
    def test_factory_boy_integration_organization(self):
        """Test factory boy integration for organizations"""
        try:
            from core.user_management.factories.user_factory import OrganizationFactory
            org = OrganizationFactory()
            self.assertIsInstance(org, Organization)
            self.assertTrue(org.name.startswith('Test Organization'))
        except ImportError:
            # Fallback factory test
            org = OrganizationFactory.create()
            self.assertIsInstance(org, Organization)
            self.assertEqual(org.name, 'Test Organization')
    
    def test_factory_boy_integration_user(self):
        """Test factory boy integration for users"""
        try:
            from core.user_management.factories.user_factory import UserFactory as FactoryBoyUserFactory
            user = FactoryBoyUserFactory()
            self.assertIsInstance(user, CustomUser)
            self.assertEqual(user.role, 'viewer')
        except ImportError:
            # Fallback factory test
            user = TestUserFactory.create()
            self.assertIsInstance(user, CustomUser)
            self.assertEqual(user.role, 'viewer')
    
    def test_fallback_factory_organization(self):
        """Test fallback organization factory"""
        # Mock import error to test fallback
        with patch('builtins.__import__', side_effect=ImportError):
            from core.user_management.factories.user_factory import OrganizationFactory
            org = OrganizationFactory.create(name='Custom Org')
            self.assertEqual(org.name, 'Custom Org')
    
    def test_fallback_factory_user(self):
        """Test fallback user factory"""
        # Mock import error to test fallback
        with patch('builtins.__import__', side_effect=ImportError):
            from core.user_management.factories.user_factory import UserFactory as FallbackUserFactory
            user = FallbackUserFactory.create(username='fallback@example.com')
            self.assertEqual(user.username, 'fallback@example.com')
    
    def test_user_creator_abstract_method(self):
        """Test that UserCreator is abstract"""
        with self.assertRaises(TypeError):
            UserCreator()
    
    def test_validate_user_data_empty_fields(self):
        """Test validation with empty but present fields"""
        creator = StandardUserCreator()
        invalid_data = self.valid_user_data.copy()
        invalid_data['username'] = ''
        
        with self.assertRaises(ValidationError):
            creator._validate_user_data(invalid_data)
    
    def test_password_generation_complexity_retry(self):
        """Test password generation retries when complexity not met"""
        creator = StandardUserCreator()
        
        # Mock secrets.choice to return predictable values that might not meet complexity
        with patch('secrets.choice') as mock_choice:
            # First call returns all lowercase, second call returns complex password
            mock_choice.side_effect = ['a'] * 16 + list('Aa1!')  # Simple then complex
            
            password = creator._generate_secure_password(4)
            
            # Should have retried and generated a complex password
            self.assertTrue(any(c.isupper() for c in password))
    
    def test_publisher_validation_empty_organization(self):
        """Test publisher validation with empty organization"""
        creator = PublisherUserCreator()
        data_with_empty_org = self.valid_user_data.copy()
        data_with_empty_org['organization'] = ''
        
        with self.assertRaises(ValidationError):
            creator._validate_publisher_requirements(data_with_empty_org)