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

from ..models import CustomUser, Organization, UserSession, AuthenticationLog
from ..middleware import (
    SecurityHeadersMiddleware, RateLimitMiddleware, SecurityAuditMiddleware, 
    SessionTimeoutMiddleware, AuthenticationMiddleware, SessionActivityMiddleware
)
from ..factories.user_factory import UserFactory
from .test_base import CrispTestCase
import json
import time

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


class SecurityAuditMiddlewareTestCase(CrispTestCase):
    """Test security audit middleware"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = SecurityAuditMiddleware(get_response=lambda r: HttpResponse())
        
        # Create test user using base method
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com'
        )
    
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


class SessionTimeoutMiddlewareTestCase(CrispTestCase):
    """Test session timeout middleware"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = SessionTimeoutMiddleware(get_response=lambda r: HttpResponse())
        
        # Create test user using base method
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com'
        )
    
    def test_valid_token_passes(self):
        """Test that valid tokens pass through"""
        request = self.factory.get('/api/users/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer valid_token'
        
        # Mock the auth service verify_token method
        with patch('core.middleware.AuthenticationService.verify_token') as mock_verify:
            mock_verify.return_value = {'success': True, 'user': self.test_user}
            
            response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
    
    def test_invalid_token_returns_401(self):
        """Test that invalid tokens return 401"""
        request = self.factory.get('/api/users/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token'
        
        # Mock the auth service verify_token method
        with patch('core.middleware.AuthenticationService.verify_token') as mock_verify:
            mock_verify.return_value = {'success': False, 'message': 'Invalid token'}
            
            response = self.middleware(request)
            self.assertEqual(response.status_code, 401)
    
    
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


class MiddlewareIntegrationTestCase(CrispTestCase):
    """Test middleware integration"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        
        # Create test user using base method
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com'
        )
    
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


class AuthenticationMiddlewareTestCase(CrispTestCase):
    """Test AuthenticationMiddleware"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = AuthenticationMiddleware(get_response=lambda r: HttpResponse())
        self.test_user = self.create_test_user(role='viewer')
    
    def test_skip_paths(self):
        """Test that certain paths are skipped"""
        skip_paths = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/password-reset/',
            '/admin/',
            '/static/test.css',
            '/media/test.jpg'
        ]
        
        for path in skip_paths:
            request = self.factory.get(path)
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
    
    def test_valid_bearer_token(self):
        """Test processing with valid Bearer token"""
        request = self.factory.get('/api/users/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer valid_token'
        
        with patch.object(self.middleware.auth_service, 'verify_token') as mock_verify:
            mock_verify.return_value = {
                'success': True,
                'user_id': str(self.test_user.id)
            }
            
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
            self.assertEqual(request.user, self.test_user)
            self.assertEqual(request.auth, 'valid_token')
    
    def test_invalid_bearer_token(self):
        """Test processing with invalid Bearer token"""
        request = self.factory.get('/api/users/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token'
        
        with patch.object(self.middleware.auth_service, 'verify_token') as mock_verify:
            mock_verify.return_value = {
                'success': False,
                'message': 'Invalid token'
            }
            
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
            self.assertTrue(hasattr(request, 'user'))
    
    def test_malformed_authorization_header(self):
        """Test processing with malformed authorization header"""
        request = self.factory.get('/api/users/')
        request.META['HTTP_AUTHORIZATION'] = 'Invalid header format'
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        self.assertTrue(hasattr(request, 'user'))
    
    def test_no_authorization_header(self):
        """Test processing without authorization header"""
        request = self.factory.get('/api/users/')
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        self.assertTrue(hasattr(request, 'user'))
    
    def test_user_does_not_exist(self):
        """Test processing when user from token doesn't exist"""
        request = self.factory.get('/api/users/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer valid_token'
        
        with patch.object(self.middleware.auth_service, 'verify_token') as mock_verify:
            mock_verify.return_value = {
                'success': True,
                'user_id': 'non-existent-uuid'
            }
            
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
            self.assertTrue(hasattr(request, 'user'))


class SessionActivityMiddlewareTestCase(CrispTestCase):
    """Test SessionActivityMiddleware"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = SessionActivityMiddleware(get_response=lambda r: HttpResponse())
        self.test_user = self.create_test_user(role='viewer')
    
    def test_update_session_activity_success(self):
        """Test successful session activity update"""
        # Create active session
        session = UserSession.objects.create(
            user=self.test_user,
            session_token='test_token',
            refresh_token='test_refresh',
            device_info={},
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=True,
            last_activity=timezone.now() - timedelta(minutes=30)
        )
        
        old_activity = session.last_activity
        
        request = self.factory.get('/api/test/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer test_token'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        self.middleware._update_session_activity(request)
        
        session.refresh_from_db()
        self.assertGreater(session.last_activity, old_activity)
        self.assertTrue(session.is_active)
    
    def test_update_session_activity_inactive_too_long(self):
        """Test session deactivation when inactive too long"""
        # Create session that's been inactive too long
        session = UserSession.objects.create(
            user=self.test_user,
            session_token='test_token',
            refresh_token='test_refresh',
            device_info={},
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=True,
            last_activity=timezone.now() - timedelta(hours=25)  # Inactive for 25 hours
        )
        
        request = self.factory.get('/api/test/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer test_token'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        
        with patch('core.models.auth.AuthenticationLog.log_authentication_event') as mock_log:
            self.middleware._update_session_activity(request)
            mock_log.assert_called_once()
        
        session.refresh_from_db()
        self.assertFalse(session.is_active)
    
    def test_update_session_activity_no_bearer_token(self):
        """Test session activity update without Bearer token"""
        request = self.factory.get('/api/test/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Basic dGVzdA=='
        
        # Should not raise exception
        self.middleware._update_session_activity(request)
    
    def test_update_session_activity_session_not_found(self):
        """Test session activity update when session doesn't exist"""
        request = self.factory.get('/api/test/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer nonexistent_token'
        
        # Should not raise exception
        self.middleware._update_session_activity(request)
    
    def test_update_session_activity_error_handling(self):
        """Test error handling in session activity update"""
        request = self.factory.get('/api/test/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer test_token'
        
        with patch('core.models.UserSession.objects.get', side_effect=Exception('DB Error')):
            with patch('core.middleware.logger.error') as mock_logger:
                self.middleware._update_session_activity(request)
                mock_logger.assert_called_once()
    
    @override_settings(TESTING=True)
    def test_cleanup_expired_sessions_in_testing(self):
        """Test periodic session cleanup in testing environment"""
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
        
        self.middleware._cleanup_expired_sessions_periodically()
        
        expired_session.refresh_from_db()
        self.assertFalse(expired_session.is_active)
    
    def test_process_request_authenticated_user(self):
        """Test process_request with authenticated user"""
        request = self.factory.get('/api/test/')
        request.user = self.test_user
        request.META['HTTP_AUTHORIZATION'] = 'Bearer test_token'
        
        with patch.object(self.middleware, '_update_session_activity') as mock_update:
            with patch.object(self.middleware, '_cleanup_expired_sessions_periodically') as mock_cleanup:
                response = self.middleware.process_request(request)
                self.assertIsNone(response)
                mock_update.assert_called_once_with(request)
                mock_cleanup.assert_called_once()


class ComprehensiveMiddlewareTestCase(CrispTestCase):
    """Comprehensive middleware functionality tests"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.test_user = self.create_test_user(role='admin')
    
    def test_rate_limit_get_client_ip_methods(self):
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
        
        # Test fallback
        request = self.factory.get('/')
        request.META.pop('HTTP_X_FORWARDED_FOR', None)
        request.META.pop('REMOTE_ADDR', None)
        ip = middleware._get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')
    
    def test_rate_limit_response_format(self):
        """Test rate limit response format"""
        middleware = RateLimitMiddleware(get_response=lambda r: HttpResponse())
        response = middleware._rate_limit_response('Test message')
        
        self.assertEqual(response.status_code, 429)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'rate_limit_exceeded')
        self.assertEqual(response_data['message'], 'Test message')
    
    def test_security_audit_suspicious_patterns(self):
        """Test SecurityAuditMiddleware suspicious pattern detection"""
        middleware = SecurityAuditMiddleware(get_response=lambda r: HttpResponse())
        
        suspicious_patterns = [
            'eval(', 'exec(', '<script', 'javascript:', 'vbscript:',
            'SELECT * FROM', 'DROP TABLE', 'UNION SELECT',
            '../../../', '..\\..\\..\\',
            'cmd.exe', '/bin/bash', '/bin/sh'
        ]
        
        for pattern in suspicious_patterns:
            request = self.factory.get(f'/api/test/?q={pattern}')
            request.user = self.test_user
            request.META['REMOTE_ADDR'] = '192.168.1.1'
            request.META['HTTP_USER_AGENT'] = 'Test Agent'
            
            with patch.object(middleware, '_log_suspicious_activity') as mock_log:
                middleware.process_request(request)
                mock_log.assert_called_once()
    
    def test_security_headers_comprehensive(self):
        """Test comprehensive security headers"""
        middleware = SecurityHeadersMiddleware(get_response=lambda r: HttpResponse())
        request = self.factory.get('/')
        response = middleware.process_response(request, HttpResponse())
        
        expected_headers = {
            'X-XSS-Protection': '1; mode=block',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; media-src 'self'; frame-src 'none';"
        }
        
        for header, value in expected_headers.items():
            self.assertIn(header, response)
            self.assertEqual(response[header], value)
    
    def test_session_timeout_cleanup_comprehensive(self):
        """Test comprehensive session timeout cleanup"""
        middleware = SessionTimeoutMiddleware(get_response=lambda r: HttpResponse())
        
        # Create multiple expired sessions
        for i in range(3):
            UserSession.objects.create(
                user=self.test_user,
                session_token=f'expired_token_{i}',
                refresh_token=f'expired_refresh_{i}',
                device_info={},
                ip_address='127.0.0.1',
                expires_at=timezone.now() - timedelta(hours=i+1),
                is_active=True
            )
        
        # Create active session
        active_session = UserSession.objects.create(
            user=self.test_user,
            session_token='active_token',
            refresh_token='active_refresh',
            device_info={},
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=True
        )
        
        middleware._cleanup_expired_sessions()
        
        # Check that expired sessions are deactivated
        expired_count = UserSession.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=False
        ).count()
        self.assertEqual(expired_count, 3)
        
        # Check that active session remains active
        active_session.refresh_from_db()
        self.assertTrue(active_session.is_active)