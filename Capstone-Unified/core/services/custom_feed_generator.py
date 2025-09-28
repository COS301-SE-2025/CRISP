"""
Custom Feed Generator Service
Converts custom threat feed configurations into STIX 2.1 objects
that can be consumed by the CRISP platform exactly like external feeds.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

class CustomSTIXGenerator:
    """
    Generates comprehensive STIX 2.1 objects from custom threat feed configurations.
    Creates realistic threat intelligence that matches the structure of external feeds.
    """

    def __init__(self):
        self.spec_version = "2.1"
        self.object_id_counter = 0

    def generate_feed_stix_bundle(self, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete STIX bundle for a custom threat feed.
        Returns a STIX bundle containing all indicators and associated objects.
        """
        bundle_objects = []

        # Create identity object for the feed
        identity = self._create_identity_object(feed_config)
        bundle_objects.append(identity)

        # Create malware objects for each family
        malware_objects = self._create_malware_objects(feed_config)
        bundle_objects.extend(malware_objects)

        # Create threat actor objects
        threat_actors = self._create_threat_actor_objects(feed_config)
        bundle_objects.extend(threat_actors)

        # Create attack pattern objects from TTPs
        attack_patterns = self._create_attack_pattern_objects(feed_config.get('ttps', []))
        bundle_objects.extend(attack_patterns)

        # Create indicator objects
        indicators = self._create_indicator_objects(
            feed_config.get('indicators', []),
            identity['id']
        )
        bundle_objects.extend(indicators)

        # Create relationships between objects
        relationships = self._create_relationship_objects(
            bundle_objects,
            feed_config
        )
        bundle_objects.extend(relationships)

        # Create the bundle
        bundle = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "spec_version": self.spec_version,
            "objects": bundle_objects
        }

        return bundle

    def _create_identity_object(self, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create STIX identity object for the feed source"""
        return {
            "type": "identity",
            "spec_version": self.spec_version,
            "id": f"identity--{uuid.uuid4()}",
            "created": datetime.now().isoformat() + "Z",
            "modified": datetime.now().isoformat() + "Z",
            "name": feed_config['name'],
            "description": feed_config['description'],
            "identity_class": "organization",
            "sectors": ["technology", "cybersecurity"],
            "labels": ["threat-intelligence-provider"],
            "x_crisp_feed_type": feed_config.get('feed_type', 'general'),
            "x_crisp_collection_id": feed_config['taxii_collection_id'],
            "x_crisp_sync_interval": feed_config.get('sync_interval_hours', 24)
        }

    def _create_malware_objects(self, feed_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create STIX malware objects based on feed indicators"""
        malware_objects = []
        malware_families = set()

        # Extract unique malware families from indicators
        for indicator in feed_config.get('indicators', []):
            if 'malware_family' in indicator:
                malware_families.add(indicator['malware_family'])

        for family_name in malware_families:
            malware_obj = {
                "type": "malware",
                "spec_version": self.spec_version,
                "id": f"malware--{uuid.uuid4()}",
                "created": datetime.now().isoformat() + "Z",
                "modified": datetime.now().isoformat() + "Z",
                "name": family_name,
                "description": f"{family_name} malware family commonly used in {feed_config.get('feed_type', 'cybercrime')} operations",
                "malware_types": self._get_malware_types(family_name, feed_config),
                "is_family": True,
                "labels": [feed_config.get('feed_type', 'malware')],
                "x_crisp_first_seen": (datetime.now() - timedelta(days=90)).isoformat() + "Z",
                "x_crisp_threat_level": self._get_threat_level(family_name),
                "x_crisp_prevalence": "high" if family_name.lower() in ['emotet', 'trickbot', 'ryuk'] else "medium"
            }

            # Add architecture and platform info
            if feed_config.get('feed_type') == 'malware_analysis':
                malware_obj.update({
                    "architecture_execution_envs": ["x86", "x86-64"],
                    "implementation_languages": ["c", "c++", "assembly"],
                    "capabilities": self._get_malware_capabilities(family_name)
                })

            malware_objects.append(malware_obj)

        return malware_objects

    def _create_threat_actor_objects(self, feed_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create STIX threat actor objects"""
        threat_actors = []
        actor_names = set()

        # Extract threat actors from indicators
        for indicator in feed_config.get('indicators', []):
            if 'threat_actor' in indicator:
                actor_names.add(indicator['threat_actor'])

        for actor_name in actor_names:
            actor_obj = {
                "type": "threat-actor",
                "spec_version": self.spec_version,
                "id": f"threat-actor--{uuid.uuid4()}",
                "created": datetime.now().isoformat() + "Z",
                "modified": datetime.now().isoformat() + "Z",
                "name": actor_name,
                "description": f"{actor_name} threat actor associated with {feed_config.get('feed_type', 'cybercrime')} activities",
                "threat_actor_types": self._get_threat_actor_types(feed_config),
                "aliases": [actor_name],
                "labels": [feed_config.get('feed_type', 'cybercriminal')],
                "sophistication": self._get_sophistication_level(feed_config),
                "resource_level": self._get_resource_level(feed_config),
                "primary_motivation": self._get_primary_motivation(feed_config),
                "x_crisp_confidence": 85,
                "x_crisp_activity_level": "high"
            }

            # Add geographic info for certain feed types
            if feed_config.get('feed_type') in ['apt_intelligence', 'industrial_espionage']:
                actor_obj.update({
                    "x_crisp_suspected_origin": self._get_suspected_origin(actor_name),
                    "x_crisp_target_sectors": self._get_target_sectors(feed_config)
                })

            threat_actors.append(actor_obj)

        return threat_actors

    def _create_attack_pattern_objects(self, ttps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create STIX attack pattern objects from TTPs"""
        attack_patterns = []

        for ttp in ttps:
            attack_pattern = {
                "type": "attack-pattern",
                "spec_version": self.spec_version,
                "id": f"attack-pattern--{uuid.uuid4()}",
                "created": datetime.now().isoformat() + "Z",
                "modified": datetime.now().isoformat() + "Z",
                "name": ttp['name'],
                "description": ttp['description'],
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": ttp['mitre_technique_id'],
                        "url": f"https://attack.mitre.org/techniques/{ttp['mitre_technique_id'].replace('.', '/')}"
                    }
                ],
                "kill_chain_phases": [
                    {
                        "kill_chain_name": "mitre-attack",
                        "phase_name": ttp['tactic']
                    }
                ],
                "x_mitre_detection": ttp.get('detection_rules', []),
                "x_mitre_defense_bypassed": self._get_defense_bypassed(ttp['tactic']),
                "x_mitre_platforms": self._get_platforms(ttp['mitre_technique_id']),
                "x_crisp_mitigations": ttp.get('mitigations', [])
            }
            attack_patterns.append(attack_pattern)

        return attack_patterns

    def _create_indicator_objects(self, indicators: List[Dict[str, Any]], created_by_ref: str) -> List[Dict[str, Any]]:
        """Create STIX indicator objects"""
        stix_indicators = []

        for indicator_data in indicators:
            # Create the pattern based on indicator type
            pattern = self._create_indicator_pattern(indicator_data)

            indicator = {
                "type": "indicator",
                "spec_version": self.spec_version,
                "id": f"indicator--{uuid.uuid4()}",
                "created": datetime.now().isoformat() + "Z",
                "modified": datetime.now().isoformat() + "Z",
                "created_by_ref": created_by_ref,
                "pattern": pattern,
                "pattern_type": "stix",
                "pattern_version": "2.1",
                "valid_from": indicator_data.get('first_seen', datetime.now().isoformat() + "Z"),
                "valid_until": self._calculate_valid_until(indicator_data),
                "labels": indicator_data.get('labels', ['malicious-activity']),
                "confidence": indicator_data.get('confidence', 75),
                "x_crisp_first_seen": indicator_data.get('first_seen'),
                "x_crisp_last_seen": indicator_data.get('last_seen'),
                "x_crisp_kill_chain_phases": indicator_data.get('kill_chain_phases', []),
                "x_crisp_threat_actor": indicator_data.get('threat_actor'),
                "x_crisp_malware_family": indicator_data.get('malware_family'),
                "x_crisp_campaign": indicator_data.get('campaign'),
                "x_crisp_metadata": indicator_data.get('metadata', {})
            }

            # Add type-specific extensions
            if indicator_data['type'] == 'file':
                indicator.update({
                    "x_crisp_file_size": indicator_data.get('metadata', {}).get('file_size'),
                    "x_crisp_file_type": indicator_data.get('metadata', {}).get('file_type'),
                    "x_crisp_packer": indicator_data.get('metadata', {}).get('packer')
                })
            elif indicator_data['type'] in ['domain-name', 'ipv4-addr']:
                indicator.update({
                    "x_crisp_geolocation": indicator_data.get('metadata', {}).get('geolocation'),
                    "x_crisp_hosting_provider": indicator_data.get('metadata', {}).get('hosting_provider')
                })

            stix_indicators.append(indicator)

        return stix_indicators

    def _create_relationship_objects(self, bundle_objects: List[Dict[str, Any]], feed_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create STIX relationship objects between bundle objects"""
        relationships = []

        # Get objects by type
        indicators = [obj for obj in bundle_objects if obj['type'] == 'indicator']
        malware_objects = [obj for obj in bundle_objects if obj['type'] == 'malware']
        threat_actors = [obj for obj in bundle_objects if obj['type'] == 'threat-actor']
        attack_patterns = [obj for obj in bundle_objects if obj['type'] == 'attack-pattern']
        identity = next((obj for obj in bundle_objects if obj['type'] == 'identity'), None)

        # Create relationships between indicators and malware
        for indicator in indicators:
            malware_family = indicator.get('x_crisp_malware_family')
            if malware_family:
                matching_malware = next((m for m in malware_objects if m['name'] == malware_family), None)
                if matching_malware:
                    rel = {
                        "type": "relationship",
                        "spec_version": self.spec_version,
                        "id": f"relationship--{uuid.uuid4()}",
                        "created": datetime.now().isoformat() + "Z",
                        "modified": datetime.now().isoformat() + "Z",
                        "relationship_type": "indicates",
                        "source_ref": indicator['id'],
                        "target_ref": matching_malware['id'],
                        "x_crisp_confidence": 90
                    }
                    relationships.append(rel)

        # Create relationships between threat actors and malware
        for threat_actor in threat_actors:
            actor_name = threat_actor['name']
            for malware_obj in malware_objects:
                # Create probabilistic relationships
                if feed_config.get('feed_type') == 'apt_intelligence':
                    rel = {
                        "type": "relationship",
                        "spec_version": self.spec_version,
                        "id": f"relationship--{uuid.uuid4()}",
                        "created": datetime.now().isoformat() + "Z",
                        "modified": datetime.now().isoformat() + "Z",
                        "relationship_type": "uses",
                        "source_ref": threat_actor['id'],
                        "target_ref": malware_obj['id'],
                        "x_crisp_confidence": 80
                    }
                    relationships.append(rel)

        # Create relationships between malware and attack patterns
        for malware_obj in malware_objects:
            for attack_pattern in attack_patterns:
                rel = {
                    "type": "relationship",
                    "spec_version": self.spec_version,
                    "id": f"relationship--{uuid.uuid4()}",
                    "created": datetime.now().isoformat() + "Z",
                    "modified": datetime.now().isoformat() + "Z",
                    "relationship_type": "uses",
                    "source_ref": malware_obj['id'],
                    "target_ref": attack_pattern['id'],
                    "x_crisp_confidence": 85
                }
                relationships.append(rel)

        return relationships

    def _create_indicator_pattern(self, indicator_data: Dict[str, Any]) -> str:
        """Create STIX pattern from indicator data"""
        if indicator_data['type'] == 'domain-name':
            return f"[domain-name:value = '{indicator_data['value']}']"
        elif indicator_data['type'] == 'ipv4-addr':
            return f"[ipv4-addr:value = '{indicator_data['value']}']"
        elif indicator_data['type'] == 'file':
            hash_val = list(indicator_data['hashes'].values())[0]
            hash_type = list(indicator_data['hashes'].keys())[0].lower().replace('-', '')
            return f"[file:hashes.{hash_type} = '{hash_val}']"
        elif indicator_data['type'] == 'email-addr':
            return f"[email-addr:value = '{indicator_data['value']}']"
        else:
            return f"[{indicator_data['type']}:value = '{indicator_data['value']}']"

    def _calculate_valid_until(self, indicator_data: Dict[str, Any]) -> str:
        """Calculate indicator expiration based on type and confidence"""
        base_date = datetime.fromisoformat(indicator_data.get('first_seen', datetime.now().isoformat()).replace('Z', ''))
        confidence = indicator_data.get('confidence', 75)

        # Higher confidence indicators are valid longer
        if confidence >= 90:
            days_valid = 365
        elif confidence >= 80:
            days_valid = 180
        elif confidence >= 70:
            days_valid = 90
        else:
            days_valid = 30

        return (base_date + timedelta(days=days_valid)).isoformat() + "Z"

    def _get_malware_types(self, family_name: str, feed_config: Dict[str, Any]) -> List[str]:
        """Determine malware types based on family and feed type"""
        malware_type_mapping = {
            'ransomware': ['ransomware', 'trojan'],
            'banking_trojan': ['banking-trojan', 'trojan', 'spyware'],
            'apt': ['backdoor', 'trojan', 'remote-access-trojan'],
            'industrial': ['backdoor', 'rootkit', 'trojan']
        }

        feed_type = feed_config.get('feed_type', 'general')
        if 'ransomware' in family_name.lower() or feed_type == 'cybercrime':
            return malware_type_mapping['ransomware']
        elif any(term in family_name.lower() for term in ['zeus', 'dridex', 'emotet', 'trickbot']):
            return malware_type_mapping['banking_trojan']
        elif feed_type == 'apt_intelligence':
            return malware_type_mapping['apt']
        elif feed_type == 'industrial_espionage':
            return malware_type_mapping['industrial']
        else:
            return ['trojan', 'malware']

    def _get_malware_capabilities(self, family_name: str) -> List[str]:
        """Get malware capabilities based on family"""
        capabilities_map = {
            'emotet': ['spying-on-users', 'downloading-additional-malware', 'credential-theft'],
            'trickbot': ['banking-credential-theft', 'lateral-movement', 'data-exfiltration'],
            'cobalt strike': ['command-and-control', 'post-exploitation', 'lateral-movement'],
            'meterpreter': ['remote-machine-access', 'file-system-access', 'screen-capture']
        }
        return capabilities_map.get(family_name.lower(), ['unknown'])

    def _get_threat_actor_types(self, feed_config: Dict[str, Any]) -> List[str]:
        """Determine threat actor types based on feed type"""
        type_mapping = {
            'apt_intelligence': ['nation-state'],
            'cybercrime': ['cybercriminal'],
            'malware_analysis': ['cybercriminal'],
            'industrial_espionage': ['nation-state', 'cybercriminal']
        }
        return type_mapping.get(feed_config.get('feed_type', 'general'), ['unknown'])

    def _get_sophistication_level(self, feed_config: Dict[str, Any]) -> str:
        """Get sophistication level based on feed type"""
        sophistication_map = {
            'apt_intelligence': 'expert',
            'industrial_espionage': 'expert',
            'cybercrime': 'intermediate',
            'malware_analysis': 'intermediate'
        }
        return sophistication_map.get(feed_config.get('feed_type', 'general'), 'intermediate')

    def _get_resource_level(self, feed_config: Dict[str, Any]) -> str:
        """Get resource level based on feed type"""
        resource_map = {
            'apt_intelligence': 'government',
            'industrial_espionage': 'organization',
            'cybercrime': 'organization',
            'malware_analysis': 'individual'
        }
        return resource_map.get(feed_config.get('feed_type', 'general'), 'organization')

    def _get_primary_motivation(self, feed_config: Dict[str, Any]) -> str:
        """Get primary motivation based on feed type"""
        motivation_map = {
            'apt_intelligence': 'organizational-gain',
            'industrial_espionage': 'organizational-gain',
            'cybercrime': 'personal-gain',
            'malware_analysis': 'personal-gain'
        }
        return motivation_map.get(feed_config.get('feed_type', 'general'), 'personal-gain')

    def _get_suspected_origin(self, actor_name: str) -> str:
        """Get suspected origin based on actor name patterns"""
        if 'APT' in actor_name:
            apt_origins = {'APT1': 'CN', 'APT28': 'RU', 'APT29': 'RU', 'APT34': 'IR', 'APT40': 'CN'}
            return apt_origins.get(actor_name, 'Unknown')
        return 'Unknown'

    def _get_target_sectors(self, feed_config: Dict[str, Any]) -> List[str]:
        """Get target sectors based on feed type"""
        sector_map = {
            'apt_intelligence': ['government', 'technology', 'telecommunications'],
            'industrial_espionage': ['manufacturing', 'energy', 'transportation'],
            'cybercrime': ['financial-services', 'retail', 'healthcare'],
            'malware_analysis': ['multiple']
        }
        return sector_map.get(feed_config.get('feed_type', 'general'), ['multiple'])

    def _get_threat_level(self, family_name: str) -> str:
        """Get threat level based on malware family"""
        high_threat = ['emotet', 'trickbot', 'ryuk', 'maze', 'revil', 'cobalt strike']
        if family_name.lower() in high_threat:
            return 'high'
        return 'medium'

    def _get_defense_bypassed(self, tactic: str) -> List[str]:
        """Get defense bypass methods based on tactic"""
        bypass_map = {
            'defense-evasion': ['anti-virus', 'signature-based-detection'],
            'initial-access': ['email-security-gateway', 'user-training'],
            'persistence': ['system-monitoring', 'file-integrity-monitoring'],
            'privilege-escalation': ['user-account-control', 'privilege-monitoring']
        }
        return bypass_map.get(tactic, [])

    def _get_platforms(self, technique_id: str) -> List[str]:
        """Get platforms based on MITRE technique"""
        # Most techniques are Windows-focused in our demo
        if 'T0' in technique_id:  # ICS techniques
            return ['human-machine-interface', 'control-server', 'engineering-workstation']
        else:
            return ['windows', 'linux', 'macos']

    def generate_all_custom_feeds_stix(self) -> Dict[str, Dict[str, Any]]:
        """Generate STIX bundles for all custom feeds"""
        from core.config.custom_threat_feeds import CUSTOM_FEEDS_CONFIG

        stix_bundles = {}
        for feed_config in CUSTOM_FEEDS_CONFIG:
            bundle = self.generate_feed_stix_bundle(feed_config)
            stix_bundles[feed_config['name']] = bundle

        return stix_bundles