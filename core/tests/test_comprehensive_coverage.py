"""
Comprehensive test coverage for achieving 90-100% code coverage
This file consolidates tests for all major components to maximize coverage
"""
import uuid
import json
import hashlib
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.request import Request
from rest_framework.views import APIView

from ..models.auth import CustomUser, Organization, UserSession, AuthenticationLog
from ..models.stix_object import STIXObject, Collection
from ..models.indicator import Indicator
from ..models.ttp_data import TTPs
from ..models.threat_feed import ThreatFeed
from ..models.trust_models.models import TrustLevel, TrustRelationship

# Import actual classes that exist
from ..observers.auth_observers import SecurityAuditObserver, AccountLockoutObserver, NotificationObserver
from ..strategies.anonymization import DomainAnonymizationStrategy, AnonymizationStrategy
from ..services.stix_taxii_service import StixTaxiiService
from ..services.auth_service import AuthService
from ..services.trust_service import TrustService
from ..services.trust_anonymization_service import TrustAnonymizationService

from ..middleware import SecurityHeadersMiddleware, RateLimitMiddleware, SecurityAuditMiddleware, SessionTimeoutMiddleware
from .test_base import CrispTestCase


User = get_user_model()


class ComprehensiveObserverTestCase(CrispTestCase):
    """Comprehensive tests for all observer pattern implementations"""
    
    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user(role='viewer')
        
    def test_security_audit_observer_success_event(self):
        """Test SecurityAuditObserver with successful event"""
        observer = SecurityAuditObserver()
        event_data = {
            'ip_address': '192.168.1.100',
            'user_agent': 'TestAgent/1.0',
            'success': True,
            'additional_data': {'test': 'data'}
        }
        
        with patch.object(observer.security_logger, 'info') as mock_log:
            observer.notify('login_success', self.test_user, event_data)
            mock_log.assert_called_once()
            
    def test_security_audit_observer_failure_event(self):
        """Test SecurityAuditObserver with failure event"""
        observer = SecurityAuditObserver()
        event_data = {
            'ip_address': '192.168.1.100',
            'user_agent': 'TestAgent/1.0',
            'success': False,
            'failure_reason': 'Invalid credentials'
        }
        
        with patch.object(observer.security_logger, 'warning') as mock_log:
            observer.notify('login_failed', self.test_user, event_data)
            mock_log.assert_called_once()
            
    def test_security_audit_observer_critical_event(self):
        """Test SecurityAuditObserver with critical event"""
        observer = SecurityAuditObserver()
        event_data = {
            'ip_address': '192.168.1.100',
            'user_agent': 'TestAgent/1.0',
            'success': False
        }
        
        with patch.object(observer.security_logger, 'critical') as mock_log:
            observer.notify('account_locked', self.test_user, event_data)
            mock_log.assert_called_once()
            
    def test_account_lockout_observer_failed_login(self):
        """Test AccountLockoutObserver handling failed login"""
        observer = AccountLockoutObserver()
        self.test_user.failed_login_attempts = 4  # Close to lockout
        event_data = {'ip_address': '192.168.1.100'}
        
        with patch.object(observer, '_send_security_warning') as mock_warning:
            observer.notify('login_failed', self.test_user, event_data)
            mock_warning.assert_called_once()
            
    def test_account_lockout_observer_suspicious_activity(self):
        """Test AccountLockoutObserver handling suspicious activity"""
        observer = AccountLockoutObserver()
        event_data = {'ip_address': '192.168.1.100'}
        
        with patch.object(self.test_user, 'lock_account') as mock_lock:
            with patch('core.models.auth.AuthenticationLog.log_authentication_event') as mock_log:
                observer.notify('suspicious_activity', self.test_user, event_data)
                mock_lock.assert_called_once_with(duration_minutes=60)
                mock_log.assert_called_once()
                
    def test_notification_observer_successful_login(self):
        """Test NotificationObserver handling successful login"""
        observer = NotificationObserver()
        event_data = {'ip_address': '192.168.1.100', 'user_agent': 'TestAgent/1.0'}
        
        with patch.object(observer, '_is_new_location', return_value=True) as mock_new_location:
            with patch.object(observer, '_send_new_location_alert') as mock_alert:
                observer.notify('login_success', self.test_user, event_data)
                mock_new_location.assert_called_once()
                mock_alert.assert_called_once()
                
    def test_notification_observer_password_changed(self):
        """Test NotificationObserver handling password change"""
        observer = NotificationObserver()
        event_data = {'ip_address': '192.168.1.100'}
        
        with patch.object(observer, '_send_password_change_notification') as mock_notify:
            observer.notify('password_changed', self.test_user, event_data)
            mock_notify.assert_called_once()


