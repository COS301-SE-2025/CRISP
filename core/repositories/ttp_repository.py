"""
Repository for handling TTP (Tactics, Techniques, and Procedures) data operations.
"""
import logging
from typing import List, Optional
from django.db import transaction

from core.models.ttp_data import TTPData

logger = logging.getLogger(__name__)


class TTPRepository:
    """Repository for TTP operations"""
    
    def __init__(self):
        pass
    
    def create_from_stix(self, stix_data, threat_feed=None):
        """Create TTP from STIX data"""
        try:
            # Extract STIX ID if available
            stix_id = None
            if hasattr(stix_data, 'id'):
                stix_id = str(stix_data.id)
            elif isinstance(stix_data, dict) and 'id' in stix_data:
                stix_id = stix_data['id']
            
            # Check if TTP already exists
            if stix_id:
                existing = TTPData.objects.filter(stix_id=stix_id).first()
                if existing:
                    logger.info(f"TTP {stix_id} already exists, updating")
                    return self._update_ttp(existing, stix_data, threat_feed)
            
            # Create new TTP
            ttp_data = self._extract_ttp_data(stix_data)
            ttp = TTPData.objects.create(
                stix_id=stix_id,
                threat_feed=threat_feed,
                **ttp_data
            )
            
            logger.info(f"Created TTP {ttp.id}")
            return ttp
            
        except Exception as e:
            logger.error(f"Error creating TTP from STIX: {str(e)}")
            raise
    
    def get_by_id(self, ttp_id):
        """Get TTP by ID"""
        try:
            return TTPData.objects.get(id=ttp_id)
        except TTPData.DoesNotExist:
            return None
    
    def get_by_stix_id(self, stix_id):
        """Get TTP by STIX ID"""
        try:
            return TTPData.objects.get(stix_id=stix_id)
        except TTPData.DoesNotExist:
            return None
    
    def get_all(self):
        """Get all TTPs"""
        return TTPData.objects.all()
    
    def get_by_threat_feed(self, threat_feed):
        """Get TTPs by threat feed"""
        return TTPData.objects.filter(threat_feed=threat_feed)
    
    def create(self, ttp_data):
        """Create a new TTP"""
        return TTPData.objects.create(**ttp_data)
    
    def get_by_feed(self, feed_id):
        """Get TTPs by threat feed ID"""
        return TTPData.objects.filter(threat_feed_id=feed_id)
    
    def update(self, ttp_id, update_data):
        """Update TTP by ID"""
        try:
            ttp = TTPData.objects.get(id=ttp_id)
            for key, value in update_data.items():
                if hasattr(ttp, key):
                    setattr(ttp, key, value)
            ttp.save()
            return ttp
        except TTPData.DoesNotExist:
            return None
    
    def delete(self, ttp_id):
        """Delete TTP by ID"""
        try:
            ttp = TTPData.objects.get(id=ttp_id)
            ttp.delete()
            return True
        except TTPData.DoesNotExist:
            return False
    
    def _extract_ttp_data(self, stix_data):
        """Extract TTP data from STIX object"""
        data = {}
        
        if hasattr(stix_data, 'name'):
            data['name'] = str(stix_data.name)
        elif isinstance(stix_data, dict) and 'name' in stix_data:
            data['name'] = stix_data['name']
        else:
            data['name'] = 'Unknown TTP'
        
        if hasattr(stix_data, 'description'):
            data['description'] = str(stix_data.description)
        elif isinstance(stix_data, dict) and 'description' in stix_data:
            data['description'] = stix_data['description']
        else:
            data['description'] = ''
        
        # Handle MITRE ATT&CK technique ID
        if hasattr(stix_data, 'external_references'):
            for ref in stix_data.external_references:
                if hasattr(ref, 'source_name') and ref.source_name == 'mitre-attack':
                    if hasattr(ref, 'external_id'):
                        data['mitre_technique_id'] = ref.external_id
                    break
        elif isinstance(stix_data, dict) and 'external_references' in stix_data:
            for ref in stix_data['external_references']:
                if ref.get('source_name') == 'mitre-attack':
                    if 'external_id' in ref:
                        data['mitre_technique_id'] = ref['external_id']
                    break
        
        # Handle kill chain phases and map to MITRE tactic
        mitre_tactic = None
        if hasattr(stix_data, 'kill_chain_phases'):
            for phase in stix_data.kill_chain_phases:
                phase_name = None
                if hasattr(phase, 'phase_name'):
                    phase_name = phase.phase_name
                elif isinstance(phase, dict) and 'phase_name' in phase:
                    phase_name = phase['phase_name']
                
                if phase_name:
                    mitre_tactic = self._map_phase_to_tactic(phase_name)
                    if mitre_tactic:
                        break
        elif isinstance(stix_data, dict) and 'kill_chain_phases' in stix_data:
            for phase in stix_data['kill_chain_phases']:
                if 'phase_name' in phase:
                    mitre_tactic = self._map_phase_to_tactic(phase['phase_name'])
                    if mitre_tactic:
                        break
        
        if mitre_tactic:
            data['mitre_tactic'] = mitre_tactic
        
        # Default values for required fields only
        data.setdefault('mitre_technique_id', '')
        data.setdefault('is_anonymized', False)
        
        return data
    
    def _map_phase_to_tactic(self, phase_name):
        """Map STIX kill chain phase to MITRE tactic"""
        phase_mapping = {
            'reconnaissance': 'reconnaissance',
            'resource-development': 'resource_development',
            'initial-access': 'initial_access',
            'execution': 'execution',
            'persistence': 'persistence',
            'privilege-escalation': 'privilege_escalation',
            'defense-evasion': 'defense_evasion',
            'credential-access': 'credential_access',
            'discovery': 'discovery',
            'lateral-movement': 'lateral_movement',
            'collection': 'collection',
            'command-and-control': 'command_and_control',
            'exfiltration': 'exfiltration',
            'impact': 'impact',
            # Handle common variations
            'command-control': 'command_and_control',
            'c2': 'command_and_control',
            'privesc': 'privilege_escalation',
            'lateral-move': 'lateral_movement',
            'defense-evasion': 'defense_evasion',
        }
        
        if phase_name:
            normalized_phase = phase_name.lower().replace('_', '-')
            return phase_mapping.get(normalized_phase, 'other')
        return 'other'
    
    def _update_ttp(self, ttp, stix_data, threat_feed=None):
        """Update existing TTP with new STIX data"""
        try:
            updated_data = self._extract_ttp_data(stix_data)
            
            # Update fields
            for key, value in updated_data.items():
                if hasattr(ttp, key):
                    setattr(ttp, key, value)
            
            if threat_feed:
                ttp.threat_feed = threat_feed
            
            ttp.save()
            logger.info(f"Updated TTP {ttp.id}")
            return ttp
            
        except Exception as e:
            logger.error(f"Error updating TTP: {str(e)}")
            raise