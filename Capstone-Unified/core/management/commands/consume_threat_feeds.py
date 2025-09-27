#!/usr/bin/env python
"""
Direct threat feed consumption without requiring Celery/Redis
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from core.models.models import ThreatFeed
from core.services.otx_taxii_service import OTXTaxiiService
from core.services.stix_taxii_service import StixTaxiiService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Consume threat feeds directly (without Celery) - useful when Redis/Celery is not available'

    def add_arguments(self, parser):
        parser.add_argument('--feed-id', type=int, help='Specific feed ID to consume')
        parser.add_argument('--feed-name', type=str, help='Feed name to consume (partial match)')
        parser.add_argument('--limit', type=int, default=10, help='Maximum number of content blocks to process')
        parser.add_argument('--all', action='store_true', help='Consume all active external feeds')
        parser.add_argument('--force-days', type=int, help='Force specific number of days to look back')
        parser.add_argument('--dry-run', action='store_true', help='Test connection without consuming data')

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity', 1)

        if options.get('feed_id'):
            self.consume_specific_feed(options['feed_id'], options)
        elif options.get('feed_name'):
            self.consume_feeds_by_name(options['feed_name'], options)
        elif options.get('all'):
            self.consume_all_feeds(options)
        else:
            self.stdout.write(self.style.ERROR("Please specify --feed-id, --feed-name, or --all"))
            self.print_available_feeds()

    def consume_specific_feed(self, feed_id, options):
        """Consume a specific feed by ID"""
        try:
            feed = ThreatFeed.objects.get(id=feed_id)
            self.stdout.write(f"Consuming feed: {feed.name} (ID: {feed_id})")
            return self.consume_feed(feed, options)
        except ThreatFeed.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Feed with ID {feed_id} does not exist"))
            return False

    def consume_feeds_by_name(self, feed_name, options):
        """Consume feeds matching name pattern"""
        feeds = ThreatFeed.objects.filter(
            name__icontains=feed_name,
            is_active=True,
            is_external=True
        )

        if not feeds.exists():
            self.stdout.write(self.style.WARNING(f"No active external feeds found matching '{feed_name}'"))
            return False

        self.stdout.write(f"Found {feeds.count()} feeds matching '{feed_name}':")
        success_count = 0

        for feed in feeds:
            self.stdout.write(f"\n--- Processing: {feed.name} ---")
            if self.consume_feed(feed, options):
                success_count += 1

        self.stdout.write(f"\nSummary: {success_count}/{feeds.count()} feeds consumed successfully")
        return success_count > 0

    def consume_all_feeds(self, options):
        """Consume all active external feeds"""
        feeds = ThreatFeed.objects.filter(
            is_active=True,
            is_external=True,
            taxii_server_url__isnull=False,
            taxii_collection_id__isnull=False
        )

        if not feeds.exists():
            self.stdout.write(self.style.WARNING("No active external feeds found with valid TAXII configuration"))
            return False

        self.stdout.write(f"Consuming {feeds.count()} active external feeds:")
        success_count = 0

        for feed in feeds:
            self.stdout.write(f"\n--- Processing: {feed.name} ---")
            if self.consume_feed(feed, options):
                success_count += 1

        self.stdout.write(f"\nSummary: {success_count}/{feeds.count()} feeds consumed successfully")
        return success_count > 0

    def consume_feed(self, feed, options):
        """Consume a single feed"""
        try:
            # Validate feed configuration
            if not self.validate_feed(feed):
                return False

            # Choose appropriate service
            if 'otx' in feed.name.lower() or 'alienvault' in feed.name.lower():
                service = OTXTaxiiService()
                service_type = "OTX"
            else:
                service = StixTaxiiService()
                service_type = "STIX"

            self.stdout.write(f"  Using {service_type} service")
            self.stdout.write(f"  Server: {feed.taxii_server_url}")
            self.stdout.write(f"  Collection: {feed.taxii_collection_id}")

            # Dry run - just test connection
            if options.get('dry_run'):
                self.stdout.write("  🔍 Testing connection (dry run)...")
                try:
                    if service_type == "OTX":
                        collections = service.get_collections()
                        self.stdout.write(f"  ✅ Connection successful, found {len(collections)} collections")
                    else:
                        collections = service.get_collections(feed.taxii_server_url, feed.taxii_api_root)
                        self.stdout.write(f"  ✅ Connection successful, found {len(collections)} collections")
                    return True
                except Exception as e:
                    self.stdout.write(f"  ❌ Connection failed: {e}")
                    return False

            # Actual consumption
            self.stdout.write(f"  🔄 Starting consumption (limit: {options.get('limit', 10)})...")

            # Set consumption status
            feed.consumption_status = 'processing'
            feed.save()

            try:
                stats = service.consume_feed(
                    feed,
                    limit=options.get('limit', 10),
                    force_days=options.get('force_days')
                )

                # Update feed status
                feed.consumption_status = 'idle'
                feed.last_sync = timezone.now()
                feed.sync_count = (feed.sync_count or 0) + 1
                feed.last_error = None
                feed.save()

                if isinstance(stats, tuple):
                    indicators_count, ttps_count = stats
                    self.stdout.write(f"  ✅ Success: {indicators_count} indicators, {ttps_count} TTPs")
                else:
                    self.stdout.write(f"  ✅ Success: {stats}")

                return True

            except Exception as e:
                # Update feed with error
                feed.consumption_status = 'idle'
                feed.last_error = str(e)[:500]  # Truncate long errors
                feed.save()

                self.stdout.write(f"  ❌ Consumption failed: {e}")
                return False

        except Exception as e:
            self.stdout.write(f"  ❌ Error processing feed: {e}")
            return False

    def validate_feed(self, feed):
        """Validate feed configuration"""
        errors = []

        if not feed.taxii_server_url:
            errors.append("Missing TAXII server URL")
        if not feed.taxii_collection_id:
            errors.append("Missing TAXII collection ID")
        if not feed.is_active:
            errors.append("Feed is not active")

        if errors:
            for error in errors:
                self.stdout.write(f"  ❌ {error}")
            return False

        return True

    def print_available_feeds(self):
        """Print list of available feeds"""
        self.stdout.write("\nAvailable feeds:")

        feeds = ThreatFeed.objects.filter(is_active=True, is_external=True)
        if not feeds.exists():
            self.stdout.write("  No active external feeds found")
            return

        for feed in feeds:
            status = "✅" if feed.taxii_server_url and feed.taxii_collection_id else "❌"
            last_sync = feed.last_sync.strftime('%Y-%m-%d %H:%M') if feed.last_sync else "Never"
            self.stdout.write(f"  {status} [{feed.id}] {feed.name} (Last sync: {last_sync})")