import logging
import pytz
from typing import Dict, Any
import stix2
from django.utils import timezone
from .stix_base_factory import StixObjectCreator, STIXObjectFactory

logger = logging.getLogger(__name__)


class StixMalwareCreator(StixObjectCreator):
    """
    Integrated factory for creating STIX Malware objects.
    Supports bidirectional CRISP↔STIX conversion and data→STIX creation
    """
    
    def create_from_stix(self, stix_obj) -> Dict[str, Any]:
        """
        Create a CRISP Malware entity from a STIX Malware object
        """
        try:
            # Extract malware types
            malware_types = []
            if hasattr(stix_obj, 'malware_types'):
                malware_types = stix_obj.malware_types
            elif hasattr(stix_obj, 'labels'):  # STIX 2.0
                malware_types = stix_obj.labels
            
            # Convert STIX timestamps to datetime objects
            created = stix_obj.created.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'created') else None
            modified = stix_obj.modified.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'modified') else None
            
            # Map STIX Malware to CRISP Malware
            malware_data = {
                'name': stix_obj.name,
                'description': stix_obj.description if hasattr(stix_obj, 'description') else '',
                'malware_types': malware_types,
                'is_family': stix_obj.is_family if hasattr(stix_obj, 'is_family') else False,
                'stix_id': stix_obj.id,
                'created_at': created,
                'updated_at': modified,
                'is_anonymized': False,
            }
            
            return malware_data
            
        except Exception as e:
            logger.error(f"Error creating malware from STIX: {str(e)}")
            raise
    
    def create_stix_object(self, crisp_entity):
        """
        Create a STIX Malware object from a CRISP Malware entity
        """
        try:
            # Determine malware types
            malware_types = crisp_entity.malware_types if hasattr(crisp_entity, 'malware_types') else ['trojan']
            if isinstance(malware_types, str):
                malware_types = [malware_types]
            
            # Create the STIX Malware object
            stix_malware = stix2.Malware(
                name=crisp_entity.name,
                description=crisp_entity.description or '',
                malware_types=malware_types,
                is_family=getattr(crisp_entity, 'is_family', False),
                created=crisp_entity.created_at,
                modified=crisp_entity.updated_at or crisp_entity.created_at
            )
            
            return stix_malware
            
        except Exception as e:
            logger.error(f"Error creating STIX object from malware: {str(e)}")
            raise
    
    def create_object(self, data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Create a STIX Malware object from input data dictionary
        """

        try:
            stix_obj = {
                'type': 'malware',
                'name': data.get('name', 'Unknown Malware'),
                'is_family': data.get('is_family', False),
                'malware_types': data.get('malware_types', ['trojan']),
            }
            
            if 'description' in data:
                stix_obj['description'] = data['description']
            
            if 'labels' in data:
                stix_obj['labels'] = data['labels']
            
            if 'external_references' in data:
                stix_obj['external_references'] = data['external_references']
            
            if 'kill_chain_phases' in data:
                stix_obj['kill_chain_phases'] = data['kill_chain_phases']
            
            if 'created_by_ref' in data:
                stix_obj['created_by_ref'] = data['created_by_ref']
            
            # Handle version-specific differences
            if spec_version == "2.0":
                if 'malware_types' in stix_obj:
                    stix_obj['labels'] = stix_obj.get('labels', []) + stix_obj['malware_types']
                    del stix_obj['malware_types']
                
                # STIX 2.0 doesn't have 'is_family' field
                if 'is_family' in stix_obj:
                    del stix_obj['is_family']
            
            stix_obj = self._ensure_common_properties(stix_obj, spec_version)
            
            # Validate required fields for malware
            if not stix_obj.get('name'):
                raise ValueError("Malware objects must have a name")
            
            # Version-specific validation
            if spec_version == "2.1":
                if 'malware_types' not in data or not data.get('malware_types'):
                    raise ValueError("STIX 2.1 Malware objects must have malware_types")
            elif spec_version == "2.0":
                if not stix_obj.get('labels'):
                    raise ValueError("STIX 2.0 Malware objects must have labels")
            
            logger.debug(f"Created STIX Malware: {stix_obj['id']}")
            return stix_obj
            
        except Exception as e:
            logger.error(f"Error creating STIX object from data: {str(e)}")
            raise


class StixIdentityCreator(StixObjectCreator):
    """
    Integrated factory for creating STIX Identity objects
    """
    
    def create_from_stix(self, stix_obj) -> Dict[str, Any]:
        """
        Create a CRISP Identity entity from a STIX Identity object
        """
        try:
            # Convert STIX timestamps to datetime objects
            created = stix_obj.created.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'created') else None
            modified = stix_obj.modified.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'modified') else None
            
            # Map STIX Identity to CRISP Identity
            identity_data = {
                'name': stix_obj.name,
                'description': stix_obj.description if hasattr(stix_obj, 'description') else '',
                'identity_class': stix_obj.identity_class,
                'sectors': stix_obj.sectors if hasattr(stix_obj, 'sectors') else [],
                'contact_information': stix_obj.contact_information if hasattr(stix_obj, 'contact_information') else '',
                'stix_id': stix_obj.id,
                'created_at': created,
                'updated_at': modified,
                'is_anonymized': False,
            }
            
            return identity_data
            
        except Exception as e:
            logger.error(f"Error creating identity from STIX: {str(e)}")
            raise
    
    def create_stix_object(self, crisp_entity):
        """
        Create a STIX Identity object from a CRISP Identity entity
        """
        try:
            # Create the STIX Identity object
            stix_identity = stix2.Identity(
                name=crisp_entity.name,
                identity_class=crisp_entity.identity_class,
                description=crisp_entity.description or '',
                sectors=getattr(crisp_entity, 'sectors', []),
                contact_information=getattr(crisp_entity, 'contact_information', ''),
                created=crisp_entity.created_at,
                modified=crisp_entity.updated_at or crisp_entity.created_at
            )
            
            return stix_identity
            
        except Exception as e:
            logger.error(f"Error creating STIX object from identity: {str(e)}")
            raise
    
    def create_object(self, data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Create a STIX Identity object from input data dictionary
        """
        try:
            stix_obj = {
                'type': 'identity',
                'name': data.get('name', 'Unknown Identity'),
                'identity_class': data.get('identity_class', 'organization'),
            }
            
            if 'description' in data:
                stix_obj['description'] = data['description']
            
            if 'sectors' in data:
                stix_obj['sectors'] = data['sectors']
            
            if 'contact_information' in data:
                stix_obj['contact_information'] = data['contact_information']
            
            if 'external_references' in data:
                stix_obj['external_references'] = data['external_references']
            
            if 'created_by_ref' in data:
                stix_obj['created_by_ref'] = data['created_by_ref']
            
            # Ensure common properties
            stix_obj = self._ensure_common_properties(stix_obj, spec_version)
            
            # Validate required fields for identity
            if not stix_obj.get('name'):
                raise ValueError("Identity objects must have a name")
            
            if not stix_obj.get('identity_class'):
                raise ValueError("Identity objects must have an identity_class")
            
            logger.debug(f"Created STIX Identity: {stix_obj['id']}")
            return stix_obj
            
        except Exception as e:
            logger.error(f"Error creating STIX object from data: {str(e)}")
            raise


# Register the additional creators
STIXObjectFactory.register_creator('malware', StixMalwareCreator)
STIXObjectFactory.register_creator('identity', StixIdentityCreator)