"""
Repository for handling Indicator data operations.
"""
import logging
from typing import List, Optional
from django.db import transaction

from core.models.indicator import Indicator

logger = logging.getLogger(__name__)


class IndicatorRepository:
    """Repository for Indicator operations"""
    
    def __init__(self):
        pass
    
    def create_from_stix(self, stix_data, threat_feed=None):
        """Create indicator from STIX data"""
        try:
            # Extract STIX ID if available
            stix_id = None
            if hasattr(stix_data, 'id'):
                stix_id = str(stix_data.id)
            elif isinstance(stix_data, dict) and 'id' in stix_data:
                stix_id = stix_data['id']
            
            # Check if indicator already exists
            if stix_id:
                existing = Indicator.objects.filter(stix_id=stix_id).first()
                if existing:
                    logger.info(f"Indicator {stix_id} already exists, updating")
                    return self._update_indicator(existing, stix_data, threat_feed)
            
            # Create new indicator
            indicator_data = self._extract_indicator_data(stix_data)
            indicator = Indicator.objects.create(
                stix_id=stix_id,
                threat_feed=threat_feed,
                **indicator_data
            )
            
            logger.info(f"Created indicator {indicator.id}")
            return indicator
            
        except Exception as e:
            logger.error(f"Error creating indicator from STIX: {str(e)}")
            raise
    
    def get_by_id(self, indicator_id):
        """Get indicator by ID"""
        try:
            return Indicator.objects.get(id=indicator_id)
        except Indicator.DoesNotExist:
            return None
    
    def get_by_stix_id(self, stix_id):
        """Get indicator by STIX ID"""
        try:
            return Indicator.objects.get(stix_id=stix_id)
        except Indicator.DoesNotExist:
            return None
    
    def get_all(self):
        """Get all indicators"""
        return Indicator.objects.all()
    
    def get_by_threat_feed(self, threat_feed):
        """Get indicators by threat feed"""
        return Indicator.objects.filter(threat_feed=threat_feed)
    
    def create(self, indicator_data):
        """Create a new indicator"""
        return Indicator.objects.create(**indicator_data)
    
    def get_by_feed(self, feed_id):
        """Get indicators by threat feed ID"""
        return Indicator.objects.filter(threat_feed_id=feed_id)
    
    def get_by_type(self, indicator_type):
        """Get indicators by type"""
        return Indicator.objects.filter(type=indicator_type)
    
    def update(self, indicator_id, update_data):
        """Update indicator by ID"""
        try:
            indicator = Indicator.objects.get(id=indicator_id)
            for key, value in update_data.items():
                if hasattr(indicator, key):
                    setattr(indicator, key, value)
            indicator.save()
            return indicator
        except Indicator.DoesNotExist:
            return None
    
    def delete(self, indicator_id):
        """Delete indicator by ID"""
        try:
            indicator = Indicator.objects.get(id=indicator_id)
            indicator.delete()
            return True
        except Indicator.DoesNotExist:
            return False
    
    def _extract_indicator_data(self, stix_data):
        """Extract indicator data from STIX object"""
        data = {}
        
        # Extract pattern/value from STIX data
        if hasattr(stix_data, 'pattern'):
            pattern = str(stix_data.pattern)
            # Extract value from pattern (simplified)
            if '[file:hashes.' in pattern:
                data['type'] = 'file_hash'
                data['value'] = pattern.split("'")[1] if "'" in pattern else 'unknown_hash'
                data['hash_type'] = 'md5'  # Default
            elif '[domain-name:' in pattern:
                data['type'] = 'domain'
                data['value'] = pattern.split("'")[1] if "'" in pattern else 'unknown_domain'
            elif '[ipv4-addr:' in pattern or '[ipv6-addr:' in pattern:
                data['type'] = 'ip'
                data['value'] = pattern.split("'")[1] if "'" in pattern else 'unknown_ip'
            else:
                data['type'] = 'other'
                data['value'] = pattern
        elif isinstance(stix_data, dict) and 'pattern' in stix_data:
            pattern = stix_data['pattern']
            # Extract value from pattern (simplified)
            if '[file:hashes.' in pattern:
                data['type'] = 'file_hash'
                data['value'] = pattern.split("'")[1] if "'" in pattern else 'unknown_hash'
                data['hash_type'] = 'md5'  # Default
            elif '[domain-name:' in pattern:
                data['type'] = 'domain'
                data['value'] = pattern.split("'")[1] if "'" in pattern else 'unknown_domain'
            elif '[ipv4-addr:' in pattern or '[ipv6-addr:' in pattern:
                data['type'] = 'ip'
                data['value'] = pattern.split("'")[1] if "'" in pattern else 'unknown_ip'
            else:
                data['type'] = 'other'
                data['value'] = pattern
        else:
            data['type'] = 'other'
            data['value'] = 'unknown_indicator'
        
        if hasattr(stix_data, 'created'):
            data['first_seen'] = stix_data.created
        elif isinstance(stix_data, dict) and 'created' in stix_data:
            data['first_seen'] = stix_data['created']
        
        if hasattr(stix_data, 'modified'):
            data['last_seen'] = stix_data.modified
        elif isinstance(stix_data, dict) and 'modified' in stix_data:
            data['last_seen'] = stix_data['modified']
        
        # Set description from labels
        if hasattr(stix_data, 'labels'):
            data['description'] = ', '.join(stix_data.labels) if stix_data.labels else ''
        elif isinstance(stix_data, dict) and 'labels' in stix_data:
            data['description'] = ', '.join(stix_data['labels']) if stix_data['labels'] else ''
        
        # Default values
        data.setdefault('confidence', 50)
        data.setdefault('description', '')
        
        return data
    
    def _update_indicator(self, indicator, stix_data, threat_feed=None):
        """Update existing indicator with new STIX data"""
        try:
            updated_data = self._extract_indicator_data(stix_data)
            
            # Update fields
            for key, value in updated_data.items():
                if hasattr(indicator, key):
                    setattr(indicator, key, value)
            
            if threat_feed:
                indicator.threat_feed = threat_feed
            
            indicator.save()
            logger.info(f"Updated indicator {indicator.id}")
            return indicator
            
        except Exception as e:
            logger.error(f"Error updating indicator: {str(e)}")
            raise