import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model  # Use this instead
from sqlite3 import IntegrityError
import random
from core.models.models import (
    Organization, Institution, ThreatFeed, Indicator, TTPData, 
    Collection, STIXObject, CollectionObject
)

# Get the correct user model
User = get_user_model()

def create_test_user(base_name='testuser', unique=True):
    """Create a test user with unique username and email."""
    if unique:
        unique_suffix = str(uuid.uuid4())[:8]
        username = f'{base_name}_{unique_suffix}'
        email = f'{base_name}_{unique_suffix}@example.com'
    else:
        username = base_name
        email = f'{base_name}@example.com'
    
    return User.objects.create_user(
        username=username,
        email=email,
        password='testpass123'
    )


def create_test_organization(name_suffix="", unique=True, created_by=None):
    """Create a test organization with all required fields."""
    if unique:
        unique_id = str(uuid.uuid4())[:8]
        name_suffix = f"{name_suffix}_{unique_id}" if name_suffix else unique_id
    
    if created_by is None:
        created_by = create_test_user(unique=unique)
    
    return Organization.objects.create(
        name=f"Test Organization {name_suffix}",
        description="Test Organization",
        identity_class="organization",
        organization_type="university",
        contact_email=f"test_{name_suffix}@example.com" if name_suffix else "test@example.com",
        created_by=created_by
    )


def create_test_institution(organization=None, name_suffix="", unique=True):
    """Create a test institution with all required fields."""
    if organization is None:
        organization = create_test_organization(name_suffix, unique=unique)
    
    if unique:
        unique_id = str(uuid.uuid4())[:8]
        name_suffix = f"{name_suffix}_{unique_id}" if name_suffix else unique_id
    
    return Institution.objects.create(
        name=f"Test Institution {name_suffix}",
        description="Test Institution",
        contact_email=f"test_{name_suffix}@example.com" if name_suffix else "test@example.com",
        contact_name="Test Contact",
        organization=organization
    )


def create_test_collection(owner=None, alias_suffix="", unique=True, **kwargs):
    """Create a test collection with unique alias."""
    if owner is None:
        owner = create_test_organization(unique=unique)
    
    if unique:
        unique_id = str(uuid.uuid4())[:8]
        alias_suffix = f"{alias_suffix}_{unique_id}" if alias_suffix else unique_id
    
    defaults = {
        'title': f'Test Collection {alias_suffix}',
        'description': 'Test collection',
        'alias': f'test-collection-{alias_suffix}',
        'owner': owner,
        'can_read': True,
        'can_write': True,
        'default_anonymization_level': 'medium'
    }
    
    defaults.update(kwargs)
    
    return Collection.objects.create(**defaults)


def create_test_stix_object(source_organization=None, created_by=None, unique=True, **kwargs):
    """Create a test STIX object with unique ID."""
    if source_organization is None:
        source_organization = create_test_organization(unique=unique)
    
    if created_by is None:
        created_by = create_test_user(unique=unique)
    
    if unique:
        stix_id = f"indicator--{uuid.uuid4()}"
    else:
        stix_id = "indicator--test-12345"
    
    stix_data = {
        'type': 'indicator',
        'id': stix_id,
        'spec_version': '2.1',
        'pattern': "[domain-name:value = 'test.example.com']",
        'labels': ['malicious-activity'],
        'created': timezone.now().isoformat(),
        'modified': timezone.now().isoformat(),
    }
    
    if 'stix_data' in kwargs:
        stix_data.update(kwargs.pop('stix_data'))
    
    defaults = {
        'stix_id': stix_id,
        'stix_type': 'indicator',
        'created': timezone.now(),
        'modified': timezone.now(),
        'raw_data': stix_data,
        'source_organization': source_organization,
        'created_by': created_by
    }
    
    defaults.update(kwargs)
    
    return STIXObject.objects.create(**defaults)


def create_test_threat_feed(owner=None, name_suffix="", unique=True, **kwargs):
    """Create a test threat feed with all required fields."""
    if owner is None:
        owner = create_test_organization(unique=unique)
    
    if unique:
        unique_id = str(uuid.uuid4())[:8]
        name_suffix = f"{name_suffix}_{unique_id}" if name_suffix else unique_id
    
    defaults = {
        'name': f"Test Feed {name_suffix}",
        'description': "Test threat feed",
        'owner': owner,
        'is_external': True,
        'is_active': True,
        'last_sync': timezone.now(),
        'taxii_server_url': kwargs.get('taxii_server_url', 'https://example.com/taxii'),
        'taxii_collection_id': kwargs.get('taxii_collection_id', f'default-collection-{name_suffix}'),
        'taxii_api_root': kwargs.get('taxii_api_root', 'api'),
        'is_public': kwargs.get('is_public', False)
    }

    valid_fields = [
        'name', 'description', 'owner', 'is_external', 'is_active', 
        'last_sync', 'taxii_server_url', 'taxii_collection_id', 'is_public',
        'taxii_api_root', 'taxii_username', 'taxii_password', 'sync_interval_hours'
    ]
    
    for key, value in kwargs.items():
        if key in valid_fields:
            defaults[key] = value
    
    return ThreatFeed.objects.create(**defaults)


