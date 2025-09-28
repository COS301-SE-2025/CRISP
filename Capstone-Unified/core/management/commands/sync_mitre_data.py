"""
Management command to sync MITRE ATT&CK data from official sources
"""
from django.core.management.base import BaseCommand, CommandError
from core.services.mitre_integration_service import MITREIntegrationService
from core.models.models import ThreatFeed


class Command(BaseCommand):
    help = 'Sync MITRE ATT&CK data from official sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feed-id',
            type=int,
            help='Sync specific MITRE feed by ID'
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all MITRE feeds'
        )

        parser.add_argument(
            '--check-freshness',
            action='store_true',
            help='Check data freshness without syncing'
        )

        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if data is fresh'
        )

    def handle(self, *args, **options):
        mitre_service = MITREIntegrationService()

        # Check freshness only
        if options['check_freshness']:
            self.check_data_freshness(mitre_service)
            return

        # Sync all MITRE feeds
        if options['all']:
            self.sync_all_feeds(mitre_service, options['force'])
            return

        # Sync specific feed
        if options['feed_id']:
            self.sync_specific_feed(mitre_service, options['feed_id'], options['force'])
            return

        # Default: check what needs syncing and provide recommendations
        self.show_sync_recommendations(mitre_service)

    def check_data_freshness(self, mitre_service):
        """Check and display data freshness information"""
        self.stdout.write("Checking MITRE data freshness...")

        validation = mitre_service.validate_mitre_data_freshness()

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write("MITRE DATA FRESHNESS REPORT")
        self.stdout.write(f"{'='*50}")

        # Never synced
        if validation['never_synced']:
            self.stdout.write(f"\n📋 NEVER SYNCED ({len(validation['never_synced'])})")
            self.stdout.write("-" * 30)
            for feed in validation['never_synced']:
                self.stdout.write(f"• {feed['feed_name']}")
                self.stdout.write(f"  {feed['recommendation']}")

        # Needs update
        if validation['needs_update']:
            self.stdout.write(f"\n⚠️  NEEDS UPDATE ({len(validation['needs_update'])})")
            self.stdout.write("-" * 30)
            for feed in validation['needs_update']:
                self.stdout.write(f"• {feed['feed_name']}")
                self.stdout.write(f"  Last sync: {feed['hours_since_sync']} hours ago")
                self.stdout.write(f"  {feed['recommendation']}")

        # Up to date
        if validation['up_to_date']:
            self.stdout.write(f"\n✅ UP TO DATE ({len(validation['up_to_date'])})")
            self.stdout.write("-" * 30)
            for feed in validation['up_to_date']:
                self.stdout.write(f"• {feed['feed_name']}")
                self.stdout.write(f"  Last sync: {feed['hours_since_sync']} hours ago")
                self.stdout.write(f"  Next sync in: {feed['next_sync_in']} hours")

        # Recommendations
        if validation['recommendations']:
            self.stdout.write(f"\n💡 RECOMMENDATIONS")
            self.stdout.write("-" * 30)
            for rec in validation['recommendations']:
                self.stdout.write(f"• {rec}")

    def sync_all_feeds(self, mitre_service, force_sync=False):
        """Sync all MITRE feeds"""
        if not force_sync:
            # Check if sync is needed
            validation = mitre_service.validate_mitre_data_freshness()
            needs_sync = validation['never_synced'] + validation['needs_update']

            if not needs_sync:
                self.stdout.write(
                    self.style.SUCCESS("All MITRE feeds are up to date. Use --force to sync anyway.")
                )
                return

        self.stdout.write("Syncing all MITRE feeds...")

        result = mitre_service.sync_all_mitre_feeds()

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write("MITRE SYNC SUMMARY")
        self.stdout.write(f"{'='*50}")
        self.stdout.write(f"Feeds synced: {result['total_feeds_synced']}")
        self.stdout.write(f"Successful: {result['successful_syncs']}")
        self.stdout.write(f"Failed: {result['failed_syncs']}")
        self.stdout.write(f"Total techniques: {result['total_techniques']}")

        # Show individual feed results
        for feed_result in result['feed_results']:
            if feed_result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ {feed_result['feed_name']}: "
                        f"{feed_result['techniques_synced']} techniques "
                        f"({feed_result['new_created']} new, {feed_result['existing_updated']} updated)"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ {feed_result['feed_name']}: Failed")
                )
                if 'errors' in feed_result:
                    for error in feed_result['errors']:
                        self.stdout.write(f"    Error: {error}")

    def sync_specific_feed(self, mitre_service, feed_id, force_sync=False):
        """Sync a specific MITRE feed"""
        try:
            feed = ThreatFeed.objects.get(id=feed_id)
        except ThreatFeed.DoesNotExist:
            raise CommandError(f'Feed with ID {feed_id} does not exist')

        if 'mitre' not in feed.name.lower():
            self.stdout.write(
                self.style.WARNING(f"Warning: {feed.name} doesn't appear to be a MITRE feed")
            )

        self.stdout.write(f"Syncing MITRE feed: {feed.name}")

        result = mitre_service.sync_mitre_enterprise_data(feed)

        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Sync completed: {result['techniques_synced']} techniques synced "
                    f"({result['new_created']} new, {result['existing_updated']} updated)"
                )
            )
        else:
            self.stdout.write(self.style.ERROR(f"✗ Sync failed"))
            for error in result['errors']:
                self.stdout.write(f"Error: {error}")

    def show_sync_recommendations(self, mitre_service):
        """Show sync recommendations and usage information"""
        self.stdout.write("MITRE ATT&CK Data Sync Tool")
        self.stdout.write("=" * 30)

        # Check current status
        validation = mitre_service.validate_mitre_data_freshness()

        total_feeds = (len(validation['never_synced']) +
                      len(validation['needs_update']) +
                      len(validation['up_to_date']))

        self.stdout.write(f"Found {total_feeds} MITRE feeds")

        if validation['never_synced'] or validation['needs_update']:
            needs_sync_count = len(validation['never_synced']) + len(validation['needs_update'])
            self.stdout.write(f"⚠️  {needs_sync_count} feeds need syncing")

            self.stdout.write("\nRecommended commands:")
            self.stdout.write("  python manage.py sync_mitre_data --all")
            self.stdout.write("  python manage.py sync_mitre_data --check-freshness")
        else:
            self.stdout.write("✅ All MITRE feeds are up to date")

        self.stdout.write("\nAvailable options:")
        self.stdout.write("  --all                 Sync all MITRE feeds")
        self.stdout.write("  --feed-id <ID>        Sync specific feed")
        self.stdout.write("  --check-freshness     Check data freshness")
        self.stdout.write("  --force               Force sync regardless of freshness")

        self.stdout.write("\nExamples:")
        self.stdout.write("  python manage.py sync_mitre_data --all")
        self.stdout.write("  python manage.py sync_mitre_data --feed-id 1")
        self.stdout.write("  python manage.py sync_mitre_data --check-freshness")