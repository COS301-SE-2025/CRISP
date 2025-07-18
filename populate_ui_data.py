#!/usr/bin/env python3
"""
Script to populate CRISP database with mock data for UI testing.
This script creates organizations, users, and trust relationships.
"""

import os
import sys
import django
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

# Add the project root to the path
sys.path.insert(0, '/mnt/c/Users/Client/Documents/GitHub/CRISP')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')

# Setup Django
django.setup()

# Import models after Django setup
from core.user_management.models import CustomUser, Organization
from core.trust.models import TrustRelationship, TrustLevel, TrustGroup

def create_organizations():
    """Create test organizations"""
    print("Creating organizations...")
    
    orgs_data = [
        {
            'name': 'University of Cape Town',
            'domain': 'uct.ac.za',
            'contact_email': 'admin@uct.ac.za',
            'website': 'https://www.uct.ac.za',
            'organization_type': 'educational',
            'description': 'Leading research university in South Africa',
            'is_publisher': True,
            'is_verified': True,
            'is_active': True,
        },
        {
            'name': 'Stellenbosch University',
            'domain': 'sun.ac.za',
            'contact_email': 'admin@sun.ac.za',
            'website': 'https://www.sun.ac.za',
            'organization_type': 'educational',
            'description': 'Premier research-intensive university',
            'is_publisher': True,
            'is_verified': True,
            'is_active': True,
        },
        {
            'name': 'University of Witwatersrand',
            'domain': 'wits.ac.za',
            'contact_email': 'admin@wits.ac.za',
            'website': 'https://www.wits.ac.za',
            'organization_type': 'educational',
            'description': 'Leading university in Johannesburg',
            'is_publisher': True,
            'is_verified': True,
            'is_active': True,
        },
        {
            'name': 'CSIR',
            'domain': 'csir.co.za',
            'contact_email': 'admin@csir.co.za',
            'website': 'https://www.csir.co.za',
            'organization_type': 'government',
            'description': 'Council for Scientific and Industrial Research',
            'is_publisher': True,
            'is_verified': True,
            'is_active': True,
        },
        {
            'name': 'South African Police Service',
            'domain': 'saps.gov.za',
            'contact_email': 'admin@saps.gov.za',
            'website': 'https://www.saps.gov.za',
            'organization_type': 'government',
            'description': 'South African national police service',
            'is_publisher': False,
            'is_verified': True,
            'is_active': True,
        },
        {
            'name': 'MTN Group',
            'domain': 'mtn.com',
            'contact_email': 'admin@mtn.com',
            'website': 'https://www.mtn.com',
            'organization_type': 'private',
            'description': 'Leading telecommunications company',
            'is_publisher': False,
            'is_verified': True,
            'is_active': True,
        },
        {
            'name': 'Vodacom',
            'domain': 'vodacom.co.za',
            'contact_email': 'admin@vodacom.co.za',
            'website': 'https://www.vodacom.co.za',
            'organization_type': 'private',
            'description': 'Mobile telecommunications company',
            'is_publisher': False,
            'is_verified': True,
            'is_active': True,
        },
        {
            'name': 'Standard Bank',
            'domain': 'standardbank.co.za',
            'contact_email': 'admin@standardbank.co.za',
            'website': 'https://www.standardbank.co.za',
            'organization_type': 'private',
            'description': 'Leading financial services group',
            'is_publisher': False,
            'is_verified': True,
            'is_active': True,
        },
    ]
    
    organizations = []
    for org_data in orgs_data:
        org, created = Organization.objects.get_or_create(
            name=org_data['name'],
            defaults=org_data
        )
        if created:
            print(f"Created organization: {org.name}")
        else:
            print(f"Organization already exists: {org.name}")
        organizations.append(org)
    
    return organizations

