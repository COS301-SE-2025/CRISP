#!/usr/bin/env python
"""
Fix existing threat feeds with invalid collection IDs
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import ThreatFeed

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix threat feeds with invalid collection IDs by updating them with real ones'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without actually changing it')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write("DRY RUN - No changes will be made")

        # Real, working TAXII server configurations
        real_feeds = [
            {
                'server_url': 'https://cti-taxii.mitre.org',
                'api_root': 'stix',
                'collection_id': '95ecc380-afe9-11e4-9b6c-751b66dd541e',
                'name_pattern': 'MITRE ATT&CK Enterprise'
            },
            {
                'server_url': 'https://otx.alienvault.com',
                'api_root': 'taxii',
                'collection_id': 'user_AlienVault',
                'name_pattern': 'AlienVault OTX'
            },
            {
                'server_url': 'https://otx.alienvault.com',
                'api_root': 'taxii',
                'collection_id': 'user_datadefenders',
                'name_pattern': 'DataDefenders'
            },
            {
                'server_url': 'https://cti-taxii.mitre.org',
                'api_root': 'stix',
                'collection_id': '2f669986-b40b-4423-b720-4396ca6a462b',
                'name_pattern': 'MITRE Mobile'
            },
            {
                'server_url': 'https://cti-taxii.mitre.org',
                'api_root': 'stix',
                'collection_id': '02c3ef24-9cd4-48f3-a99f-b74ce24f1d34',
                'name_pattern': 'MITRE ICS'
            }
        ]

        # Get all threat feeds with potentially invalid collection IDs
        feeds = ThreatFeed.objects.filter(is_external=True)

        self.stdout.write(f"Found {feeds.count()} external threat feeds to check")

        fixed_count = 0

        for i, feed in enumerate(feeds):
            # Check if collection ID looks like a UUID (probably invalid)
            if self.looks_like_uuid(feed.taxii_collection_id):
                # Use a real configuration
                real_config = real_feeds[i % len(real_feeds)]

                old_config = {
                    'server': feed.taxii_server_url,
                    'api_root': feed.taxii_api_root,
                    'collection': feed.taxii_collection_id
                }

                new_config = {
                    'server': real_config['server_url'],
                    'api_root': real_config['api_root'],
                    'collection': real_config['collection_id']
                }

                self.stdout.write(f"\nFeed: {feed.name}")
                self.stdout.write(f"  OLD: {old_config}")
                self.stdout.write(f"  NEW: {new_config}")

                if not dry_run:
                    with transaction.atomic():
                        feed.taxii_server_url = new_config['server']
                        feed.taxii_api_root = new_config['api_root']
                        feed.taxii_collection_id = new_config['collection']
                        feed.name = f"{real_config['name_pattern']} - {feed.owner.name}"
                        feed.description = f"Real {real_config['name_pattern']} threat intelligence feed"
                        feed.save()

                    self.stdout.write(f"  ✅ FIXED")
                else:
                    self.stdout.write(f"  🔍 WOULD FIX")

                fixed_count += 1
            else:
                self.stdout.write(f"Feed {feed.name}: Collection ID looks valid, skipping")

        if dry_run:
            self.stdout.write(f"\nDRY RUN: Would fix {fixed_count} feeds")
        else:
            self.stdout.write(f"\n✅ Fixed {fixed_count} threat feeds with real TAXII configurations")

    def looks_like_uuid(self, text):
        """Check if text looks like a UUID"""
        if not text:
            return False

        # UUIDs have specific patterns
        import re
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        return bool(re.match(uuid_pattern, text.lower()))