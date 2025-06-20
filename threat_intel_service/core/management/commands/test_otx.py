from django.core.management.base import BaseCommand
from django.conf import settings
import logging

from core.otx_client import OTXClient, OTXAPIError
from core.tasks import test_otx_connection, fetch_otx_threat_feeds

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test OTX integration and fetch sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fetch-feeds',
            action='store_true',
            help='Fetch threat feeds from OTX after testing connection',
        )
        parser.add_argument(
            '--api-key',
            type=str,
            help='OTX API key to use for testing (overrides settings)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing OTX Integration'))
        
        # Check if API key is configured
        api_key = options.get('api_key') or settings.OTX_API_KEY
        if not api_key:
            self.stdout.write(
                self.style.ERROR(
                    'OTX API key not configured. Set OTX_API_KEY environment variable or use --api-key option.'
                )
            )
            return
        
        try:
            # Initialize client
            client = OTXClient(api_key=api_key)
            
            # Test connection
            self.stdout.write('Testing OTX API connection...')
            if client.test_connection():
                self.stdout.write(self.style.SUCCESS('✓ OTX API connection successful'))
                
                # Get user info
                try:
                    user_info = client.get_user_info()
                    self.stdout.write(f"Connected as: {user_info.get('username', 'Unknown')}")
                    self.stdout.write(f"Follower count: {user_info.get('follower_count', 0)}")
                    self.stdout.write(f"Following count: {user_info.get('following_count', 0)}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not retrieve user info: {e}'))
                
            else:
                self.stdout.write(self.style.ERROR('✗ OTX API connection failed'))
                return
            
            # Test getting recent pulses
            self.stdout.write('\nTesting pulse retrieval...')
            try:
                pulses = client.get_pulses(limit=5)
                self.stdout.write(self.style.SUCCESS(f'✓ Retrieved {len(pulses)} recent pulses'))
                
                for i, pulse in enumerate(pulses[:3], 1):
                    self.stdout.write(f"  {i}. {pulse.get('name', 'Unnamed pulse')}")
                    self.stdout.write(f"     Created: {pulse.get('created', 'Unknown')}")
                    self.stdout.write(f"     Indicators: {len(pulse.get('indicators', []))}")
                    self.stdout.write(f"     Tags: {', '.join(pulse.get('tags', []))}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to retrieve pulses: {e}'))
            
            # Test getting recent indicators
            self.stdout.write('\nTesting indicator retrieval...')
            try:
                indicators = client.get_recent_indicators(
                    types=['IPv4', 'domain'], 
                    limit=10
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Retrieved {len(indicators)} recent indicators'))
                
                for i, indicator in enumerate(indicators[:5], 1):
                    self.stdout.write(f"  {i}. {indicator.get('type', 'Unknown')}: {indicator.get('indicator', 'N/A')}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to retrieve indicators: {e}'))
            
            # Fetch feeds if requested
            if options['fetch_feeds']:
                self.stdout.write('\nFetching and processing OTX threat feeds...')
                try:
                    result = fetch_otx_threat_feeds.delay()
                    task_result = result.get(timeout=300)  # 5 minute timeout
                    
                    if task_result.get('status') == 'success':
                        self.stdout.write(self.style.SUCCESS('✓ Successfully fetched and processed OTX feeds'))
                        results = task_result.get('results', {})
                        self.stdout.write(f"  Processed pulses: {results.get('processed_pulses', 0)}")
                        self.stdout.write(f"  Created objects: {results.get('created_objects', 0)}")
                        if results.get('errors'):
                            self.stdout.write(f"  Errors: {len(results['errors'])}")
                    else:
                        self.stdout.write(self.style.ERROR(f"✗ Feed fetch failed: {task_result.get('message')}"))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'✗ Feed fetch task failed: {e}'))
            
            self.stdout.write(self.style.SUCCESS('\nOTX integration test completed'))
            
        except OTXAPIError as e:
            self.stdout.write(self.style.ERROR(f'OTX API Error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {e}'))
            
        # Print configuration summary
        self.stdout.write('\n--- OTX Configuration ---')
        self.stdout.write(f"Enabled: {settings.OTX_SETTINGS.get('ENABLED', False)}")
        self.stdout.write(f"Fetch interval: {settings.OTX_SETTINGS.get('FETCH_INTERVAL', 3600)} seconds")
        self.stdout.write(f"Batch size: {settings.OTX_SETTINGS.get('BATCH_SIZE', 50)}")
        self.stdout.write(f"Max age: {settings.OTX_SETTINGS.get('MAX_AGE_DAYS', 30)} days")
        self.stdout.write(f"Indicator types: {', '.join(settings.OTX_SETTINGS.get('INDICATOR_TYPES', []))}")