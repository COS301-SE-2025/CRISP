"""
Publish Feeds Management Command
"""
from django.core.management.base import BaseCommand
from core.models.models import Feed
from crisp_unified.utils import publish_feed


class Command(BaseCommand):
    help = 'Publish threat intelligence feeds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feed-id',
            type=str,
            help='Specific feed ID to publish',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Publish all active feeds',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be published without actually publishing',
        )

    def handle(self, *args, **options):
        if options['feed_id']:
            self.publish_specific_feed(options['feed_id'], options['dry_run'])
        elif options['all']:
            self.publish_all_feeds(options['dry_run'])
        else:
            self.show_feed_status()

    def publish_specific_feed(self, feed_id, dry_run):
        """Publish a specific feed"""
        try:
            feed = Feed.objects.get(id=feed_id)
        except Feed.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Feed with ID {feed_id} not found'))
            return

        if dry_run:
            self.stdout.write(f'Would publish feed: {feed.name}')
            self.stdout.write(f'Collection: {feed.collection.title}')
            self.stdout.write(f'Objects: {feed.collection.stix_objects.count()}')
            return

        try:
            result = publish_feed(feed)
            self.stdout.write(self.style.SUCCESS(f'✓ Published feed: {feed.name}'))
            self.stdout.write(f'  Bundle ID: {result["bundle_id"]}')
            self.stdout.write(f'  Objects: {result["object_count"]}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to publish feed {feed.name}: {e}'))

    def publish_all_feeds(self, dry_run):
        """Publish all active feeds"""
        active_feeds = Feed.objects.filter(status='active')
        
        if not active_feeds.exists():
            self.stdout.write(self.style.WARNING('No active feeds found'))
            return

        self.stdout.write(f'Found {active_feeds.count()} active feeds')
        
        for feed in active_feeds:
            if dry_run:
                self.stdout.write(f'Would publish: {feed.name}')
            else:
                try:
                    result = publish_feed(feed)
                    self.stdout.write(self.style.SUCCESS(f'✓ Published: {feed.name}'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'✗ Failed: {feed.name} - {e}'))

    def show_feed_status(self):
        """Show status of all feeds"""
        feeds = Feed.objects.all()
        
        if not feeds.exists():
            self.stdout.write(self.style.WARNING('No feeds found'))
            return

        self.stdout.write('Feed Status:')
        self.stdout.write('-' * 80)
        
        for feed in feeds:
            status_color = self.style.SUCCESS if feed.status == 'active' else self.style.WARNING
            
            self.stdout.write(f'Name: {feed.name}')
            self.stdout.write(f'Status: {status_color(feed.status)}')
            self.stdout.write(f'Collection: {feed.collection.title}')
            self.stdout.write(f'Objects: {feed.collection.stix_objects.count()}')
            self.stdout.write(f'Last Published: {getattr(feed, "last_published_time", "Never")}')
            self.stdout.write(f'Publish Count: {getattr(feed, "publish_count", 0)}')
            if hasattr(feed, 'last_error') and feed.last_error:
                self.stdout.write(self.style.ERROR(f'Last Error: {feed.last_error}'))
            self.stdout.write('-' * 40)