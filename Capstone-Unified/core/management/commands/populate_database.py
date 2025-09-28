#!/usr/bin/env python
"""
CRISP Database Population Script
Creates test data with parallel processing for development and testing.
"""

import os
import sys
import random
import uuid
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from faker import Faker

# Install tqdm if not available
try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm for progress bars...")
    os.system("pip install tqdm")
    from tqdm import tqdm

from core.models.models import (
    Organization, ThreatFeed, Collection, Feed, SystemActivity, UserProfile
)
from core.user_management.models.user_models import CustomUser, UserSession
from core.user_management.models.invitation_models import UserInvitation
from core.trust_management.models.trust_models import (
    TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership
)

fake = Faker()

class Command(BaseCommand):
    help = 'Populate database with test data for development and testing'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organizations = []
        self.users = []
        self.trust_levels = []
        self.trust_groups = []
        
        # Scale parameters for test data generation - reduced for easier testing
        self.NUM_ORGANIZATIONS = 10
        self.USERS_PER_ORG = (5, 15)
        self.NUM_SYSTEM_ACTIVITIES = 500
        self.NUM_TRUST_RELATIONSHIPS = 30
        self.NUM_TRUST_GROUPS = 5
        self.NUM_USER_SESSIONS = 100
        self.NUM_THREAT_FEEDS = 5
        
        # Parallel processing configuration
        self.MAX_WORKERS = min(cpu_count(), 8)
        self.BATCH_SIZE = 25
        
        # Company data for realistic organizations
        self.company_types = [
            'Technology', 'Healthcare', 'Financial Services', 'Manufacturing', 
            'Retail', 'Energy', 'Transportation', 'Telecommunications', 
            'Government', 'Education', 'Legal Services', 'Consulting',
            'Real Estate', 'Insurance', 'Media', 'Defense', 'Aerospace',
            'Pharmaceuticals', 'Automotive', 'Construction', 'Banking',
            'E-commerce', 'Logistics', 'Entertainment', 'Publishing'
        ]
        
        self.domain_suffixes = [
            'com', 'corp', 'inc', 'ltd', 'org', 'gov', 'edu', 'net',
            'international.com', 'global.com', 'security.com', 'solutions.com',
            'group.com', 'consulting.com', 'services.com', 'tech.com',
            'systems.com', 'enterprises.com', 'industries.com'
        ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Run without user confirmation',
        )

    def handle(self, *args, **options):
        start_time = time.time()
        
        self.stdout.write("Starting CRISP Database Population...")
        self.stdout.write("Using parallel processing for faster execution.")
        self.stdout.write("="*60)
        self.stdout.write(f"System Configuration:")
        self.stdout.write(f"   CPU Cores: {cpu_count()}")
        self.stdout.write(f"   Max Workers: {self.MAX_WORKERS}")
        self.stdout.write(f"   Batch Size: {self.BATCH_SIZE}")
        self.stdout.write("="*60)
        self.stdout.write(f"Target Data Volume:")
        self.stdout.write(f"   {self.NUM_ORGANIZATIONS} organizations")
        self.stdout.write(f"   {self.USERS_PER_ORG[0]}-{self.USERS_PER_ORG[1]} users per org")
        self.stdout.write(f"   {self.NUM_TRUST_RELATIONSHIPS} trust relationships")
        self.stdout.write(f"   {self.NUM_TRUST_GROUPS} trust groups")
        self.stdout.write(f"   {self.NUM_USER_SESSIONS} user sessions")
        self.stdout.write(f"   {self.NUM_THREAT_FEEDS} threat feeds")
        self.stdout.write(f"   {self.NUM_SYSTEM_ACTIVITIES} system activities")
        self.stdout.write("="*60)
        
        if not options['no_input']:
            confirm = input("Ready to start population? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write("Cancelled.")
                return
        
        self.stdout.write(f"\nStarting population at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Run all phases with progress tracking
            phases = [
                ("Phase 1/9: Clearing Data", self.clear_existing_data),
                ("Phase 2/9: Trust Levels", self.create_trust_levels),
                ("Phase 3/9: Organizations", self.create_organizations),
                ("Phase 4/9: Super Admins", self.create_super_admin_users),
                ("Phase 5/9: Users", self.create_users),
                ("Phase 6/9: Trust Relationships", self.create_trust_relationships),
                ("Phase 7/9: Trust Groups", self.create_trust_groups),
                ("Phase 8/9: User Sessions", self.create_user_sessions),
                ("Phase 9/9: Threat Feeds", self.create_threat_feeds),
            ]
            
            self.stdout.write(f"\nExecuting {len(phases)} phases...")
            
            for phase_name, phase_func in phases:
                phase_start = time.time()
                self.stdout.write(f"\n{phase_name}")
                phase_func()
                phase_time = time.time() - phase_start
                self.stdout.write(f"Completed in {phase_time:.1f}s")
            
            self.print_summary()
            
        except Exception as e:
            self.stdout.write(f"Error during population: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def clear_existing_data(self):
        """Clear existing test data with progress tracking"""
        self.stdout.write("Clearing existing data...")
        
        operations = [
            ("Trust Group Memberships", lambda: self._safe_delete(TrustGroupMembership) if TrustGroupMembership else None),
            ("Trust Relationships", lambda: self._safe_delete(TrustRelationship) if TrustRelationship else None),
            ("Trust Groups", lambda: self._safe_delete(TrustGroup) if TrustGroup else None),
            ("User Sessions", lambda: self._safe_delete(UserSession)),
            ("User Profiles", lambda: self._safe_delete(UserProfile)),
            ("User Invitations", lambda: self._safe_delete(UserInvitation)),
            ("Threat Feeds", lambda: self._safe_delete(ThreatFeed)),
            ("Collections", lambda: self._safe_delete(Collection)),
            ("Feeds", lambda: self._safe_delete(Feed)),
            ("System Activities", lambda: self._safe_delete(SystemActivity)),
            ("Non-superusers", lambda: CustomUser.objects.filter(is_superuser=False).delete()),
            ("Organizations", lambda: Organization.objects.exclude(domain='bluevision.tech').delete()),
        ]
        
        for name, operation in operations:
            self.stdout.write(f"   Clearing {name}...")
            try:
                result = operation()
                if result is None:
                    self.stdout.write(f"   Skipping {name} (model not available)")
            except Exception as e:
                self.stdout.write(f"   Warning: Could not clear {name}: {e}")
                
        self.stdout.write("Existing data cleared")

    def _safe_delete(self, model_class):
        """Safely delete all objects from a model, handling missing tables"""
        try:
            return model_class.objects.all().delete()
        except Exception as e:
            # Table might not exist yet, skip
            self.stdout.write(f"   Skipping {model_class.__name__} (table may not exist)")
            return (0, {})

    def create_trust_levels(self):
        """Create or get trust levels"""
        self.stdout.write("Creating trust levels...")
        
        levels = [
            {'name': 'Basic Trust', 'level': 'public', 'numerical_value': 25, 'description': 'Basic trust level for initial partnerships', 'created_by': 'system'},
            {'name': 'Standard Trust', 'level': 'trusted', 'numerical_value': 50, 'description': 'Standard trust level for established relationships', 'created_by': 'system'},
            {'name': 'Premium Trust', 'level': 'restricted', 'numerical_value': 75, 'description': 'Premium trust level for strategic partnerships', 'created_by': 'system'},
        ]
        
        for level_data in levels:
            level, created = TrustLevel.objects.get_or_create(
                name=level_data['name'],
                defaults=level_data
            )
            self.trust_levels.append(level)
            
        self.stdout.write(f"Created/verified {len(self.trust_levels)} trust levels")

    def create_organization_batch(self, batch_data):
        """Create a batch of organizations in parallel"""
        created_orgs = []
        
        for org_data in batch_data:
            try:
                with transaction.atomic():
                    org = Organization.objects.create(**org_data)
                    created_orgs.append(org)
            except Exception as e:
                # Skip duplicates or errors
                continue
                
        return created_orgs

    def create_organizations(self):
        """Create organizations with parallel processing"""
        self.stdout.write(f"Creating {self.NUM_ORGANIZATIONS} organizations...")
        
        # Prepare organization data
        org_data_list = []
        for i in range(self.NUM_ORGANIZATIONS):
            company_type = random.choice(self.company_types)
            company_name = f"{fake.company().replace(',', '').replace('.', '')} {company_type}"
            
            # Create domain based on company name
            domain_base = company_name.lower().replace(' ', '').replace('&', 'and')[:15]
            domain = f"{domain_base}{i}.{random.choice(self.domain_suffixes)}"
            
            # Map company types to valid organization types
            org_type_mapping = {
                'Government': 'government',
                'Education': 'educational',
                'Legal Services': 'government',
                'Defense': 'government',
            }
            
            organization_type = org_type_mapping.get(company_type, 'private')
            
            org_data = {
                'name': company_name,
                'domain': domain,
                'organization_type': organization_type,
                'description': fake.catch_phrase(),
                'contact_email': f"contact@{domain}",
                'website': f"https://www.{domain}",
                'is_active': random.choice([True, True, True, False]),
                'is_publisher': random.choice([True, False]),
                'is_verified': random.choice([True, True, False]),
                'trust_metadata': {'industry': company_type, 'country': fake.country()}
            }
            org_data_list.append(org_data)
        
        # Split into batches for parallel processing
        batches = [org_data_list[i:i + self.BATCH_SIZE] for i in range(0, len(org_data_list), self.BATCH_SIZE)]
        
        # Process in parallel
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = [executor.submit(self.create_organization_batch, batch) for batch in batches]
            
            for future in as_completed(futures):
                try:
                    created_orgs = future.result()
                    self.organizations.extend(created_orgs)
                except Exception as e:
                    self.stdout.write(f"Warning: Batch failed: {e}")
                        
        self.stdout.write(f"Created {len(self.organizations)} organizations")

    def create_super_admin_users(self):
        """Create super admin users"""
        self.stdout.write("Creating super admin users...")
        
        super_admins = [
            ('demo', 'demo@crisp.com', 'Demo Account'),
            ('test', 'test@crisp.com', 'Test Account'),
        ]
        
        for username, email, first_name in super_admins:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': 'User',
                    'is_superuser': True,
                    'is_staff': True,
                    'role': 'BlueVisionAdmin',
                    'is_active': True,
                }
            )
            if created:
                user.set_password('AdminPass123!')
                user.save()
            self.users.append(user)
            
        self.stdout.write(f"Created {len(super_admins)} super admin users")

    def create_user_batch(self, org_user_data):
        """Create a batch of users for an organization"""
        org, user_count = org_user_data
        created_users = []
        
        roles = ['viewer', 'publisher', 'BlueVisionAdmin']
        role_weights = [70, 25, 5]
        
        for i in range(user_count):
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    role = random.choices(roles, weights=role_weights)[0]
                    
                    first_name = fake.first_name()
                    last_name = fake.last_name()
                    unique_id = int(time.time() * 1000000) % 1000000
                    username = f"{first_name.lower()}.{last_name.lower()}.{unique_id}@{org.domain}"
                    
                    with transaction.atomic():
                        user = CustomUser.objects.create(
                            username=username,
                            email=username,
                            first_name=first_name,
                            last_name=last_name,
                            organization=org,
                            role=role,
                            is_active=random.choice([True, True, True, False]),
                            is_publisher=random.choice([True, False]),
                            is_verified=random.choice([True, True, False]),
                            date_joined=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
                        )
                        user.set_password('UserPass123!')
                        user.save()
                        created_users.append(user)
                        break
                        
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        break
                    time.sleep(0.01)
                    
        return created_users

    def create_users(self):
        """Create users with parallel processing"""
        self.stdout.write(f"Creating users for {len(self.organizations)} organizations...")
        
        # Prepare organization-user count pairs
        org_user_pairs = []
        total_estimated_users = 0
        
        for org in self.organizations:
            user_count = random.randint(*self.USERS_PER_ORG)
            org_user_pairs.append((org, user_count))
            total_estimated_users += user_count
            
        self.stdout.write(f"Estimated total users: {total_estimated_users}")
        
        # Process in parallel
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = [executor.submit(self.create_user_batch, org_data) for org_data in org_user_pairs]
            
            for future in as_completed(futures):
                try:
                    created_users = future.result()
                    self.users.extend(created_users)
                except Exception as e:
                    self.stdout.write(f"Warning: User batch failed: {e}")
                        
        self.stdout.write(f"Created {len(self.users)} users")

    def create_trust_relationships(self):
        """Create trust relationships"""
        self.stdout.write(f"Creating {self.NUM_TRUST_RELATIONSHIPS} trust relationships...")
        
        created_count = 0
        relationship_types = ['bilateral', 'community', 'hierarchical']
        statuses = ['pending', 'active', 'suspended']
        
        if not self.organizations or not self.users or not self.trust_levels:
            self.stdout.write("Skipping trust relationships - missing prerequisites")
            return
        
        admin_users = [u for u in self.users if u.role == 'BlueVisionAdmin']
        if not admin_users:
            admin_users = [u for u in self.users if u.is_superuser]
        
        for _ in range(self.NUM_TRUST_RELATIONSHIPS):
            try:
                source_org = random.choice(self.organizations)
                target_org = random.choice(self.organizations)
                
                if source_org == target_org:
                    continue
                    
                # Check for existing relationship
                if TrustRelationship.objects.filter(
                    source_organization=source_org,
                    target_organization=target_org
                ).exists():
                    continue
                    
                if not admin_users:
                    continue
                    
                admin_user = random.choice(admin_users)
                trust_level = random.choice(self.trust_levels)
                
                with transaction.atomic():
                    trust_rel = TrustRelationship.objects.create(
                        source_organization=source_org,
                        target_organization=target_org,
                        trust_level=trust_level,
                        relationship_type=random.choice(relationship_types),
                        status=random.choice(statuses),
                        is_active=random.choice([True, False]),
                        created_by=admin_user,
                        created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
                        notes=fake.sentence(),
                        metadata={'created_via': 'turbo_population_script'},
                        sharing_preferences={}  # Add this line - empty dict for sharing preferences
                    )
                    created_count += 1
                    
            except Exception as e:
                continue
                
        self.stdout.write(f"Created {created_count} trust relationships")

    def create_trust_groups(self):
        """Create trust groups"""
        self.stdout.write(f"Creating {self.NUM_TRUST_GROUPS} trust groups...")
        
        # Check if TrustGroup models are available
        if TrustGroup is None or TrustGroupMembership is None:
            self.stdout.write("Skipping trust groups - models not available")
            return
            
        try:
            TrustGroup.objects.model._meta.get_field('id')
            TrustGroupMembership.objects.model._meta.get_field('id')
        except Exception as e:
            self.stdout.write(f"Skipping trust groups - model not available: {e}")
            return
        
        if not self.organizations or not self.users or not self.trust_levels:
            self.stdout.write("Skipping trust groups - missing prerequisites")
            return
        
        admin_users = [u for u in self.users if u.role == 'BlueVisionAdmin']
        if not admin_users:
            admin_users = [u for u in self.users if u.is_superuser]
        
        created_count = 0
        
        for i in range(self.NUM_TRUST_GROUPS):
            try:
                if not admin_users:
                    continue
                    
                admin_user = random.choice(admin_users)
                group_name = f"{fake.word().title()} {random.choice(['Alliance', 'Network', 'Consortium', 'Partnership', 'Coalition'])}"
                
                # Ensure unique name
                counter = 0
                original_name = group_name
                while TrustGroup.objects.filter(name=group_name).exists() and counter < 100:
                    counter += 1
                    group_name = f"{original_name} {counter}"
                
                with transaction.atomic():
                    trust_group = TrustGroup.objects.create(
                        name=group_name,
                        description=fake.paragraph(),
                        default_trust_level=random.choice(self.trust_levels),
                        created_by=str(admin_user),
                        is_active=random.choice([True, True, False]),
                        group_type=random.choice(['industry', 'regional', 'strategic', 'community']),
                        is_public=random.choice([True, False]),
                        requires_approval=random.choice([True, False]),
                        administrators=[str(admin_user.organization.id)] if admin_user.organization else []
                    )
                    
                    # Add admin user's organization as first member
                    if admin_user.organization:
                        TrustGroupMembership.objects.create(
                            trust_group=trust_group,
                            organization=admin_user.organization,
                            membership_type='administrator',
                            is_active=True,
                            joined_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
                            invited_by=str(admin_user.organization.id),
                            approved_by=str(admin_user)
                        )
                    
                    # Add random organizations to the group
                    num_members = random.randint(2, 8)
                    available_orgs = [org for org in self.organizations if org != admin_user.organization]
                    member_orgs = random.sample(available_orgs, min(num_members, len(available_orgs)))
                    
                    for org in member_orgs:
                        TrustGroupMembership.objects.create(
                            trust_group=trust_group,
                            organization=org,
                            membership_type=random.choice(['member', 'member', 'member', 'moderator']),
                            is_active=random.choice([True, True, False]),
                            joined_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
                            invited_by=str(admin_user.organization.id) if admin_user.organization else None,
                            approved_by=str(admin_user) if trust_group.requires_approval else None
                        )
                        
                    self.trust_groups.append(trust_group)
                    created_count += 1
                    
            except Exception as e:
                continue
                
        self.stdout.write(f"Created {created_count} trust groups")

    def create_user_sessions(self):
        """Create user sessions"""
        self.stdout.write(f"Creating {self.NUM_USER_SESSIONS} user sessions...")
        
        if not self.users:
            self.stdout.write("No users available for session creation!")
            return
        
        created_count = 0
        
        for i in range(self.NUM_USER_SESSIONS):
            try:
                user = random.choice(self.users)
                session_start = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
                session_duration = timedelta(minutes=random.randint(5, 480))
                
                with transaction.atomic():
                    session = UserSession.objects.create(
                        user=user,
                        session_token=fake.sha256(),
                        refresh_token=fake.sha256(),
                        device_info={
                            'user_agent': fake.user_agent(), 
                            'browser': fake.random_element(['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']),
                            'os': fake.random_element(['Windows', 'macOS', 'Linux', 'iOS', 'Android'])
                        },
                        ip_address=fake.ipv4(),
                        is_active=random.choice([True, False]),
                        expires_at=session_start + session_duration,
                        is_trusted_device=random.choice([True, False])
                    )
                    created_count += 1
                    
            except Exception as e:
                continue
                
        self.stdout.write(f"Created {created_count} user sessions")

    def create_threat_feeds(self):
        """Create comprehensive threat feeds including custom CRISP feeds"""
        self.stdout.write("Creating comprehensive threat feeds with custom CRISP intelligence...")

        if not self.organizations or not self.users:
            self.stdout.write("Skipping threat feeds - missing prerequisites")
            return

        created_count = 0

        # Import custom feed configurations
        try:
            from core.config.custom_threat_feeds import CUSTOM_FEEDS_CONFIG
            self.stdout.write(f"Loaded {len(CUSTOM_FEEDS_CONFIG)} custom CRISP threat feeds")
        except ImportError as e:
            self.stdout.write(f"Warning: Could not import custom feeds: {e}")
            CUSTOM_FEEDS_CONFIG = []

        # Create some collections first
        collections = []
        for i in range(15):  # Increased for more comprehensive coverage
            try:
                with transaction.atomic():
                    collection = Collection.objects.create(
                        title=f"{fake.word().title()} Threat Collection {i}",
                        description=fake.text(),
                        alias=f"collection-{i}-{uuid.uuid4().hex[:8]}",
                        owner=random.choice(self.organizations),
                        can_read=True,
                        can_write=random.choice([True, False]),
                        media_types=["application/stix+json;version=2.1"]
                    )
                    collections.append(collection)
            except Exception as e:
                self.stdout.write(f"Error creating collection: {e}")
                continue

        # First, create our comprehensive custom CRISP feeds
        self.stdout.write("Creating custom CRISP threat intelligence feeds...")
        for feed_config in CUSTOM_FEEDS_CONFIG:
            try:
                user = random.choice(self.users)
                org = random.choice(self.organizations)
                collection = random.choice(collections) if collections else None

                with transaction.atomic():
                    threat_feed = ThreatFeed.objects.create(
                        name=feed_config['name'],
                        description=feed_config['description'],
                        taxii_server_url=feed_config['taxii_server_url'],
                        taxii_api_root=feed_config['taxii_api_root'],
                        taxii_collection_id=feed_config['taxii_collection_id'],
                        taxii_username=feed_config.get('taxii_username'),
                        taxii_password=feed_config.get('taxii_password'),
                        owner=org,
                        is_external=feed_config['is_external'],
                        is_public=feed_config['is_public'],
                        sync_interval_hours=feed_config['sync_interval_hours'],
                        is_active=True,
                        last_sync=fake.date_time_between(start_date='-7d', end_date='now', tzinfo=timezone.get_current_timezone()),
                        sync_count=random.randint(50, 500)  # Simulate active feeds
                    )

                    # Create associated Feed if collection exists
                    if collection:
                        feed_name = f"Feed for {threat_feed.name}"
                        Feed.objects.create(
                            title=feed_name,
                            name=feed_name,
                            alias=f"feed--{uuid.uuid4()}",
                            description=f"TAXII feed for {threat_feed.name}",
                            status='active',
                            created_by=user,
                            collection=collection,
                            organization=org,
                            threat_feed=threat_feed,
                            is_public=threat_feed.is_public
                        )

                    created_count += 1
                    self.stdout.write(f"  ✓ Created: {feed_config['name']}")

            except Exception as e:
                self.stdout.write(f"Error creating custom feed {feed_config['name']}: {e}")
                continue

        # Then create standard external feeds (only the working ones after cleanup)
        self.stdout.write("Creating working external threat feeds...")
        standard_feeds = [
            {
                'name': 'MITRE ATT&CK Enterprise',
                'description': 'MITRE ATT&CK Enterprise tactics, techniques, and procedures',
                'taxii_server_url': 'https://cti-taxii.mitre.org',
                'taxii_api_root': 'stix',
                'taxii_collection_id': '95ecc380-afe9-11e4-9b6c-751b66dd541e',
                'is_external': True,
                'is_public': True,
                'sync_interval_hours': 24,
            },
            {
                'name': 'MITRE ATT&CK Mobile',
                'description': 'MITRE ATT&CK Mobile tactics and techniques',
                'taxii_server_url': 'https://cti-taxii.mitre.org',
                'taxii_api_root': 'stix',
                'taxii_collection_id': '2f669986-b40b-4423-b720-4396ca6a462b',
                'is_external': True,
                'is_public': True,
                'sync_interval_hours': 24,
            },
            {
                'name': 'MITRE ATT&CK ICS',
                'description': 'MITRE ATT&CK Industrial Control Systems',
                'taxii_server_url': 'https://cti-taxii.mitre.org',
                'taxii_api_root': 'stix',
                'taxii_collection_id': '02c3ef24-9cd4-48f3-a99f-b74ce24f1d34',
                'is_external': True,
                'is_public': True,
                'sync_interval_hours': 24,
            },
            {
                'name': 'AlienVault OTX - General',
                'description': 'AlienVault Open Threat Exchange general threat intelligence',
                'taxii_server_url': 'https://otx.alienvault.com',
                'taxii_api_root': 'taxii',
                'taxii_collection_id': 'user_AlienVault',
                'is_external': True,
                'is_public': True,
                'sync_interval_hours': 6,
            },
            {
                'name': 'AlienVault OTX - DataDefenders',
                'description': 'AlienVault OTX DataDefenders collection',
                'taxii_server_url': 'https://otx.alienvault.com',
                'taxii_api_root': 'taxii',
                'taxii_collection_id': 'user_datadefenders',
                'is_external': True,
                'is_public': True,
                'sync_interval_hours': 12,
            }
        ]

        for config in standard_feeds:
            try:
                user = random.choice(self.users)
                org = random.choice(self.organizations)
                collection = random.choice(collections) if collections else None

                with transaction.atomic():
                    threat_feed = ThreatFeed.objects.create(
                        name=config['name'],
                        description=config['description'],
                        taxii_server_url=config['taxii_server_url'],
                        taxii_api_root=config['taxii_api_root'],
                        taxii_collection_id=config['taxii_collection_id'],
                        taxii_username=config.get('taxii_username'),
                        taxii_password=config.get('taxii_password'),
                        owner=org,
                        is_external=config['is_external'],
                        is_public=config['is_public'],
                        sync_interval_hours=config['sync_interval_hours'],
                        is_active=True,
                        last_sync=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone()) if random.choice([True, False]) else None,
                        sync_count=random.randint(0, 100) if random.choice([True, False]) else 0
                    )

                    # Create associated Feed if collection exists
                    if collection:
                        feed_name = f"Feed for {threat_feed.name}"
                        Feed.objects.create(
                            title=feed_name,
                            name=feed_name,
                            alias=f"feed--{uuid.uuid4()}",
                            description=f"TAXII feed for {threat_feed.name}",
                            status='active',
                            created_by=user,
                            collection=collection,
                            organization=org,
                            threat_feed=threat_feed,
                            is_public=threat_feed.is_public
                        )

                    created_count += 1
                    self.stdout.write(f"  ✓ Created: {config['name']}")

            except Exception as e:
                self.stdout.write(f"Error creating standard feed {config['name']}: {e}")
                continue

        # Create Demo Threat Feed as INACTIVE (for manual consumption only)
        self.stdout.write("Creating inactive demo threat feed...")
        try:
            user = random.choice(self.users)
            org = random.choice(self.organizations)
            collection = random.choice(collections) if collections else None

            with transaction.atomic():
                demo_feed = ThreatFeed.objects.create(
                    name='Demo Threat Feed',
                    description='Demo threat intelligence feed for testing purposes (INACTIVE)',
                    taxii_server_url='https://demo-feeds.crisp.internal',
                    taxii_api_root='demo-api',
                    taxii_collection_id='demo-collection-123',
                    owner=org,
                    is_external=False,
                    is_public=False,
                    is_active=False,  # INACTIVE - won't be consumed during server runs
                    sync_interval_hours=24,
                    last_sync=timezone.now() - timedelta(hours=48)
                )

                # Create corresponding Feed object
                Feed.objects.create(
                    title='Demo Feed',
                    name='Demo Feed',
                    alias=f"feed--{uuid.uuid4()}",
                    description=f"TAXII feed for {demo_feed.name} (INACTIVE)",
                    status='inactive',
                    created_by=user,
                    collection=collection,
                    organization=org,
                    threat_feed=demo_feed,
                    is_public=False
                )

                created_count += 1
                self.stdout.write(f"  ✓ Created INACTIVE Demo Feed (for manual consumption only)")

        except Exception as e:
            self.stdout.write(f"Error creating demo feed: {e}")

        self.stdout.write(f"Created {created_count} comprehensive threat feeds")
        self.stdout.write(f"  - {len(CUSTOM_FEEDS_CONFIG)} custom CRISP intelligence feeds")
        self.stdout.write(f"  - {len(standard_feeds)} standard external feeds")
        self.stdout.write(f"  - 1 inactive demo feed (manual consumption only)")

        # Now populate indicators and TTPs for custom feeds
        self.stdout.write("Populating indicators and TTPs for custom feeds...")
        self.populate_custom_feed_data()

    def populate_custom_feed_data(self):
        """Populate indicators and TTPs for custom threat feeds"""
        try:
            from core.config.custom_threat_feeds import CUSTOM_FEEDS_CONFIG
            from core.models.models import Indicator, TTPData

            # Get created threat feeds
            created_feeds = ThreatFeed.objects.filter(
                name__in=[feed['name'] for feed in CUSTOM_FEEDS_CONFIG]
            )

            indicator_count = 0
            ttp_count = 0

            for feed_config in CUSTOM_FEEDS_CONFIG:
                try:
                    threat_feed = created_feeds.get(name=feed_config['name'])

                    # Create indicators
                    indicators = feed_config.get('indicators', [])
                    for indicator_data in indicators:
                        try:
                            with transaction.atomic():
                                # Map indicator type
                                indicator_type_mapping = {
                                    'domain-name': 'domain',
                                    'ipv4-addr': 'ip',
                                    'file': 'hash',
                                    'email-addr': 'email',
                                    'url': 'url'
                                }

                                mapped_type = indicator_type_mapping.get(
                                    indicator_data['type'],
                                    indicator_data['type']
                                )

                                # Get the indicator value
                                if indicator_data['type'] == 'file':
                                    value = list(indicator_data['hashes'].values())[0]
                                else:
                                    value = indicator_data['value']

                                indicator = Indicator.objects.create(
                                    value=value,
                                    type=mapped_type,
                                    threat_feed=threat_feed,
                                    confidence=indicator_data.get('confidence', 75),
                                    first_seen=timezone.now() - timedelta(days=30),
                                    last_seen=timezone.now() - timedelta(days=1),
                                    stix_id=indicator_data.get('id', f"indicator--{uuid.uuid4()}")
                                )
                                indicator_count += 1

                        except Exception as e:
                            self.stdout.write(f"    Warning: Could not create indicator {indicator_data.get('value', 'unknown')}: {e}")
                            continue

                    # Create TTPs
                    ttps = feed_config.get('ttps', [])
                    for ttp_data in ttps:
                        try:
                            with transaction.atomic():
                                ttp = TTPData.objects.create(
                                    name=ttp_data['name'],
                                    description=ttp_data['description'],
                                    mitre_technique_id=ttp_data['mitre_technique_id'],
                                    mitre_tactic=ttp_data['tactic'],
                                    threat_feed=threat_feed,
                                    stix_id=ttp_data.get('id', f"attack-pattern--{uuid.uuid4()}")
                                )
                                ttp_count += 1

                        except Exception as e:
                            self.stdout.write(f"    Warning: Could not create TTP {ttp_data.get('name', 'unknown')}: {e}")
                            continue

                    self.stdout.write(f"  ✓ {threat_feed.name}: {len(indicators)} indicators, {len(ttps)} TTPs")

                except ThreatFeed.DoesNotExist:
                    self.stdout.write(f"    Warning: Feed {feed_config['name']} not found")
                    continue
                except Exception as e:
                    self.stdout.write(f"    Error populating {feed_config['name']}: {e}")
                    continue

            self.stdout.write(f"Populated {indicator_count} indicators and {ttp_count} TTPs across custom feeds")

        except ImportError as e:
            self.stdout.write(f"Could not import custom feeds for data population: {e}")
        except Exception as e:
            self.stdout.write(f"Error during custom feed data population: {e}")

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write("="*100)
        self.stdout.write("DATABASE POPULATION COMPLETE!")
        self.stdout.write("="*100)
        self.stdout.write("")
        self.stdout.write("Summary of created data:")
        self.stdout.write(f"  Organizations: {len(self.organizations)}")
        self.stdout.write(f"  Users: {len(self.users)}")
        
        # Safely get counts for models that might not exist
        try:
            trust_rel_count = TrustRelationship.objects.count() if TrustRelationship else 0
        except:
            trust_rel_count = 0
        self.stdout.write(f"  Trust Relationships: {trust_rel_count}")
        
        self.stdout.write(f"  Trust Groups: {len(self.trust_groups)}")
        
        try:
            session_count = UserSession.objects.count()
        except:
            session_count = 0
        self.stdout.write(f"  User Sessions: {session_count}")
        
        try:
            feed_count = ThreatFeed.objects.count()
        except:
            feed_count = 0
        self.stdout.write(f"  Threat Feeds: {feed_count}")
        self.stdout.write("")
        self.stdout.write("Login credentials:")
        self.stdout.write("  Super Admins:")
        self.stdout.write("    Username: admin, Password: AdminPass123!")
        self.stdout.write("    Username: publisher, Password: PublisherPass123!")
        self.stdout.write("    Username: viewer, Password: ViewerPass123!")
        self.stdout.write("    Username: demo, Password: AdminPass123!")
        self.stdout.write("    Username: test, Password: AdminPass123!")
        self.stdout.write("")
        self.stdout.write("  Regular Users:")
        self.stdout.write("    All users have password: UserPass123!")
        self.stdout.write("")
        self.stdout.write("Test data ready for development and testing!")
        self.stdout.write("="*100)