"""
Management command to initialize the unified CRISP system with default data
Creates default organizations, users, and system configuration
"""

import os
import secrets
import getpass
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passwords = {}

    def add_arguments(self, parser):
        parser.add_argument('--admin-password', type=str, help='Password for the main admin user.')

    def _get_password(self, role_key, env_var):
        """Get password from environment or generate a random one."""
        password = os.getenv(env_var)
        if password:
            self.stdout.write(self.style.SUCCESS(f'Using password from {env_var} for {role_key}'))
        else:
            password = secrets.token_urlsafe(16)
            self.stdout.write(self.style.WARNING(f'{env_var} not set. Generated a random password for {role_key}.'))
        self.passwords[role_key] = password
        return password

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting CRISP Unified System initialization...'))

        try:
            with transaction.atomic():
                bluevision_org = self._create_bluevision_organization()
                admin_user = self._create_admin_user(organization=bluevision_org, password=options['admin_password'])
                sample_orgs = self._create_sample_organizations()
                self._create_sample_users(sample_orgs, admin_user)
                self._setup_system_configuration()
                
                self.stdout.write(self.style.SUCCESS('System initialization completed successfully!'))
                self._display_summary(admin_user, bluevision_org, sample_orgs)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'System initialization failed: {str(e)}'))
            raise

    def _create_bluevision_organization(self):
        self.stdout.write('Creating BlueVision organization...')
        existing_org = Organization.objects.filter(domain='bluevision.tech').first()
        if existing_org:
            self.stdout.write(self.style.WARNING('BlueVision organization already exists'))
            return existing_org

        primary_user_data = {
            'username': 'bluevision_admin',
            'email': 'admin@bluevision.tech',
            'password': self._get_password('bluevision_admin', 'DEFAULT_BLUEVISION_ADMIN_PASSWORD'),
            'first_name': 'BlueVision',
            'last_name': 'Administrator'
        }

        org_service = OrganizationService()
        result = org_service.create_organization(
            name='BlueVision Technologies',
            domain='bluevision.tech',
            organization_type='technology_vendor',
            primary_user_data=primary_user_data,
            created_by=None
        )
        
        if result['success']:
            org = Organization.objects.get(id=result['organization_id'])
            self.stdout.write(self.style.SUCCESS(f'Created BlueVision organization: {org.name}'))
            return org
        else:
            raise Exception(f