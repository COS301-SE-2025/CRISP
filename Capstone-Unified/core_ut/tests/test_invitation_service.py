"""
Comprehensive unit tests for User Invitation Service
Tests all service methods, email integration, and business logic
"""
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from core.user_management.services.invitation_service import UserInvitationService, PasswordResetService
from core.user_management.models.invitation_models import UserInvitation, PasswordResetToken
from core.user_management.models.user_models import CustomUser, Organization
from core.tests.factories import CustomUserFactory, OrganizationFactory, CustomUserWithoutOrgFactory
import secrets


class UserInvitationServiceTestCase(TestCase):
    """Test cases for UserInvitationService"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = OrganizationFactory()
        self.publisher = CustomUserFactory(role='publisher', organization=self.organization)
        self.admin = CustomUserFactory(role='BlueVisionAdmin')
        self.viewer = CustomUserFactory(role='viewer', organization=self.organization)
        self.invitee_email = 'newuser@example.com'
    
    def test_send_invitation_success_publisher(self):
        """Test successful invitation sending by publisher"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Call service
        result = service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=self.invitee_email,
            role='viewer',
            message='Welcome to our team!'
        )
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIn('sent successfully', result['message'])
        self.assertIn('invitation_id', result)
        self.assertIn('expires_at', result)
        
        # Verify invitation was created
        invitation = UserInvitation.objects.get(email=self.invitee_email)
        self.assertEqual(invitation.organization, self.organization)
        self.assertEqual(invitation.inviter, self.publisher)
        self.assertEqual(invitation.invited_role, 'viewer')
        self.assertEqual(invitation.message, 'Welcome to our team!')
        self.assertEqual(invitation.status, 'pending')
        
        # Verify email was sent
        mock_email_service.send_user_invitation_email.assert_called_once()
        
        # Verify audit log
        mock_audit_service.log_user_action.assert_called()
    
    def test_send_invitation_success_admin(self):
        """Test successful invitation sending by BlueVision admin"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.send_invitation(
            inviter=self.admin,
            organization=self.organization,
            email=self.invitee_email,
            role='publisher'
        )
        
        self.assertTrue(result['success'])
        
        # Verify invitation was created with publisher role
        invitation = UserInvitation.objects.get(email=self.invitee_email)
        self.assertEqual(invitation.invited_role, 'publisher')
    
    def test_send_invitation_no_permission_viewer(self):
        """Test invitation sending fails for viewer"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.send_invitation(
            inviter=self.viewer,
            organization=self.organization,
            email=self.invitee_email
        )
        
        self.assertFalse(result['success'])
        self.assertIn('do not have permission', result['message'])
        
        # Verify no invitation was created
        self.assertEqual(UserInvitation.objects.count(), 0)
    
    def test_send_invitation_user_already_exists(self):
        """Test invitation fails when user already exists in organization"""
        existing_user = CustomUserFactory(
            email=self.invitee_email,
            organization=self.organization
        )
        
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=self.invitee_email
        )
        
        self.assertFalse(result['success'])
        self.assertIn('already a member', result['message'])
    
    def test_send_invitation_duplicate_pending(self):
        """Test invitation fails when pending invitation already exists"""
        UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='existing_token',
            status='pending'
        )
        
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=self.invitee_email
        )
        
        self.assertFalse(result['success'])
        self.assertIn('pending invitation already exists', result['message'])
    
    def test_send_invitation_replace_expired(self):
        """Test invitation replaces expired invitation"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {'success': True}
        
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Create expired invitation
        expired_invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='expired_token',
            status='pending',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        result = service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=self.invitee_email
        )
        
        self.assertTrue(result['success'])
        
        # Verify expired invitation was cancelled
        expired_invitation.refresh_from_db()
        self.assertEqual(expired_invitation.status, 'cancelled')
        
        # Verify new invitation was created
        new_invitation = UserInvitation.objects.filter(
            email=self.invitee_email,
            status='pending'
        ).first()
        self.assertIsNotNone(new_invitation)
        self.assertNotEqual(new_invitation.id, expired_invitation.id)
    
    def test_send_invitation_email_failure(self):
        """Test invitation fails when email sending fails"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_email_service.send_user_invitation_email.return_value = {
            'success': False, 
            'message': 'SMTP error'
        }
        
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.send_invitation(
            inviter=self.publisher,
            organization=self.organization,
            email=self.invitee_email
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Failed to send invitation email', result['message'])
        
        # Verify no invitation was created (transaction rollback)
        self.assertEqual(UserInvitation.objects.count(), 0)
    
    def test_accept_invitation_success(self):
        """Test successful invitation acceptance"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Create user with matching email
        accepter = CustomUserWithoutOrgFactory(email=self.invitee_email)
        
        # Create invitation
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            invited_role='viewer',
            token='accept_token'
        )
        
        result = service.accept_invitation('accept_token', accepter)
        
        self.assertTrue(result['success'])
        self.assertIn('Successfully joined', result['message'])
        self.assertIn('organization', result)
        
        # Verify invitation was accepted
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'accepted')
        self.assertEqual(invitation.accepted_by, accepter)
        self.assertIsNotNone(invitation.accepted_at)
        
        # Verify user was added to organization
        accepter.refresh_from_db()
        self.assertEqual(accepter.organization, self.organization)
        self.assertEqual(accepter.role, 'viewer')
    
    def test_accept_invitation_invalid_token(self):
        """Test invitation acceptance with invalid token"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        accepter = CustomUserFactory()
        
        result = service.accept_invitation('invalid_token', accepter)
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid invitation token', result['message'])
    
    def test_accept_invitation_expired(self):
        """Test invitation acceptance when expired"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        accepter = CustomUserWithoutOrgFactory(email=self.invitee_email)
        
        # Create expired invitation
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='expired_token',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        result = service.accept_invitation('expired_token', accepter)
        
        self.assertFalse(result['success'])
        self.assertIn('expired', result['message'])
    
    def test_accept_invitation_already_accepted(self):
        """Test invitation acceptance when already accepted"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        accepter = CustomUserWithoutOrgFactory(email=self.invitee_email)
        other_user = CustomUserFactory()
        
        # Create accepted invitation
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='accepted_token',
            status='accepted',
            accepted_by=other_user
        )
        
        result = service.accept_invitation('accepted_token', accepter)
        
        self.assertFalse(result['success'])
        self.assertIn('already been accepted', result['message'])
    
    def test_accept_invitation_email_mismatch(self):
        """Test invitation acceptance with email mismatch"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        accepter = CustomUserFactory(email='different@example.com')
        
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='mismatch_token'
        )
        
        result = service.accept_invitation('mismatch_token', accepter)
        
        self.assertFalse(result['success'])
        self.assertIn('email address does not match', result['message'])
    
    def test_accept_invitation_user_already_in_org(self):
        """Test invitation acceptance when user already in another organization"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        other_org = OrganizationFactory()
        accepter = CustomUserFactory(email=self.invitee_email, organization=other_org)
        
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='conflict_token'
        )
        
        result = service.accept_invitation('conflict_token', accepter)
        
        self.assertFalse(result['success'])
        self.assertIn('already a member of another organization', result['message'])
    
    def test_list_invitations_success(self):
        """Test successful invitation listing"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Create multiple invitations
        invitation1 = UserInvitation.objects.create(
            email='user1@example.com',
            organization=self.organization,
            inviter=self.publisher,
            token='token1',
            status='pending'
        )
        
        invitation2 = UserInvitation.objects.create(
            email='user2@example.com',
            organization=self.organization,
            inviter=self.publisher,
            token='token2',
            status='accepted'
        )
        
        invitation3 = UserInvitation.objects.create(
            email='user3@example.com',
            organization=self.organization,
            inviter=self.publisher,
            token='token3',
            status='expired'
        )
        
        # Test listing all invitations
        invitations = service.list_invitations(self.organization)
        
        self.assertEqual(len(invitations), 3)
        
        # Test filtering by status
        pending_invitations = service.list_invitations(self.organization, 'pending')
        self.assertEqual(len(pending_invitations), 1)
        self.assertEqual(pending_invitations[0]['email'], 'user1@example.com')
    
    def test_list_invitations_auto_expire(self):
        """Test that expired invitations are automatically updated"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Create invitation that should be expired
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='auto_expire_token',
            status='pending',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        invitations = service.list_invitations(self.organization)
        
        # Verify invitation was auto-expired
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'expired')
    
    def test_cancel_invitation_success_by_inviter(self):
        """Test successful invitation cancellation by inviter"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='cancel_token'
        )
        
        result = service.cancel_invitation(str(invitation.id), self.publisher)
        
        self.assertTrue(result['success'])
        self.assertIn('cancelled successfully', result['message'])
        
        # Verify invitation was cancelled
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'cancelled')
    
    def test_cancel_invitation_success_by_admin(self):
        """Test successful invitation cancellation by admin"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='cancel_admin_token'
        )
        
        result = service.cancel_invitation(str(invitation.id), self.admin)
        
        self.assertTrue(result['success'])
    
    def test_cancel_invitation_no_permission(self):
        """Test invitation cancellation without permission"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='no_permission_token'
        )
        
        result = service.cancel_invitation(str(invitation.id), self.viewer)
        
        self.assertFalse(result['success'])
        self.assertIn('do not have permission', result['message'])
    
    def test_cancel_invitation_not_found(self):
        """Test cancellation of non-existent invitation"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        fake_id = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        
        result = service.cancel_invitation(fake_id, self.publisher)
        
        self.assertFalse(result['success'])
        self.assertIn('not found', result['message'])
    
    def test_cancel_invitation_not_pending(self):
        """Test cancellation of non-pending invitation"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.publisher,
            token='accepted_token',
            status='accepted'
        )
        
        result = service.cancel_invitation(str(invitation.id), self.publisher)
        
        self.assertFalse(result['success'])
        self.assertIn('Only pending invitations can be cancelled', result['message'])
    
    def test_can_invite_users_permissions(self):
        """Test _can_invite_users permission checking"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Test BlueVision admin can invite to any organization
        self.assertTrue(service._can_invite_users(self.admin, self.organization))
        
        # Test publisher can invite to their own organization
        self.assertTrue(service._can_invite_users(self.publisher, self.organization))
        
        # Test publisher cannot invite to other organization
        other_org = OrganizationFactory()
        self.assertFalse(service._can_invite_users(self.publisher, other_org))
        
        # Test viewer cannot invite
        self.assertFalse(service._can_invite_users(self.viewer, self.organization))
    
    def test_user_exists_in_organization(self):
        """Test _user_exists_in_organization checking"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        existing_user = CustomUserFactory(
            email='existing@example.com',
            organization=self.organization
        )
        
        # Test existing user detection
        self.assertTrue(service._user_exists_in_organization(
            'existing@example.com', self.organization
        ))
        
        # Test case insensitive check
        self.assertTrue(service._user_exists_in_organization(
            'EXISTING@EXAMPLE.COM', self.organization
        ))
        
        # Test non-existing user
        self.assertFalse(service._user_exists_in_organization(
            'nonexistent@example.com', self.organization
        ))
    
    def test_generate_invitation_token(self):
        """Test invitation token generation"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        token = service._generate_invitation_token()
        
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)  # Should be sufficiently long
        
        # Test uniqueness
        token2 = service._generate_invitation_token()
        self.assertNotEqual(token, token2)


