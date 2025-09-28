"""
Management command to sync TTP data from VirusTotal feeds
"""
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models.models import ThreatFeed
from core.services.virustotal_service import VirusTotalService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync TTP data from VirusTotal threat feeds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feed-id',
            type=int,
            help='Specific VirusTotal feed ID to sync (optional)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Number of indicators to process per feed (default: 50)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting VirusTotal TTP sync...'))

        # Initialize VirusTotal service
        vt_service = VirusTotalService()

        # Test API connection first
        connection_test = vt_service.test_api_connection()
        if not connection_test['success']:
            raise CommandError(f"VirusTotal API connection failed: {connection_test['error']}")

        self.stdout.write(f"✓ VirusTotal API connection successful")
        if connection_test.get('quota'):
            self.stdout.write(f"  API Quota: {connection_test['quota']}")

        # Get VirusTotal feeds
        if options['feed_id']:
            try:
                feeds = [ThreatFeed.objects.get(id=options['feed_id'])]
                if 'virustotal' not in feeds[0].name.lower():
                    self.stdout.write(
                        self.style.WARNING(f"Warning: Feed '{feeds[0].name}' doesn't appear to be a VirusTotal feed")
                    )
            except ThreatFeed.DoesNotExist:
                raise CommandError(f"Feed with ID {options['feed_id']} not found")
        else:
            # Get all VirusTotal-related feeds
            feeds = ThreatFeed.objects.filter(
                name__icontains='virustotal',
                is_active=True
            )

        if not feeds:
            raise CommandError("No active VirusTotal feeds found")

        self.stdout.write(f"Found {len(feeds)} VirusTotal feed(s) to process")

        total_ttps_created = 0
        total_indicators_processed = 0

        for feed in feeds:
            self.stdout.write(f"\nProcessing feed: {feed.name}")
            self.stdout.write(f"  TAXII Server: {feed.taxii_server_url}")
            self.stdout.write(f"  Collection ID: {feed.taxii_collection_id}")
            self.stdout.write(f"  Last sync: {feed.last_sync or 'Never'}")

            if options['dry_run']:
                self.stdout.write("  [DRY RUN] Would process indicators for TTP extraction")
                continue

            try:
                with transaction.atomic():
                    # Sync TTP data from VirusTotal
                    result = vt_service.sync_virustotal_feed(feed, limit=options['limit'])

                    if result['success']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ Processed {result['indicators_processed']} indicators, "
                                f"created {result['ttps_created']} TTPs"
                            )
                        )
                        total_ttps_created += result['ttps_created']
                        total_indicators_processed += result['indicators_processed']
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ Sync failed for {feed.name}")
                        )

                    # Display any errors
                    if result.get('errors'):
                        for error in result['errors']:
                            self.stdout.write(f"    Error: {error}")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Unexpected error processing {feed.name}: {str(e)}")
                )
                logger.error(f"VirusTotal sync error for {feed.name}: {str(e)}")

        # Summary
        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n=== VirusTotal Sync Complete ===\n"
                    f"Total indicators processed: {total_indicators_processed}\n"
                    f"Total TTPs created: {total_ttps_created}\n"
                    f"Feeds processed: {len(feeds)}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n=== Dry Run Complete ===\nNo changes made.")
            )