def create_test_indicator(threat_feed=None, unique=True, **kwargs):
    """Create a test indicator with all required fields."""
    if threat_feed is None:
        threat_feed = create_test_threat_feed(unique=unique)
    
    if unique:
        stix_id = f"indicator--{uuid.uuid4()}"
        value = f"192.168.1.{uuid.uuid4().int % 255}"
    else:
        stix_id = "indicator--test-indicator"
        value = "192.168.1.100"
    
    defaults = {
        'threat_feed': threat_feed,
        'value': value,
        'type': 'ip',
        'confidence': 75,
        'stix_id': stix_id,
        'first_seen': timezone.now(),
        'last_seen': timezone.now()
    }
    
    defaults.update(kwargs)
    
    return Indicator.objects.create(**defaults)


def create_test_ttp(threat_feed, **kwargs):
    """Create a test TTP with unique mitre_technique_id for the given threat_feed."""
    unique = kwargs.pop('unique', False)
    
    defaults = {
        'name': f'Test TTP {uuid.uuid4().hex[:8]}',
        'description': 'Test description',
        'mitre_technique_id': f'T{random.randint(1000, 9999)}',  # Generate random ID
        'stix_id': f'attack-pattern--{uuid.uuid4()}',  # Generate unique STIX ID
        'threat_feed': threat_feed,
    }
    defaults.update(kwargs)
    
    try:
        return TTPData.objects.create(**defaults)
    except IntegrityError:
        # If it exists, get and update the existing record
        ttp = TTPData.objects.get(
            mitre_technique_id=defaults['mitre_technique_id'],
            threat_feed=defaults['threat_feed']
        )
        for key, value in defaults.items():
            if key not in ['mitre_technique_id', 'threat_feed']:
                setattr(ttp, key, value)
        ttp.save()
        return ttp


def create_test_collection_with_objects(owner=None, object_count=3, unique=True):
    """Create a test collection with STIX objects."""
    if owner is None:
        owner = create_test_organization(unique=unique)
    
    collection = create_test_collection(owner=owner, unique=unique)
    
    # Create STIX objects and add to collection
    for i in range(object_count):
        stix_object = create_test_stix_object(
            source_organization=owner,
            unique=unique
        )
        collection.stix_objects.add(stix_object)
    
    return collection


def create_complete_test_scenario(unique=True):
    """Create a complete test scenario with all related objects."""
    # Create user
    user = create_test_user(unique=unique)
    
    # Create organization
    organization = create_test_organization(created_by=user, unique=unique)
    
    # Create institution
    institution = create_test_institution(organization=organization, unique=unique)
    
    # Create threat feed
    threat_feed = create_test_threat_feed(owner=organization, unique=unique)
    
    # Create indicators
    indicators = []
    for i in range(3):
        indicator = create_test_indicator(
            threat_feed=threat_feed,
            value=f"10.0.0.{i + 1}",
            type='ip',
            unique=unique
        )
        indicators.append(indicator)
    
    # Create TTPs
    ttps = []
    for i in range(2):
        ttp = create_test_ttp(
            threat_feed=threat_feed,
            name=f"Test TTP {i + 1}",
            unique=unique
        )
        ttps.append(ttp)
    
    # Create collection
    collection = create_test_collection(owner=organization, unique=unique)
    
    # Create STIX objects
    stix_objects = []
    for i in range(2):
        stix_object = create_test_stix_object(
            source_organization=organization,
            created_by=user,
            unique=unique
        )
        stix_objects.append(stix_object)
        collection.stix_objects.add(stix_object)
    
    return {
        'user': user,
        'organization': organization,
        'institution': institution,
        'threat_feed': threat_feed,
        'indicators': indicators,
        'ttps': ttps,
        'collection': collection,
        'stix_objects': stix_objects
    }


def cleanup_test_data():
    """Clean up all test data from the database."""
    # Delete in reverse dependency order
    CollectionObject.objects.all().delete()
    Collection.objects.all().delete()
    STIXObject.objects.all().delete()
    Indicator.objects.all().delete()
    TTPData.objects.all().delete()
    ThreatFeed.objects.all().delete()
    Institution.objects.all().delete()
    Organization.objects.all().delete()
    User.objects.filter(username__startswith='testuser_').delete()


def create_test_data_batch(count=10, unique=True):
    """Create a batch of test data for performance testing."""
    organizations = []
    collections = []
    stix_objects = []
    
    for i in range(count):
        # Create organization
        org = create_test_organization(
            name_suffix=f"batch_{i}",
            unique=unique
        )
        organizations.append(org)
        
        # Create collection
        collection = create_test_collection(
            owner=org,
            alias_suffix=f"batch_{i}",
            unique=unique
        )
        collections.append(collection)
        
        # Create STIX objects for this collection
        for j in range(3):  # 3 objects per collection
            stix_object = create_test_stix_object(
                source_organization=org,
                unique=unique
            )
            stix_objects.append(stix_object)
            collection.stix_objects.add(stix_object)
    
    return {
        'organizations': organizations,
        'collections': collections,
        'stix_objects': stix_objects
    }