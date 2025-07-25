"""
Comprehensive integration tests for Email Workflows
Tests end-to-end email notification workflows across all components
"""
import unittest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from core.user_management.models.invitation_models import UserInvitation, PasswordResetToken
from core.user_management.models.user_models import CustomUser, Organization
from core.user_management.services.invitation_service import UserInvitationService, PasswordResetService
from core.notifications.services.gmail_smtp_service import GmailSMTPService
from core.tests.factories import CustomUserFactory, OrganizationFactory
import uuid


class EmailWorkflowIntegrationTestCase(TransactionTestCase):
    """Integration tests for complete email workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = OrganizationFactory()
        self.publisher = CustomUserFactory(role='publisher', organization=self.organization)
        self.admin = CustomUserFactory(role='BlueVisionAdmin')
        self.user = CustomUserFactory()
    
    def test_complete_user_invitation_workflow(self):
        """Test complete user invitation workflow with email integration"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitee_email = 'newuser@example.com'
        
        # Step 1: Send invitation
        result = invitation_service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=invitee_email,
            role='viewer',
            message='Welcome to our threat intelligence sharing platform!'
        )
        
        # Verify invitation was created and email sent
        self.assertTrue(result['success'])
        self.assertIn('sent successfully', result['message'])
        
        # Verify database state
        invitation = UserInvitation.objects.get(email=invitee_email)
        self.assertEqual(invitation.status, 'pending')
        self.assertEqual(invitation.organization, self.organization)
        self.assertEqual(invitation.inviter, self.publisher)
        
        # Verify email was sent
        mock_email_service.send_user_invitation_email.assert_called_once()
        
        # Verify audit logging
        mock_audit_service.log_user_action.assert_called()
        
        # Step 2: Accept invitation
        new_user = CustomUserFactory(email=invitee_email)
        accept_result = invitation_service.accept_invitation(invitation.token, new_user)
        
        # Verify acceptance
        self.assertTrue(accept_result['success'])
        self.assertIn('Successfully joined', accept_result['message'])
        
        # Verify database updates
        invitation.refresh_from_db()
        new_user.refresh_from_db()
        
        self.assertEqual(invitation.status, 'accepted')
        self.assertEqual(invitation.accepted_by, new_user)
        self.assertIsNotNone(invitation.accepted_at)
        self.assertEqual(new_user.organization, self.organization)
        self.assertEqual(new_user.role, 'viewer')
    
    def test_complete_password_reset_workflow(self):
        """Test complete password reset workflow with email integration"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_password_reset_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        password_service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        original_password = self.user.password
        
        # Step 1: Request password reset
        result = password_service.request_password_reset(
            email=self.user.email,
            ip_address='192.168.1.100',
            user_agent='Test Browser/1.0'
        )
        
        # Verify request was processed and email sent
        self.assertTrue(result['success'])
        self.assertIn('password reset instructions have been sent', result['message'])
        
        # Verify database state
        token = PasswordResetToken.objects.get(user=self.user)
        self.assertIsNotNone(token.token)
        self.assertEqual(token.ip_address, '192.168.1.100')
        self.assertEqual(token.user_agent, 'Test Browser/1.0')
        self.assertTrue(token.is_valid)
        
        # Verify email was sent
        mock_email_service.send_password_reset_email.assert_called_once()
        
        # Step 2: Validate token
        validate_result = password_service.validate_reset_token(token.token)
        
        self.assertTrue(validate_result['success'])
        self.assertIn('token is valid', validate_result['message'])
        self.assertEqual(validate_result['user_id'], str(self.user.id))
        
        # Step 3: Reset password
        new_password = 'new_secure_password_123!'
        reset_result = password_service.reset_password(token.token, new_password)
        
        # Verify password was reset
        self.assertTrue(reset_result['success'])
        self.assertIn('reset successfully', reset_result['message'])
        
        # Verify database updates
        self.user.refresh_from_db()
        token.refresh_from_db()
        
        self.assertNotEqual(self.user.password, original_password)
        self.assertTrue(self.user.check_password(new_password))
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertFalse(token.is_valid)
        self.assertIsNotNone(token.used_at)
        
        # Verify audit logging
        mock_audit_service.log_user_action.assert_called()
    
    def test_multiple_concurrent_invitations_workflow(self):
        """Test handling of multiple concurrent invitation workflows"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitees = [
            'user1@example.com',
            'user2@example.com',
            'user3@example.com'
        ]
        
        results = []
        
        # Send multiple invitations concurrently
        for email in invitees:
            result = invitation_service.send_invitation(
                inviter=self.publisher,
                organization=self.organization,
                email=email,
                role='viewer'
            )
            results.append(result)
        
        # Verify all invitations were successful
        for result in results:
            self.assertTrue(result['success'])
        
        # Verify all invitations were created
        for email in invitees:
            invitation = UserInvitation.objects.get(email=email)
            self.assertEqual(invitation.status, 'pending')
            self.assertEqual(invitation.organization, self.organization)
        
        # Verify emails were sent for each invitation
        self.assertEqual(mock_email_service.send_user_invitation_email.call_count, 3)
    
    def test_invitation_expiry_and_renewal_workflow(self):
        """Test invitation expiry and renewal workflow"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitee_email = 'expiry_test@example.com'
        
        # Step 1: Send initial invitation
        result1 = invitation_service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=invitee_email,
            role='viewer'
        )
        
        self.assertTrue(result1['success'])
        
        # Get the invitation and manually expire it
        invitation = UserInvitation.objects.get(email=invitee_email)
        invitation.expires_at = timezone.now() - timedelta(days=1)
        invitation.save()
        
        # Step 2: Send new invitation (should replace expired one)
        result2 = invitation_service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=invitee_email,
            role='publisher'  # Different role
        )
            
        self.assertTrue(result2['success'])
        
        # Verify old invitation was cancelled and new one created
        old_invitation = UserInvitation.objects.get(id=invitation.id)
        self.assertEqual(old_invitation.status, 'cancelled')
        
        new_invitation = UserInvitation.objects.filter(
            email=invitee_email,
            status='pending'
        ).first()
        self.assertIsNotNone(new_invitation)
        self.assertEqual(new_invitation.invited_role, 'publisher')
        self.assertNotEqual(new_invitation.id, invitation.id)
    
    def test_email_failure_rollback_workflow(self):
        """Test that database transactions are rolled back on email failures"""
        # Create mocks - setup email to fail
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.side_effect = Exception('Email service failed')
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitee_email = 'rollback_test@example.com'
        
        # Attempt to send invitation
        result = invitation_service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=invitee_email,
            role='viewer'
        )
        
        # Verify operation failed
        self.assertFalse(result['success'])
        self.assertIn('Failed to send invitation', result['message'])
        
        # Verify no invitation was created (rollback occurred)
        invitation_count = UserInvitation.objects.filter(email=invitee_email).count()
        self.assertEqual(invitation_count, 0)
    
    def test_account_locked_email_workflow(self):
        """Test account locked email workflow integration"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_account_locked_email.return_value = {'success': True}
        
        # Simulate account being locked
        self.user.failed_login_attempts = 5
        self.user.save()
        
        # Send account locked email
        result = mock_email_service.send_account_locked_email(self.user)
        
        # Verify email was sent
        self.assertTrue(result['success'])
        mock_email_service.send_account_locked_email.assert_called_once_with(self.user)
    
    def test_feed_subscription_confirmation_workflow(self):
        """Test feed subscription confirmation email workflow"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_feed_subscription_confirmation.return_value = {'success': True}
        
        feed_name = 'Critical Infrastructure Threats'
        
        # Send subscription confirmation email
        result = mock_email_service.send_feed_subscription_confirmation(self.user, feed_name)
        
        # Verify email was sent
        self.assertTrue(result['success'])
        mock_email_service.send_feed_subscription_confirmation.assert_called_once_with(self.user, feed_name)
    
    def test_cross_organization_invitation_workflow(self):
        """Test invitation workflow across different organizations"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Create second organization
        other_organization = OrganizationFactory()
        
        invitee_email = 'cross_org@example.com'
        
        # Admin can invite to any organization
        result = invitation_service.send_invitation(
            inviter=self.admin,
            organization=other_organization,
            email=invitee_email,
            role='publisher'
        )
            
        self.assertTrue(result['success'])
        
        # Verify invitation was created for correct organization
        invitation = UserInvitation.objects.get(email=invitee_email)
        self.assertEqual(invitation.organization, other_organization)
        self.assertEqual(invitation.inviter, self.admin)
        
        # Accept invitation
        new_user = CustomUserFactory(email=invitee_email)
        accept_result = invitation_service.accept_invitation(invitation.token, new_user)
        
        self.assertTrue(accept_result['success'])
        
        # Verify user joined correct organization
        new_user.refresh_from_db()
        self.assertEqual(new_user.organization, other_organization)
    
    def test_invitation_cancellation_workflow(self):
        """Test invitation cancellation workflow"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitee_email = 'cancel_test@example.com'
        
        # Send invitation
        send_result = invitation_service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=invitee_email,
            role='viewer'
        )
            
        self.assertTrue(send_result['success'])
        
        # Get invitation
        invitation = UserInvitation.objects.get(email=invitee_email)
        self.assertEqual(invitation.status, 'pending')
        
        # Cancel invitation
        cancel_result = invitation_service.cancel_invitation(
            str(invitation.id), 
            self.publisher
        )
            
        self.assertTrue(cancel_result['success'])
        self.assertIn('cancelled successfully', cancel_result['message'])
        
        # Verify invitation was cancelled
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'cancelled')
        
        # Attempt to accept cancelled invitation should fail
        new_user = CustomUserFactory(email=invitee_email)
        accept_result = invitation_service.accept_invitation(invitation.token, new_user)
        
        self.assertFalse(accept_result['success'])
    
    def test_email_template_personalization_workflow(self):
        """Test that email templates are properly personalized"""
        # Test with user having full name
        user_with_name = CustomUserFactory(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com'
        )
        
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_password_reset_email.return_value = {'success': True}
        
        # Send password reset email
        result = mock_email_service.send_password_reset_email(user_with_name, 'test_token')
        
        # Verify email service was called with correct parameters
        self.assertTrue(result['success'])
        mock_email_service.send_password_reset_email.assert_called_once_with(user_with_name, 'test_token')
    
    def test_bulk_email_workflow_performance(self):
        """Test performance of bulk email operations"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        import time
        
        # Create multiple users for bulk operations
        users = []
        for i in range(10):
            user = CustomUserFactory(email=f'bulk{i}@example.com')
            users.append(user)
        
        start_time = time.time()
        
        # Send bulk invitations
        for user in users:
            result = invitation_service.send_invitation(
                inviter=self.publisher,
                organization=self.organization,
                email=user.email,
                role='viewer'
            )
            self.assertTrue(result['success'])
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify reasonable performance (should complete within reasonable time)
        self.assertLess(execution_time, 5.0)  # 5 seconds for 10 operations
        
        # Verify all emails were sent
        self.assertEqual(mock_email_service.send_user_invitation_email.call_count, 10)
    
    def test_email_workflow_data_consistency(self):
        """Test data consistency across email workflows"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Perform multiple operations in sequence
        invitee_email = 'consistency@example.com'
        
        # Send invitation
        send_result = invitation_service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=invitee_email,
            role='viewer'
        )
        self.assertTrue(send_result['success'])
        
        # Check database state
        invitation = UserInvitation.objects.get(email=invitee_email)
        self.assertEqual(invitation.status, 'pending')
        
        # Accept invitation
        new_user = CustomUserFactory(email=invitee_email)
        accept_result = invitation_service.accept_invitation(invitation.token, new_user)
        self.assertTrue(accept_result['success'])
        
        # Verify final consistent state
        invitation.refresh_from_db()
        new_user.refresh_from_db()
        
        self.assertEqual(invitation.status, 'accepted')
        self.assertEqual(invitation.accepted_by, new_user)
        self.assertEqual(new_user.organization, self.organization)
        self.assertEqual(new_user.role, 'viewer')
        
        # Verify no orphaned records
        all_invitations = UserInvitation.objects.filter(email=invitee_email)
        self.assertEqual(all_invitations.count(), 1)


class EmailWorkflowErrorHandlingTestCase(TestCase):
    """Test error handling in email workflows"""
    
    def setUp(self):
        self.organization = OrganizationFactory()
        self.publisher = CustomUserFactory(role='publisher', organization=self.organization)
    
    def test_graceful_email_service_failure_handling(self):
        """Test graceful handling of email service failures"""
        # Create mocks - simulate email service completely failing
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.side_effect = Exception('Email service unavailable')
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = invitation_service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email='test@example.com',
            role='viewer'
        )
        
        # Should fail gracefully
        self.assertFalse(result['success'])
        self.assertIn('Failed to send invitation', result['message'])
        
        # No invitation should be created
        self.assertEqual(UserInvitation.objects.count(), 0)
    
    def test_partial_failure_recovery_workflow(self):
        """Test recovery from partial failures in workflows"""
        # Create mocks for first attempt (fails)
        mock_email_service_fail = MagicMock()
        mock_email_service_fail.send_user_invitation_email.side_effect = Exception('Temporary failure')
        mock_audit_service = MagicMock()
        
        # Create service with failing email service
        invitation_service_fail = UserInvitationService(
            email_service=mock_email_service_fail,
            audit_service=mock_audit_service
        )
        
        result1 = invitation_service_fail.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email='recovery@example.com',
            role='viewer'
        )
        
        self.assertFalse(result1['success'])
        
        # Create mocks for second attempt (succeeds)
        mock_email_service_success = MagicMock()
        mock_email_service_success.send_user_invitation_email.return_value = {'success': True}
        
        # Create service with working email service
        invitation_service_success = UserInvitationService(
            email_service=mock_email_service_success,
            audit_service=mock_audit_service
        )
        
        result2 = invitation_service_success.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email='recovery@example.com',
            role='viewer'
        )
        
        self.assertTrue(result2['success'])
        
        # Verify only one invitation exists
        invitations = UserInvitation.objects.filter(email='recovery@example.com')
        self.assertEqual(invitations.count(), 1)
    
    def test_database_integrity_on_workflow_failures(self):
        """Test database integrity is maintained on workflow failures"""
        # Create mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        with patch('core.user_management.models.invitation_models.UserInvitation.save') as mock_save:
            # Simulate database error during save
            mock_save.side_effect = Exception('Database integrity error')
            
            result = invitation_service.send_invitation(
                inviter=self.publisher,
                organization=self.organization,
                email='integrity@example.com',
                role='viewer'
            )
            
            # Should fail
            self.assertFalse(result['success'])
            
            # Database should remain clean
            self.assertEqual(UserInvitation.objects.count(), 0)


if __name__ == '__main__':
    unittest.main()