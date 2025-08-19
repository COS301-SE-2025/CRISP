"""
Management command to populate trust relationships and fix trust data display
"""
import random
import logging
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from core.models.models import Organization, CustomUser
from faker import Faker

fake = Faker()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populate trust relationships and fix trust data display'
    
    def add_arguments(self, parser):
        parser.add_argument('--relationships', type=int, default=50, help='Number of trust relationships to create')
        parser.add_argument('--fix-tables', action='store_true', help='Fix table structure issues')
    
    def handle(self, *args, **options):
        self.stdout.write("Starting Trust Data Population...")
        
        if options['fix_tables']:
            self.fix_table_structure()
        
        self.populate_trust_relationships(options['relationships'])
        self.verify_trust_data()
    
    def fix_table_structure(self):
        """Check if Django migrations need to be run"""
        self.stdout.write("Checking Django migration status...")
        
        try:
            from core.trust_management.models.trust_models import TrustRelationship, TrustLevel
            # Try to access the models to see if migrations are applied
            trust_rel_count = TrustRelationship.objects.count()
            trust_level_count = TrustLevel.objects.count()
            self.stdout.write(f"✅ Trust management tables are properly set up")
            self.stdout.write(f"   Current trust relationships: {trust_rel_count}")
            self.stdout.write(f"   Current trust levels: {trust_level_count}")
        except Exception as e:
            self.stdout.write(f"⚠️ Trust management tables may need migrations: {e}")
            self.stdout.write("Please run: python manage.py makemigrations trust_management && python manage.py migrate")
    
    def populate_trust_relationships(self, count):
        """Populate trust relationships using Django ORM"""
        self.stdout.write(f"Creating {count} trust relationships...")
        
        organizations = list(Organization.objects.all()[:50])  # Limit to prevent too many combinations
        if len(organizations) < 2:
            self.stdout.write("Not enough organizations to create trust relationships")
            return
        
        users = list(CustomUser.objects.filter(is_active=True)[:10])
        relationship_types = ['bilateral', 'hierarchical', 'community', 'federation']
        statuses = ['pending', 'active', 'suspended', 'revoked']
        anonymization_levels = ['none', 'minimal', 'partial', 'full']
        access_levels = ['none', 'read', 'subscribe', 'contribute', 'full']
        
        created_count = 0
        
        try:
            # Import the trust management models
            from core.trust_management.models.trust_models import TrustRelationship, TrustLevel
            
            # Get or create default trust levels
            trust_levels = []
            for level_name, level_type, numerical_value in [
                ('Basic Trust', 'public', 25),
                ('Standard Trust', 'trusted', 50), 
                ('Premium Trust', 'restricted', 75)
            ]:
                trust_level, created = TrustLevel.objects.get_or_create(
                    name=level_name,
                    defaults={
                        'level': level_type,
                        'description': f'{level_name} for partnerships',
                        'numerical_value': numerical_value,
                        'created_by': 'population_script'
                    }
                )
                trust_levels.append(trust_level)
            
            for _ in range(count):
                try:
                    # Pick two different organizations
                    source_org = random.choice(organizations)
                    target_org = random.choice(organizations)
                    
                    if source_org.id == target_org.id:
                        continue
                    
                    # Check if relationship already exists
                    if TrustRelationship.objects.filter(
                        source_organization=source_org,
                        target_organization=target_org
                    ).exists():
                        continue
                    
                    # Create the relationship using Django ORM
                    trust_relationship = TrustRelationship.objects.create(
                        source_organization=source_org,
                        target_organization=target_org,
                        relationship_type=random.choice(relationship_types),
                        trust_level=random.choice(trust_levels),
                        status=random.choice(statuses),
                        is_bilateral=random.choice([True, False]),
                        is_active=True,
                        anonymization_level=random.choice(anonymization_levels),
                        access_level=random.choice(access_levels),
                        approved_by_source=random.choice([True, False]),
                        approved_by_target=random.choice([True, False]),
                        created_by=random.choice(users) if users else None,
                        notes=f"Auto-generated trust relationship between {source_org.name} and {target_org.name}"
                    )
                    
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"Error creating trust relationship: {e}")
                    continue
                    
        except ImportError as e:
            self.stdout.write(f"Could not import trust management models: {e}")
            self.stdout.write("Skipping trust relationship creation")
            return
        
        self.stdout.write(f"✅ Created {created_count} trust relationships")
    
    def verify_trust_data(self):
        """Verify trust data is properly populated"""
        self.stdout.write("\\n=== TRUST DATA VERIFICATION ===")
        
        try:
            from core.trust_management.models.trust_models import TrustRelationship, TrustGroup, TrustGroupMembership
            
            # Check trust relationships using Django ORM
            relationships_count = TrustRelationship.objects.count()
            self.stdout.write(f"Trust Relationships: {relationships_count}")
            
            # Check trust groups  
            groups_count = TrustGroup.objects.count()
            self.stdout.write(f"Trust Groups: {groups_count}")
            
            # Check trust group memberships
            memberships_count = TrustGroupMembership.objects.count()
            self.stdout.write(f"Trust Group Memberships: {memberships_count}")
            
            # Sample relationships
            if relationships_count > 0:
                self.stdout.write("\\nSample Trust Relationships:")
                sample_relationships = TrustRelationship.objects.select_related(
                    'source_organization', 'target_organization', 'trust_level'
                )[:3]
                
                for tr in sample_relationships:
                    self.stdout.write(
                        f"  {tr.source_organization.name} → {tr.target_organization.name} "
                        f"({tr.relationship_type}, {tr.trust_level.name}, {tr.status})"
                    )
            
            # Sample trust groups
            if groups_count > 0:
                self.stdout.write("\\nSample Trust Groups:")
                sample_groups = TrustGroup.objects.prefetch_related('group_memberships')[:3]
                
                for tg in sample_groups:
                    member_count = tg.group_memberships.count()
                    self.stdout.write(f"  {tg.name}: {member_count} members")
                    
        except ImportError as e:
            self.stdout.write(f"Could not import trust management models for verification: {e}")
        except Exception as e:
            self.stdout.write(f"Error during verification: {e}")
        
        self.stdout.write("\\n✅ Trust data verification complete!")