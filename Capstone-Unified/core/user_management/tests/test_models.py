from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import Organization, AuthenticationLog, UserSession
from core.tests.test_data_fixtures import create_test_user, create_test_organization


User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model"""
    
    def setUp(self):
        self.organization, _ = Organization.objects.get_or_create(
            name="Test Organization for User Tests",
            defaults={
                "organization_type": "educational",
                "trust_metadata": {}
            }
        )

    def test_create_user(self):
        """Test creating a user with required fields"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            organization=self.organization
        )
        
        # Refresh from database to ensure password is properly set
        user.refresh_from_db()
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.organization, self.organization)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            organization=self.organization
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.role, 'BlueVisionAdmin')
    
    def test_user_roles(self):
        """Test different user roles"""
        viewer = create_test_user(base_name='viewer')
        viewer.role = 'viewer'
        viewer.organization = self.organization
        viewer.save()
        
        publisher = create_test_user(base_name='publisher')
        publisher.role = 'publisher'
        publisher.organization = self.organization
        publisher.save()
        
        admin = create_test_user(base_name='admin')
        admin.role = 'BlueVisionAdmin'
        admin.organization = self.organization
        admin.save()
        
        self.assertEqual(viewer.role, 'viewer')
        self.assertEqual(publisher.role, 'publisher')
        self.assertEqual(admin.role, 'BlueVisionAdmin')
    
    def test_user_str_representation(self):
        """Test string representation of user"""
        user = create_test_user(base_name='testuser@example.com')
        user.organization = self.organization
        user.save()
        self.assertEqual(str(user), f'{user.username} (Viewer)')


class OrganizationModelTest(TestCase):
    """Test cases for Organization model"""
    
    def test_create_organization(self):
        """Test creating an organization"""
        org = Organization.objects.create(
            name='Test Organization Model Test',
            domain='test.org',
            contact_email='contact@test.org',
            organization_type='educational'
        )
        self.assertEqual(org.name, 'Test Organization Model Test')
        self.assertEqual(org.domain, 'test.org')
        self.assertFalse(org.is_publisher)  # Default value
        self.assertTrue(org.is_active)  # Default value
    
    def test_organization_str_representation(self):
        """Test string representation of organization"""
        org = create_test_organization(name_suffix='Org')
        self.assertEqual(str(org), org.name)


class AuthenticationLogModelTest(TestCase):
    """Test cases for AuthenticationLog model"""
    
    def setUp(self):
        self.user = create_test_user()
    
    def test_log_authentication_event(self):
        """Test logging authentication events"""
        log = AuthenticationLog.log_authentication_event(
            user=self.user,
            action='login_success',
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            success=True
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'login_success')
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertTrue(log.success)
    
    def test_log_failed_authentication(self):
        """Test logging failed authentication"""
        log = AuthenticationLog.log_authentication_event(
            user=None,
            action='login_failure',
            ip_address='192.168.1.100',
            success=False,
            failure_reason='Invalid credentials'
        )
        
        self.assertIsNone(log.user)
        self.assertEqual(log.action, 'login_failure')
        self.assertFalse(log.success)
        self.assertEqual(log.failure_reason, 'Invalid credentials')


class UserSessionModelTest(TestCase):
    """Test cases for UserSession model"""
    
    def setUp(self):
        self.user = create_test_user()
    
    def test_create_user_session(self):
        """Test creating a user session"""
        from django.utils import timezone
        from datetime import timedelta
        
        expires_at = timezone.now() + timedelta(hours=1)
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_session_token',
            refresh_token='test_refresh_token',
            ip_address='127.0.0.1',
            device_info={'browser': 'Test Browser'},
            expires_at=expires_at
        )
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_token, 'test_session_token')
        self.assertTrue(session.is_active)
    
    def test_deactivate_session(self):
        """Test deactivating a session"""
        from django.utils import timezone
        from datetime import timedelta
        
        expires_at = timezone.now() + timedelta(hours=1)
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_session_token',
            refresh_token='test_refresh_token',
            ip_address='127.0.0.1',
            expires_at=expires_at
        )
        
        session.is_active = False
        session.save()
        self.assertFalse(session.is_active)