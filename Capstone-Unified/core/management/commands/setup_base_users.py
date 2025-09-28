"""
Management command to create base users for the CRISP system
Creates admin, publisher, and viewer users with default credentials for Docker setup
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models.models import Organization 
from core.user_management.models import CustomUser
from core.services.organization_service import OrganizationService
from core.services.user_service import UserService

User = get_user_model()

class Command(BaseCommand):
    help = 'Create base users (admin, publisher, viewer) for Docker setup'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Creating base users for CRISP system...')
        )

        try:
            with transaction.atomic():
                # Create or get BlueVision organization
                bluevision_org = self._get_or_create_bluevision_org()
                
                # Create base users
                admin_user = self._create_admin_user(bluevision_org)
                publisher_user = self._create_publisher_user(bluevision_org, admin_user)
                viewer_user = self._create_viewer_user(bluevision_org, admin_user)
                
                self.stdout.write(
                    self.style.SUCCESS('Base users created successfully!')
                )
                
                self._display_credentials(admin_user, publisher_user, viewer_user)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create base users: {str(e)}')
            )
            raise

    def _get_or_create_bluevision_org(self):
        """Get or create the BlueVision organization"""
        self.stdout.write('Setting up BlueVision organization...')
        
        # Check if BlueVision org already exists
        existing_org = Organization.objects.filter(domain='bluevision.tech').first()
        if existing_org:
            self.stdout.write(
                self.style.WARNING('BlueVision organization already exists')
            )
            return existing_org
        
        # Create organization directly without service to avoid primary user requirement
        org = Organization.objects.create(
            name='BlueVision Technologies',
            domain='bluevision.tech',
            organization_type='private',
            description='BlueVision Technologies - CRISP Platform Administrator',
            contact_email='admin@bluevision.tech',
            website='https://bluevision.tech',
            is_publisher=True,
            is_verified=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created BlueVision organization: {org.name}')
        )
        return org

    def _create_admin_user(self, organization):
        """Create admin user with BlueVisionAdmin role"""
        self.stdout.write('Creating admin user...')
        
        username = 'admin'
        email = 'admin@bluevision.tech'
        password = 'AdminPass123!'
        
        # Check if admin user already exists
        existing_user = CustomUser.objects.filter(username=username).first()
        if existing_user:
            self.stdout.write(
                self.style.WARNING(f'Admin user {username} already exists, updating...')
            )
            existing_user.set_password(password)
            existing_user.role = 'BlueVisionAdmin'
            existing_user.is_staff = True
            existing_user.is_superuser = True
            existing_user.is_verified = True
            existing_user.is_active = True
            existing_user.save()
            return existing_user
        
        # Create user directly
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator',
            role='BlueVisionAdmin',
            organization=organization,
            is_staff=True,
            is_superuser=True,
            is_verified=True,
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created admin user: {user.username}')
        )
        return user

    def _create_publisher_user(self, organization, admin_user):
        """Create publisher user"""
        self.stdout.write('Creating publisher user...')
        
        username = 'publisher'
        email = 'publisher@bluevision.tech'
        password = 'PublisherPass123!'
        
        # Check if publisher user already exists
        existing_user = CustomUser.objects.filter(username=username).first()
        if existing_user:
            self.stdout.write(
                self.style.WARNING(f'Publisher user {username} already exists, updating...')
            )
            existing_user.set_password(password)
            existing_user.role = 'publisher'
            existing_user.is_publisher = True
            existing_user.is_verified = True
            existing_user.is_active = True
            existing_user.save()
            return existing_user
        
        # Create user directly
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Content',
            last_name='Publisher',
            role='publisher',
            organization=organization,
            is_publisher=True,
            is_verified=True,
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created publisher user: {user.username}')
        )
        return user

    def _create_viewer_user(self, organization, admin_user):
        """Create viewer user"""
        self.stdout.write('Creating viewer user...')
        
        username = 'viewer'
        email = 'viewer@bluevision.tech'
        password = 'ViewerPass123!'
        
        # Check if viewer user already exists
        existing_user = CustomUser.objects.filter(username=username).first()
        if existing_user:
            self.stdout.write(
                self.style.WARNING(f'Viewer user {username} already exists, updating...')
            )
            existing_user.set_password(password)
            existing_user.role = 'viewer'
            existing_user.is_verified = True
            existing_user.is_active = True
            existing_user.save()
            return existing_user
        
        # Create user directly
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Content',
            last_name='Viewer',
            role='viewer',
            organization=organization,
            is_verified=True,
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created viewer user: {user.username}')
        )
        return user

    def _display_credentials(self, admin_user, publisher_user, viewer_user):
        """Display all user credentials"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('BASE USER CREDENTIALS FOR DOCKER SETUP')
        )
        self.stdout.write('='*60)
        
        self.stdout.write('\nADMIN USER (BlueVisionAdmin):')
        self.stdout.write(f'   Username: admin')
        self.stdout.write(f'   Password: AdminPass123!')
        self.stdout.write(f'   Email: admin@bluevision.tech')
        self.stdout.write(f'   Role: BlueVisionAdmin')
        self.stdout.write(f'   Permissions: Full system access, superuser')
        
        self.stdout.write('\nPUBLISHER USER:')
        self.stdout.write(f'   Username: publisher')
        self.stdout.write(f'   Password: PublisherPass123!')
        self.stdout.write(f'   Email: publisher@bluevision.tech')
        self.stdout.write(f'   Role: publisher')
        self.stdout.write(f'   Permissions: Create and publish threat intelligence')
        
        self.stdout.write('\nVIEWER USER:')
        self.stdout.write(f'   Username: viewer')
        self.stdout.write(f'   Password: ViewerPass123!')
        self.stdout.write(f'   Email: viewer@bluevision.tech')
        self.stdout.write(f'   Role: viewer')
        self.stdout.write(f'   Permissions: View threat intelligence data')
        
        self.stdout.write('\nACCESS URLS:')
        self.stdout.write(f'   Frontend UI: http://localhost:5173')
        self.stdout.write(f'   Backend API: http://localhost:8000')
        self.stdout.write(f'   Django Admin: http://localhost:8000/admin')
        
        self.stdout.write('\nUSAGE:')
        self.stdout.write('   1. Use admin credentials for full system management')
        self.stdout.write('   2. Use publisher credentials to create and share threat data')
        self.stdout.write('   3. Use viewer credentials for read-only access')
        self.stdout.write('   4. Change passwords after first login for security')
        
        self.stdout.write('\n' + '='*60)