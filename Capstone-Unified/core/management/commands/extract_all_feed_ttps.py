import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import ThreatFeed
from core.services.ttp_extraction_service import TTPExtractionService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Extract TTPs from all existing threat feeds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feed-id',
            type=int,
            help='Extract TTPs from a specific feed only'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-extraction of existing TTPs'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be extracted without actually extracting'
        )

    def handle(self, *args, **options):
        feed_id = options.get('feed_id')
        force = options.get('force', False)
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No TTPs will be actually extracted"))

        try:
            # Get feeds to process
            if feed_id:
                feeds = ThreatFeed.objects.filter(id=feed_id)
                if not feeds.exists():
                    self.stdout.write(
                        self.style.ERROR(f"Feed with ID {feed_id} not found")
                    )
                    return
            else:
                feeds = ThreatFeed.objects.all()

            if not feeds.exists():
                self.stdout.write(self.style.WARNING("No feeds found"))
                return

            self.stdout.write(f"Processing {feeds.count()} feeds...")

            ttp_extractor = TTPExtractionService()
            total_extracted = 0
            total_errors = 0

            for feed in feeds:
                # Check if feed has indicators
                indicator_count = feed.indicators.count()
                if indicator_count == 0:
                    self.stdout.write(f"  {feed.name}: No indicators, skipping")
                    continue

                self.stdout.write(f"  Processing {feed.name} ({indicator_count} indicators)...")

                if dry_run:
                    self.stdout.write(f"    Would extract TTPs from {indicator_count} indicators")
                    continue

                try:
                    with transaction.atomic():
                        result = ttp_extractor.extract_ttps_from_feed(feed, force_reextract=force)

                        if result.get('success', False):
                            extracted = len(result.get('ttps_extracted', []))
                            existing = len(result.get('ttps_existing', []))
                            total_extracted += extracted

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"    ✓ {feed.name}: {extracted} extracted, {existing} existing"
                                )
                            )
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            self.stdout.write(
                                self.style.ERROR(f"    ✗ {feed.name}: {error_msg}")
                            )
                            total_errors += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"    ✗ {feed.name}: {str(e)}")
                    )
                    total_errors += 1
                    logger.error(f"Error extracting TTPs from feed {feed.name}: {str(e)}")

            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nExtraction completed: {total_extracted} TTPs extracted, {total_errors} errors"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"\nDRY RUN completed - would have processed {feeds.count()} feeds")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Command failed: {str(e)}")
            )
            logger.error(f"Extract all feed TTPs command failed: {str(e)}")
            raise