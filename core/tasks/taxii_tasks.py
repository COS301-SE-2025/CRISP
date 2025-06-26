from django.utils import timezone
from crisp.celery import app
from core.models.threat_feed import ThreatFeed
from core.services.stix_taxii_service import StixTaxiiService
import logging

logger = logging.getLogger(__name__)