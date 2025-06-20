from typing import Dict, Any, List, Optional, Union
from django.utils import timezone
import json
import uuid
import logging

from ..domain.models import Institution, ThreatFeed, Indicator, TTPData
from ..factories.stix_object_creator import StixObjectFactory, StixObject
from ..decorators.stix_decorators import (
    StixValidationDecorator, 
    StixTaxiiExportDecorator, 
    StixEnrichmentDecorator,
    StixMarkingDecorator
)
from ..strategies.anonymization_strategy import AnonymizationContext, AnonymizationStrategyFactory

logger = logging.getLogger(__name__)


class StixTaxiiService:
    """
    Service class for handling STIX/TAXII operations
    """
    
    def __init__(self):
        self.stix_factory = StixObjectFactory()
        self.anonymization_context = AnonymizationContext()
    
    def create_stix_bundle(self, objects: List[Union[Indicator, TTPData]], bundle_id: str = None) -> Dict[str, Any]:
        """Create a STIX bundle from domain objects"""
        try:
            if not bundle_id:
                bundle_id = f"bundle--{uuid.uuid4()}"
            
            stix_objects = []
            
            for obj in objects:
                if isinstance(obj, Indicator):
                    stix_data = obj.to_stix()
                elif isinstance(obj, TTPData):
                    stix_data = obj.to_stix()
                else:
                    logger.warning(f"Unsupported object type: {type(obj)}")
                    continue
                
                stix_objects.append(stix_data)
            
            bundle = {
                'type': 'bundle',
                'id': bundle_id,
                'spec_version': '2.1',
                'objects': stix_objects
            }
            
            logger.info(f"Created STIX bundle with {len(stix_objects)} objects")
            return bundle
            
        except Exception as e:
            logger.error(f"Failed to create STIX bundle: {e}")
            raise
    
    def create_anonymized_bundle(self, objects: List[Union[Indicator, TTPData]], 
                                target_institution: Institution, 
                                source_institution: Institution) -> Dict[str, Any]:
        """Create an anonymized STIX bundle based on trust level"""
        try:
            # Get trust level between institutions
            trust_level = self._get_trust_level(source_institution, target_institution)
            
            # Set appropriate anonymization strategy
            strategy = AnonymizationStrategyFactory.get_strategy_for_trust_level(trust_level)
            self.anonymization_context.set_strategy(strategy)
            
            anonymized_objects = []
            
            for obj in objects:
                if isinstance(obj, Indicator):
                    stix_data = obj.to_stix()
                elif isinstance(obj, TTPData):
                    stix_data = obj.to_stix()
                else:
                    continue
                
                # Apply anonymization
                anonymized_data = self.anonymization_context.anonymize_data(stix_data, trust_level)
                anonymized_objects.append(anonymized_data)
            
            bundle = {
                'type': 'bundle',
                'id': f"bundle--{uuid.uuid4()}",
                'spec_version': '2.1',
                'objects': anonymized_objects
            }
            
            logger.info(f"Created anonymized STIX bundle with {len(anonymized_objects)} objects for {target_institution.name}")
            return bundle
            
        except Exception as e:
            logger.error(f"Failed to create anonymized STIX bundle: {e}")
            raise
    
    def validate_stix_object(self, stix_data: Dict[str, Any], strict: bool = True) -> Dict[str, Any]:
        """Validate a STIX object"""
        try:
            stix_obj = StixObject(stix_data)
            validator = StixValidationDecorator(stix_obj, strict_validation=strict)
            
            is_valid = validator.validate()
            validation_results = validator.get_validation_results()
            
            logger.info(f"STIX object validation: {'passed' if is_valid else 'failed'}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate STIX object: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    def prepare_for_taxii_export(self, stix_data: Dict[str, Any], collection_id: str) -> Dict[str, Any]:
        """Prepare STIX object for TAXII export"""
        try:
            stix_obj = StixObject(stix_data)
            taxii_decorator = StixTaxiiExportDecorator(stix_obj, collection_id)
            
            export_data = taxii_decorator.prepare_for_taxii_export()
            
            logger.info(f"Prepared STIX object for TAXII export to collection {collection_id}")
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to prepare STIX object for TAXII export: {e}")
            raise
    
    def create_taxii_envelope(self, stix_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create TAXII envelope for STIX objects"""
        try:
            if not stix_objects:
                raise ValueError("No STIX objects provided")
            
            # Use the first object to create the decorator
            first_obj = StixObject(stix_objects[0])
            taxii_decorator = StixTaxiiExportDecorator(first_obj)
            
            envelope = {
                'id': f"bundle--{uuid.uuid4()}",
                'type': 'bundle',
                'spec_version': '2.1',
                'objects': stix_objects
            }
            
            logger.info(f"Created TAXII envelope with {len(stix_objects)} objects")
            return envelope
            
        except Exception as e:
            logger.error(f"Failed to create TAXII envelope: {e}")
            raise
    
    def enrich_stix_object(self, stix_data: Dict[str, Any], enrichments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enrich STIX object with additional data"""
        try:
            stix_obj = StixObject(stix_data)
            enrichment_decorator = StixEnrichmentDecorator(stix_obj)
            
            for enrichment in enrichments:
                enrichment_type = enrichment.get('type')
                enrichment_data = enrichment.get('data', {})
                
                if enrichment_type == 'confidence':
                    score = enrichment_data.get('score', 0)
                    source = enrichment_data.get('source')
                    enrichment_decorator.add_confidence_score(score, source)
                
                elif enrichment_type == 'external_reference':
                    enrichment_decorator.add_external_reference(
                        source_name=enrichment_data.get('source_name', ''),
                        url=enrichment_data.get('url'),
                        external_id=enrichment_data.get('external_id'),
                        description=enrichment_data.get('description')
                    )
                
                elif enrichment_type == 'context':
                    context_type = enrichment_data.get('context_type', '')
                    context_data = enrichment_data.get('context_data', {})
                    enrichment_decorator.add_context_information(context_type, context_data)
            
            enriched_data = enrichment_decorator.to_dict()
            
            logger.info(f"Enriched STIX object with {len(enrichments)} enrichments")
            return enriched_data
            
        except Exception as e:
            logger.error(f"Failed to enrich STIX object: {e}")
            raise
    
    def apply_marking(self, stix_data: Dict[str, Any], markings: Dict[str, Any]) -> Dict[str, Any]:
        """Apply markings to STIX object"""
        try:
            stix_obj = StixObject(stix_data)
            marking_decorator = StixMarkingDecorator(stix_obj)
            
            # Apply TLP markings
            tlp_level = markings.get('tlp')
            if tlp_level:
                marking_decorator.add_tlp_marking(tlp_level)
            
            # Apply object markings
            object_markings = markings.get('object_markings', [])
            for marking_ref in object_markings:
                marking_decorator.add_object_marking(marking_ref)
            
            # Apply granular markings
            granular_markings = markings.get('granular_markings', [])
            for granular_marking in granular_markings:
                selectors = granular_marking.get('selectors', [])
                marking_ref = granular_marking.get('marking_ref', '')
                if selectors and marking_ref:
                    marking_decorator.add_granular_marking(selectors, marking_ref)
            
            marked_data = marking_decorator.to_dict()
            
            logger.info(f"Applied markings to STIX object")
            return marked_data
            
        except Exception as e:
            logger.error(f"Failed to apply markings to STIX object: {e}")
            raise
    
    def import_stix_bundle(self, bundle_data: Dict[str, Any], target_feed: ThreatFeed) -> Dict[str, Any]:
        """Import STIX bundle into threat feed"""
        try:
            if bundle_data.get('type') != 'bundle':
                raise ValueError("Invalid STIX bundle: missing 'bundle' type")
            
            objects = bundle_data.get('objects', [])
            if not objects:
                raise ValueError("STIX bundle contains no objects")
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            from ..services.indicator_service import IndicatorService
            from ..services.ttp_service import TTPService
            
            indicator_service = IndicatorService()
            ttp_service = TTPService()
            
            for obj in objects:
                try:
                    obj_type = obj.get('type')
                    
                    if obj_type == 'indicator':
                        # Convert STIX indicator to domain model
                        indicator_data = self._convert_stix_indicator(obj)
                        indicator_service.create_indicator(target_feed, target_feed.created_by, indicator_data)
                        imported_count += 1
                    
                    elif obj_type == 'attack-pattern':
                        # Convert STIX attack pattern to TTP
                        ttp_data = self._convert_stix_attack_pattern(obj)
                        ttp_service.create_ttp(target_feed, target_feed.created_by, ttp_data)
                        imported_count += 1
                    
                    else:
                        skipped_count += 1
                        logger.info(f"Skipped unsupported object type: {obj_type}")
                
                except Exception as e:
                    errors.append(f"Error importing {obj.get('type', 'unknown')} object: {str(e)}")
            
            result = {
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'error_count': len(errors),
                'errors': errors
            }
            
            logger.info(f"Imported STIX bundle: {imported_count} objects imported, {skipped_count} skipped, {len(errors)} errors")
            return result
            
        except Exception as e:
            logger.error(f"Failed to import STIX bundle: {e}")
            raise
    
    def export_threat_feed_to_stix(self, threat_feed: ThreatFeed, include_anonymization: bool = False, 
                                  target_institution: Institution = None) -> Dict[str, Any]:
        """Export threat feed to STIX bundle"""
        try:
            objects = []
            
            # Get all indicators and TTPs from the feed
            indicators = threat_feed.indicators.all()
            ttps = threat_feed.ttp_data.all()
            
            # Add indicators
            for indicator in indicators:
                objects.append(indicator)
            
            # Add TTPs
            for ttp in ttps:
                objects.append(ttp)
            
            # Create bundle
            if include_anonymization and target_institution:
                bundle = self.create_anonymized_bundle(objects, target_institution, threat_feed.institution)
            else:
                bundle = self.create_stix_bundle(objects)
            
            logger.info(f"Exported threat feed '{threat_feed.name}' to STIX bundle")
            return bundle
            
        except Exception as e:
            logger.error(f"Failed to export threat feed to STIX: {e}")
            raise
    
    def _get_trust_level(self, source_institution: Institution, target_institution: Institution) -> float:
        """Get trust level between institutions"""
        from ..domain.models import TrustRelationship
        
        trust_rel = TrustRelationship.objects.filter(
            source_institution=source_institution,
            target_institution=target_institution,
            is_active=True
        ).first()
        
        if trust_rel:
            return trust_rel.trust_level
        
        # Default trust level
        return 0.5
    
    def _convert_stix_indicator(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Convert STIX indicator to domain model format"""
        return {
            'name': stix_obj.get('name', f"Imported Indicator {stix_obj.get('id', '')}"),
            'description': stix_obj.get('description', ''),
            'pattern': stix_obj.get('pattern', ''),
            'labels': stix_obj.get('labels', []),
            'valid_from': stix_obj.get('valid_from'),
            'valid_until': stix_obj.get('valid_until'),
            'confidence': stix_obj.get('confidence', 0),
            'created_by_ref': stix_obj.get('created_by_ref'),
            'external_references': stix_obj.get('external_references', []),
            'object_marking_refs': stix_obj.get('object_marking_refs', [])
        }
    
    def _convert_stix_attack_pattern(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Convert STIX attack pattern to TTP domain model format"""
        return {
            'name': stix_obj.get('name', f"Imported TTP {stix_obj.get('id', '')}"),
            'description': stix_obj.get('description', ''),
            'kill_chain_phases': stix_obj.get('kill_chain_phases', []),
            'x_mitre_platforms': stix_obj.get('x_mitre_platforms', []),
            'x_mitre_tactics': stix_obj.get('x_mitre_tactics', []),
            'x_mitre_techniques': stix_obj.get('x_mitre_techniques', []),
            'created_by_ref': stix_obj.get('created_by_ref'),
            'external_references': stix_obj.get('external_references', []),
            'object_marking_refs': stix_obj.get('object_marking_refs', [])
        }