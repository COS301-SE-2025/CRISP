import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import Indicator, ThreatFeed
from collections import defaultdict

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check for and optionally clean up duplicate indicators across feeds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show duplicates but do not delete them'
        )
        parser.add_argument(
            '--delete-duplicates',
            action='store_true',
            help='Actually delete duplicate indicators (keeps the most recent)'
        )
        parser.add_argument(
            '--merge-feeds',
            action='store_true',
            help='Merge indicators from duplicate feeds into the oldest feed'
        )

    def handle(self, *args, **options):
        self.stdout.write("Checking for duplicate indicators...")

        # Check for exact duplicates (same value, type, different feeds)
        duplicates = self._find_duplicates()

        if not duplicates:
            self.stdout.write(self.style.SUCCESS("No duplicate indicators found!"))
            return

        self.stdout.write(f"Found {len(duplicates)} groups of duplicate indicators:")

        total_duplicates = 0
        for key, indicators in duplicates.items():
            total_duplicates += len(indicators) - 1  # -1 because we keep one
            self.stdout.write(f"  {key[0]} '{key[1][:50]}...': {len(indicators)} copies across feeds:")
            for ind in indicators:
                self.stdout.write(f"    - Feed: {ind.threat_feed.name} (ID: {ind.id}, Created: {ind.created_at})")

        self.stdout.write(f"Total duplicate indicators to clean: {total_duplicates}")

        if options['dry_run']:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes made"))
            return

        if options['delete_duplicates']:
            self._delete_duplicates(duplicates)
        elif options['merge_feeds']:
            self._merge_duplicate_feeds(duplicates)
        else:
            self.stdout.write(self.style.WARNING("Use --delete-duplicates or --merge-feeds to actually clean up"))

    def _find_duplicates(self):
        """Find indicators with same value and type but different feeds"""
        # Group indicators by value and type
        indicator_groups = defaultdict(list)

        for indicator in Indicator.objects.select_related('threat_feed').all():
            key = (indicator.type, indicator.value)
            indicator_groups[key].append(indicator)

        # Filter to only groups with duplicates
        duplicates = {k: v for k, v in indicator_groups.items() if len(v) > 1}
        return duplicates

    def _delete_duplicates(self, duplicates):
        """Delete duplicate indicators, keeping the most recent one"""
        deleted_count = 0

        with transaction.atomic():
            for key, indicators in duplicates.items():
                # Sort by creation date, keep the most recent
                indicators_sorted = sorted(indicators, key=lambda x: x.created_at, reverse=True)
                to_keep = indicators_sorted[0]
                to_delete = indicators_sorted[1:]

                self.stdout.write(f"Keeping indicator {to_keep.id} from feed '{to_keep.threat_feed.name}'")

                for ind in to_delete:
                    self.stdout.write(f"  Deleting duplicate {ind.id} from feed '{ind.threat_feed.name}'")
                    ind.delete()
                    deleted_count += 1

        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} duplicate indicators"))

    def _merge_duplicate_feeds(self, duplicates):
        """Merge indicators from duplicate feeds into oldest feed"""
        # First, identify feeds that might be duplicates
        feed_groups = defaultdict(list)

        for key, indicators in duplicates.items():
            feeds = list(set(ind.threat_feed for ind in indicators))
            if len(feeds) > 1:
                # Check if feeds have similar names (potential duplicates)
                alienvault_feeds = [f for f in feeds if 'alien' in f.name.lower()]
                if len(alienvault_feeds) > 1:
                    feed_key = 'alienvault'
                    feed_groups[feed_key].extend(alienvault_feeds)

        if not feed_groups:
            self.stdout.write(self.style.WARNING("No duplicate feeds detected for merging"))
            return

        # Process each group of duplicate feeds
        for feed_type, feeds in feed_groups.items():
            # Remove duplicates and sort by creation date
            unique_feeds = list(set(feeds))
            if len(unique_feeds) <= 1:
                continue

            unique_feeds.sort(key=lambda x: x.created_at)
            primary_feed = unique_feeds[0]  # Oldest feed
            duplicate_feeds = unique_feeds[1:]

            self.stdout.write(f"Merging {feed_type} feeds into '{primary_feed.name}':")

            with transaction.atomic():
                for dup_feed in duplicate_feeds:
                    indicators_to_move = Indicator.objects.filter(threat_feed=dup_feed)
                    moved_count = 0

                    for indicator in indicators_to_move:
                        # Check if indicator already exists in primary feed
                        existing = Indicator.objects.filter(
                            value=indicator.value,
                            type=indicator.type,
                            threat_feed=primary_feed
                        ).first()

                        if existing:
                            # Update existing indicator with newer info if needed
                            if indicator.last_seen > existing.last_seen:
                                existing.last_seen = indicator.last_seen
                                existing.save()
                            indicator.delete()
                        else:
                            # Move indicator to primary feed
                            indicator.threat_feed = primary_feed
                            indicator.save()
                            moved_count += 1

                    self.stdout.write(f"  Moved {moved_count} indicators from '{dup_feed.name}'")

                    # Optionally delete the empty duplicate feed
                    remaining_indicators = Indicator.objects.filter(threat_feed=dup_feed).count()
                    if remaining_indicators == 0:
                        self.stdout.write(f"  Deleted empty feed '{dup_feed.name}'")
                        dup_feed.delete()

        self.stdout.write(self.style.SUCCESS("Feed merging completed"))

    def _check_feed_similarity(self, feed1, feed2):
        """Check if two feeds are likely duplicates based on name/config"""
        name1, name2 = feed1.name.lower(), feed2.name.lower()

        # Check for common duplicate patterns
        if 'alien' in name1 and 'alien' in name2:
            return True
        if 'otx' in name1 and 'otx' in name2:
            return True
        if feed1.taxii_server_url and feed2.taxii_server_url:
            return feed1.taxii_server_url == feed2.taxii_server_url

        return False