class PasswordResetServiceTestCase(TestCase):
    """Test cases for PasswordResetService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUserFactory()
        self.test_ip = '192.168.1.100'
        self.test_user_agent = 'Test Browser'
    
    def test_request_password_reset_success(self):
        """Test successful password reset request"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_email_service.send_password_reset_email.return_value = {'success': True}
        
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.request_password_reset(
            email=self.user.email,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        self.assertTrue(result['success'])
        self.assertIn('password reset instructions have been sent', result['message'])
        
        # Verify token was created
        token = PasswordResetToken.objects.get(user=self.user)
        self.assertEqual(token.ip_address, self.test_ip)
        self.assertEqual(token.user_agent, self.test_user_agent)
        
        # Verify email was sent
        mock_email_service.send_password_reset_email.assert_called_once()
        
        # Verify audit log
        mock_audit_service.log_user_action.assert_called()
    
    def test_request_password_reset_nonexistent_user(self):
        """Test password reset request for non-existent user"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.request_password_reset('nonexistent@example.com')
        
        # Should return success to prevent email enumeration
        self.assertTrue(result['success'])
        self.assertIn('password reset instructions have been sent', result['message'])
        
        # Verify no token was created
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_request_password_reset_inactive_user(self):
        """Test password reset request for inactive user"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        inactive_user = CustomUserFactory(is_active=False)
        
        result = service.request_password_reset(inactive_user.email)
        
        # Should return success to prevent user enumeration
        self.assertTrue(result['success'])
        
        # Verify no token was created
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_request_password_reset_invalidates_old_tokens(self):
        """Test that new reset request invalidates old tokens"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_email_service.send_password_reset_email.return_value = {'success': True}
        
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        # Create old token
        old_token = PasswordResetToken.objects.create(
            user=self.user,
            token='old_token'
        )
        
        # Request new reset
        result = service.request_password_reset(self.user.email)
        
        self.assertTrue(result['success'])
        
        # Verify old token was invalidated
        old_token.refresh_from_db()
        self.assertIsNotNone(old_token.used_at)
        
        # Verify new token was created
        new_tokens = PasswordResetToken.objects.filter(
            user=self.user,
            used_at__isnull=True
        )
        self.assertEqual(new_tokens.count(), 1)
    
    def test_request_password_reset_email_failure(self):
        """Test password reset when email sending fails"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_email_service.send_password_reset_email.return_value = {
            'success': False,
            'message': 'SMTP error'
        }
        
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.request_password_reset(self.user.email)
        
        self.assertFalse(result['success'])
        self.assertIn('Failed to send password reset email', result['message'])
        
        # Verify token was not created (transaction rollback)
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_validate_reset_token_success(self):
        """Test successful token validation"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid_token'
        )
        
        result = service.validate_reset_token('valid_token')
        
        self.assertTrue(result['success'])
        self.assertIn('token is valid', result['message'])
        self.assertEqual(result['user_id'], str(self.user.id))
    
    def test_validate_reset_token_invalid(self):
        """Test validation of invalid token"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.validate_reset_token('invalid_token')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid reset token', result['message'])
    
    def test_validate_reset_token_expired(self):
        """Test validation of expired token"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired_token',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        result = service.validate_reset_token('expired_token')
        
        self.assertFalse(result['success'])
        self.assertIn('expired', result['message'])
    
    def test_validate_reset_token_used(self):
        """Test validation of used token"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='used_token',
            used_at=timezone.now()
        )
        
        result = service.validate_reset_token('used_token')
        
        self.assertFalse(result['success'])
        self.assertIn('already been used', result['message'])
    
    def test_reset_password_success(self):
        """Test successful password reset"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset_token'
        )
        
        old_password = self.user.password
        new_password = 'new_secure_password_123'
        
        result = service.reset_password('reset_token', new_password)
        
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
        
        # Verify audit log
        mock_audit_service.log_user_action.assert_called()
    
    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = service.reset_password('invalid_token', 'new_password')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid or expired', result['message'])
    
    def test_reset_password_expired_token(self):
        """Test password reset with expired token"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired_reset_token',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        result = service.reset_password('expired_reset_token', 'new_password')
        
        self.assertFalse(result['success'])
        self.assertIn('Invalid or expired', result['message'])
    
    def test_generate_reset_token(self):
        """Test reset token generation"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        token = service._generate_reset_token()
        
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)  # Should be sufficiently long
        
        # Test uniqueness
        token2 = service._generate_reset_token()
        self.assertNotEqual(token, token2)


class ServiceErrorHandlingTestCase(TestCase):
    """Test cases for service error handling and edge cases"""
    
    def setUp(self):
        self.organization = OrganizationFactory()
        self.user = CustomUserFactory()
    
    def test_invitation_service_database_error(self):
        """Test invitation service handles database errors gracefully"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        with patch('core.user_management.models.invitation_models.UserInvitation.objects.create') as mock_create:
            mock_create.side_effect = Exception('Database error')
            
            result = invitation_service.send_invitation(
                inviter=CustomUserFactory(role='BlueVisionAdmin'),
                organization=self.organization,
                email='test@example.com'
            )
            
            self.assertFalse(result['success'])
            self.assertIn('Failed to send invitation', result['message'])
    
    def test_password_service_database_error(self):
        """Test password service handles database errors gracefully"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        password_service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        with patch('core.user_management.models.invitation_models.PasswordResetToken.objects.create') as mock_create:
            mock_create.side_effect = Exception('Database error')
            
            result = password_service.request_password_reset(self.user.email)
            
            self.assertFalse(result['success'])
            self.assertIn('Failed to process password reset request', result['message'])
    
    def test_invitation_service_with_none_values(self):
        """Test invitation service handles None values gracefully"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = invitation_service.send_invitation(
            inviter=None,
            organization=self.organization,
            email='test@example.com'
        )
        
        self.assertFalse(result['success'])
    
    def test_password_service_with_empty_values(self):
        """Test password service handles empty values gracefully"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        password_service = PasswordResetService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        result = password_service.request_password_reset('')
        
        self.assertTrue(result['success'])  # Should still return success for security
    
    def test_concurrent_invitation_creation(self):
        """Test handling of concurrent invitation creation attempts"""
        # Setup mocks
        mock_email_service = MagicMock()
        mock_audit_service = MagicMock()
        
        # Create service with mocked dependencies
        invitation_service = UserInvitationService(
            email_service=mock_email_service,
            audit_service=mock_audit_service
        )
        
        publisher = CustomUserFactory(role='publisher', organization=self.organization)
        
        # Simulate concurrent creation by creating one invitation first
        UserInvitation.objects.create(
            email='concurrent@example.com',
            organization=self.organization,
            inviter=publisher,
            token='concurrent_token',
            status='pending'
        )
        
        # Second attempt should fail
        result = invitation_service.send_invitation(
            inviter=publisher,
            organization=self.organization,
            email='concurrent@example.com'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('pending invitation already exists', result['message'])


if __name__ == '__main__':
    unittest.main()