"""
Test factories for Trust Management module.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from core_ut.user_management.models import Organization, UserSession
from core_ut.trust.models import TrustLevel, TrustRelationship, TrustGroup, TrustLog
import uuid
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = 'user_management.Organization'
    
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Organization {n}")
    description = factory.Faker('text', max_nb_chars=200)
    domain = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '')}.edu")
    contact_email = factory.LazyAttribute(lambda obj: f"contact@{obj.domain}")
    website = factory.LazyAttribute(lambda obj: f"https://www.{obj.domain}")
    organization_type = 'educational'  # Set default to educational
    is_publisher = False
    is_verified = True
    is_active = True
    trust_metadata = factory.LazyFunction(lambda: {'default': True})


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = 'user_management.CustomUser'
    
    id = factory.LazyFunction(uuid.uuid4)
    username = factory.Sequence(lambda n: f"user{n}")
    organization = factory.SubFactory(OrganizationFactory)
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@{obj.organization.domain}")
    password = factory.LazyFunction(lambda: make_password('testpass123'))
    role = 'viewer'
    is_active = True
    is_verified = True
    
    # Provide default JSON field values
    trusted_devices = factory.LazyFunction(lambda: [])
    preferences = factory.LazyFunction(lambda: {})
    metadata = factory.LazyFunction(lambda: {})


class CustomUserWithoutOrgFactory(DjangoModelFactory):
    """Factory for creating users without organization for invitation tests"""
    class Meta:
        model = 'user_management.CustomUser'
    
    id = factory.LazyFunction(uuid.uuid4)
    username = factory.Sequence(lambda n: f"user{n}")
    organization = None  # No organization initially
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.LazyFunction(lambda: make_password('testpass123'))
    role = 'viewer'
    is_active = True
    is_verified = True
    
    # Provide default JSON field values
    trusted_devices = factory.LazyFunction(lambda: [])
    preferences = factory.LazyFunction(lambda: {})
    metadata = factory.LazyFunction(lambda: {})
    
    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'testpass123'
        self.set_password(password)
        if create:
            self.save(update_fields=['password'])


class TrustLevelFactory(DjangoModelFactory):
    class Meta:
        model = TrustLevel
        django_get_or_create = ('name',)
    
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Trust Level {n}")
    level = factory.Iterator(['public', 'trusted', 'restricted'])
    numerical_value = factory.Faker('random_int', min=0, max=100)
    description = factory.Faker('sentence')
    sharing_policies = factory.LazyFunction(lambda: {'default_policy': 'allow', 'restrictions': []})
    created_by = factory.LazyAttribute(lambda obj: f"user_{obj.name.lower().replace(' ', '_')}")


class TrustRelationshipFactory(DjangoModelFactory):
    class Meta:
        model = 'trust.TrustRelationship'
    
    id = factory.LazyFunction(uuid.uuid4)
    source_organization = factory.SubFactory(OrganizationFactory)
    target_organization = factory.SubFactory(OrganizationFactory)
    trust_level = factory.SubFactory(TrustLevelFactory)
    status = 'pending'
    relationship_type = factory.Iterator(['bilateral', 'community', 'hierarchical', 'federation'])
    anonymization_level = 'partial'  # Set default to partial
    access_level = 'read'
    notes = factory.Faker('sentence')
    valid_until = factory.LazyFunction(lambda: timezone.now() + timedelta(days=365))
    created_by = factory.SubFactory(CustomUserFactory)
    last_modified_by = factory.SelfAttribute('created_by')


class TrustGroupFactory(DjangoModelFactory):
    class Meta:
        model = TrustGroup
    
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Trust Group {n}")
    description = factory.Faker('sentence')
    group_type = factory.Iterator(['sector', 'geography', 'purpose', 'custom', 'community'])
    is_public = factory.Iterator([True, False])
    default_trust_level = factory.SubFactory(TrustLevelFactory)
    created_by = factory.LazyAttribute(lambda obj: f"org_{obj.name.lower().replace(' ', '_')}")


class TrustLogFactory(DjangoModelFactory):
    class Meta:
        model = TrustLog
    
    id = factory.LazyFunction(uuid.uuid4)
    action = factory.Iterator(['relationship_created', 'group_joined', 'trust_granted'])
    user = factory.SubFactory(CustomUserFactory)
    success = True
    details = factory.LazyFunction(dict)
    metadata = factory.LazyFunction(dict)
