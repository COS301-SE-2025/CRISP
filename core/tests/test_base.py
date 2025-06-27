"""
Base test classes for CRISP platform
Provides robust database cleanup and organization management
"""

import uuid
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
import pytest

from ..models import Organization, CustomUser
from ..factories.user_factory import UserFactory

@pytest.mark.django_db
class CrispTestMixin:
    """
    Mixin providing common test utilities and database cleanup
    """
    
    @classmethod
    def create_unique_organization(cls, name_prefix="Test Org", **kwargs):
        """
        Create an organization with guaranteed unique name
        """
        unique_suffix = str(uuid.uuid4())[:8]
        unique_name = f"{name_prefix} {unique_suffix}"
        
        defaults = {
            'name': unique_name,
            'domain': f"test-{unique_suffix}.com",
            'description': f'Test organization for {cls.__name__}'
        }
        defaults.update(kwargs)
        
        return Organization.objects.create(**defaults)
    
    def setUp(self):
        """Enhanced setUp with proper database state management"""
        super().setUp()
        
        # Clear any existing test data to prevent conflicts
        self._cleanup_test_data()
        
        # Create unique organization for this test
        self.organization = self.create_unique_organization()
        
        # Store created objects for cleanup
        self._created_organizations = [self.organization]
        self._created_users = []
    
    def tearDown(self):
        """Robust tearDown ensuring complete cleanup"""
        try:
            # Clean up created objects
            self._cleanup_test_data()
        finally:
            super().tearDown()
    
    def _cleanup_test_data(self):
        """
        Comprehensive cleanup of test data
        """
        # Clean up users first (due to foreign key constraints)
        if hasattr(self, '_created_users'):
            for user in self._created_users:
                try:
                    if hasattr(user, 'delete'):
                        user.delete()
                except Exception:
                    pass
        
        # Clean up organizations
        if hasattr(self, '_created_organizations'):
            for org in self._created_organizations:
                try:
                    if hasattr(org, 'delete'):
                        org.delete()
                except Exception:
                    pass
        
        # Additional cleanup for any remaining test data
        try:
            # Remove any organizations with test-related names
            Organization.objects.filter(
                name__icontains='Test'
            ).delete()
        except Exception:
            pass
    
    def create_test_user(self, role='viewer', username=None, email=None, **kwargs):
        """
        Create a test user with unique credentials
        """
        unique_suffix = str(uuid.uuid4())[:8]
        
        if not username:
            username = f"testuser_{role}_{unique_suffix}"
        if not email:
            email = f"test_{role}_{unique_suffix}@test.com"
        
        user_data = {
            'username': username,
            'email': email,
            'password': f'Complex{role.title()}Pass2024!@#{unique_suffix}',
            'organization': self.organization,
            'is_verified': True,
            **kwargs
        }
        
        user = UserFactory.create_user(role, user_data)
        self._created_users.append(user)
        return user


class CrispTestCase(CrispTestMixin, TestCase):
    """
    Base test case for CRISP platform with robust database management
    """
    pass


@pytest.mark.django_db
class CrispAPITestCase(CrispTestMixin, APITestCase):
    """
    Base API test case for CRISP platform with robust database management
    """
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
    
    def authenticate_user(self, user):
        """Convenience method to authenticate a user"""
        self.client.force_authenticate(user=user)
    
    def create_authenticated_user(self, role='viewer', **kwargs):
        """Create and authenticate a user in one step"""
        user = self.create_test_user(role=role, **kwargs)
        self.authenticate_user(user)
        return user


@pytest.mark.django_db
class CrispTransactionTestCase(CrispTestMixin, TransactionTestCase):
    """
    Transaction test case for tests that need database transaction control
    """
    
    def setUp(self):
        super().setUp()
        # Ensure we start with a clean slate
        with transaction.atomic():
            self._cleanup_test_data()
            self.organization = self.create_unique_organization()
            self._created_organizations = [self.organization]
            self._created_users = []