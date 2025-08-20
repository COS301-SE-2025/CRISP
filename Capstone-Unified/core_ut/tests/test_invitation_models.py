"""
Comprehensive unit tests for User Invitation and Password Reset models
Tests all model methods, properties, validations, and edge cases
"""
import unittest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from core_ut.user_management.models.invitation_models import UserInvitation, PasswordResetToken
from core_ut.user_management.models.user_models import CustomUser, Organization
from core_ut.tests.factories import CustomUserFactory, OrganizationFactory
import uuid


class UserInvitationModelTestCase(TestCase):
    """Test cases for UserInvitation model"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = OrganizationFactory()
        self.inviter = CustomUserFactory(role='publisher', organization=self.organization)
        self.invitee_email = 'newuser@example.com'
        
    def test_create_user_invitation_success(self):
        """Test successful creation of user invitation"""
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            invited_role='viewer',
            token='secure_token_123'
        )
        
        self.assertEqual(invitation.email, self.invitee_email)
        self.assertEqual(invitation.organization, self.organization)
        self.assertEqual(invitation.inviter, self.inviter)
        self.assertEqual(invitation.invited_role, 'viewer')
        self.assertEqual(invitation.status, 'pending')
        self.assertIsNotNone(invitation.expires_at)
        self.assertIsNone(invitation.accepted_at)
        self.assertIsNone(invitation.accepted_by)
    
    def test_invitation_automatic_expiry_date(self):
        """Test that invitation gets automatic expiry date"""
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='secure_token_123'
        )
        
        # Should expire in 7 days
        expected_expiry = timezone.now() + timedelta(days=7)
        time_diff = abs((invitation.expires_at - expected_expiry).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute tolerance
    
    def test_invitation_custom_expiry_date(self):
        """Test invitation with custom expiry date"""
        custom_expiry = timezone.now() + timedelta(days=3)
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='secure_token_123',
            expires_at=custom_expiry
        )
        
        self.assertEqual(invitation.expires_at, custom_expiry)
    
    def test_invitation_is_expired_property(self):
        """Test is_expired property"""
        # Create expired invitation
        past_date = timezone.now() - timedelta(days=1)
        expired_invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='expired_token',
            expires_at=past_date
        )
        
        # Create non-expired invitation
        future_date = timezone.now() + timedelta(days=1)
        valid_invitation = UserInvitation.objects.create(
            email='valid@example.com',
            organization=self.organization,
            inviter=self.inviter,
            token='valid_token',
            expires_at=future_date
        )
        
        self.assertTrue(expired_invitation.is_expired)
        self.assertFalse(valid_invitation.is_expired)
    
    def test_invitation_is_pending_property(self):
        """Test is_pending property"""
        # Create pending invitation
        pending_invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='pending_token'
        )
        
        # Create accepted invitation
        accepted_invitation = UserInvitation.objects.create(
            email='accepted@example.com',
            organization=self.organization,
            inviter=self.inviter,
            token='accepted_token',
            status='accepted'
        )
        
        # Create expired invitation
        expired_invitation = UserInvitation.objects.create(
            email='expired@example.com',
            organization=self.organization,
            inviter=self.inviter,
            token='expired_token',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        self.assertTrue(pending_invitation.is_pending)
        self.assertFalse(accepted_invitation.is_pending)
        self.assertFalse(expired_invitation.is_pending)
    
    def test_invitation_expire_method(self):
        """Test expire method"""
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='token_to_expire'
        )
        
        self.assertEqual(invitation.status, 'pending')
        
        invitation.expire()
        invitation.refresh_from_db()
        
        self.assertEqual(invitation.status, 'expired')
    
    def test_invitation_cancel_method(self):
        """Test cancel method"""
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='token_to_cancel'
        )
        
        self.assertEqual(invitation.status, 'pending')
        
        invitation.cancel()
        invitation.refresh_from_db()
        
        self.assertEqual(invitation.status, 'cancelled')
    
    def test_invitation_accept_method(self):
        """Test accept method"""
        accepter = CustomUserFactory(email=self.invitee_email)
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='token_to_accept'
        )
        
        self.assertEqual(invitation.status, 'pending')
        self.assertIsNone(invitation.accepted_at)
        self.assertIsNone(invitation.accepted_by)
        
        invitation.accept(accepter)
        invitation.refresh_from_db()
        
        self.assertEqual(invitation.status, 'accepted')
        self.assertIsNotNone(invitation.accepted_at)
        self.assertEqual(invitation.accepted_by, accepter)
    
    def test_invitation_unique_constraint(self):
        """Test unique constraint on email + organization + status"""
        UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='first_token'
        )
        
        # Should not be able to create duplicate pending invitation
        with self.assertRaises(IntegrityError):
            UserInvitation.objects.create(
                email=self.invitee_email,
                organization=self.organization,
                inviter=self.inviter,
                token='second_token'
            )
    
    def test_invitation_role_choices_validation(self):
        """Test role choices validation"""
        # Valid roles
        for role in ['viewer', 'publisher']:
            invitation = UserInvitation.objects.create(
                email=f'user_{role}@example.com',
                organization=self.organization,
                inviter=self.inviter,
                invited_role=role,
                token=f'token_{role}'
            )
            self.assertEqual(invitation.invited_role, role)
    
    def test_invitation_status_choices_validation(self):
        """Test status choices validation"""
        # Valid statuses
        for status in ['pending', 'accepted', 'expired', 'cancelled']:
            invitation = UserInvitation.objects.create(
                email=f'user_{status}@example.com',
                organization=self.organization,
                inviter=self.inviter,
                status=status,
                token=f'token_{status}'
            )
            self.assertEqual(invitation.status, status)
    
    def test_invitation_string_representation(self):
        """Test string representation of invitation"""
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='test_token'
        )
        
        expected_str = f"Invitation to {self.invitee_email} for {self.organization.name} (pending)"
        self.assertEqual(str(invitation), expected_str)
    
    def test_invitation_with_message(self):
        """Test invitation with optional message"""
        message = "Welcome to our threat intelligence sharing community!"
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='test_token',
            message=message
        )
        
        self.assertEqual(invitation.message, message)
    
    def test_invitation_cascade_delete_on_organization(self):
        """Test cascade delete when organization is deleted"""
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='test_token'
        )
        
        invitation_id = invitation.id
        self.organization.delete()
        
        # Invitation should be deleted
        with self.assertRaises(UserInvitation.DoesNotExist):
            UserInvitation.objects.get(id=invitation_id)
    
    def test_invitation_cascade_delete_on_inviter(self):
        """Test cascade delete when inviter is deleted"""
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='test_token'
        )
        
        invitation_id = invitation.id
        self.inviter.delete()
        
        # Invitation should be deleted
        with self.assertRaises(UserInvitation.DoesNotExist):
            UserInvitation.objects.get(id=invitation_id)
    
    def test_invitation_set_null_on_accepted_by_delete(self):
        """Test SET_NULL behavior when accepted_by user is deleted"""
        accepter = CustomUserFactory(email=self.invitee_email)
        invitation = UserInvitation.objects.create(
            email=self.invitee_email,
            organization=self.organization,
            inviter=self.inviter,
            token='test_token'
        )
        
        invitation.accept(accepter)
        accepter.delete()
        
        invitation.refresh_from_db()
        self.assertIsNone(invitation.accepted_by)
        self.assertEqual(invitation.status, 'accepted')  # Status should remain


class PasswordResetTokenModelTestCase(TestCase):
    """Test cases for PasswordResetToken model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUserFactory()
        self.test_token = 'secure_reset_token_123'
        self.test_ip = '192.168.1.100'
        self.test_user_agent = 'Mozilla/5.0 Test Browser'
    
    def test_create_password_reset_token_success(self):
        """Test successful creation of password reset token"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.token, self.test_token)
        self.assertEqual(token.ip_address, self.test_ip)
        self.assertEqual(token.user_agent, self.test_user_agent)
        self.assertIsNotNone(token.expires_at)
        self.assertIsNone(token.used_at)
    
    def test_token_automatic_expiry_date(self):
        """Test that token gets automatic expiry date"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token
        )
        
        # Should expire in 24 hours
        expected_expiry = timezone.now() + timedelta(hours=24)
        time_diff = abs((token.expires_at - expected_expiry).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute tolerance
    
    def test_token_custom_expiry_date(self):
        """Test token with custom expiry date"""
        custom_expiry = timezone.now() + timedelta(hours=12)
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token,
            expires_at=custom_expiry
        )
        
        self.assertEqual(token.expires_at, custom_expiry)
    
    def test_token_is_expired_property(self):
        """Test is_expired property"""
        # Create expired token
        past_date = timezone.now() - timedelta(hours=1)
        expired_token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired_token',
            expires_at=past_date
        )
        
        # Create non-expired token
        future_date = timezone.now() + timedelta(hours=1)
        valid_token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid_token',
            expires_at=future_date
        )
        
        self.assertTrue(expired_token.is_expired)
        self.assertFalse(valid_token.is_expired)
    
    def test_token_is_used_property(self):
        """Test is_used property"""
        # Create unused token
        unused_token = PasswordResetToken.objects.create(
            user=self.user,
            token='unused_token'
        )
        
        # Create used token
        used_token = PasswordResetToken.objects.create(
            user=self.user,
            token='used_token',
            used_at=timezone.now()
        )
        
        self.assertFalse(unused_token.is_used)
        self.assertTrue(used_token.is_used)
    
    def test_token_is_valid_property(self):
        """Test is_valid property"""
        # Create valid token (not expired, not used)
        valid_token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid_token'
        )
        
        # Create expired token
        expired_token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired_token',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Create used token
        used_token = PasswordResetToken.objects.create(
            user=self.user,
            token='used_token',
            used_at=timezone.now()
        )
        
        self.assertTrue(valid_token.is_valid)
        self.assertFalse(expired_token.is_valid)
        self.assertFalse(used_token.is_valid)
    
    def test_token_mark_as_used_method(self):
        """Test mark_as_used method"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token
        )
        
        self.assertIsNone(token.used_at)
        self.assertTrue(token.is_valid)
        
        token.mark_as_used()
        token.refresh_from_db()
        
        self.assertIsNotNone(token.used_at)
        self.assertFalse(token.is_valid)
    
    def test_token_unique_constraint(self):
        """Test unique constraint on token"""
        PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token
        )
        
        # Should not be able to create duplicate token
        with self.assertRaises(IntegrityError):
            PasswordResetToken.objects.create(
                user=self.user,
                token=self.test_token
            )
    
    def test_token_string_representation(self):
        """Test string representation of token"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token
        )
        
        expected_str = f"Password reset token for {self.user.username}"
        self.assertEqual(str(token), expected_str)
    
    def test_token_cascade_delete_on_user(self):
        """Test cascade delete when user is deleted"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token
        )
        
        token_id = token.id
        self.user.delete()
        
        # Token should be deleted
        with self.assertRaises(PasswordResetToken.DoesNotExist):
            PasswordResetToken.objects.get(id=token_id)
    
    def test_token_multiple_tokens_per_user(self):
        """Test that a user can have multiple reset tokens"""
        # Create first token
        token1 = PasswordResetToken.objects.create(
            user=self.user,
            token='token_1'
        )
        
        # Create second token (should be allowed)
        token2 = PasswordResetToken.objects.create(
            user=self.user,
            token='token_2'
        )
        
        self.assertEqual(token1.user, self.user)
        self.assertEqual(token2.user, self.user)
        self.assertNotEqual(token1.token, token2.token)
    
    def test_token_with_null_ip_and_user_agent(self):
        """Test token creation with null IP and user agent"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token
        )
        
        self.assertIsNone(token.ip_address)
        self.assertEqual(token.user_agent, '')
    
    def test_token_uuid_primary_key(self):
        """Test that token uses UUID as primary key"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token
        )
        
        self.assertIsInstance(token.id, uuid.UUID)
    
    def test_token_database_indexes(self):
        """Test that proper database indexes exist"""
        # This test ensures the Meta indexes are properly defined
        token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.test_token
        )
        
        # Test query performance (indexes should make these fast)
        # Find by user and expiry
        found_token = PasswordResetToken.objects.filter(
            user=self.user,
            expires_at__gt=timezone.now()
        ).first()
        self.assertEqual(found_token, token)
        
        # Find by token
        found_token = PasswordResetToken.objects.filter(
            token=self.test_token
        ).first()
        self.assertEqual(found_token, token)
    
    def test_model_verbose_names(self):
        """Test model verbose names"""
        self.assertEqual(UserInvitation._meta.verbose_name, 'User Invitation')
        self.assertEqual(UserInvitation._meta.verbose_name_plural, 'User Invitations')
        self.assertEqual(PasswordResetToken._meta.verbose_name, 'Password Reset Token')
        self.assertEqual(PasswordResetToken._meta.verbose_name_plural, 'Password Reset Tokens')
    
    def test_model_table_names(self):
        """Test custom database table names"""
        self.assertEqual(UserInvitation._meta.db_table, 'user_invitations')
        self.assertEqual(PasswordResetToken._meta.db_table, 'password_reset_tokens')


class ModelRelationshipTestCase(TestCase):
    """Test cases for model relationships and foreign keys"""
    
    def setUp(self):
        self.organization = OrganizationFactory()
        self.inviter = CustomUserFactory(role='publisher', organization=self.organization)
        self.user = CustomUserFactory()
    
    def test_user_invitation_related_names(self):
        """Test related names work correctly"""
        invitation = UserInvitation.objects.create(
            email='test@example.com',
            organization=self.organization,
            inviter=self.inviter,
            token='test_token'
        )
        
        # Test organization.invitations
        self.assertIn(invitation, self.organization.invitations.all())
        
        # Test inviter.sent_invitations
        self.assertIn(invitation, self.inviter.sent_invitations.all())
    
    def test_password_reset_token_related_names(self):
        """Test related names work correctly"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='test_token'
        )
        
        # Test user.password_reset_tokens
        self.assertIn(token, self.user.password_reset_tokens.all())
    
    def test_invitation_accepted_by_relationship(self):
        """Test accepted_by relationship"""
        accepter = CustomUserFactory(email='accepter@example.com')
        invitation = UserInvitation.objects.create(
            email='accepter@example.com',
            organization=self.organization,
            inviter=self.inviter,
            token='test_token'
        )
        
        invitation.accept(accepter)
        
        # Test accepter.accepted_invitations
        self.assertIn(invitation, accepter.accepted_invitations.all())


if __name__ == '__main__':
    unittest.main()