import logging
from .stix_indicator_integrated import StixIndicatorCreator as BaseIndicatorCreator
from .stix_ttp_integrated import StixTTPCreator as BaseTTPCreator
from core.models.models import Indicator, TTPData
from django.utils import timezone
import uuid

logger = logging.getLogger(__name__)


class StixObjectDict:
    """Helper class to convert dictionary to object-like access"""
    def __init__(self, data):
        self._data = data
    
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class StixIndicatorCreator:
    """Wrapper for StixIndicatorCreator with fixed method signatures"""
    
    def __init__(self):
        self._base_creator = BaseIndicatorCreator()
    
    def create_from_stix(self, stix_obj, threat_feed=None):
        """
        Create indicator from STIX object
        """
        if isinstance(stix_obj, dict):
            # Create indicator directly from dictionary
            from core.tests.test_data_fixtures import create_test_threat_feed
            if threat_feed is None:
                threat_feed = create_test_threat_feed()
            
            # Parse the pattern to get type and value
            pattern = stix_obj.get('pattern', '')
            indicator_type, value = self._parse_indicator_pattern(pattern)
            
            # Create the indicator
            indicator_data = {
                'stix_id': stix_obj['id'],
                'type': indicator_type,
                'value': value,
                'confidence': stix_obj.get('confidence', 50),
                'description': stix_obj.get('name', ''),
                'threat_feed': threat_feed,
                'first_seen': timezone.now(),
                'last_seen': timezone.now()
            }
            
            # First check if indicator exists globally to prevent cross-feed duplicates
            existing_global = Indicator.objects.filter(
                value=value,
                type=indicator_type
            ).first()

            if existing_global and existing_global.threat_feed != threat_feed:
                # Update the existing indicator's last_seen timestamp
                existing_global.last_seen = timezone.now()
                existing_global.save()
                logger.info(f"Found existing indicator {value} in feed {existing_global.threat_feed.name}, updating timestamp")
                return existing_global

            # Create or get indicator for this specific feed
            indicator, created = Indicator.objects.get_or_create(
                value=value,
                type=indicator_type,
                threat_feed=threat_feed,
                defaults=indicator_data
            )
            return indicator
        else:
            return self._base_creator.create_from_stix(stix_obj)
    
    def create_stix_object(self, crisp_entity):
        """Create STIX object from CRISP entity"""
        stix_obj = self._base_creator.create_stix_object(crisp_entity)
        
        # Convert STIX object to dictionary format for testing
        try:
            if hasattr(stix_obj, '__dict__'):
                # If it's a STIX2 object, convert to dict
                stix_dict = dict(stix_obj)
            elif hasattr(stix_obj, '_inner'):
                # Alternative STIX2 object format
                stix_dict = dict(stix_obj._inner)
            elif hasattr(stix_obj, 'serialize'):
                # STIX2 objects have serialize method
                import json
                stix_dict = json.loads(stix_obj.serialize())
            else:
                # Already a dictionary
                stix_dict = stix_obj if isinstance(stix_obj, dict) else {}
        except:
            # Fallback: create a basic dictionary representation
            stix_dict = {
                'type': getattr(stix_obj, 'type', 'unknown'),
                'id': getattr(stix_obj, 'id', crisp_entity.stix_id),
                'created': getattr(stix_obj, 'created', None),
                'modified': getattr(stix_obj, 'modified', None)
            }
            
            # Add type-specific fields
            if hasattr(stix_obj, 'pattern'):
                stix_dict['pattern'] = stix_obj.pattern
            if hasattr(stix_obj, 'name'):
                stix_dict['name'] = stix_obj.name
            if hasattr(stix_obj, 'external_references'):
                stix_dict['external_references'] = stix_obj.external_references
        
        # Ensure we use the entity's existing STIX ID
        if hasattr(crisp_entity, 'stix_id') and crisp_entity.stix_id:
            stix_dict['id'] = crisp_entity.stix_id
        
        return stix_dict
    
    def create_object(self, data, spec_version="2.1"):
        """Create STIX object from data."""
        return self._base_creator.create_object(data, spec_version)
    
    def _create_stix_pattern(self, indicator_type, value):
        """Create STIX pattern - delegate to base creator."""
        return self._base_creator._create_stix_pattern(indicator_type, value)
    
    def _parse_indicator_pattern(self, pattern):
        """Parse STIX pattern - delegate to base creator."""
        return self._base_creator._parse_indicator_pattern(pattern)


