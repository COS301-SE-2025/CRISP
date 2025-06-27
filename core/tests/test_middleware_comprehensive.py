"""
Comprehensive tests for all middleware components
Tests for security, authentication, rate limiting, and session management middleware.
"""
import time
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from core.models.auth import CustomUser, Organization, AuthenticationLog, UserSession
from core.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    AuthenticationMiddleware,
    SecurityAuditMiddleware,
    SessionTimeoutMiddleware,
    SessionActivityMiddleware
)
from core.tests.test_base import CrispTestCase


class SecurityHeadersMiddlewareTest(CrispTestCase):
    """Test SecurityHeadersMiddleware functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware()
    
    def test_security_headers_added(self):
        """Test that security headers are added to responses"""
        request = self.factory.get('/')
        response = HttpResponse()
        
        # Process response through middleware
        response = self.middleware.process_response(request, response)
        
        # Check security headers
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertIn('default-src \'self\'', response['Content-Security-Policy'])
    
    def test_hsts_header_in_production(self):
        """Test HSTS header is added in production"""
        request = self.factory.get('/')
        response = HttpResponse()
        
        with patch.object(settings, 'DEBUG', False):
            response = self.middleware.process_response(request, response)
            self.assertIn('Strict-Transport-Security', response)
            self.assertIn('max-age=31536000', response['Strict-Transport-Security'])
    
    def test_no_hsts_header_in_debug(self):
        """Test HSTS header is not added in debug mode"""
        request = self.factory.get('/')
        response = HttpResponse()
        
        with patch.object(settings, 'DEBUG', True):
            response = self.middleware.process_response(request, response)
            self.assertNotIn('Strict-Transport-Security', response)
    
    def test_csp_header_content(self):
        """Test Content Security Policy header content"""
        request = self.factory.get('/')
        response = HttpResponse()
        
        response = self.middleware.process_response(request, response)
        csp = response['Content-Security-Policy']
        
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self' 'unsafe-inline'", csp)
        self.assertIn("style-src 'self' 'unsafe-inline'", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertIn("frame-src 'none'", csp)


class RateLimitMiddlewareTest(CrispTestCase):
    """Test RateLimitMiddleware functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware()
        # Clear cache before each test
        cache.clear()
    
    def test_rate_limit_disabled(self):
        """Test middleware when rate limiting is disabled"""
        request = self.factory.post('/api/auth/login/')
        
        with patch.object(settings, 'RATELIMIT_ENABLE', False):
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
    
    def test_login_rate_limit(self):
        """Test rate limiting for login endpoint"""
        ip = '192.168.1.100'
        request = self.factory.post('/api/auth/login/', HTTP_X_FORWARDED_FOR=ip)
        
        # First 5 requests should pass
        for i in range(5):
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
        
        # 6th request should be rate limited
        response = self.middleware.process_request(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 429)
        
        # Parse response content
        content = json.loads(response.content.decode())
        self.assertEqual(content['error'], 'rate_limit_exceeded')
        self.assertIn('Too many login attempts', content['message'])
    
    def test_password_reset_rate_limit(self):
        """Test rate limiting for password reset endpoint"""
        ip = '192.168.1.101'
        request = self.factory.post('/api/auth/password-reset/', HTTP_X_FORWARDED_FOR=ip)
        
        # First 3 requests should pass
        for i in range(3):
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
        
        # 4th request should be rate limited
        response = self.middleware.process_request(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 429)
    
    def test_api_rate_limit(self):
        """Test rate limiting for general API endpoints"""
        ip = '192.168.1.102'
        request = self.factory.get('/api/some-endpoint/', HTTP_X_FORWARDED_FOR=ip)
        
        # Mock high frequency requests (100+ in a minute)
        with patch('time.time', return_value=1000000):
            # First 100 requests should pass
            for i in range(100):
                response = self.middleware.process_request(request)
                self.assertIsNone(response)
            
            # 101st request should be rate limited
            response = self.middleware.process_request(request)
            self.assertIsInstance(response, JsonResponse)
            self.assertEqual(response.status_code, 429)
    
    def test_get_client_ip_forwarded(self):
        """Test getting client IP from X-Forwarded-For header"""
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='192.168.1.100,10.0.0.1')
        ip = self.middleware._get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_remote_addr(self):
        """Test getting client IP from REMOTE_ADDR"""
        request = self.factory.get('/', REMOTE_ADDR='192.168.1.103')
        ip = self.middleware._get_client_ip(request)
        self.assertEqual(ip, '192.168.1.103')
    
    def test_get_client_ip_default(self):
        """Test default IP when none available"""
        request = self.factory.get('/')
        ip = self.middleware._get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')
    
    def test_rate_limit_different_ips(self):
        """Test that different IPs have separate rate limits"""
        request1 = self.factory.post('/api/auth/login/', HTTP_X_FORWARDED_FOR='192.168.1.100')
        request2 = self.factory.post('/api/auth/login/', HTTP_X_FORWARDED_FOR='192.168.1.200')
        
        # Exhaust rate limit for first IP
        for i in range(5):
            response = self.middleware.process_request(request1)
            self.assertIsNone(response)
        
        # First IP should be rate limited
        response = self.middleware.process_request(request1)
        self.assertIsInstance(response, JsonResponse)
        
        # Second IP should still work
        response = self.middleware.process_request(request2)
        self.assertIsNone(response)


