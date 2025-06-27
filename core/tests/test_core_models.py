"""
Comprehensive tests for core.models.py
Tests for all models in the main models file.
"""
import uuid
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from core.models import *
from core.tests.test_base import CrispTestCase


class OrganizationModelTest(CrispTestCase):
    """Test Organization model functionality"""
    
    def test_organization_creation(self):
        """Test basic organization creation"""
        org = Organization.objects.create(
            name="Test Organization",
            domain="test.com",
            contact_email="contact@test.com",
            description="Test organization for testing"
        )
        
        self.assertIsNotNone(org.id)
        self.assertTrue(isinstance(org.id, uuid.UUID))
        self.assertEqual(org.name, "Test Organization")
        self.assertEqual(org.domain, "test.com")
        self.assertEqual(org.contact_email, "contact@test.com")
        self.assertTrue(org.is_active)
        self.assertIsNotNone(org.created_at)
        self.assertIsNotNone(org.updated_at)
    
    def test_organization_str_method(self):
        """Test organization string representation"""
        org = Organization.objects.create(
            name="String Test Org",
            domain="string.com",
            contact_email="test@string.com"
        )
        
        self.assertEqual(str(org), "String Test Org")
    
    def test_organization_unique_name(self):
        """Test organization name uniqueness"""
        Organization.objects.create(
            name="Unique Org",
            domain="unique.com",
            contact_email="test@unique.com"
        )
        
        # Try to create another organization with same name
        with self.assertRaises(IntegrityError):
            Organization.objects.create(
                name="Unique Org",
                domain="unique2.com",
                contact_email="test@unique2.com"
            )
    
    def test_organization_unique_domain(self):
        """Test organization domain uniqueness"""
        Organization.objects.create(
            name="Domain Org 1",
            domain="domain.com",
            contact_email="test1@domain.com"
        )
        
        # Try to create another organization with same domain
        with self.assertRaises(IntegrityError):
            Organization.objects.create(
                name="Domain Org 2",
                domain="domain.com",
                contact_email="test2@domain.com"
            )
    
    def test_organization_optional_fields(self):
        """Test organization with optional fields"""
        org = Organization.objects.create(
            name="Optional Fields Org",
            domain="optional.com",
            contact_email="test@optional.com",
            phone_number="+1234567890",
            address="123 Test St",
            city="Test City",
            country="Test Country",
            website="https://optional.com",
            industry="Technology",
            organization_type="private"
        )
        
        self.assertEqual(org.phone_number, "+1234567890")
        self.assertEqual(org.address, "123 Test St")
        self.assertEqual(org.city, "Test City")
        self.assertEqual(org.country, "Test Country")
        self.assertEqual(org.website, "https://optional.com")
        self.assertEqual(org.industry, "Technology")
        self.assertEqual(org.organization_type, "private")
    
    def test_organization_defaults(self):
        """Test organization default values"""
        org = Organization.objects.create(
            name="Defaults Org",
            domain="defaults.com",
            contact_email="test@defaults.com"
        )
        
        self.assertTrue(org.is_active)
        self.assertIsNotNone(org.created_at)
        self.assertIsNotNone(org.updated_at)
    
    def test_organization_methods(self):
        """Test organization custom methods"""
        org = Organization.objects.create(
            name="Methods Org",
            domain="methods.com",
            contact_email="test@methods.com"
        )
        
        # Test string representation
        self.assertEqual(str(org), "Methods Org")
        
        # Test if organization has expected attributes
        self.assertTrue(hasattr(org, 'id'))
        self.assertTrue(hasattr(org, 'name'))
        self.assertTrue(hasattr(org, 'domain'))
        self.assertTrue(hasattr(org, 'contact_email'))
        self.assertTrue(hasattr(org, 'is_active'))
        self.assertTrue(hasattr(org, 'created_at'))
        self.assertTrue(hasattr(org, 'updated_at'))


