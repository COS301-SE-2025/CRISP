"""
Comprehensive tests for organization service to increase coverage
"""

from django.test import TestCase
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from unittest.mock import patch, Mock
from datetime import timedelta
from core_ut.user_management.services.organization_service import OrganizationService
from core_ut.user_management.models import CustomUser, Organization, AuthenticationLog
from core_ut.trust.models import TrustRelationship, TrustLevel, TrustGroup, TrustGroupMembership


class OrganizationServiceComprehensiveTest(TestCase):
    """Comprehensive test suite for organization service"""
    
    def setUp(self):
        """Set up test data"""
        # Create test organization
        self.organization = Organization.objects.create(
            name='Service Test Org',
            domain='servicetest.com',
            contact_email='admin@servicetest.com',
            organization_type='educational',
            is_active=True,
            is_verified=True,
            is_publisher=True
        )
        
        # Create another organization
        self.other_organization = Organization.objects.create(
            name='Other Test Org',
            domain='othertest.com',
            contact_email='admin@othertest.com',
            organization_type='government',
            is_active=True,
            is_verified=True,
            is_publisher=False
        )
        
        # Create test users
        self.admin_user = CustomUser.objects.create_user(
            username='admin@servicetest.com',
            email='admin@servicetest.com',
            password='TestPassword123',
            first_name='Admin',
            last_name='User',
            role='BlueVisionAdmin',
            organization=self.organization,
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        
        self.publisher_user = CustomUser.objects.create_user(
            username='publisher@servicetest.com',
            email='publisher@servicetest.com',
            password='TestPassword123',
            first_name='Publisher',
            last_name='User',
            role='publisher',
            organization=self.organization,
            is_active=True,
            is_verified=True,
            is_publisher=True
        )
        
        self.viewer_user = CustomUser.objects.create_user(
            username='viewer@servicetest.com',
            email='viewer@servicetest.com',
            password='TestPassword123',
            first_name='Viewer',
            last_name='User',
            role='viewer',
            organization=self.organization,
            is_active=True,
            is_verified=True
        )
        
        # Create trust level
        self.trust_level = TrustLevel.objects.create(
            name='High Trust',
            level='trusted',
            numerical_value=80,
            description='High level of trust',
            created_by='system'
        )
        
        self.service = OrganizationService()
    
    def test_create_organization_pattern_1_success(self):
        """Test organization creation with pattern 1 (org_data contains primary_user)"""
        org_data = {
            'name': 'New Test Org',
            'organization_type': 'private',
            'domain': 'newtest.com',
            'contact_email': 'admin@newtest.com',
            'primary_user': {
                'username': 'newadmin@newtest.com',
                'email': 'newadmin@newtest.com',
                'password': 'SecurePassword123!',
                'first_name': 'New',
                'last_name': 'Admin'
            }
        }
        
        org, user = self.service.create_organization(
            creating_user=self.admin_user,
            org_data=org_data
        )
        
        self.assertEqual(org.name, 'New Test Org')
        self.assertEqual(org.organization_type, 'private')
        self.assertEqual(user.role, 'publisher')
        self.assertTrue(user.is_publisher)
        self.assertEqual(user.organization, org)
    
    def test_create_organization_pattern_2_success(self):
        """Test organization creation with pattern 2 (separate primary_user_data)"""
        org_data = {
            'name': 'Pattern 2 Org',
            'organization_type': 'educational',
            'domain': 'pattern2.com',
            'contact_email': 'admin@pattern2.com'
        }
        
        primary_user_data = {
            'username': 'pattern2admin@pattern2.com',
            'email': 'pattern2admin@pattern2.com',
            'password': 'SecurePassword123!',
            'first_name': 'Pattern2',
            'last_name': 'Admin'
        }
        
        org, user = self.service.create_organization(
            creating_user=self.admin_user,
            org_data=org_data,
            primary_user_data=primary_user_data
        )
        
        self.assertEqual(org.name, 'Pattern 2 Org')
        self.assertEqual(user.username, 'pattern2admin@pattern2.com')
    
    def test_create_organization_pattern_3_success(self):
        """Test organization creation with pattern 3 (direct arguments)"""
        primary_user_data = {
            'username': 'pattern3admin@pattern3.com',
            'email': 'pattern3admin@pattern3.com',
            'password': 'SecurePassword123!',
            'first_name': 'Pattern3',
            'last_name': 'Admin'
        }
        
        org, user = self.service.create_organization(
            name='Pattern 3 Org',
            organization_type='government',
            primary_user_data=primary_user_data,
            domain='pattern3.com'
        )
        
        self.assertEqual(org.name, 'Pattern 3 Org')
        self.assertEqual(org.organization_type, 'government')
        self.assertEqual(user.username, 'pattern3admin@pattern3.com')
    
    def test_create_organization_missing_creating_user(self):
        """Test organization creation with missing creating_user"""
        org_data = {
            'name': 'Test Org',
            'organization_type': 'private'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_organization(org_data=org_data)
        
        self.assertIn('creating_user and org_data are required', str(context.exception))
    
    @patch('core.user_management.services.organization_service.AccessControlService')
    def test_create_organization_no_permission(self, mock_access_control):
        """Test organization creation without permission"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = False
        mock_access_control.return_value = mock_access_control_instance
        
        org_data = {
            'name': 'No Permission Org',
            'organization_type': 'private',
            'primary_user': {
                'username': 'test@test.com',
                'email': 'test@test.com',
                'password': 'Password123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        service = OrganizationService()
        
        with self.assertRaises(PermissionDenied):
            service.create_organization(
                creating_user=self.viewer_user,
                org_data=org_data
            )
    
    def test_create_organization_missing_required_fields(self):
        """Test organization creation with missing required fields"""
        org_data = {
            'organization_type': 'private',
            'primary_user': {
                'username': 'test@test.com',
                'email': 'test@test.com',
                'password': 'Password123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_organization(
                creating_user=self.admin_user,
                org_data=org_data
            )
        
        self.assertIn('Organization name is required', str(context.exception))
    
    def test_create_organization_missing_primary_user_field(self):
        """Test organization creation with missing primary user field"""
        org_data = {
            'name': 'Test Org',
            'organization_type': 'private',
            'primary_user': {
                'username': 'test@test.com',
                'email': 'test@test.com',
                # Missing password
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_organization(
                creating_user=self.admin_user,
                org_data=org_data
            )
        
        self.assertIn("Primary user 'password' is required", str(context.exception))
    
    def test_create_organization_duplicate_name(self):
        """Test organization creation with duplicate name"""
        org_data = {
            'name': 'Service Test Org',  # Already exists
            'organization_type': 'private',
            'primary_user': {
                'username': 'test@test.com',
                'email': 'test@test.com',
                'password': 'Password123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_organization(
                creating_user=self.admin_user,
                org_data=org_data
            )
        
        self.assertIn('Organization name already exists', str(context.exception))
    
    def test_create_organization_duplicate_domain(self):
        """Test organization creation with duplicate domain"""
        org_data = {
            'name': 'New Org',
            'organization_type': 'private',
            'domain': 'servicetest.com',  # Already exists
            'primary_user': {
                'username': 'test@test.com',
                'email': 'test@test.com',
                'password': 'Password123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_organization(
                creating_user=self.admin_user,
                org_data=org_data
            )
        
        self.assertIn('Organization domain already exists', str(context.exception))
    
    def test_create_organization_duplicate_username(self):
        """Test organization creation with duplicate username"""
        org_data = {
            'name': 'New Org',
            'organization_type': 'private',
            'primary_user': {
                'username': 'admin@servicetest.com',  # Already exists
                'email': 'new@test.com',
                'password': 'Password123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_organization(
                creating_user=self.admin_user,
                org_data=org_data
            )
        
        self.assertIn('Primary user username already exists', str(context.exception))
    
    def test_create_organization_duplicate_email(self):
        """Test organization creation with duplicate email"""
        org_data = {
            'name': 'New Org',
            'organization_type': 'private',
            'primary_user': {
                'username': 'newuser@test.com',
                'email': 'admin@servicetest.com',  # Already exists
                'password': 'Password123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_organization(
                creating_user=self.admin_user,
                org_data=org_data
            )
        
        self.assertIn('Primary user email already exists', str(context.exception))
    
    @patch('core.user_management.services.organization_service.AuthenticationLog.log_authentication_event')
    def test_create_organization_logging(self, mock_log):
        """Test that organization creation logs events"""
        org_data = {
            'name': 'Logging Test Org',
            'organization_type': 'private',
            'primary_user': {
                'username': 'logging@test.com',
                'email': 'logging@test.com',
                'password': 'Password123!',
                'first_name': 'Logging',
                'last_name': 'User'
            }
        }
        
        self.service.create_organization(
            creating_user=self.admin_user,
            org_data=org_data
        )
        
        mock_log.assert_called()
        call_args = mock_log.call_args
        self.assertEqual(call_args[1]['action'], 'organization_created')
        self.assertTrue(call_args[1]['success'])
    
    def test_update_organization_success_admin(self):
        """Test successful organization update by admin"""
        update_data = {
            'description': 'Updated description',
            'contact_email': 'updated@servicetest.com',
            'website': 'https://updated.servicetest.com'
        }
        
        updated_org = self.service.update_organization(
            updating_user=self.admin_user,
            organization_id=str(self.organization.id),
            update_data=update_data
        )
        
        self.assertEqual(updated_org.description, 'Updated description')
        self.assertEqual(updated_org.contact_email, 'updated@servicetest.com')
        self.assertEqual(updated_org.website, 'https://updated.servicetest.com')
    
    def test_update_organization_success_publisher(self):
        """Test successful organization update by publisher from same org"""
        update_data = {
            'description': 'Publisher updated description'
        }
        
        updated_org = self.service.update_organization(
            updating_user=self.publisher_user,
            organization_id=str(self.organization.id),
            update_data=update_data
        )
        
        self.assertEqual(updated_org.description, 'Publisher updated description')
    
    def test_update_organization_not_found(self):
        """Test organization update with non-existent organization"""
        update_data = {'description': 'Test'}
        
        with self.assertRaises(ValidationError) as context:
            self.service.update_organization(
                updating_user=self.admin_user,
                organization_id='00000000-0000-0000-0000-000000000000',
                update_data=update_data
            )
        
        self.assertIn('Organization not found', str(context.exception))
    
    def test_update_organization_no_permission(self):
        """Test organization update without permission"""
        update_data = {'description': 'Test'}
        
        with self.assertRaises(PermissionDenied):
            self.service.update_organization(
                updating_user=self.viewer_user,
                organization_id=str(self.organization.id),
                update_data=update_data
            )
    
    def test_update_organization_different_org_publisher(self):
        """Test organization update by publisher from different org"""
        other_publisher = CustomUser.objects.create_user(
            username='otherpub@othertest.com',
            email='otherpub@othertest.com',
            password='Password123!',
            role='publisher',
            organization=self.other_organization
        )
        
        update_data = {'description': 'Test'}
        
        with self.assertRaises(PermissionDenied):
            self.service.update_organization(
                updating_user=other_publisher,
                organization_id=str(self.organization.id),
                update_data=update_data
            )
    
    def test_update_organization_admin_fields(self):
        """Test that admin can update restricted fields"""
        update_data = {
            'name': 'Admin Updated Name',
            'is_verified': False,
            'is_active': False
        }
        
        updated_org = self.service.update_organization(
            updating_user=self.admin_user,
            organization_id=str(self.organization.id),
            update_data=update_data
        )
        
        self.assertEqual(updated_org.name, 'Admin Updated Name')
        self.assertFalse(updated_org.is_verified)
        self.assertFalse(updated_org.is_active)
    
    def test_update_organization_no_changes(self):
        """Test organization update with no actual changes"""
        update_data = {
            'description': self.organization.description  # Same as current
        }
        
        updated_org = self.service.update_organization(
            updating_user=self.admin_user,
            organization_id=str(self.organization.id),
            update_data=update_data
        )
        
        self.assertEqual(updated_org, self.organization)
    
    @patch('core.user_management.services.organization_service.AccessControlService')
    def test_get_organization_details_success(self, mock_access_control):
        """Test successful organization details retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.can_access_organization.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        service = OrganizationService()
        details = service.get_organization_details(
            requesting_user=self.admin_user,
            organization_id=str(self.organization.id)
        )
        
        self.assertEqual(details['name'], self.organization.name)
        self.assertEqual(details['organization_type'], self.organization.organization_type)
        self.assertIn('user_count', details)
        self.assertIn('can_publish_threat_intelligence', details)
    
    def test_get_organization_details_not_found(self):
        """Test organization details retrieval with non-existent organization"""
        with self.assertRaises(ValidationError) as context:
            self.service.get_organization_details(
                requesting_user=self.admin_user,
                organization_id='00000000-0000-0000-0000-000000000000'
            )
        
        self.assertIn('Organization not found', str(context.exception))
    
    @patch('core.user_management.services.organization_service.AccessControlService')
    def test_get_organization_details_no_access(self, mock_access_control):
        """Test organization details retrieval without access"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.can_access_organization.return_value = False
        mock_access_control.return_value = mock_access_control_instance
        
        service = OrganizationService()
        
        with self.assertRaises(PermissionDenied):
            service.get_organization_details(
                requesting_user=self.viewer_user,
                organization_id=str(self.organization.id)
            )
    
    def test_get_organization_trust_info(self):
        """Test organization trust info retrieval"""
        # Create trust relationship
        TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.other_organization,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            created_by=self.admin_user
        )
        
        # Create trust group and membership
        trust_group = TrustGroup.objects.create(
            name='Test Trust Group',
            description='Test group',
            default_trust_level=self.trust_level,
            group_type='community',
            is_public=True,
            created_by=self.admin_user
        )
        
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.organization,
            membership_type='member',
            is_active=True
        )
        
        trust_info = self.service._get_organization_trust_info(
            self.admin_user, 
            self.organization
        )
        
        self.assertIn('trust_relationships', trust_info)
        self.assertIn('trust_groups', trust_info)
        self.assertEqual(len(trust_info['trust_relationships']['outgoing']), 1)
        self.assertEqual(len(trust_info['trust_groups']), 1)
    
    def test_get_organization_users(self):
        """Test organization users retrieval"""
        users = self.service._get_organization_users(self.organization)
        
        self.assertEqual(len(users), 3)  # admin, publisher, viewer
        usernames = [user['username'] for user in users]
        self.assertIn('admin@servicetest.com', usernames)
        self.assertIn('publisher@servicetest.com', usernames)
        self.assertIn('viewer@servicetest.com', usernames)
    
    @patch('core.user_management.services.organization_service.AccessControlService')
    def test_list_organizations_success(self, mock_access_control):
        """Test successful organization listing"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.get_accessible_organizations.return_value = [
            self.organization, self.other_organization
        ]
        mock_access_control_instance.get_trust_aware_data_access.return_value = {
            'access_level': 'read',
            'trust_level': 'medium'
        }
        mock_access_control.return_value = mock_access_control_instance
        
        service = OrganizationService()
        org_list = service.list_organizations(self.admin_user)
        
        self.assertEqual(len(org_list), 2)
        self.assertTrue(any(org['name'] == 'Service Test Org' for org in org_list))
        self.assertTrue(any(org['name'] == 'Other Test Org' for org in org_list))
    
    @patch('core.user_management.services.organization_service.AccessControlService')
    def test_list_organizations_with_filters(self, mock_access_control):
        """Test organization listing with filters"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.get_accessible_organizations.return_value = [
            self.organization, self.other_organization
        ]
        mock_access_control_instance.get_trust_aware_data_access.return_value = {
            'access_level': 'read',
            'trust_level': 'medium'
        }
        mock_access_control.return_value = mock_access_control_instance
        
        service = OrganizationService()
        
        # Test is_publisher filter
        org_list = service.list_organizations(
            self.admin_user, 
            filters={'is_publisher': True}
        )
        self.assertEqual(len(org_list), 1)
        self.assertEqual(org_list[0]['name'], 'Service Test Org')
        
        # Test organization_type filter
        org_list = service.list_organizations(
            self.admin_user,
            filters={'organization_type': 'government'}
        )
        self.assertEqual(len(org_list), 1)
        self.assertEqual(org_list[0]['name'], 'Other Test Org')
        
        # Test search filter
        org_list = service.list_organizations(
            self.admin_user,
            filters={'search': 'service'}
        )
        self.assertEqual(len(org_list), 1)
        self.assertEqual(org_list[0]['name'], 'Service Test Org')
    
    @patch('core.user_management.services.organization_service.AccessControlService')
    def test_deactivate_organization_success(self, mock_access_control):
        """Test successful organization deactivation"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.require_permission.return_value = None
        mock_access_control.return_value = mock_access_control_instance
        
        service = OrganizationService()
        
        # Create trust relationship to test revocation
        TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.other_organization,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            created_by=self.admin_user
        )
        
        deactivated_org = service.deactivate_organization(
            deactivating_user=self.admin_user,
            organization_id=str(self.organization.id),
            reason='Test deactivation'
        )
        
        self.assertFalse(deactivated_org.is_active)
        
        # Check that users were deactivated
        users = CustomUser.objects.filter(organization=self.organization)
        self.assertTrue(all(not user.is_active for user in users))
        
        # Check that trust relationships were revoked
        relationships = TrustRelationship.objects.filter(
            source_organization=self.organization
        )
        self.assertTrue(all(rel.status == 'revoked' for rel in relationships))
    
    def test_deactivate_organization_not_found(self):
        """Test organization deactivation with non-existent organization"""
        with self.assertRaises(ValidationError) as context:
            self.service.deactivate_organization(
                deactivating_user=self.admin_user,
                organization_id='00000000-0000-0000-0000-000000000000',
                reason='Test'
            )
        
        self.assertIn('Organization not found', str(context.exception))
    
    def test_deactivate_organization_already_inactive(self):
        """Test deactivation of already inactive organization"""
        # First deactivate
        self.organization.is_active = False
        self.organization.save()
        
        with self.assertRaises(ValidationError) as context:
            self.service.deactivate_organization(
                deactivating_user=self.admin_user,
                organization_id=str(self.organization.id),
                reason='Test'
            )
        
        self.assertIn('Organization is already deactivated', str(context.exception))
    
    @patch('core.user_management.services.organization_service.AccessControlService')
    def test_get_organization_statistics_success(self, mock_access_control):
        """Test successful organization statistics retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.require_permission.return_value = None
        mock_access_control.return_value = mock_access_control_instance
        
        service = OrganizationService()
        stats = service.get_organization_statistics(self.admin_user)
        
        self.assertIn('total_organizations', stats)
        self.assertIn('active_organizations', stats)
        self.assertIn('publisher_organizations', stats)
        self.assertIn('verified_organizations', stats)
        self.assertIn('by_type', stats)
        self.assertIn('recent_registrations', stats)
        self.assertIn('trust_metrics', stats)
        
        self.assertIsInstance(stats['total_organizations'], int)
        self.assertIsInstance(stats['by_type'], dict)
        self.assertIsInstance(stats['recent_registrations'], list)
    
    def test_get_organization_statistics_with_data(self):
        """Test organization statistics with actual data"""
        # Create additional organizations for better statistics
        for i in range(3):
            Organization.objects.create(
                name=f'Stats Test Org {i}',
                domain=f'statstest{i}.com',
                contact_email=f'admin@statstest{i}.com',
                organization_type='private' if i % 2 else 'educational',
                is_active=True,
                is_verified=True,
                is_publisher=i % 2 == 0
            )
        
        # Create trust relationships
        TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.other_organization,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            created_by=self.admin_user
        )
        
        stats = self.service.get_organization_statistics(self.admin_user)
        
        self.assertGreater(stats['total_organizations'], 2)
        self.assertGreater(stats['trust_metrics']['total_relationships'], 0)
    
    def test_exception_handling_in_trust_info(self):
        """Test exception handling in trust info retrieval"""
        with patch('core.user_management.services.organization_service.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            trust_info = self.service._get_organization_trust_info(
                self.admin_user,
                self.organization
            )
            
            # Should return empty structure when exception occurs
            self.assertEqual(len(trust_info['trust_relationships']['outgoing']), 0)
    
    def test_exception_handling_in_users_list(self):
        """Test exception handling in users list retrieval"""
        with patch('core.user_management.services.organization_service.CustomUser.objects.filter', side_effect=Exception('DB Error')):
            users = self.service._get_organization_users(self.organization)
            
            # Should return empty list when exception occurs
            self.assertEqual(len(users), 0)
    
    def test_exception_handling_in_statistics(self):
        """Test exception handling in statistics retrieval"""
        with patch('django.db.models.Count', side_effect=Exception('Stats Error')):
            stats = self.service.get_organization_statistics(self.admin_user)
            
            # Should still return basic stats structure
            self.assertIn('total_organizations', stats)
            self.assertIn('by_type', stats)
    
    def test_create_organization_transaction_rollback(self):
        """Test that creation transaction rolls back on error"""
        org_data = {
            'name': 'Transaction Test Org',
            'organization_type': 'private',
            'primary_user': {
                'username': 'transaction@test.com',
                'email': 'transaction@test.com',
                'password': 'Password123!',
                'first_name': 'Transaction',
                'last_name': 'User'
            }
        }
        
        # Mock to cause error during user creation
        with patch('core.user_management.models.CustomUser.objects.create_user', side_effect=Exception('User creation failed')):
            with self.assertRaises(ValidationError):
                self.service.create_organization(
                    creating_user=self.admin_user,
                    org_data=org_data
                )
            
            # Organization should not exist due to rollback
            self.assertFalse(Organization.objects.filter(name='Transaction Test Org').exists())
    
    def test_update_organization_invalid_field(self):
        """Test organization update with invalid field"""
        update_data = {
            'invalid_field': 'test_value',
            'description': 'Valid update'
        }
        
        updated_org = self.service.update_organization(
            updating_user=self.admin_user,
            organization_id=str(self.organization.id),
            update_data=update_data
        )
        
        # Should only update valid fields
        self.assertEqual(updated_org.description, 'Valid update')
        self.assertFalse(hasattr(updated_org, 'invalid_field'))
    
    def test_organization_details_with_trust_management(self):
        """Test organization details for user with trust management permissions"""
        # Set trust management permission
        self.admin_user.can_manage_trust_relationships = True
        
        details = self.service.get_organization_details(
            requesting_user=self.admin_user,
            organization_id=str(self.organization.id)
        )
        
        self.assertIn('trust_info', details)
    
    def test_organization_details_with_user_management(self):
        """Test organization details for user with user management permissions"""
        details = self.service.get_organization_details(
            requesting_user=self.admin_user,
            organization_id=str(self.organization.id)
        )
        
        self.assertIn('users', details)
        self.assertEqual(len(details['users']), 3)
    
    def test_list_organizations_own_vs_external(self):
        """Test organization list distinguishes own vs external organizations"""
        with patch.object(self.service.access_control, 'get_accessible_organizations', return_value=[self.organization, self.other_organization]):
            with patch.object(self.service.access_control, 'get_trust_aware_data_access', return_value={'access_level': 'read', 'trust_level': 'medium'}):
                org_list = self.service.list_organizations(self.admin_user)
                
                own_org = next(org for org in org_list if org['name'] == 'Service Test Org')
                external_org = next(org for org in org_list if org['name'] == 'Other Test Org')
                
                self.assertTrue(own_org['is_own_organization'])
                self.assertEqual(own_org['access_level'], 'full')
                
                self.assertFalse(external_org['is_own_organization'])
                self.assertEqual(external_org['access_level'], 'read')