def create_users(organizations):
    """Create test users for each organization"""
    print("Creating users...")
    
    users_data = [
        # UCT Users
        {
            'username': 'john.smith',
            'email': 'john.smith@uct.ac.za',
            'first_name': 'John',
            'last_name': 'Smith',
            'password': 'password123',
            'role': 'publisher',
            'is_publisher': True,
            'is_verified': True,
            'organization': 'University of Cape Town',
        },
        {
            'username': 'sarah.jones',
            'email': 'sarah.jones@uct.ac.za',
            'first_name': 'Sarah',
            'last_name': 'Jones',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'University of Cape Town',
        },
        # Stellenbosch Users
        {
            'username': 'mike.brown',
            'email': 'mike.brown@sun.ac.za',
            'first_name': 'Mike',
            'last_name': 'Brown',
            'password': 'password123',
            'role': 'publisher',
            'is_publisher': True,
            'is_verified': True,
            'organization': 'Stellenbosch University',
        },
        {
            'username': 'lisa.white',
            'email': 'lisa.white@sun.ac.za',
            'first_name': 'Lisa',
            'last_name': 'White',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'Stellenbosch University',
        },
        # Wits Users
        {
            'username': 'david.wilson',
            'email': 'david.wilson@wits.ac.za',
            'first_name': 'David',
            'last_name': 'Wilson',
            'password': 'password123',
            'role': 'publisher',
            'is_publisher': True,
            'is_verified': True,
            'organization': 'University of Witwatersrand',
        },
        {
            'username': 'anna.taylor',
            'email': 'anna.taylor@wits.ac.za',
            'first_name': 'Anna',
            'last_name': 'Taylor',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'University of Witwatersrand',
        },
        # CSIR Users
        {
            'username': 'robert.garcia',
            'email': 'robert.garcia@csir.co.za',
            'first_name': 'Robert',
            'last_name': 'Garcia',
            'password': 'password123',
            'role': 'publisher',
            'is_publisher': True,
            'is_verified': True,
            'organization': 'CSIR',
        },
        {
            'username': 'maria.martinez',
            'email': 'maria.martinez@csir.co.za',
            'first_name': 'Maria',
            'last_name': 'Martinez',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'CSIR',
        },
        # SAPS Users
        {
            'username': 'james.anderson',
            'email': 'james.anderson@saps.gov.za',
            'first_name': 'James',
            'last_name': 'Anderson',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'South African Police Service',
        },
        {
            'username': 'jennifer.thomas',
            'email': 'jennifer.thomas@saps.gov.za',
            'first_name': 'Jennifer',
            'last_name': 'Thomas',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'South African Police Service',
        },
        # MTN Users
        {
            'username': 'peter.jackson',
            'email': 'peter.jackson@mtn.com',
            'first_name': 'Peter',
            'last_name': 'Jackson',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'MTN Group',
        },
        {
            'username': 'susan.lee',
            'email': 'susan.lee@mtn.com',
            'first_name': 'Susan',
            'last_name': 'Lee',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'MTN Group',
        },
        # Vodacom Users
        {
            'username': 'chris.harris',
            'email': 'chris.harris@vodacom.co.za',
            'first_name': 'Chris',
            'last_name': 'Harris',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'Vodacom',
        },
        {
            'username': 'nancy.clark',
            'email': 'nancy.clark@vodacom.co.za',
            'first_name': 'Nancy',
            'last_name': 'Clark',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'Vodacom',
        },
        # Standard Bank Users
        {
            'username': 'kevin.rodriguez',
            'email': 'kevin.rodriguez@standardbank.co.za',
            'first_name': 'Kevin',
            'last_name': 'Rodriguez',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'Standard Bank',
        },
        {
            'username': 'michelle.lewis',
            'email': 'michelle.lewis@standardbank.co.za',
            'first_name': 'Michelle',
            'last_name': 'Lewis',
            'password': 'password123',
            'role': 'viewer',
            'is_publisher': False,
            'is_verified': True,
            'organization': 'Standard Bank',
        },
    ]
    
    # Create organization lookup
    org_lookup = {org.name: org for org in organizations}
    
    users = []
    for user_data in users_data:
        org_name = user_data.pop('organization')
        organization = org_lookup.get(org_name)
        
        if not organization:
            print(f"Warning: Organization '{org_name}' not found for user {user_data['username']}")
            continue
        
        user_data['organization'] = organization
        
        user, created = CustomUser.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            print(f"Created user: {user.username} ({user.organization.name})")
        else:
            print(f"User already exists: {user.username}")
        users.append(user)
    
    return users

