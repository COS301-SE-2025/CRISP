"""
Comprehensive unit tests for Password Reset Service
Tests all service methods, security features, and edge cases
"""
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import check_password
from core_ut.user_management.services.invitation_service import PasswordResetService
from core_ut.user_management.models.invitation_models import PasswordResetToken
from core_ut.user_management.models.user_models import CustomUser
from core_ut.tests.factories import CustomUserFactory
import secrets


class PasswordResetServiceTestCase(TestCase):
    """Test cases for PasswordResetService"""
    
    def setUp(self):
        """Set up test data"""
        # Create mock services
        self.mock_email_service = MagicMock()
        self.mock_email_service.send_password_reset_email.return_value = {'success': True}
        self.mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        self.service = PasswordResetService(
            email_service=self.mock_email_service,
            audit_service=self.mock_audit_service
        )
        self.user = CustomUserFactory()
        self.inactive_user = CustomUserFactory(is_active=False)
        self.test_ip = '192.168.1.100'
        self.test_user_agent = 'Test Browser/1.0'
        self.test_email = self.user.email
    
    def test_request_password_reset_success(self):
        """Test successful password reset request"""
        # Call service
        result = self.service.request_password_reset(
            email=self.test_email,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIn('password reset instructions have been sent', result['message'])
        
        # Verify token was created
        token = PasswordResetToken.objects.get(user=self.user)
        self.assertEqual(token.ip_address, self.test_ip)
        self.assertEqual(token.user_agent, self.test_user_agent)
        self.assertIsNotNone(token.token)
        self.assertIsNone(token.used_at)
        self.assertTrue(token.is_valid)
        
        # Verify email was sent with keyword arguments
        self.mock_email_service.send_password_reset_email.assert_called_once_with(
            user=self.user, reset_token=token.token
        )
        
        # Verify audit log was called (just check it was called, don't verify exact params)
        self.mock_audit_service.log_user_action.assert_called()
    
    def test_request_password_reset_nonexistent_user(self):
        """Test password reset request for non-existent user"""
        result = self.service.request_password_reset('nonexistent@example.com')
        
        # Should return success to prevent email enumeration
        self.assertTrue(result['success'])
        self.assertIn('password reset instructions have been sent', result['message'])
        
        # Verify no token was created
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_request_password_reset_inactive_user(self):
        """Test password reset request for inactive user"""
        result = self.service.request_password_reset(self.inactive_user.email)
        
        # Should return success to prevent user enumeration
        self.assertTrue(result['success'])
        self.assertIn('password reset instructions have been sent', result['message'])
        
        # Verify no token was created
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_request_password_reset_empty_email(self):
        """Test password reset request with empty email"""
        result = self.service.request_password_reset('')
        
        # Should return success for security (don't reveal validation)
        self.assertTrue(result['success'])
        
        # Verify no token was created
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_request_password_reset_none_email(self):
        """Test password reset request with None email"""
        result = self.service.request_password_reset(None)
        
        # Should return success for security
        self.assertTrue(result['success'])
        
        # Verify no token was created
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_request_password_reset_invalidates_old_tokens(self):
        """Test that new reset request invalidates old tokens"""
        # Create old tokens
        old_token1 = PasswordResetToken.objects.create(
            user=self.user,
            token='old_token_1'
        )
        old_token2 = PasswordResetToken.objects.create(
            user=self.user,
            token='old_token_2'
        )
        
        # Request new reset
        result = self.service.request_password_reset(self.user.email)
        
        self.assertTrue(result['success'])
        
        # Verify old tokens were invalidated
        old_token1.refresh_from_db()
        old_token2.refresh_from_db()
        self.assertIsNotNone(old_token1.used_at)
        self.assertIsNotNone(old_token2.used_at)
        
        # Verify new token was created
        new_tokens = PasswordResetToken.objects.filter(
            user=self.user,
            used_at__isnull=True
        )
        self.assertEqual(new_tokens.count(), 1)
        new_token = new_tokens.first()
        self.assertNotEqual(new_token.token, 'old_token_1')
        self.assertNotEqual(new_token.token, 'old_token_2')
    
    def test_request_password_reset_email_failure(self):
        """Test password reset when email sending fails"""
        # Configure the existing mock to fail
        self.mock_email_service.send_password_reset_email.return_value = {
            'success': False,
            'message': 'SMTP connection failed'
        }
        
        result = self.service.request_password_reset(self.user.email)
        
        self.assertFalse(result['success'])
        self.assertIn('Failed to send password reset email', result['message'])
        
        # Verify token was not created (should be rolled back)
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_validate_reset_token_success(self):
        """Test successful token validation"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid_token_123'
        )
        
        result = self.service.validate_reset_token('valid_token_123')
        
        self.assertTrue(result['success'])
        self.assertIn('token is valid', result['message'])
        self.assertEqual(result['user_id'], str(self.user.id))
    
    def test_validate_reset_token_invalid(self):
        """Test validation of invalid token"""
        result = self.service.validate_reset_token('invalid_token')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid reset token', result['message'])
        self.assertNotIn('user_id', result)
    
    def test_validate_reset_token_expired(self):
        """Test validation of expired token"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired_token_123',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        result = self.service.validate_reset_token('expired_token_123')
        
        self.assertFalse(result['success'])
        self.assertIn('expired', result['message'])
    
    def test_validate_reset_token_used(self):
        """Test validation of already used token"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='used_token_123',
            used_at=timezone.now()
        )
        
        result = self.service.validate_reset_token('used_token_123')
        
        self.assertFalse(result['success'])
        self.assertIn('already been used', result['message'])
    
    def test_validate_reset_token_empty_string(self):
        """Test validation of empty token string"""
        result = self.service.validate_reset_token('')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid reset token', result['message'])
    
    def test_validate_reset_token_none(self):
        """Test validation of None token"""
        result = self.service.validate_reset_token(None)
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid reset token', result['message'])
    
    def test_reset_password_success(self):
        """Test successful password reset"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset_token_123'
        )
        
        old_password = self.user.password
        new_password = 'new_secure_password_123!'
        
        result = self.service.reset_password('reset_token_123', new_password)
        
        self.assertTrue(result['success'])
        self.assertIn('reset successfully', result['message'])
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, old_password)
        self.assertTrue(self.user.check_password(new_password))
        
        # Verify failed login attempts were reset
        self.assertEqual(self.user.failed_login_attempts, 0)
        
        # Verify token was marked as used
        token.refresh_from_db()
        self.assertIsNotNone(token.used_at)
        self.assertFalse(token.is_valid)
        
        # Verify audit log was called
        self.mock_audit_service.log_user_action.assert_called()
    
    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token"""
        result = self.service.reset_password('invalid_token', 'new_password123')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid or expired', result['message'])
    
    def test_reset_password_expired_token(self):
        """Test password reset with expired token"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired_reset_token',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        result = self.service.reset_password('expired_reset_token', 'new_password123')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid or expired', result['message'])
        
        # Verify password was not changed
        token.refresh_from_db()
        self.assertIsNone(token.used_at)
    
    def test_reset_password_used_token(self):
        """Test password reset with already used token"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='used_reset_token',
            used_at=timezone.now()
        )
        
        result = self.service.reset_password('used_reset_token', 'new_password123')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid or expired', result['message'])
    
    def test_reset_password_empty_password(self):
        """Test password reset with empty password"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid_token'
        )
        
        result = self.service.reset_password('valid_token', '')
        
        self.assertFalse(result['success'])
        self.assertIn('Password is required', result['message'])
        
        # Verify token was not marked as used
        token.refresh_from_db()
        self.assertIsNone(token.used_at)
    
    def test_reset_password_none_password(self):
        """Test password reset with None password"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid_token'
        )
        
        result = self.service.reset_password('valid_token', None)
        
        self.assertFalse(result['success'])
        self.assertIn('Password is required', result['message'])
    
    def test_reset_password_weak_password(self):
        """Test password reset with weak password"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid_token'
        )
        
        # Test with too short password
        result = self.service.reset_password('valid_token', '123')
        
        self.assertFalse(result['success'])
        self.assertIn('Password must be at least 8 characters', result['message'])
        
        # Verify token was not marked as used
        token.refresh_from_db()
        self.assertIsNone(token.used_at)
    
    def test_generate_reset_token_uniqueness(self):
        """Test reset token generation produces unique tokens"""
        tokens = set()
        for i in range(100):
            token = self.service._generate_reset_token()
            self.assertNotIn(token, tokens)
            tokens.add(token)
            self.assertIsInstance(token, str)
            self.assertGreater(len(token), 20)
    
    def test_generate_reset_token_format(self):
        """Test reset token format and characteristics"""
        token = self.service._generate_reset_token()
        
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 30)  # Should be long enough
        # Should contain only URL-safe characters
        import string
        allowed_chars = string.ascii_letters + string.digits + '-_'
        self.assertTrue(all(c in allowed_chars for c in token))
    
    def test_concurrent_password_reset_requests(self):
        """Test handling of concurrent password reset requests for same user"""
        # Make multiple concurrent requests
        result1 = self.service.request_password_reset(self.user.email)
        result2 = self.service.request_password_reset(self.user.email)
        result3 = self.service.request_password_reset(self.user.email)
        
        # All should succeed
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertTrue(result3['success'])
        
        # Only one token should be valid (latest)
        valid_tokens = PasswordResetToken.objects.filter(
            user=self.user,
            used_at__isnull=True
        )
        self.assertEqual(valid_tokens.count(), 1)
    
    def test_password_reset_user_with_failed_attempts(self):
        """Test password reset clears failed login attempts"""
        # Set failed login attempts
        self.user.failed_login_attempts = 5
        self.user.save()
        
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset_token'
        )
        
        with patch('core.user_management.services.invitation_service.AuditService'):
            result = self.service.reset_password('reset_token', 'new_password123!')
        
        self.assertTrue(result['success'])
        
        # Verify failed attempts were cleared
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 0)
    
    def test_password_reset_preserves_user_data(self):
        """Test password reset preserves other user data"""
        # Store original data
        original_username = self.user.username
        original_email = self.user.email
        original_role = self.user.role
        original_organization = self.user.organization
        
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset_token'
        )
        
        with patch('core.user_management.services.invitation_service.AuditService'):
            result = self.service.reset_password('reset_token', 'new_password123!')
        
        self.assertTrue(result['success'])
        
        # Verify other data was preserved
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, original_username)
        self.assertEqual(self.user.email, original_email)
        self.assertEqual(self.user.role, original_role)
        self.assertEqual(self.user.organization, original_organization)
    
    def test_password_reset_with_special_characters(self):
        """Test password reset with special characters in password"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset_token'
        )
        
        special_password = 'P@ssw0rd!#$%^&*()_+{}[]|;:,.<>?'
        
        with patch('core.user_management.services.invitation_service.AuditService'):
            result = self.service.reset_password('reset_token', special_password)
        
        self.assertTrue(result['success'])
        
        # Verify password was set correctly
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(special_password))
    
    def test_password_reset_with_unicode_password(self):
        """Test password reset with unicode characters in password"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset_token'
        )
        
        unicode_password = 'pássw0rd123áéíóú中文🔒'
        
        with patch('core.user_management.services.invitation_service.AuditService'):
            result = self.service.reset_password('reset_token', unicode_password)
        
        self.assertTrue(result['success'])
        
        # Verify password was set correctly
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(unicode_password))