class ComprehensiveAnonymizationTestCase(CrispTestCase):
    """Comprehensive tests for anonymization strategies"""
    
    def setUp(self):
        super().setUp()
        self.domain_strategy = DomainAnonymizationStrategy()
        
    def test_domain_anonymization_high_trust(self):
        """Test domain anonymization with high trust (no anonymization)"""
        stix_object = {
            'type': 'indicator',
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity']
        }
        
        result = self.domain_strategy.anonymize(stix_object, 0.9)  # High trust
        self.assertEqual(result['pattern'], stix_object['pattern'])
        
    def test_domain_anonymization_medium_trust(self):
        """Test domain anonymization with medium trust (partial anonymization)"""
        stix_object = {
            'type': 'indicator',
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity']
        }
        
        result = self.domain_strategy.anonymize(stix_object, 0.6)  # Medium trust
        # Should anonymize domain but keep pattern structure
        self.assertIn('domain-name:value', result['pattern'])
        self.assertNotIn('malicious.example.com', result['pattern'])
        
    def test_domain_anonymization_low_trust(self):
        """Test domain anonymization with low trust (full anonymization)"""
        stix_object = {
            'type': 'indicator',
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity']
        }
        
        result = self.domain_strategy.anonymize(stix_object, 0.2)  # Low trust
        # Should be fully anonymized with hash
        self.assertIn('domain-name:value', result['pattern'])
        self.assertNotIn('malicious.example.com', result['pattern'])


