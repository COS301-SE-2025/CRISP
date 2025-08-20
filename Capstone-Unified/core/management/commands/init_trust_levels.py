"""
Management command to initialize default trust levels
"""

from django.core.management.base import BaseCommand
from core.models.models import TrustLevel


class Command(BaseCommand):
    help = 'Initialize default trust levels in the database'
    
    def handle(self, *args, **options):
        self.stdout.write('Initializing default trust levels...')
        
        # Default trust levels
        default_trust_levels = [
            {
                'name': 'Public',
                'level': 'public',
                'description': 'Public trust level - data can be shared openly with minimal restrictions',
                'numerical_value': 10,
                'default_anonymization_level': 'minimal',
                'default_access_level': 'read',
                'sharing_policies': {
                    'allow_public_sharing': True,
                    'require_attribution': False,
                    'allow_modification': True
                }
            },
            {
                'name': 'Trusted',
                'level': 'trusted', 
                'description': 'Trusted level - data shared with verified organizations with moderate restrictions',
                'numerical_value': 50,
                'default_anonymization_level': 'partial',
                'default_access_level': 'subscribe',
                'sharing_policies': {
                    'allow_public_sharing': False,
                    'require_attribution': True,
                    'allow_modification': False
                }
            },
            {
                'name': 'Restricted',
                'level': 'restricted',
                'description': 'Restricted level - highly sensitive data with strict access controls',
                'numerical_value': 90,
                'default_anonymization_level': 'full',
                'default_access_level': 'none',
                'sharing_policies': {
                    'allow_public_sharing': False,
                    'require_attribution': True,
                    'allow_modification': False
                }
            }
        ]
        
        created_count = 0
        for level_data in default_trust_levels:
            trust_level, created = TrustLevel.objects.get_or_create(
                name=level_data['name'],
                defaults=level_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created trust level: {trust_level.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Trust level already exists: {trust_level.name}')
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} trust levels')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All trust levels already exist')
            )