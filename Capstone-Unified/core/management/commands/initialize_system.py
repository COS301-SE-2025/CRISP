"""
Management command to initialize the unified CRISP system with default data
Creates default organizations, users, and system configuration
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models.models import Organization
from core.user_management.models import CustomUser
from core.services.organization_service import OrganizationService
from core.services.user_service import UserService

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize the CRISP unified system with default data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-superuser',
            action='store_true',
            help='Skip creating superuser if one already exists',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@crisp-system.org',
            help='Email for the admin user',
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Username for the admin user',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            help='Password for the admin user (will prompt if not provided)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting CRISP Unified System initialization...')
        )

        try:
            with transaction.atomic():
                # Create BlueVision organization
                bluevision_org = self._create_bluevision_organization()
                
                # Create admin user
                admin_user = self._create_admin_user(
                    organization=bluevision_org,
                    username=options['admin_username'],
                    email=options['admin_email'],
                    password=options['admin_password'],
                    skip_if_exists=options['skip_superuser']
                )
                
                # Create sample organizations
                sample_orgs = self._create_sample_organizations()
                
                # Create sample users for each organization
                self._create_sample_users(sample_orgs, admin_user)
                
                # Set up system configuration
                self._setup_system_configuration()
                
                self.stdout.write(
                    self.style.SUCCESS('System initialization completed successfully!')
                )
                
                self._display_summary(admin_user, bluevision_org, sample_orgs)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'System initialization failed: {str(e)}')
            )
            raise

    def _create_bluevision_organization(self):
        """Create the BlueVision administrative organization"""
        self.stdout.write('Creating BlueVision organization...')
        
        org_service = OrganizationService()
        
        # Check if BlueVision org already exists
        existing_org = Organization.objects.filter(domain='bluevision.tech').first()
        if existing_org:
            self.stdout.write(
                self.style.WARNING('BlueVision organization already exists')
            )
            return existing_org
        
        # Primary user data for BlueVision admin
        primary_user_data = {
            'username': 'bluevision_admin',
            'email': 'admin@bluevision.tech',
            'password': 'AdminPass123',
            'first_name': 'BlueVision',
            'last_name': 'Administrator'
        }

        result = org_service.create_organization(
            name='BlueVision Technologies',
            domain='bluevision.tech',
            organization_type='technology_vendor',
            description='BlueVision Technologies - CRISP Platform Administrator',
            contact_email='admin@bluevision.tech',
            contact_phone='+1-555-CRISP-01',
            primary_user_data=primary_user_data,
            created_by=None  # System creation
        )
        
        if result['success']:
            org = Organization.objects.get(id=result['organization_id'])
            self.stdout.write(
                self.style.SUCCESS(f'Created BlueVision organization: {org.name}')
            )
            return org
        else:
            raise Exception(f"Failed to create BlueVision organization: {result['message']}")

    def _create_admin_user(self, organization, username, email, password, skip_if_exists):
        """Create the system administrator user"""
        self.stdout.write('Creating admin user...')
        
        # Check if admin user already exists
        existing_user = CustomUser.objects.filter(username=username).first()
        if existing_user:
            self.stdout.write(
                self.style.WARNING(f'Admin user {username} already exists, updating...')
            )
            # Update existing user
            existing_user.first_name = 'System'
            existing_user.last_name = 'Administrator'
            existing_user.role = 'BlueVisionAdmin'
            existing_user.organization = organization
            existing_user.is_staff = True
            existing_user.is_superuser = True
            existing_user.is_verified = True
            existing_user.save()
            return existing_user
        
        # Get password if not provided
        if not password:
            import getpass
            password = getpass.getpass('Enter password for admin user: ')
            if not password:
                raise Exception('Password is required for admin user')
        
        user_service = UserService()
        result = user_service.create_user(
            username=username,
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator',
            role='BlueVisionAdmin',
            organization_id=str(organization.id),
            created_by=None  # System creation
        )
        
        if result['success']:
            user = CustomUser.objects.get(id=result['user_id'])
            user.is_staff = True
            user.is_superuser = True
            user.is_verified = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {user.username}')
            )
            return user
        else:
            raise Exception(f"Failed to create admin user: {result['message']}")

    def _create_sample_organizations(self):
        """Create sample organizations for demonstration"""
        self.stdout.write('Creating sample organizations...')
        
        org_service = OrganizationService()
        sample_orgs = []
        
        organizations_data = [
            {
                'name': 'TechCorp Security',
                'domain': 'techcorp.com',
                'organization_type': 'private_sector',
                'description': 'Technology company focused on cybersecurity solutions',
                'contact_email': 'security@techcorp.com'
            },
            {
                'name': 'Federal Cyber Defense',
                'domain': 'fedcyber.gov',
                'organization_type': 'government',
                'description': 'Federal government cybersecurity agency',
                'contact_email': 'contact@fedcyber.gov'
            },
            {
                'name': 'University Research Lab',
                'domain': 'cyberlab.edu',
                'organization_type': 'academic',
                'description': 'Academic cybersecurity research laboratory',
                'contact_email': 'research@cyberlab.edu'
            }
        ]
        
        for org_data in organizations_data:
            # Check if organization already exists
            existing_org = Organization.objects.filter(domain=org_data['domain']).first()
            if existing_org:
                self.stdout.write(
                    self.style.WARNING(f'Organization {org_data["name"]} already exists')
                )
                sample_orgs.append(existing_org)
                continue
            
            result = org_service.create_organization(
                name=org_data['name'],
                domain=org_data['domain'],
                organization_type=org_data['organization_type'],
                description=org_data['description'],
                contact_email=org_data['contact_email'],
                created_by=None  # System creation
            )
            
            if result['success']:
                org = Organization.objects.get(id=result['organization_id'])
                sample_orgs.append(org)
                self.stdout.write(
                    self.style.SUCCESS(f'Created organization: {org.name}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create organization {org_data["name"]}: {result["message"]}')
                )
        
        return sample_orgs

    def _create_sample_users(self, sample_orgs, admin_user):
        """Create sample users for each organization"""
        self.stdout.write('Creating sample users...')
        
        user_service = UserService()
        
        for org in sample_orgs:
            # Create a publisher for each organization
            publisher_username = f'{org.domain.split(".")[0]}_publisher'
            
            # Check if user already exists
            if CustomUser.objects.filter(username=publisher_username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {publisher_username} already exists')
                )
                continue
            
            result = user_service.create_user(
                username=publisher_username,
                email=f'publisher@{org.domain}',
                password='DefaultPassword123!',  # Should be changed on first login
                first_name='Organization',
                last_name='Publisher',
                role='publisher',
                organization_id=str(org.id),
                created_by=admin_user
            )
            
            if result['success']:
                user = CustomUser.objects.get(id=result['user_id'])
                user.is_verified = True
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created publisher user: {user.username} for {org.name}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create publisher for {org.name}: {result["message"]}')
                )

    def _setup_system_configuration(self):
        """Set up initial system configuration"""
        self.stdout.write('Setting up system configuration...')
        
        # Create necessary directories
        import os
        from django.conf import settings
        
        directories = [
            'logs',
            'uploads',
            'static',
            'media'
        ]
        
        for directory in directories:
            dir_path = os.path.join(settings.BASE_DIR, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                self.stdout.write(f'Created directory: {directory}')
        
        self.stdout.write(
            self.style.SUCCESS('System configuration completed')
        )

    def _display_summary(self, admin_user, bluevision_org, sample_orgs):
        """Display initialization summary"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('CRISP UNIFIED SYSTEM INITIALIZATION SUMMARY')
        )
        self.stdout.write('='*50)
        
        self.stdout.write(f'Admin User: {admin_user.username} ({admin_user.email})')
        self.stdout.write(f'BlueVision Org: {bluevision_org.name}')
        
        self.stdout.write('\nSample Organizations:')
        for org in sample_orgs:
            user_count = CustomUser.objects.filter(organization=org).count()
            self.stdout.write(f'  - {org.name} ({org.domain}) - {user_count} users')
        
        self.stdout.write('\nNext Steps:')
        self.stdout.write('1. Change default passwords for all sample users')
        self.stdout.write('2. Configure email settings in .env file')
        self.stdout.write('3. Set up trust relationships between organizations')
        self.stdout.write('4. Import threat intelligence feeds')
        self.stdout.write('5. Configure STIX/TAXII endpoints')
        
        self.stdout.write('\nAPI Endpoints:')
        self.stdout.write('  Authentication: /api/auth/')
        self.stdout.write('  Users: /api/users/')
        self.stdout.write('  Organizations: /api/organizations/')
        self.stdout.write('  Trust: /api/trust/')
        self.stdout.write('  System Status: /api/')
        
        self.stdout.write('\n' + '='*50)