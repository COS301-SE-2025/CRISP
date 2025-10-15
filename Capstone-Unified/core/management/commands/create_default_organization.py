from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Create default organization and assign admin user to it'

    def handle(self, *args, **options):
        try:
            # Create or get default organization
            organization, created = Organization.objects.get_or_create(
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
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created default organization: {organization.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'✓ Default organization already exists: {organization.name}')
                )
            
            # Assign admin user to organization
            try:
                admin_user = User.objects.get(username='admin')
                if not admin_user.organization:
                    admin_user.organization = organization
                    admin_user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Assigned admin user to organization: {organization.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'✓ Admin user already has organization: {admin_user.organization.name}')
                    )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING('⚠ Admin user not found - will be assigned to org when created')
                )
            
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('   DEFAULT ORGANIZATION SETUP COMPLETE'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(f'   Organization: {organization.name}')
            self.stdout.write(f'   ID: {organization.id}')
            self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating organization: {e}')
            )