def create_trust_levels():
    """Create trust levels"""
    print("Creating trust levels...")
    
    trust_levels_data = [
        {
            'name': 'Full Trust',
            'description': 'Complete trust relationship with full data sharing',
            'level': 'trusted',
            'numerical_value': 100,
            'is_active': True,
            'created_by': 'system',
        },
        {
            'name': 'High Trust',
            'description': 'High level of trust with extensive data sharing',
            'level': 'trusted',
            'numerical_value': 80,
            'is_active': True,
            'created_by': 'system',
        },
        {
            'name': 'Medium Trust',
            'description': 'Medium level of trust with limited data sharing',
            'level': 'trusted',
            'numerical_value': 60,
            'is_active': True,
            'created_by': 'system',
        },
        {
            'name': 'Low Trust',
            'description': 'Low level of trust with minimal data sharing',
            'level': 'public',
            'numerical_value': 40,
            'is_active': True,
            'created_by': 'system',
        },
        {
            'name': 'Restricted',
            'description': 'Restricted trust with very limited access',
            'level': 'restricted',
            'numerical_value': 20,
            'is_active': True,
            'created_by': 'system',
        },
    ]
    
    trust_levels = []
    for level_data in trust_levels_data:
        level, created = TrustLevel.objects.get_or_create(
            name=level_data['name'],
            defaults=level_data
        )
        if created:
            print(f"Created trust level: {level.name}")
        else:
            print(f"Trust level already exists: {level.name}")
        trust_levels.append(level)
    
    return trust_levels

def create_trust_relationships(organizations, trust_levels):
    """Create trust relationships between organizations"""
    print("Creating trust relationships...")
    
    if not trust_levels:
        print("No trust levels available, skipping trust relationships")
        return []
    
    # Create some trust relationships
    relationships_data = [
        {
            'source': 'University of Cape Town',
            'target': 'Stellenbosch University',
            'trust_level': 'High Trust',
            'relationship_type': 'bilateral',
            'status': 'active',
            'notes': 'Academic collaboration partnership',
        },
        {
            'source': 'University of Cape Town',
            'target': 'University of Witwatersrand',
            'trust_level': 'High Trust',
            'relationship_type': 'bilateral',
            'status': 'active',
            'notes': 'Research consortium partnership',
        },
        {
            'source': 'CSIR',
            'target': 'University of Cape Town',
            'trust_level': 'Medium Trust',
            'relationship_type': 'bilateral',
            'status': 'active',
            'notes': 'Research collaboration',
        },
        {
            'source': 'CSIR',
            'target': 'Stellenbosch University',
            'trust_level': 'Medium Trust',
            'relationship_type': 'bilateral',
            'status': 'active',
            'notes': 'Technology transfer partnership',
        },
        {
            'source': 'South African Police Service',
            'target': 'CSIR',
            'trust_level': 'Full Trust',
            'relationship_type': 'hierarchical',
            'status': 'active',
            'notes': 'Government cybersecurity collaboration',
        },
        {
            'source': 'MTN Group',
            'target': 'Vodacom',
            'trust_level': 'Low Trust',
            'relationship_type': 'bilateral',
            'status': 'pending',
            'notes': 'Industry threat information sharing',
        },
        {
            'source': 'Standard Bank',
            'target': 'MTN Group',
            'trust_level': 'Medium Trust',
            'relationship_type': 'bilateral',
            'status': 'active',
            'notes': 'Financial services security partnership',
        },
    ]
    
    # Create organization and trust level lookups
    org_lookup = {org.name: org for org in organizations}
    trust_lookup = {level.name: level for level in trust_levels}
    
    relationships = []
    for rel_data in relationships_data:
        source_org = org_lookup.get(rel_data['source'])
        target_org = org_lookup.get(rel_data['target'])
        trust_level = trust_lookup.get(rel_data['trust_level'])
        
        if not source_org or not target_org or not trust_level:
            print(f"Warning: Missing data for relationship {rel_data['source']} -> {rel_data['target']}")
            continue
        
        relationship, created = TrustRelationship.objects.get_or_create(
            source_organization=source_org,
            target_organization=target_org,
            defaults={
                'trust_level': trust_level,
                'relationship_type': rel_data['relationship_type'],
                'status': rel_data['status'],
                'notes': rel_data['notes'],
                'is_active': True,
            }
        )
        if created:
            print(f"Created trust relationship: {source_org.name} -> {target_org.name}")
        else:
            print(f"Trust relationship already exists: {source_org.name} -> {target_org.name}")
        relationships.append(relationship)
    
    return relationships

