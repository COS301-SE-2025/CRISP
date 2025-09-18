"""
Management command to ensure VirusTotal feed exists and is properly configured
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from core.models.models import ThreatFeed, Indicator
from core.user_management.models import CustomUser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ensure VirusTotal threat feed exists and is properly configured'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-samples',
            action='store_true',
            help='Add sample indicators for testing',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== VIRUSTOTAL FEED SETUP ==='))

        try:
            # Get or create system organization for feed ownership
            from core.models.models import Organization

            system_org, created = Organization.objects.get_or_create(
                name='System',
                defaults={
                    'domain': 'crisp-system.org',
                    'organization_type': 'government',
                    'description': 'System organization for internal feeds',
                    'is_active': True,
                    'created_at': timezone.now(),
                    'updated_at': timezone.now()
                }
            )

            if created:
                self.stdout.write(f"  ✓ Created system organization")

            # Check if VirusTotal feed exists
            vt_feed, created = ThreatFeed.objects.get_or_create(
                name='VirusTotal Threat Intelligence',
                defaults={
                    'description': 'VirusTotal API integration for malware analysis and TTP extraction',
                    'taxii_server_url': 'https://virustotal-api-service',
                    'taxii_api_root': '/api/v3',
                    'taxii_collection_id': 'virustotal-ttp-collection',
                    'taxii_username': '',  # API key will be used via settings
                    'taxii_password': '',
                    'owner': system_org,
                    'is_external': True,
                    'is_public': True,
                    'is_active': True,
                    'sync_interval_hours': 24,
                    'sync_count': 0,
                    'created_at': timezone.now(),
                    'updated_at': timezone.now()
                }
            )

            if created:
                self.stdout.write(f"  ✓ Created VirusTotal feed (ID: {vt_feed.id})")
            else:
                self.stdout.write(f"  ✓ VirusTotal feed already exists (ID: {vt_feed.id})")
                # Update configuration if needed
                vt_feed.is_active = True
                vt_feed.taxii_collection_id = 'virustotal-ttp-collection'
                vt_feed.description = 'VirusTotal API integration for malware analysis and TTP extraction'
                vt_feed.save()
                self.stdout.write("  ✓ Updated VirusTotal feed configuration")

            # Add sample indicators if requested
            if options['with_samples']:
                self.stdout.write("\nAdding sample indicators...")

                sample_indicators = [
                    ('275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'sha256', 'Known malware sample'),
                    ('44d88612fea8a8f36de82e1278abb02f', 'md5', 'Common test hash'),
                    ('da39a3ee5e6b4b0d3255bfef95601890afd80709', 'sha1', 'Empty file hash'),
                    ('http://malicious-example.com/malware.exe', 'url', 'Sample malicious URL'),
                    ('https://suspicious-site.net/payload.php', 'url', 'Sample suspicious URL'),
                ]

                created_indicators = 0
                for value, itype, description in sample_indicators:
                    indicator, created = Indicator.objects.get_or_create(
                        value=value,
                        type=itype,
                        threat_feed=vt_feed,
                        defaults={
                            'name': f'Sample {itype.upper()} for VirusTotal analysis',
                            'description': description,
                            'confidence': 70,
                            'hash_type': itype if itype in ['md5', 'sha1', 'sha256'] else '',
                            'stix_id': f'indicator--vt-{itype}-{abs(hash(value))}',
                            'first_seen': timezone.now(),
                            'last_seen': timezone.now(),
                            'is_anonymized': False,
                            'created_at': timezone.now(),
                            'updated_at': timezone.now()
                        }
                    )
                    if created:
                        created_indicators += 1

                self.stdout.write(f"  ✓ Added {created_indicators} sample indicators")

            # Display final status
            vt_indicators_count = Indicator.objects.filter(threat_feed=vt_feed).count()

            self.stdout.write(f"\n{self.style.SUCCESS('=== VIRUSTOTAL SETUP COMPLETE ===')}")
            self.stdout.write(f"Feed ID: {vt_feed.id}")
            self.stdout.write(f"Feed Name: {vt_feed.name}")
            self.stdout.write(f"Collection ID: {vt_feed.taxii_collection_id}")
            self.stdout.write(f"Active: {vt_feed.is_active}")
            self.stdout.write(f"Indicators: {vt_indicators_count}")
            self.stdout.write(f"Last Sync: {vt_feed.last_sync or 'Never'}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up VirusTotal feed: {str(e)}"))
            raise