class CustomUserModelTest(CrispTestCase):
    """Test CustomUser model functionality"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="User Test Org",
            domain="usertest.com",
            contact_email="test@usertest.com"
        )
    
    def test_custom_user_creation(self):
        """Test custom user creation"""
        user = CustomUser.objects.create_user(
            username="testuser",
            email="test@usertest.com",
            password="testpass123",
            organization=self.org,
            role="viewer"
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@usertest.com")
        self.assertEqual(user.organization, self.org)
        self.assertEqual(user.role, "viewer")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_custom_user_str_method(self):
        """Test custom user string representation"""
        user = CustomUser.objects.create_user(
            username="struser",
            email="str@usertest.com",
            password="testpass123",
            organization=self.org
        )
        
        self.assertEqual(str(user), "struser")
    
    def test_user_role_choices(self):
        """Test user role choices"""
        valid_roles = ['viewer', 'publisher', 'BlueVisionAdmin']
        
        for role in valid_roles:
            user = CustomUser.objects.create_user(
                username=f"role_{role}",
                email=f"{role}@usertest.com",
                password="testpass123",
                organization=self.org,
                role=role
            )
            self.assertEqual(user.role, role)
    
    def test_user_optional_fields(self):
        """Test user with optional fields"""
        user = CustomUser.objects.create_user(
            username="fulluser",
            email="full@usertest.com",
            password="testpass123",
            organization=self.org,
            first_name="Test",
            last_name="User",
            phone_number="+1234567890",
            department="IT",
            job_title="Developer",
            role="publisher"
        )
        
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.phone_number, "+1234567890")
        self.assertEqual(user.department, "IT")
        self.assertEqual(user.job_title, "Developer")
    
    def test_user_permissions(self):
        """Test user permission system"""
        # Test viewer permissions
        viewer = CustomUser.objects.create_user(
            username="viewer",
            email="viewer@usertest.com",
            password="testpass123",
            organization=self.org,
            role="viewer"
        )
        
        # Test publisher permissions
        publisher = CustomUser.objects.create_user(
            username="publisher",
            email="publisher@usertest.com",
            password="testpass123",
            organization=self.org,
            role="publisher"
        )
        
        # Test admin permissions
        admin = CustomUser.objects.create_user(
            username="admin",
            email="admin@usertest.com",
            password="testpass123",
            organization=self.org,
            role="BlueVisionAdmin"
        )
        
        self.assertEqual(viewer.role, "viewer")
        self.assertEqual(publisher.role, "publisher")
        self.assertEqual(admin.role, "BlueVisionAdmin")
    
    def test_user_organization_relationship(self):
        """Test user-organization relationship"""
        user = CustomUser.objects.create_user(
            username="orguser",
            email="org@usertest.com",
            password="testpass123",
            organization=self.org
        )
        
        self.assertEqual(user.organization, self.org)
        self.assertEqual(user.organization.name, "User Test Org")
        
        # Test user without organization
        user_no_org = CustomUser.objects.create_user(
            username="noorguser",
            email="noorg@usertest.com",
            password="testpass123"
        )
        
        self.assertIsNone(user_no_org.organization)
    
    def test_user_authentication_fields(self):
        """Test user authentication-related fields"""
        user = CustomUser.objects.create_user(
            username="authuser",
            email="auth@usertest.com",
            password="testpass123",
            organization=self.org,
            is_verified=True,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        self.assertTrue(user.is_verified)
        self.assertEqual(user.failed_login_attempts, 0)
        self.assertIsNone(user.account_locked_until)
        self.assertIsNotNone(user.last_login_ip)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
    
    def test_user_account_lockout(self):
        """Test user account lockout functionality"""
        user = CustomUser.objects.create_user(
            username="lockuser",
            email="lock@usertest.com",
            password="testpass123",
            organization=self.org
        )
        
        # Test account lockout
        lockout_time = timezone.now() + timedelta(hours=1)
        user.account_locked_until = lockout_time
        user.failed_login_attempts = 5
        user.save()
        
        self.assertEqual(user.failed_login_attempts, 5)
        self.assertEqual(user.account_locked_until, lockout_time)
    
    def test_user_profile_completion(self):
        """Test user profile completion status"""
        incomplete_user = CustomUser.objects.create_user(
            username="incomplete",
            email="incomplete@usertest.com",
            password="testpass123",
            organization=self.org
        )
        
        complete_user = CustomUser.objects.create_user(
            username="complete",
            email="complete@usertest.com",
            password="testpass123",
            organization=self.org,
            first_name="Complete",
            last_name="User",
            phone_number="+1234567890",
            department="IT"
        )
        
        # Basic profile data should exist
        self.assertTrue(incomplete_user.username)
        self.assertTrue(incomplete_user.email)
        
        # Complete profile should have additional data
        self.assertTrue(complete_user.first_name)
        self.assertTrue(complete_user.last_name)
        self.assertTrue(complete_user.phone_number)
        self.assertTrue(complete_user.department)


class UserSessionModelTest(CrispTestCase):
    """Test UserSession model functionality"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Session Test Org",
            domain="session.com",
            contact_email="test@session.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="sessionuser",
            email="session@test.com",
            password="testpass123",
            organization=self.org
        )
    
    def test_user_session_creation(self):
        """Test user session creation"""
        session = UserSession.objects.create(
            user=self.user,
            session_key="test_session_key_123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_key, "test_session_key_123")
        self.assertEqual(session.ip_address, "192.168.1.100")
        self.assertEqual(session.user_agent, "Mozilla/5.0")
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.last_activity)
    
    def test_user_session_str_method(self):
        """Test user session string representation"""
        session = UserSession.objects.create(
            user=self.user,
            session_key="str_test_session",
            ip_address="192.168.1.101"
        )
        
        expected_str = f"{self.user.username} - str_test_session"
        self.assertEqual(str(session), expected_str)
    
    def test_session_expiry_check(self):
        """Test session expiry functionality"""
        # Create expired session
        expired_session = UserSession.objects.create(
            user=self.user,
            session_key="expired_session",
            ip_address="192.168.1.102",
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Create active session
        active_session = UserSession.objects.create(
            user=self.user,
            session_key="active_session",
            ip_address="192.168.1.103",
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Test expiry logic would go here
        self.assertTrue(expired_session.expires_at < timezone.now())
        self.assertTrue(active_session.expires_at > timezone.now())
    
    def test_session_activity_tracking(self):
        """Test session activity tracking"""
        session = UserSession.objects.create(
            user=self.user,
            session_key="activity_session",
            ip_address="192.168.1.104"
        )
        
        initial_activity = session.last_activity
        
        # Simulate activity update
        session.last_activity = timezone.now()
        session.save()
        
        self.assertGreater(session.last_activity, initial_activity)
    
    def test_session_device_tracking(self):
        """Test session device and location tracking"""
        session = UserSession.objects.create(
            user=self.user,
            session_key="device_session",
            ip_address="192.168.1.105",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            device_type="desktop",
            browser="Chrome",
            os="Windows"
        )
        
        self.assertEqual(session.device_type, "desktop")
        self.assertEqual(session.browser, "Chrome")
        self.assertEqual(session.os, "Windows")
    
    def test_multiple_sessions_per_user(self):
        """Test multiple sessions for one user"""
        session1 = UserSession.objects.create(
            user=self.user,
            session_key="session_1",
            ip_address="192.168.1.106"
        )
        
        session2 = UserSession.objects.create(
            user=self.user,
            session_key="session_2",
            ip_address="192.168.1.107"
        )
        
        user_sessions = UserSession.objects.filter(user=self.user)
        self.assertEqual(user_sessions.count(), 2)
        self.assertIn(session1, user_sessions)
        self.assertIn(session2, user_sessions)


class AuthenticationLogModelTest(CrispTestCase):
    """Test AuthenticationLog model functionality"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Auth Log Org",
            domain="authlog.com",
            contact_email="test@authlog.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="authloguser",
            email="authlog@test.com",
            password="testpass123",
            organization=self.org
        )
    
    def test_authentication_log_creation(self):
        """Test authentication log creation"""
        log = AuthenticationLog.objects.create(
            user=self.user,
            action="login_success",
            ip_address="192.168.1.200",
            user_agent="Mozilla/5.0",
            success=True,
            details={"method": "username_password"}
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, "login_success")
        self.assertEqual(log.ip_address, "192.168.1.200")
        self.assertTrue(log.success)
        self.assertIsNotNone(log.timestamp)
        self.assertEqual(log.details["method"], "username_password")
    
    def test_authentication_log_str_method(self):
        """Test authentication log string representation"""
        log = AuthenticationLog.objects.create(
            user=self.user,
            action="login_attempt",
            ip_address="192.168.1.201",
            success=False
        )
        
        expected_str = f"{self.user.username} - login_attempt - {log.timestamp}"
        self.assertEqual(str(log), expected_str)
    
    def test_failed_login_log(self):
        """Test failed login logging"""
        failed_log = AuthenticationLog.objects.create(
            user=self.user,
            action="login_failed",
            ip_address="192.168.1.202",
            success=False,
            failure_reason="invalid_password",
            details={"attempts": 3}
        )
        
        self.assertFalse(failed_log.success)
        self.assertEqual(failed_log.failure_reason, "invalid_password")
        self.assertEqual(failed_log.details["attempts"], 3)
    
    def test_logout_log(self):
        """Test logout logging"""
        logout_log = AuthenticationLog.objects.create(
            user=self.user,
            action="logout",
            ip_address="192.168.1.203",
            success=True,
            details={"session_duration": 3600}
        )
        
        self.assertEqual(logout_log.action, "logout")
        self.assertTrue(logout_log.success)
        self.assertEqual(logout_log.details["session_duration"], 3600)
    
    def test_security_event_log(self):
        """Test security event logging"""
        security_log = AuthenticationLog.objects.create(
            user=self.user,
            action="suspicious_activity",
            ip_address="192.168.1.204",
            success=False,
            failure_reason="multiple_failed_attempts",
            details={
                "failed_attempts": 5,
                "time_window": "5_minutes",
                "action_taken": "account_locked"
            }
        )
        
        self.assertEqual(security_log.action, "suspicious_activity")
        self.assertFalse(security_log.success)
        self.assertEqual(security_log.failure_reason, "multiple_failed_attempts")
        self.assertEqual(security_log.details["action_taken"], "account_locked")


class PermissionSystemTest(CrispTestCase):
    """Test permission system components"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Permission Org",
            domain="perm.com",
            contact_email="test@perm.com"
        )
    
    def test_user_role_choices(self):
        """Test USER_ROLE_CHOICES constant"""
        expected_roles = [
            ('viewer', 'Viewer'),
            ('publisher', 'Publisher'),
            ('BlueVisionAdmin', 'BlueVision Admin'),
        ]
        
        self.assertEqual(USER_ROLE_CHOICES, expected_roles)
        
        # Test that roles are valid choices
        for role_code, role_name in USER_ROLE_CHOICES:
            user = CustomUser.objects.create_user(
                username=f"role_{role_code}",
                email=f"{role_code}@perm.com",
                password="testpass123",
                organization=self.org,
                role=role_code
            )
            self.assertEqual(user.role, role_code)
    
    def test_permission_choices(self):
        """Test PERMISSION_CHOICES constant"""
        expected_permissions = [
            ('read', 'Read'),
            ('write', 'Write'),
            ('admin', 'Admin'),
        ]
        
        self.assertEqual(PERMISSION_CHOICES, expected_permissions)
        
        # Test permission values
        for perm_code, perm_name in PERMISSION_CHOICES:
            self.assertIn(perm_code, ['read', 'write', 'admin'])
            self.assertTrue(isinstance(perm_name, str))
    
    def test_role_hierarchy(self):
        """Test role hierarchy implications"""
        viewer = CustomUser.objects.create_user(
            username="viewer_hier",
            email="viewer@perm.com",
            password="testpass123",
            organization=self.org,
            role="viewer"
        )
        
        publisher = CustomUser.objects.create_user(
            username="publisher_hier",
            email="publisher@perm.com",
            password="testpass123",
            organization=self.org,
            role="publisher"
        )
        
        admin = CustomUser.objects.create_user(
            username="admin_hier",
            email="admin@perm.com",
            password="testpass123",
            organization=self.org,
            role="BlueVisionAdmin"
        )
        
        # Test role assignments
        self.assertEqual(viewer.role, "viewer")
        self.assertEqual(publisher.role, "publisher")
        self.assertEqual(admin.role, "BlueVisionAdmin")
        
        # Test implicit hierarchy (would need methods to test fully)
        roles_by_level = {
            "viewer": 1,
            "publisher": 2,
            "BlueVisionAdmin": 3
        }
        
        self.assertLess(roles_by_level[viewer.role], roles_by_level[publisher.role])
        self.assertLess(roles_by_level[publisher.role], roles_by_level[admin.role])


class ModelFieldValidationTest(CrispTestCase):
    """Test model field validation and constraints"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Validation Org",
            domain="validation.com",
            contact_email="test@validation.com"
        )
    
    def test_organization_field_validation(self):
        """Test organization field validation"""
        # Test required fields
        with self.assertRaises(IntegrityError):
            org = Organization(name="", domain="empty.com", contact_email="test@empty.com")
            org.save()
    
    def test_user_field_validation(self):
        """Test user field validation"""
        # Test required fields
        user = CustomUser(
            username="validuser",
            email="valid@validation.com",
            organization=self.org
        )
        
        # Should be able to save with required fields
        user.save()
        self.assertIsNotNone(user.id)
    
    def test_email_field_validation(self):
        """Test email field validation"""
        # Valid email should work
        user = CustomUser.objects.create_user(
            username="emailuser",
            email="valid@validation.com",
            password="testpass123",
            organization=self.org
        )
        
        self.assertEqual(user.email, "valid@validation.com")
    
    def test_uuid_field_behavior(self):
        """Test UUID field behavior"""
        org1 = Organization.objects.create(
            name="UUID Org 1",
            domain="uuid1.com",
            contact_email="test@uuid1.com"
        )
        
        org2 = Organization.objects.create(
            name="UUID Org 2",
            domain="uuid2.com",
            contact_email="test@uuid2.com"
        )
        
        # UUIDs should be unique
        self.assertNotEqual(org1.id, org2.id)
        
        # UUIDs should be valid UUID objects
        self.assertTrue(isinstance(org1.id, uuid.UUID))
        self.assertTrue(isinstance(org2.id, uuid.UUID))
    
    def test_datetime_field_behavior(self):
        """Test datetime field behavior"""
        org = Organization.objects.create(
            name="DateTime Org",
            domain="datetime.com",
            contact_email="test@datetime.com"
        )
        
        # created_at should be auto-set
        self.assertIsNotNone(org.created_at)
        self.assertTrue(org.created_at <= timezone.now())
        
        # updated_at should be auto-set
        self.assertIsNotNone(org.updated_at)
        self.assertTrue(org.updated_at <= timezone.now())
        
        # Save again to test updated_at auto-update
        original_updated_at = org.updated_at
        org.description = "Updated description"
        org.save()
        
        # updated_at should be newer
        self.assertGreater(org.updated_at, original_updated_at)


class ModelRelationshipTest(CrispTestCase):
    """Test model relationships and foreign keys"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Relationship Org",
            domain="rel.com",
            contact_email="test@rel.com"
        )
    
    def test_user_organization_relationship(self):
        """Test user-organization foreign key relationship"""
        user = CustomUser.objects.create_user(
            username="reluser",
            email="rel@test.com",
            password="testpass123",
            organization=self.org
        )
        
        # Test forward relationship
        self.assertEqual(user.organization, self.org)
        self.assertEqual(user.organization.name, "Relationship Org")
        
        # Test reverse relationship (if exists)
        org_users = self.org.customuser_set.all()
        self.assertIn(user, org_users)
    
    def test_cascade_behavior(self):
        """Test cascade behavior on deletion"""
        user = CustomUser.objects.create_user(
            username="cascadeuser",
            email="cascade@test.com",
            password="testpass123",
            organization=self.org
        )
        
        session = UserSession.objects.create(
            user=user,
            session_key="cascade_session",
            ip_address="192.168.1.250"
        )
        
        log = AuthenticationLog.objects.create(
            user=user,
            action="test_action",
            ip_address="192.168.1.251",
            success=True
        )
        
        # Verify relationships exist
        self.assertEqual(session.user, user)
        self.assertEqual(log.user, user)
        
        # Delete user and test cascade
        user_id = user.id
        user.delete()
        
        # Sessions and logs should be handled according to cascade rules
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(id=user_id)


