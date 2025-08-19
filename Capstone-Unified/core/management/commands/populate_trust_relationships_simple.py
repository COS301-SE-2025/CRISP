"""
Simple management command to populate trust relationships using existing tables
"""
import random
import uuid
from django.core.management.base import BaseCommand
from django.db import connection
from core.models.models import Organization, CustomUser
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Populate trust relationships using existing table structure'
    
    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=40, help='Number of relationships to create')
    
    def handle(self, *args, **options):
        self.stdout.write("Populating trust relationships...")
        
        # Get organizations
        organizations = list(Organization.objects.all()[:30])
        if len(organizations) < 2:
            self.stdout.write("Need at least 2 organizations")
            return
        
        users = list(CustomUser.objects.filter(is_active=True)[:10])
        
        count = options['count']
        created = 0
        
        with connection.cursor() as cursor:
            # Clear existing relationships first - handle both possible table names
            try:
                cursor.execute("DELETE FROM trust_management_trustrelationship")
                self.stdout.write("Cleared existing trust relationships (trust_management)")
            except Exception:
                try:
                    cursor.execute("DELETE FROM trust_trustrelationship")
                    self.stdout.write("Cleared existing trust relationships (legacy)")
                except Exception:
                    self.stdout.write("No existing trust relationship table found - will create new records")
            
            relationship_types = ['bilateral', 'hierarchical', 'community', 'strategic']
            statuses = ['active', 'pending', 'suspended']
            
            for _ in range(count):
                try:
                    source_org = random.choice(organizations)
                    target_org = random.choice(organizations)
                    
                    # Don't create self-relationships
                    if source_org.id == target_org.id:
                        continue
                    
                    # Check if exists - try both table names
                    exists = False
                    try:
                        cursor.execute("""
                            SELECT COUNT(*) FROM trust_management_trustrelationship 
                            WHERE source_organization_id = %s AND target_organization_id = %s
                        """, [str(source_org.id), str(target_org.id)])
                        exists = cursor.fetchone()[0] > 0
                    except Exception:
                        try:
                            cursor.execute("""
                                SELECT COUNT(*) FROM trust_trustrelationship 
                                WHERE source_organization_id = %s AND target_organization_id = %s
                            """, [str(source_org.id), str(target_org.id)])
                            exists = cursor.fetchone()[0] > 0
                        except Exception:
                            exists = False
                    
                    if exists:
                        continue
                    
                    # Insert relationship - try to use Django ORM first, fallback to raw SQL
                    try:
                        # Try using Django ORM with trust_management models
                        from core.trust_management.models.trust_models import TrustRelationship, TrustLevel
                        
                        # Get or create a default trust level
                        trust_level, _ = TrustLevel.objects.get_or_create(
                            name='Basic Trust',
                            defaults={
                                'level': 'public',
                                'description': 'Basic trust level for partnerships',
                                'numerical_value': 25,
                                'created_by': 'system'
                            }
                        )
                        
                        TrustRelationship.objects.create(
                            source_organization=source_org,
                            target_organization=target_org,
                            trust_level=trust_level,
                            relationship_type=random.choice(relationship_types),
                            status=random.choice(statuses),
                            is_active=True,
                            created_by='population_script'
                        )
                        created += 1
                        
                    except Exception as orm_error:
                        # Fallback to raw SQL if ORM fails
                        try:
                            # Get a random user ID for created_by_id
                            user_id = random.choice(users).id if users else None
                            cursor.execute("""
                                INSERT INTO trust_management_trustrelationship 
                                (id, source_organization_id, target_organization_id, relationship_type, 
                                 status, is_active, created_at, updated_at, created_by_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, [
                                str(uuid.uuid4()),
                                str(source_org.id),
                                str(target_org.id),
                                random.choice(relationship_types),
                                random.choice(statuses),
                                True,
                                fake.date_time_this_year(),
                                fake.date_time_this_year(),
                                user_id
                            ])
                            created += 1
                        except Exception:
                            # Try legacy table name
                            try:
                                cursor.execute("""
                                    INSERT INTO trust_trustrelationship 
                                    (id, source_organization_id, target_organization_id, relationship_type, 
                                     status, access_level, anonymization_level, is_active, is_bilateral,
                                     approved_by_source, approved_by_target, 
                                     source_approval_status, target_approval_status,
                                     valid_from, created_at, updated_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, [
                                    str(uuid.uuid4()),
                                    str(source_org.id),
                                    str(target_org.id),
                                    random.choice(relationship_types),
                                    random.choice(statuses),
                                    random.choice(['read', 'contribute', 'full']),
                                    random.choice(['none', 'minimal', 'partial', 'full']),
                                    True,
                                    random.choice([True, False]),
                                    random.choice([True, False]),
                                    random.choice([True, False]),
                                    random.choice(['approved', 'pending', 'rejected']),
                                    random.choice(['approved', 'pending', 'rejected']),
                                    fake.date_time_this_year(),
                                    fake.date_time_this_year(),
                                    fake.date_time_this_year()
                                ])
                                created += 1
                            except Exception:
                                continue
                                
                except Exception as e:
                    self.stdout.write(f"Error creating relationship: {e}")
                    continue
        
        self.stdout.write(f"✅ Created {created} trust relationships")
        
        # Verify the data
        with connection.cursor() as cursor:
            # Try new table names first, fallback to legacy
            try:
                cursor.execute("SELECT COUNT(*) FROM trust_management_trustrelationship")
                total = cursor.fetchone()[0]
            except Exception:
                try:
                    cursor.execute("SELECT COUNT(*) FROM trust_trustrelationship")
                    total = cursor.fetchone()[0]
                except Exception:
                    total = 0
            
            try:
                cursor.execute("SELECT COUNT(*) FROM trust_management_trustgroup")
                groups = cursor.fetchone()[0]
            except Exception:
                try:
                    cursor.execute("SELECT COUNT(*) FROM trust_trustgroup")
                    groups = cursor.fetchone()[0]
                except Exception:
                    groups = 0
            
            try:
                cursor.execute("SELECT COUNT(*) FROM trust_management_trustgroupmembership") 
                memberships = cursor.fetchone()[0]
            except Exception:
                try:
                    cursor.execute("SELECT COUNT(*) FROM trust_trustgroupmembership") 
                    memberships = cursor.fetchone()[0]
                except Exception:
                    memberships = 0
            
            self.stdout.write(f"\\n=== VERIFICATION ===")
            self.stdout.write(f"Trust Relationships: {total}")
            self.stdout.write(f"Trust Groups: {groups}")
            self.stdout.write(f"Trust Group Memberships: {memberships}")
            
            # Show sample relationships
            if total > 0:
                self.stdout.write("\\nSample relationships:")
                try:
                    cursor.execute("""
                        SELECT 
                            o1.name as source,
                            o2.name as target,
                            tr.relationship_type,
                            tr.status
                        FROM trust_management_trustrelationship tr
                        JOIN core_organization o1 ON tr.source_organization_id = o1.id
                        JOIN core_organization o2 ON tr.target_organization_id = o2.id
                        ORDER BY tr.created_at DESC
                        LIMIT 5
                    """)
                except Exception:
                    try:
                        cursor.execute("""
                            SELECT 
                                o1.name as source,
                                o2.name as target,
                                tr.relationship_type,
                                tr.access_level,
                                tr.status
                            FROM trust_trustrelationship tr
                            JOIN core_organization o1 ON tr.source_organization_id = o1.id
                            JOIN core_organization o2 ON tr.target_organization_id = o2.id
                            ORDER BY tr.created_at DESC
                            LIMIT 5
                        """)
                    except Exception:
                        self.stdout.write("  Could not retrieve sample relationships")
                
                try:
                    for row in cursor.fetchall():
                        if len(row) >= 4:
                            self.stdout.write(f"  {row[0]} → {row[1]} ({row[2]}, {row[3]})")
                        else:
                            self.stdout.write(f"  {row[0]} → {row[1]} ({row[2]})")
                except Exception:
                    pass
        
        self.stdout.write("\\n✅ Trust relationships populated successfully!")