"""
Comprehensive tests for trust aware service to increase coverage
"""

from django.test import TestCase
from django.core.exceptions import PermissionDenied
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from core.user_management.services.trust_aware_service import TrustAwareService
from core.user_management.models import CustomUser, Organization
from core.trust.models import TrustRelationship, TrustLevel, TrustGroup, TrustGroupMembership


class TrustAwareServiceComprehensiveTest(TestCase):
    """Comprehensive test suite for trust aware service"""
    
    def setUp(self):
        """Set up test data"""
        # Create test organizations
        self.organization = Organization.objects.create(
            name='Trust Aware Test Org',
            domain='trustawaretest.com',
            contact_email='admin@trustawaretest.com',
            organization_type='educational',
            is_active=True,
            is_verified=True,
            is_publisher=True
        )
        
        self.target_organization = Organization.objects.create(
            name='Target Test Org',
            domain='targettest.com',
            contact_email='admin@targettest.com',
            organization_type='government',
            is_active=True,
            is_verified=True,
            is_publisher=True
        )
        
        self.third_organization = Organization.objects.create(
            name='Third Test Org',
            domain='thirdtest.com',
            contact_email='admin@thirdtest.com',
            organization_type='private',
            is_active=True,
            is_verified=True,
            is_publisher=False
        )
        
        # Create trust levels
        self.high_trust_level = TrustLevel.objects.create(
            name='High Trust',
            level='trusted',
            numerical_value=80,
            description='High level of trust',
            created_by='system',
            default_access_level='full',
            default_anonymization_level='none'
        )
        
        self.medium_trust_level = TrustLevel.objects.create(
            name='Medium Trust',
            level='public',
            numerical_value=50,
            description='Medium level of trust',
            created_by='system',
            default_access_level='read',
            default_anonymization_level='minimal'
        )
        
        # Create test users
        self.admin_user = CustomUser.objects.create_user(
            username='admin@trustawaretest.com',
            email='admin@trustawaretest.com',
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
            username='publisher@trustawaretest.com',
            email='publisher@trustawaretest.com',
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
            username='viewer@trustawaretest.com',
            email='viewer@trustawaretest.com',
            password='TestPassword123',
            first_name='Viewer',
            last_name='User',
            role='viewer',
            organization=self.organization,
            is_active=True,
            is_verified=True
        )
        
        self.inactive_user = CustomUser.objects.create_user(
            username='inactive@trustawaretest.com',
            email='inactive@trustawaretest.com',
            password='TestPassword123',
            first_name='Inactive',
            last_name='User',
            role='viewer',
            organization=self.organization,
            is_active=False,
            is_verified=True
        )
        
        self.service = TrustAwareService()
    
    def test_get_user_dashboard_data_inactive_user(self):
        """Test dashboard data for inactive user"""
        dashboard_data = self.service.get_user_dashboard_data(self.inactive_user)
        
        self.assertIn('error', dashboard_data)
        self.assertEqual(dashboard_data['error'], 'User account is not active')
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_get_user_dashboard_data_active_user(self, mock_access_control):
        """Test dashboard data for active user"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.get_user_permissions.return_value = ['permission1', 'permission2']
        mock_access_control_instance.get_accessible_organizations.return_value = [self.organization, self.target_organization]
        mock_access_control.return_value = mock_access_control_instance
        
        service = TrustAwareService()
        dashboard_data = service.get_user_dashboard_data(self.publisher_user)
        
        self.assertIn('user_info', dashboard_data)
        self.assertIn('accessible_organizations', dashboard_data)
        self.assertIn('trust_relationships', dashboard_data)
        self.assertIn('trust_groups', dashboard_data)
        
        user_info = dashboard_data['user_info']
        self.assertEqual(user_info['username'], 'publisher@trustawaretest.com')
        self.assertEqual(user_info['role'], 'publisher')
        self.assertTrue(user_info['is_publisher'])
        
        self.assertEqual(len(dashboard_data['accessible_organizations']), 2)
    
    def test_get_user_dashboard_data_no_organization(self):
        """Test dashboard data for user without organization"""
        user_no_org = CustomUser.objects.create_user(
            username='noorg@test.com',
            email='noorg@test.com',
            password='TestPassword123',
            first_name='No',
            last_name='Org',
            role='viewer',
            organization=None,
            is_active=True
        )
        
        dashboard_data = self.service.get_user_dashboard_data(user_no_org)
        
        self.assertIsNone(dashboard_data['user_info']['organization'])
    
    def test_get_org_access_level_own_org(self):
        """Test organization access level for own organization"""
        access_level = self.service._get_org_access_level(self.publisher_user, self.organization)
        self.assertEqual(access_level, 'full')
    
    def test_get_org_access_level_admin(self):
        """Test organization access level for admin user"""
        access_level = self.service._get_org_access_level(self.admin_user, self.target_organization)
        self.assertEqual(access_level, 'administrative')
    
    def test_get_org_access_level_with_trust_relationship(self):
        """Test organization access level with trust relationship"""
        # Create trust relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.target_organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            created_by=self.admin_user
        )
        
        with patch('core.trust.models.TrustRelationship.objects.filter') as mock_filter:
            mock_queryset = Mock()
            mock_queryset.select_related.return_value.first.return_value = relationship
            mock_filter.return_value = mock_queryset
            
            with patch.object(relationship, 'get_effective_access_level', return_value='limited'):
                access_level = self.service._get_org_access_level(self.publisher_user, self.target_organization)
                self.assertEqual(access_level, 'limited')
    
    def test_get_org_access_level_no_relationship(self):
        """Test organization access level with no relationship"""
        access_level = self.service._get_org_access_level(self.publisher_user, self.target_organization)
        self.assertEqual(access_level, 'none')
    
    def test_get_org_access_level_exception_handling(self):
        """Test organization access level with exception during relationship check"""
        with patch('core.user_management.services.trust_aware_service.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            access_level = self.service._get_org_access_level(self.publisher_user, self.target_organization)
            self.assertEqual(access_level, 'none')
    
    def test_get_user_trust_relationships(self):
        """Test getting user trust relationships"""
        # Create outgoing relationship
        outgoing_rel = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.target_organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            created_by=self.admin_user
        )
        
        # Create incoming relationship
        incoming_rel = TrustRelationship.objects.create(
            source_organization=self.third_organization,
            target_organization=self.organization,
            trust_level=self.medium_trust_level,
            relationship_type='bilateral',
            status='pending',
            is_active=True,
            created_by=self.admin_user
        )
        
        def mock_filter(**kwargs):
            mock_queryset = Mock()
            if 'source_organization' in kwargs:
                # Outgoing relationships query
                mock_queryset.select_related.return_value = [outgoing_rel]
            elif 'target_organization' in kwargs:
                # Incoming relationships query
                mock_queryset.select_related.return_value = [incoming_rel]
            else:
                mock_queryset.select_related.return_value = []
            return mock_queryset
            
        with patch('core.trust.models.TrustRelationship.objects.filter', side_effect=mock_filter):
            with patch.object(outgoing_rel, 'get_effective_access_level', return_value='full'):
                with patch.object(outgoing_rel, 'get_effective_anonymization_level', return_value='none'):
                    with patch.object(incoming_rel, 'get_effective_access_level', return_value='limited'):
                        with patch.object(incoming_rel, 'get_effective_anonymization_level', return_value='minimal'):
                            relationships = self.service._get_user_trust_relationships(self.publisher_user)
        
        self.assertEqual(len(relationships), 2)
        
        outgoing = next(r for r in relationships if r['type'] == 'outgoing')
        incoming = next(r for r in relationships if r['type'] == 'incoming')
        
        self.assertEqual(outgoing['partner_organization']['name'], 'Target Test Org')
        self.assertEqual(outgoing['trust_level'], 'High Trust')
        self.assertEqual(outgoing['status'], 'active')
        
        self.assertEqual(incoming['partner_organization']['name'], 'Third Test Org')
        self.assertEqual(incoming['trust_level'], 'Medium Trust')
        self.assertEqual(incoming['status'], 'pending')
    
    def test_get_user_trust_relationships_no_organization(self):
        """Test getting trust relationships for user without organization"""
        user_no_org = CustomUser.objects.create_user(
            username='noorg2@test.com',
            email='noorg2@test.com',
            password='TestPassword123',
            organization=None
        )
        
        relationships = self.service._get_user_trust_relationships(user_no_org)
        self.assertEqual(len(relationships), 0)
    
    def test_get_user_trust_relationships_exception_handling(self):
        """Test trust relationships with exception handling"""
        with patch('core.user_management.services.trust_aware_service.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            relationships = self.service._get_user_trust_relationships(self.publisher_user)
            self.assertEqual(len(relationships), 0)
    
    def test_get_user_trust_groups(self):
        """Test getting user trust groups"""
        # Create trust group
        trust_group = TrustGroup.objects.create(
            name='Test Trust Group',
            description='Test group',
            default_trust_level=self.high_trust_level,
            group_type='community',
            is_public=True,
            created_by=self.admin_user
        )
        
        # Create membership
        membership = TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.organization,
            membership_type='member',
            is_active=True
        )
        
        with patch('core.trust.models.TrustGroup.get_member_count', return_value=5):
            groups = self.service._get_user_trust_groups(self.publisher_user)
        
        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEqual(group['name'], 'Test Trust Group')
        self.assertEqual(group['membership_type'], 'member')
        self.assertEqual(group['member_count'], 5)
        self.assertTrue(group['is_public'])
    
    def test_get_user_trust_groups_no_organization(self):
        """Test getting trust groups for user without organization"""
        user_no_org = CustomUser.objects.create_user(
            username='noorg3@test.com',
            email='noorg3@test.com',
            password='TestPassword123',
            organization=None
        )
        
        groups = self.service._get_user_trust_groups(user_no_org)
        self.assertEqual(len(groups), 0)
    
    def test_get_user_trust_groups_exception_handling(self):
        """Test trust groups with exception handling"""
        with patch('core.trust.models.TrustGroupMembership.objects.filter', side_effect=Exception('DB Error')):
            groups = self.service._get_user_trust_groups(self.publisher_user)
            self.assertEqual(len(groups), 0)
    
    def test_get_pending_trust_actions(self):
        """Test getting pending trust actions"""
        # Create pending trust relationship
        pending_rel = TrustRelationship.objects.create(
            source_organization=self.target_organization,
            target_organization=self.organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='pending',
            approved_by_target=False,
            created_by=self.admin_user
        )
        
        pending_actions = self.service._get_pending_trust_actions(self.publisher_user)
        
        self.assertEqual(len(pending_actions), 1)
        action = pending_actions[0]
        self.assertEqual(action['type'], 'trust_approval')
        self.assertIn('Target Test Org', action['title'])
        self.assertEqual(action['priority'], 'medium')
        self.assertEqual(action['action_required'], 'approve_or_deny')
    
    def test_get_pending_trust_actions_no_organization(self):
        """Test getting pending actions for user without organization"""
        user_no_org = CustomUser.objects.create_user(
            username='noorg4@test.com',
            email='noorg4@test.com',
            password='TestPassword123',
            organization=None
        )
        
        pending_actions = self.service._get_pending_trust_actions(user_no_org)
        self.assertEqual(len(pending_actions), 0)
    
    def test_get_pending_trust_actions_exception_handling(self):
        """Test pending actions with exception handling"""
        with patch('core.user_management.services.trust_aware_service.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            pending_actions = self.service._get_pending_trust_actions(self.publisher_user)
            self.assertEqual(len(pending_actions), 0)
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_create_trust_relationship_success(self, mock_access_control):
        """Test successful trust relationship creation"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.require_permission.return_value = None
        mock_access_control.return_value = mock_access_control_instance
        
        service = TrustAwareService()
        
        relationship = service.create_trust_relationship(
            requesting_user=self.publisher_user,
            target_organization=self.target_organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            notes='Test relationship'
        )
        
        self.assertEqual(relationship.source_organization, self.organization)
        self.assertEqual(relationship.target_organization, self.target_organization)
        self.assertEqual(relationship.trust_level, self.high_trust_level)
        self.assertEqual(relationship.relationship_type, 'bilateral')
        self.assertEqual(relationship.notes, 'Test relationship')
        self.assertEqual(relationship.status, 'pending')
    
    def test_create_trust_relationship_same_organization(self):
        """Test trust relationship creation with same organization"""
        with self.assertRaises(ValueError) as context:
            self.service.create_trust_relationship(
                requesting_user=self.publisher_user,
                target_organization=self.organization,
                trust_level=self.high_trust_level
            )
        
        self.assertIn('Cannot create trust relationship with own organization', str(context.exception))
    
    def test_create_trust_relationship_already_exists(self):
        """Test trust relationship creation when relationship already exists"""
        # Create existing relationship
        TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.target_organization,
            trust_level=self.medium_trust_level,
            relationship_type='bilateral',
            status='active',
            created_by=self.admin_user
        )
        
        with self.assertRaises(ValueError) as context:
            self.service.create_trust_relationship(
                requesting_user=self.publisher_user,
                target_organization=self.target_organization,
                trust_level=self.high_trust_level
            )
        
        self.assertIn('Trust relationship already exists', str(context.exception))
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_approve_trust_relationship_success(self, mock_access_control):
        """Test successful trust relationship approval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.require_permission.return_value = None
        mock_access_control.return_value = mock_access_control_instance
        
        # Create pending relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.target_organization,
            target_organization=self.organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='pending',
            created_by=self.admin_user
        )
        
        service = TrustAwareService()
        
        with patch.object(relationship, 'approve') as mock_approve, \
             patch('core.trust.models.TrustRelationship.objects.get', return_value=relationship):
            updated_relationship = service.approve_trust_relationship(
                approving_user=self.publisher_user,
                relationship_id=str(relationship.id),
                approve=True,
                reason='Approved for testing'
            )
            
            mock_approve.assert_called_once_with(self.organization, self.publisher_user)
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_approve_trust_relationship_deny(self, mock_access_control):
        """Test trust relationship denial"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.require_permission.return_value = None
        mock_access_control.return_value = mock_access_control_instance
        
        # Create pending relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.target_organization,
            target_organization=self.organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='pending',
            created_by=self.admin_user
        )
        
        service = TrustAwareService()
        
        with patch.object(relationship, 'deny') as mock_deny, \
             patch('core.trust.models.TrustRelationship.objects.get', return_value=relationship):
            service.approve_trust_relationship(
                approving_user=self.publisher_user,
                relationship_id=str(relationship.id),
                approve=False,
                reason='Not suitable'
            )
            
            mock_deny.assert_called_once_with(self.organization, self.publisher_user, 'Not suitable')
    
    def test_approve_trust_relationship_not_found(self):
        """Test approval of non-existent trust relationship"""
        with self.assertRaises(ValueError) as context:
            self.service.approve_trust_relationship(
                approving_user=self.publisher_user,
                relationship_id='00000000-0000-0000-0000-000000000000',
                approve=True
            )
        
        self.assertIn('Trust relationship not found', str(context.exception))
    
    def test_approve_trust_relationship_wrong_organization(self):
        """Test approval by user from wrong organization"""
        # Create relationship targeting different organization
        relationship = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.target_organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='pending',
            created_by=self.admin_user
        )
        
        with self.assertRaises(PermissionDenied):
            self.service.approve_trust_relationship(
                approving_user=self.publisher_user,  # User from source org, not target
                relationship_id=str(relationship.id),
                approve=True
            )
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_get_threat_intelligence_access_allowed(self, mock_access_control):
        """Test threat intelligence access when allowed"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.get_trust_aware_data_access.return_value = {
            'can_access': True,
            'access_level': 'full',
            'anonymization_level': 'none',
            'restrictions': []
        }
        mock_access_control.return_value = mock_access_control_instance
        
        threat_data = {
            'ip_addresses': ['192.168.1.100', '10.0.0.1'],
            'email_addresses': ['threat@example.com'],
            'organization_id': 'org123',
            'timestamp': '2023-01-01T12:00:00Z'
        }
        
        service = TrustAwareService()
        access_info = service.get_threat_intelligence_access(
            user=self.publisher_user,
            source_organization=self.target_organization,
            threat_data=threat_data
        )
        
        self.assertTrue(access_info['can_access'])
        self.assertIn('data', access_info)
        self.assertIn('trust_metadata', access_info)
        self.assertEqual(access_info['data'], threat_data)  # No anonymization
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_get_threat_intelligence_access_denied(self, mock_access_control):
        """Test threat intelligence access when denied"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.get_trust_aware_data_access.return_value = {
            'can_access': False
        }
        mock_access_control.return_value = mock_access_control_instance
        
        service = TrustAwareService()
        access_info = service.get_threat_intelligence_access(
            user=self.viewer_user,
            source_organization=self.target_organization,
            threat_data={}
        )
        
        self.assertFalse(access_info['can_access'])
        self.assertIn('message', access_info)
        self.assertEqual(access_info['message'], 'Access denied based on trust relationships')
    
    def test_apply_anonymization_none(self):
        """Test anonymization with none level"""
        data = {
            'ip_addresses': ['192.168.1.100'],
            'email_addresses': ['user@example.com'],
            'organization_id': 'org123'
        }
        
        anonymized = self.service._apply_anonymization(data, 'none')
        self.assertEqual(anonymized, data)
    
    def test_apply_anonymization_minimal(self):
        """Test anonymization with minimal level"""
        data = {
            'ip_addresses': ['192.168.1.100', '10.0.0.1'],
            'email_addresses': ['user@example.com', 'admin@test.org'],
            'organization_id': 'org123',
            'timestamp': '2023-01-01T12:00:00Z'
        }
        
        anonymized = self.service._apply_anonymization(data, 'minimal')
        
        self.assertEqual(anonymized['ip_addresses'], ['192.168.1.XXX', '10.0.0.XXX'])
        self.assertEqual(anonymized['email_addresses'], ['us***@example.com', 'ad***@test.org'])
        self.assertEqual(anonymized['organization_id'], 'org123')  # Not removed at minimal level
    
    def test_apply_anonymization_partial(self):
        """Test anonymization with partial level"""
        data = {
            'ip_addresses': ['192.168.1.100'],
            'email_addresses': ['user@example.com'],
            'organization_id': 'org123',
            'internal_reference': 'ref456',
            'timestamp': '2023-01-01T12:00:00Z'
        }
        
        anonymized = self.service._apply_anonymization(data, 'partial')
        
        self.assertEqual(anonymized['ip_addresses'], ['192.168.1.XXX'])
        self.assertEqual(anonymized['email_addresses'], ['us***@example.com'])
        self.assertNotIn('organization_id', anonymized)
        self.assertNotIn('internal_reference', anonymized)
        self.assertEqual(anonymized['timestamp'], '2023-01-01')  # Generalized
    
    def test_apply_anonymization_full(self):
        """Test anonymization with full level"""
        data = {
            'ip_addresses': ['192.168.1.100'],
            'email_addresses': ['user@example.com'],
            'organization_id': 'org123',
            'internal_reference': 'ref456',
            'user_id': 'user789',
            'source_system': 'internal',
            'detailed_context': 'sensitive info',
            'timestamp': '2023-01-01T12:00:00Z'
        }
        
        anonymized = self.service._apply_anonymization(data, 'full')
        
        self.assertEqual(anonymized['ip_addresses'], ['192.168.1.XXX'])
        self.assertEqual(anonymized['email_addresses'], ['us***@example.com'])
        self.assertNotIn('organization_id', anonymized)
        self.assertNotIn('internal_reference', anonymized)
        self.assertNotIn('user_id', anonymized)
        self.assertNotIn('source_system', anonymized)
        self.assertNotIn('detailed_context', anonymized)
    
    def test_anonymize_ip_ipv4(self):
        """Test IPv4 anonymization"""
        anonymized = self.service._anonymize_ip('192.168.1.100')
        self.assertEqual(anonymized, '192.168.1.XXX')
    
    def test_anonymize_ip_invalid(self):
        """Test invalid IP anonymization"""
        anonymized = self.service._anonymize_ip('invalid-ip')
        self.assertEqual(anonymized, 'XXX.XXX.XXX.XXX')
    
    def test_anonymize_email_valid(self):
        """Test valid email anonymization"""
        anonymized = self.service._anonymize_email('user@example.com')
        self.assertEqual(anonymized, 'us***@example.com')
    
    def test_anonymize_email_invalid(self):
        """Test invalid email anonymization"""
        anonymized = self.service._anonymize_email('invalid-email')
        self.assertEqual(anonymized, '***@***.***')
    
    def test_generalize_timestamp_valid(self):
        """Test valid timestamp generalization"""
        generalized = self.service._generalize_timestamp('2023-01-01T12:30:45Z')
        self.assertEqual(generalized, '2023-01-01')
    
    def test_generalize_timestamp_invalid(self):
        """Test invalid timestamp generalization"""
        invalid_timestamp = 'invalid-date'
        generalized = self.service._generalize_timestamp(invalid_timestamp)
        self.assertEqual(generalized, invalid_timestamp)  # Returns original if parsing fails
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_validate_organization_access(self, mock_access_control):
        """Test organization access validation"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.get_accessible_organizations.return_value = [
            self.organization, self.target_organization
        ]
        mock_access_control.return_value = mock_access_control_instance
        
        service = TrustAwareService()
        org_ids = [str(self.organization.id), str(self.target_organization.id), str(self.third_organization.id)]
        
        access_map = service.validate_organization_access(self.publisher_user, org_ids)
        
        self.assertTrue(access_map[str(self.organization.id)])
        self.assertTrue(access_map[str(self.target_organization.id)])
        self.assertFalse(access_map[str(self.third_organization.id)])
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_get_organization_trust_metrics(self, mock_access_control):
        """Test organization trust metrics retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.require_permission.return_value = None
        mock_access_control.return_value = mock_access_control_instance
        
        # Create trust relationships
        active_rel = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.target_organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            created_by=self.admin_user
        )
        
        pending_rel = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.third_organization,
            trust_level=self.medium_trust_level,
            relationship_type='bilateral',
            status='pending',
            created_by=self.admin_user
        )
        
        # Create trust group membership
        trust_group = TrustGroup.objects.create(
            name='Metrics Test Group',
            description='Test group',
            default_trust_level=self.high_trust_level,
            group_type='community',
            is_public=True,
            created_by=self.admin_user
        )
        
        membership = TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.organization,
            membership_type='administrator',
            is_active=True
        )
        
        service = TrustAwareService()
        
        with patch.object(active_rel, 'get_effective_access_level', return_value='full'):
            with patch.object(pending_rel, 'get_effective_access_level', return_value='read'):
                metrics = service.get_organization_trust_metrics(self.publisher_user)
        
        self.assertIn('organization', metrics)
        self.assertIn('trust_relationships', metrics)
        self.assertIn('trust_groups', metrics)
        self.assertIn('data_sharing', metrics)
        
        trust_rels = metrics['trust_relationships']
        self.assertEqual(trust_rels['total'], 2)
        self.assertEqual(trust_rels['active'], 1)
        self.assertEqual(trust_rels['pending'], 1)
        self.assertEqual(trust_rels['by_trust_level']['High Trust'], 1)
        self.assertEqual(trust_rels['by_trust_level']['Medium Trust'], 1)
        self.assertEqual(trust_rels['by_access_level']['full'], 1)
        self.assertEqual(trust_rels['by_access_level']['read'], 1)
        
        trust_groups = metrics['trust_groups']
        self.assertEqual(trust_groups['member_of'], 1)
        self.assertEqual(trust_groups['administering'], 1)
    
    def test_get_organization_trust_metrics_exception_handling(self):
        """Test trust metrics with exception handling"""
        with patch('core.user_management.services.trust_aware_service.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            metrics = self.service.get_organization_trust_metrics(self.publisher_user)
            
            # Should still return basic structure
            self.assertIn('trust_relationships', metrics)
            self.assertEqual(metrics['trust_relationships']['total'], 0)
    
    def test_get_accessible_organizations_with_trust_relationships(self):
        """Test getting accessible organizations through trust relationships"""
        # Create trust relationship
        TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.target_organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            created_by=self.admin_user
        )
        
        accessible = self.service.get_accessible_organizations(self.publisher_user)
        
        org_names = [org.name for org in accessible]
        self.assertIn('Trust Aware Test Org', org_names)  # Own org
        self.assertIn('Target Test Org', org_names)  # Through trust relationship
    
    def test_get_accessible_organizations_through_trust_groups(self):
        """Test getting accessible organizations through trust groups"""
        # Create trust group
        trust_group = TrustGroup.objects.create(
            name='Access Test Group',
            description='Test group',
            default_trust_level=self.high_trust_level,
            group_type='community',
            is_public=True,
            created_by=self.admin_user
        )
        
        # Add both organizations to the group
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.organization,
            membership_type='member',
            is_active=True
        )
        
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.third_organization,
            membership_type='member',
            is_active=True
        )
        
        accessible = self.service.get_accessible_organizations(self.publisher_user)
        
        org_names = [org.name for org in accessible]
        self.assertIn('Trust Aware Test Org', org_names)  # Own org
        self.assertIn('Third Test Org', org_names)  # Through trust group
    
    def test_get_accessible_organizations_no_organization(self):
        """Test getting accessible organizations for user without organization"""
        user_no_org = CustomUser.objects.create_user(
            username='noorg5@test.com',
            email='noorg5@test.com',
            password='TestPassword123',
            organization=None
        )
        
        accessible = self.service.get_accessible_organizations(user_no_org)
        self.assertEqual(len(accessible), 0)
    
    def test_get_accessible_organizations_exception_handling(self):
        """Test accessible organizations with exception handling"""
        with patch('core.user_management.services.trust_aware_service.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            accessible = self.service.get_accessible_organizations(self.publisher_user)
            
            # Should still include own organization
            self.assertEqual(len(accessible), 1)
            self.assertEqual(accessible[0], self.organization)
    
    def test_calculate_trust_score_direct_relationship(self):
        """Test trust score calculation with direct relationship"""
        TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.target_organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            created_by=self.admin_user
        )
        
        score = self.service.calculate_trust_score(self.organization, self.target_organization)
        self.assertEqual(score, 80.0)  # High trust level numerical value
    
    def test_calculate_trust_score_through_trust_group(self):
        """Test trust score calculation through trust groups"""
        # Create trust group with default trust level
        trust_group = TrustGroup.objects.create(
            name='Score Test Group',
            description='Test group',
            default_trust_level=self.medium_trust_level,
            group_type='community',
            is_public=True,
            created_by=self.admin_user
        )
        
        # Add both organizations to the group
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.organization,
            membership_type='member',
            is_active=True
        )
        
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.target_organization,
            membership_type='member',
            is_active=True
        )
        
        score = self.service.calculate_trust_score(self.organization, self.target_organization)
        self.assertEqual(score, 50.0)  # Medium trust level numerical value
    
    def test_calculate_trust_score_no_relationship(self):
        """Test trust score calculation with no relationship"""
        score = self.service.calculate_trust_score(self.organization, self.target_organization)
        self.assertEqual(score, 0.0)
    
    def test_calculate_trust_score_exception_handling(self):
        """Test trust score calculation with exception handling"""
        with patch('core.user_management.services.trust_aware_service.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            score = self.service.calculate_trust_score(self.organization, self.target_organization)
            self.assertEqual(score, 0.0)
    
    @patch('core.user_management.services.trust_aware_service.AccessControlService')
    def test_get_trust_context_success(self, mock_access_control):
        """Test successful trust context retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.get_user_permissions.return_value = ['permission1', 'permission2']
        mock_access_control.return_value = mock_access_control_instance
        
        # Create trust relationship
        TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.target_organization,
            trust_level=self.high_trust_level,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            created_by=self.admin_user,
            access_level='full'
        )
        
        # Create trust group membership
        trust_group = TrustGroup.objects.create(
            name='Context Test Group',
            description='Test group',
            default_trust_level=self.high_trust_level,
            group_type='community',
            is_public=True,
            created_by=self.admin_user
        )
        
        TrustGroupMembership.objects.create(
            trust_group=trust_group,
            organization=self.organization,
            membership_type='administrator',
            is_active=True
        )
        
        service = TrustAwareService()
        
        with patch.object(service, 'get_accessible_organizations', return_value=[self.organization, self.target_organization]):
            context = service.get_trust_context(self.publisher_user)
        
        self.assertIn('user_organization', context)
        self.assertIn('trust_relationships', context)
        self.assertIn('trust_groups', context)
        self.assertIn('accessible_organizations', context)
        self.assertIn('trust_permissions', context)
        
        self.assertEqual(len(context['trust_relationships']), 1)
        self.assertEqual(len(context['trust_groups']), 1)
        self.assertEqual(len(context['accessible_organizations']), 2)
        
        trust_rel = context['trust_relationships'][0]
        self.assertEqual(trust_rel['target_organization'], 'Target Test Org')
        self.assertEqual(trust_rel['trust_level'], 'High Trust')
        self.assertEqual(trust_rel['access_level'], 'full')
        
        trust_group = context['trust_groups'][0]
        self.assertEqual(trust_group['name'], 'Context Test Group')
        self.assertEqual(trust_group['membership_type'], 'administrator')
        self.assertEqual(trust_group['member_count'], 1)
    
    def test_get_trust_context_no_organization(self):
        """Test trust context for user without organization"""
        user_no_org = CustomUser.objects.create_user(
            username='noorg6@test.com',
            email='noorg6@test.com',
            password='TestPassword123',
            organization=None
        )
        
        context = self.service.get_trust_context(user_no_org)
        
        self.assertIsNone(context['user_organization'])
        self.assertEqual(len(context['trust_relationships']), 0)
        self.assertEqual(len(context['trust_groups']), 0)
    
    def test_get_trust_context_exception_handling(self):
        """Test trust context with exception handling"""
        with patch('core.user_management.services.trust_aware_service.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            context = self.service.get_trust_context(self.publisher_user)
            
            self.assertIn('error', context)
            self.assertEqual(context['error'], 'Failed to get trust context')
            self.assertEqual(len(context['trust_relationships']), 0)
            self.assertEqual(len(context['trust_groups']), 0)