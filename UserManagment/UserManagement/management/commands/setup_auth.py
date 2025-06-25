from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import os

from ...models import CustomUser
from ...factories.user_factory import UserFactory


class Command(BaseCommand):
    help = 'Set up CRISP authentication system with initial data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a system administrator user',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the system administrator',
            default='admin'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the system administrator',
            default='admin@crisp.local'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the system administrator (will prompt if not provided)',
        )
        parser.add_argument(
            '--organization-name',
            type=str,
            help='Name of the default organization',
            default='CRISP System Administration'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip creation if users already exist',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up CRISP User Management & Authentication...')
        )
        
        # Check if users already exist
        if options['skip_existing'] and CustomUser.objects.exists():
            self.stdout.write(
                self.style.WARNING('Users already exist. Skipping setup.')
            )
            return
        
        try:
            with transaction.atomic():
                # Create default organization (mock for now)
                organization = self.create_default_organization(options['organization_name'])
                
                # Create system administrator if requested
                if options['create_superuser']:
                    self.create_system_administrator(
                        username=options['username'],
                        email=options['email'],
                        password=options['password'],
                        organization=organization
                    )
                
                # Set up default permissions and groups
                self.setup_default_permissions()
                
                # Clean up expired sessions and logs
                self.cleanup_expired_data()
                
            self.stdout.write(
                self.style.SUCCESS('CRISP User Management setup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Setup failed: {str(e)}')
            )
            raise
    
    def create_default_organization(self, name):
        """Create default organization (mock implementation)"""
        from unittest.mock import MagicMock
        
        # In a real implementation, this would create an actual Organization
        # For now, we'll mock it
        organization = MagicMock()
        organization.id = '00000000-0000-0000-0000-000000000001'
        organization.name = name
        organization.description = 'Default system administration organization'
        organization.contact_email = 'admin@crisp.local'
        
        self.stdout.write(f'Created default organization: {name}')
        return organization
    
    def create_system_administrator(self, username, email, password, organization):
        """Create system administrator user"""
        
        # Check if user already exists
        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User {username} already exists. Skipping creation.')
            )
            return
        
        # Get password if not provided
        if not password:
            password = input(f'Enter password for {username}: ')
            if not password:
                self.stdout.write(
                    self.style.ERROR('Password is required.')
                )
                return
        
        # Create system administrator
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'first_name': 'System',
            'last_name': 'Administrator',
            'organization': organization,
            'role': 'system_admin',
            'created_from_ip': '127.0.0.1',
            'user_agent': 'Management Command'
        }
        
        try:
            user = UserFactory.create_user('system_admin', user_data)
            
            # Make user staff and superuser for Django admin
            user.is_staff = True
            user.is_superuser = True
            user.is_verified = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Created system administrator: {username}')
            )
            
            return user
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create system administrator: {str(e)}')
            )
            raise
    
    def setup_default_permissions(self):
        """Set up default permissions and groups"""
        from django.contrib.auth.models import Group, Permission
        
        # Define default groups and their permissions
        groups_permissions = {
            'System Administrators': [
                'add_customuser', 'change_customuser', 'delete_customuser', 'view_customuser',
                'add_usersession', 'change_usersession', 'delete_usersession', 'view_usersession',
                'view_authenticationlog', 'delete_authenticationlog',
                'add_stixobjectpermission', 'change_stixobjectpermission', 
                'delete_stixobjectpermission', 'view_stixobjectpermission',
            ],
            'Organization Administrators': [
                'add_customuser', 'change_customuser', 'view_customuser',
                'view_usersession', 'view_authenticationlog',
                'add_stixobjectpermission', 'change_stixobjectpermission', 
                'view_stixobjectpermission',
            ],
            'Publishers': [
                'view_customuser', 'view_usersession', 'view_authenticationlog',
                'view_stixobjectpermission',
            ],
            'Viewers': [
                'view_customuser', 'view_authenticationlog',
            ]
        }
        
        for group_name, permission_codenames in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(f'Created group: {group_name}')
            
            # Add permissions to group
            for codename in permission_codenames:
                try:
                    permission = Permission.objects.get(codename=codename)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Permission {codename} does not exist. Skipping.')
                    )
            
            group.save()
        
        self.stdout.write('Set up default permissions and groups')
    
    def cleanup_expired_data(self):
        """Clean up expired sessions and old logs"""
        from ...models import UserSession, AuthenticationLog
        from datetime import timedelta
        
        # Clean up expired sessions
        expired_sessions = UserSession.objects.filter(
            expires_at__lt=timezone.now()
        )
        expired_count = expired_sessions.count()
        expired_sessions.delete()
        
        if expired_count > 0:
            self.stdout.write(f'Cleaned up {expired_count} expired sessions')
        
        # Clean up old authentication logs (older than 1 year)
        old_logs = AuthenticationLog.objects.filter(
            timestamp__lt=timezone.now() - timedelta(days=365)
        )
        old_count = old_logs.count()
        old_logs.delete()
        
        if old_count > 0:
            self.stdout.write(f'Cleaned up {old_count} old authentication logs')
    
    def create_sample_users(self, organization):
        """Create sample users for testing (optional)"""
        sample_users = [
            {
                'username': 'publisher1',
                'email': 'publisher1@crisp.local',
                'password': 'PublisherPassword123!',
                'first_name': 'Test',
                'last_name': 'Publisher',
                'role': 'publisher'
            },
            {
                'username': 'analyst1',
                'email': 'analyst1@crisp.local',
                'password': 'AnalystPassword123!',
                'first_name': 'Test',
                'last_name': 'Analyst',
                'role': 'analyst'
            },
            {
                'username': 'viewer1',
                'email': 'viewer1@crisp.local',
                'password': 'ViewerPassword123!',
                'first_name': 'Test',
                'last_name': 'Viewer',
                'role': 'viewer'
            }
        ]
        
        for user_info in sample_users:
            if not CustomUser.objects.filter(username=user_info['username']).exists():
                user_data = user_info.copy()
                user_data['organization'] = organization
                user_data['created_from_ip'] = '127.0.0.1'
                user_data['user_agent'] = 'Management Command'
                
                try:
                    user = UserFactory.create_user(user_info['role'], user_data)
                    user.is_verified = True
                    user.save()
                    
                    self.stdout.write(f'Created sample user: {user_info["username"]}')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Failed to create sample user {user_info["username"]}: {str(e)}'
                        )
                    )