"""
Test factories for Trust Management module.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from TrustManagement.models import (
    TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership,
    TrustLog, SharingPolicy
)

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True


class TrustLevelFactory(DjangoModelFactory):
    class Meta:
        model = TrustLevel
    
    name = factory.Sequence(lambda n: f"Trust Level {n}")
    description = factory.Faker('sentence')
    trust_score = factory.Faker('random_int', min=0, max=100)
    access_level = factory.Iterator(['none', 'read', 'subscribe', 'contribute', 'full'])
    anonymization_strategy = factory.Iterator(['full', 'partial', 'minimal', 'none'])
    is_active = True


class TrustRelationshipFactory(DjangoModelFactory):
    class Meta:
        model = TrustRelationship
    
    source_organization = factory.LazyFunction(lambda: str(uuid.uuid4()))
    target_organization = factory.LazyFunction(lambda: str(uuid.uuid4()))
    trust_level = factory.SubFactory(TrustLevelFactory)
    relationship_type = factory.Iterator(['bilateral', 'unilateral', 'hierarchical', 'federation'])
    status = 'pending'
    notes = factory.Faker('text', max_nb_chars=200)
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=365))
    created_by = factory.LazyFunction(lambda: str(uuid.uuid4()))


class TrustGroupFactory(DjangoModelFactory):
    class Meta:
        model = TrustGroup
    
    name = factory.Sequence(lambda n: f"Trust Group {n}")
    description = factory.Faker('text', max_nb_chars=500)
    creator_organization = factory.LazyFunction(lambda: str(uuid.uuid4()))
    group_type = factory.Iterator(['sector', 'geography', 'purpose', 'custom'])
    is_public = factory.Iterator([True, False])
    is_active = True
    default_trust_level = factory.SubFactory(TrustLevelFactory)


class TrustGroupMembershipFactory(DjangoModelFactory):
    class Meta:
        model = TrustGroupMembership
    
    group = factory.SubFactory(TrustGroupFactory)
    organization_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    membership_type = factory.Iterator(['admin', 'member', 'observer'])
    status = 'active'
    joined_by = factory.LazyFunction(lambda: str(uuid.uuid4()))


class SharingPolicyFactory(DjangoModelFactory):
    class Meta:
        model = SharingPolicy
    
    name = factory.Sequence(lambda n: f"Policy {n}")
    description = factory.Faker('sentence')
    trust_level = factory.SubFactory(TrustLevelFactory)
    resource_types = factory.List(['indicator', 'report', 'signature'])
    allowed_actions = factory.List(['read', 'download', 'share'])
    anonymization_rules = factory.Dict({
        'remove_identifiers': True,
        'mask_ips': True,
        'generalize_timestamps': False
    })
    is_active = True


class TrustLogFactory(DjangoModelFactory):
    class Meta:
        model = TrustLog
    
    organization_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    action = factory.Iterator(['create', 'approve', 'deny', 'revoke', 'access'])
    resource_type = factory.Iterator(['relationship', 'group', 'membership', 'intelligence'])
    resource_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    target_organization = factory.LazyFunction(lambda: str(uuid.uuid4()))
    user_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    ip_address = factory.Faker('ipv4')
    user_agent = factory.Faker('user_agent')
    details = factory.Dict({'test': 'data'})
    success = True