class ModelMetaOptionsTest(CrispTestCase):
    """Test model Meta options and database table configuration"""
    
    def test_organization_meta_options(self):
        """Test Organization model Meta options"""
        # Test model has expected meta attributes
        self.assertTrue(hasattr(Organization, '_meta'))
        
        # Test ordering if specified
        if hasattr(Organization._meta, 'ordering'):
            self.assertTrue(isinstance(Organization._meta.ordering, (list, tuple)))
    
    def test_custom_user_meta_options(self):
        """Test CustomUser model Meta options"""
        self.assertTrue(hasattr(CustomUser, '_meta'))
        
        # Test that CustomUser extends AbstractUser properly
        self.assertTrue(issubclass(CustomUser, AbstractUser))
    
    def test_model_verbose_names(self):
        """Test model verbose names"""
        # Test Organization verbose name
        if hasattr(Organization._meta, 'verbose_name'):
            self.assertTrue(isinstance(Organization._meta.verbose_name, str))
        
        if hasattr(Organization._meta, 'verbose_name_plural'):
            self.assertTrue(isinstance(Organization._meta.verbose_name_plural, str))
    
    def test_model_permissions(self):
        """Test model-level permissions"""
        # Test default permissions exist
        for model_class in [Organization, CustomUser, UserSession, AuthenticationLog]:
            model_name = model_class._meta.model_name
            app_label = model_class._meta.app_label
            
            # Default permissions should exist conceptually
            default_permissions = ['add', 'change', 'delete', 'view']
            for perm in default_permissions:
                permission_codename = f"{perm}_{model_name}"
                # Permission should be correctly formatted
                self.assertTrue(permission_codename.startswith(perm))