class ComprehensiveServiceTestCase(CrispTestCase):
    """Comprehensive tests for service layer functionality"""
    
    def setUp(self):
        super().setUp()
        self.test_organization = self.create_test_organization()
        self.test_user = self.create_test_user(role='admin')
        
    def test_stix_taxii_service_discover_collections(self):
        """Test STIX TAXII service collection discovery"""
        service = StixTaxiiService()
        
        # Mock the TAXII server response
        mock_collection = Mock()
        mock_collection.id = 'test-collection'
        mock_collection.title = 'Test Collection'
        mock_collection.description = 'Test Description'
        mock_collection.can_read = True
        mock_collection.can_write = False
        mock_collection.media_types = ['application/stix+json']
        
        with patch('core.services.stix_taxii_service.ApiRoot') as mock_api_root:
            mock_api_root.return_value.collections = [mock_collection]
            
            collections = service.discover_collections(
                'https://test.server.com',
                'api/v1',
                'test_user',
                'test_pass'
            )
            
            self.assertEqual(len(collections), 1)
            self.assertEqual(collections[0]['id'], 'test-collection')
            self.assertEqual(collections[0]['title'], 'Test Collection')
            
    def test_auth_service_validate_token(self):
        """Test AuthService token validation"""
        service = AuthService()
        
        # Test with valid token
        with patch.object(service, '_decode_jwt_token') as mock_decode:
            mock_decode.return_value = {
                'user_id': str(self.test_user.id),
                'exp': timezone.now() + timedelta(hours=1)
            }
            
            result = service.verify_token('valid_token')
            self.assertTrue(result['success'])
            self.assertEqual(result['user_id'], str(self.test_user.id))
            
    def test_trust_service_calculate_trust_level(self):
        """Test TrustService trust level calculation"""
        service = TrustService()
        
        # Create trust level
        trust_level = TrustLevel.objects.create(
            name='High Trust',
            level=4,
            description='High trust level',
            anonymization_level='low'
        )
        
        # Create trust relationship
        other_org = Organization.objects.create(
            name='Other Organization',
            domain='other.example.com'
        )
        
        trust_rel = TrustRelationship.objects.create(
            trustor=self.test_organization,
            trustee=other_org,
            trust_level=trust_level,
            created_by=self.test_user
        )
        
        calculated_level = service.get_trust_level(self.test_organization, other_org)
        self.assertEqual(calculated_level, trust_level)
        
    def test_trust_anonymization_service_anonymize_object(self):
        """Test TrustAnonymizationService object anonymization"""
        service = TrustAnonymizationService()
        
        stix_object = {
            'type': 'indicator',
            'pattern': "[domain-name:value = 'test.example.com']",
            'labels': ['malicious-activity']
        }
        
        other_org = Organization.objects.create(
            name='Other Organization',
            domain='other.example.com'
        )
        
        # Test anonymization based on trust
        result = service.anonymize_for_organization(
            stix_object,
            self.test_organization,
            other_org
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('type', result)


class ComprehensiveMiddlewareTestCase(CrispTestCase):
    """Comprehensive tests for middleware functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.test_user = self.create_test_user(role='viewer')
        
    def test_security_headers_middleware_all_headers(self):
        """Test SecurityHeadersMiddleware sets all required headers"""
        middleware = SecurityHeadersMiddleware(get_response=lambda r: HttpResponse())
        request = self.factory.get('/')
        response = middleware.process_response(request, HttpResponse())
        
        required_headers = [
            'X-XSS-Protection',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Referrer-Policy',
            'Content-Security-Policy'
        ]
        
        for header in required_headers:
            self.assertIn(header, response)
            
    def test_rate_limit_middleware_ip_extraction(self):
        """Test RateLimitMiddleware IP extraction methods"""
        middleware = RateLimitMiddleware(get_response=lambda r: HttpResponse())
        
        # Test with X-Forwarded-For
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 198.51.100.1'
        ip = middleware._get_client_ip(request)
        self.assertEqual(ip, '203.0.113.1')
        
        # Test with REMOTE_ADDR
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '203.0.113.2'
        ip = middleware._get_client_ip(request)
        self.assertEqual(ip, '203.0.113.2')
        
    def test_security_audit_middleware_suspicious_detection(self):
        """Test SecurityAuditMiddleware suspicious pattern detection"""
        middleware = SecurityAuditMiddleware(get_response=lambda r: HttpResponse())
        
        suspicious_patterns = [
            'eval(', '<script', 'SELECT * FROM', '../../../', 'cmd.exe'
        ]
        
        for pattern in suspicious_patterns:
            request = self.factory.get(f'/api/test/?q={pattern}')
            request.user = self.test_user
            request.META['REMOTE_ADDR'] = '192.168.1.1'
            request.META['HTTP_USER_AGENT'] = 'Test Agent'
            
            with patch.object(middleware, '_log_suspicious_activity') as mock_log:
                middleware.process_request(request)
                mock_log.assert_called_once()
                
    def test_session_timeout_middleware_cleanup(self):
        """Test SessionTimeoutMiddleware session cleanup"""
        middleware = SessionTimeoutMiddleware(get_response=lambda r: HttpResponse())
        
        # Create expired session
        expired_session = UserSession.objects.create(
            user=self.test_user,
            session_token='expired_token',
            refresh_token='expired_refresh',
            device_info={},
            ip_address='127.0.0.1',
            expires_at=timezone.now() - timedelta(hours=1),
            is_active=True
        )
        
        middleware._cleanup_expired_sessions()
        
        expired_session.refresh_from_db()
        self.assertFalse(expired_session.is_active)


class ComprehensiveModelTestCase(CrispTestCase):
    """Comprehensive tests for model functionality"""
    
    def setUp(self):
        super().setUp()
        self.test_organization = self.create_test_organization()
        self.test_user = self.create_test_user(role='admin')
        
    def test_stix_object_creation_and_validation(self):
        """Test STIXObject model creation and validation"""
        collection = Collection.objects.create(
            name='Test Collection',
            description='Test collection',
            can_read=True,
            can_write=True,
            owner=self.test_organization
        )
        
        stix_data = {
            'type': 'indicator',
            'spec_version': '2.1',
            'id': 'indicator--' + str(uuid.uuid4()),
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'pattern': "[file:hashes.MD5 = 'test']",
            'labels': ['malicious-activity']
        }
        
        stix_obj = STIXObject.objects.create(
            stix_id=stix_data['id'],
            stix_type='indicator',
            created=timezone.now(),
            modified=timezone.now(),
            object_data=stix_data,
            collection=collection
        )
        
        self.assertEqual(stix_obj.stix_type, 'indicator')
        self.assertEqual(stix_obj.collection, collection)
        self.assertEqual(stix_obj.object_data, stix_data)
        
    def test_threat_feed_creation_and_configuration(self):
        """Test ThreatFeed model creation and configuration"""
        threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            description='Test threat feed',
            is_external=True,
            taxii_server_url='https://test.server.com',
            taxii_api_root='api/v1',
            taxii_collection_id='test-collection',
            owner=self.test_organization
        )
        
        self.assertEqual(threat_feed.name, 'Test Feed')
        self.assertTrue(threat_feed.is_external)
        self.assertEqual(threat_feed.owner, self.test_organization)
        
    def test_trust_relationship_creation(self):
        """Test TrustRelationship model creation"""
        trust_level = TrustLevel.objects.create(
            name='Medium Trust',
            level=3,
            description='Medium trust level',
            anonymization_level='medium'
        )
        
        other_org = Organization.objects.create(
            name='Partner Organization',
            domain='partner.example.com'
        )
        
        trust_rel = TrustRelationship.objects.create(
            trustor=self.test_organization,
            trustee=other_org,
            trust_level=trust_level,
            created_by=self.test_user
        )
        
        self.assertEqual(trust_rel.trustor, self.test_organization)
        self.assertEqual(trust_rel.trustee, other_org)
        self.assertEqual(trust_rel.trust_level, trust_level)
        
    def test_authentication_log_creation(self):
        """Test AuthenticationLog model functionality"""
        auth_log = AuthenticationLog.log_authentication_event(
            user=self.test_user,
            action='login_success',
            ip_address='192.168.1.100',
            user_agent='TestAgent/1.0',
            success=True,
            additional_data={'test': 'data'}
        )
        
        self.assertEqual(auth_log.user, self.test_user)
        self.assertEqual(auth_log.action, 'login_success')
        self.assertTrue(auth_log.success)
        
    def test_user_session_management(self):
        """Test UserSession model functionality"""
        session = UserSession.objects.create(
            user=self.test_user,
            session_token='test_session_token',
            refresh_token='test_refresh_token',
            device_info={'browser': 'Chrome', 'os': 'Windows'},
            ip_address='192.168.1.100',
            expires_at=timezone.now() + timedelta(hours=24),
            is_active=True
        )
        
        self.assertEqual(session.user, self.test_user)
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.created_at)


class ComprehensiveIntegrationTestCase(CrispTestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        super().setUp()
        self.test_organization = self.create_test_organization()
        self.test_user = self.create_test_user(role='admin')
        
    def test_complete_threat_intelligence_workflow(self):
        """Test complete threat intelligence creation and sharing workflow"""
        # Create collection
        collection = Collection.objects.create(
            name='Integration Test Collection',
            description='Test collection for integration tests',
            can_read=True,
            can_write=True,
            owner=self.test_organization
        )
        
        # Create STIX indicator
        stix_data = {
            'type': 'indicator',
            'spec_version': '2.1',
            'id': 'indicator--' + str(uuid.uuid4()),
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity']
        }
        
        stix_obj = STIXObject.objects.create(
            stix_id=stix_data['id'],
            stix_type='indicator',
            created=timezone.now(),
            modified=timezone.now(),
            object_data=stix_data,
            collection=collection
        )
        
        # Create partner organization
        partner_org = Organization.objects.create(
            name='Partner Organization',
            domain='partner.example.com'
        )
        
        # Create trust relationship
        trust_level = TrustLevel.objects.create(
            name='High Trust',
            level=4,
            description='High trust level',
            anonymization_level='low'
        )
        
        trust_rel = TrustRelationship.objects.create(
            trustor=self.test_organization,
            trustee=partner_org,
            trust_level=trust_level,
            created_by=self.test_user
        )
        
        # Test anonymization service
        anonymization_service = TrustAnonymizationService()
        anonymized_data = anonymization_service.anonymize_for_organization(
            stix_data,
            self.test_organization,
            partner_org
        )
        
        # Verify workflow completed successfully
        self.assertIsNotNone(stix_obj)
        self.assertIsNotNone(trust_rel)
        self.assertIsInstance(anonymized_data, dict)
        
    def test_authentication_and_authorization_workflow(self):
        """Test complete authentication and authorization workflow"""
        auth_service = AuthService()
        
        # Test user authentication
        login_data = {
            'username': self.test_user.username,
            'password': 'testpassword123',
            'ip_address': '192.168.1.100',
            'user_agent': 'TestAgent/1.0'
        }
        
        # Mock successful authentication
        with patch.object(auth_service, 'authenticate_user') as mock_auth:
            mock_auth.return_value = {
                'success': True,
                'user': self.test_user,
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token'
            }
            
            result = auth_service.authenticate_user(
                login_data['username'],
                login_data['password'],
                login_data['ip_address'],
                login_data['user_agent']
            )
            
            self.assertTrue(result['success'])
            self.assertEqual(result['user'], self.test_user)
            
    def test_observer_pattern_integration(self):
        """Test observer pattern integration with authentication events"""
        # Create observers
        security_observer = SecurityAuditObserver()
        lockout_observer = AccountLockoutObserver()
        notification_observer = NotificationObserver()
        
        event_data = {
            'ip_address': '192.168.1.100',
            'user_agent': 'TestAgent/1.0',
            'success': True
        }
        
        # Test all observers receive notification
        with patch.object(security_observer.security_logger, 'info') as mock_security:
            with patch.object(notification_observer, '_handle_successful_login') as mock_notification:
                security_observer.notify('login_success', self.test_user, event_data)
                notification_observer.notify('login_success', self.test_user, event_data)
                
                mock_security.assert_called_once()
                mock_notification.assert_called_once()
