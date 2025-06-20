import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from ..domain.models import Institution, ThreatFeed, Indicator, TTPData, User
from ..factories.stix_object_creator import StixObjectFactory, StixIndicatorCreator, StixTTPCreator
from .otx_client import OTXClient, OTXAPIError

logger = logging.getLogger(__name__)

class OTXProcessor:
    """
    Processes OTX threat intelligence data and converts it to the CRISP domain model format.
    Integrates with the new architecture using domain models, factories, and services.
    """
    
    def __init__(self, institution: Institution, threat_feed: ThreatFeed):
        """
        Initialize processor with target institution and threat feed.
        
        Args:
            institution: Institution that will own the processed data
            threat_feed: Threat feed to store the processed objects
        """
        self.institution = institution
        self.threat_feed = threat_feed
        self.client = OTXClient()
        self.stix_factory = StixObjectFactory()
        self.indicator_creator = StixIndicatorCreator()
        self.ttp_creator = StixTTPCreator()
        
        # Processing statistics
        self.stats = {
            'pulses_processed': 0,
            'indicators_created': 0,
            'ttps_created': 0,
            'errors': []
        }
    
    def configure_client(self, config: Dict[str, Any]) -> None:
        """
        Configure the OTX client with custom settings.
        
        Args:
            config: Client configuration
        """
        self.client.configure(config)
    
    def convert_otx_pulse_to_domain_objects(self, pulse: Dict[str, Any]) -> Tuple[List[Indicator], List[TTPData]]:
        """
        Convert an OTX pulse to domain model objects.
        
        Args:
            pulse: OTX pulse data
            
        Returns:
            Tuple of (indicators, ttp_data) lists
        """
        indicators = []
        ttp_data_list = []
        
        try:
            # Process indicators from the pulse
            pulse_indicators = pulse.get('indicators', [])
            
            for indicator_data in pulse_indicators:
                domain_indicator = self._convert_otx_indicator_to_domain(indicator_data, pulse)
                if domain_indicator:
                    indicators.append(domain_indicator)
            
            # Extract TTP information if available
            ttp_info = self._extract_ttp_from_pulse(pulse)
            if ttp_info:
                domain_ttp = self._convert_ttp_to_domain(ttp_info, pulse)
                if domain_ttp:
                    ttp_data_list.append(domain_ttp)
            
            logger.info(f"Converted OTX pulse '{pulse.get('name')}' to {len(indicators)} indicators and {len(ttp_data_list)} TTPs")
            
        except Exception as e:
            error_msg = f"Error converting OTX pulse '{pulse.get('name', 'Unknown')}': {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            
        return indicators, ttp_data_list
    
    def _convert_otx_indicator_to_domain(self, indicator: Dict[str, Any], pulse: Dict[str, Any]) -> Optional[Indicator]:
        """
        Convert an OTX indicator to a domain model Indicator.
        
        Args:
            indicator: OTX indicator data
            pulse: Parent pulse data for context
            
        Returns:
            Domain model Indicator or None if conversion fails
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
            
            # Create domain model Indicator
            domain_indicator = Indicator(
                name=f"{indicator_type.upper()}: {indicator_value}",
                description=f"Indicator from OTX pulse: {pulse.get('name', 'Unknown')}",
                pattern=pattern,
                labels=['malicious-activity'],
                valid_from=self._parse_datetime(pulse.get('created')) or timezone.now(),
                confidence=indicator.get('confidence', 50),
                created=self._parse_datetime(pulse.get('created')) or timezone.now(),
                modified=self._parse_datetime(pulse.get('modified')) or timezone.now(),
                created_by_ref=f"identity--otx-{pulse.get('author_name', 'unknown')}",
                external_references=[
                    {
                        'source_name': 'AlienVault OTX',
                        'url': f"https://otx.alienvault.com/pulse/{pulse.get('id', '')}"
                    }
                ],
                threat_feed=self.threat_feed,
                created_by=None,  # Will be set by the service layer
                anonymized=False
            )
            
            return domain_indicator
            
        except Exception as e:
            logger.error(f"Error converting OTX indicator to domain model: {e}")
            return None
    
    def _convert_ttp_to_domain(self, ttp_info: Dict[str, Any], pulse: Dict[str, Any]) -> Optional[TTPData]:
        """
        Convert TTP information to a domain model TTPData.
        
        Args:
            ttp_info: Extracted TTP information
            pulse: Parent pulse data for context
            
        Returns:
            Domain model TTPData or None if conversion fails
        """
        try:
            domain_ttp = TTPData(
                name=ttp_info.get('name', f"TTP from {pulse.get('name', 'Unknown')}"),
                description=ttp_info.get('description', f"TTP extracted from OTX pulse: {pulse.get('name', 'Unknown')}"),
                kill_chain_phases=ttp_info.get('kill_chain_phases', []),
                x_mitre_platforms=ttp_info.get('platforms', []),
                x_mitre_tactics=ttp_info.get('tactics', []),
                x_mitre_techniques=ttp_info.get('techniques', []),
                created=self._parse_datetime(pulse.get('created')) or timezone.now(),
                modified=self._parse_datetime(pulse.get('modified')) or timezone.now(),
                created_by_ref=f"identity--otx-{pulse.get('author_name', 'unknown')}",
                external_references=[
                    {
                        'source_name': 'AlienVault OTX',
                        'url': f"https://otx.alienvault.com/pulse/{pulse.get('id', '')}"
                    }
                ],
                threat_feed=self.threat_feed,
                created_by=None,  # Will be set by the service layer
                anonymized=False
            )
            
            return domain_ttp
            
        except Exception as e:
            logger.error(f"Error converting TTP to domain model: {e}")
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
        # Escape special characters in value
        escaped_value = value.replace("'", "\\'").replace("\\", "\\\\")
        
        # Mapping of OTX types to STIX patterns
        pattern_mapping = {
            'ipv4': f"[ipv4-addr:value = '{escaped_value}']",
            'ipv6': f"[ipv6-addr:value = '{escaped_value}']",
            'domain': f"[domain-name:value = '{escaped_value}']",
            'hostname': f"[domain-name:value = '{escaped_value}']",
            'url': f"[url:value = '{escaped_value}']",
            'uri': f"[url:value = '{escaped_value}']",
            'filehash-md5': f"[file:hashes.MD5 = '{escaped_value}']",
            'filehash-sha1': f"[file:hashes.SHA1 = '{escaped_value}']",
            'filehash-sha256': f"[file:hashes.SHA256 = '{escaped_value}']",
            'email': f"[email-addr:value = '{escaped_value}']",
            'mutex': f"[mutex:name = '{escaped_value}']",
            'cve': f"[vulnerability:name = '{escaped_value}']",
        }
        
        return pattern_mapping.get(indicator_type.lower())
    
    def _extract_ttp_from_pulse(self, pulse: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract TTP information from an OTX pulse.
        
        Args:
            pulse: OTX pulse data
            
        Returns:
            TTP information dictionary or None
        """
        # Look for MITRE ATT&CK references or technique mentions
        description = pulse.get('description', '').lower()
        tags = [tag.lower() for tag in pulse.get('tags', [])]
        
        # Simple extraction based on common patterns
        ttp_info = {
            'name': None,
            'description': None,
            'kill_chain_phases': [],
            'platforms': [],
            'tactics': [],
            'techniques': []
        }
        
        # Check for MITRE ATT&CK technique IDs (T####)
        import re
        technique_pattern = r'T\d{4}(?:\.\d{3})?'
        techniques = re.findall(technique_pattern, pulse.get('description', '') + ' ' + ' '.join(pulse.get('tags', [])))
        
        if techniques:
            ttp_info['techniques'] = list(set(techniques))
            ttp_info['name'] = f"Techniques: {', '.join(techniques)}"
            ttp_info['description'] = f"MITRE ATT&CK techniques extracted from OTX pulse: {pulse.get('name', 'Unknown')}"
            
            # Basic mapping of common technique phases
            kill_chain_mapping = {
                'T1193': [{'kill_chain_name': 'mitre-attack', 'phase_name': 'initial-access'}],
                'T1105': [{'kill_chain_name': 'mitre-attack', 'phase_name': 'command-and-control'}],
                'T1064': [{'kill_chain_name': 'mitre-attack', 'phase_name': 'execution'}],
            }
            
            for technique in techniques:
                if technique in kill_chain_mapping:
                    ttp_info['kill_chain_phases'].extend(kill_chain_mapping[technique])
            
            return ttp_info
        
        # Check for common tactic keywords in tags
        tactic_keywords = {
            'phishing': 'initial-access',
            'malware': 'execution',
            'backdoor': 'persistence',
            'lateral': 'lateral-movement',
            'exfiltration': 'exfiltration',
            'c2': 'command-and-control',
            'command-control': 'command-and-control'
        }
        
        found_tactics = []
        for tag in tags:
            for keyword, tactic in tactic_keywords.items():
                if keyword in tag:
                    found_tactics.append(tactic)
                    ttp_info['kill_chain_phases'].append({
                        'kill_chain_name': 'mitre-attack',
                        'phase_name': tactic
                    })
        
        if found_tactics:
            ttp_info['name'] = f"Tactics: {', '.join(set(found_tactics))}"
            ttp_info['description'] = f"Tactics extracted from OTX pulse tags: {pulse.get('name', 'Unknown')}"
            ttp_info['tactics'] = list(set(found_tactics))
            return ttp_info
        
        return None
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse datetime string from OTX format.
        
        Args:
            date_str: Date string
            
        Returns:
            Parsed datetime or None
        """
        if not date_str:
            return None
        
        try:
            # Handle various OTX datetime formats
            if date_str.endswith('Z'):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif '+' in date_str or date_str.endswith('UTC'):
                return datetime.fromisoformat(date_str.replace('UTC', '').strip())
            else:
                return datetime.fromisoformat(date_str)
        except Exception as e:
            logger.warning(f"Could not parse datetime '{date_str}': {e}")
            return None
    
    def process_otx_pulses(self, pulses: List[Dict[str, Any]], user: Optional[User] = None) -> Dict[str, Any]:
        """
        Process multiple OTX pulses and store as domain model objects.
        
        Args:
            pulses: List of OTX pulse data
            user: User creating the objects (optional)
            
        Returns:
            Processing results summary
        """
        results = {
            'total_pulses': len(pulses),
            'processed_pulses': 0,
            'created_indicators': 0,
            'created_ttps': 0,
            'errors': []
        }
        
        for pulse in pulses:
            try:
                with transaction.atomic():
                    # Convert pulse to domain objects
                    indicators, ttp_data_list = self.convert_otx_pulse_to_domain_objects(pulse)
                    
                    # Store indicators
                    for indicator in indicators:
                        if user:
                            indicator.created_by = user
                        indicator.save()
                        results['created_indicators'] += 1
                    
                    # Store TTP data
                    for ttp_data in ttp_data_list:
                        if user:
                            ttp_data.created_by = user
                        ttp_data.save()
                        results['created_ttps'] += 1
                    
                    results['processed_pulses'] += 1
                    self.stats['pulses_processed'] += 1
                    
            except Exception as e:
                error_msg = f"Error processing pulse '{pulse.get('name', 'Unknown')}': {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                self.stats['errors'].append(error_msg)
        
        # Update overall stats
        self.stats['indicators_created'] += results['created_indicators']
        self.stats['ttps_created'] += results['created_ttps']
        
        logger.info(f"OTX processing complete. Processed {results['processed_pulses']}/{results['total_pulses']} pulses, "
                   f"created {results['created_indicators']} indicators and {results['created_ttps']} TTPs")
        
        return results
    
    def fetch_and_process_recent_pulses(self, days_back: int = 1, user: Optional[User] = None) -> Dict[str, Any]:
        """
        Fetch recent pulses from OTX and process them.
        
        Args:
            days_back: Number of days back to fetch pulses
            user: User creating the objects (optional)
            
        Returns:
            Processing results summary
        """
        try:
            # Calculate date threshold
            since_date = timezone.now() - timedelta(days=days_back)
            
            # Fetch pulses from OTX
            logger.info(f"Fetching OTX pulses modified since {since_date}")
            pulses = self.client.get_pulses(modified_since=since_date)
            
            # Process the pulses
            results = self.process_otx_pulses(pulses, user)
            
            return results
            
        except OTXAPIError as e:
            logger.error(f"OTX API error: {e}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error processing OTX feeds: {e}")
            return {'error': str(e)}
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset processing statistics."""
        self.stats = {
            'pulses_processed': 0,
            'indicators_created': 0,
            'ttps_created': 0,
            'errors': []
        }
    
    def validate_otx_data(self, pulse: Dict[str, Any]) -> List[str]:
        """
        Validate OTX pulse data before processing.
        
        Args:
            pulse: OTX pulse data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not pulse.get('name'):
            errors.append("Pulse missing required 'name' field")
        
        if not pulse.get('id'):
            errors.append("Pulse missing required 'id' field")
        
        # Check indicators
        indicators = pulse.get('indicators', [])
        if not indicators:
            errors.append("Pulse has no indicators")
        else:
            for i, indicator in enumerate(indicators):
                if not indicator.get('indicator'):
                    errors.append(f"Indicator {i} missing value")
                if not indicator.get('type'):
                    errors.append(f"Indicator {i} missing type")
                elif not self.client.validate_indicator_type(indicator['type']):
                    errors.append(f"Indicator {i} has unsupported type: {indicator['type']}")
        
        return errors