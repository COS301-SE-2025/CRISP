
"""
Management command to create base users for the CRISP system
Creates admin, publisher, and viewer users with secure, environment-driven, or randomly generated credentials.
"""

import os
import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models.models import Organization
from core.user_management.models import CustomUser

User = get_user_model()

class Command(BaseCommand):
    help = 'Create base users (admin, publisher, viewer) with secure passwords.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Creating base users for CRISP system...')
        )
        passwords = {}

        try:
            with transaction.atomic():
                # Create or get BlueVision organization
                bluevision_org = self._get_or_create_bluevision_org()

                # Create base users
                admin_user, admin_password = self._create_admin_user(bluevision_org)
                passwords['admin'] = admin_password

                publisher_user, publisher_password = self._create_publisher_user(bluevision_org, admin_user)
                passwords['publisher'] = publisher_password

                viewer_user, viewer_password = self._create_viewer_user(bluevision_org, admin_user)
                passwords['viewer'] = viewer_password

                self.stdout.write(
                    self.style.SUCCESS('Base users created successfully!')
                )

                self._display_credentials(admin_user, publisher_user, viewer_user, passwords)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create base users: {str(e)}')
            )
            raise

    def _get_password(self, env_var, role):
        """Get password from environment variable or generate a random one."""
        password = os.getenv(env_var)
        if password:
            self.stdout.write(self.style.SUCCESS(f'Using password from {env_var} for {role} user.'))
            return password
        
        password = secrets.token_urlsafe(16)
        self.stdout.write(self.style.WARNING(f'{env_var} not set. Generated a random password for {role} user.'))
        return password

    def _get_or_create_bluevision_org(self):
        """Get or create the BlueVision organization"""
        self.stdout.write('Setting up BlueVision organization...')

        existing_org = Organization.objects.filter(domain='bluevision.tech').first()
        if existing_org:
            self.stdout.write(
                self.style.WARNING('BlueVision organization already exists')
            )
            return existing_org

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
        password = self._get_password('DEFAULT_ADMIN_PASSWORD', 'admin')

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
            return existing_user, password

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
        return user, password

    def _create_publisher_user(self, organization, admin_user):
        """Create publisher user"""
        self.stdout.write('Creating publisher user...')

        username = 'publisher'
        email = 'publisher@bluevision.tech'
        password = self._get_password('DEFAULT_PUBLISHER_PASSWORD', 'publisher')

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
            return existing_user, password

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
        return user, password

    def _create_viewer_user(self, organization, admin_user):
        """Create viewer user"""
        self.stdout.write('Creating viewer user...')

        username = 'viewer'
        email = 'viewer@bluevision.tech'
        password = self._get_password('DEFAULT_VIEWER_PASSWORD', 'viewer')

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
            return existing_user, password

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
        return user, password

    def _display_credentials(self, admin_user, publisher_user, viewer_user, passwords):
        """Display all user credentials"""
        self.stdout.write('
' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('BASE USER CREDENTIALS')
        )
        self.stdout.write('='*60)

        self.stdout.write('
🔑 ADMIN USER (BlueVisionAdmin):')
        self.stdout.write(f'   Username: {admin_user.username}')
        self.stdout.write(self.style.SUCCESS(f'   Password: {passwords["admin"]}'))
        self.stdout.write(f'   Email: {admin_user.email}')

        self.stdout.write('
📝 PUBLISHER USER:')
        self.stdout.write(f'   Username: {publisher_user.username}')
        self.stdout.write(self.style.SUCCESS(f'   Password: {passwords["publisher"]}'))
        self.stdout.write(f'   Email: {publisher_user.email}')

        self.stdout.write('
👀 VIEWER USER:')
        self.stdout.write(f'   Username: {viewer_user.username}')
        self.stdout.write(self.style.SUCCESS(f'   Password: {passwords["viewer"]}'))
        self.stdout.write(f'   Email: {viewer_user.email}')

        self.stdout.write('
' + '='*60)
        self.stdout.write(self.style.WARNING('Please save these passwords. They will not be shown again.'))
        self.stdout.write('
' + '='*60)
