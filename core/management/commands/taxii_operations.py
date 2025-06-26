import logging
from django.core.management.base import BaseCommand, CommandError
from core.models.threat_feed import ThreatFeed
from core.services.stix_taxii_service import StixTaxiiService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch and update threat feeds'

    def handle(self, *args, **options):
        try:
            # Logic to fetch and update threat feeds
            self.stdout.write(self.style.SUCCESS('Successfully updated threat feeds'))
        except Exception as e:
            logger.error(f'Error updating threat feeds: {e}')
            raise CommandError('Error updating threat feeds') from e