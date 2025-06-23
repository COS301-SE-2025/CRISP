import logging
import xml.etree.ElementTree as ET
from io import BytesIO
from datetime import datetime
import pytz
from django.utils import timezone
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData

logger = logging.getLogger(__name__)

# Define XML namespaces that is used in STIX 1.x
NAMESPACES = {
    'stix': 'http://stix.mitre.org/stix-1',
    'stixCommon': 'http://stix.mitre.org/common-1',
    'cybox': 'http://cybox.mitre.org/cybox-2',
    'indicator': 'http://stix.mitre.org/Indicator-2',
    'AddressObj': 'http://cybox.mitre.org/objects#AddressObject-2',
    'DomainNameObj': 'http://cybox.mitre.org/objects#DomainNameObject-1',
    'URIObj': 'http://cybox.mitre.org/objects#URIObject-2',
    'FileObj': 'http://cybox.mitre.org/objects#FileObject-2',
}

class STIX1Parser:
    """
    Parser for STIX 1.x XML content received from TAXII 1.x feeds.
    """
    
    def __init__(self):
        # Register namespaces
        for prefix, uri in NAMESPACES.items():
            ET.register_namespace(prefix, uri)
        logger.info("STIX1Parser initialized with registered namespaces")
    
    def parse_content_block(self, content, threat_feed=None):
        """
        Parse a STIX 1.x content block and extract indicators and TTPs.
        
        Args:
            content (bytes or str): STIX 1.x XML content
            threat_feed: ThreatFeed model instance to associate with extracted data
            
        Returns:
            dict: Dictionary with extraction statistics
        """
        stats = {
            'indicators_created': 0,
            'indicators_updated': 0,
            'ttp_created': 0,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        if not content:
            logger.warning("Empty content block received")
            stats['skipped'] += 1
            return stats
        
        try:
            # Convert content to bytes
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            # Log content info
            logger.info(f"Parsing XML content of length {len(content)}")
            content_preview = content[:200].decode('utf-8', errors='replace')
            logger.info(f"Content preview: {content_preview}...")
            
            # Parse XML
            try:
                root = ET.parse(BytesIO(content)).getroot()
                logger.info(f"Successfully parsed XML. Root tag: {root.tag}")
                
                # Process STIX Package
                self._process_stix_package(root, threat_feed, stats)
            except ET.ParseError as pe:
                logger.error(f"XML parsing error: {str(pe)}")
                stats['errors'] += 1
            
            return stats
        
        except Exception as e:
            logger.error(f"Error parsing STIX 1.x content: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            stats['errors'] += 1
            return stats
    
    def _process_stix_package(self, stix_package, threat_feed, stats):
        """
        Process a STIX Package element to extract indicators and TTPs.
        """
        # Extract STIX package ID if available
        package_id = stix_package.get('{http://stix.mitre.org/common-1}id', '')
        logger.info(f"Processing STIX Package: {package_id}")
        
        # Process indicators using direct tag searches
        logger.info("Looking for indicators")
        
        # Find indicators by searching for namespace-qualified tags or without namespaces
        indicators = []
        
        for indicator_tag in ['{http://stix.mitre.org/Indicator-2}Indicator', 'Indicator']:
            found = self._find_elements_by_tag(stix_package, indicator_tag)
            if found:
                indicators.extend(found)
                logger.info(f"Found {len(found)} indicators with tag {indicator_tag}")
                
        if not indicators:
            logger.info("No indicators found")
        else:
            logger.info(f"Found total of {len(indicators)} indicators")
            
        # Process each indicator
        for indicator in indicators:
            try:
                self._process_single_indicator(indicator, threat_feed, stats)
            except Exception as e:
                logger.error(f"Error processing indicator: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                stats['errors'] += 1
        
        # Process TTPs
        ttp_elements = []
        for ttp_tag in ['{http://stix.mitre.org/TTP-1}TTP', 'TTP']:
            found = self._find_elements_by_tag(stix_package, ttp_tag)
            if found:
                ttp_elements.extend(found)
                logger.info(f"Found {len(found)} TTPs with tag {ttp_tag}")

        for ttp in ttp_elements:
            try:
                self._process_single_ttp(ttp, threat_feed, stats)
            except Exception as e:
                logger.error(f"Error processing TTP: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                stats['errors'] += 1
    
    def _find_elements_by_tag(self, element, tag_name):
        """
        Find all elements with a specific tag recursively.
        """
        result = []
        
        # Check current element
        if element.tag.endswith(tag_name.split('}')[-1]):
            result.append(element)
            
        # Check all children recursively
        for child in element:
            result.extend(self._find_elements_by_tag(child, tag_name))
            
        return result
    
    def _process_single_indicator(self, indicator, threat_feed, stats):
        """
        Process a single indicator element and create/update Indicator model.
        """
        # Extract indicator ID
        indicator_id = indicator.get('{http://stix.mitre.org/common-1}id', '')
        
        # Try alternative attribute name if ID not found
        if not indicator_id:
            for attr_name, attr_value in indicator.attrib.items():
                if attr_name.endswith('id') or attr_name.endswith('ID'):
                    indicator_id = attr_value
                    break
        
        if not indicator_id:
            logger.warning("Indicator without ID found, skipping")
            stats['skipped'] += 1
            return
        
        logger.info(f"Processing indicator: {indicator_id}")
        
        # Extract indicator type and value
        indicator_type = 'other'
        indicator_value = self._extract_observable_value(indicator)
        
        if not indicator_value:
            logger.warning(f"Could not extract value for indicator {indicator_id}, skipping")
            stats['skipped'] += 1
            return
        
        # Create indicator data
        indicator_data = {
            'type': indicator_type,
            'value': indicator_value,
            'stix_id': indicator_id,
            'description': self._get_element_text(indicator, "Description") or "Imported from TAXII feed",
            'confidence': 50,  # Default confidence
            'is_anonymized': False,
        }
        
        # Log the indicator data
        logger.info(f"Extracted indicator data: {indicator_data}")
        
        # Check if indicator already exists
        existing = Indicator.objects.filter(stix_id=indicator_id).first()
        
        if existing:
            # Update existing indicator
            for key, value in indicator_data.items():
                setattr(existing, key, value)
            
            existing.updated_at = timezone.now()
            existing.save()
            stats['indicators_updated'] += 1
            logger.info(f"Updated indicator: {indicator_id}")
        else:
            # Create new indicator ONLY if we have a threat feed
            if threat_feed:
                indicator_data['threat_feed'] = threat_feed
                Indicator.objects.create(**indicator_data)
                stats['indicators_created'] += 1
                logger.info(f"Created indicator: {indicator_id}")
            else:
                # Skip creation if no threat feed is provided
                logger.warning(f"Cannot create indicator {indicator_id}: No threat feed provided")
                stats['skipped'] += 1
    
    def _extract_observable_value(self, indicator):
        """Extract value from an observable - simplified version"""
        # Look for common value elements
        for value_tag in ['Value', 'Address_Value', 'Hash_Value']:
            for elem in self._find_elements_by_tag(indicator, value_tag):
                if elem.text and elem.text.strip():
                    return elem.text.strip()
        
        # If we can't find a specific value element then just- use any text content
        for elem in indicator.iter():
            if elem.text and elem.text.strip() and len(elem.text.strip()) > 4:
                return elem.text.strip()
                
        return None
    
    def _get_element_text(self, parent, tag_name):
        """Get text of a child element by tag name"""
        for elem in self._find_elements_by_tag(parent, tag_name):
            if elem.text:
                return elem.text.strip()
        return None
    
    def _process_single_ttp(self, ttp, threat_feed, stats):
        """
        Process a single TTP element and create/update TTPData model.
        
        Args:
            ttp: ElementTree element of the TTP
            threat_feed: ThreatFeed model instance
            stats: Statistics dictionary to update
        """
        # Extract TTP ID
        ttp_id = ttp.get('{http://stix.mitre.org/common-1}id', '')
        
        # Try alternative attribute name if ID not found
        if not ttp_id:
            for attr_name, attr_value in ttp.attrib.items():
                if attr_name.endswith('id') or attr_name.endswith('ID'):
                    ttp_id = attr_value
                    break
        
        if not ttp_id:
            logger.warning("TTP without ID found, skipping")
            stats['skipped'] += 1
            return
        
        logger.info(f"Processing TTP: {ttp_id}")
        
        # Extract title/name and description
        name = self._get_element_text(ttp, "Title") or "Unknown TTP"
        description = self._get_element_text(ttp, "Description") or ""
        
        mitre_technique_id = None
        mitre_tactic = None
        
        # Create TTP data
        ttp_data = {
            'name': name,
            'description': description,
            'stix_id': ttp_id,
            'is_anonymized': False,
        }
        
        # Add MITRE ATT&CK info if available
        if mitre_technique_id:
            ttp_data['mitre_technique_id'] = mitre_technique_id
        
        if mitre_tactic:
            # Default to 'other' if not a recognized tactic
            ttp_data['mitre_tactic'] = 'other'
        
        # Log the TTP data
        logger.info(f"Extracted TTP data: {ttp_data}")
        
        # Check if TTP already exists
        existing = TTPData.objects.filter(stix_id=ttp_id).first()
        
        if existing:
            # Update existing TTP
            for key, value in ttp_data.items():
                setattr(existing, key, value)
            
            existing.updated_at = timezone.now()
            existing.save()
            stats['ttp_updated'] += 1
            logger.info(f"Updated TTP: {ttp_id}")
        else:
            # Create new TTP - only if we have a threat feed
            if threat_feed:
                ttp_data['threat_feed'] = threat_feed
                TTPData.objects.create(**ttp_data)
                stats['ttp_created'] += 1
                logger.info(f"Created TTP: {ttp_id}")
            else:
                logger.warning(f"Cannot create TTP {ttp_id}: No threat feed provided")
                stats['skipped'] += 1