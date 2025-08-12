"""
MITRE ATT&CK Mapping Service

This service provides functionality to automatically map internal TTPs to MITRE ATT&CK framework
techniques and tactics using text analysis and similarity matching.
"""

import logging
import json
import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from django.conf import settings
import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)


class MITREFrameworkData:
    """
    Service to manage MITRE ATT&CK framework data
    """
    
    # MITRE ATT&CK Enterprise Matrix URL
    MITRE_ENTERPRISE_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    CACHE_KEY = "mitre_attack_data"
    CACHE_TIMEOUT = 86400  # 24 hours
    
    def __init__(self):
        self.techniques = {}
        self.tactics = {}
        self.load_framework_data()
    
    def load_framework_data(self):
        """Load MITRE ATT&CK framework data from cache or external source"""
        try:
            # Try to load from cache first
            cached_data = cache.get(self.CACHE_KEY)
            if cached_data:
                self.techniques = cached_data.get('techniques', {})
                self.tactics = cached_data.get('tactics', {})
                logger.info("Loaded MITRE ATT&CK data from cache")
                return
            
            # If not in cache, fetch from external source
            self._fetch_and_parse_data()
            
        except Exception as e:
            logger.error(f"Failed to load MITRE data, using fallback: {e}")
            self._load_fallback_data()
    
    def _fetch_and_parse_data(self):
        """Fetch and parse MITRE ATT&CK data from external source"""
        try:
            response = requests.get(self.MITRE_ENTERPRISE_URL, timeout=30)
            response.raise_for_status()
            
            mitre_data = response.json()
            self._parse_mitre_data(mitre_data)
            
            # Cache the parsed data
            cache_data = {
                'techniques': self.techniques,
                'tactics': self.tactics
            }
            cache.set(self.CACHE_KEY, cache_data, self.CACHE_TIMEOUT)
            logger.info("Successfully loaded and cached MITRE ATT&CK data")
            
        except Exception as e:
            logger.error(f"Failed to fetch MITRE data: {e}")
            self._load_fallback_data()
    
    def _parse_mitre_data(self, mitre_data):
        """Parse MITRE ATT&CK JSON data"""
        objects = mitre_data.get('objects', [])
        
        # Parse tactics
        for obj in objects:
            if obj.get('type') == 'x-mitre-tactic':
                tactic_id = obj.get('x_mitre_shortname', '')
                if tactic_id:
                    self.tactics[tactic_id] = {
                        'name': obj.get('name', ''),
                        'description': obj.get('description', ''),
                        'id': obj.get('id', ''),
                        'shortname': tactic_id
                    }
        
        # Parse techniques
        for obj in objects:
            if obj.get('type') == 'attack-pattern':
                technique_id = None
                
                # Extract technique ID from external references
                external_refs = obj.get('external_references', [])
                for ref in external_refs:
                    if ref.get('source_name') == 'mitre-attack':
                        technique_id = ref.get('external_id')
                        break
                
                if technique_id:
                    # Extract kill chain phases (tactics)
                    kill_chain_phases = []
                    for phase in obj.get('kill_chain_phases', []):
                        if phase.get('kill_chain_name') == 'mitre-attack':
                            kill_chain_phases.append(phase.get('phase_name'))
                    
                    self.techniques[technique_id] = {
                        'name': obj.get('name', ''),
                        'description': obj.get('description', ''),
                        'id': obj.get('id', ''),
                        'technique_id': technique_id,
                        'tactics': kill_chain_phases,
                        'kill_chain_phases': kill_chain_phases,
                        'revoked': obj.get('revoked', False),
                        'deprecated': obj.get('x_mitre_deprecated', False)
                    }
    
    def _load_fallback_data(self):
        """Load fallback MITRE data when external source is unavailable"""
        # Basic fallback tactics
        fallback_tactics = {
            'reconnaissance': {'name': 'Reconnaissance', 'description': 'The adversary is trying to gather information they can use to plan future operations.'},
            'resource-development': {'name': 'Resource Development', 'description': 'The adversary is trying to establish resources they can use to support operations.'},
            'initial-access': {'name': 'Initial Access', 'description': 'The adversary is trying to get into your network.'},
            'execution': {'name': 'Execution', 'description': 'The adversary is trying to run malicious code.'},
            'persistence': {'name': 'Persistence', 'description': 'The adversary is trying to maintain their foothold.'},
            'privilege-escalation': {'name': 'Privilege Escalation', 'description': 'The adversary is trying to gain higher-level permissions.'},
            'defense-evasion': {'name': 'Defense Evasion', 'description': 'The adversary is trying to avoid being detected.'},
            'credential-access': {'name': 'Credential Access', 'description': 'The adversary is trying to steal account names and passwords.'},
            'discovery': {'name': 'Discovery', 'description': 'The adversary is trying to figure out your environment.'},
            'lateral-movement': {'name': 'Lateral Movement', 'description': 'The adversary is trying to move through your environment.'},
            'collection': {'name': 'Collection', 'description': 'The adversary is trying to gather data of interest to their goal.'},
            'command-and-control': {'name': 'Command and Control', 'description': 'The adversary is trying to communicate with compromised systems.'},
            'exfiltration': {'name': 'Exfiltration', 'description': 'The adversary is trying to steal data.'},
            'impact': {'name': 'Impact', 'description': 'The adversary is trying to manipulate, interrupt, or destroy your systems and data.'}
        }
        
        # Basic fallback techniques
        fallback_techniques = {
            'T1566': {'name': 'Phishing', 'description': 'Adversaries may send phishing messages to gain access to victim systems.', 'tactics': ['initial-access']},
            'T1059': {'name': 'Command and Scripting Interpreter', 'description': 'Adversaries may abuse command and script interpreters to execute commands.', 'tactics': ['execution']},
            'T1055': {'name': 'Process Injection', 'description': 'Adversaries may inject code into processes in order to evade process-based defenses.', 'tactics': ['defense-evasion', 'privilege-escalation']},
            'T1082': {'name': 'System Information Discovery', 'description': 'An adversary may attempt to get detailed information about the operating system.', 'tactics': ['discovery']},
            'T1041': {'name': 'Exfiltration Over C2 Channel', 'description': 'Adversaries may steal data by exfiltrating it over an existing command and control channel.', 'tactics': ['exfiltration']}
        }
        
        self.tactics = fallback_tactics
        self.techniques = fallback_techniques
        logger.warning("Using fallback MITRE ATT&CK data")
    
    def get_technique(self, technique_id: str) -> Optional[Dict]:
        """Get technique by ID"""
        return self.techniques.get(technique_id)
    
    def get_tactic(self, tactic_id: str) -> Optional[Dict]:
        """Get tactic by ID"""
        return self.tactics.get(tactic_id)
    
    def search_techniques(self, query: str, limit: int = 10) -> List[Dict]:
        """Search techniques by name or description"""
        query = query.lower()
        results = []
        
        for tech_id, tech_data in self.techniques.items():
            score = 0
            name = tech_data.get('name', '').lower()
            description = tech_data.get('description', '').lower()
            
            # Exact name match gets highest score
            if query == name:
                score = 100
            elif query in name:
                score = 80
            elif query in description:
                score = 60
            else:
                # Use sequence matcher for fuzzy matching
                name_similarity = SequenceMatcher(None, query, name).ratio()
                desc_similarity = SequenceMatcher(None, query, description).ratio()
                score = max(name_similarity, desc_similarity) * 50
            
            if score > 30:  # Only include reasonably good matches
                results.append({
                    'technique_id': tech_id,
                    'name': tech_data.get('name', ''),
                    'description': tech_data.get('description', ''),
                    'tactics': tech_data.get('tactics', []),
                    'score': score
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]


class TTPMappingService:
    """
    Service to automatically map TTPs to MITRE ATT&CK techniques
    """
    
    def __init__(self):
        self.mitre_data = MITREFrameworkData()
        self.keyword_patterns = self._build_keyword_patterns()
    
    def _build_keyword_patterns(self):
        """Build keyword patterns for common TTP indicators"""
        return {
            'phishing': ['phish', 'email', 'spear phish', 'social engineering'],
            'malware': ['malware', 'trojan', 'virus', 'backdoor', 'rat', 'ransomware'],
            'command_injection': ['command injection', 'code injection', 'script', 'powershell', 'cmd'],
            'persistence': ['persistence', 'startup', 'service', 'registry', 'scheduled task'],
            'privilege_escalation': ['privilege escalation', 'admin', 'root', 'elevation'],
            'lateral_movement': ['lateral movement', 'rdp', 'ssh', 'psexec', 'wmi'],
            'data_exfiltration': ['exfiltration', 'data theft', 'file transfer', 'upload'],
            'reconnaissance': ['reconnaissance', 'scan', 'discovery', 'enumeration'],
            'credential_access': ['credential', 'password', 'hash', 'keylog', 'credential dump']
        }
    
    def map_ttp_to_mitre(self, ttp_name: str, ttp_description: str) -> Dict:
        """
        Map a TTP to MITRE ATT&CK technique
        
        Args:
            ttp_name: Name of the TTP
            ttp_description: Description of the TTP
            
        Returns:
            Dictionary containing mapping results with confidence scores
        """
        try:
            # Combine name and description for analysis
            text_to_analyze = f"{ttp_name} {ttp_description}".lower()
            
            # Get technique suggestions
            technique_suggestions = self._analyze_text_for_techniques(text_to_analyze)
            
            # Get tactic suggestions
            tactic_suggestions = self._analyze_text_for_tactics(text_to_analyze)
            
            # Find the best overall match
            best_match = self._find_best_match(technique_suggestions, tactic_suggestions)
            
            return {
                'success': True,
                'best_match': best_match,
                'technique_suggestions': technique_suggestions[:5],
                'tactic_suggestions': tactic_suggestions[:3],
                'confidence': best_match.get('confidence', 0) if best_match else 0,
                'mapping_method': 'automated_text_analysis'
            }
            
        except Exception as e:
            logger.error(f"Error mapping TTP to MITRE: {e}")
            return {
                'success': False,
                'error': str(e),
                'best_match': None,
                'technique_suggestions': [],
                'tactic_suggestions': [],
                'confidence': 0
            }
    
    def _analyze_text_for_techniques(self, text: str) -> List[Dict]:
        """Analyze text to find matching MITRE techniques"""
        suggestions = []
        
        # First, try direct search in MITRE data
        search_results = self.mitre_data.search_techniques(text)
        for result in search_results:
            suggestions.append({
                'technique_id': result['technique_id'],
                'name': result['name'],
                'description': result['description'],
                'tactics': result['tactics'],
                'confidence': min(result['score'], 95),  # Cap at 95% for text matching
                'match_type': 'direct_search'
            })
        
        # Then, try keyword pattern matching
        for pattern_name, keywords in self.keyword_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    # Find techniques associated with this pattern
                    pattern_techniques = self._get_techniques_for_pattern(pattern_name)
                    for tech in pattern_techniques:
                        # Check if already in suggestions
                        existing = next((s for s in suggestions if s['technique_id'] == tech['technique_id']), None)
                        if not existing:
                            suggestions.append({
                                'technique_id': tech['technique_id'],
                                'name': tech['name'],
                                'description': tech['description'],
                                'tactics': tech['tactics'],
                                'confidence': 70,  # Lower confidence for keyword matching
                                'match_type': 'keyword_pattern'
                            })
                        else:
                            # Boost confidence if found through multiple methods
                            existing['confidence'] = min(existing['confidence'] + 10, 90)
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions
    
    def _analyze_text_for_tactics(self, text: str) -> List[Dict]:
        """Analyze text to find matching MITRE tactics"""
        suggestions = []
        
        for tactic_id, tactic_data in self.mitre_data.tactics.items():
            confidence = 0
            match_reasons = []
            
            # Check if tactic name appears in text
            tactic_name = tactic_data.get('name', '').lower()
            if tactic_name in text:
                confidence += 80
                match_reasons.append(f"Tactic name '{tactic_name}' found in text")
            elif any(word in text for word in tactic_name.split()):
                confidence += 40
                match_reasons.append("Partial tactic name match")
            
            # Check description similarity
            tactic_desc = tactic_data.get('description', '').lower()
            desc_similarity = SequenceMatcher(None, text, tactic_desc).ratio()
            if desc_similarity > 0.3:
                confidence += desc_similarity * 30
                match_reasons.append(f"Description similarity: {desc_similarity:.2f}")
            
            if confidence > 20:
                suggestions.append({
                    'tactic_id': tactic_id,
                    'name': tactic_data.get('name', ''),
                    'description': tactic_data.get('description', ''),
                    'confidence': min(confidence, 90),
                    'match_reasons': match_reasons
                })
        
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions
    
    def _get_techniques_for_pattern(self, pattern_name: str) -> List[Dict]:
        """Get MITRE techniques associated with a keyword pattern"""
        pattern_mapping = {
            'phishing': ['T1566'],
            'malware': ['T1059', 'T1055'],
            'command_injection': ['T1059', 'T1190'],
            'persistence': ['T1053', 'T1547'],
            'privilege_escalation': ['T1055', 'T1068'],
            'lateral_movement': ['T1021', 'T1570'],
            'data_exfiltration': ['T1041', 'T1048'],
            'reconnaissance': ['T1595', 'T1590'],
            'credential_access': ['T1003', 'T1555']
        }
        
        technique_ids = pattern_mapping.get(pattern_name, [])
        techniques = []
        
        for tech_id in technique_ids:
            tech_data = self.mitre_data.get_technique(tech_id)
            if tech_data:
                techniques.append({
                    'technique_id': tech_id,
                    'name': tech_data.get('name', ''),
                    'description': tech_data.get('description', ''),
                    'tactics': tech_data.get('tactics', [])
                })
        
        return techniques
    
    def _find_best_match(self, technique_suggestions: List[Dict], tactic_suggestions: List[Dict]) -> Optional[Dict]:
        """Find the best overall MITRE mapping match"""
        if not technique_suggestions:
            return None
        
        best_technique = technique_suggestions[0]
        
        # Try to match with suggested tactics
        if tactic_suggestions:
            best_tactic = tactic_suggestions[0]
            technique_tactics = best_technique.get('tactics', [])
            
            # Check if the best tactic matches the technique's tactics
            if best_tactic['tactic_id'] in technique_tactics:
                # Boost confidence for consistent tactic-technique mapping
                confidence = (best_technique['confidence'] + best_tactic['confidence']) / 2
                return {
                    'technique_id': best_technique['technique_id'],
                    'technique_name': best_technique['name'],
                    'tactic_id': best_tactic['tactic_id'],
                    'tactic_name': best_tactic['name'],
                    'confidence': min(confidence + 10, 95),
                    'match_quality': 'high'
                }
        
        # Return technique with its primary tactic
        primary_tactic = best_technique.get('tactics', [None])[0]
        tactic_data = self.mitre_data.get_tactic(primary_tactic) if primary_tactic else None
        
        return {
            'technique_id': best_technique['technique_id'],
            'technique_name': best_technique['name'],
            'tactic_id': primary_tactic or 'unknown',
            'tactic_name': tactic_data.get('name', 'Unknown') if tactic_data else 'Unknown',
            'confidence': best_technique['confidence'],
            'match_quality': 'medium'
        }
    
    def bulk_map_ttps(self, ttps: List[Dict]) -> Dict:
        """
        Map multiple TTPs to MITRE techniques in bulk
        
        Args:
            ttps: List of dictionaries with 'name' and 'description' keys
            
        Returns:
            Dictionary with mapping results for each TTP
        """
        results = {
            'success': True,
            'total_ttps': len(ttps),
            'mapped_count': 0,
            'high_confidence_count': 0,
            'mappings': [],
            'errors': []
        }
        
        for i, ttp in enumerate(ttps):
            try:
                mapping_result = self.map_ttp_to_mitre(
                    ttp.get('name', ''),
                    ttp.get('description', '')
                )
                
                mapping_data = {
                    'index': i,
                    'ttp_id': ttp.get('id'),
                    'ttp_name': ttp.get('name', ''),
                    'mapping': mapping_result
                }
                
                if mapping_result.get('success') and mapping_result.get('best_match'):
                    results['mapped_count'] += 1
                    if mapping_result.get('confidence', 0) >= 80:
                        results['high_confidence_count'] += 1
                
                results['mappings'].append(mapping_data)
                
            except Exception as e:
                error_msg = f"Error mapping TTP {i}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    def validate_mapping(self, technique_id: str, tactic_id: str) -> Dict:
        """
        Validate a MITRE technique-tactic mapping
        
        Args:
            technique_id: MITRE technique ID (e.g., T1566)
            tactic_id: MITRE tactic ID (e.g., initial-access)
            
        Returns:
            Validation result dictionary
        """
        technique_data = self.mitre_data.get_technique(technique_id)
        tactic_data = self.mitre_data.get_tactic(tactic_id)
        
        if not technique_data:
            return {
                'valid': False,
                'error': f"Technique {technique_id} not found in MITRE ATT&CK framework"
            }
        
        if not tactic_data:
            return {
                'valid': False,
                'error': f"Tactic {tactic_id} not found in MITRE ATT&CK framework"
            }
        
        technique_tactics = technique_data.get('tactics', [])
        if tactic_id not in technique_tactics:
            return {
                'valid': False,
                'error': f"Technique {technique_id} is not associated with tactic {tactic_id}",
                'valid_tactics': technique_tactics
            }
        
        return {
            'valid': True,
            'technique': technique_data,
            'tactic': tactic_data
        }