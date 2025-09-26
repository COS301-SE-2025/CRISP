#!/usr/bin/env python
"""
Comprehensive Threat Intelligence Population Command
Populates the database with extensive threat intelligence from custom CRISP feeds.
This command creates realistic threat data that can be consumed exactly like external feeds.
"""

import os
import json
import time
import uuid
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.utils import IntegrityError

try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm for progress bars...")
    os.system("pip install tqdm")
    from tqdm import tqdm

from core.models.models import (
    Organization, ThreatFeed, Collection, Feed, Indicator, TTPData
)
from core.config.custom_threat_feeds import CUSTOM_FEEDS_CONFIG
from core.services.custom_feed_generator import CustomSTIXGenerator


class Command(BaseCommand):
    help = 'Populate database with comprehensive threat intelligence from custom CRISP feeds'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stix_generator = CustomSTIXGenerator()
        self.created_feeds = []
        self.created_indicators = 0
        self.created_ttps = 0

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing custom feed data before populating',
        )
        parser.add_argument(
            '--skip-feeds',
            action='store_true',
            help='Skip creating feeds, only populate indicators and TTPs',
        )
        parser.add_argument(
            '--feed-name',
            type=str,
            help='Populate only a specific feed by name',
        )

    def handle(self, *args, **options):
        start_time = time.time()

        self.stdout.write("="*80)
        self.stdout.write("CRISP COMPREHENSIVE THREAT INTELLIGENCE POPULATION")
        self.stdout.write("="*80)
        self.stdout.write("")

        # Clean if requested
        if options['clean']:
            self.clean_custom_feeds()

        # Create or update threat feeds
        if not options['skip_feeds']:
            self.create_custom_threat_feeds(options.get('feed_name'))

        # Populate comprehensive threat intelligence data
        self.populate_threat_intelligence(options.get('feed_name'))

        # Generate STIX bundles for external consumption
        self.generate_stix_bundles()

        # Print comprehensive summary
        self.print_final_summary()

        total_time = time.time() - start_time
        self.stdout.write(f"\nCompleted in {total_time:.1f} seconds")

    def clean_custom_feeds(self):
        """Clean existing custom feed data"""
        self.stdout.write("Cleaning existing custom feed data...")

        try:
            # Get custom feed names
            custom_feed_names = [feed['name'] for feed in CUSTOM_FEEDS_CONFIG]

            # Delete indicators and TTPs from custom feeds
            custom_feeds = ThreatFeed.objects.filter(name__in=custom_feed_names)

            for feed in custom_feeds:
                indicator_count = Indicator.objects.filter(threat_feed=feed).count()
                ttp_count = TTPData.objects.filter(threat_feed=feed).count()

                Indicator.objects.filter(threat_feed=feed).delete()
                TTPData.objects.filter(threat_feed=feed).delete()

                self.stdout.write(f"  Cleaned {feed.name}: {indicator_count} indicators, {ttp_count} TTPs")

            self.stdout.write("Custom feed data cleaned successfully")

        except Exception as e:
            self.stdout.write(f"Error cleaning custom feeds: {e}")

    def create_custom_threat_feeds(self, specific_feed=None):
        """Create custom threat feeds"""
        self.stdout.write("Creating/updating custom threat feeds...")

        # Get or create a default organization
        default_org, created = Organization.objects.get_or_create(
            name='CRISP Threat Intelligence',
            defaults={
                'description': 'CRISP Internal Threat Intelligence Organization',
                'organization_type': 'private',
                'domain': 'crisp-threat-intel.internal',
                'is_active': True,
                'is_verified': True
            }
        )

        feeds_to_process = CUSTOM_FEEDS_CONFIG
        if specific_feed:
            feeds_to_process = [feed for feed in CUSTOM_FEEDS_CONFIG if feed['name'] == specific_feed]

        for feed_config in feeds_to_process:
            try:
                with transaction.atomic():
                    threat_feed, created = ThreatFeed.objects.get_or_create(
                        name=feed_config['name'],
                        defaults={
                            'description': feed_config['description'],
                            'taxii_server_url': feed_config['taxii_server_url'],
                            'taxii_api_root': feed_config['taxii_api_root'],
                            'taxii_collection_id': feed_config['taxii_collection_id'],
                            'owner': default_org,
                            'is_external': feed_config['is_external'],
                            'is_public': feed_config['is_public'],
                            'sync_interval_hours': feed_config['sync_interval_hours'],
                            'is_active': True,
                            'last_sync': timezone.now() - timedelta(hours=1),
                            'sync_count': 0
                        }
                    )

                    if not created:
                        # Update existing feed
                        threat_feed.description = feed_config['description']
                        threat_feed.taxii_server_url = feed_config['taxii_server_url']
                        threat_feed.taxii_api_root = feed_config['taxii_api_root']
                        threat_feed.taxii_collection_id = feed_config['taxii_collection_id']
                        threat_feed.sync_interval_hours = feed_config['sync_interval_hours']
                        threat_feed.is_active = True
                        threat_feed.save()

                    self.created_feeds.append(threat_feed)
                    action = "Created" if created else "Updated"
                    self.stdout.write(f"  ✓ {action}: {feed_config['name']}")

            except Exception as e:
                self.stdout.write(f"  ✗ Error with feed {feed_config['name']}: {e}")
                continue

        self.stdout.write(f"Processed {len(self.created_feeds)} custom threat feeds")

    def populate_threat_intelligence(self, specific_feed=None):
        """Populate comprehensive threat intelligence data"""
        self.stdout.write("\nPopulating comprehensive threat intelligence data...")

        feeds_to_process = CUSTOM_FEEDS_CONFIG
        if specific_feed:
            feeds_to_process = [feed for feed in CUSTOM_FEEDS_CONFIG if feed['name'] == specific_feed]

        total_feeds = len(feeds_to_process)
        processed_feeds = 0

        for feed_config in feeds_to_process:
            try:
                threat_feed = ThreatFeed.objects.get(name=feed_config['name'])

                self.stdout.write(f"\nProcessing: {feed_config['name']}")
                self.stdout.write("-" * 60)

                # Populate indicators
                indicators_created = self.populate_indicators(threat_feed, feed_config)

                # Populate TTPs
                ttps_created = self.populate_ttps(threat_feed, feed_config)

                # Update feed sync information
                threat_feed.sync_count += 1
                threat_feed.last_sync = timezone.now()
                threat_feed.save()

                processed_feeds += 1
                self.stdout.write(f"✓ Completed {feed_config['name']}: {indicators_created} indicators, {ttps_created} TTPs")

            except ThreatFeed.DoesNotExist:
                self.stdout.write(f"✗ Feed not found: {feed_config['name']}")
                continue
            except Exception as e:
                self.stdout.write(f"✗ Error processing {feed_config['name']}: {e}")
                continue

        self.stdout.write(f"\nProcessed {processed_feeds}/{total_feeds} threat feeds")

    def populate_indicators(self, threat_feed, feed_config):
        """Populate indicators for a threat feed"""
        indicators = feed_config.get('indicators', [])
        created_count = 0
        skipped_count = 0

        self.stdout.write(f"  Creating {len(indicators)} indicators...")

        # Use progress bar for large indicator sets
        if len(indicators) > 50:
            progress_bar = tqdm(indicators, desc="  Indicators", leave=False)
        else:
            progress_bar = indicators

        for indicator_data in progress_bar:
            try:
                with transaction.atomic():
                    # Map indicator type
                    indicator_type_mapping = {
                        'domain-name': 'domain',
                        'ipv4-addr': 'ip',
                        'file': 'file_hash',
                        'email-addr': 'email',
                        'url': 'url'
                    }

                    mapped_type = indicator_type_mapping.get(
                        indicator_data['type'],
                        indicator_data['type']
                    )

                    # Get the indicator value
                    if indicator_data['type'] == 'file':
                        value = list(indicator_data['hashes'].values())[0]
                        hash_type = list(indicator_data['hashes'].keys())[0].lower().replace('-', '')
                    else:
                        value = indicator_data['value']
                        hash_type = None

                    # Check if indicator already exists
                    existing_indicator = Indicator.objects.filter(
                        value=value,
                        threat_feed=threat_feed
                    ).first()

                    if existing_indicator:
                        skipped_count += 1
                        continue

                    # Parse dates
                    first_seen = self.parse_date(indicator_data.get('first_seen'))
                    last_seen = self.parse_date(indicator_data.get('last_seen'))

                    # Create STIX ID
                    stix_id = f"indicator--{uuid.uuid4()}"

                    indicator = Indicator.objects.create(
                        value=value,
                        type=mapped_type,
                        hash_type=hash_type,
                        threat_feed=threat_feed,
                        confidence=indicator_data.get('confidence', 75),
                        first_seen=first_seen,
                        last_seen=last_seen,
                        stix_id=stix_id,
                        description=f"Custom CRISP indicator from {feed_config['name']}"
                    )
                    created_count += 1
                    self.created_indicators += 1

            except IntegrityError:
                skipped_count += 1
                continue
            except Exception as e:
                if hasattr(progress_bar, 'write'):
                    progress_bar.write(f"    Warning: Could not create indicator {indicator_data.get('value', 'unknown')}: {e}")
                skipped_count += 1
                continue

        if hasattr(progress_bar, 'close'):
            progress_bar.close()

        if skipped_count > 0:
            self.stdout.write(f"  Indicators: {created_count} created, {skipped_count} skipped (duplicates)")
        else:
            self.stdout.write(f"  Indicators: {created_count} created")

        return created_count

    def populate_ttps(self, threat_feed, feed_config):
        """Populate TTPs for a threat feed"""
        ttps = feed_config.get('ttps', [])
        created_count = 0
        skipped_count = 0

        self.stdout.write(f"  Creating {len(ttps)} TTPs...")

        for ttp_data in ttps:
            try:
                with transaction.atomic():
                    # Check if TTP already exists
                    existing_ttp = TTPData.objects.filter(
                        mitre_technique_id=ttp_data['mitre_technique_id'],
                        threat_feed=threat_feed
                    ).first()

                    if existing_ttp:
                        skipped_count += 1
                        continue

                    # Create STIX ID
                    ttp_stix_id = f"attack-pattern--{uuid.uuid4()}"

                    ttp = TTPData.objects.create(
                        name=ttp_data['name'],
                        description=ttp_data['description'],
                        mitre_technique_id=ttp_data['mitre_technique_id'],
                        mitre_tactic=ttp_data['tactic'],
                        threat_feed=threat_feed,
                        stix_id=ttp_stix_id
                    )
                    created_count += 1
                    self.created_ttps += 1

            except IntegrityError:
                skipped_count += 1
                continue
            except Exception as e:
                self.stdout.write(f"    Warning: Could not create TTP {ttp_data.get('name', 'unknown')}: {e}")
                skipped_count += 1
                continue

        if skipped_count > 0:
            self.stdout.write(f"  TTPs: {created_count} created, {skipped_count} skipped (duplicates)")
        else:
            self.stdout.write(f"  TTPs: {created_count} created")

        return created_count

    def generate_stix_bundles(self):
        """Generate STIX bundles for external consumption"""
        self.stdout.write("\nGenerating STIX bundles for external consumption...")

        try:
            stix_bundles = self.stix_generator.generate_all_custom_feeds_stix()

            # Create output directory
            output_dir = '/tmp/crisp_stix_bundles'
            os.makedirs(output_dir, exist_ok=True)

            for feed_name, bundle in stix_bundles.items():
                filename = f"{feed_name.lower().replace(' ', '_').replace('-', '_')}_bundle.json"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'w') as f:
                    json.dump(bundle, f, indent=2)

                self.stdout.write(f"  ✓ Generated STIX bundle: {filepath}")

            self.stdout.write(f"STIX bundles available in: {output_dir}")

        except Exception as e:
            self.stdout.write(f"Error generating STIX bundles: {e}")

    def parse_date(self, date_str):
        """Parse date string to datetime object"""
        if not date_str:
            return timezone.now() - timedelta(days=30)

        try:
            # Remove 'Z' suffix if present
            if date_str.endswith('Z'):
                date_str = date_str[:-1]

            return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        except ValueError:
            return timezone.now() - timedelta(days=30)

    def print_final_summary(self):
        """Print comprehensive summary"""
        self.stdout.write("\n" + "="*80)
        self.stdout.write("COMPREHENSIVE THREAT INTELLIGENCE POPULATION COMPLETE")
        self.stdout.write("="*80)

        self.stdout.write(f"\nSummary:")
        self.stdout.write(f"  Custom Threat Feeds: {len(self.created_feeds)}")
        self.stdout.write(f"  Total Indicators: {self.created_indicators}")
        self.stdout.write(f"  Total TTPs: {self.created_ttps}")

        self.stdout.write(f"\nCreated Feeds:")
        for feed in self.created_feeds:
            indicator_count = Indicator.objects.filter(threat_feed=feed).count()
            ttp_count = TTPData.objects.filter(threat_feed=feed).count()
            self.stdout.write(f"  • {feed.name}: {indicator_count} indicators, {ttp_count} TTPs")

        # Feed consumption statistics
        self.stdout.write(f"\nFeed Consumption Statistics:")
        total_feeds = ThreatFeed.objects.count()
        active_feeds = ThreatFeed.objects.filter(is_active=True).count()
        custom_feeds = len(self.created_feeds)
        external_feeds = active_feeds - custom_feeds

        self.stdout.write(f"  Total Feeds: {total_feeds}")
        self.stdout.write(f"  Active Feeds: {active_feeds}")
        self.stdout.write(f"  Custom CRISP Feeds: {custom_feeds}")
        self.stdout.write(f"  External Feeds: {external_feeds}")

        self.stdout.write(f"\nThreat Intelligence Breakdown by Feed Type:")
        feed_types = {}
        for feed_config in CUSTOM_FEEDS_CONFIG:
            feed_type = feed_config.get('feed_type', 'general')
            if feed_type not in feed_types:
                feed_types[feed_type] = {'indicators': 0, 'ttps': 0}

            feed_types[feed_type]['indicators'] += len(feed_config.get('indicators', []))
            feed_types[feed_type]['ttps'] += len(feed_config.get('ttps', []))

        for feed_type, counts in feed_types.items():
            self.stdout.write(f"  {feed_type.replace('_', ' ').title()}: {counts['indicators']} indicators, {counts['ttps']} TTPs")

        self.stdout.write(f"\nData is ready for consumption via TAXII and can be used exactly like AlienVault or VirusTotal feeds!")
        self.stdout.write("="*80)