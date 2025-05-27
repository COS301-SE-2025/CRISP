#!/usr/bin/env python
"""
Script to initialize the database with basic setup data for the
Threat Intelligence Publication Service.
"""
import os
import sys
import django
import uuid
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threat_intel.settings')
django.setup()

# Import models
from django.contrib.auth.models import User, Group
from core.models import Organization, Collection
from trust.models import TrustRelationship, TrustGroup, TrustGroupMembership

def create_admin_user():
    """Create admin user if it doesn't exist."""
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.edu',
            password='admin123'  # In production, use a secure password
        )
        print("Created admin user")
        return admin
    else:
        print("Admin user already exists")
        return User.objects.get(username='admin')

def create_organization(name, description, admin_user):
    """Create organization and associated group."""
    # Create organization
    organization, created = Organization.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'identity_class': 'organization',
            'sectors': ['education'],
            'stix_id': f"identity--{str(uuid.uuid4())}"
        }
    )
    
    # Create group with same name as organization id
    group, _ = Group.objects.get_or_create(name=str(organization.id))
    
    # Add admin user to group
    admin_user.groups.add(group)
    
    if created:
        print(f"Created organization: {name}")
    else:
        print(f"Organization already exists: {name}")
    
    return organization

def create_collections(organization):
    """Create default collections for an organization."""
    collections = [
        {
            'title': 'Indicators',
            'description': 'Collection of threat indicators',
            'alias': f"{organization.name.lower().replace(' ', '-')}-indicators",
            'can_read': True,
            'can_write': True,
            'media_types': ['application/stix+json;version=2.1'],
            'default_anonymization': 'partial'
        },
        {
            'title': 'Malware',
            'description': 'Collection of malware information',
            'alias': f"{organization.name.lower().replace(' ', '-')}-malware",
            'can_read': True,
            'can_write': True,
            'media_types': ['application/stix+json;version=2.1'],
            'default_anonymization': 'partial'
        },
        {
            'title': 'Threat Actors',
            'description': 'Collection of threat actor information',
            'alias': f"{organization.name.lower().replace(' ', '-')}-threat-actors",
            'can_read': True,
            'can_write': True,
            'media_types': ['application/stix+json;version=2.1'],
            'default_anonymization': 'partial'
        },
        {
            'title': 'Attack Patterns',
            'description': 'Collection of attack pattern information',
            'alias': f"{organization.name.lower().replace(' ', '-')}-attack-patterns",
            'can_read': True,
            'can_write': True,
            'media_types': ['application/stix+json;version=2.1'],
            'default_anonymization': 'partial'
        }
    ]
    
    created_collections = []
    
    for collection_data in collections:
        collection, created = Collection.objects.get_or_create(
            title=collection_data['title'],
            owner=organization,
            defaults={
                'description': collection_data['description'],
                'alias': collection_data['alias'],
                'can_read': collection_data['can_read'],
                'can_write': collection_data['can_write'],
                'media_types': collection_data['media_types'],
                'default_anonymization': collection_data['default_anonymization']
            }
        )
        
        if created:
            print(f"Created collection: {collection_data['title']}")
        else:
            print(f"Collection already exists: {collection_data['title']}")
            
        created_collections.append(collection)
    
    return created_collections

def create_trust_group(name, description, trust_level='medium'):
    """Create a trust group."""
    group, created = TrustGroup.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'default_trust_level_name': trust_level
        }
    )
    
    if created:
        print(f"Created trust group: {name}")
    else:
        print(f"Trust group already exists: {name}")
        
    return group

def add_organization_to_group(organization, group):
    """Add an organization to a trust group."""
    membership, created = TrustGroupMembership.objects.get_or_create(
        trust_group=group,
        organization=organization
    )
    
    if created:
        print(f"Added {organization.name} to {group.name}")
    else:
        print(f"{organization.name} already in {group.name}")
    
    return membership

def create_trust_relationship(source_org, target_org, trust_level='medium'):
    """Create a trust relationship between organizations."""
    relationship, created = TrustRelationship.objects.get_or_create(
        source_organization=source_org,
        target_organization=target_org,
        defaults={
            'trust_level_name': trust_level,
            'notes': f"Trust relationship from {source_org.name} to {target_org.name}"
        }
    )
    
    if created:
        print(f"Created trust relationship: {source_org.name} -> {target_org.name}")
    else:
        print(f"Trust relationship already exists: {source_org.name} -> {target_org.name}")
        
    return relationship

def main():
    """Main function to set up initial data."""
    print("Initializing Threat Intelligence Publication Service...")
    
    # Create admin user
    admin = create_admin_user()
    
    # Create organizations
    org1 = create_organization("University A", "A large research university", admin)
    org2 = create_organization("College B", "A liberal arts college", admin)
    org3 = create_organization("Institute C", "A technical institute", admin)
    
    # Create collections for each organization
    collections1 = create_collections(org1)
    collections2 = create_collections(org2)
    collections3 = create_collections(org3)
    
    # Create trust groups
    edu_group = create_trust_group("Educational Institutions", "Group for educational institutions")
    research_group = create_trust_group("Research Institutions", "Group for research-focused institutions", "high")
    
    # Add organizations to groups
    add_organization_to_group(org1, edu_group)
    add_organization_to_group(org2, edu_group)
    add_organization_to_group(org3, edu_group)
    add_organization_to_group(org1, research_group)
    add_organization_to_group(org3, research_group)
    
    # Create trust relationships
    create_trust_relationship(org1, org2, "medium")
    create_trust_relationship(org1, org3, "high")
    create_trust_relationship(org2, org1, "medium")
    create_trust_relationship(org2, org3, "low")
    create_trust_relationship(org3, org1, "high")
    create_trust_relationship(org3, org2, "medium")
    
    print("Initialization complete!")

if __name__ == "__main__":
    main()