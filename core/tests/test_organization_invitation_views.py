"""
Comprehensive unit tests for Organization Invitation Views
Tests all invitation endpoints, permissions, and workflows
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
from core.user_management.models.invitation_models import UserInvitation
from core.user_management.models.user_models import CustomUser, Organization
from core.tests.factories import CustomUserFactory, OrganizationFactory
import uuid


class OrganizationInvitationViewsTestCase(TestCase):
    """Test cases for organization invitation endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.organization = OrganizationFactory()
        
        # Create users with different roles
        self.admin = CustomUserFactory(role='BlueVisionAdmin')
        self.publisher = CustomUserFactory(role='publisher', organization=self.organization)
        self.viewer = CustomUserFactory(role='viewer', organization=self.organization)
        self.other_org_publisher = CustomUserFactory(role='publisher', organization=OrganizationFactory())
        
        # Test data
        self.invitation_data = {
            'email': 'newuser@example.com',
            'role': 'viewer',
            'message': 'Welcome to our team!'
        }
    
    def _authenticate_user(self, user):
        """Helper method to authenticate a user"""
        self.client.force_authenticate(user=user)
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.send_invitation')
    def test_invite_user_success_publisher(self, mock_send_invitation):
        """Test successful user invitation by publisher"""
        mock_send_invitation.return_value = {
            'success': True,
            'message': 'Invitation sent successfully',
            'invitation_id': str(uuid.uuid4()),
            'expires_at': timezone.now() + timedelta(days=7)
        }
        
        self._authenticate_user(self.publisher)
        
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, self.invitation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('sent successfully', response.data['message'])
        self.assertIn('invitation_id', response.data)
        
        # Verify service was called with correct parameters
        mock_send_invitation.assert_called_once_with(
            inviter=self.publisher,
            organization=self.organization,
            email='newuser@example.com',
            role='viewer',
            message='Welcome to our team!'
        )
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.send_invitation')
    def test_invite_user_success_admin(self, mock_send_invitation):
        """Test successful user invitation by BlueVision admin"""
        mock_send_invitation.return_value = {
            'success': True,
            'message': 'Invitation sent successfully',
            'invitation_id': str(uuid.uuid4()),
            'expires_at': timezone.now() + timedelta(days=7)
        }
        
        self._authenticate_user(self.admin)
        
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, self.invitation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify service was called
        mock_send_invitation.assert_called_once()
    
    def test_invite_user_permission_denied_viewer(self):
        """Test invitation denied for viewer role"""
        self._authenticate_user(self.viewer)
        
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, self.invitation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('do not have permission', response.data['detail'])
    
    def test_invite_user_permission_denied_other_org(self):
        """Test invitation denied for publisher from different organization"""
        self._authenticate_user(self.other_org_publisher)
        
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, self.invitation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_invite_user_unauthenticated(self):
        """Test invitation requires authentication"""
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, self.invitation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_invite_user_invalid_email(self):
        """Test invitation with invalid email"""
        self._authenticate_user(self.publisher)
        
        invalid_data = self.invitation_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(response.data).lower())
    
    def test_invite_user_missing_email(self):
        """Test invitation with missing email"""
        self._authenticate_user(self.publisher)
        
        invalid_data = self.invitation_data.copy()
        del invalid_data['email']
        
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invite_user_invalid_role(self):
        """Test invitation with invalid role"""
        self._authenticate_user(self.publisher)
        
        invalid_data = self.invitation_data.copy()
        invalid_data['role'] = 'invalid_role'
        
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invite_user_nonexistent_organization(self):
        """Test invitation to non-existent organization"""
        self._authenticate_user(self.admin)
        
        fake_org_id = str(uuid.uuid4())
        url = reverse('organization-invite-user', kwargs={'pk': fake_org_id})
        response = self.client.post(url, self.invitation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.send_invitation')
    def test_invite_user_service_failure(self, mock_send_invitation):
        """Test handling of service failure"""
        mock_send_invitation.return_value = {
            'success': False,
            'message': 'User already exists in organization'
        }
        
        self._authenticate_user(self.publisher)
        
        url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
        response = self.client.post(url, self.invitation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('already exists', response.data['message'])
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.list_invitations')
    def test_list_invitations_success(self, mock_list_invitations):
        """Test successful invitation listing"""
        mock_invitations = [
            {
                'id': str(uuid.uuid4()),
                'email': 'user1@example.com',
                'role': 'viewer',
                'status': 'pending',
                'inviter_name': self.publisher.get_full_name(),
                'created_at': timezone.now().isoformat(),
                'expires_at': (timezone.now() + timedelta(days=7)).isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'email': 'user2@example.com',
                'role': 'publisher',
                'status': 'accepted',
                'inviter_name': self.publisher.get_full_name(),
                'created_at': timezone.now().isoformat(),
                'expires_at': (timezone.now() + timedelta(days=7)).isoformat()
            }
        ]
        mock_list_invitations.return_value = mock_invitations
        
        self._authenticate_user(self.publisher)
        
        url = reverse('organization-invitations', kwargs={'pk': str(self.organization.id)})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['invitations']), 2)
        self.assertEqual(response.data['data']['invitations'][0]['email'], 'user1@example.com')
        
        # Verify service was called with correct parameters
        mock_list_invitations.assert_called_once_with(organization=self.organization, status=None)
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.list_invitations')
    def test_list_invitations_filtered_by_status(self, mock_list_invitations):
        """Test invitation listing filtered by status"""
        mock_list_invitations.return_value = []
        
        self._authenticate_user(self.publisher)
        
        url = reverse('organization-invitations', kwargs={'pk': str(self.organization.id)})
        response = self.client.get(url, {'status': 'pending'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify service was called with status filter
        mock_list_invitations.assert_called_once_with(organization=self.organization, status='pending')
    
    def test_list_invitations_permission_denied(self):
        """Test invitation listing permission denied"""
        self._authenticate_user(self.viewer)
        
        url = reverse('organization-invitations', kwargs={'pk': str(self.organization.id)})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.cancel_invitation')
    def test_cancel_invitation_success(self, mock_cancel_invitation):
        """Test successful invitation cancellation"""
        invitation_id = str(uuid.uuid4())
        mock_cancel_invitation.return_value = {
            'success': True,
            'message': 'Invitation cancelled successfully'
        }
        
        self._authenticate_user(self.publisher)
        
        url = reverse('organization-cancel-invitation', kwargs={
            'pk': str(self.organization.id),
            'invitation_id': invitation_id
        })
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('cancelled successfully', response.data['message'])
        
        # Verify service was called with correct parameters
        mock_cancel_invitation.assert_called_once_with(invitation_id, self.publisher)
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.cancel_invitation')
    def test_cancel_invitation_not_found(self, mock_cancel_invitation):
        """Test cancellation of non-existent invitation"""
        invitation_id = str(uuid.uuid4())
        mock_cancel_invitation.return_value = {
            'success': False,
            'message': 'Invitation not found'
        }
        
        self._authenticate_user(self.publisher)
        
        url = reverse('organization-cancel-invitation', kwargs={
            'pk': str(self.organization.id),
            'invitation_id': invitation_id
        })
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.cancel_invitation')
    def test_cancel_invitation_permission_denied(self, mock_cancel_invitation):
        """Test cancellation permission denied"""
        invitation_id = str(uuid.uuid4())
        mock_cancel_invitation.return_value = {
            'success': False,
            'message': 'You do not have permission to cancel this invitation'
        }
        
        self._authenticate_user(self.viewer)
        
        url = reverse('organization-cancel-invitation', kwargs={
            'pk': str(self.organization.id),
            'invitation_id': invitation_id
        })
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.accept_invitation')
    def test_accept_invitation_success(self, mock_accept_invitation):
        """Test successful invitation acceptance"""
        invitation_token = 'test_invitation_token_123'
        mock_accept_invitation.return_value = {
            'success': True,
            'message': 'Successfully joined organization',
            'organization': {
                'id': str(self.organization.id),
                'name': self.organization.name
            }
        }
        
        new_user = CustomUserFactory(email='newuser@example.com')
        self._authenticate_user(new_user)
        
        url = reverse('accept-invitation')
        response = self.client.post(url, {'token': invitation_token}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('Successfully joined', response.data['message'])
        self.assertIn('organization', response.data)
        
        # Verify service was called with correct parameters
        mock_accept_invitation.assert_called_once_with(invitation_token, new_user)
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.accept_invitation')
    def test_accept_invitation_invalid_token(self, mock_accept_invitation):
        """Test invitation acceptance with invalid token"""
        mock_accept_invitation.return_value = {
            'success': False,
            'message': 'Invalid invitation token'
        }
        
        new_user = CustomUserFactory()
        self._authenticate_user(new_user)
        
        url = reverse('accept-invitation')
        response = self.client.post(url, {'token': 'invalid_token'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Invalid invitation token', response.data['message'])
    
    def test_accept_invitation_missing_token(self):
        """Test invitation acceptance with missing token"""
        new_user = CustomUserFactory()
        self._authenticate_user(new_user)
        
        url = reverse('accept-invitation')
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', str(response.data).lower())
    
    def test_accept_invitation_unauthenticated(self):
        """Test invitation acceptance requires authentication"""
        url = reverse('accept-invitation')
        response = self.client.post(url, {'token': 'test_token'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('core.user_management.services.invitation_service.UserInvitationService.accept_invitation')
    def test_accept_invitation_expired(self, mock_accept_invitation):
        """Test acceptance of expired invitation"""
        mock_accept_invitation.return_value = {
            'success': False,
            'message': 'Invitation has expired'
        }
        
        new_user = CustomUserFactory()
        self._authenticate_user(new_user)
        
        url = reverse('accept-invitation')
        response = self.client.post(url, {'token': 'expired_token'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', response.data['message'])
    
    def test_invite_user_with_optional_message(self):
        """Test invitation with optional message"""
        self._authenticate_user(self.publisher)
        
        data_without_message = {
            'email': 'user@example.com',
            'role': 'viewer'
        }
        
        with patch('core.user_management.services.invitation_service.UserInvitationService.send_invitation') as mock_send:
            mock_send.return_value = {'success': True, 'message': 'Sent'}
            
            url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
            response = self.client.post(url, data_without_message, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Verify service was called with None message
            call_args = mock_send.call_args
            self.assertIsNone(call_args[1]['message'])
    
    def test_invite_user_role_validation(self):
        """Test role validation in invitation"""
        self._authenticate_user(self.publisher)
        
        # Test valid roles
        valid_roles = ['viewer', 'publisher']
        for role in valid_roles:
            with self.subTest(role=role):
                data = self.invitation_data.copy()
                data['role'] = role
                data['email'] = f'user_{role}@example.com'
                
                with patch('core.user_management.services.invitation_service.UserInvitationService.send_invitation') as mock_send:
                    mock_send.return_value = {'success': True, 'message': 'Sent'}
                    
                    url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
                    response = self.client.post(url, data, format='json')
                    
                    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_invitation_endpoints_require_organization_access(self):
        """Test that invitation endpoints require organization access"""
        other_organization = OrganizationFactory()
        self._authenticate_user(self.publisher)  # Publisher of different org
        
        endpoints = [
            ('organization-invite-user', 'post', self.invitation_data),
            ('organization-invitations', 'get', None),
            ('organization-cancel-invitation', 'delete', None, str(uuid.uuid4())),
        ]
        
        for endpoint_data in endpoints:
            with self.subTest(endpoint=endpoint_data[0]):
                if len(endpoint_data) == 4:
                    url = reverse(endpoint_data[0], kwargs={
                        'pk': str(other_organization.id),
                        'invitation_id': endpoint_data[3]
                    })
                else:
                    url = reverse(endpoint_data[0], kwargs={'pk': str(other_organization.id)})
                
                method = getattr(self.client, endpoint_data[1])
                
                if endpoint_data[2]:
                    response = method(url, endpoint_data[2], format='json')
                else:
                    response = method(url)
                
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_invitation_list_pagination(self):
        """Test invitation list supports pagination"""
        self._authenticate_user(self.publisher)
        
        with patch('core.user_management.services.invitation_service.UserInvitationService.list_invitations') as mock_list:
            # Create large mock dataset
            mock_invitations = []
            for i in range(50):
                mock_invitations.append({
                    'id': str(uuid.uuid4()),
                    'email': f'user{i}@example.com',
                    'role': 'viewer',
                    'status': 'pending',
                    'created_at': timezone.now().isoformat()
                })
            mock_list.return_value = mock_invitations
            
            url = reverse('organization-invitations', kwargs={'pk': str(self.organization.id)})
            response = self.client.get(url, {'limit': 10, 'offset': 20})
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('invitations', response.data['data'])
    
    def test_invitation_endpoints_handle_invalid_uuid(self):
        """Test invitation endpoints handle invalid UUID formats"""
        self._authenticate_user(self.admin)
        
        invalid_ids = ['invalid-uuid', '123', 'not-a-uuid-at-all']
        
        for invalid_id in invalid_ids:
            with self.subTest(invalid_id=invalid_id):
                url = reverse('organization-invite-user', kwargs={'pk': invalid_id})
                response = self.client.post(url, self.invitation_data, format='json')
                
                # Should return 404 for invalid UUID format
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrganizationInvitationViewsIntegrationTestCase(TestCase):
    """Integration test cases for invitation workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.organization = OrganizationFactory()
        self.publisher = CustomUserFactory(role='publisher', organization=self.organization)
        
    def test_complete_invitation_workflow(self):
        """Test complete invitation workflow from send to accept"""
        # Step 1: Send invitation
        self._authenticate_user(self.publisher)
        
        invitation_data = {
            'email': 'newuser@example.com',
            'role': 'viewer',
            'message': 'Welcome to our team!'
        }
        
        with patch('core.user_management.services.invitation_service.GmailSMTPService') as mock_email:
            mock_email_service = MagicMock()
            mock_email_service.send_user_invitation_email.return_value = {'success': True}
            mock_email.return_value = mock_email_service
            
            url = reverse('organization-invite-user', kwargs={'pk': str(self.organization.id)})
            response = self.client.post(url, invitation_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Verify invitation was created
        invitation = UserInvitation.objects.get(email='newuser@example.com')
        self.assertEqual(invitation.status, 'pending')
        self.assertEqual(invitation.invited_role, 'viewer')
        
        # Step 3: Accept invitation
        new_user = CustomUserFactory(email='newuser@example.com')
        self._authenticate_user(new_user)
        
        accept_url = reverse('accept-invitation')
        accept_response = self.client.post(
            accept_url, 
            {'token': invitation.token}, 
            format='json'
        )
        
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertTrue(accept_response.data['success'])
        
        # Step 4: Verify invitation was accepted and user was updated
        invitation.refresh_from_db()
        new_user.refresh_from_db()
        
        self.assertEqual(invitation.status, 'accepted')
        self.assertEqual(new_user.organization, self.organization)
        self.assertEqual(new_user.role, 'viewer')
    
    def _authenticate_user(self, user):
        """Helper method to authenticate a user"""
        self.client.force_authenticate(user=user)


if __name__ == '__main__':
    unittest.main()