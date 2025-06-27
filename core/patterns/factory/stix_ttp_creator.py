import logging
from datetime import datetime
import pytz
from stix2 import AttackPattern
from core.patterns.factory.stix_object_creator import StixObjectCreator

logger = logging.getLogger(__name__)

class StixTTPCreator(StixObjectCreator):
    """
    Factory for creating STIX Attack Pattern objects
    """
    
    def create_from_stix(self, stix_obj):
        """
        Create a CRISP TTP entity from a STIX Attack Pattern object.
        
        Args:
            stix_obj: STIX Attack Pattern object
            
        Returns:
            Dictionary with CRISP TTP properties
        """
        try:
            mitre_technique_id = None
            mitre_tactic = None
            
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
            
            # Map STIX Attack Pattern to CRISP TTP
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
        Create a STIX Attack Pattern object from a CRISP TTP entity.
        
        Args:
            crisp_entity: CRISP TTP model instance
            
        Returns:
            STIX Attack Pattern object
        """
        try:
            # Create external references if MITRE ATT&CK info is available
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
                kill_chain_phases=kill_chain_phases if kill_chain_phases else None
            )
            
            return attack_pattern
            
        except Exception as e:
            logger.error(f"Error creating STIX object from TTP: {str(e)}")
            raise