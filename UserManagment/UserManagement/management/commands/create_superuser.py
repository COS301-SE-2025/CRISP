from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
import getpass

from ...models import CustomUser
from ...factories.user_factory import UserFactory


class Command(BaseCommand):
    help = 'Create a CRISP system administrator (superuser)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the superuser'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser (will prompt if not provided)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='First name for the superuser',
            default='System'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Last name for the superuser',
            default='Administrator'
        )
        parser.add_argument(
            '--organization-name',
            type=str,
            help='Organization name for the superuser',
            default='CRISP System Administration'
        )
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help='Run in non-interactive mode (all fields must be provided)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Creating CRISP System Administrator...')
        )
        
        try:
            if options['non_interactive']:
                superuser = self.create_superuser_non_interactive(options)
            else:
                superuser = self.create_superuser_interactive(options)
            
            if superuser:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'System administrator "{superuser.username}" created successfully!'
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'User ID: {superuser.id}'
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Email: {superuser.email}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create superuser: {str(e)}')
            )
            raise
    
    def create_superuser_interactive(self, options):
        """Create superuser with interactive prompts"""
        
        # Get username
        username = options.get('username')
        while not username:
            username = input('Username: ').strip()
            if not username:
                self.stdout.write(self.style.ERROR('Username cannot be empty'))
                continue
            
            # Check if username already exists
            if CustomUser.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR(f'Username "{username}" already exists'))
                username = None
                continue
        
        # Get email
        email = options.get('email')
        while not email:
            email = input('Email: ').strip()
            if not email:
                self.stdout.write(self.style.ERROR('Email cannot be empty'))
                continue
            
            # Basic email validation
            if '@' not in email:
                self.stdout.write(self.style.ERROR('Please enter a valid email address'))
                email = None
                continue
            
            # Check if email already exists
            if CustomUser.objects.filter(email=email).exists():
                self.stdout.write(self.style.ERROR(f'Email "{email}" already exists'))
                email = None
                continue
        
        # Get password
        password = options.get('password')
        while not password:
            password = getpass.getpass('Password: ')
            if not password:
                self.stdout.write(self.style.ERROR('Password cannot be empty'))
                continue
            
            password_confirm = getpass.getpass('Password (again): ')
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Passwords do not match'))
                password = None
                continue
        
        # Get first name
        first_name = options.get('first_name')
        if not first_name:
            first_name = input(f'First name (default: System): ').strip() or 'System'
        
        # Get last name
        last_name = options.get('last_name')
        if not last_name:
            last_name = input(f'Last name (default: Administrator): ').strip() or 'Administrator'
        
        # Get organization name
        org_name = options.get('organization_name')
        if not org_name:
            org_name = input(
                f'Organization name (default: CRISP System Administration): '
            ).strip() or 'CRISP System Administration'
        
        return self.create_superuser_with_data(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            organization_name=org_name
        )
    
    def create_superuser_non_interactive(self, options):
        """Create superuser without interactive prompts"""
        required_fields = ['username', 'email', 'password']
        
        for field in required_fields:
            if not options.get(field):
                raise ValueError(f'{field} is required in non-interactive mode')
        
        # Check if username already exists
        if CustomUser.objects.filter(username=options['username']).exists():
            raise ValueError(f'Username "{options["username"]}" already exists')
        
        # Check if email already exists
        if CustomUser.objects.filter(email=options['email']).exists():
            raise ValueError(f'Email "{options["email"]}" already exists')
        
        return self.create_superuser_with_data(
            username=options['username'],
            email=options['email'],
            password=options['password'],
            first_name=options.get('first_name', 'System'),
            last_name=options.get('last_name', 'Administrator'),
            organization_name=options.get('organization_name', 'CRISP System Administration')
        )
    
    def create_superuser_with_data(self, username, email, password, first_name, 
                                 last_name, organization_name):
        """Create superuser with provided data"""
        
        with transaction.atomic():
            # Create mock organization
            organization = self.create_or_get_organization(organization_name)
            
            # Prepare user data
            user_data = {
                'username': username,
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'organization': organization,
                'created_from_ip': '127.0.0.1',
                'user_agent': 'Management Command - create_superuser'
            }
            
            # Create system administrator using factory
            user = UserFactory.create_user('BlueVisionAdmin', user_data)
            
            # Set additional superuser properties
            user.is_staff = True
            user.is_superuser = True
            user.is_verified = True
            user.is_active = True
            user.save()
            
            # Log creation
            self.stdout.write(f'Created system administrator user: {username}')
            self.stdout.write(f'Organization: {organization.name}')
            self.stdout.write(f'Django admin access: Enabled')
            self.stdout.write(f'Verification status: Verified')
            
            return user
    
    def create_or_get_organization(self, name):
        """Create or get organization (mock implementation)"""
        from unittest.mock import MagicMock
        
        # In real implementation, this would create/get actual Organization
        # For now, we'll mock it with consistent ID based on name
        organization = MagicMock()
        
        # Generate consistent UUID based on organization name
        import hashlib
        import uuid
        
        name_hash = hashlib.md5(name.encode()).hexdigest()
        org_uuid = str(uuid.UUID(name_hash))
        
        organization.id = org_uuid
        organization.name = name
        organization.description = f'Organization for {name}'
        organization.contact_email = 'admin@crisp.local'
        organization.website = None
        organization.created_at = None
        
        self.stdout.write(f'Using organization: {name} (ID: {org_uuid})')
        
        return organization
    
    def validate_user_data(self, username, email, password):
        """Validate user data before creation"""
        errors = []
        
        # Validate username
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        if len(username) > 30:
            errors.append('Username must not exceed 30 characters')
        
        # Validate email
        if '@' not in email or '.' not in email.split('@')[1]:
            errors.append('Please enter a valid email address')
        
        # Validate password
        if len(password) < 12:
            errors.append('Password must be at least 12 characters long')
        
        # Check password complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not has_upper:
            errors.append('Password must contain at least one uppercase letter')
        if not has_lower:
            errors.append('Password must contain at least one lowercase letter')
        if not has_digit:
            errors.append('Password must contain at least one digit')
        if not has_special:
            errors.append('Password must contain at least one special character')
        
        if errors:
            raise ValidationError(errors)
        
        return True