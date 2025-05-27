"""Management command to refresh a feed"""
from django.core.management.base import BaseCommand, CommandError
from feed_consumption.models import ExternalFeedSource
from feed_consumption.tasks import manual_feed_refresh

class Command(BaseCommand):
    help = 'Refreshes a TAXII feed immediately'
    
    def add_arguments(self, parser):
        parser.add_argument('feed_id', help='ID of the feed to refresh')
        
    def handle(self, *args, **options):
        feed_id = options['feed_id']
        
        try:
            feed = ExternalFeedSource.objects.get(id=feed_id)
        except ExternalFeedSource.DoesNotExist:
            raise CommandError(f'Feed with ID "{feed_id}" does not exist')
            
        if not feed.collection_id:
            raise CommandError(f'Feed "{feed.name}" has no collection set')
            
        self.stdout.write(f'Refreshing feed: {feed.name}')
        
        # Start the refresh task
        result = manual_feed_refresh.delay(feed_id)
        
        self.stdout.write(self.style.SUCCESS(f'Feed refresh started. Task ID: {result.id}'))
        self.stdout.write('Use "celery -A crisp_project result <task_id>" to check the result.')
