"""
Comprehensive test helpers
"""
import random
import string
import uuid
from functools import wraps


def get_unique_username(prefix="testuser"):
    """Generate a unique username for test users."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{random_suffix}"


def get_unique_collection_alias(prefix="testcol"):
    """Generate a unique alias for test collections."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def get_unique_org_name(prefix="Test Org"):
    """Generate a unique name for test organizations."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix} {random_suffix}"


def get_unique_email(prefix="test"):
    """Generate a unique email address."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{random_suffix}@example.com"


def get_unique_identifier():
    """Generate a unique identifier for test resources."""
    return f"{uuid.uuid4().hex[:8]}_{uuid.uuid4().hex[:8]}"


def get_unique_domain(prefix="test"):
    """Generate a unique domain for institutions."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
    return f"{prefix}-{random_suffix}.edu"


def get_unique_api_key():
    """Generate a unique API key."""
    return f"api_key_{uuid.uuid4().hex}"


def get_unique_stix_id(type_name="indicator"):
    """Generate a unique STIX ID."""
    return f"{type_name}--{uuid.uuid4()}"


def get_unique_taxii_collection_id(prefix="collection"):
    """Generate a unique TAXII collection ID."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def with_unique_test_data(setup_method):
    """
    Decorator for setUp methods to ensure all test data is unique.
    Apply to setUp methods that create User objects, Collections, etc.
    """
    @wraps(setup_method)
    def wrapper(self, *args, **kwargs):
        # Generate unique identifiers and store them on the class
        if not hasattr(self.__class__, '_unique_data'):
            self.__class__._unique_data = {
                'username': get_unique_username(),
                'collection_alias': get_unique_collection_alias(),
                'org_name': get_unique_org_name(),
                'domain': get_unique_domain(),
                'api_key': get_unique_api_key(),
                'email': get_unique_email(),
                'stix_id': get_unique_stix_id(),
                'taxii_collection_id': get_unique_taxii_collection_id()
            }
        
        # Call the original setUp
        setup_method(self, *args, **kwargs)
    
    return wrapper


def generate_unique_test_data():
    """
    Generate a dictionary with unique test data.
    Useful for test classes that need multiple unique values.
    """
    return {
        'username': get_unique_username(),
        'collection_alias': get_unique_collection_alias(),
        'org_name': get_unique_org_name(),
        'domain': get_unique_domain(),
        'api_key': get_unique_api_key(),
        'email': get_unique_email(),
        'stix_id': get_unique_stix_id(),
        'taxii_collection_id': get_unique_taxii_collection_id(),
        'unique_id': get_unique_identifier()
    }


def reset_test_database():
    """
    Helper function to manually reset test database state.
    Can be called from tearDown methods if needed.
    """
    from django.db import connections
    
    # Get the test database connection
    connection = connections['default']
    
    # Create a cursor
    with connection.cursor() as cursor:
        # Delete test data from critical tables to avoid constraints
        cursor.execute("DELETE FROM core_collection WHERE title LIKE 'Test%'")
        cursor.execute("DELETE FROM auth_user WHERE username LIKE 'testuser_%'")
        cursor.execute("DELETE FROM core_organization WHERE name LIKE 'Test%'")
        cursor.execute("DELETE FROM core_institution WHERE name LIKE 'Test%'")
        cursor.execute("DELETE FROM core_threatfeed WHERE name LIKE 'Test%'")