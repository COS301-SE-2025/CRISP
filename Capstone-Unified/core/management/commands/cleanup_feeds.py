"""
Management command to remove mock and invalid threat feeds
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import ThreatFeed

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Remove mock and invalid threat feeds, keep only working ones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== THREAT FEED CLEANUP ==='))

        # Define mock patterns to identify invalid feeds
        mock_patterns = [
            'internal-collection',
            'mock',
            'demo',
            'test',
            'clone',
            'sample',
            'fake',
            'bishop',  # From the logs - "Bishop, Blake and Gamble"
            'blake',
            'gamble',
            'green group',
            'internal feed'
        ]

        # Valid collection IDs for real feeds
        valid_collections = [
            'user_AlienVault',
            'user_datadefenders',
            'virustotal-ttp-collection',
            None  # Allow None for MITRE ATT&CK
        ]

        # List all current feeds
        all_feeds = ThreatFeed.objects.all().order_by('name')
        self.stdout.write(f"Found {all_feeds.count()} total feeds")

        feeds_to_delete = []
        feeds_to_keep = []

        for feed in all_feeds:
            should_delete = False
            reason = ""

            # Check for mock patterns in name
            feed_name_lower = feed.name.lower()
            for pattern in mock_patterns:
                if pattern in feed_name_lower:
                    should_delete = True
                    reason = f"Contains mock pattern: '{pattern}'"
                    break

            # Check for invalid collection IDs
            if not should_delete and feed.taxii_collection_id not in valid_collections:
                # Special case: Keep MITRE ATT&CK and fix their collection IDs
                if 'mitre' in feed_name_lower and 'att' in feed_name_lower:
                    # Fix MITRE collection IDs to None (they don't use TAXII)
                    feed.taxii_collection_id = None
                    feed.save()
                    reason = "MITRE ATT&CK feed (fixed collection ID to None)"
                    feeds_to_keep.append((feed, reason))
                else:
                    should_delete = True
                    reason = f"Invalid collection ID: '{feed.taxii_collection_id}'"

            if should_delete:
                feeds_to_delete.append((feed, reason))
            elif not reason:  # Only add to keep list if not already added above
                reason = "Valid feed"
                feeds_to_keep.append((feed, reason))

        # Display what will be kept
        self.stdout.write(f"\n{self.style.SUCCESS('FEEDS TO KEEP')} ({len(feeds_to_keep)}):")
        for feed, reason in feeds_to_keep:
            status = "✓ ACTIVE" if feed.is_active else "✗ INACTIVE"
            self.stdout.write(f"  {status} {feed.name}")
            self.stdout.write(f"    Collection: {feed.taxii_collection_id or 'None'}")
            self.stdout.write(f"    Reason: {reason}")

        # Display what will be deleted
        self.stdout.write(f"\n{self.style.ERROR('FEEDS TO DELETE')} ({len(feeds_to_delete)}):")
        for feed, reason in feeds_to_delete:
            status = "✓ ACTIVE" if feed.is_active else "✗ INACTIVE"
            self.stdout.write(f"  {status} {feed.name}")
            self.stdout.write(f"    Collection: {feed.taxii_collection_id or 'None'}")
            self.stdout.write(f"    Reason: {reason}")

        if not feeds_to_delete:
            self.stdout.write(self.style.SUCCESS("\n✓ No feeds need to be deleted"))
            return

        if options['dry_run']:
            self.stdout.write(f"\n{self.style.WARNING('[DRY RUN]')} Would delete {len(feeds_to_delete)} feeds")
            return

        # Confirm deletion
        if not options['force']:
            confirm = input(f"\nDelete {len(feeds_to_delete)} feeds? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write("Cancelled")
                return

        # Delete the feeds
        deleted_count = 0
        with transaction.atomic():
            for feed, reason in feeds_to_delete:
                try:
                    feed_name = feed.name
                    feed.delete()
                    self.stdout.write(f"  ✓ Deleted: {feed_name}")
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(f"  ✗ Error deleting {feed.name}: {str(e)}")

        # Final summary
        remaining_count = ThreatFeed.objects.count()
        self.stdout.write(f"\n{self.style.SUCCESS('=== CLEANUP COMPLETE ===')}")
        self.stdout.write(f"Deleted: {deleted_count} feeds")
        self.stdout.write(f"Remaining: {remaining_count} feeds")

        # Show final feed list
        if remaining_count > 0:
            self.stdout.write(f"\n{self.style.SUCCESS('FINAL FEED LIST:')}")
            remaining_feeds = ThreatFeed.objects.all().order_by('name')
            for feed in remaining_feeds:
                status = "✓ ACTIVE" if feed.is_active else "✗ INACTIVE"
                self.stdout.write(f"  {feed.id}: {status} - {feed.name}")
                self.stdout.write(f"      Collection: {feed.taxii_collection_id or 'None'}")