"""
Tests for middleware functionality
"""
from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from unittest.mock import Mock, patch

from ..models import CustomUser, Organization, UserSession
from ..middleware import SecurityHeadersMiddleware, RateLimitMiddleware, SecurityAuditMiddleware, SessionTimeoutMiddleware
from ..factories.user_factory import UserFactory

User = get_user_model()


class SecurityHeadersMiddlewareTestCase(TestCase):
    """Test security headers middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(get_response=lambda r: HttpResponse())
    
    def test_security_headers_added(self):
        """Test that security headers are added to response"""
        request = self.factory.get('/')
        
        response = self.middleware(request)
        
        # Check that security headers are present
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        
        self.assertIn('X-XSS-Protection', response)
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        
        self.assertIn('Referrer-Policy', response)
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')
    
    @patch('django.conf.settings.DEBUG', False)
    def test_hsts_header_in_production(self):
        """Test HSTS header is added in production"""
        request = self.factory.get('/')
        
        response = self.middleware(request)
        
        self.assertIn('Strict-Transport-Security', response)
        self.assertEqual(response['Strict-Transport-Security'], 'max-age=31536000; includeSubDomains')


class RateLimitMiddlewareTestCase(TestCase):
    """Test rate limiting middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(get_response=lambda r: HttpResponse())
        cache.clear()  # Clear cache before each test
    
    def test_rate_limiting_under_threshold(self):
        """Test that requests under threshold are allowed"""
        request = self.factory.post('/api/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
    
    def test_rate_limiting_over_threshold(self):
        """Test that requests over threshold are blocked"""
        request = self.factory.post('/api/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Simulate multiple requests to exceed threshold
        with patch('django.core.cache.cache.get', return_value=20):  # Simulate 20 requests already
            response = self.middleware(request)
            self.assertEqual(response.status_code, 429)
    
    def test_different_ips_not_rate_limited_together(self):
        """Test that different IPs are rate limited separately"""
        request1 = self.factory.post('/api/auth/login/')
        request1.META['REMOTE_ADDR'] = '127.0.0.1'
        
        request2 = self.factory.post('/api/auth/login/')
        request2.META['REMOTE_ADDR'] = '127.0.0.2'
        
        response1 = self.middleware(request1)
        response2 = self.middleware(request2)
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
    
    @override_settings(RATELIMIT_ENABLE=False)
    def test_rate_limiting_disabled(self):
        """Test that rate limiting can be disabled"""
        request = self.factory.post('/api/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Even with high request count, should not be rate limited when disabled
        with patch('django.core.cache.cache.get', return_value=100):
            response = self.middleware(request)
            self.assertEqual(response.status_code, 200)


class SecurityAuditMiddlewareTestCase(TestCase):
    """Test security audit middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityAuditMiddleware(get_response=lambda r: HttpResponse())
        
        # Create test organization and user
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        self.test_user = UserFactory.create_user('viewer', {
            'username': 'testuser',
            'email': 'testuser@test.com',
            'password': 'TestPassword123!',
            'organization': self.organization
        })
    
    def test_api_access_logging(self):
        """Test that API access is logged"""
        request = self.factory.get('/api/users/')
        request.user = self.test_user
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        
        response = self.middleware(request)
        
        # Check that the request was processed
        self.assertEqual(response.status_code, 200)
    
    def test_suspicious_pattern_detection(self):
        """Test detection of suspicious patterns"""
        request = self.factory.post('/api/auth/login/')
        request.user = self.test_user
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        request._body = b'password=\'; DROP TABLE users; --'
        
        response = self.middleware(request)
        
        # Check that the request was processed (suspicious patterns logged but not blocked)
        self.assertEqual(response.status_code, 200)
    
    def test_post_data_inspection(self):
        """Test inspection of POST data"""
        request = self.factory.post('/api/users/', {'username': 'testuser', 'password': 'test123'})
        request.user = self.test_user
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        
        response = self.middleware(request)
        
        # Check that the request was processed
        self.assertEqual(response.status_code, 200)


class SessionTimeoutMiddlewareTestCase(TestCase):
    """Test session timeout middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SessionTimeoutMiddleware(get_response=lambda r: HttpResponse())
        
        # Create test organization and user
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        self.test_user = UserFactory.create_user('viewer', {
            'username': 'testuser',
            'email': 'testuser@test.com',
            'password': 'TestPassword123!',
            'organization': self.organization
        })
    
    def test_valid_token_passes(self):
        """Test that valid tokens pass through"""
        request = self.factory.get('/api/users/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer valid_token'
        
        # Mock the auth service verify_token method
        with patch('UserManagement.middleware.AuthenticationService.verify_token') as mock_verify:
            mock_verify.return_value = {'success': True, 'user': self.test_user}
            
            response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
    
    def test_invalid_token_returns_401(self):
        """Test that invalid tokens return 401"""
        request = self.factory.get('/api/users/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token'
        
        # Mock the auth service verify_token method
        with patch('UserManagement.middleware.AuthenticationService.verify_token') as mock_verify:
            mock_verify.return_value = {'success': False, 'message': 'Invalid token'}
            
            response = self.middleware(request)
            self.assertEqual(response.status_code, 401)
    
    def test_session_activity_update(self):
        """Test that session activity is updated"""
        # Create a session for the user
        session = UserSession.objects.create(
            user=self.test_user,
            session_token='test_token',
            refresh_token='test_refresh',
            device_info={},
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        request = self.factory.get('/api/users/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer test_token'
        
        original_activity = session.last_activity
        
        # Mock the auth service verify_token method
        with patch('UserManagement.middleware.AuthenticationService.verify_token') as mock_verify:
            mock_verify.return_value = {'success': True, 'user': self.test_user}
            
            response = self.middleware(request)
            
            # Check that session activity was updated
            session.refresh_from_db()
            self.assertGreater(session.last_activity, original_activity)
    
    def test_session_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions"""
        # Create expired session
        expired_session = UserSession.objects.create(
            user=self.test_user,
            session_token='expired_token',
            refresh_token='expired_refresh',
            device_info={},
            ip_address='127.0.0.1',
            expires_at=timezone.now() - timedelta(hours=1),  # Expired
            is_active=True
        )
        
        request = self.factory.get('/api/users/')
        request.user = self.test_user
        
        response = self.middleware(request)
        
        # Check that expired session was deactivated
        expired_session.refresh_from_db()
        self.assertFalse(expired_session.is_active)


class MiddlewareIntegrationTestCase(TestCase):
    """Test middleware integration"""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create test organization and user
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        self.test_user = UserFactory.create_user('viewer', {
            'username': 'testuser',
            'email': 'testuser@test.com',
            'password': 'TestPassword123!',
            'organization': self.organization
        })
    
    def test_middleware_chain_execution(self):
        """Test that middleware chain executes properly"""
        # Create a simple middleware chain
        def get_response(request):
            return HttpResponse('OK')
        
        # Chain middlewares
        session_middleware = SessionTimeoutMiddleware(get_response)
        audit_middleware = SecurityAuditMiddleware(session_middleware)
        rate_middleware = RateLimitMiddleware(audit_middleware)
        security_middleware = SecurityHeadersMiddleware(rate_middleware)
        
        request = self.factory.get('/api/users/')
        request.user = self.test_user
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        
        response = security_middleware(request)
        
        # Check that response has security headers from the chain
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response.status_code, 200)