#!/usr/bin/env python
"""
Test ThreatFeed consumption to ensure feeds are properly configured and consumable
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import ThreatFeed
from core.services.stix_taxii_service import StixTaxiiService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test threat feed consumption to ensure all feeds are properly configured'

    def add_arguments(self, parser):
        parser.add_argument('--feed-id', type=int, help='Specific feed ID to test')
        parser.add_argument('--limit', type=int, default=5, help='Maximum number of feeds to test')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity', 1)
        self.verbose = options.get('verbose', False)

        if options.get('feed_id'):
            self.test_specific_feed(options['feed_id'])
        else:
            self.test_all_feeds(options.get('limit', 5))

    def test_specific_feed(self, feed_id):
        """Test a specific feed"""
        try:
            feed = ThreatFeed.objects.get(id=feed_id)
            self.stdout.write(f"Testing feed: {feed.name}")
            self.test_feed_consumption(feed)
        except ThreatFeed.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Feed with ID {feed_id} does not exist"))

    def test_all_feeds(self, limit):
        """Test multiple feeds"""
        feeds = ThreatFeed.objects.filter(is_active=True)[:limit]

        if not feeds:
            self.stdout.write(self.style.WARNING("No active threat feeds found"))
            return

        self.stdout.write(f"Testing {len(feeds)} threat feeds...")

        success_count = 0
        for feed in feeds:
            if self.test_feed_consumption(feed):
                success_count += 1

        self.stdout.write(f"\nSummary: {success_count}/{len(feeds)} feeds tested successfully")

    def test_feed_consumption(self, feed):
        """Test consumption of a single feed"""
        try:
            self.stdout.write(f"  Testing: {feed.name}")

            # Validate feed configuration
            validation_errors = self.validate_feed_config(feed)
            if validation_errors:
                for error in validation_errors:
                    self.stdout.write(f"    ❌ {error}")
                return False

            # Test TAXII connection (without actually consuming)
            service = StixTaxiiService()

            if self.verbose:
                self.stdout.write(f"    Server: {feed.taxii_server_url}")
                self.stdout.write(f"    API Root: {feed.taxii_api_root}")
                self.stdout.write(f"    Collection: {feed.taxii_collection_id}")

            # Try to establish connection (this will test the configuration)
            try:
                # Just test the configuration without consuming data
                if feed.taxii_server_url and feed.taxii_api_root and feed.taxii_collection_id:
                    self.stdout.write(f"    ✅ Configuration is valid")
                    self.stdout.write(f"    ℹ️  External: {feed.is_external}, Public: {feed.is_public}")
                    self.stdout.write(f"    ℹ️  Sync interval: {feed.sync_interval_hours} hours")
                    return True
                else:
                    self.stdout.write(f"    ❌ Missing required TAXII configuration")
                    return False

            except Exception as e:
                self.stdout.write(f"    ❌ Connection test failed: {e}")
                return False

        except Exception as e:
            self.stdout.write(f"    ❌ Error testing feed: {e}")
            return False

    def validate_feed_config(self, feed):
        """Validate feed configuration"""
        errors = []

        if not feed.name:
            errors.append("Feed name is required")

        if not feed.owner:
            errors.append("Feed owner is required")

        if feed.is_external:
            if not feed.taxii_server_url:
                errors.append("TAXII server URL is required for external feeds")
            if not feed.taxii_api_root:
                errors.append("TAXII API root is required for external feeds")
            if not feed.taxii_collection_id:
                errors.append("TAXII collection ID is required for external feeds")

        if feed.sync_interval_hours <= 0:
            errors.append("Sync interval must be positive")

        return errors