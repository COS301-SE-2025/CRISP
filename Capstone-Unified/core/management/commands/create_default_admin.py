import os
import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.models.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Create or update the default admin user with a secure password.'

    def _get_password(self):
        """Get password from environment variable or generate a random one."""
        password = os.getenv('DEFAULT_ADMIN_PASSWORD')
        if password:
            self.stdout.write(self.style.SUCCESS('Using password from DEFAULT_ADMIN_PASSWORD.'))
            return password
        
        password = secrets.token_urlsafe(16)
        self.stdout.write(self.style.WARNING('DEFAULT_ADMIN_PASSWORD not set. Generated a random password.'))
        return password

    def handle(self, *args, **options):
        username = 'admin'
        password = self._get_password()
        email = 'admin@crisp.local'

        try:
            # Create or get BlueVision ITM organization
            bluevision_org, org_created = Organization.objects.get_or_create(
                name='BlueVision ITM',
                defaults={
                    'description': 'BlueVision ITM - System Administrators with full access',
                    'organization_type': 'technology',
                    'sectors': ['technology', 'cybersecurity'],
                    'contact_email': 'admin@bluevision-itm.com',
                    'is_publisher': True,
                    'is_verified': True,
                    'is_active': True
                }
            )

            if org_created:
                self.stdout.write(
                    self.style.SUCCESS('✓ Created BlueVision ITM organization')
                )
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'✓ Admin user "{username}" already exists. Ensuring superuser privileges...')
                )
                user = User.objects.get(username=username)
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.email = email
                user.first_name = 'Admin'
                user.last_name = 'User'
                user.organization = bluevision_org
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Admin user "{username}" updated with superuser privileges and BlueVision ITM organization')
                )
            else:
                # Create new superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name='Admin',
                    last_name='User'
                )
                user.is_active = True
                user.organization = bluevision_org
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Successfully created admin user "{username}" with BlueVision ITM organization')
                )

            # Display credentials for confirmation
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('   DEFAULT ADMIN CREDENTIALS (Ready to Use)'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(f'   Username:     {username}')
            self.stdout.write(self.style.SUCCESS(f'   Password:     {password}'))
            self.stdout.write(f'   Email:        {email}')
            self.stdout.write(f'   Organization: {bluevision_org.name}')
            self.stdout.write(f'   Role:         BlueVisionAdmin (Full System Access)')
            self.stdout.write(self.style.WARNING('   Please save this password. It will not be shown again.'))
            self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {e}')
            )