class AuthenticationMiddlewareTest(CrispTestCase):
    """Test AuthenticationMiddleware functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = AuthenticationMiddleware()
        
        # Create test organization and user
        self.org = Organization.objects.create(
            name="Auth Test Org", domain="authtest.com", contact_email="test@authtest.com"
        )
        self.user = CustomUser.objects.create_user(
            username="auth_user", email="user@authtest.com", password="testpass123",
            organization=self.org, role="admin"
        )
    
    def test_skip_paths(self):
        """Test that certain paths skip authentication"""
        skip_paths = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/password-reset/',
            '/admin/login/',
            '/static/css/style.css',
            '/media/images/logo.png'
        ]
        
        for path in skip_paths:
            request = self.factory.get(path)
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
    
    @patch('core.services.auth_service.AuthenticationService.verify_token')
    def test_valid_jwt_token(self, mock_verify):
        """Test authentication with valid JWT token"""
        mock_verify.return_value = {
            'success': True,
            'user_id': self.user.id
        }
        
        request = self.factory.get('/api/protected/', HTTP_AUTHORIZATION='Bearer valid_token_123')
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.auth, 'valid_token_123')
    
    @patch('core.services.auth_service.AuthenticationService.verify_token')
    def test_invalid_jwt_token(self, mock_verify):
        """Test authentication with invalid JWT token"""
        mock_verify.return_value = {
            'success': False,
            'error': 'Invalid token'
        }
        
        request = self.factory.get('/api/protected/', HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertIsInstance(request.user, AnonymousUser)
    
    def test_no_authorization_header(self):
        """Test request without Authorization header"""
        request = self.factory.get('/api/protected/')
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertIsInstance(request.user, AnonymousUser)
    
    def test_malformed_authorization_header(self):
        """Test request with malformed Authorization header"""
        request = self.factory.get('/api/protected/', HTTP_AUTHORIZATION='InvalidFormat token123')
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertIsInstance(request.user, AnonymousUser)
    
    @patch('core.services.auth_service.AuthenticationService.verify_token')
    def test_user_not_found(self, mock_verify):
        """Test when token is valid but user doesn't exist"""
        mock_verify.return_value = {
            'success': True,
            'user_id': 'non-existent-user-id'
        }
        
        request = self.factory.get('/api/protected/', HTTP_AUTHORIZATION='Bearer valid_token_123')
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertIsInstance(request.user, AnonymousUser)


