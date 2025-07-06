"""
Test fixtures for CRISP Trust Management Tests

Provides reusable test data setup to fix model instance issues across all test files.
"""

import uuid
from django.test import TestCase
from core.user_management.models import Organization, CustomUser
from core.trust.models import TrustLevel


class BaseTestCase(TestCase):
    """Base test case with common fixtures for all trust management tests"""
    
    def setUp(self):
        """Set up common test data"""
        # Create organizations FIRST (they are referenced by other models)
        self.source_org = Organization.objects.create(
            name='Source Organization',
            domain='source.edu',
            contact_email='contact@source.edu',
            description='Source organization for testing'
        )
        
        self.target_org = Organization.objects.create(
            name='Target Organization',
            domain='target.edu', 
            contact_email='contact@target.edu',
            description='Target organization for testing'
        )
        
        self.test_org = Organization.objects.create(
            name='Test Organization',
            domain='test.edu',
            contact_email='contact@test.edu',
            description='General test organization'
        )
        
        # Additional organizations for comprehensive testing
        self.org1 = self.source_org  # Alias for backward compatibility
        self.org2 = self.target_org  # Alias for backward compatibility
        
        # Create users SECOND (they reference organizations)
        self.admin_user = CustomUser.objects.create_user(
            username='admin_user',
            email='admin@source.edu',
            organization=self.source_org,
            password='testpass123',
            role='BlueVisionAdmin',
            is_staff=True,
            is_verified=True
        )
        
        self.publisher_user = CustomUser.objects.create_user(
            username='publisher_user',
            email='publisher@source.edu',
            organization=self.source_org,
            password='testpass123',
            role='publisher',
            is_publisher=True,
            is_verified=True
        )
        
        self.viewer_user = CustomUser.objects.create_user(
            username='viewer_user',
            email='viewer@target.edu',
            organization=self.target_org,
            password='testpass123',
            role='viewer',
            is_verified=True
        )
        
        self.test_user = CustomUser.objects.create_user(
            username='test_user',
            email='test@test.edu',
            organization=self.test_org,
            password='testpass123',
            role='publisher',
            is_verified=True
        )
        
        # Alias for backward compatibility
        self.user = self.admin_user
        
        # Create trust levels THIRD (they reference users)
        self.high_trust = TrustLevel.objects.create(
            name='High Trust',
            level='trusted',
            numerical_value=80,
            description='High trust level for testing',
            default_anonymization_level='none',
            default_access_level='full',
            created_by=f'user_{self.admin_user.username}'
        )
        
        self.medium_trust = TrustLevel.objects.create(
            name='Medium Trust',
            level='public', 
            numerical_value=50,
            description='Medium trust level for testing',
            default_anonymization_level='partial',
            default_access_level='read',
            created_by=f'user_{self.admin_user.username}'
        )
        
        self.low_trust = TrustLevel.objects.create(
            name='Low Trust',
            level='restricted',
            numerical_value=20,
            description='Low trust level for testing',
            default_anonymization_level='full',
            default_access_level='none',
            created_by=f'user_{self.admin_user.username}'
        )
        
        # Default trust level for backward compatibility
        self.trust_level = self.high_trust


def create_test_organization(name_suffix="", **kwargs):
    """Helper function to create test organizations"""
    unique_suffix = str(uuid.uuid4())[:8] if not name_suffix else name_suffix
    defaults = {
        'name': f'Test Org {unique_suffix}',
        'domain': f'test{unique_suffix}.edu'.lower().replace('-', ''),
        'contact_email': f'contact@test{unique_suffix}.edu'.lower().replace('-', ''),
        'description': f'Test organization {unique_suffix}'
    }
    defaults.update(kwargs)
    return Organization.objects.create(**defaults)


def create_test_user(organization, username_suffix="", role='viewer', **kwargs):
    """Helper function to create test users"""
    unique_suffix = str(uuid.uuid4())[:8] if not username_suffix else username_suffix
    username = f'testuser{unique_suffix}'.replace('-', '')
    email = f'{username}@{organization.domain}'
    
    defaults = {
        'username': username,
        'email': email,
        'organization': organization,  # IMPORTANT: Pass the actual Organization instance
        'password': 'testpass123',
        'role': role,
        'is_verified': True
    }
    defaults.update(kwargs)
    return CustomUser.objects.create_user(**defaults)


def create_test_trust_level(created_by, name_suffix="", **kwargs):
    """Helper function to create test trust levels"""
    unique_suffix = str(uuid.uuid4())[:8] if not name_suffix else name_suffix
    defaults = {
        'name': f'Test Trust Level {unique_suffix}',
        'level': 'public',
        'numerical_value': 50,
        'description': f'Test trust level {unique_suffix}',
        'default_anonymization_level': 'partial',
        'default_access_level': 'read',
        'created_by': f'user_{created_by.username}'  # Convert user to string representation
    }
    defaults.update(kwargs)
    return TrustLevel.objects.create(**defaults)