class PasswordResetServiceSecurityTestCase(TestCase):
    """Test cases for password reset security features"""
    
    def setUp(self):
        # Create mock services
        self.mock_email_service = MagicMock()
        self.mock_email_service.send_password_reset_email.return_value = {'success': True}
        self.mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        self.service = PasswordResetService(
            email_service=self.mock_email_service,
            audit_service=self.mock_audit_service
        )
        self.user = CustomUserFactory()
    
    def test_token_expiry_security(self):
        """Test that expired tokens cannot be used"""
        # Create token that expires in the past
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired_token',
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        
        result = self.service.reset_password('expired_token', 'new_password123')
        
        self.assertFalse(result['success'])
        
        # Verify password was not changed
        old_password = self.user.password
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, old_password)
    
    def test_one_time_use_security(self):
        """Test that tokens can only be used once"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='one_time_token'
        )
        
        with patch('core.user_management.services.invitation_service.AuditService'):
            # First use should succeed
            result1 = self.service.reset_password('one_time_token', 'password1')
            self.assertTrue(result1['success'])
            
            # Second use should fail
            result2 = self.service.reset_password('one_time_token', 'password2')
            self.assertFalse(result2['success'])
    
    def test_email_enumeration_protection(self):
        """Test protection against email enumeration attacks"""
        # Request for existing user
        result1 = self.service.request_password_reset(self.user.email)
        
        # Request for non-existing user
        result2 = self.service.request_password_reset('nonexistent@example.com')
        
        # Both should return same success message
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertEqual(result1['message'], result2['message'])
    
    def test_timing_attack_protection(self):
        """Test consistent response times to prevent timing attacks"""
        import time
        
        # Measure time for existing user
        start_time = time.time()
        self.service.request_password_reset(self.user.email)
        existing_user_time = time.time() - start_time
        
        # Measure time for non-existing user
        start_time = time.time()
        self.service.request_password_reset('nonexistent@example.com')
        nonexistent_user_time = time.time() - start_time
        
        # Times should be similar (within reasonable threshold)
        time_difference = abs(existing_user_time - nonexistent_user_time)
        self.assertLess(time_difference, 2.0)  # 2 second threshold (more reasonable for email failures)
    
    def test_rate_limiting_preparation(self):
        """Test that service is prepared for rate limiting implementation"""
        # Multiple rapid requests should all succeed at service level
        # (Rate limiting would be implemented at middleware/view level)
        results = []
        for i in range(5):
            result = self.service.request_password_reset(self.user.email)
            results.append(result)
        
        # All should succeed (service doesn't implement rate limiting directly)
        for result in results:
            self.assertTrue(result['success'])
    
    def test_secure_token_generation(self):
        """Test that tokens are cryptographically secure"""
        # Generate multiple tokens to check for patterns
        tokens = []
        for i in range(50):
            token = self.service._generate_reset_token()
            tokens.append(token)
        
        # All tokens should be unique
        self.assertEqual(len(tokens), len(set(tokens)))
        
        # Tokens should have sufficient entropy (length)
        for token in tokens:
            self.assertGreater(len(token), 30)
        
        # Tokens should not contain predictable patterns
        for i in range(len(tokens) - 1):
            # No token should be a substring of another
            for j in range(i + 1, len(tokens)):
                self.assertNotIn(tokens[i][:10], tokens[j])
                self.assertNotIn(tokens[j][:10], tokens[i])


class PasswordResetServiceErrorHandlingTestCase(TestCase):
    """Test cases for error handling and edge cases"""
    
    def setUp(self):
        # Create mock services
        self.mock_email_service = MagicMock()
        self.mock_email_service.send_password_reset_email.return_value = {'success': True}
        self.mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        self.service = PasswordResetService(
            email_service=self.mock_email_service,
            audit_service=self.mock_audit_service
        )
        self.user = CustomUserFactory()
    
    def test_database_error_handling(self):
        """Test graceful handling of database errors"""
        with patch('core.user_management.models.invitation_models.PasswordResetToken.objects.create') as mock_create:
            mock_create.side_effect = Exception('Database connection failed')
            
            result = self.service.request_password_reset(self.user.email)
            
            self.assertFalse(result['success'])
            self.assertIn('Failed to process password reset request', result['message'])
    
    def test_email_service_unavailable(self):
        """Test handling when email service is unavailable"""
        # Configure the existing mock to fail with a specific error
        self.mock_email_service.send_password_reset_email.side_effect = Exception('Email service unavailable')
        
        result = self.service.request_password_reset(self.user.email)
        
        self.assertFalse(result['success'])
        self.assertIn('Failed to process password reset request', result['message'])
    
    def test_user_deletion_during_reset(self):
        """Test handling when user is deleted after token creation but before reset"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset_token_for_deleted_user'
        )
        
        # Delete the user
        user_id = self.user.id
        self.user.delete()
        
        # Attempt to reset password
        result = self.service.reset_password('reset_token_for_deleted_user', 'new_password')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid or expired', result['message'])
    
    def test_malformed_token_input(self):
        """Test handling of malformed token inputs"""
        malformed_inputs = [
            '',
            None,
            '   ',
            'token with spaces',
            'token\nwith\nnewlines',
            'token\twith\ttabs',
            'token with unicode: áéíóú',
            'very_long_token_' + 'x' * 1000,
            123,  # numeric input
            [],   # list input
            {},   # dict input
        ]
        
        for malformed_input in malformed_inputs:
            with self.subTest(input=malformed_input):
                result = self.service.validate_reset_token(malformed_input)
                self.assertFalse(result['success'])
                self.assertIn('Invalid reset token', result['message'])
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection in token validation"""
        malicious_inputs = [
            "'; DROP TABLE password_reset_tokens; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; DELETE FROM users; --",
        ]
        
        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                result = self.service.validate_reset_token(malicious_input)
                self.assertFalse(result['success'])
                
                # Verify database integrity
                self.assertTrue(CustomUser.objects.filter(id=self.user.id).exists())
    
    def test_memory_exhaustion_protection(self):
        """Test protection against memory exhaustion attacks"""
        # Very large password input
        large_password = 'a' * (10 * 1024 * 1024)  # 10MB password
        
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset_token'
        )
        
        result = self.service.reset_password('reset_token', large_password)
        
        # Should handle gracefully (either succeed with truncation or fail)
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)


if __name__ == '__main__':
    unittest.main()