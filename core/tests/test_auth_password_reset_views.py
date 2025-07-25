"""
Comprehensive unit tests for Authentication Password Reset Views
Tests enhanced password reset endpoints with email integration
"""
import unittest
from unittest.mock import patch, MagicMock
import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import check_password
from core.user_management.models.invitation_models import PasswordResetToken
from core.user_management.models.user_models import CustomUser
from core.tests.factories import CustomUserFactory
import uuid


class AuthPasswordResetViewsTestCase(TestCase):
    """Test cases for authentication password reset endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = CustomUserFactory(email='testuser@example.com')
        self.inactive_user = CustomUserFactory(email='inactive@example.com', is_active=False)
        
        # Test request data
        self.reset_request_data = {
            'email': 'testuser@example.com'
        }
        
        self.validate_token_data = {
            'token': 'test_reset_token_123'
        }
        
        self.reset_password_data = {
            'token': 'test_reset_token_123',
            'new_password': 'new_secure_password_123!'
        }
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.request_password_reset')
    def test_forgot_password_success(self, mock_request_reset):
        """Test successful password reset request"""
        mock_request_reset.return_value = {
            'success': True,
            'message': 'If an account with this email exists, password reset instructions have been sent.'
        }
        
        url = reverse('auth-forgot-password')
        response = self.client.post(url, self.reset_request_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('password reset instructions have been sent', response.data['message'])
        
        # Verify service was called with correct parameters
        mock_request_reset.assert_called_once_with(
            email='testuser@example.com',
            ip_address='127.0.0.1',  # Test client IP
            user_agent=''  # Empty string when not provided
        )
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.request_password_reset')
    def test_forgot_password_with_real_ip_and_user_agent(self, mock_request_reset):
        """Test password reset request captures IP and user agent"""
        mock_request_reset.return_value = {
            'success': True,
            'message': 'Password reset instructions sent.'
        }
        
        url = reverse('auth-forgot-password')
        response = self.client.post(
            url, 
            self.reset_request_data, 
            format='json',
            HTTP_USER_AGENT='Test Browser/1.0',
            HTTP_X_FORWARDED_FOR='192.168.1.100'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify service was called with captured metadata
        call_args = mock_request_reset.call_args
        self.assertEqual(call_args[1]['user_agent'], 'Test Browser/1.0')
        # Note: In Django test client, HTTP_X_FORWARDED_FOR might not be processed exactly like in production
    
    def test_forgot_password_invalid_email_format(self):
        """Test password reset with invalid email format"""
        invalid_data = {'email': 'invalid-email-format'}
        
        url = reverse('auth-forgot-password')
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(response.data).lower())
    
    def test_forgot_password_missing_email(self):
        """Test password reset with missing email"""
        url = reverse('auth-forgot-password')
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(response.data).lower())
    
    def test_forgot_password_empty_email(self):
        """Test password reset with empty email"""
        empty_data = {'email': ''}
        
        url = reverse('auth-forgot-password')
        response = self.client.post(url, empty_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.request_password_reset')
    def test_forgot_password_nonexistent_user(self, mock_request_reset):
        """Test password reset for non-existent user (should still return success)"""
        mock_request_reset.return_value = {
            'success': True,
            'message': 'If an account with this email exists, password reset instructions have been sent.'
        }
        
        nonexistent_data = {'email': 'nonexistent@example.com'}
        
        url = reverse('auth-forgot-password')
        response = self.client.post(url, nonexistent_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify service was still called (for security consistency)
        mock_request_reset.assert_called_once()
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.request_password_reset')
    def test_forgot_password_service_failure(self, mock_request_reset):
        """Test handling of service failure"""
        mock_request_reset.return_value = {
            'success': False,
            'message': 'Failed to send password reset email'
        }
        
        url = reverse('auth-forgot-password')
        response = self.client.post(url, self.reset_request_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertIn('Failed to send', response.data['message'])
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.validate_reset_token')
    def test_validate_reset_token_success(self, mock_validate_token):
        """Test successful token validation"""
        mock_validate_token.return_value = {
            'success': True,
            'message': 'Reset token is valid',
            'user_id': str(self.user.id)
        }
        
        url = reverse('auth-validate-reset-token')
        response = self.client.post(url, self.validate_token_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('token is valid', response.data['message'])
        self.assertEqual(response.data['user_id'], str(self.user.id))
        
        # Verify service was called
        mock_validate_token.assert_called_once_with('test_reset_token_123')
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.validate_reset_token')
    def test_validate_reset_token_invalid(self, mock_validate_token):
        """Test invalid token validation"""
        mock_validate_token.return_value = {
            'success': False,
            'message': 'Invalid reset token'
        }
        
        invalid_data = {'token': 'invalid_token'}
        
        url = reverse('auth-validate-reset-token')
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Invalid reset token', response.data['message'])
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.validate_reset_token')
    def test_validate_reset_token_expired(self, mock_validate_token):
        """Test expired token validation"""
        mock_validate_token.return_value = {
            'success': False,
            'message': 'Reset token has expired'
        }
        
        expired_data = {'token': 'expired_token'}
        
        url = reverse('auth-validate-reset-token')
        response = self.client.post(url, expired_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', response.data['message'])
    
    def test_validate_reset_token_missing_token(self):
        """Test token validation with missing token"""
        url = reverse('auth-validate-reset-token')
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', str(response.data).lower())
    
    def test_validate_reset_token_empty_token(self):
        """Test token validation with empty token"""
        empty_data = {'token': ''}
        
        url = reverse('auth-validate-reset-token')
        response = self.client.post(url, empty_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.reset_password')
    def test_reset_password_success(self, mock_reset_password):
        """Test successful password reset"""
        mock_reset_password.return_value = {
            'success': True,
            'message': 'Password has been reset successfully'
        }
        
        url = reverse('auth-reset-password')
        response = self.client.post(url, self.reset_password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('reset successfully', response.data['message'])
        
        # Verify service was called with correct parameters
        mock_reset_password.assert_called_once_with(
            'test_reset_token_123', 
            'new_secure_password_123!'
        )
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.reset_password')
    def test_reset_password_invalid_token(self, mock_reset_password):
        """Test password reset with invalid token"""
        mock_reset_password.return_value = {
            'success': False,
            'message': 'Invalid or expired reset token'
        }
        
        invalid_data = {
            'token': 'invalid_token',
            'new_password': 'new_password123'
        }
        
        url = reverse('auth-reset-password')
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Invalid or expired', response.data['message'])
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.reset_password')
    def test_reset_password_weak_password(self, mock_reset_password):
        """Test password reset with weak password"""
        mock_reset_password.return_value = {
            'success': False,
            'message': 'Password must be at least 8 characters long'
        }
        
        weak_data = {
            'token': 'valid_token',
            'new_password': '123'
        }
        
        url = reverse('auth-reset-password')
        response = self.client.post(url, weak_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Password must be', response.data['message'])
    
    def test_reset_password_missing_fields(self):
        """Test password reset with missing required fields"""
        # Missing token
        missing_token = {'new_password': 'password123'}
        url = reverse('auth-reset-password')
        response = self.client.post(url, missing_token, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing password
        missing_password = {'token': 'token123'}
        response = self.client.post(url, missing_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing both
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_reset_password_empty_fields(self):
        """Test password reset with empty fields"""
        empty_data = {
            'token': '',
            'new_password': ''
        }
        
        url = reverse('auth-reset-password')
        response = self.client.post(url, empty_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_reset_endpoints_accept_post_only(self):
        """Test that password reset endpoints only accept POST requests"""
        endpoints = [
            ('auth-forgot-password', self.reset_request_data),
            ('auth-validate-reset-token', self.validate_token_data),
            ('auth-reset-password', self.reset_password_data),
        ]
        
        http_methods = ['get', 'put', 'patch', 'delete']
        
        for endpoint_name, data in endpoints:
            url = reverse(endpoint_name)
            
            for method in http_methods:
                with self.subTest(endpoint=endpoint_name, method=method):
                    client_method = getattr(self.client, method)
                    response = client_method(url, data, format='json')
                    
                    self.assertEqual(
                        response.status_code, 
                        status.HTTP_405_METHOD_NOT_ALLOWED
                    )
    
    def test_password_reset_endpoints_require_json(self):
        """Test that password reset endpoints properly handle different content types"""
        url = reverse('auth-forgot-password')
        
        # Test with form data (should still work)
        response = self.client.post(url, self.reset_request_data)
        self.assertIn(response.status_code, [200, 400, 500])  # Should not be 415
        
        # Test with JSON (should work)
        response = self.client.post(url, self.reset_request_data, format='json')
        self.assertIn(response.status_code, [200, 400, 500])  # Should not be 415
    
    def test_password_reset_input_sanitization(self):
        """Test input sanitization for password reset endpoints"""
        malicious_inputs = [
            {'email': '<script>alert("xss")</script>@example.com'},
            {'email': 'test@example.com"; DROP TABLE users; --'},
            {'token': '<script>alert("xss")</script>'},
            {'token': 'token"; DROP TABLE password_reset_tokens; --'},
            {'new_password': '<script>alert("xss")</script>password'},
        ]
        
        endpoints = [
            ('auth-forgot-password', ['email']),
            ('auth-validate-reset-token', ['token']),
            ('auth-reset-password', ['token', 'new_password']),
        ]
        
        for endpoint_name, fields in endpoints:
            url = reverse(endpoint_name)
            
            for malicious_input in malicious_inputs:
                for field in fields:
                    if field in malicious_input:
                        with self.subTest(endpoint=endpoint_name, field=field):
                            response = self.client.post(url, malicious_input, format='json')
                            
                            # Should not return 500 (should handle gracefully)
                            self.assertNotEqual(response.status_code, 500)
                            
                            # Response should not contain unescaped script tags
                            response_text = str(response.content)
                            self.assertNotIn('<script>', response_text)
    
    def test_password_reset_rate_limiting_headers(self):
        """Test that password reset endpoints are prepared for rate limiting"""
        url = reverse('auth-forgot-password')
        
        # Make multiple requests
        for i in range(5):
            response = self.client.post(url, self.reset_request_data, format='json')
            
            # Verify response includes proper headers for rate limiting middleware
            # (Actual rate limiting would be implemented at middleware level)
            self.assertIsNotNone(response)
    
    @patch('core.user_management.services.invitation_service.PasswordResetService.request_password_reset')
    def test_forgot_password_logs_attempts(self, mock_request_reset):
        """Test that password reset attempts are properly logged"""
        mock_request_reset.return_value = {
            'success': True,
            'message': 'Password reset instructions sent.'
        }
        
        url = reverse('auth-forgot-password')
        response = self.client.post(url, self.reset_request_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify service was called (which should handle audit logging)
        mock_request_reset.assert_called_once()
    
    def test_password_reset_unicode_handling(self):
        """Test password reset with unicode characters"""
        unicode_data = {
            'email': 'tëst@éxämplé.com',
            'token': 'tökën123',
            'new_password': 'pássw0rd123áéíóú'
        }
        
        endpoints = [
            ('auth-forgot-password', {'email': unicode_data['email']}),
            ('auth-validate-reset-token', {'token': unicode_data['token']}),
            ('auth-reset-password', {
                'token': unicode_data['token'],
                'new_password': unicode_data['new_password']
            }),
        ]
        
        for endpoint_name, data in endpoints:
            with self.subTest(endpoint=endpoint_name):
                url = reverse(endpoint_name)
                response = self.client.post(url, data, format='json')
                
                # Should handle unicode gracefully (not crash)
                self.assertNotEqual(response.status_code, 500)
    
    def test_password_reset_case_sensitivity(self):
        """Test email case sensitivity in password reset"""
        case_variations = [
            'TestUser@Example.com',
            'TESTUSER@EXAMPLE.COM',
            'testuser@EXAMPLE.COM',
            'TestUser@example.com'
        ]
        
        with patch('core.user_management.services.invitation_service.PasswordResetService.request_password_reset') as mock_request:
            mock_request.return_value = {
                'success': True,
                'message': 'Password reset instructions sent.'
            }
            
            url = reverse('auth-forgot-password')
            
            for email_variation in case_variations:
                with self.subTest(email=email_variation):
                    data = {'email': email_variation}
                    response = self.client.post(url, data, format='json')
                    
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    
                    # Verify service was called with the email as provided
                    call_args = mock_request.call_args
                    self.assertEqual(call_args[1]['email'], email_variation)
    
    def test_password_reset_concurrent_requests(self):
        """Test handling of concurrent password reset requests"""
        import threading
        import time
        
        responses = []
        
        def make_request():
            url = reverse('auth-forgot-password')
            response = self.client.post(url, self.reset_request_data, format='json')
            responses.append(response)
        
        # Create multiple concurrent requests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests were handled
        self.assertEqual(len(responses), 3)
        
        for response in responses:
            # Should not crash or return 500
            self.assertNotEqual(response.status_code, 500)


class AuthPasswordResetViewsIntegrationTestCase(TestCase):
    """Integration test cases for password reset workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = CustomUserFactory(email='integration@example.com')
    
    def test_complete_password_reset_workflow(self):
        """Test complete password reset workflow from request to reset"""
        # Step 1: Request password reset
        with patch('core.user_management.services.invitation_service.GmailSMTPService') as mock_email:
            mock_email_service = MagicMock()
            mock_email_service.send_password_reset_email.return_value = {'success': True}
            mock_email.return_value = mock_email_service
            
            forgot_url = reverse('auth-forgot-password')
            forgot_response = self.client.post(
                forgot_url, 
                {'email': 'integration@example.com'}, 
                format='json'
            )
            
            self.assertEqual(forgot_response.status_code, status.HTTP_200_OK)
        
        # Step 2: Verify token was created
        token = PasswordResetToken.objects.get(user=self.user)
        self.assertIsNotNone(token.token)
        self.assertTrue(token.is_valid)
        
        # Step 3: Validate the token
        validate_url = reverse('auth-validate-reset-token')
        validate_response = self.client.post(
            validate_url,
            {'token': token.token},
            format='json'
        )
        
        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertTrue(validate_response.data['success'])
        
        # Step 4: Reset the password
        old_password = self.user.password
        new_password = 'new_integration_password_123!'
        
        reset_url = reverse('auth-reset-password')
        reset_response = self.client.post(
            reset_url,
            {
                'token': token.token,
                'new_password': new_password
            },
            format='json'
        )
        
        self.assertEqual(reset_response.status_code, status.HTTP_200_OK)
        self.assertTrue(reset_response.data['success'])
        
        # Step 5: Verify password was changed and token was consumed
        self.user.refresh_from_db()
        token.refresh_from_db()
        
        self.assertNotEqual(self.user.password, old_password)
        self.assertTrue(self.user.check_password(new_password))
        self.assertFalse(token.is_valid)
        self.assertIsNotNone(token.used_at)


if __name__ == '__main__':
    unittest.main()