from django.core.management.base import BaseCommand
from core.models.models import TrustLevel


class Command(BaseCommand):
    help = 'Initialize default trust levels if they don\'t exist'

    def handle(self, *args, **options):
        self.stdout.write('Initializing trust levels...')
        
        # Define standard trust levels
        trust_levels = [
            {'name': 'high', 'description': 'High trust level - Full access to sensitive data', 'numerical_value': 80},
            {'name': 'medium', 'description': 'Medium trust level - Limited access to sensitive data', 'numerical_value': 50},
            {'name': 'low', 'description': 'Low trust level - Public information only', 'numerical_value': 20}
        ]
        
        created_count = 0
        updated_count = 0
        
        for level_data in trust_levels:
            trust_level, created = TrustLevel.objects.get_or_create(
                name=level_data['name'],
                defaults={
                    'description': level_data['description'],
                    'numerical_value': level_data['numerical_value']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created trust level: {trust_level.name}')
                )
            else:
                # Update existing trust level if needed
                if trust_level.numerical_value != level_data['numerical_value']:
                    trust_level.numerical_value = level_data['numerical_value'] 
                    trust_level.description = level_data['description']
                    trust_level.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated trust level: {trust_level.name}')
                    )
        
        if created_count == 0 and updated_count == 0:
            self.stdout.write(
                self.style.SUCCESS('All trust levels already exist and are up to date.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Trust levels initialized: {created_count} created, {updated_count} updated.'
                )
            )