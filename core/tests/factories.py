"""
Test factories for Trust Management module.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from core.trust.models import (
    TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership,
    TrustLog, SharingPolicy
)
from core.user_management.models import Organization

User = get_user_model()


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization
    
    name = factory.Sequence(lambda n: f"Organization {n}")
    domain = factory.Sequence(lambda n: f"org{n}.edu")
    contact_email = factory.LazyAttribute(lambda obj: f"contact@{obj.domain}")
    description = factory.Faker('company')
    organization_type = 'educational'
    trust_metadata = factory.Dict({'trust_score': 50, 'verified': True})


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@{obj.organization.domain}")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    organization = factory.SubFactory(OrganizationFactory)
    role = 'viewer'
    is_active = True
    is_verified = True


class TrustLevelFactory(DjangoModelFactory):
    class Meta:
        model = TrustLevel
    
    name = factory.Sequence(lambda n: f"Trust Level {n}")
    description = factory.Faker('sentence')
    level = factory.Iterator(['public', 'trusted', 'restricted'])
    numerical_value = factory.Faker('random_int', min=0, max=100)
    default_access_level = factory.Iterator(['none', 'read', 'subscribe', 'contribute', 'full'])
    default_anonymization_level = factory.Iterator(['full', 'partial', 'minimal', 'none'])
    created_by = factory.LazyAttribute(lambda obj: f"system_user_{obj.name}")
    is_active = True


class TrustRelationshipFactory(DjangoModelFactory):
    class Meta:
        model = TrustRelationship
    
    source_organization = factory.SubFactory(OrganizationFactory)
    target_organization = factory.SubFactory(OrganizationFactory)
    trust_level = factory.SubFactory(TrustLevelFactory)
    relationship_type = factory.Iterator(['bilateral', 'community', 'hierarchical', 'federation'])
    status = 'pending'
    anonymization_level = 'partial'
    access_level = 'read'
    notes = factory.Faker('text', max_nb_chars=200)
    valid_until = factory.LazyFunction(lambda: timezone.now() + timedelta(days=365))
    created_by = factory.SubFactory(UserFactory)
    last_modified_by = factory.SubFactory(UserFactory)


class TrustGroupFactory(DjangoModelFactory):
    class Meta:
        model = TrustGroup
    
    name = factory.Sequence(lambda n: f"Trust Group {n}")
    description = factory.Faker('text', max_nb_chars=500)
    created_by = factory.LazyAttribute(lambda obj: f"org_{obj.name}")
    group_type = factory.Iterator(['sector', 'geography', 'purpose', 'custom'])
    is_public = factory.Iterator([True, False])
    is_active = True
    default_trust_level = factory.SubFactory(TrustLevelFactory)


class TrustGroupMembershipFactory(DjangoModelFactory):
    class Meta:
        model = TrustGroupMembership
    
    trust_group = factory.SubFactory(TrustGroupFactory)
    organization = factory.SubFactory(OrganizationFactory)
    membership_type = factory.Iterator(['member', 'administrator', 'moderator'])
    is_active = True
    invited_by = factory.LazyAttribute(lambda obj: f"admin_{obj.trust_group.name}")
    approved_by = factory.LazyAttribute(lambda obj: f"admin_{obj.trust_group.name}")


class SharingPolicyFactory(DjangoModelFactory):
    class Meta:
        model = SharingPolicy
    
    name = factory.Sequence(lambda n: f"Policy {n}")
    description = factory.Faker('sentence')
    created_by = factory.LazyAttribute(lambda obj: f"admin_{obj.name}")
    allowed_stix_types = factory.List(['indicator', 'malware', 'threat-actor'])
    allowed_indicator_types = factory.List(['file', 'domain-name', 'ipv4-addr'])
    max_tlp_level = 'green'
    require_anonymization = True
    allow_attribution = False
    is_active = True


class TrustLogFactory(DjangoModelFactory):
    class Meta:
        model = TrustLog
    
    source_organization = factory.SubFactory(OrganizationFactory)
    action = factory.Iterator(['relationship_created', 'relationship_approved', 'group_created', 'access_granted'])
    target_organization = factory.SubFactory(OrganizationFactory)
    user = factory.SubFactory(UserFactory)
    ip_address = factory.Faker('ipv4')
    user_agent = factory.Faker('user_agent')
    details = factory.Dict({'test': 'data'})
    metadata = factory.Dict({'source': 'test'})
    success = True
