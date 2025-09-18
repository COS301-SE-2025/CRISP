"""
Management command to extract TTPs from threat feeds
"""
from django.core.management.base import BaseCommand, CommandError
from core.services.ttp_extraction_service import TTPExtractionService
from core.models.models import ThreatFeed


class Command(BaseCommand):
    help = 'Extract TTPs from threat feeds using pattern recognition and inference'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feed-id',
            type=int,
            help='Extract TTPs from a specific feed ID'
        )

        parser.add_argument(
            '--feed-name',
            type=str,
            help='Extract TTPs from feeds matching this name pattern'
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='Extract TTPs from all active feeds'
        )

        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-extraction even for feeds that already have TTPs'
        )

        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Include inactive feeds in processing'
        )

        parser.add_argument(
            '--recommendations',
            action='store_true',
            help='Show recommendations for TTP extraction without running extraction'
        )

    def handle(self, *args, **options):
        extraction_service = TTPExtractionService()

        # Show recommendations only
        if options['recommendations']:
            self.show_recommendations(extraction_service)
            return

        # Determine which feeds to process
        feeds_to_process = []

        if options['feed_id']:
            try:
                feed = ThreatFeed.objects.get(id=options['feed_id'])
                feeds_to_process = [feed]
                self.stdout.write(f"Processing feed: {feed.name} (ID: {feed.id})")
            except ThreatFeed.DoesNotExist:
                raise CommandError(f'Feed with ID {options["feed_id"]} does not exist')

        elif options['feed_name']:
            feeds = ThreatFeed.objects.filter(name__icontains=options['feed_name'])
            if not options['inactive']:
                feeds = feeds.filter(is_active=True)
            feeds_to_process = list(feeds)
            self.stdout.write(f"Found {len(feeds_to_process)} feeds matching '{options['feed_name']}'")

        elif options['all']:
            feeds = ThreatFeed.objects.all()
            if not options['inactive']:
                feeds = feeds.filter(is_active=True)
            feeds_to_process = list(feeds)
            self.stdout.write(f"Processing all {len(feeds_to_process)} {'active ' if not options['inactive'] else ''}feeds")

        else:
            raise CommandError('Must specify --feed-id, --feed-name, --all, or --recommendations')

        if not feeds_to_process:
            self.stdout.write(self.style.WARNING('No feeds to process'))
            return

        # Process each feed
        total_extracted = 0
        successful_feeds = 0
        failed_feeds = 0

        for feed in feeds_to_process:
            self.stdout.write(f"\nProcessing: {feed.name}")

            try:
                result = extraction_service.extract_ttps_from_feed(
                    threat_feed=feed,
                    force_reextract=options['force']
                )

                if result['success']:
                    extracted_count = len(result['ttps_extracted'])
                    existing_count = len(result['ttps_existing'])
                    total_extracted += extracted_count
                    successful_feeds += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Extracted {extracted_count} TTPs, "
                            f"{existing_count} already existed, "
                            f"analyzed {result['indicators_analyzed']} indicators"
                        )
                    )

                    # Show extracted TTPs
                    for ttp in result['ttps_extracted']:
                        self.stdout.write(f"  - {ttp['technique_id']}: {ttp['name']}")

                else:
                    failed_feeds += 1
                    self.stdout.write(
                        self.style.ERROR(f"✗ Failed to extract TTPs")
                    )
                    for error in result['errors']:
                        self.stdout.write(f"    Error: {error}")

            except Exception as e:
                failed_feeds += 1
                self.stdout.write(
                    self.style.ERROR(f"✗ Unexpected error: {str(e)}")
                )

        # Summary
        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"EXTRACTION SUMMARY")
        self.stdout.write(f"{'='*50}")
        self.stdout.write(f"Feeds processed: {len(feeds_to_process)}")
        self.stdout.write(f"Successful: {successful_feeds}")
        self.stdout.write(f"Failed: {failed_feeds}")
        self.stdout.write(f"Total TTPs extracted: {total_extracted}")

        if successful_feeds > 0:
            self.stdout.write(self.style.SUCCESS(f"\n✓ TTP extraction completed successfully"))
        else:
            self.stdout.write(self.style.ERROR(f"\n✗ No TTPs were extracted"))

    def show_recommendations(self, extraction_service):
        """Show TTP extraction recommendations"""
        self.stdout.write("Getting TTP extraction recommendations...")

        recommendations = extraction_service.get_extraction_recommendations()

        if 'error' in recommendations:
            self.stdout.write(self.style.ERROR(f"Error getting recommendations: {recommendations['error']}"))
            return

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write("TTP EXTRACTION RECOMMENDATIONS")
        self.stdout.write(f"{'='*50}")

        # Feeds without TTPs
        if recommendations['feeds_without_ttps']:
            self.stdout.write(f"\n📋 FEEDS WITHOUT TTPs ({len(recommendations['feeds_without_ttps'])})")
            self.stdout.write("-" * 40)
            for feed in recommendations['feeds_without_ttps'][:10]:  # Show top 10
                self.stdout.write(
                    f"• {feed['name']} - {feed['indicator_count']} indicators "
                    f"(~{feed['potential_ttps']} potential TTPs)"
                )

        # Feeds with low coverage
        if recommendations['feeds_with_low_ttp_coverage']:
            self.stdout.write(f"\n📊 FEEDS WITH LOW TTP COVERAGE ({len(recommendations['feeds_with_low_ttp_coverage'])})")
            self.stdout.write("-" * 40)
            for feed in recommendations['feeds_with_low_ttp_coverage'][:10]:  # Show top 10
                ratio = feed['coverage_ratio']
                self.stdout.write(
                    f"• {feed['name']} - {feed['ttp_count']} TTPs / {feed['indicator_count']} indicators "
                    f"({ratio:.2%} coverage)"
                )

        # Recommendations
        if recommendations['recommendations']:
            self.stdout.write(f"\n💡 RECOMMENDATIONS")
            self.stdout.write("-" * 40)
            for rec in recommendations['recommendations']:
                priority_color = self.style.ERROR if rec['priority'] == 'high' else self.style.WARNING
                self.stdout.write(priority_color(f"[{rec['priority'].upper()}] {rec['message']}"))

        # Usage suggestions
        self.stdout.write(f"\n🚀 SUGGESTED COMMANDS")
        self.stdout.write("-" * 40)
        if recommendations['feeds_without_ttps']:
            self.stdout.write("Extract TTPs from all feeds without TTPs:")
            self.stdout.write("  python manage.py extract_ttps --all")

        if recommendations['feeds_with_low_ttp_coverage']:
            self.stdout.write("Force re-extraction to improve coverage:")
            self.stdout.write("  python manage.py extract_ttps --all --force")

        self.stdout.write("\nExtract TTPs from a specific feed:")
        self.stdout.write("  python manage.py extract_ttps --feed-id <ID>")

        if not recommendations['feeds_without_ttps'] and not recommendations['feeds_with_low_ttp_coverage']:
            self.stdout.write(self.style.SUCCESS("\n✓ All active feeds have good TTP coverage!"))