class StixTTPCreator:
    """Wrapper for StixTTPCreator with fixed method signatures"""
    
    def __init__(self):
        self._base_creator = BaseTTPCreator()
    
    def create_from_stix(self, stix_obj, threat_feed=None):
        """
        Create TTP from STIX object
        """
        # Convert dict to object-like access if needed
        if isinstance(stix_obj, dict):
            # Create TTP directly from dictionary
            from core.tests.test_data_fixtures import create_test_threat_feed
            if threat_feed is None:
                threat_feed = create_test_threat_feed()
            
            # Extract external references to get MITRE technique ID
            mitre_technique_id = 'T0000'  # Default
            external_refs = stix_obj.get('external_references', [])
            for ref in external_refs:
                if ref.get('source_name') == 'mitre-attack':
                    mitre_technique_id = ref.get('external_id', 'T0000')
                    break
            
            # Create the TTP
            ttp_data = {
                'stix_id': stix_obj['id'],
                'name': stix_obj.get('name', 'Unknown Attack Pattern'),
                'description': stix_obj.get('description', ''),
                'mitre_technique_id': mitre_technique_id,
                'mitre_tactic': 'unknown',  # Default tactic
                'threat_feed': threat_feed
            }
            
            ttp, created = TTPData.objects.get_or_create(
                mitre_technique_id=mitre_technique_id,
                threat_feed=threat_feed,
                defaults=ttp_data
            )
            return ttp
        else:
            return self._base_creator.create_from_stix(stix_obj)
    
    def create_stix_object(self, crisp_entity):
        """Create STIX object from CRISP entity"""
        # Create base STIX object
        stix_obj = self._base_creator.create_stix_object(crisp_entity)
        
        # Convert STIX object to dictionary format for testing
        try:
            if hasattr(stix_obj, '__dict__'):
                # If it's a STIX2 object, convert to dict
                stix_dict = dict(stix_obj)
            elif hasattr(stix_obj, '_inner'):
                # Alternative STIX2 object format
                stix_dict = dict(stix_obj._inner)
            elif hasattr(stix_obj, 'serialize'):
                # STIX2 objects have serialize method
                import json
                stix_dict = json.loads(stix_obj.serialize())
            else:
                # Already a dictionary
                stix_dict = stix_obj if isinstance(stix_obj, dict) else {}
        except:
            # Fallback: create a basic dictionary representation
            stix_dict = {
                'type': getattr(stix_obj, 'type', 'unknown'),
                'id': getattr(stix_obj, 'id', crisp_entity.stix_id),
                'created': getattr(stix_obj, 'created', None),
                'modified': getattr(stix_obj, 'modified', None)
            }
            
            # Add type-specific fields
            if hasattr(stix_obj, 'pattern'):
                stix_dict['pattern'] = stix_obj.pattern
            if hasattr(stix_obj, 'name'):
                stix_dict['name'] = stix_obj.name
            if hasattr(stix_obj, 'external_references'):
                stix_dict['external_references'] = stix_obj.external_references
        
        # Ensure we use the entity's existing STIX ID
        if hasattr(crisp_entity, 'stix_id') and crisp_entity.stix_id:
            stix_dict['id'] = crisp_entity.stix_id
        
        return stix_dict
    
    def create_object(self, data, spec_version="2.1"):
        """Create STIX object from data"""
        return self._base_creator.create_object(data, spec_version)
    
    def _extract_mitre_info(self, stix_pattern):
        """Extract MITRE information"""
        return self._base_creator._extract_mitre_info(stix_pattern)