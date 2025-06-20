import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import stix2

from .models import STIXObject, Organization, Collection, CollectionObject
from .otx_client import OTXClient, OTXAPIError
from stix_factory.factory import STIXObjectFactoryRegistry

logger = logging.getLogger(__name__)

class OTXProcessor:
    """
    Processes OTX threat intelligence data and converts it to STIX format.
    """
    
    def __init__(self, organization: Organization, collection: Collection):
        """
        Initialize processor with target organization and collection.
        
        Args:
            organization: Organization that will own the processed data
            collection: Collection to store the processed STIX objects
        """
        self.organization = organization
        self.collection = collection
        self.client = OTXClient()
        self.factory_registry = STIXObjectFactoryRegistry()
        
    def convert_otx_pulse_to_stix(self, pulse: Dict[str, Any]) -> List[stix2.v21.base._STIXBase]:
        """
        Convert an OTX pulse to STIX objects.
        
        Args:
            pulse: OTX pulse data
            
        Returns:
            List of STIX objects created from the pulse
        """
        stix_objects = []
        
        try:
            # Create a STIX Report object for the pulse
            report_data = {
                'type': 'report',
                'name': pulse.get('name', 'Unknown Pulse'),
                'description': pulse.get('description', ''),
                'published': pulse.get('created', timezone.now().isoformat()),
                'labels': ['threat-report'],
                'object_refs': [],  # Will be populated with indicator references
            }
            
            # Add external references
            if pulse.get('references'):
                report_data['external_references'] = [
                    {'source_name': 'OTX', 'url': ref} 
                    for ref in pulse['references'] if ref
                ]
            
            # Add tags as labels if available
            if pulse.get('tags'):
                report_data['labels'].extend(pulse['tags'])
            
            # Process indicators from the pulse
            indicators = pulse.get('indicators', [])
            indicator_refs = []
            
            for indicator_data in indicators:
                stix_indicator = self._convert_otx_indicator_to_stix(indicator_data, pulse)
                if stix_indicator:
                    stix_objects.append(stix_indicator)
                    indicator_refs.append(stix_indicator.id)
            
            # Update report with indicator references
            if indicator_refs:
                report_data['object_refs'] = indicator_refs
                
                # Create the report object
                report = self.factory_registry.create_object(report_data)
                stix_objects.append(report)
            
            logger.info(f"Converted OTX pulse '{pulse.get('name')}' to {len(stix_objects)} STIX objects")
            
        except Exception as e:
            logger.error(f"Error converting OTX pulse to STIX: {e}")
            
        return stix_objects
    
    def _convert_otx_indicator_to_stix(self, indicator: Dict[str, Any], pulse: Dict[str, Any]) -> Optional[stix2.v21.Indicator]:
        """
        Convert an OTX indicator to a STIX indicator.
        
        Args:
            indicator: OTX indicator data
            pulse: Parent pulse data for context
            
        Returns:
            STIX Indicator object or None if conversion fails
        """
        try:
            indicator_type = indicator.get('type', '').lower()
            indicator_value = indicator.get('indicator', '')
            
            if not indicator_value:
                logger.warning("Skipping indicator with no value")
                return None
            
            # Create STIX pattern based on indicator type
            pattern = self._create_stix_pattern(indicator_type, indicator_value)
            if not pattern:
                logger.warning(f"Could not create STIX pattern for indicator type: {indicator_type}")
                return None
            
            # Prepare indicator data
            indicator_data = {
                'type': 'indicator',
                'pattern': pattern,
                'pattern_type': 'stix',
                'valid_from': pulse.get('created', timezone.now().isoformat()),
                'labels': ['malicious-activity'],
                'description': f"Indicator from OTX pulse: {pulse.get('name', 'Unknown')}",
            }
            
            # Add confidence if available
            if indicator.get('confidence'):
                indicator_data['confidence'] = indicator['confidence']
            
            # Add external references
            indicator_data['external_references'] = [
                {
                    'source_name': 'AlienVault OTX',
                    'url': f"https://otx.alienvault.com/pulse/{pulse.get('id', '')}"
                }
            ]
            
            # Create STIX indicator
            stix_indicator = self.factory_registry.create_object(indicator_data)
            return stix_indicator
            
        except Exception as e:
            logger.error(f"Error converting OTX indicator to STIX: {e}")
            return None
    
    def _create_stix_pattern(self, indicator_type: str, value: str) -> Optional[str]:
        """
        Create a STIX pattern from OTX indicator type and value.
        
        Args:
            indicator_type: OTX indicator type
            value: Indicator value
            
        Returns:
            STIX pattern string or None if type not supported
        """
        # Mapping of OTX types to STIX patterns
        pattern_mapping = {
            'ipv4': f"[ipv4-addr:value = '{value}']",
            'ipv6': f"[ipv6-addr:value = '{value}']",
            'domain': f"[domain-name:value = '{value}']",
            'hostname': f"[domain-name:value = '{value}']",
            'url': f"[url:value = '{value}']",
            'uri': f"[url:value = '{value}']",
            'filehash-md5': f"[file:hashes.MD5 = '{value}']",
            'filehash-sha1': f"[file:hashes.SHA1 = '{value}']",
            'filehash-sha256': f"[file:hashes.SHA256 = '{value}']",
            'email': f"[email-addr:value = '{value}']",
            'mutex': f"[mutex:name = '{value}']",
            'cve': f"[vulnerability:name = '{value}']",
        }
        
        return pattern_mapping.get(indicator_type.lower())
    
    def process_otx_pulses(self, pulses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple OTX pulses and store as STIX objects.
        
        Args:
            pulses: List of OTX pulse data
            
        Returns:
            Processing results summary
        """
        results = {
            'total_pulses': len(pulses),
            'processed_pulses': 0,
            'created_objects': 0,
            'errors': []
        }
        
        for pulse in pulses:
            try:
                with transaction.atomic():
                    # Convert pulse to STIX objects
                    stix_objects = self.convert_otx_pulse_to_stix(pulse)
                    
                    # Store STIX objects in database
                    for stix_obj in stix_objects:
                        db_obj = self._store_stix_object(stix_obj)
                        if db_obj:
                            # Add to collection
                            CollectionObject.objects.get_or_create(
                                collection=self.collection,
                                stix_object=db_obj
                            )
                            results['created_objects'] += 1
                    
                    results['processed_pulses'] += 1
                    
            except Exception as e:
                error_msg = f"Error processing pulse '{pulse.get('name', 'Unknown')}': {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        logger.info(f"OTX processing complete. Processed {results['processed_pulses']}/{results['total_pulses']} pulses, "
                   f"created {results['created_objects']} objects")
        
        return results
    
    def _store_stix_object(self, stix_obj: stix2.v21.base._STIXBase) -> Optional[STIXObject]:
        """
        Store a STIX object in the database.
        
        Args:
            stix_obj: STIX object to store
            
        Returns:
            Created STIXObject instance or None if creation fails
        """
        try:
            # Convert STIX object to dictionary
            stix_dict = stix_obj._inner
            
            # Check if object already exists
            if STIXObject.objects.filter(stix_id=stix_dict['id']).exists():
                logger.debug(f"STIX object {stix_dict['id']} already exists, skipping")
                return None
            
            # Create database object
            db_obj = STIXObject(
                stix_id=stix_dict['id'],
                stix_type=stix_dict['type'],
                spec_version=stix_dict.get('spec_version', '2.1'),
                created=datetime.fromisoformat(stix_dict['created'].replace('Z', '+00:00')),
                modified=datetime.fromisoformat(stix_dict['modified'].replace('Z', '+00:00')),
                created_by_ref=stix_dict.get('created_by_ref', ''),
                revoked=stix_dict.get('revoked', False),
                labels=stix_dict.get('labels', []),
                confidence=stix_dict.get('confidence', 0),
                external_references=stix_dict.get('external_references', []),
                object_marking_refs=stix_dict.get('object_marking_refs', []),
                granular_markings=stix_dict.get('granular_markings', []),
                raw_data=stix_dict,
                source_organization=self.organization,
            )
            
            db_obj.save()
            logger.debug(f"Stored STIX object: {stix_dict['id']}")
            return db_obj
            
        except Exception as e:
            logger.error(f"Error storing STIX object: {e}")
            return None
    
    def fetch_and_process_recent_pulses(self, days_back: int = 1) -> Dict[str, Any]:
        """
        Fetch recent pulses from OTX and process them.
        
        Args:
            days_back: Number of days back to fetch pulses
            
        Returns:
            Processing results summary
        """
        try:
            # Calculate date threshold
            since_date = timezone.now() - timedelta(days=days_back)
            
            # Fetch pulses from OTX
            logger.info(f"Fetching OTX pulses modified since {since_date}")
            pulses = self.client.get_pulses(
                modified_since=since_date,
                limit=settings.OTX_SETTINGS.get('BATCH_SIZE', 50)
            )
            
            # Process the pulses
            results = self.process_otx_pulses(pulses)
            
            return results
            
        except OTXAPIError as e:
            logger.error(f"OTX API error: {e}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error processing OTX feeds: {e}")
            return {'error': str(e)}