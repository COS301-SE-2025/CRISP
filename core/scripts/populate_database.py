#!/usr/bin/env python
"""
CRISP Database Population Script
Populates the PostgreSQL database with extensive test data for testing and development.
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
# This allows Django to find the 'crisp' module and its settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')
django.setup()

from core.user_management.models import CustomUser, Organization, UserSession
from core.trust.models import TrustRelationship, TrustGroup, TrustLevel, TrustGroupMembership
from core.audit.services.audit_service import AuditService

fake = Faker()

class DatabasePopulator:
    def __init__(self):
        self.audit_service = AuditService()
        self.organizations = []
        self.users = []
        self.trust_relationships = []
        
        # Predefined company types for realistic organizations
        self.company_types = [
            "Financial Services", "Healthcare", "Technology", "Government", 
            "Defense", "Energy", "Retail", "Manufacturing", "Education",
            "Legal Services", "Insurance", "Telecommunications", "Media",
            "Transportation", "Real Estate", "Consulting"
        ]
        
        # Predefined domains for organizations
        self.domain_suffixes = [
            "corp.com", "inc.com", "ltd.com", "group.com", "systems.com",
            "solutions.com", "tech.com", "security.com", "services.com",
            "consulting.com", "global.com", "international.com"
        ]
        
    def clear_existing_data(self):
        """Clear existing test data (optional)"""
        print("🧹 Skipping data clearing to avoid FK constraint issues...")
        print("✅ Proceeding with data population (existing data will remain)")
    
    def create_trust_levels(self):
        """Create default trust levels if they don't exist"""
        print("🔐 Creating trust levels...")
        
        trust_levels_data = [
            {
                'name': 'Public',
                'level': 'public',
                'description': 'Public information sharing with minimal restrictions',
                'numerical_value': 25,
                'default_anonymization_level': 'minimal',
                'default_access_level': 'read',
                'sharing_policies': {
                    'data_types': ['indicators', 'general_threats'],
                    'restrictions': ['no_pii', 'no_internal_details']
                }
            },
            {
                'name': 'Trusted',
                'level': 'trusted',
                'description': 'Trusted partner sharing with moderate restrictions',
                'numerical_value': 50,
                'default_anonymization_level': 'partial',
                'default_access_level': 'subscribe',
                'sharing_policies': {
                    'data_types': ['indicators', 'threats', 'incidents'],
                    'restrictions': ['anonymized_sources', 'no_attribution']
                }
            },
            {
                'name': 'Restricted',
                'level': 'restricted',
                'description': 'Restricted sharing with high-trust partners',
                'numerical_value': 75,
                'default_anonymization_level': 'none',
                'default_access_level': 'contribute',
                'sharing_policies': {
                    'data_types': ['indicators', 'threats', 'incidents', 'malware'],
                    'restrictions': ['verified_partners_only']
                }
            }
        ]
        
        self.trust_levels = []
        for level_data in trust_levels_data:
            trust_level, created = TrustLevel.objects.get_or_create(
                name=level_data['name'],
                defaults={
                    'level': level_data['level'],
                    'description': level_data['description'],
                    'numerical_value': level_data['numerical_value'],
                    'default_anonymization_level': level_data['default_anonymization_level'],
                    'default_access_level': level_data['default_access_level'],
                    'sharing_policies': level_data['sharing_policies'],
                    'is_active': True,
                    'is_system_default': True,
                    'created_by': 'system'
                }
            )
            self.trust_levels.append(trust_level)
        
        print(f"✅ Created/verified {len(self.trust_levels)} trust levels")
        
    def create_organizations(self, count=25):
        """Create organizations with realistic data"""
        print(f"🏢 Creating {count} organizations...")
        
        for i in range(count):
            company_type = random.choice(self.company_types)
            company_name = f"{fake.company().replace(',', '').replace('.', '')} {company_type}"
            
            # Create domain based on company name
            domain_base = company_name.lower().replace(' ', '').replace('&', 'and')[:15]
            domain = f"{domain_base}.{random.choice(self.domain_suffixes)}"
            
            org = Organization.objects.create(
                name=company_name,
                domain=domain,
                description=f"Leading {company_type.lower()} organization specializing in {fake.bs()}",
                contact_email=f"contact@{domain}",
                website=f"https://{domain}",
                organization_type=random.choice(['educational', 'government', 'private']),
                is_publisher=random.choice([True, False]),
                is_verified=random.choice([True, True, False]),  # 66% verified
                is_active=random.choice([True, True, True, False]),  # 75% active
                trust_metadata={
                    'industry': company_type,
                    'size': random.choice(['Small', 'Medium', 'Large', 'Enterprise']),
                    'founded': fake.year(),
                    'revenue': random.choice(['< $1M', '$1M-$10M', '$10M-$100M', '$100M+']),
                    'employees': random.randint(10, 5000),
                    'security_clearance': random.choice(['None', 'Confidential', 'Secret', 'Top Secret']),
                    'compliance': random.sample(['SOC2', 'ISO27001', 'PCI-DSS', 'HIPAA', 'GDPR'], random.randint(1, 3)),
                    'address': fake.address(),
                    'phone': fake.phone_number()
                }
            )
            self.organizations.append(org)
            
        print(f"✅ Created {len(self.organizations)} organizations")
        
    def create_users(self, users_per_org_range=(3, 15)):
        """Create users for each organization with different roles"""
        print("👥 Creating users for organizations...")
        
        roles = ['viewer', 'publisher', 'BlueVisionAdmin']
        role_weights = [70, 25, 5]  # Percentage distribution
        
        total_users = 0
        
        for org in self.organizations:
            num_users = random.randint(*users_per_org_range)
            
            for i in range(num_users):
                # Determine role based on weights
                role = random.choices(roles, weights=role_weights)[0]
                
                # Create realistic user data
                first_name = fake.first_name()
                last_name = fake.last_name()
                username = f"{first_name.lower()}.{last_name.lower()}@{org.domain}"
                
                # Special handling for admin users
                if role == 'BlueVisionAdmin':
                    username = f"admin.{fake.last_name().lower()}@{org.domain}"
                
                user = CustomUser.objects.create_user(
                    username=username,
                    email=username,
                    password='TestPass123!',  # Same password for all test users
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    organization=org,
                    is_active=random.choice([True, True, True, False]),  # 75% active
                    metadata={
                        'department': random.choice(['IT', 'Security', 'Operations', 'Management', 'Finance', 'HR']),
                        'title': fake.job(),
                        'phone': fake.phone_number(),
                        'hire_date': fake.date_between(start_date='-5y', end_date='today').isoformat(),
                        'security_training': random.choice([True, False]),
                        'last_training_date': fake.date_between(start_date='-1y', end_date='today').isoformat(),
                        'clearance_level': random.choice(['None', 'Basic', 'Intermediate', 'Advanced']),
                        'preferred_language': random.choice(['en', 'es', 'fr', 'de', 'zh']),
                        'timezone': random.choice(['UTC', 'EST', 'PST', 'GMT', 'CET'])
                    }
                )
                
                # Add some users with failed login attempts (for testing lockout)
                if random.random() < 0.1:  # 10% of users
                    user.failed_login_attempts = random.randint(1, 4)
                    user.save()
                
                self.users.append(user)
                total_users += 1
                
        print(f"✅ Created {total_users} users across all organizations")
        
    def create_super_admin_users(self):
        """Create a few super admin users for testing"""
        print("👑 Creating super admin users...")
        
        super_admins = [
            {'username': 'admin@crisp.local', 'name': 'System Administrator'},
            {'username': 'security@crisp.local', 'name': 'Security Admin'},
            {'username': 'audit@crisp.local', 'name': 'Audit Admin'}
        ]
        
        for admin_data in super_admins:
            user, created = CustomUser.objects.get_or_create(
                username=admin_data['username'],
                defaults={
                    'email': admin_data['username'],
                    'first_name': admin_data['name'].split()[0],
                    'last_name': admin_data['name'].split()[-1],
                    'role': 'BlueVisionAdmin',
                    'is_active': True,
                    'is_staff': True,
                    'is_superuser': True,
                    'metadata': {
                        'department': 'Administration',
                        'title': admin_data['name'],
                        'clearance_level': 'System Administrator',
                        'created_for': 'Testing and Administration'
                    }
                }
            )
            if created:
                user.set_password('AdminPass123!')
                user.save()
            self.users.append(user)
            
        print(f"✅ Created {len(super_admins)} super admin users")
        
    def create_trust_relationships(self):
        """Create trust relationships between organizations"""
        print("🤝 Creating trust relationships...")
        
        relationship_types = ['bilateral', 'community', 'hierarchical']
        
        # Create relationships for about 60% of organization pairs
        num_relationships = 0
        
        for i, source_org in enumerate(self.organizations):
            # Each org will have relationships with 2-5 other orgs
            num_targets = random.randint(2, min(5, len(self.organizations) - 1))
            target_orgs = random.sample([org for org in self.organizations if org != source_org], num_targets)
            
            for target_org in target_orgs:
                # Avoid duplicate relationships
                existing = TrustRelationship.objects.filter(
                    source_organization=source_org,
                    target_organization=target_org
                ).exists()
                
                if not existing:
                    trust_level = random.choice(self.trust_levels)
                    relationship_type = random.choice(relationship_types)
                    
                    # Find admin users for relationship creation
                    source_admins = [u for u in self.users if u.organization == source_org and u.role == 'BlueVisionAdmin']
                    target_admins = [u for u in self.users if u.organization == target_org and u.role == 'BlueVisionAdmin']
                    
                    # Skip if no admins available
                    if not source_admins:
                        continue
                    
                    # Create relationship
                    trust_rel = TrustRelationship.objects.create(
                        source_organization=source_org,
                        target_organization=target_org,
                        trust_level=trust_level,
                        relationship_type=relationship_type,
                        status=random.choice(['pending', 'active', 'suspended']),
                        is_active=random.choice([True, True, False]),  # 66% active
                        created_by=random.choice(source_admins),
                        valid_until=timezone.now() + timedelta(days=random.randint(30, 730)),
                        source_approval_status=random.choice(['pending', 'approved']),
                        target_approval_status=random.choice(['pending', 'approved']) if target_admins else 'pending',
                        metadata={
                            'purpose': random.choice(['Threat Intelligence Sharing', 'Incident Response', 'Security Collaboration', 'Information Exchange']),
                            'classification': random.choice(['Public', 'Internal', 'Confidential', 'Restricted']),
                            'data_types': random.sample(['IOCs', 'Malware Samples', 'Incident Reports', 'Vulnerability Data', 'Threat Analysis'], random.randint(1, 3)),
                            'communication_channels': random.sample(['Email', 'API', 'Portal', 'Phone', 'Secure Messaging'], random.randint(1, 2)),
                            'review_frequency': random.choice(['Monthly', 'Quarterly', 'Bi-annually', 'Annually'])
                        }
                    )
                    
                    self.trust_relationships.append(trust_rel)
                    num_relationships += 1
                    
        print(f"✅ Created {num_relationships} trust relationships")
        
    def create_trust_groups(self):
        """Create trust groups for organizations"""
        print("🏷️ Creating trust groups...")
        
        group_types = [
            'Financial Sector', 'Healthcare Alliance', 'Government Agencies',
            'Technology Partners', 'Critical Infrastructure', 'Defense Contractors',
            'Energy Sector', 'Regional Consortium', 'Industry Specific',
            'Emergency Response', 'Cybersecurity Coalition'
        ]
        
        num_groups = 0
        
        # Create 5-8 trust groups
        for i in range(random.randint(5, 8)):
            group_name = random.choice(group_types)
            group_type = random.choice(group_types)
            
            # Select 3-8 organizations for this group
            group_orgs = random.sample(self.organizations, random.randint(3, min(8, len(self.organizations))))
            
            trust_group = TrustGroup.objects.create(
                name=f"{group_name} Trust Group {i+1}",
                description=f"Collaborative trust group for {group_name.lower()} organizations to share threat intelligence and security information.",
                group_type=group_type,
                is_public=random.choice([True, False]),
                requires_approval=random.choice([True, True, False]),  # 66% require approval
                default_trust_level=random.choice(self.trust_levels),
                is_active=True,
                created_by=str(random.choice([u for u in self.users if u.role == 'BlueVisionAdmin' and u.organization]).id),
                group_policies={
                    'focus_areas': random.sample(['Malware Analysis', 'APT Tracking', 'Vulnerability Management', 'Incident Response', 'Threat Hunting'], random.randint(2, 4)),
                    'meeting_frequency': random.choice(['Weekly', 'Bi-weekly', 'Monthly', 'Quarterly']),
                    'classification_level': random.choice(['Unclassified', 'Restricted', 'Confidential']),
                    'established_date': fake.date_between(start_date='-2y', end_date='today').isoformat(),
                    'member_requirements': random.sample(['Security Clearance', 'Industry Certification', 'Background Check', 'NDA Required'], random.randint(1, 2)),
                    'sharing_permissions': random.sample(['read', 'write', 'admin'], random.randint(1, 2)),
                    'data_retention_days': random.choice([30, 90, 180, 365])
                },
                administrators=[str(random.choice([u for u in self.users if u.role == 'BlueVisionAdmin' and u.organization]).organization.id)]
            )
            
            # Add organizations to the group through TrustGroupMembership
            for org in group_orgs:
                TrustGroupMembership.objects.create(
                    trust_group=trust_group,
                    organization=org,
                    membership_type=random.choice(['member', 'administrator', 'moderator']),
                    is_active=True,
                    invited_by=str(random.choice([u for u in self.users if u.role == 'BlueVisionAdmin' and u.organization]).organization.id),
                    approved_by=str(random.choice([u for u in self.users if u.role == 'BlueVisionAdmin' and u.organization]).id)
                )
            num_groups += 1
            
        print(f"✅ Created {num_groups} trust groups")
        
    def create_user_sessions(self):
        """Create recent user sessions for realistic activity"""
        print("🔐 Creating user sessions...")
        
        num_sessions = 0
        
        # Create sessions for 70% of active users
        active_users = [u for u in self.users if u.is_active]
        users_with_sessions = random.sample(active_users, int(len(active_users) * 0.7))
        
        for user in users_with_sessions:
            # Each user might have 1-3 recent sessions
            for _ in range(random.randint(1, 3)):
                session_start = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
                session_duration = timedelta(minutes=random.randint(15, 480))  # 15 minutes to 8 hours
                
                UserSession.objects.create(
                    user=user,
                    session_token=fake.uuid4(),
                    refresh_token=fake.uuid4(),
                    ip_address=fake.ipv4(),
                    device_info={
                        'user_agent': fake.user_agent(),
                        'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                        'platform': random.choice(['Windows', 'macOS', 'Linux', 'Mobile']),
                        'device_fingerprint': fake.uuid4(),
                        'login_method': random.choice(['password', '2fa', 'sso']),
                        'location': fake.city(),
                        'country': fake.country_code()
                    },
                    is_trusted_device=random.choice([True, False]),
                    is_active=random.choice([True, False]),
                    expires_at=session_start + session_duration,
                    last_activity=session_start + session_duration
                )
                num_sessions += 1
                
        print(f"✅ Created {num_sessions} user sessions")
        
    def create_audit_logs(self):
        """Create audit log entries for system activity"""
        print("📝 Creating audit logs...")
        
        actions = [
            'login', 'logout', 'profile_update', 'password_change', 'trust_relationship_created',
            'trust_relationship_modified', 'user_created', 'user_deactivated', 'organization_updated',
            'data_export', 'report_generated', 'settings_changed', 'permission_granted',
            'permission_revoked', 'trust_group_joined', 'trust_group_left'
        ]
        
        num_logs = 0
        
        # Create 200-500 audit log entries
        for _ in range(random.randint(200, 500)):
            user = random.choice(self.users)
            action = random.choice(actions)
            timestamp = fake.date_time_between(start_date='-90d', end_date='now', tzinfo=timezone.get_current_timezone())
            
            # Create audit log through the service
            success = random.choice([True, True, True, False])  # 75% success rate
            self.audit_service.log_user_event(
                user=user,
                action=action,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                success=success,
                failure_reason=fake.sentence() if not success else None,
                additional_data={
                    'target': fake.word(),
                    'duration_ms': random.randint(100, 5000),
                    'resource_accessed': fake.uri_path(),
                    'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                    'status_code': random.choice([200, 201, 400, 401, 403, 500])
                },
                target_user=random.choice(self.users) if action in ['user_created', 'user_deactivated'] else None,
                target_organization=random.choice(self.organizations) if action in ['organization_updated'] else None
            )
            num_logs += 1
            
        print(f"✅ Created {num_logs} audit log entries")
        
    def print_summary(self):
        """Print a summary of created data"""
        print("\n" + "="*60)
        print("🎉 DATABASE POPULATION COMPLETE!")
        print("="*60)
        print(f"📊 SUMMARY:")
        print(f"  • Organizations: {len(self.organizations)}")
        print(f"  • Users: {len(self.users)}")
        print(f"  • Trust Relationships: {len(self.trust_relationships)}")
        print(f"  • Trust Groups: {TrustGroup.objects.count()}")
        print(f"  • User Sessions: {UserSession.objects.count()}")
        print("")
        print("🔑 TEST LOGIN CREDENTIALS:")
        print("  • Password for all users: TestPass123!")
        print("  • Super Admins:")
        print("    - admin@crisp.local / AdminPass123!")
        print("    - security@crisp.local / AdminPass123!")
        print("    - audit@crisp.local / AdminPass123!")
        print("")
        print("👥 USER ROLES DISTRIBUTION:")
        for role in ['viewer', 'publisher', 'BlueVisionAdmin']:
            count = CustomUser.objects.filter(role=role).count()
            print(f"  • {role}: {count} users")
        print("")
        print("🏢 ORGANIZATIONS:")
        for org in self.organizations[:5]:  # Show first 5
            admin_count = CustomUser.objects.filter(organization=org, role='BlueVisionAdmin').count()
            user_count = CustomUser.objects.filter(organization=org).count()
            print(f"  • {org.name}: {user_count} users ({admin_count} admins)")
        print(f"  ... and {len(self.organizations) - 5} more organizations")
        print("")
        print("✅ Ready for testing! You can now log in with any user and explore the system.")
        print("="*60)
        
    def run(self):
        """Run the complete database population"""
        print("🚀 Starting CRISP Database Population...")
        print("This will create extensive test data for development and testing.")
        print("")
        
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
    populator = DatabasePopulator()
    populator.run()