"""
Test OTX Connection Management Command
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from crisp_threat_intel.services.otx_service import OTXClient


class Command(BaseCommand):
    help = 'Test OTX API connection and retrieve basic information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='OTX API key (if not set in environment)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information',
        )

    def handle(self, *args, **options):
        # Get API key
        api_key = options.get('api_key') or settings.OTX_SETTINGS.get('API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('No OTX API key found. Set OTX_API_KEY in environment or use --api-key'))
            return

        try:
            client = OTXClient(api_key)
            
            self.stdout.write('Testing OTX API connection...')
            
            # Test basic connection
            if client.test_connection():
                self.stdout.write(self.style.SUCCESS('✓ OTX API connection successful'))
                
                # Get user information
                user_info = client.get_user_info()
                self.stdout.write(f'✓ Connected as: {user_info.get("username", "Unknown")}')
                
                if options['verbose']:
                    self.stdout.write('\nUser Details:')
                    for key, value in user_info.items():
                        if key not in ['avatar_url', 'pulse_count']:  # Skip some fields
                            self.stdout.write(f'  {key}: {value}')
                
                # Test getting recent pulses
                self.stdout.write('\nTesting pulse retrieval...')
                try:
                    pulses = client.get_pulses(limit=5)
                    self.stdout.write(self.style.SUCCESS(f'✓ Retrieved {len(pulses)} recent pulses'))
                    
                    if options['verbose'] and pulses:
                        self.stdout.write('\nRecent Pulses:')
                        for i, pulse in enumerate(pulses[:3], 1):
                            self.stdout.write(f'  {i}. {pulse.get("name", "Unknown")}')
                            self.stdout.write(f'     Created: {pulse.get("created", "Unknown")}')
                            self.stdout.write(f'     Indicators: {len(pulse.get("indicators", []))}')
                            
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠ Could not retrieve pulses: {e}'))
                
                # Show configuration
                self.stdout.write('\nOTX Configuration:')
                self.stdout.write(f'  Enabled: {settings.OTX_SETTINGS.get("ENABLED", False)}')
                self.stdout.write(f'  Fetch Interval: {settings.OTX_SETTINGS.get("FETCH_INTERVAL", 3600)} seconds')
                self.stdout.write(f'  Batch Size: {settings.OTX_SETTINGS.get("BATCH_SIZE", 50)}')
                self.stdout.write(f'  Max Age: {settings.OTX_SETTINGS.get("MAX_AGE_DAYS", 30)} days')
                
            else:
                self.stdout.write(self.style.ERROR('✗ OTX API connection failed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ OTX API error: {e}'))