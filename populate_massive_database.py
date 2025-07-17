#!/usr/bin/env python
"""
CRISP MASSIVE Database Population Script
Creates INSANE amounts of test data for stress testing and demonstration.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random
import uuid
from faker import Faker

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')
django.setup()

from core.user_management.models import CustomUser, Organization, UserSession
from core.trust.models import TrustRelationship, TrustGroup, TrustLevel, TrustGroupMembership
from core.services.audit_service import AuditService

fake = Faker()

class MassiveDatabasePopulator:
    def __init__(self):
        self.organizations = []
        self.users = []
        self.trust_levels = []
        self.trust_groups = []
        self.audit_service = AuditService()
        
        # MASSIVE SCALE PARAMETERS
        self.NUM_ORGANIZATIONS = 200      # 200 organizations
        self.USERS_PER_ORG = (15, 50)    # 15-50 users per org = 3,000-10,000 users
        self.NUM_AUDIT_LOGS = 50000      # 50,000 audit logs
        self.NUM_TRUST_RELATIONSHIPS = 1000  # 1,000 trust relationships
        self.NUM_TRUST_GROUPS = 50       # 50 trust groups
        self.NUM_USER_SESSIONS = 10000   # 10,000 user sessions
        
        # Company data for realistic organizations
        self.company_types = [
            'Technology', 'Healthcare', 'Financial Services', 'Manufacturing', 
            'Retail', 'Energy', 'Transportation', 'Telecommunications', 
            'Government', 'Education', 'Legal Services', 'Consulting',
            'Real Estate', 'Insurance', 'Media', 'Defense', 'Aerospace',
            'Pharmaceuticals', 'Automotive', 'Construction'
        ]
        
        self.domain_suffixes = [
            'com', 'corp', 'inc', 'ltd', 'org', 'gov', 'edu', 'net',
            'international.com', 'global.com', 'security.com', 'solutions.com',
            'group.com', 'consulting.com', 'services.com'
        ]

    def clear_existing_data(self):
        """Clear existing test data"""
        print("🧹 Clearing existing data (this may take a while)...")
        
        # Clear in correct order to avoid foreign key issues
        TrustGroupMembership.objects.all().delete()
        TrustRelationship.objects.all().delete() 
        TrustGroup.objects.all().delete()
        UserSession.objects.all().delete()
        
        # Delete non-superuser users first
        CustomUser.objects.filter(is_superuser=False).delete()
        
        # Delete organizations (will cascade to remaining users)
        Organization.objects.all().delete()
        
        print("✅ Existing data cleared")

    def create_trust_levels(self):
        """Create or get trust levels"""
        print("🔐 Creating trust levels...")
        
        levels = [
            {'name': 'Basic', 'level': 1, 'numerical_value': 1.0, 'description': 'Basic trust level for initial partnerships'},
            {'name': 'Standard', 'level': 2, 'numerical_value': 2.0, 'description': 'Standard trust level for established relationships'},
            {'name': 'Premium', 'level': 3, 'numerical_value': 3.0, 'description': 'Premium trust level for strategic partnerships'},
        ]
        
        for level_data in levels:
            level, created = TrustLevel.objects.get_or_create(
                name=level_data['name'],
                defaults=level_data
            )
            self.trust_levels.append(level)
            
        print(f"✅ Created/verified {len(self.trust_levels)} trust levels")

    def create_organizations(self):
        """Create massive number of organizations"""
        print(f"🏢 Creating {self.NUM_ORGANIZATIONS} organizations...")
        
        for i in range(self.NUM_ORGANIZATIONS):
            if i % 50 == 0:
                print(f"  Created {i}/{self.NUM_ORGANIZATIONS} organizations...")
                
            company_type = random.choice(self.company_types)
            company_name = f"{fake.company().replace(',', '').replace('.', '')} {company_type}"
            
            # Create domain based on company name
            domain_base = company_name.lower().replace(' ', '').replace('&', 'and')[:15]
            domain = f"{domain_base}.{random.choice(self.domain_suffixes)}"
            
            org = Organization.objects.create(
                name=company_name,
                domain=domain,
                organization_type=company_type.lower(),
                description=fake.catch_phrase(),
                contact_email=f"contact@{domain}",
                website=f"https://www.{domain}",
                is_active=random.choice([True, True, True, False]),  # 75% active
                is_publisher=random.choice([True, False]),
                is_verified=random.choice([True, True, False]),  # 66% verified
                trust_metadata={'industry': company_type, 'country': fake.country()}
            )
            self.organizations.append(org)
            
        print(f"✅ Created {len(self.organizations)} organizations")

    def create_super_admin_users(self):
        """Create super admin users"""
        print("👑 Creating super admin users...")
        
        super_admins = [
            ('admin', 'admin@crisp.com', 'System Administrator'),
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
            
        print(f"✅ Created {len(super_admins)} super admin users")

    def create_users(self):
        """Create massive number of users"""
        print(f"👥 Creating users for {len(self.organizations)} organizations...")
        print("This will create 3,000-10,000 users total...")
        
        roles = ['viewer', 'publisher', 'BlueVisionAdmin']
        role_weights = [70, 25, 5]  # Percentage distribution
        
        total_users = 0
        
        for i, org in enumerate(self.organizations):
            if i % 25 == 0:
                print(f"  Processing organization {i+1}/{len(self.organizations)}...")
                
            num_users = random.randint(*self.USERS_PER_ORG)
            
            for j in range(num_users):
                role = random.choices(roles, weights=role_weights)[0]
                
                first_name = fake.first_name()
                last_name = fake.last_name()
                username = f"{first_name.lower()}.{last_name.lower()}@{org.domain}"
                
                user = CustomUser.objects.create(
                    username=username,
                    email=username,
                    first_name=first_name,
                    last_name=last_name,
                    organization=org,
                    role=role,
                    is_active=random.choice([True, True, True, False]),  # 75% active
                    is_publisher=random.choice([True, False]),
                    is_verified=random.choice([True, True, False]),  # 66% verified
                    date_joined=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
                )
                user.set_password('UserPass123!')
                user.save()
                
                self.users.append(user)
                total_users += 1
                
        print(f"✅ Created {total_users} users across all organizations")

    def create_trust_relationships(self):
        """Create massive number of trust relationships"""
        print(f"🤝 Creating {self.NUM_TRUST_RELATIONSHIPS} trust relationships...")
        
        relationship_types = ['bilateral', 'community', 'hierarchical']
        statuses = ['pending', 'active', 'suspended', 'terminated']
        
        created_count = 0
        attempts = 0
        max_attempts = self.NUM_TRUST_RELATIONSHIPS * 3
        
        while created_count < self.NUM_TRUST_RELATIONSHIPS and attempts < max_attempts:
            attempts += 1
            
            if attempts % 100 == 0:
                print(f"  Created {created_count}/{self.NUM_TRUST_RELATIONSHIPS} relationships...")
            
            source_org = random.choice(self.organizations)
            target_org = random.choice(self.organizations)
            
            if source_org == target_org:
                continue
                
            # Check for existing relationship
            existing = TrustRelationship.objects.filter(
                source_organization=source_org,
                target_organization=target_org
            ).exists()
            
            if existing:
                continue
                
            # Find admin users
            source_admins = [u for u in self.users if u.organization == source_org and u.role == 'BlueVisionAdmin']
            
            if not source_admins:
                continue
                
            trust_level = random.choice(self.trust_levels)
            relationship_type = random.choice(relationship_types)
            status = random.choice(statuses)
            
            trust_rel = TrustRelationship.objects.create(
                source_organization=source_org,
                target_organization=target_org,
                trust_level=trust_level,
                relationship_type=relationship_type,
                status=status,
                is_active=status == 'active',
                created_by=random.choice(source_admins),
                created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
                description=fake.sentence(),
                metadata={'created_via': 'massive_population_script'}
            )
            
            created_count += 1
            
        print(f"✅ Created {created_count} trust relationships")

    def create_trust_groups(self):
        """Create trust groups"""
        print(f"🏗️ Creating {self.NUM_TRUST_GROUPS} trust groups...")
        
        for i in range(self.NUM_TRUST_GROUPS):
            admin_user = random.choice([u for u in self.users if u.role == 'BlueVisionAdmin'])
            
            group_name = f"{fake.word().title()} {random.choice(['Alliance', 'Network', 'Consortium', 'Partnership', 'Coalition'])}"
            
            trust_group = TrustGroup.objects.create(
                name=group_name,
                description=fake.paragraph(),
                trust_level=random.choice(self.trust_levels),
                created_by=admin_user,
                is_active=random.choice([True, True, False]),  # 66% active
                metadata={'group_type': random.choice(['industry', 'regional', 'strategic'])}
            )
            
            # Add random organizations to the group
            num_members = random.randint(3, 10)
            member_orgs = random.sample(self.organizations, min(num_members, len(self.organizations)))
            
            for org in member_orgs:
                TrustGroupMembership.objects.create(
                    group=trust_group,
                    organization=org,
                    role=random.choice(['member', 'admin', 'observer']),
                    joined_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
                )
                
            self.trust_groups.append(trust_group)
            
        print(f"✅ Created {len(self.trust_groups)} trust groups")

    def create_user_sessions(self):
        """Create massive number of user sessions"""
        print(f"🔐 Creating {self.NUM_USER_SESSIONS} user sessions...")
        
        for i in range(self.NUM_USER_SESSIONS):
            if i % 1000 == 0:
                print(f"  Created {i}/{self.NUM_USER_SESSIONS} sessions...")
                
            user = random.choice(self.users)
            session_start = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
            session_duration = timedelta(minutes=random.randint(5, 480))  # 5 min to 8 hours
            
            UserSession.objects.create(
                user=user,
                session_key=fake.uuid4(),
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                created_at=session_start,
                last_activity=session_start + session_duration,
                is_active=random.choice([True, False])
            )
            
        print(f"✅ Created {self.NUM_USER_SESSIONS} user sessions")

    def create_audit_logs(self):
        """Create MASSIVE number of audit logs"""
        print(f"📝 Creating {self.NUM_AUDIT_LOGS} audit logs...")
        
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
        
        for i in range(self.NUM_AUDIT_LOGS):
            if i % 5000 == 0:
                print(f"  Created {i}/{self.NUM_AUDIT_LOGS} audit logs...")
                
            user = random.choice(self.users)
            action = random.choice(actions)
            timestamp = fake.date_time_between(start_date='-90d', end_date='now', tzinfo=timezone.get_current_timezone())
            
            # Create realistic additional data based on action
            additional_data = {}
            if 'trust_relationship' in action:
                additional_data['target_organization'] = random.choice(self.organizations).name
            elif 'user' in action:
                additional_data['target_user'] = random.choice(self.users).username
            elif action in ['data_export', 'report_generated']:
                additional_data['file_size'] = random.randint(1024, 10485760)  # 1KB to 10MB
                additional_data['format'] = random.choice(['CSV', 'PDF', 'JSON', 'XML'])
            
            # Create audit log through the service
            success = random.choice([True, True, True, False])  # 75% success rate
            failure_reason = None if success else random.choice([
                'Invalid credentials', 'Access denied', 'Network timeout', 
                'Invalid input', 'System error', 'Rate limit exceeded'
            ])
            
            self.audit_service.log_user_event(
                user=user,
                action=action,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                success=success,
                failure_reason=failure_reason,
                additional_data=additional_data
            )
            
        print(f"✅ Created {self.NUM_AUDIT_LOGS} audit logs")

    def print_summary(self):
        """Print summary of created data"""
        print("="*80)
        print("🎉 MASSIVE DATABASE POPULATION COMPLETE!")
        print("="*80)
        print("")
        print("📊 Summary of created data:")
        print(f"  🏢 Organizations: {len(self.organizations)}")
        print(f"  👥 Users: {len(self.users)}")
        print(f"  🤝 Trust Relationships: {TrustRelationship.objects.count()}")
        print(f"  🏗️ Trust Groups: {len(self.trust_groups)}")
        print(f"  🔐 User Sessions: {UserSession.objects.count()}")
        print(f"  📝 Audit Logs: Approximately {self.NUM_AUDIT_LOGS}")
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
        print(f"    ... and {len(self.organizations) - 5} more organizations")
        print("")
        print("✅ STRESS TEST READY! Your database now has INSANE amounts of data!")
        print("="*80)

    def run(self):
        """Run the complete massive database population"""
        print("🚀 Starting MASSIVE CRISP Database Population...")
        print("⚠️  WARNING: This will create MASSIVE amounts of data!")
        print(f"   • {self.NUM_ORGANIZATIONS} organizations")
        print(f"   • {self.USERS_PER_ORG[0]}-{self.USERS_PER_ORG[1]} users per org = ~{self.NUM_ORGANIZATIONS * self.USERS_PER_ORG[0]}-{self.NUM_ORGANIZATIONS * self.USERS_PER_ORG[1]} users")
        print(f"   • {self.NUM_TRUST_RELATIONSHIPS} trust relationships")
        print(f"   • {self.NUM_TRUST_GROUPS} trust groups")
        print(f"   • {self.NUM_USER_SESSIONS} user sessions")
        print(f"   • {self.NUM_AUDIT_LOGS} audit logs")
        print("")
        
        try:
            confirm = input("Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Cancelled.")
                return
        except EOFError:
            # Running in non-interactive mode, proceed automatically
            print("Running in non-interactive mode, proceeding automatically...")
            pass
            
        try:
            self.clear_existing_data()
            self.create_trust_levels()
            self.create_organizations()
            self.create_super_admin_users()
            self.create_users()
            self.create_trust_relationships()
            self.create_trust_groups()
            self.create_user_sessions()
            self.create_audit_logs()
            self.print_summary()
            
        except Exception as e:
            print(f"❌ Error during population: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    populator = MassiveDatabasePopulator()
    populator.run()