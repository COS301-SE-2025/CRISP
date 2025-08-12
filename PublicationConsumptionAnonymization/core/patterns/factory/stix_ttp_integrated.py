import logging
from datetime import datetime
from typing import Dict, Any
import pytz
from stix2 import AttackPattern
import stix2
import re
from django.utils import timezone
from .stix_base_factory import StixObjectCreator, STIXObjectFactory

logger = logging.getLogger(__name__)


class StixTTPCreator(StixObjectCreator):
    """
    Integrated factory for creating STIX Attack Pattern objects (TTPs)
    """
    
    def create_from_stix(self, stix_obj) -> Dict[str, Any]:
        """
        Create a CRISP TTP entity from a STIX Attack Pattern object
        """
        try:
            mitre_technique_id = None
            mitre_tactic = None
            
            # Extract MITRE ATT&CK information from external references
            if hasattr(stix_obj, 'external_references'):
                for ref in stix_obj.external_references:
                    if ref.get('source_name') == 'mitre-attack':
                        mitre_technique_id = ref.get('external_id')
                        break
            
            # Try to determine the tactic from the kill chain phases
            if hasattr(stix_obj, 'kill_chain_phases'):
                for phase in stix_obj.kill_chain_phases:
                    if phase.get('kill_chain_name') == 'mitre-attack':
                        mitre_tactic = phase.get('phase_name')
                        break
            
            # Convert STIX timestamps to datetime objects
            created = stix_obj.created.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'created') else None
            modified = stix_obj.modified.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'modified') else None
            
            # Map STIX Attack Pattern to TTP
            ttp_data = {
                'name': stix_obj.name,
                'description': stix_obj.description if hasattr(stix_obj, 'description') else '',
                'mitre_technique_id': mitre_technique_id,
                'mitre_tactic': mitre_tactic,
                'stix_id': stix_obj.id,
                'created_at': created,
                'updated_at': modified,
                'is_anonymized': False,
            }
            
            return ttp_data
            
        except Exception as e:
            logger.error(f"Error creating TTP from STIX: {str(e)}")
            raise
    
    def create_stix_object(self, crisp_entity):
        """
        Create a STIX Attack Pattern object from a CRISP TTP entity
        """
        try:
            # Create external references if MITRE ATT&CK
            external_references = []
            if crisp_entity.mitre_technique_id:
                external_references.append({
                    'source_name': 'mitre-attack',
                    'external_id': crisp_entity.mitre_technique_id,
                    'url': f'https://attack.mitre.org/techniques/{crisp_entity.mitre_technique_id}/'
                })
            
            # Create kill chain phases if tactic is available
            kill_chain_phases = []
            if crisp_entity.mitre_tactic:
                kill_chain_phases.append({
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': crisp_entity.mitre_tactic
                })
            
            # Create the STIX Attack Pattern
            attack_pattern = AttackPattern(
                name=crisp_entity.name,
                description=crisp_entity.description,
                external_references=external_references if external_references else None,
                kill_chain_phases=kill_chain_phases if kill_chain_phases else None,
                created=crisp_entity.created_at,
                modified=crisp_entity.updated_at or crisp_entity.created_at
            )
            
            return attack_pattern
            
        except Exception as e:
            logger.error(f"Error creating STIX object from TTP: {str(e)}")
            raise
    
    def create_object(self, data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Create a STIX Attack Pattern object from input data dictionary
        """
        try:
            # Create base STIX object
            stix_obj = {
                'type': 'attack-pattern',
                'name': data.get('name', 'Unknown Attack Pattern'),
            }
            
            # Add optional properties
            if 'description' in data:
                stix_obj['description'] = data['description']
            
            if 'external_references' in data:
                stix_obj['external_references'] = data['external_references']
            
            if 'kill_chain_phases' in data:
                stix_obj['kill_chain_phases'] = data['kill_chain_phases']
            
            if 'x_mitre_id' in data:
                stix_obj['x_mitre_id'] = data['x_mitre_id']
            
            if 'created_by_ref' in data:
                stix_obj['created_by_ref'] = data['created_by_ref']
            
            if 'mitre_technique_id' in data and 'external_references' not in data:
                stix_obj['external_references'] = [{
                    'source_name': 'mitre-attack',
                    'external_id': data['mitre_technique_id'],
                    'url': f'https://attack.mitre.org/techniques/{data["mitre_technique_id"]}/'
                }]
            
            if 'mitre_tactic' in data and 'kill_chain_phases' not in data:
                stix_obj['kill_chain_phases'] = [{
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': data['mitre_tactic']
                }]
            
            # Ensure common properties
            stix_obj = self._ensure_common_properties(stix_obj, spec_version)
            
            # Validate required fields for attack patterns
            if not stix_obj.get('name'):
                raise ValueError("Attack Pattern objects must have a name")
            
            logger.debug(f"Created STIX Attack Pattern: {stix_obj['id']}")
            return stix_obj
            
        except Exception as e:
            logger.error(f"Error creating STIX object from data: {str(e)}")
            raise

    def _extract_mitre_info(self, stix_pattern):
        """
        Extract MITRE ATT&CK technique ID and tactic from STIX pattern
        """
        # Default values
        technique_id = None
        tactic = None
        
        # Handle both dictionary (STIX object) and string patterns
        if isinstance(stix_pattern, dict):
            # Extract from external_references
            if 'external_references' in stix_pattern:
                for ref in stix_pattern['external_references']:
                    if ref.get('source_name') == 'mitre-attack':
                        technique_id = ref.get('external_id')
                        break
            
            # Extract from kill_chain_phases
            if 'kill_chain_phases' in stix_pattern:
                for phase in stix_pattern['kill_chain_phases']:
                    if phase.get('kill_chain_name') == 'mitre-attack':
                        tactic = phase.get('phase_name')
                        break
        
        # Handle string patterns (original logic)
        elif stix_pattern and "attack-pattern" in str(stix_pattern):
            # Extract technique ID using regex
            technique_match = re.search(r'technique_id=[\'"](T\d+\.\d+)[\'"]', stix_pattern)
            if technique_match:
                technique_id = technique_match.group(1)
                
            # Extract tactic
            tactic_match = re.search(r'tactic=[\'"]([\w\-]+)[\'"]', stix_pattern)
            if tactic_match:
                tactic = tactic_match.group(1)
                
        return technique_id, tactic


# Register the TTP creator
STIXObjectFactory.register_creator('attack-pattern', StixTTPCreator)