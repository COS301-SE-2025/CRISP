#!/usr/bin/env python
"""
CRISP TURBO MASSIVE Database Population Script
Creates INSANE amounts of test data with parallel processing and progress bars.
MAXIMUM SPEED EDITION with tqdm progress tracking!
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random
import uuid
from faker import Faker
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import threading
from functools import partial
import time

# Install tqdm if not available
try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm for progress bars...")
    os.system("pip install tqdm")
    from tqdm import tqdm

# Configure tqdm for better display
import sys
tqdm.monitor_interval = 0
tqdm.mininterval = 0.1

# Add the project root to the Python path
# This allows Django to find the 'crisp' module and its settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')
django.setup()

from core_ut.user_management.models import CustomUser, Organization, UserSession
from core_ut.trust.models import TrustRelationship, TrustGroup, TrustLevel, TrustGroupMembership
from core_ut.audit.services.audit_service import AuditService
from django.db import transaction, connection

fake = Faker()

class TurboMassiveDatabasePopulator:
    def __init__(self):
        self.organizations = []
        self.users = []
        self.trust_levels = []
        self.trust_groups = []
        self.audit_service = AuditService()
        
        # OPTIMIZED SCALE PARAMETERS (faster execution)
        self.NUM_ORGANIZATIONS = 50       # 50 organizations (reasonable amount)
        self.USERS_PER_ORG = (10, 30)     # 10-30 users per org = 500-1,500 users
        self.NUM_AUDIT_LOGS = 5000        # 5,000 audit logs (much faster)
        self.NUM_TRUST_RELATIONSHIPS = 200  # 200 trust relationships
        self.NUM_TRUST_GROUPS = 20        # 20 trust groups
        self.NUM_USER_SESSIONS = 1000     # 1,000 user sessions
        
        # PARALLEL PROCESSING SETTINGS
        self.MAX_WORKERS = min(cpu_count(), 8)  # Reduced workers for smaller datasets
        self.BATCH_SIZE = 25  # Smaller batch size for faster processing
        
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

    def clear_existing_data(self):
        """Clear existing test data with progress tracking"""
        print("🧹 Clearing existing data...")
        
        operations = [
            ("Trust Group Memberships", TrustGroupMembership.objects.all().delete),
            ("Trust Relationships", TrustRelationship.objects.all().delete),
            ("Trust Groups", TrustGroup.objects.all().delete),
            ("User Sessions", UserSession.objects.all().delete),
            ("Non-superusers", lambda: CustomUser.objects.filter(is_superuser=False).delete()),
            ("Organizations", Organization.objects.all().delete),
        ]
        
        with tqdm(operations, desc="Clearing data", unit="table", 
                  position=0, leave=True, file=sys.stdout, dynamic_ncols=True) as pbar:
            for name, operation in pbar:
                pbar.set_description(f"Clearing {name}")
                operation()
                pbar.update(1)
                
        print("✅ Existing data cleared")

    def create_trust_levels(self):
        """Create or get trust levels"""
        print("🔐 Creating trust levels...")
        
        levels = [
            {'name': 'Basic Trust', 'level': 'public', 'numerical_value': 25, 'description': 'Basic trust level for initial partnerships', 'created_by': 'system'},
            {'name': 'Standard Trust', 'level': 'trusted', 'numerical_value': 50, 'description': 'Standard trust level for established relationships', 'created_by': 'system'},
            {'name': 'Premium Trust', 'level': 'restricted', 'numerical_value': 75, 'description': 'Premium trust level for strategic partnerships', 'created_by': 'system'},
        ]
        
        for level_data in tqdm(levels, desc="Creating trust levels", unit="level", 
                              position=0, leave=True, file=sys.stdout, dynamic_ncols=True):
            level, created = TrustLevel.objects.get_or_create(
                name=level_data['name'],
                defaults=level_data
            )
            self.trust_levels.append(level)
            
        print(f"✅ Created/verified {len(self.trust_levels)} trust levels")

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
        """Create massive number of organizations with parallel processing"""
        print(f"🏢 Creating {self.NUM_ORGANIZATIONS} organizations with {self.MAX_WORKERS} workers...")
        
        # Prepare organization data
        org_data_list = []
        for i in range(self.NUM_ORGANIZATIONS):
            company_type = random.choice(self.company_types)
            company_name = f"{fake.company().replace(',', '').replace('.', '')} {company_type}"
            
            # Create domain based on company name
            domain_base = company_name.lower().replace(' ', '').replace('&', 'and')[:15]
            domain = f"{domain_base}{i}.{random.choice(self.domain_suffixes)}"  # Add index to avoid duplicates
            
            # Map company types to valid organization types
            org_type_mapping = {
                'Government': 'government',
                'Education': 'educational',
                'Legal Services': 'government',
                'Defense': 'government',
                'Banking': 'private',
                'Financial Services': 'private',
                'Technology': 'private',
                'Healthcare': 'private',
                'Manufacturing': 'private',
                'Retail': 'private',
                'Energy': 'private',
                'Transportation': 'private',
                'Telecommunications': 'private',
                'Consulting': 'private',
                'Real Estate': 'private',
                'Insurance': 'private',
                'Media': 'private',
                'Aerospace': 'private',
                'Pharmaceuticals': 'private',
                'Automotive': 'private',
                'Construction': 'private',
                'E-commerce': 'private',
                'Logistics': 'private',
                'Entertainment': 'private',
                'Publishing': 'private'
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
        
        # Process in parallel with progress bar
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            with tqdm(total=self.NUM_ORGANIZATIONS, desc="Creating organizations", unit="org", 
                      position=0, leave=True, file=sys.stdout, dynamic_ncols=True) as pbar:
                futures = [executor.submit(self.create_organization_batch, batch) for batch in batches]
                
                for future in as_completed(futures):
                    try:
                        created_orgs = future.result()
                        self.organizations.extend(created_orgs)
                        pbar.update(len(created_orgs))
                        pbar.set_postfix({"Created": len(self.organizations)})
                    except Exception as e:
                        pbar.write(f"Warning: Batch failed: {e}")
                        
        print(f"\n✅ Created {len(self.organizations)} organizations")

    def create_super_admin_users(self):
        """Create super admin users"""
        print("👑 Creating super admin users...")
        
        super_admins = [
            ('admin', 'admin@crisp.com', 'System Administrator'),
            ('demo', 'demo@crisp.com', 'Demo Account'),
            ('test', 'test@crisp.com', 'Test Account'),
        ]
        
        for username, email, first_name in tqdm(super_admins, desc="Creating super admins", unit="admin", 
                                               position=0, leave=True, file=sys.stdout, dynamic_ncols=True):
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
            
        print(f"✅ Created {len(super_admins)} super admin users")

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
                    # Add timestamp to make username more unique
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
                        break  # Success, exit retry loop
                        
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"Failed to create user after {max_retries} retries: {e}")
                        break
                    # Add small delay before retry
                    time.sleep(0.01)
                
    def create_users(self):
        """Create massive number of users with parallel processing"""
        print(f"👥 Creating users for {len(self.organizations)} organizations...")
        
        # Prepare organization-user count pairs
        org_user_pairs = []
        total_estimated_users = 0
        
        for org in self.organizations:
            user_count = random.randint(*self.USERS_PER_ORG)
            org_user_pairs.append((org, user_count))
            total_estimated_users += user_count
            
        print(f"Estimated total users: {total_estimated_users}")
        
        # Process in parallel with progress bar
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            with tqdm(total=total_estimated_users, desc="Creating users", unit="user", 
                      position=0, leave=True, file=sys.stdout, dynamic_ncols=True) as pbar:
                futures = [executor.submit(self.create_user_batch, org_data) for org_data in org_user_pairs]
                
                total_created = 0
                for future in as_completed(futures):
                    try:
                        created_users = future.result()
                        self.users.extend(created_users)
                        batch_size = len(created_users)
                        total_created += batch_size
                        pbar.update(batch_size)
                        pbar.set_postfix({"Created": total_created, "Target": total_estimated_users})
                    except Exception as e:
                        pbar.write(f"Warning: User batch failed: {e}")
                        
        print(f"\n✅ Created {len(self.users)} users across all organizations (target was {total_estimated_users})")
        
        if len(self.users) < total_estimated_users * 0.8:  # If we created less than 80% of target
            print(f"⚠️ Warning: Only created {len(self.users)}/{total_estimated_users} users. Check for errors above.")

    def create_trust_relationship_batch(self, batch_size):
        """Create a batch of trust relationships"""
        created_relationships = []
        relationship_types = ['bilateral', 'community', 'hierarchical']
        statuses = ['pending', 'active', 'suspended']
        
        # Check if we have organizations and users to work with
        if not self.organizations or not self.users:
            print(f"Skipping trust relationships - no organizations ({len(self.organizations)}) or users ({len(self.users)}) available")
            return created_relationships
        
        attempts = 0
        max_attempts = batch_size * 10  # Increased retry attempts
        
        # Pre-filter admin users to avoid repeated filtering
        admin_users_by_org = {}
        for user in self.users:
            if user.role == 'BlueVisionAdmin' and user.organization:
                if user.organization not in admin_users_by_org:
                    admin_users_by_org[user.organization] = []
                admin_users_by_org[user.organization].append(user)
        
        # Use first super admin if no org admins found
        super_admins = [u for u in self.users if u.is_superuser]
        fallback_admin = super_admins[0] if super_admins else None
        
        # Ensure we have trust levels available
        if not self.trust_levels:
            print("Warning: No trust levels available for trust relationships")
            return created_relationships
        
        while len(created_relationships) < batch_size and attempts < max_attempts:
            attempts += 1
            
            try:
                source_org = random.choice(self.organizations)
                target_org = random.choice(self.organizations)
                
                if source_org == target_org:
                    continue
                    
                # Quick check for existing relationship (both directions)
                if TrustRelationship.objects.filter(
                    source_organization=source_org,
                    target_organization=target_org
                ).exists() or TrustRelationship.objects.filter(
                    source_organization=target_org,
                    target_organization=source_org
                ).exists():
                    continue
                    
                # Find admin users for the source org
                source_admins = admin_users_by_org.get(source_org, [])
                
                if not source_admins and fallback_admin:
                    source_admins = [fallback_admin]
                    
                if not source_admins:
                    continue
                    
                trust_level = random.choice(self.trust_levels)
                relationship_type = random.choice(relationship_types)
                status = random.choice(statuses)
                
                with transaction.atomic():
                    selected_admin = random.choice(source_admins)
                    
                    trust_rel = TrustRelationship.objects.create(
                        source_organization=source_org,
                        target_organization=target_org,
                        trust_level=trust_level,
                        relationship_type=relationship_type,
                        status=status,
                        is_active=status == 'active',
                        created_by=selected_admin,
                        created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
                        notes=fake.sentence(),
                        metadata={'created_via': 'turbo_population_script'},
                        # Set default anonymization and access levels based on trust level
                        anonymization_level=trust_level.default_anonymization_level if hasattr(trust_level, 'default_anonymization_level') else 'partial',
                        access_level=trust_level.default_access_level if hasattr(trust_level, 'default_access_level') else 'read'
                    )
                    
                    # Auto-approve some relationships for testing
                    if random.choice([True, False]):
                        trust_rel.approved_by_source = True
                        trust_rel.approved_by_source_user = selected_admin
                        if random.choice([True, False]):
                            trust_rel.approved_by_target = True
                            trust_rel.approved_by_target_user = selected_admin
                            trust_rel.status = 'active'
                        trust_rel.save()
                    
                    created_relationships.append(trust_rel)
                    
            except Exception as e:
                # Log the specific error for debugging
                print(f"Trust relationship creation error: {e}")
                continue
                
        return created_relationships

    def create_trust_relationships(self):
        """Create massive number of trust relationships with parallel processing"""
        print(f"🤝 Creating {self.NUM_TRUST_RELATIONSHIPS} trust relationships with {self.MAX_WORKERS} workers...")
        
        batch_size = self.NUM_TRUST_RELATIONSHIPS // self.MAX_WORKERS
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            with tqdm(total=self.NUM_TRUST_RELATIONSHIPS, desc="Creating trust relationships", unit="rel", 
                      position=0, leave=True, file=sys.stdout, dynamic_ncols=True) as pbar:
                futures = [executor.submit(self.create_trust_relationship_batch, batch_size) for _ in range(self.MAX_WORKERS)]
                
                total_created = 0
                for future in as_completed(futures):
                    try:
                        created_rels = future.result()
                        total_created += len(created_rels)
                        pbar.update(len(created_rels))
                        pbar.set_postfix({"Total Created": total_created})
                    except Exception as e:
                        pbar.write(f"Warning: Trust relationship batch failed: {e}")
                        
        print(f"\n✅ Created {total_created} trust relationships")

    def create_trust_group_batch(self, batch_size):
        """Create a batch of trust groups"""
        created_groups = []
        
        # Check if we have organizations and users to work with
        if not self.organizations or not self.users or not self.trust_levels:
            print(f"Skipping trust groups - no organizations ({len(self.organizations)}), users ({len(self.users)}), or trust levels ({len(self.trust_levels)}) available")
            return created_groups
        
        for i in range(batch_size):
            try:
                admin_users = [u for u in self.users if u.role == 'BlueVisionAdmin']
                if not admin_users:
                    # Use super admin as fallback
                    admin_users = [u for u in self.users if u.is_superuser]
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
                        created_by=str(admin_user),  # Store as string for compatibility
                        is_active=random.choice([True, True, False]),
                        group_type=random.choice(['industry', 'regional', 'strategic', 'community']),
                        is_public=random.choice([True, False]),
                        requires_approval=random.choice([True, False]),
                        administrators=[str(admin_user.organization.id)] if admin_user.organization else []
                    )
                    
                    # Add the admin user's organization as first member with administrator role
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
                    num_members = random.randint(2, 8)  # Reduced to avoid too many members
                    available_orgs = [org for org in self.organizations if org != admin_user.organization]
                    member_orgs = random.sample(available_orgs, min(num_members, len(available_orgs)))
                    
                    for org in member_orgs:
                        membership_type = random.choice(['member', 'member', 'member', 'moderator'])  # Favor regular members
                        TrustGroupMembership.objects.create(
                            trust_group=trust_group,
                            organization=org,
                            membership_type=membership_type,
                            is_active=random.choice([True, True, False]),  # Most active
                            joined_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
                            invited_by=str(admin_user.organization.id) if admin_user.organization else None,
                            approved_by=str(admin_user) if trust_group.requires_approval else None
                        )
                        
                    created_groups.append(trust_group)
                    
            except Exception as e:
                print(f"Trust group creation error: {e}")
                continue
                
        return created_groups

    def create_trust_groups(self):
        """Create trust groups with parallel processing"""
        print(f"🏗️ Creating {self.NUM_TRUST_GROUPS} trust groups with {self.MAX_WORKERS} workers...")
        
        batch_size = self.NUM_TRUST_GROUPS // self.MAX_WORKERS
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            with tqdm(total=self.NUM_TRUST_GROUPS, desc="Creating trust groups", unit="group", 
                      position=0, leave=True, file=sys.stdout, dynamic_ncols=True) as pbar:
                futures = [executor.submit(self.create_trust_group_batch, batch_size) for _ in range(self.MAX_WORKERS)]
                
                for future in as_completed(futures):
                    try:
                        created_groups = future.result()
                        self.trust_groups.extend(created_groups)
                        pbar.update(len(created_groups))
                        pbar.set_postfix({"Total Groups": len(self.trust_groups)})
                    except Exception as e:
                        pbar.write(f"Warning: Trust group batch failed: {e}")
                        
        print(f"\n✅ Created {len(self.trust_groups)} trust groups")

    def create_user_session_batch(self, batch_size):
        """Create a batch of user sessions with retry logic for database locks"""
        import time
        from django.db import OperationalError
        
        created_sessions = []
        
        # Check if we have users available
        if not self.users:
            print(f"Warning: No users available for session creation")
            return 0
        
        for i in range(batch_size):
            max_retries = 5
            retry_count = 0
            
            while retry_count < max_retries:
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
                        created_sessions.append(session)
                        break  # Success, exit retry loop
                        
                except OperationalError as e:
                    if "database is locked" in str(e).lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            # Exponential backoff with jitter
                            sleep_time = (2 ** retry_count) * 0.1 + random.uniform(0, 0.1)
                            time.sleep(sleep_time)
                            continue
                        else:
                            print(f"Error creating user session after {max_retries} retries: {e}")
                            break
                    else:
                        print(f"Error creating user session: {e}")
                        break
                except Exception as e:
                    print(f"Error creating user session: {e}")
                    break
                
        return len(created_sessions)

    def create_user_sessions(self):
        """Create massive number of user sessions with parallel processing"""
        print(f"🔐 Creating {self.NUM_USER_SESSIONS} user sessions with {self.MAX_WORKERS} workers...")
        
        # Check prerequisites
        if not self.users:
            print("❌ No users available for session creation!")
            return
        
        print(f"📊 Available users for sessions: {len(self.users)}")
        
        batch_size = self.NUM_USER_SESSIONS // self.MAX_WORKERS
        if batch_size == 0:
            batch_size = 1
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            with tqdm(total=self.NUM_USER_SESSIONS, desc="Creating user sessions", unit="session", 
                      position=0, leave=True, file=sys.stdout, dynamic_ncols=True) as pbar:
                futures = [executor.submit(self.create_user_session_batch, batch_size) for _ in range(self.MAX_WORKERS)]
                
                total_created = 0
                for future in as_completed(futures):
                    try:
                        created_count = future.result()
                        total_created += created_count
                        pbar.update(created_count)
                        pbar.set_postfix({"Total Sessions": total_created})
                    except Exception as e:
                        pbar.write(f"Warning: User session batch failed: {e}")
                        
        print(f"\n✅ Created {total_created} user sessions")

    def create_audit_log_batch(self, batch_size):
        """Create a batch of audit logs with improved error handling and database locking mitigation"""
        import time
        from django.db import OperationalError
        
        actions = [
            'login_success', 'login_failed', 'logout', 'profile_update', 'password_change', 
            'trust_relationship_created', 'trust_relationship_modified', 'trust_relationship_deleted',
            'user_created', 'user_updated', 'user_deactivated', 'user_deleted',
            'organization_created', 'organization_updated', 'organization_deleted',
            'data_export', 'data_import', 'report_generated', 'settings_changed', 
            'permission_granted', 'permission_revoked', 'trust_group_created',
            'trust_group_joined', 'trust_group_left', 'trust_group_deleted',
            'security_scan', 'vulnerability_detected', 'incident_reported',
            'backup_created', 'backup_restored', 'system_maintenance',
            'api_access', 'file_upload', 'file_download', 'search_performed'
        ]
        
        created_logs = 0
        
        for i in range(batch_size):
            max_retries = 5
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    user = random.choice(self.users)
                    action = random.choice(actions)
                    timestamp = fake.date_time_between(start_date='-90d', end_date='now', tzinfo=timezone.get_current_timezone())
                    
                    # Create realistic additional data
                    additional_data = {}
                    if 'trust_relationship' in action:
                        additional_data['target_organization'] = random.choice(self.organizations).name
                    elif 'user' in action:
                        additional_data['target_user'] = random.choice(self.users).username
                    elif action in ['data_export', 'report_generated']:
                        additional_data['file_size'] = random.randint(1024, 10485760)
                        additional_data['format'] = random.choice(['CSV', 'PDF', 'JSON', 'XML'])
                    
                    success = random.choice([True, True, True, False])
                    failure_reason = None if success else random.choice([
                        'Invalid credentials', 'Access denied', 'Network timeout', 
                        'Invalid input', 'System error', 'Rate limit exceeded'
                    ])
                    
                    # Use audit service (which handles DB operations)
                    result = self.audit_service.log_user_event(
                        user=user,
                        action=action,
                        ip_address=fake.ipv4(),
                        user_agent=fake.user_agent(),
                        success=success,
                        failure_reason=failure_reason,
                        additional_data=additional_data
                    )
                    
                    if result:
                        created_logs += 1
                        break  # Success, exit retry loop
                    else:
                        # log_user_event returned False, try again
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(random.uniform(0.01, 0.1))  # Small random delay
                        
                except OperationalError as e:
                    if "database is locked" in str(e).lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            # Exponential backoff with jitter
                            sleep_time = (2 ** retry_count) * 0.1 + random.uniform(0, 0.1)
                            time.sleep(sleep_time)
                            continue
                        else:
                            print(f"Failed to log user event after {max_retries} retries: {e}")
                            break
                    else:
                        print(f"Failed to log user event: {e}")
                        break
                except Exception as e:
                    print(f"Failed to log user event: {e}")
                    break
                
        return created_logs

    def create_audit_logs(self):
        """Create MASSIVE number of audit logs with optimized parallel processing"""
        print(f"📝 Creating {self.NUM_AUDIT_LOGS} audit logs with {self.MAX_WORKERS} workers...")
        
        # Reduce workers for audit logs to minimize database locking
        audit_workers = min(self.MAX_WORKERS, 4)  # Cap at 4 workers for audit logs
        batch_size = self.NUM_AUDIT_LOGS // audit_workers
        
        with ThreadPoolExecutor(max_workers=audit_workers) as executor:
            with tqdm(total=self.NUM_AUDIT_LOGS, desc="Creating audit logs", unit="log", 
                      position=0, leave=True, file=sys.stdout, dynamic_ncols=True) as pbar:
                futures = [executor.submit(self.create_audit_log_batch, batch_size) for _ in range(audit_workers)]
                
                total_created = 0
                for future in as_completed(futures):
                    try:
                        created_count = future.result()
                        total_created += created_count
                        pbar.update(created_count)
                        pbar.set_postfix({"Total Logs": total_created})
                    except Exception as e:
                        pbar.write(f"Warning: Audit log batch failed: {e}")
                        
        print(f"\n✅ Created {total_created} audit logs")

    def print_summary(self):
        """Print summary of created data"""
        print("="*100)
        print("🚀 OPTIMIZED DATABASE POPULATION COMPLETE!")
        print("="*100)
        print("")
        print("📊 Summary of created data:")
        print(f"  🏢 Organizations: {len(self.organizations)}")
        print(f"  👥 Users: {len(self.users)}")
        print(f"  🤝 Trust Relationships: {TrustRelationship.objects.count()}")
        print(f"  🏗️ Trust Groups: {len(self.trust_groups)}")
        print(f"  🔐 User Sessions: {UserSession.objects.count()}")
        print(f"  📝 Audit Logs: Approximately {self.NUM_AUDIT_LOGS}")
        print("")
        print("⚡ Performance Stats:")
        print(f"  🔧 Workers Used: {self.MAX_WORKERS}")
        print(f"  💾 Batch Size: {self.BATCH_SIZE}")
        print(f"  🖥️ CPU Cores: {cpu_count()}")
        print("")
        print("🔐 Login credentials:")
        print("  Super Admins:")
        print("    Username: admin, Password: AdminPass123!")
        print("    Username: demo, Password: AdminPass123!")
        print("    Username: test, Password: AdminPass123!")
        print("")
        print("  Regular Users:")
        print("    All users have password: UserPass123!")
        print("    Example usernames:")
        for i, org in enumerate(self.organizations[:5]):
            admin_count = len([u for u in self.users if u.organization == org and u.role == 'BlueVisionAdmin'])
            user_count = len([u for u in self.users if u.organization == org])
            print(f"    • {org.name}: {user_count} users ({admin_count} admins)")
        if len(self.organizations) > 5:
            print(f"    ... and {len(self.organizations) - 5} more organizations")
        print("")
        print("🎯 OPTIMIZED TEST DATA READY! Fast execution achieved!")
        print("="*100)

    def run(self):
        """Run the complete turbo massive database population"""
        start_time = time.time()
        
        print("🚀 Starting OPTIMIZED CRISP Database Population...")
        print("⚡ FAST EXECUTION with Parallel Processing!")
        print("="*60)
        print(f"🔧 System Configuration:")
        print(f"   • CPU Cores: {cpu_count()}")
        print(f"   • Max Workers: {self.MAX_WORKERS}")
        print(f"   • Batch Size: {self.BATCH_SIZE}")
        print("="*60)
        print(f"📊 Target Data Volume (Optimized for Speed):")
        print(f"   • {self.NUM_ORGANIZATIONS} organizations")
        print(f"   • {self.USERS_PER_ORG[0]}-{self.USERS_PER_ORG[1]} users per org = ~{self.NUM_ORGANIZATIONS * self.USERS_PER_ORG[0]}-{self.NUM_ORGANIZATIONS * self.USERS_PER_ORG[1]} users")
        print(f"   • {self.NUM_TRUST_RELATIONSHIPS} trust relationships")
        print(f"   • {self.NUM_TRUST_GROUPS} trust groups")
        print(f"   • {self.NUM_USER_SESSIONS} user sessions")
        print(f"   • {self.NUM_AUDIT_LOGS} audit logs")
        print("="*60)
        
        try:
            confirm = input("🚀 Ready to launch OPTIMIZED population? (y/N): ")
            if confirm.lower() != 'y':
                print("Cancelled.")
                return
        except EOFError:
            print("Running in non-interactive mode, proceeding automatically...")
            
        print(f"\n⏱️ Starting population at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Run all phases with progress tracking
            phases = [
                ("🧹 Phase 1/9: Clearing Data", self.clear_existing_data),
                ("🔐 Phase 2/9: Trust Levels", self.create_trust_levels),
                ("🏢 Phase 3/9: Organizations", self.create_organizations),
                ("👑 Phase 4/9: Super Admins", self.create_super_admin_users),
                ("👥 Phase 5/9: Users", self.create_users),
                ("🤝 Phase 6/9: Trust Relationships", self.create_trust_relationships),
                ("🏗️ Phase 7/9: Trust Groups", self.create_trust_groups),
                ("🔐 Phase 8/9: User Sessions", self.create_user_sessions),
                ("📝 Phase 9/9: Audit Logs", self.create_audit_logs),
            ]
            
            print(f"\n🎯 Executing {len(phases)} phases with turbo speed...")
            
            # Use a manual tqdm context manager for better control
            with tqdm(total=len(phases), desc="Overall Progress", unit="phase", 
                      position=1, leave=True, file=sys.stdout, dynamic_ncols=True,
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]') as overall_pbar:
                
                for phase_name, phase_func in phases:
                    phase_start = time.time()
                    # Update the description of the overall bar to show the current phase
                    overall_pbar.set_description(f"🚀 {phase_name}")
                    
                    # Run the phase function (which contains its own tqdm bar at position=0)
                    phase_func()
                    
                    phase_time = time.time() - phase_start
                    overall_pbar.update(1)
                    # Use set_postfix_str to show the time taken for the last completed phase
                    overall_pbar.set_postfix_str(f"Last phase: {phase_time:.1f}s", refresh=True)

            
        except Exception as e:
            print(f"❌ Error during population: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    populator = TurboMassiveDatabasePopulator()
    populator.run()