def create_trust_groups(organizations):
    """Create trust groups"""
    print("Creating trust groups...")
    
    groups_data = [
        {
            'name': 'Academic Research Consortium',
            'description': 'Group for academic institutions sharing research threat data',
            'is_public': True,
            'is_active': True,
            'members': ['University of Cape Town', 'Stellenbosch University', 'University of Witwatersrand'],
        },
        {
            'name': 'Government Security Network',
            'description': 'Government agencies sharing cybersecurity intelligence',
            'is_public': False,
            'is_active': True,
            'members': ['South African Police Service', 'CSIR'],
        },
        {
            'name': 'Telecommunications Alliance',
            'description': 'Telecom companies sharing network security threats',
            'is_public': True,
            'is_active': True,
            'members': ['MTN Group', 'Vodacom'],
        },
        {
            'name': 'Financial Services Security',
            'description': 'Financial institutions sharing fraud and security intelligence',
            'is_public': False,
            'is_active': True,
            'members': ['Standard Bank'],
        },
    ]
    
    # Create organization lookup
    org_lookup = {org.name: org for org in organizations}
    
    groups = []
    for group_data in groups_data:
        member_names = group_data.pop('members', [])
        
        group, created = TrustGroup.objects.get_or_create(
            name=group_data['name'],
            defaults=group_data
        )
        if created:
            print(f"Created trust group: {group.name}")
            
            # Add members to the group using TrustGroupMembership
            from core.trust.models import TrustGroupMembership
            for member_name in member_names:
                member_org = org_lookup.get(member_name)
                if member_org:
                    membership, created = TrustGroupMembership.objects.get_or_create(
                        trust_group=group,
                        organization=member_org,
                        defaults={
                            'membership_type': 'member',
                            'is_active': True,
                        }
                    )
                    if created:
                        print(f"Added {member_name} to {group.name}")
        else:
            print(f"Trust group already exists: {group.name}")
        groups.append(group)
    
    return groups

def main():
    """Main function to populate database"""
    print("Starting database population...")
    
    try:
        # Create organizations
        organizations = create_organizations()
        print(f"Created/found {len(organizations)} organizations")
        
        # Create users
        users = create_users(organizations)
        print(f"Created/found {len(users)} users")
        
        # Create trust levels
        trust_levels = create_trust_levels()
        print(f"Created/found {len(trust_levels)} trust levels")
        
        # Create trust relationships
        relationships = create_trust_relationships(organizations, trust_levels)
        print(f"Created/found {len(relationships)} trust relationships")
        
        # Create trust groups
        groups = create_trust_groups(organizations)
        print(f"Created/found {len(groups)} trust groups")
        
        print("\nDatabase population completed successfully!")
        print(f"Summary:")
        print(f"- Organizations: {len(organizations)}")
        print(f"- Users: {len(users)}")
        print(f"- Trust Levels: {len(trust_levels)}")
        print(f"- Trust Relationships: {len(relationships)}")
        print(f"- Trust Groups: {len(groups)}")
        
    except Exception as e:
        print(f"Error during database population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()