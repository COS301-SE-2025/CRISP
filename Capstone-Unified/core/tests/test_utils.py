"""
Test utilities for proper test isolation
"""
import uuid
from django.contrib.auth import get_user_model
from core.tests.test_config import TEST_USER_PASSWORD

User = get_user_model()
from core.models.models import Organization, Collection, STIXObject

class TestDataManager:
    """
    Manages test data creation with unique identifiers
    """
    
    def __init__(self):
        self.test_id = str(uuid.uuid4())[:8]
        self.created_objects = []
    
    def create_unique_user(self, base_name="testuser"):
        """Create a user with unique username and email"""
        unique_name = f"{base_name}_{self.test_id}_{len(self.created_objects)}"
        user = User.objects.create_user(
            username=unique_name,
            email=f"{unique_name}@example.com",
            password=TEST_USER_PASSWORD
        )
        self.created_objects.append(user)
        return user
    
    def create_unique_organization(self, user, base_name="Test Org"):
        """Create an organization with unique name and email"""
        unique_suffix = f"{self.test_id}_{len(self.created_objects)}"
        org = Organization.objects.create(
            name=f"{base_name} {unique_suffix}",
            description="Test organization",
            identity_class="organization",
            sectors=["education"],
            contact_email=f"contact_{unique_suffix}@testorg.edu",
            created_by=user
        )
        self.created_objects.append(org)
        return org
    
    def create_unique_collection(self, owner, base_title="Test Collection"):
        """Create a collection with unique title and alias"""
        unique_suffix = f"{self.test_id}_{len(self.created_objects)}"
        collection = Collection.objects.create(
            title=f"{base_title} {unique_suffix}",
            description="Test collection",
            alias=f"test-collection-{unique_suffix}",
            owner=owner,
            can_read=True,
            can_write=True
        )
        self.created_objects.append(collection)
        return collection
    
    def cleanup(self):
        """Clean up all created test objects"""
        for obj in reversed(self.created_objects):
            try:
                obj.delete()
            except:
                pass
        self.created_objects.clear() 