"""
TTP Extraction Service - Extracts TTPs from threat intelligence data
"""
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from django.db import transaction
from django.utils import timezone

from core.models.models import ThreatFeed, TTPData, Indicator, SystemActivity

logger = logging.getLogger(__name__)


class TTPExtractionService:
    """Service for extracting TTPs from threat intelligence data"""

    def __init__(self):
        # MITRE ATT&CK technique patterns
        self.mitre_patterns = {
            # Common technique IDs
            'technique_id': r'T\d{4}(?:\.\d{3})?',

            # Common technique names and their IDs
            'techniques': {
                'spearphishing': 'T1566.001',
                'credential dumping': 'T1003',
                'lsass': 'T1003.001',
                'powershell': 'T1059.001',
                'cmd': 'T1059.003',
                'registry': 'T1112',
                'persistence': 'T1547',
                'lateral movement': 'T1021',
                'remote desktop': 'T1021.001',
                'file transfer': 'T1105',
                'data exfiltration': 'T1041',
                'ransomware': 'T1486',
                'encryption': 'T1486',
                'keylogging': 'T1056.001',
                'screen capture': 'T1113',
                'process injection': 'T1055',
                'dll injection': 'T1055.001',
                'scheduled task': 'T1053.005',
                'service creation': 'T1543.003',
                'web shell': 'T1505.003',
                'backdoor': 'T1546',
                'privilege escalation': 'T1068',
                'token impersonation': 'T1134',
                'network sniffing': 'T1040',
                'domain trust discovery': 'T1482',
                'system information discovery': 'T1082',
                'file and directory discovery': 'T1083',
                'network service scanning': 'T1046',
                'remote system discovery': 'T1018',
                'account discovery': 'T1087'
            },

            # Tactic mappings
            'tactics': {
                'T1566': 'initial_access',
                'T1003': 'credential_access',
                'T1059': 'execution',
                'T1112': 'defense_evasion',
                'T1547': 'persistence',
                'T1021': 'lateral_movement',
                'T1105': 'command_and_control',
                'T1041': 'exfiltration',
                'T1486': 'impact',
                'T1056': 'collection',
                'T1113': 'collection',
                'T1055': 'defense_evasion',
                'T1053': 'persistence',
                'T1543': 'persistence',
                'T1505': 'persistence',
                'T1546': 'persistence',
                'T1068': 'privilege_escalation',
                'T1134': 'privilege_escalation',
                'T1040': 'credential_access',
                'T1482': 'discovery',
                'T1082': 'discovery',
                'T1083': 'discovery',
                'T1046': 'discovery',
                'T1018': 'discovery',
                'T1087': 'discovery'
            }
        }

    def extract_ttps_from_feed(self, threat_feed: ThreatFeed, force_reextract: bool = False) -> Dict[str, Any]:
        """
        Extract TTPs from a threat feed by analyzing indicators and descriptions

        Args:
            threat_feed: ThreatFeed to extract TTPs from
            force_reextract: Whether to force re-extraction of existing TTPs

        Returns:
            Dictionary containing extraction results
        """
        results = {
            'feed_id': threat_feed.id,
            'feed_name': threat_feed.name,
            'extraction_timestamp': timezone.now().isoformat(),
            'ttps_extracted': [],
            'ttps_existing': [],
            'indicators_analyzed': 0,
            'success': True,
            'errors': []
        }

        try:
            with transaction.atomic():
                # Get indicators from this feed
                indicators = Indicator.objects.filter(threat_feed=threat_feed)
                results['indicators_analyzed'] = indicators.count()

                if results['indicators_analyzed'] == 0:
                    results['errors'].append('No indicators found in this threat feed')
                    return results

                # Extract TTPs from indicators
                extracted_ttps = []
                for indicator in indicators:
                    indicator_ttps = self._extract_ttps_from_indicator(indicator)
                    extracted_ttps.extend(indicator_ttps)

                # Also extract from feed description if available
                if threat_feed.description:
                    feed_ttps = self._extract_ttps_from_text(threat_feed.description)
                    for ttp_data in feed_ttps:
                        ttp_data['source'] = 'feed_description'
                        ttp_data['source_id'] = threat_feed.id
                    extracted_ttps.extend(feed_ttps)

                # Remove duplicates and create TTP records
                unique_ttps = self._deduplicate_ttps(extracted_ttps)

                for ttp_data in unique_ttps:
                    try:
                        # Check if TTP already exists for this feed
                        existing_ttp = TTPData.objects.filter(
                            threat_feed=threat_feed,
                            mitre_technique_id=ttp_data['mitre_technique_id']
                        ).first()

                        if existing_ttp and not force_reextract:
                            results['ttps_existing'].append({
                                'technique_id': ttp_data['mitre_technique_id'],
                                'name': existing_ttp.name,
                                'reason': 'Already exists'
                            })
                            continue

                        if existing_ttp and force_reextract:
                            # Update existing TTP
                            for key, value in ttp_data.items():
                                if key not in ['source', 'source_id'] and hasattr(existing_ttp, key):
                                    setattr(existing_ttp, key, value)
                            existing_ttp.save()

                            results['ttps_extracted'].append({
                                'technique_id': ttp_data['mitre_technique_id'],
                                'name': ttp_data['name'],
                                'action': 'updated'
                            })
                        else:
                            # Create new TTP
                            new_ttp = TTPData.objects.create(
                                name=ttp_data['name'],
                                description=ttp_data['description'],
                                mitre_technique_id=ttp_data['mitre_technique_id'],
                                mitre_tactic=ttp_data.get('mitre_tactic', 'unknown'),
                                mitre_subtechnique=ttp_data.get('mitre_subtechnique'),
                                threat_feed=threat_feed,
                                stix_id=f"attack-pattern--{ttp_data['mitre_technique_id'].lower()}-{threat_feed.id}"
                            )

                            results['ttps_extracted'].append({
                                'technique_id': ttp_data['mitre_technique_id'],
                                'name': ttp_data['name'],
                                'action': 'created',
                                'id': new_ttp.id
                            })

                    except Exception as e:
                        results['errors'].append(f"Error creating TTP {ttp_data['mitre_technique_id']}: {str(e)}")
                        continue

                # Log the extraction activity
                SystemActivity.objects.create(
                    activity_type='ttp_extraction',
                    category='system',
                    title=f'TTP extraction completed for {threat_feed.name}',
                    description=f'Extracted {len(results["ttps_extracted"])} TTPs from {results["indicators_analyzed"]} indicators',
                    threat_feed=threat_feed,
                    metadata=results
                )

                logger.info(f"TTP extraction completed for feed {threat_feed.name}: {len(results['ttps_extracted'])} TTPs extracted")
                return results

        except Exception as e:
            results['success'] = False
            results['errors'].append(f"Extraction failed: {str(e)}")
            logger.error(f"TTP extraction failed for feed {threat_feed.name}: {str(e)}")
            return results

    def _extract_ttps_from_indicator(self, indicator: Indicator) -> List[Dict[str, Any]]:
        """Extract TTPs from an individual indicator"""
        ttps = []

        # Analyze indicator value
        value_ttps = self._extract_ttps_from_text(indicator.value)
        for ttp in value_ttps:
            ttp['source'] = 'indicator_value'
            ttp['source_id'] = indicator.id
        ttps.extend(value_ttps)

        # Analyze indicator description if available
        if hasattr(indicator, 'description') and indicator.description:
            desc_ttps = self._extract_ttps_from_text(indicator.description)
            for ttp in desc_ttps:
                ttp['source'] = 'indicator_description'
                ttp['source_id'] = indicator.id
            ttps.extend(desc_ttps)

        # Infer TTPs based on indicator type
        type_ttps = self._infer_ttps_from_indicator_type(indicator)
        ttps.extend(type_ttps)

        return ttps

    def _extract_ttps_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract TTPs from text using pattern matching"""
        ttps = []
        text_lower = text.lower()

        # Look for explicit technique IDs
        technique_matches = re.findall(self.mitre_patterns['technique_id'], text, re.IGNORECASE)
        for technique_id in technique_matches:
            technique_id = technique_id.upper()
            ttp_data = self._create_ttp_data_from_technique_id(technique_id)
            if ttp_data:
                ttps.append(ttp_data)

        # Look for technique names
        for technique_name, technique_id in self.mitre_patterns['techniques'].items():
            if technique_name in text_lower:
                ttp_data = self._create_ttp_data_from_technique_name(technique_name, technique_id)
                ttps.append(ttp_data)

        return ttps

    def _infer_ttps_from_indicator_type(self, indicator: Indicator) -> List[Dict[str, Any]]:
        """Infer TTPs based on indicator type and characteristics"""
        ttps = []

        # File hash indicators often indicate malware execution
        if indicator.type in ['md5', 'sha1', 'sha256', 'file_hash']:
            ttps.append({
                'name': 'User Execution: Malicious File',
                'description': f'Execution of malicious file with hash {indicator.type}: {indicator.value}',
                'mitre_technique_id': 'T1204.002',
                'mitre_tactic': 'execution',
                'confidence': 70,
                'source': 'indicator_type_inference',
                'source_id': indicator.id
            })

        # IP addresses can indicate command and control
        elif indicator.type == 'ip':
            ttps.append({
                'name': 'Application Layer Protocol',
                'description': f'Command and control communication to IP address {indicator.value}',
                'mitre_technique_id': 'T1071',
                'mitre_tactic': 'command_and_control',
                'confidence': 60,
                'source': 'indicator_type_inference',
                'source_id': indicator.id
            })

        # Domain indicators can indicate various techniques
        elif indicator.type == 'domain':
            ttps.append({
                'name': 'Domain Fronting',
                'description': f'Potential domain fronting or C2 communication via domain {indicator.value}',
                'mitre_technique_id': 'T1090.004',
                'mitre_tactic': 'command_and_control',
                'confidence': 50,
                'source': 'indicator_type_inference',
                'source_id': indicator.id
            })

        # URL indicators can indicate watering hole or drive-by compromise
        elif indicator.type == 'url':
            ttps.append({
                'name': 'Drive-by Compromise',
                'description': f'Potential drive-by compromise via malicious URL {indicator.value}',
                'mitre_technique_id': 'T1189',
                'mitre_tactic': 'initial_access',
                'confidence': 55,
                'source': 'indicator_type_inference',
                'source_id': indicator.id
            })

        return ttps

    def _create_ttp_data_from_technique_id(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """Create TTP data from a MITRE technique ID"""
        # Get base technique for tactic mapping
        base_technique = technique_id.split('.')[0]
        tactic = self.mitre_patterns['tactics'].get(base_technique, 'unknown')

        return {
            'name': f'MITRE ATT&CK Technique {technique_id}',
            'description': f'Detected MITRE ATT&CK technique {technique_id}',
            'mitre_technique_id': technique_id,
            'mitre_tactic': tactic,
            'confidence': 90,
        }

    def _create_ttp_data_from_technique_name(self, technique_name: str, technique_id: str) -> Dict[str, Any]:
        """Create TTP data from a technique name"""
        base_technique = technique_id.split('.')[0]
        tactic = self.mitre_patterns['tactics'].get(base_technique, 'unknown')

        return {
            'name': technique_name.title(),
            'description': f'Detected technique: {technique_name}',
            'mitre_technique_id': technique_id,
            'mitre_tactic': tactic,
            'confidence': 80,
        }

    def _deduplicate_ttps(self, ttps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate TTPs based on technique ID"""
        seen_techniques = set()
        unique_ttps = []

        for ttp in ttps:
            technique_id = ttp.get('mitre_technique_id')
            if technique_id and technique_id not in seen_techniques:
                seen_techniques.add(technique_id)
                unique_ttps.append(ttp)

        return unique_ttps

    def extract_ttps_from_all_feeds(self, active_only: bool = True) -> Dict[str, Any]:
        """
        Extract TTPs from all threat feeds

        Args:
            active_only: Whether to only process active feeds

        Returns:
            Summary of extraction results
        """
        results = {
            'total_feeds_processed': 0,
            'total_ttps_extracted': 0,
            'feeds_with_new_ttps': 0,
            'feeds_with_errors': 0,
            'extraction_timestamp': timezone.now().isoformat(),
            'feed_results': []
        }

        # Get feeds to process
        feeds = ThreatFeed.objects.all()
        if active_only:
            feeds = feeds.filter(is_active=True)

        for feed in feeds:
            logger.info(f"Processing feed: {feed.name}")
            feed_result = self.extract_ttps_from_feed(feed)

            results['feed_results'].append(feed_result)
            results['total_feeds_processed'] += 1

            if feed_result['success']:
                ttps_count = len(feed_result['ttps_extracted'])
                results['total_ttps_extracted'] += ttps_count
                if ttps_count > 0:
                    results['feeds_with_new_ttps'] += 1
            else:
                results['feeds_with_errors'] += 1

        # Log overall activity
        SystemActivity.objects.create(
            activity_type='bulk_ttp_extraction',
            category='system',
            title='Bulk TTP extraction completed',
            description=f'Processed {results["total_feeds_processed"]} feeds, extracted {results["total_ttps_extracted"]} TTPs',
            metadata=results
        )

        return results

    def get_extraction_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations for TTP extraction based on current data

        Returns:
            Dictionary containing recommendations
        """
        recommendations = {
            'feeds_without_ttps': [],
            'feeds_with_low_ttp_coverage': [],
            'techniques_missing': [],
            'tactics_coverage': {},
            'recommendations': []
        }

        try:
            from django.db.models import Count

            # Find feeds without TTPs
            feeds_without_ttps = ThreatFeed.objects.annotate(
                ttp_count=Count('ttps')
            ).filter(ttp_count=0, is_active=True)

            for feed in feeds_without_ttps:
                indicator_count = Indicator.objects.filter(threat_feed=feed).count()
                recommendations['feeds_without_ttps'].append({
                    'id': feed.id,
                    'name': feed.name,
                    'indicator_count': indicator_count,
                    'potential_ttps': min(indicator_count // 10, 5)  # Estimate
                })

            # Find feeds with low TTP coverage
            feeds_with_low_coverage = ThreatFeed.objects.annotate(
                ttp_count=Count('ttps'),
                indicator_count=Count('indicators')
            ).filter(
                ttp_count__gt=0,
                ttp_count__lt=5,
                indicator_count__gt=10,
                is_active=True
            )

            for feed in feeds_with_low_coverage:
                recommendations['feeds_with_low_ttp_coverage'].append({
                    'id': feed.id,
                    'name': feed.name,
                    'ttp_count': feed.ttp_count,
                    'indicator_count': feed.indicator_count,
                    'coverage_ratio': feed.ttp_count / max(feed.indicator_count, 1)
                })

            # Generate recommendations
            if recommendations['feeds_without_ttps']:
                recommendations['recommendations'].append({
                    'type': 'extraction',
                    'priority': 'high',
                    'message': f"Consider running TTP extraction on {len(recommendations['feeds_without_ttps'])} feeds without TTPs"
                })

            if recommendations['feeds_with_low_ttp_coverage']:
                recommendations['recommendations'].append({
                    'type': 'enhancement',
                    'priority': 'medium',
                    'message': f"{len(recommendations['feeds_with_low_ttp_coverage'])} feeds have low TTP coverage and could benefit from enhanced extraction"
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating extraction recommendations: {str(e)}")
            recommendations['error'] = str(e)
            return recommendations