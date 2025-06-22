import json
import re
from typing import Dict, Any, Union, Optional, List
from enum import Enum
import stix2
from stix2.base import _STIXBase
from mixbox.parser import parseString as parse_stix1_xml
from mixbox.entities import Entity
import xmltodict
from datetime import datetime

class STIXVersion(Enum):
    """Enumeration of supported STIX versions."""
    STIX_1_0 = "1.0"
    STIX_1_1 = "1.1" 
    STIX_1_2 = "1.2"
    STIX_2_0 = "2.0"
    STIX_2_1 = "2.1"
    UNKNOWN = "unknown"

class STIXVersionDetector:
    """
    Detects STIX version from various input formats.
    """
    
    @classmethod
    def detect_version(cls, data: Union[str, Dict[str, Any], bytes]) -> STIXVersion:
        """
        Detect STIX version from input data.
        
        Args:
            data: STIX data as string (JSON/XML), dictionary, or bytes
            
        Returns:
            STIXVersion enum value
        """
        try:
            # Handle bytes
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Handle string data
            if isinstance(data, str):
                data = data.strip()
                
                # Check if it's XML (STIX 1.x)
                if data.startswith('<?xml') or data.startswith('<stix'):
                    return cls._detect_xml_version(data)
                
                # Try to parse as JSON (STIX 2.x)
                try:
                    parsed_data = json.loads(data)
                    return cls._detect_json_version(parsed_data)
                except json.JSONDecodeError:
                    return STIXVersion.UNKNOWN
            
            # Handle dictionary data (STIX 2.x)
            elif isinstance(data, dict):
                return cls._detect_json_version(data)
            
            # Handle STIX 2.x objects
            elif isinstance(data, _STIXBase):
                return cls._detect_stix2_object_version(data)
                
            return STIXVersion.UNKNOWN
            
        except Exception:
            return STIXVersion.UNKNOWN
    
    @classmethod
    def _detect_xml_version(cls, xml_data: str) -> STIXVersion:
        """
        Detect STIX version from XML data.
        
        Args:
            xml_data: XML string
            
        Returns:
            STIXVersion for STIX 1.x or UNKNOWN
        """
        try:
            # Look for version in XML namespace or attributes
            version_patterns = [
                r'xmlns:stix[^=]*="[^"]*stix_core/v?(\d+\.\d+)',
                r'version="(\d+\.\d+)"',
                r'stix-(\d+\.\d+)\.xsd',
                r'STIX_(\d+_\d+)',
            ]
            
            for pattern in version_patterns:
                match = re.search(pattern, xml_data, re.IGNORECASE)
                if match:
                    version_str = match.group(1).replace('_', '.')
                    if version_str.startswith('1.0'):
                        return STIXVersion.STIX_1_0
                    elif version_str.startswith('1.1'):
                        return STIXVersion.STIX_1_1
                    elif version_str.startswith('1.2'):
                        return STIXVersion.STIX_1_2
            
            # Default to 1.2 if XML but no version found
            return STIXVersion.STIX_1_2
            
        except Exception:
            return STIXVersion.UNKNOWN
    
    @classmethod
    def _detect_json_version(cls, json_data: Dict[str, Any]) -> STIXVersion:
        """
        Detect STIX version from JSON data.
        
        Args:
            json_data: Parsed JSON dictionary
            
        Returns:
            STIXVersion for STIX 2.x or UNKNOWN
        """
        try:
            # Check spec_version field (STIX 2.x)
            if 'spec_version' in json_data:
                spec_version = json_data['spec_version']
                if spec_version == '2.0':
                    return STIXVersion.STIX_2_0
                elif spec_version == '2.1':
                    return STIXVersion.STIX_2_1
            
            # Check if it's a STIX bundle
            if json_data.get('type') == 'bundle':
                if 'spec_version' in json_data:
                    spec_version = json_data['spec_version']
                    if spec_version == '2.0':
                        return STIXVersion.STIX_2_0
                    elif spec_version == '2.1':
                        return STIXVersion.STIX_2_1
                
                # Check objects in bundle
                objects = json_data.get('objects', [])
                if objects and isinstance(objects, list):
                    for obj in objects:
                        if isinstance(obj, dict) and 'spec_version' in obj:
                            spec_version = obj['spec_version']
                            if spec_version == '2.0':
                                return STIXVersion.STIX_2_0
                            elif spec_version == '2.1':
                                return STIXVersion.STIX_2_1
            
            # Check for STIX 2.x object structure
            if 'type' in json_data and 'id' in json_data:
                # Default to 2.1 if no spec_version but has STIX 2.x structure
                return STIXVersion.STIX_2_1
                
            return STIXVersion.UNKNOWN
            
        except Exception:
            return STIXVersion.UNKNOWN
    
    @classmethod
    def _detect_stix2_object_version(cls, stix_obj: _STIXBase) -> STIXVersion:
        """
        Detect STIX version from a STIX 2.x object.
        
        Args:
            stix_obj: STIX 2.x object
            
        Returns:
            STIXVersion for STIX 2.x
        """
        try:
            if hasattr(stix_obj, 'spec_version'):
                spec_version = stix_obj.spec_version
                if spec_version == '2.0':
                    return STIXVersion.STIX_2_0
                elif spec_version == '2.1':
                    return STIXVersion.STIX_2_1
            
            # Check class name for version indication
            class_name = stix_obj.__class__.__module__
            if 'v20' in class_name:
                return STIXVersion.STIX_2_0
            elif 'v21' in class_name:
                return STIXVersion.STIX_2_1
                
            # Default to 2.1
            return STIXVersion.STIX_2_1
            
        except Exception:
            return STIXVersion.STIX_2_1