class SecurityAuditMiddlewareTest(CrispTestCase):
    """Test SecurityAuditMiddleware functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = SecurityAuditMiddleware()
        
        # Create test user
        self.org = Organization.objects.create(
            name="Security Test Org", domain="sectest.com", contact_email="test@sectest.com"
        )
        self.user = CustomUser.objects.create_user(
            username="security_user", email="user@sectest.com", password="testpass123",
            organization=self.org, role="admin"
        )
    
    def test_suspicious_url_patterns(self):
        """Test detection of suspicious patterns in URLs"""
        suspicious_urls = [
            '/api/test?param=<script>alert(1)</script>',
            '/api/test?id=1\' OR 1=1--',
            '/api/test?file=../../../etc/passwd',
            '/api/test?cmd=cmd.exe'
        ]
        
        for url in suspicious_urls:
            with patch.object(self.middleware, '_log_suspicious_activity') as mock_log:
                request = self.factory.get(url)
                self.middleware.process_request(request)
                mock_log.assert_called_once()
    
    def test_suspicious_post_data(self):
        """Test detection of suspicious patterns in POST data"""
        suspicious_data = json.dumps({
            'command': 'eval(malicious_code)',
            'query': 'SELECT * FROM users'
        })
        
        with patch.object(self.middleware, '_log_suspicious_activity') as mock_log:
            request = self.factory.post('/api/test/', 
                                      data=suspicious_data, 
                                      content_type='application/json')
            self.middleware.process_request(request)
            mock_log.assert_called()
    
    def test_normal_requests_not_flagged(self):
        """Test that normal requests are not flagged as suspicious"""
        normal_urls = [
            '/api/users/',
            '/api/organizations/',
            '/api/feeds/?type=malware',
            '/api/stix/indicators/'
        ]
        
        for url in normal_urls:
            with patch.object(self.middleware, '_log_suspicious_activity') as mock_log:
                request = self.factory.get(url)
                self.middleware.process_request(request)
                mock_log.assert_not_called()
    
    @patch('core.middleware.logger')
    def test_log_suspicious_activity(self, mock_logger):
        """Test logging of suspicious activity"""
        request = self.factory.get('/test/', REMOTE_ADDR='192.168.1.100', 
                                 HTTP_USER_AGENT='Mozilla/5.0')
        
        self.middleware._log_suspicious_activity(request, 'Test suspicious pattern')
        
        mock_logger.warning.assert_called_once()
        log_call = mock_logger.warning.call_args[0][0]
        self.assertIn('SUSPICIOUS_ACTIVITY', log_call)
        self.assertIn('192.168.1.100', log_call)
        self.assertIn('Test suspicious pattern', log_call)
    
    def test_log_suspicious_activity_authenticated_user(self):
        """Test logging suspicious activity for authenticated users"""
        request = self.factory.get('/test/', REMOTE_ADDR='192.168.1.100')
        request.user = self.user
        
        with patch('core.models.auth.AuthenticationLog.log_authentication_event') as mock_log:
            self.middleware._log_suspicious_activity(request, 'Test pattern')
            mock_log.assert_called_once()
            
            call_args = mock_log.call_args[1]
            self.assertEqual(call_args['user'], self.user)
            self.assertEqual(call_args['action'], 'suspicious_activity')
            self.assertEqual(call_args['failure_reason'], 'Test pattern')
    
    @patch('core.middleware.logger')
    def test_api_access_logging(self, mock_logger):
        """Test API access logging"""
        request = self.factory.get('/api/admin/users/', REMOTE_ADDR='192.168.1.100')
        request.user = self.user
        
        self.middleware._log_api_access(request)
        
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args[0][0]
        self.assertIn('API_ACCESS', log_call)
        self.assertIn(self.user.username, log_call)
        self.assertIn('/api/admin/users/', log_call)
    
    def test_api_access_logging_insignificant_endpoints(self):
        """Test that insignificant endpoints are not logged"""
        request = self.factory.get('/api/health/', REMOTE_ADDR='192.168.1.100')
        request.user = self.user
        
        with patch('core.middleware.logger') as mock_logger:
            self.middleware._log_api_access(request)
            mock_logger.info.assert_not_called()


class SessionTimeoutMiddlewareTest(CrispTestCase):
    """Test SessionTimeoutMiddleware functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = SessionTimeoutMiddleware()
        
        # Create test user
        self.org = Organization.objects.create(
            name="Session Test Org", domain="session.com", contact_email="test@session.com"
        )
        self.user = CustomUser.objects.create_user(
            username="session_user", email="user@session.com", password="testpass123",
            organization=self.org, role="admin"
        )
    
    @patch('core.services.auth_service.AuthenticationService.verify_token')
    def test_valid_session_continues(self, mock_verify):
        """Test that valid sessions continue processing"""
        mock_verify.return_value = {'success': True}
        
        request = self.factory.get('/api/test/', HTTP_AUTHORIZATION='Bearer valid_token')
        request.user = self.user
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
    
    @patch('core.services.auth_service.AuthenticationService.verify_token')
    def test_expired_session_returns_401(self, mock_verify):
        """Test that expired sessions return 401"""
        mock_verify.return_value = {'success': False, 'error': 'Token expired'}
        
        request = self.factory.get('/api/test/', HTTP_AUTHORIZATION='Bearer expired_token')
        request.user = self.user
        
        response = self.middleware.process_request(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 401)
        
        content = json.loads(response.content.decode())
        self.assertEqual(content['error'], 'token_expired')
    
    def test_unauthenticated_user_continues(self):
        """Test that unauthenticated users continue processing"""
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
    
    @patch('core.middleware.logger')
    def test_cleanup_expired_sessions(self, mock_logger):
        """Test cleanup of expired sessions"""
        # Create expired session
        expired_session = UserSession.objects.create(
            user=self.user,
            session_token='expired_token',
            ip_address='192.168.1.100',
            expires_at=timezone.now() - timedelta(hours=1),
            is_active=True
        )
        
        # Create active session
        active_session = UserSession.objects.create(
            user=self.user,
            session_token='active_token',
            ip_address='192.168.1.101',
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=True
        )
        
        self.middleware._cleanup_expired_sessions()
        
        # Check that expired session is deactivated
        expired_session.refresh_from_db()
        self.assertFalse(expired_session.is_active)
        
        # Check that active session remains active
        active_session.refresh_from_db()
        self.assertTrue(active_session.is_active)
        
        # Check logging
        mock_logger.info.assert_called_once()


