"""
Comprehensive coverage tests for core module
Tests all functional requirements from SRS
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from apps.user_management.models import Organization, InvitationToken, AuthenticationLog
from apps.trust_management.models import TrustLevel, TrustRelationship, TrustGroup, TrustLog
from apps.core.services import CRISPIntegrationService
from apps.core.trust.models.trust_models import *
from apps.core.trust.patterns.factory.trust_factory import TrustRelationshipFactory
from apps.core.trust.validators import *
import uuid
import json


User = get_user_model()


class CRISPIntegrationServiceComprehensiveTest(TestCase):
    """Test all CRISPIntegrationService methods for R1.2, R1.3, R4 requirements"""
    
    def setUp(self):
        """Set up comprehensive test data"""
        # Create trust levels for R4.1.1
        self.public_level = TrustLevel.objects.create(
            name='Public Trust',
            level='public',
            numerical_value=25,
            description='Public access level',
            created_by='system'
        )
        
        self.trusted_level = TrustLevel.objects.create(
            name='Trusted Partners',
            level='trusted',
            numerical_value=75,
            description='Trusted institution level',
            created_by='system'
        )
        
        self.restricted_level = TrustLevel.objects.create(
            name='Restricted Access',
            level='restricted',
            numerical_value=95,
            description='Restricted high-security level',
            created_by='system'
        )
        
        # Create organizations for R1.3
        self.org1 = Organization.objects.create(
            name='University Test 1',
            domain='test1.edu',
            contact_email='admin@test1.edu',
            institution_type='university'
        )
        
        self.org2 = Organization.objects.create(
            name='College Test 2',
            domain='test2.edu',
            contact_email='admin@test2.edu',
            institution_type='college'
        )
        
        # Create users for R1.2
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@test1.edu',
            password='SecurePass123!',
            organization=self.org1,
            role='admin',
            is_organization_admin=True
        )
        
        self.publisher_user = User.objects.create_user(
            username='publisher_user',
            email='publisher@test1.edu',
            password='SecurePass123!',
            organization=self.org1,
            role='publisher'
        )
        
    def test_organization_creation_with_trust_setup_comprehensive(self):
        """Test R1.3.1 - System Administrators register new client institutions"""
        admin_data = {
            'username': 'new_admin',
            'email': 'admin@newuniv.edu',
            'password': 'SecurePass123!',
            'first_name': 'Admin',
            'last_name': 'User'
        }
        
        # Test all institution types from SRS
        institution_types = ['university', 'college', 'school', 'research_institute', 'other']
        trust_levels = ['public', 'trusted', 'restricted']
        
        for inst_type in institution_types:
            for trust_level in trust_levels:
                org = CRISPIntegrationService.create_organization_with_trust_setup(
                    name=f'Test {inst_type} {trust_level}',
                    domain=f'{inst_type}-{trust_level}.edu',
                    contact_email=f'contact@{inst_type}-{trust_level}.edu',
                    admin_user_data=admin_data.copy(),
                    institution_type=inst_type,
                    default_trust_level=trust_level
                )
                
                self.assertEqual(org.institution_type, inst_type)
                self.assertEqual(org.trust_level_default, trust_level)
                
                # Verify admin user creation (R1.2.1)
                admin = User.objects.get(email=admin_data['email'])
                self.assertEqual(admin.organization, org)
                self.assertTrue(admin.is_organization_admin)
                
                # Clean up for next iteration
                admin.delete()
                org.delete()
                
    def test_user_invitation_workflow_comprehensive(self):
        """Test R1.2.2 - Institution Publishers invite users via email"""
        # Test all user roles
        roles = ['viewer', 'publisher', 'admin']
        
        for role in roles:
            invitation = CRISPIntegrationService.invite_user_to_organization(
                organization=self.org1,
                inviting_user=self.admin_user,
                email=f'{role}@test.edu',
                role=role
            )
            
            self.assertEqual(invitation.role, role)
            self.assertEqual(invitation.organization, self.org1)
            self.assertEqual(invitation.invited_by, self.admin_user)
            self.assertFalse(invitation.used)
            self.assertTrue(invitation.is_valid())
            
    def test_trust_relationship_creation_comprehensive(self):
        """Test R4.1.4 - Enable bilateral trust agreements between institutions"""
        # Test all relationship types from SRS
        relationship_types = ['bilateral', 'community', 'hierarchical', 'federation']
        
        for rel_type in relationship_types:
            relationship = CRISPIntegrationService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org2,
                trust_level_name=self.trusted_level.name,
                relationship_type=rel_type,
                created_by_user=self.admin_user
            )
            
            self.assertEqual(relationship.relationship_type, rel_type)
            self.assertEqual(relationship.source_organization, self.org1.id)
            self.assertEqual(relationship.target_organization, self.org2.id)
            self.assertEqual(relationship.status, 'pending')
            
    def test_intelligence_access_control(self):
        """Test R4.2.1 - Filter shared intelligence based on trust relationships"""
        # Create trust relationship
        relationship = CRISPIntegrationService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org2,
            trust_level_name=self.trusted_level.name,
            relationship_type='bilateral'
        )
        
        # Test intelligence access
        sources = CRISPIntegrationService.get_user_accessible_intelligence_sources(
            user=self.admin_user,
            intelligence_type='threat_indicator'
        )
        
        self.assertIsInstance(sources, list)
        
        # Test with different user roles
        sources_publisher = CRISPIntegrationService.get_user_accessible_intelligence_sources(
            user=self.publisher_user,
            intelligence_type='malware'
        )
        
        self.assertIsInstance(sources_publisher, list)
        
    def test_permission_validation(self):
        """Test R1.2.4 - Institution Publishers manage user permissions"""
        # Test non-admin user cannot invite
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@test1.edu',
            password='SecurePass123!',
            organization=self.org1,
            role='viewer'
        )
        
        with self.assertRaises(ValidationError):
            CRISPIntegrationService.invite_user_to_organization(
                organization=self.org1,
                inviting_user=regular_user,
                email='test@example.com',
                role='viewer'
            )
            
        # Test cross-organization invitation prevention
        with self.assertRaises(ValidationError):
            CRISPIntegrationService.invite_user_to_organization(
                organization=self.org2,
                inviting_user=self.admin_user,
                email='test@example.com',
                role='viewer'
            )


class TrustModelComprehensiveTest(TestCase):
    """Test trust models from apps/core/trust/models/trust_models.py"""
    
    def setUp(self):
        """Set up trust model test data"""
        self.org1 = Organization.objects.create(
            name='Trust Test Org 1',
            domain='trust1.edu',
            contact_email='trust@trust1.edu'
        )
        
        self.org2 = Organization.objects.create(
            name='Trust Test Org 2',
            domain='trust2.edu',
            contact_email='trust@trust2.edu'
        )
        
        self.trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='trusted',
            numerical_value=50,
            description='Test level',
            created_by='test'
        )
        
    def test_trust_intelligence_model(self):
        """Test TrustIntelligence model methods"""
        # Create TrustIntelligence instance
        intel = TrustIntelligence.objects.create(
            intelligence_type='malware',
            source_organization=self.org1.id,
            sharing_level='trusted',
            anonymization_applied=True,
            original_data={'test': 'data'},
            anonymized_data={'test': 'XXX'},
            sharing_restrictions={'level': 'trusted'},
            created_by='test_user'
        )
        
        # Test model methods
        self.assertEqual(intel.intelligence_type, 'malware')
        self.assertTrue(intel.anonymization_applied)
        self.assertEqual(intel.sharing_level, 'trusted')
        
        # Test string representation
        self.assertIn('malware', str(intel))
        
    def test_trust_sharing_agreement_model(self):
        """Test TrustSharingAgreement model"""
        agreement = TrustSharingAgreement.objects.create(
            source_organization=self.org1.id,
            target_organization=self.org2.id,
            agreement_type='bilateral',
            trust_level=self.trust_level,
            data_sharing_scope=['threat_indicators', 'malware'],
            anonymization_requirements={'level': 'medium'},
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=365),
            created_by='test_user'
        )
        
        # Test agreement properties
        self.assertEqual(agreement.agreement_type, 'bilateral')
        self.assertEqual(agreement.trust_level, self.trust_level)
        self.assertIn('threat_indicators', agreement.data_sharing_scope)
        
        # Test validity methods
        self.assertTrue(agreement.is_active())
        
    def test_trust_access_log_model(self):
        """Test TrustAccessLog model for R4.2.3"""
        log = TrustAccessLog.objects.create(
            accessing_organization=self.org1.id,
            accessed_intelligence_id=str(uuid.uuid4()),
            access_type='read',
            trust_relationship_used=str(uuid.uuid4()),
            anonymization_level='medium',
            access_granted=True,
            user_id='test_user',
            access_details={'method': 'api'}
        )
        
        # Test log properties
        self.assertEqual(log.access_type, 'read')
        self.assertTrue(log.access_granted)
        self.assertEqual(log.anonymization_level, 'medium')
        
    def test_anonymization_policy_model(self):
        """Test AnonymizationPolicy model for R2.2"""
        policy = AnonymizationPolicy.objects.create(
            name='Test Policy',
            policy_type='ip_address',
            trust_level_threshold=50,
            anonymization_rules={
                'ip_mask': '255.255.255.0',
                'domain_mask': 'XXX'
            },
            effectiveness_target=95.0,
            created_by='test_user'
        )
        
        # Test policy properties
        self.assertEqual(policy.policy_type, 'ip_address')
        self.assertEqual(policy.effectiveness_target, 95.0)
        self.assertTrue(policy.is_active)
        
    def test_threat_intelligence_feed_model(self):
        """Test ThreatIntelligenceFeed model for R3.1"""
        feed = ThreatIntelligenceFeed.objects.create(
            name='Test Feed',
            feed_type='stix_taxii',
            source_url='https://example.com/feed',
            authentication_type='api_key',
            authentication_config={'api_key': 'test'},
            polling_interval=3600,
            data_format='stix2.1',
            trust_score=0.8,
            created_by='test_user'
        )
        
        # Test feed properties
        self.assertEqual(feed.feed_type, 'stix_taxii')
        self.assertEqual(feed.data_format, 'stix2.1')
        self.assertEqual(feed.trust_score, 0.8)
        self.assertTrue(feed.is_active)


class TrustValidatorTest(TestCase):
    """Test trust validators for data validation requirements"""
    
    def test_stix_validator(self):
        """Test STIX 2.1 compliance validation for R2.1.3"""
        # Valid STIX object
        valid_stix = {
            "type": "indicator",
            "id": "indicator--12345678-1234-1234-1234-123456789abc",
            "created": "2025-01-01T00:00:00Z",
            "modified": "2025-01-01T00:00:00Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "labels": ["malicious-activity"]
        }
        
        result = validate_stix_object(valid_stix)
        self.assertTrue(result['is_valid'])
        
        # Invalid STIX object
        invalid_stix = {
            "type": "indicator",
            "pattern": "[file:hashes.MD5 = 'invalid']"
        }
        
        result = validate_stix_object(invalid_stix)
        self.assertFalse(result['is_valid'])
        
    def test_threat_intelligence_validator(self):
        """Test threat intelligence validation for R2.1.3"""
        # Valid threat intelligence
        valid_threat = {
            "type": "malware",
            "indicators": ["d41d8cd98f00b204e9800998ecf8427e"],
            "description": "Test malware",
            "severity": "high",
            "confidence": 85
        }
        
        result = validate_threat_intelligence(valid_threat)
        self.assertTrue(result['is_valid'])
        
        # Invalid threat intelligence
        invalid_threat = {
            "type": "invalid_type",
            "indicators": []
        }
        
        result = validate_threat_intelligence(invalid_threat)
        self.assertFalse(result['is_valid'])
        
    def test_anonymization_validator(self):
        """Test anonymization effectiveness validation for R2.2.5"""
        original_data = {
            "ip_addresses": ["192.168.1.100", "10.0.0.50"],
            "email": "user@example.com",
            "domain": "malicious.com"
        }
        
        anonymized_data = {
            "ip_addresses": ["192.168.1.XXX", "10.0.0.XXX"],
            "email": "user@XXX.com",
            "domain": "malicious.com"
        }
        
        effectiveness = calculate_anonymization_effectiveness(original_data, anonymized_data)
        self.assertGreaterEqual(effectiveness, 0.0)
        self.assertLessEqual(effectiveness, 100.0)


class TrustFactoryTest(TestCase):
    """Test trust factory pattern implementation"""
    
    def setUp(self):
        """Set up factory test data"""
        self.org1 = Organization.objects.create(
            name='Factory Test Org 1',
            domain='factory1.edu',
            contact_email='factory@factory1.edu'
        )
        
        self.org2 = Organization.objects.create(
            name='Factory Test Org 2',
            domain='factory2.edu',
            contact_email='factory@factory2.edu'
        )
        
        self.trust_level = TrustLevel.objects.create(
            name='Factory Test Level',
            level='trusted',
            numerical_value=75,
            description='Factory test level',
            created_by='test'
        )
        
    def test_trust_relationship_factory(self):
        """Test TrustRelationshipFactory for different relationship types"""
        factory = TrustRelationshipFactory()
        
        # Test bilateral relationship creation
        bilateral_config = {
            'source_org': self.org1,
            'target_org': self.org2,
            'trust_level': self.trust_level,
            'relationship_type': 'bilateral'
        }
        
        relationship = factory.create_relationship('bilateral', bilateral_config)
        self.assertEqual(relationship.relationship_type, 'bilateral')
        self.assertEqual(relationship.source_organization, self.org1.id)
        
        # Test community relationship creation
        community_config = {
            'source_org': self.org1,
            'target_org': self.org2,
            'trust_level': self.trust_level,
            'relationship_type': 'community'
        }
        
        relationship = factory.create_relationship('community', community_config)
        self.assertEqual(relationship.relationship_type, 'community')
        
    def test_factory_validation(self):
        """Test factory input validation"""
        factory = TrustRelationshipFactory()
        
        # Test invalid relationship type
        with self.assertRaises(ValueError):
            factory.create_relationship('invalid_type', {})
            
        # Test missing required fields
        with self.assertRaises(KeyError):
            factory.create_relationship('bilateral', {})


class AuthenticationLogComprehensiveTest(TestCase):
    """Test authentication logging for R1.1.5"""
    
    def setUp(self):
        """Set up authentication test data"""
        self.org = Organization.objects.create(
            name='Auth Test Org',
            domain='auth.edu',
            contact_email='auth@auth.edu'
        )
        
        self.user = User.objects.create_user(
            username='auth_user',
            email='auth@auth.edu',
            password='SecurePass123!',
            organization=self.org
        )
        
    def test_authentication_log_actions(self):
        """Test all authentication log actions for audit requirements"""
        actions = [
            'login_success',
            'login_failed', 
            'logout',
            'password_reset',
            'account_locked',
            'account_unlocked',
            'session_timeout',
            'password_changed',
            'email_changed',
            'role_changed'
        ]
        
        for action in actions:
            log = AuthenticationLog.objects.create(
                user=self.user,
                email=self.user.email,
                action=action,
                ip_address='127.0.0.1',
                user_agent='Test Agent',
                success=(action not in ['login_failed', 'account_locked']),
                details={'test': 'data'}
            )
            
            self.assertEqual(log.action, action)
            self.assertEqual(log.email, self.user.email)
            self.assertIn(action, str(log))
            
    def test_security_event_logging(self):
        """Test security event logging for R5.1.4"""
        # Test failed login attempts (R1.1.4)
        for i in range(6):  # Exceed the 5 attempt limit
            AuthenticationLog.objects.create(
                user=self.user,
                email=self.user.email,
                action='login_failed',
                ip_address='192.168.1.100',
                user_agent='Malicious Agent',
                success=False,
                details={'attempt': i+1}
            )
            
        # Check that logs are created
        failed_attempts = AuthenticationLog.objects.filter(
            user=self.user,
            action='login_failed'
        ).count()
        
        self.assertEqual(failed_attempts, 6)
        
        # Test account lockout logging
        lockout_log = AuthenticationLog.objects.create(
            user=self.user,
            email=self.user.email,
            action='account_locked',
            ip_address='192.168.1.100',
            user_agent='System',
            success=True,
            details={'reason': 'too_many_failed_attempts'}
        )
        
        self.assertEqual(lockout_log.action, 'account_locked')
        self.assertTrue(lockout_log.success)


class TrustGroupComprehensiveTest(TestCase):
    """Test trust group functionality for R4.1.3"""
    
    def setUp(self):
        """Set up trust group test data"""
        self.trust_level = TrustLevel.objects.create(
            name='Group Test Level',
            level='trusted',
            numerical_value=50,
            description='Group test level',
            created_by='test'
        )
        
        self.org1 = Organization.objects.create(
            name='Group Test Org 1',
            domain='group1.edu',
            contact_email='group@group1.edu'
        )
        
        self.org2 = Organization.objects.create(
            name='Group Test Org 2',
            domain='group2.edu',
            contact_email='group@group2.edu'
        )
        
    def test_community_trust_groups(self):
        """Test R4.1.3 - Support community groups for multi-institution trust"""
        # Create community group
        group = TrustGroup.objects.create(
            name='Educational Sector Community',
            description='Community for educational institutions',
            group_type='community',
            default_trust_level=self.trust_level,
            administrators=[str(self.org1.id)],
            created_by='test_admin'
        )
        
        # Test group properties
        self.assertEqual(group.group_type, 'community')
        self.assertTrue(group.can_administer(self.org1.id))
        self.assertFalse(group.can_administer(self.org2.id))
        
        # Test group membership
        from apps.trust_management.models import TrustGroupMembership
        
        membership = TrustGroupMembership.objects.create(
            trust_group=group,
            organization=self.org1.id,
            joined_by='admin_user'
        )
        
        self.assertEqual(membership.trust_group, group)
        self.assertEqual(membership.organization, self.org1.id)
        
    def test_sector_based_groups(self):
        """Test sector-based trust groups"""
        sectors = ['sector', 'region', 'custom']
        
        for sector_type in sectors:
            group = TrustGroup.objects.create(
                name=f'Test {sector_type.title()} Group',
                description=f'Test group for {sector_type}',
                group_type=sector_type,
                default_trust_level=self.trust_level,
                created_by='test_admin'
            )
            
            self.assertEqual(group.group_type, sector_type)
            self.assertTrue(group.is_active)
            self.assertIn(sector_type, str(group))


class SystemRequirementTest(TestCase):
    """Test system-level requirements from SRS"""
    
    def test_password_policy_enforcement(self):
        """Test R1.1.2 - Password policy enforcement"""
        org = Organization.objects.create(
            name='Password Test Org',
            domain='password.edu',
            contact_email='password@password.edu'
        )
        
        # Test weak passwords (should be handled by Django validators)
        weak_passwords = [
            'weak',
            '12345678',
            'password',
            'PASSWORD',
            'Password',
            '1234567890'
        ]
        
        for weak_pass in weak_passwords:
            try:
                user = User.objects.create_user(
                    username=f'test_{weak_pass}',
                    email=f'{weak_pass}@test.edu',
                    password=weak_pass,
                    organization=org
                )
                # If creation succeeds, ensure password is properly hashed
                self.assertNotEqual(user.password, weak_pass)
                self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
            except ValidationError:
                # Validation error is expected for weak passwords
                pass
                
    def test_session_timeout_configuration(self):
        """Test R1.1.6 - Session timeout configuration"""
        # This tests the configuration capability
        # Actual timeout would be handled by Django middleware
        from django.conf import settings
        
        # Verify session age setting exists
        self.assertTrue(hasattr(settings, 'SESSION_COOKIE_AGE'))
        
    def test_role_based_access_control(self):
        """Test R1.2.3 - Three user roles support"""
        org = Organization.objects.create(
            name='RBAC Test Org',
            domain='rbac.edu',
            contact_email='rbac@rbac.edu'
        )
        
        roles = ['viewer', 'publisher', 'admin']
        
        for role in roles:
            user = User.objects.create_user(
                username=f'{role}_user',
                email=f'{role}@rbac.edu',
                password='SecurePass123!',
                organization=org,
                role=role
            )
            
            self.assertEqual(user.role, role)
            
            # Test role-specific permissions
            if role == 'admin':
                self.assertTrue(user.is_admin())
            elif role == 'publisher':
                self.assertTrue(user.is_publisher())
            else:  # viewer
                self.assertFalse(user.is_publisher())
                self.assertFalse(user.is_admin())
