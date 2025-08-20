from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
import random
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate database with sample users, organizations, and trust relationships'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        if options['clear']:
            self.clear_data()
        
        users_count = options['users']
        
        with transaction.atomic():
            # Create users
            users = self.create_users(users_count)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {len(users)} users')
            )
            
        # Update API endpoints with more realistic data
        self.update_api_data()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Database populated successfully!\n'
                f'Created {len(users)} users with various roles.\n'
                f'Mock organizations and trust relationships are available via API.'
            )
        )

    def clear_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        
        # Keep the bluevision_admin user
        User.objects.exclude(username='bluevision_admin').delete()
        
        self.stdout.write(self.style.SUCCESS('Existing data cleared (kept bluevision_admin)'))

    def create_users(self, count):
        """Create sample users with different roles"""
        self.stdout.write(f'Creating {count} users...')
        
        users = []
        roles = ['user', 'publisher', 'admin', 'BlueVisionAdmin']
        role_weights = [0.6, 0.25, 0.1, 0.05]  # Most users are basic users
        
        organizations = [
            'Financial Corp', 'Tech Security Inc', 'Government Agency',
            'Healthcare Systems', 'University Research', 'Defense Contractor',
            'Consulting Group', 'Retail Chain', 'Energy Company', 'Telecom Provider'
        ]
        
        first_names = [
            'Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Avery',
            'Cameron', 'Drew', 'Sage', 'Blake', 'Quinn', 'Reese', 'Dakota',
            'Phoenix', 'River', 'Skylar', 'Emery', 'Finley', 'Hayden'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
            'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez',
            'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
            'Taylor', 'Moore', 'Jackson', 'Martin'
        ]
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            org = random.choice(organizations)
            
            # Create unique username
            base_username = f"{first_name.lower()}.{last_name.lower()}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Select role based on weights
            role = random.choices(roles, weights=role_weights)[0]
            
            user = User.objects.create_user(
                username=username,
                email=f"{username}@{org.lower().replace(' ', '')}.com",
                password='password123',
                first_name=first_name,
                last_name=last_name,
                is_staff=role in ['admin', 'BlueVisionAdmin'],
                is_superuser=role == 'BlueVisionAdmin',
                is_active=True,
            )
            
            users.append(user)
            
            if (i + 1) % 10 == 0 or (i + 1) == count:
                self.stdout.write(f'Created {i + 1}/{count} users...')
        
        # Create some specific demo users
        demo_users = [
            {
                'username': 'alice.analyst',
                'email': 'alice@security.com',
                'first_name': 'Alice',
                'last_name': 'Analyst',
                'role': 'user',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'username': 'bob.publisher',
                'email': 'bob@threatintel.com', 
                'first_name': 'Bob',
                'last_name': 'Publisher',
                'role': 'publisher',
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'carol.admin',
                'email': 'carol@bluevision.com',
                'first_name': 'Carol',
                'last_name': 'Administrator', 
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        ]
        
        for demo_user in demo_users:
            if not User.objects.filter(username=demo_user['username']).exists():
                user = User.objects.create_user(
                    username=demo_user['username'],
                    email=demo_user['email'],
                    password='password123',
                    first_name=demo_user['first_name'],
                    last_name=demo_user['last_name'],
                    is_staff=demo_user['is_staff'],
                    is_superuser=demo_user['is_superuser'],
                    is_active=True
                )
                users.append(user)
        
        return users

    def update_api_data(self):
        """Update the API endpoints with more realistic data based on created users"""
        # Initialize trust levels
        from core.models.models import TrustLevel
        
        trust_levels = [
            {'name': 'high', 'description': 'High trust level', 'numerical_value': 80},
            {'name': 'medium', 'description': 'Medium trust level', 'numerical_value': 50},
            {'name': 'low', 'description': 'Low trust level', 'numerical_value': 20}
        ]
        
        for level_data in trust_levels:
            TrustLevel.objects.get_or_create(
                name=level_data['name'],
                defaults={
                    'description': level_data['description'],
                    'numerical_value': level_data['numerical_value']
                }
            )
        
        self.stdout.write('✅ Trust levels initialized')
        self.stdout.write('API data updated with realistic information.')
        self.stdout.write('Organizations, trust relationships, and metrics will show populated data.')

    def show_summary(self):
        """Show summary of created data"""
        total_users = User.objects.count()
        admin_users = User.objects.filter(is_superuser=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        active_users = User.objects.filter(is_active=True).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n--- Database Population Summary ---\n'
                f'Total Users: {total_users}\n'
                f'Admin Users: {admin_users}\n' 
                f'Staff Users: {staff_users}\n'
                f'Active Users: {active_users}\n'
                f'\n--- Sample Credentials ---\n'
                f'alice.analyst / password123 (User)\n'
                f'bob.publisher / password123 (Publisher)\n'
                f'carol.admin / password123 (Admin)\n'
                f'bluevision_admin / AdminPass123 (BlueVision Admin)\n'
            )
        )