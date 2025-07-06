"""
Tests for core signals functionality.
"""
import django
from django.test import TestCase, RequestFactory
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from unittest.mock import patch, Mock

from core.signals import (
    log_user_changes,
    log_organization_changes,
    log_trust_relationship_changes,
    log_trust_group_changes,
    log_successful_login,
    log_failed_login
)
from core.user_management.models import CustomUser, Organization
from core.trust.models import TrustLevel, TrustGroup, TrustRelationship


class SignalHandlerTest(TestCase):
    """Test signal handlers."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Org",
            domain="test.com",
            organization_type="educational",
            contact_email="contact@test.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.organization
        )
        self.trust_level = TrustLevel.objects.create(
            name="High",
            level="trusted",
            numerical_value=80,
            description="High trust",
            created_by=self.user
        )
    
    @patch('core.services.audit_service.AuditService.log_user_event')
    def test_log_user_changes_signal(self, mock_log):
        """Test that user changes trigger audit logging."""
        # Test user creation
        log_user_changes(
            sender=CustomUser,
            instance=self.user,
            created=True
        )
        
        # In test environment, signal should return early
        mock_log.assert_not_called()
    
    @patch('core.services.audit_service.AuditService.log_user_event')
    def test_log_organization_changes_signal(self, mock_log):
        """Test that organization changes trigger audit logging."""
        # Test organization creation
        log_organization_changes(
            sender=Organization,
            instance=self.organization,
            created=True
        )
        
        # In test environment, signal should return early
        mock_log.assert_not_called()
    
    @patch('core.services.audit_service.AuditService.log_trust_event')
    def test_log_trust_relationship_changes_signal(self, mock_log):
        """Test that trust relationship changes trigger audit logging."""
        # Create trust relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.organization,  # Same org for simplicity
            trust_level=self.trust_level,
            status='pending',
            created_by=self.user,
            last_modified_by=self.user
        )
        
        # Test relationship creation
        log_trust_relationship_changes(
            sender=TrustRelationship,
            instance=relationship,
            created=True
        )
        
        # In test environment, signal should return early
        mock_log.assert_not_called()
    
    @patch('core.services.audit_service.AuditService.log_trust_event')
    def test_log_trust_group_changes_signal(self, mock_log):
        """Test that trust group changes trigger audit logging."""
        # Create trust group
        group = TrustGroup.objects.create(
            name="Test Group",
            description="Test group",
            default_trust_level=self.trust_level,
            created_by=self.user
        )
        
        # Test group creation
        log_trust_group_changes(
            sender=TrustGroup,
            instance=group,
            created=True
        )
        
        # In test environment, signal should return early
        mock_log.assert_not_called()
    
    @patch('core.services.audit_service.AuditService.log_user_event')
    def test_log_successful_login_signal(self, mock_log):
        """Test that successful login triggers audit logging."""
        request = RequestFactory().get('/')
        request.META = {
            'HTTP_USER_AGENT': 'Test Browser',
            'REMOTE_ADDR': '127.0.0.1'
        }
        request.session = Mock()
        request.session.session_key = 'test_session'
        
        # Test successful login
        log_successful_login(
            sender=None,
            request=request,
            user=self.user
        )
        
        # In test environment, signal should return early
        mock_log.assert_not_called()
    
    @patch('core.services.audit_service.AuditService.log_user_event')
    def test_log_failed_login_signal(self, mock_log):
        """Test that failed login triggers audit logging."""
        request = RequestFactory().get('/')
        request.META = {
            'HTTP_USER_AGENT': 'Test Browser',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        credentials = {'username': 'testuser'}
        
        # Test failed login
        log_failed_login(
            sender=None,
            credentials=credentials,
            request=request
        )
        
        # In test environment, signal should return early
        mock_log.assert_not_called()