class STIXVersionConverter:
    """
    Converts STIX objects between different versions.
    """
    
    @classmethod
    def convert_to_stix21(cls, data: Union[str, Dict[str, Any]], source_version: STIXVersion) -> Dict[str, Any]:
        """
        Convert STIX data from any version to STIX 2.1.
        
        Args:
            data: STIX data to convert
            source_version: Source STIX version
            
        Returns:
            Dictionary representing STIX 2.1 object
        """
        if source_version == STIXVersion.STIX_2_1:
            # Already STIX 2.1
            if isinstance(data, dict):
                return data
            elif isinstance(data, str):
                return json.loads(data)
        
        elif source_version == STIXVersion.STIX_2_0:
            return cls._convert_stix20_to_stix21(data)
        
        elif source_version in [STIXVersion.STIX_1_0, STIXVersion.STIX_1_1, STIXVersion.STIX_1_2]:
            return cls._convert_stix1x_to_stix21(data, source_version)
        
        else:
            raise ValueError(f"Unsupported source version: {source_version}")
    
    @classmethod
    def _convert_stix20_to_stix21(cls, data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert STIX 2.0 to STIX 2.1.
        
        Args:
            data: STIX 2.0 data
            
        Returns:
            STIX 2.1 dictionary
        """
        if isinstance(data, str):
            data = json.loads(data)
        
        # Create a copy to avoid modifying original
        converted = data.copy()
        
        # Update spec_version
        converted['spec_version'] = '2.1'
        
        # Handle bundle objects
        if converted.get('type') == 'bundle' and 'objects' in converted:
            for obj in converted['objects']:
                if isinstance(obj, dict):
                    obj['spec_version'] = '2.1'
                    # Apply STIX 2.0 to 2.1 specific conversions
                    cls._apply_stix20_to_stix21_object_changes(obj)
        else:
            # Single object
            cls._apply_stix20_to_stix21_object_changes(converted)
        
        return converted
    
    @classmethod
    def _apply_stix20_to_stix21_object_changes(cls, obj: Dict[str, Any]) -> None:
        """
        Apply STIX 2.0 to 2.1 specific object changes.
        
        Args:
            obj: STIX object dictionary to modify in-place
        """
        obj_type = obj.get('type')
        
        # Handle malware object changes
        if obj_type == 'malware':
            # In STIX 2.1, malware requires 'is_family' field
            if 'is_family' not in obj:
                obj['is_family'] = True  # Default assumption
        
        # Handle indicator pattern changes
        if obj_type == 'indicator':
            # In STIX 2.1, pattern_type is required
            if 'pattern_type' not in obj:
                obj['pattern_type'] = 'stix'
        
        # Add other version-specific conversions as needed
    
    @classmethod
    def _convert_stix1x_to_stix21(cls, data: Union[str, Dict[str, Any]], source_version: STIXVersion) -> Dict[str, Any]:
        """
        Convert STIX 1.x to STIX 2.1.
        
        Args:
            data: STIX 1.x data (typically XML)
            source_version: Source STIX 1.x version
            
        Returns:
            STIX 2.1 dictionary
        """
        if isinstance(data, str):
            # Parse XML to dictionary
            try:
                xml_dict = xmltodict.parse(data)
            except Exception as e:
                raise ValueError(f"Failed to parse STIX 1.x XML: {e}")
        else:
            xml_dict = data
        
        # Convert STIX 1.x structure to STIX 2.1
        converted_objects = []
        
        # Extract STIX package
        stix_package = xml_dict.get('stix:STIX_Package', {})
        
        # Convert indicators
        indicators = cls._extract_stix1x_indicators(stix_package)
        converted_objects.extend(indicators)
        
        # Convert TTPs (Tactics, Techniques, and Procedures) to attack patterns
        ttps = cls._extract_stix1x_ttps(stix_package)
        converted_objects.extend(ttps)
        
        # Convert threat actors
        threat_actors = cls._extract_stix1x_threat_actors(stix_package)
        converted_objects.extend(threat_actors)
        
        # Create STIX 2.1 bundle
        bundle = {
            'type': 'bundle',
            'id': f"bundle--{cls._generate_uuid()}",
            'spec_version': '2.1',
            'objects': converted_objects
        }
        
        return bundle
    
    @classmethod
    def _extract_stix1x_indicators(cls, stix_package: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and convert STIX 1.x indicators to STIX 2.1 format.
        
        Args:
            stix_package: STIX 1.x package dictionary
            
        Returns:
            List of STIX 2.1 indicator dictionaries
        """
        indicators = []
        
        # Navigate STIX 1.x structure to find indicators
        stix_indicators = stix_package.get('stix:Indicators', {}).get('stix:Indicator', [])
        
        if not isinstance(stix_indicators, list):
            stix_indicators = [stix_indicators]
        
        for indicator in stix_indicators:
            if not indicator:
                continue
                
            # Create STIX 2.1 indicator
            stix21_indicator = {
                'type': 'indicator',
                'id': f"indicator--{cls._generate_uuid()}",
                'spec_version': '2.1',
                'created': cls._format_timestamp(indicator.get('@timestamp', datetime.utcnow().isoformat())),
                'modified': cls._format_timestamp(indicator.get('@timestamp', datetime.utcnow().isoformat())),
                'pattern': cls._convert_stix1x_pattern_to_stix21(indicator),
                'pattern_type': 'stix',
                'valid_from': cls._format_timestamp(indicator.get('@timestamp', datetime.utcnow().isoformat())),
                'labels': ['malicious-activity']  # Default label
            }
            
            # Add title as name if available
            if 'indicator:Title' in indicator:
                stix21_indicator['name'] = indicator['indicator:Title']
            
            # Add description if available
            if 'indicator:Description' in indicator:
                stix21_indicator['description'] = indicator['indicator:Description']
            
            indicators.append(stix21_indicator)
        
        return indicators
    
    @classmethod
    def _extract_stix1x_ttps(cls, stix_package: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and convert STIX 1.x TTPs to STIX 2.1 attack patterns.
        
        Args:
            stix_package: STIX 1.x package dictionary
            
        Returns:
            List of STIX 2.1 attack pattern dictionaries
        """
        attack_patterns = []
        
        # Navigate STIX 1.x structure to find TTPs
        stix_ttps = stix_package.get('stix:TTPs', {}).get('stix:TTP', [])
        
        if not isinstance(stix_ttps, list):
            stix_ttps = [stix_ttps]
        
        for ttp in stix_ttps:
            if not ttp:
                continue
                
            # Create STIX 2.1 attack pattern
            attack_pattern = {
                'type': 'attack-pattern',
                'id': f"attack-pattern--{cls._generate_uuid()}",
                'spec_version': '2.1',
                'created': cls._format_timestamp(ttp.get('@timestamp', datetime.utcnow().isoformat())),
                'modified': cls._format_timestamp(ttp.get('@timestamp', datetime.utcnow().isoformat()))
            }
            
            # Add title as name if available
            if 'ttp:Title' in ttp:
                attack_pattern['name'] = ttp['ttp:Title']
            
            # Add description if available
            if 'ttp:Description' in ttp:
                attack_pattern['description'] = ttp['ttp:Description']
            
            attack_patterns.append(attack_pattern)
        
        return attack_patterns
    
    @classmethod
    def _extract_stix1x_threat_actors(cls, stix_package: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and convert STIX 1.x threat actors to STIX 2.1 format.
        
        Args:
            stix_package: STIX 1.x package dictionary
            
        Returns:
            List of STIX 2.1 threat actor dictionaries
        """
        threat_actors = []
        
        # Navigate STIX 1.x structure to find threat actors
        stix_threat_actors = stix_package.get('stix:Threat_Actors', {}).get('stix:Threat_Actor', [])
        
        if not isinstance(stix_threat_actors, list):
            stix_threat_actors = [stix_threat_actors]
        
        for threat_actor in stix_threat_actors:
            if not threat_actor:
                continue
                
            # Create STIX 2.1 threat actor
            stix21_threat_actor = {
                'type': 'threat-actor',
                'id': f"threat-actor--{cls._generate_uuid()}",
                'spec_version': '2.1',
                'created': cls._format_timestamp(threat_actor.get('@timestamp', datetime.utcnow().isoformat())),
                'modified': cls._format_timestamp(threat_actor.get('@timestamp', datetime.utcnow().isoformat())),
                'labels': ['unknown']  # Default label
            }
            
            # Add title as name if available
            if 'threatActor:Title' in threat_actor:
                stix21_threat_actor['name'] = threat_actor['threatActor:Title']
            
            # Add description if available
            if 'threatActor:Description' in threat_actor:
                stix21_threat_actor['description'] = threat_actor['threatActor:Description']
            
            threat_actors.append(stix21_threat_actor)
        
        return threat_actors
    
    @classmethod
    def _convert_stix1x_pattern_to_stix21(cls, indicator: Dict[str, Any]) -> str:
        """
        Convert STIX 1.x indicator pattern to STIX 2.1 pattern.
        
        Args:
            indicator: STIX 1.x indicator dictionary
            
        Returns:
            STIX 2.1 pattern string
        """
        # This is a simplified conversion - real implementation would be more complex
        # Extract observable information from STIX 1.x indicator
        
        # Look for common observables
        observable = indicator.get('indicator:Observable', {})
        
        # Try to extract file hash
        if 'cybox:Object' in observable:
            obj = observable['cybox:Object']
            if 'FileObj:File' in obj:
                file_obj = obj['FileObj:File']
                if 'FileObj:Hashes' in file_obj:
                    hashes = file_obj['FileObj:Hashes']
                    if 'Common:Hash' in hashes:
                        hash_obj = hashes['Common:Hash']
                        if 'Common:Simple_Hash_Value' in hash_obj:
                            hash_value = hash_obj['Common:Simple_Hash_Value']
                            hash_type = hash_obj.get('Common:Type', 'MD5').lower()
                            return f"[file:hashes.{hash_type} = '{hash_value}']"
        
        # Default pattern if we can't extract specific observable
        return "[file:name = 'unknown']"
    
    @classmethod
    def _generate_uuid(cls) -> str:
        """Generate a UUID string."""
        import uuid
        return str(uuid.uuid4())
    
    @classmethod
    def _format_timestamp(cls, timestamp: str) -> str:
        """
        Format timestamp to ISO 8601 format.
        
        Args:
            timestamp: Input timestamp string
            
        Returns:
            ISO 8601 formatted timestamp
        """
        try:
            # Parse and reformat timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except Exception:
            # Return current timestamp if parsing fails
            return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

class STIXVersionHandler:
    """
    Main handler for managing STIX objects across different versions.
    """
    
    def __init__(self):
        self.detector = STIXVersionDetector()
        self.converter = STIXVersionConverter()
    
    def process_stix_data(self, data: Union[str, Dict[str, Any], bytes]) -> Dict[str, Any]:
        """
        Process STIX data of any version and return STIX 2.1 format.
        
        Args:
            data: STIX data in any supported format/version
            
        Returns:
            Dictionary containing processed STIX 2.1 data and metadata
        """
        # Detect version
        detected_version = self.detector.detect_version(data)
        
        if detected_version == STIXVersion.UNKNOWN:
            raise ValueError("Unable to detect STIX version from input data")
        
        # Convert to STIX 2.1
        stix21_data = self.converter.convert_to_stix21(data, detected_version)
        
        return {
            'stix_data': stix21_data,
            'original_version': detected_version.value,
            'converted_version': '2.1',
            'conversion_notes': self._get_conversion_notes(detected_version)
        }
    
    def _get_conversion_notes(self, source_version: STIXVersion) -> List[str]:
        """
        Get conversion notes for the given source version.
        
        Args:
            source_version: Source STIX version
            
        Returns:
            List of conversion notes
        """
        notes = []
        
        if source_version in [STIXVersion.STIX_1_0, STIXVersion.STIX_1_1, STIXVersion.STIX_1_2]:
            notes.extend([
                "Converted from STIX 1.x XML format to STIX 2.1 JSON format",
                "Some semantic information may be lost in conversion",
                "Observable patterns converted to STIX 2.1 pattern format",
                "TTPs converted to attack-pattern objects"
            ])
        
        elif source_version == STIXVersion.STIX_2_0:
            notes.extend([
                "Converted from STIX 2.0 to STIX 2.1",
                "Added required fields for STIX 2.1 compatibility",
                "Malware objects updated with is_family field",
                "Indicator objects updated with pattern_type field"
            ])
        
        return notes