class SessionActivityMiddlewareTest(CrispTestCase):
    """Test SessionActivityMiddleware functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = SessionActivityMiddleware(lambda r: None)
        
        # Create test user and session
        self.org = Organization.objects.create(
            name="Activity Test Org", domain="activity.com", contact_email="test@activity.com"
        )
        self.user = CustomUser.objects.create_user(
            username="activity_user", email="user@activity.com", password="testpass123",
            organization=self.org, role="admin"
        )
        
        self.session = UserSession.objects.create(
            user=self.user,
            session_token='test_token_123',
            ip_address='192.168.1.100',
            expires_at=timezone.now() + timedelta(hours=1),
            last_activity=timezone.now() - timedelta(minutes=30),
            is_active=True
        )
    
    def test_update_session_activity(self):
        """Test updating session activity"""
        request = self.factory.get('/api/test/', HTTP_AUTHORIZATION='Bearer test_token_123')
        request.user = self.user
        
        old_activity = self.session.last_activity
        
        self.middleware._update_session_activity(request)
        
        self.session.refresh_from_db()
        self.assertGreater(self.session.last_activity, old_activity)
        self.assertTrue(self.session.is_active)
    
    def test_deactivate_inactive_session(self):
        """Test deactivation of sessions that have been inactive too long"""
        # Set session as inactive for more than max hours
        self.session.last_activity = timezone.now() - timedelta(hours=25)
        self.session.save()
        
        request = self.factory.get('/api/test/', HTTP_AUTHORIZATION='Bearer test_token_123')
        request.user = self.user
        
        with patch.object(settings, 'SESSION_MAX_INACTIVE_HOURS', 24):
            with patch('core.models.auth.AuthenticationLog.log_authentication_event') as mock_log:
                self.middleware._update_session_activity(request)
                
                self.session.refresh_from_db()
                self.assertFalse(self.session.is_active)
                
                # Check that auto-deactivation was logged
                mock_log.assert_called_once()
                call_args = mock_log.call_args[1]
                self.assertEqual(call_args['action'], 'session_auto_deactivated')
    
    def test_no_authorization_header(self):
        """Test handling request without authorization header"""
        request = self.factory.get('/api/test/')
        request.user = self.user
        
        # Should not raise exception
        self.middleware._update_session_activity(request)
    
    def test_session_not_found(self):
        """Test handling when session is not found"""
        request = self.factory.get('/api/test/', HTTP_AUTHORIZATION='Bearer non_existent_token')
        request.user = self.user
        
        # Should not raise exception
        self.middleware._update_session_activity(request)
    
    @patch('core.middleware.cache')
    def test_periodic_cleanup(self, mock_cache):
        """Test periodic cleanup of expired sessions"""
        mock_cache.get.return_value = None  # No previous cleanup
        
        # Create expired session
        expired_session = UserSession.objects.create(
            user=self.user,
            session_token='expired_token',
            ip_address='192.168.1.200',
            expires_at=timezone.now() - timedelta(hours=1),
            is_active=True
        )
        
        with patch('core.middleware.logger') as mock_logger:
            self.middleware._cleanup_expired_sessions_periodically()
            
            expired_session.refresh_from_db()
            self.assertFalse(expired_session.is_active)
            
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            self.assertIn('Cleaned up', log_call)
    
    def test_skip_cleanup_if_recent(self):
        """Test skipping cleanup if it was done recently"""
        recent_time = timezone.now() - timedelta(minutes=2)
        
        with patch('core.middleware.cache.get', return_value=recent_time):
            with patch('core.middleware.UserSession.objects.filter') as mock_filter:
                self.middleware._cleanup_expired_sessions_periodically()
                
                # Should not query for expired sessions
                mock_filter.assert_not_called()
    
    def test_force_cleanup_in_testing(self):
        """Test that cleanup is forced in testing environment"""
        with patch.object(settings, 'TESTING', True):
            with patch('core.middleware.cache.get', return_value=timezone.now()):
                with patch('core.middleware.UserSession.objects.filter') as mock_filter:
                    mock_filter.return_value.count.return_value = 0
                    
                    self.middleware._cleanup_expired_sessions_periodically()
                    
                    # Should query for expired sessions even if recent cleanup
                    mock_filter.assert_called_once()


class MiddlewareIntegrationTest(CrispTestCase):
    """Test middleware integration and interaction"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        
        # Create test data
        self.org = Organization.objects.create(
            name="Integration Test Org", domain="integration.com", contact_email="test@integration.com"
        )
        self.user = CustomUser.objects.create_user(
            username="integration_user", email="user@integration.com", password="testpass123",
            organization=self.org, role="admin"
        )
    
    def test_middleware_chain_processing(self):
        """Test that multiple middleware can process the same request"""
        request = self.factory.get('/api/test/', HTTP_AUTHORIZATION='Bearer test_token')
        request.user = self.user
        
        # Test that each middleware returns None (continues processing)
        security_middleware = SecurityHeadersMiddleware()
        rate_limit_middleware = RateLimitMiddleware()
        auth_middleware = AuthenticationMiddleware()
        audit_middleware = SecurityAuditMiddleware()
        
        # Each should return None (continue processing)
        self.assertIsNone(security_middleware.process_request(request))
        self.assertIsNone(rate_limit_middleware.process_request(request))
        self.assertIsNone(auth_middleware.process_request(request))
        self.assertIsNone(audit_middleware.process_request(request))
    
    def test_rate_limit_blocks_further_processing(self):
        """Test that rate limiting blocks further processing when triggered"""
        ip = '192.168.1.100'
        
        # Exhaust rate limit
        for i in range(5):
            request = self.factory.post('/api/auth/login/', HTTP_X_FORWARDED_FOR=ip)
            rate_limit_middleware = RateLimitMiddleware()
            response = rate_limit_middleware.process_request(request)
            if i < 4:
                self.assertIsNone(response)
        
        # Final request should be blocked
        request = self.factory.post('/api/auth/login/', HTTP_X_FORWARDED_FOR=ip)
        rate_limit_middleware = RateLimitMiddleware()
        response = rate_limit_middleware.process_request(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 429)
    
    def test_security_headers_always_added(self):
        """Test that security headers are added regardless of other middleware"""
        request = self.factory.get('/api/test/')
        response = HttpResponse()
        
        security_middleware = SecurityHeadersMiddleware()
        final_response = security_middleware.process_response(request, response)
        
        # Security headers should always be present
        self.assertIn('X-XSS-Protection', final_response)
        self.assertIn('X-Content-Type-Options', final_response)
        self.assertIn('Content-Security-Policy', final_response)
    
    def test_middleware_error_handling(self):
        """Test middleware behavior when errors occur"""
        request = self.factory.get('/api/test/')
        
        # Test that middleware handles missing user gracefully
        audit_middleware = SecurityAuditMiddleware()
        
        # Should not raise exception even without user
        response = audit_middleware.process_request(request)
        self.assertIsNone(response)
    
    @patch('core.middleware.logger')
    def test_middleware_logging_integration(self, mock_logger):
        """Test that middleware logging works correctly"""
        request = self.factory.get('/api/admin/test?param=<script>alert(1)</script>', 
                                 REMOTE_ADDR='192.168.1.100')
        request.user = self.user
        
        audit_middleware = SecurityAuditMiddleware()
        audit_middleware.process_request(request)
        
        # Should log both suspicious activity and API access
        self.assertGreaterEqual(mock_logger.warning.call_count, 1)  # Suspicious activity
        self.assertGreaterEqual(mock_logger.info.call_count, 1)     # API access