"""
Management command to populate trust relationships and fix trust data display
"""
import random
import logging
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from core.models.models import Organization, 
from core.user_management.models import CustomUser
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
        """Fix table structure issues for trust management"""
        self.stdout.write("Checking and fixing table structure...")
        
        with connection.cursor() as cursor:
            try:
                # Check if trust_management_trustrelationship table exists
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables 
                    WHERE table_name = 'trust_management_trustrelationship'
                """)
                
                if cursor.fetchone()[0] == 0:
                    self.stdout.write("Creating trust_management_trustrelationship table...")
                    
                    # Create the missing table with correct UUID foreign keys
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS trust_management_trustrelationship (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            source_organization_id UUID NOT NULL,
                            target_organization_id UUID NOT NULL,
                            relationship_type VARCHAR(50) NOT NULL DEFAULT 'bilateral',
                            trust_score INTEGER NOT NULL DEFAULT 50,
                            status VARCHAR(20) NOT NULL DEFAULT 'active',
                            established_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            created_by_id INTEGER,
                            metadata JSONB DEFAULT '{}',
                            is_mutual BOOLEAN DEFAULT true,
                            expires_at TIMESTAMP WITH TIME ZONE,
                            notes TEXT,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(source_organization_id, target_organization_id),
                            FOREIGN KEY (source_organization_id) REFERENCES core_organization(id) ON DELETE CASCADE,
                            FOREIGN KEY (target_organization_id) REFERENCES core_organization(id) ON DELETE CASCADE,
                            FOREIGN KEY (created_by_id) REFERENCES core_customuser(id) ON DELETE SET NULL
                        )
                    """)
                    
                    # Copy data from trust_trustrelationship if it exists and has data
                    cursor.execute("SELECT COUNT(*) FROM trust_trustrelationship")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        cursor.execute("""
                            INSERT INTO trust_management_trustrelationship 
                            (source_organization_id, target_organization_id, relationship_type, trust_score, status, created_at, updated_at)
                            SELECT source_organization_id, target_organization_id, 
                                   COALESCE(relationship_type, 'bilateral'),
                                   COALESCE(trust_score, 50),
                                   COALESCE(status, 'active'),
                                   COALESCE(created_at, CURRENT_TIMESTAMP),
                                   COALESCE(updated_at, CURRENT_TIMESTAMP)
                            FROM trust_trustrelationship
                        """)
                        self.stdout.write(f"Copied {count} trust relationships")
                    
                    self.stdout.write("✅ Created trust_management_trustrelationship table")
                else:
                    self.stdout.write("✅ trust_management_trustrelationship table exists")
                    
            except Exception as e:
                self.stdout.write(f"Error fixing table structure: {e}")
    
    def populate_trust_relationships(self, count):
        """Populate trust relationships directly using SQL"""
        self.stdout.write(f"Creating {count} trust relationships...")
        
        organizations = list(Organization.objects.all()[:50])  # Limit to prevent too many combinations
        if len(organizations) < 2:
            self.stdout.write("Not enough organizations to create trust relationships")
            return
        
        users = list(CustomUser.objects.filter(is_active=True)[:10])
        relationship_types = ['bilateral', 'hierarchical', 'community', 'strategic']
        statuses = ['active', 'pending', 'suspended']
        
        created_count = 0
        
        with connection.cursor() as cursor:
            for _ in range(count):
                try:
                    # Pick two different organizations
                    source_org = random.choice(organizations)
                    target_org = random.choice(organizations)
                    
                    if source_org.id == target_org.id:
                        continue
                    
                    # Check if relationship already exists
                    cursor.execute("""
                        SELECT COUNT(*) FROM trust_management_trustrelationship 
                        WHERE source_organization_id = %s AND target_organization_id = %s
                    """, [str(source_org.id), str(target_org.id)])
                    
                    if cursor.fetchone()[0] > 0:
                        continue
                    
                    # Create the relationship
                    cursor.execute("""
                        INSERT INTO trust_management_trustrelationship 
                        (source_organization_id, target_organization_id, relationship_type, 
                         trust_score, status, established_date, created_by_id, is_mutual)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        str(source_org.id),  # Ensure UUID is passed as string
                        str(target_org.id),  # Ensure UUID is passed as string
                        random.choice(relationship_types),
                        random.randint(25, 95),
                        random.choice(statuses),
                        fake.date_time_this_year(),
                        random.choice(users).id if users else None,
                        random.choice([True, False])
                    ])
                    
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"Error creating trust relationship: {e}")
                    continue
        
        self.stdout.write(f"✅ Created {created_count} trust relationships")
    
    def verify_trust_data(self):
        """Verify trust data is properly populated"""
        self.stdout.write("\\n=== TRUST DATA VERIFICATION ===")
        
        with connection.cursor() as cursor:
            # Check trust relationships
            cursor.execute("SELECT COUNT(*) FROM trust_management_trustrelationship")
            relationships_count = cursor.fetchone()[0]
            self.stdout.write(f"Trust Relationships: {relationships_count}")
            
            # Check trust groups  
            cursor.execute("SELECT COUNT(*) FROM trust_management_trustgroup")
            groups_count = cursor.fetchone()[0]
            self.stdout.write(f"Trust Groups: {groups_count}")
            
            # Check trust group memberships
            cursor.execute("SELECT COUNT(*) FROM trust_management_trustgroupmembership")
            memberships_count = cursor.fetchone()[0]
            self.stdout.write(f"Trust Group Memberships: {memberships_count}")
            
            # Sample relationships
            if relationships_count > 0:
                self.stdout.write("\\nSample Trust Relationships:")
                cursor.execute("""
                    SELECT 
                        o1.name as source_org,
                        o2.name as target_org,
                        tr.relationship_type,
                        tr.trust_score,
                        tr.status
                    FROM trust_management_trustrelationship tr
                    JOIN core_organization o1 ON tr.source_organization_id = o1.id
                    JOIN core_organization o2 ON tr.target_organization_id = o2.id
                    LIMIT 3
                """)
                
                for row in cursor.fetchall():
                    self.stdout.write(f"  {row[0]} → {row[1]} ({row[2]}, Score: {row[3]}, {row[4]})")
            
            # Sample trust groups
            if groups_count > 0:
                self.stdout.write("\\nSample Trust Groups:")
                cursor.execute("""
                    SELECT name, description, 
                           (SELECT COUNT(*) FROM trust_management_trustgroupmembership 
                            WHERE trust_group_id = tg.id) as member_count
                    FROM trust_management_trustgroup tg
                    LIMIT 3
                """)
                
                for row in cursor.fetchall():
                    self.stdout.write(f"  {row[0]}: {row[2]} members")
        
        self.stdout.write("\\n✅ Trust data verification complete!")