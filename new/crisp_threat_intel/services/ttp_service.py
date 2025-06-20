from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

from ..domain.models import TTPData, ThreatFeed, User
from ..repositories.ttp_repository import TTPRepository
from ..factories.stix_object_creator import StixTTPCreator
from ..decorators.stix_decorators import StixObject, StixValidationDecorator

logger = logging.getLogger(__name__)


class TTPService:
    """
    Service class for managing Tactics, Techniques, and Procedures (TTPs)
    """
    
    def __init__(self):
        self.repository = TTPRepository()
        self.stix_creator = StixTTPCreator()
    
    def create_ttp(self, threat_feed: ThreatFeed, user: User, ttp_data: Dict[str, Any]) -> TTPData:
        """Create a new TTP"""
        try:
            with transaction.atomic():
                # Validate input data
                self._validate_ttp_data(ttp_data)
                
                # Create TTP
                ttp = TTPData(
                    name=ttp_data['name'],
                    description=ttp_data.get('description', ''),
                    kill_chain_phases=ttp_data.get('kill_chain_phases', []),
                    x_mitre_platforms=ttp_data.get('x_mitre_platforms', []),
                    x_mitre_tactics=ttp_data.get('x_mitre_tactics', []),
                    x_mitre_techniques=ttp_data.get('x_mitre_techniques', []),
                    created=timezone.now(),
                    modified=timezone.now(),
                    created_by_ref=ttp_data.get('created_by_ref'),
                    external_references=ttp_data.get('external_references', []),
                    object_marking_refs=ttp_data.get('object_marking_refs', []),
                    threat_feed=threat_feed,
                    created_by=user
                )
                
                # Save to repository
                ttp = self.repository.save(ttp)
                
                logger.info(f"Created TTP '{ttp.name}' in feed '{threat_feed.name}'")
                return ttp
                
        except Exception as e:
            logger.error(f"Failed to create TTP: {e}")
            raise
    
    def get_ttp(self, ttp_id: str) -> Optional[TTPData]:
        """Get a TTP by ID"""
        return self.repository.get_by_id(ttp_id)
    
    def get_ttps_by_feed(self, threat_feed: ThreatFeed) -> List[TTPData]:
        """Get all TTPs for a threat feed"""
        return self.repository.get_by_threat_feed(threat_feed)
    
    def update_ttp(self, ttp_id: str, update_data: Dict[str, Any], user: User) -> TTPData:
        """Update an existing TTP"""
        try:
            with transaction.atomic():
                ttp = self.repository.get_by_id(ttp_id)
                if not ttp:
                    raise ValueError(f"TTP with ID {ttp_id} not found")
                
                # Update fields
                for field, value in update_data.items():
                    if hasattr(ttp, field) and field not in ['id', 'stix_id', 'created_at', 'created_by']:
                        setattr(ttp, field, value)
                
                ttp.modified = timezone.now()
                ttp = self.repository.save(ttp)
                
                logger.info(f"Updated TTP '{ttp.name}'")
                return ttp
                
        except Exception as e:
            logger.error(f"Failed to update TTP {ttp_id}: {e}")
            raise
    
    def delete_ttp(self, ttp_id: str, user: User) -> bool:
        """Delete a TTP"""
        try:
            with transaction.atomic():
                ttp = self.repository.get_by_id(ttp_id)
                if not ttp:
                    raise ValueError(f"TTP with ID {ttp_id} not found")
                
                ttp_name = ttp.name
                success = self.repository.delete(ttp_id)
                
                if success:
                    logger.info(f"Deleted TTP '{ttp_name}' by user '{user.django_user.username}'")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to delete TTP {ttp_id}: {e}")
            raise
    
    def search_ttps(self, query_params: Dict[str, Any]) -> List[TTPData]:
        """Search TTPs based on query parameters"""
        return self.repository.search(query_params)
    
    def create_ttp_from_mitre(self, threat_feed: ThreatFeed, user: User, mitre_data: Dict[str, Any]) -> TTPData:
        """Create a TTP from MITRE ATT&CK data"""
        try:
            # Map MITRE data to TTP format
            ttp_data = {
                'name': mitre_data.get('name', ''),
                'description': mitre_data.get('description', ''),
                'kill_chain_phases': self._map_mitre_kill_chain(mitre_data.get('kill_chain_phases', [])),
                'x_mitre_platforms': mitre_data.get('x_mitre_platforms', []),
                'x_mitre_tactics': mitre_data.get('x_mitre_tactics', []),
                'x_mitre_techniques': mitre_data.get('x_mitre_techniques', []),
                'external_references': self._create_mitre_references(mitre_data)
            }
            
            return self.create_ttp(threat_feed, user, ttp_data)
            
        except Exception as e:
            logger.error(f"Failed to create TTP from MITRE data: {e}")
            raise
    
    def get_ttp_by_mitre_id(self, mitre_id: str) -> Optional[TTPData]:
        """Get TTP by MITRE ATT&CK ID"""
        ttps = self.repository.search({
            'external_references__external_id': mitre_id,
            'external_references__source_name': 'mitre-attack'
        })
        return ttps[0] if ttps else None
    
    def get_ttps_by_tactic(self, tactic: str) -> List[TTPData]:
        """Get TTPs by MITRE tactic"""
        return self.repository.search({
            'x_mitre_tactics__contains': [tactic]
        })
    
    def get_ttps_by_platform(self, platform: str) -> List[TTPData]:
        """Get TTPs by platform"""
        return self.repository.search({
            'x_mitre_platforms__contains': [platform]
        })
    
    def bulk_create_ttps(self, threat_feed: ThreatFeed, user: User, ttps_data: List[Dict[str, Any]]) -> List[TTPData]:
        """Create multiple TTPs in bulk"""
        created_ttps = []
        errors = []
        
        try:
            with transaction.atomic():
                for i, ttp_data in enumerate(ttps_data):
                    try:
                        ttp = self.create_ttp(threat_feed, user, ttp_data)
                        created_ttps.append(ttp)
                    except Exception as e:
                        errors.append(f"Error creating TTP {i+1}: {str(e)}")
                
                if errors:
                    logger.warning(f"Bulk creation completed with {len(errors)} errors: {errors}")
                
                logger.info(f"Bulk created {len(created_ttps)} TTPs in feed '{threat_feed.name}'")
                return created_ttps
                
        except Exception as e:
            logger.error(f"Failed to bulk create TTPs: {e}")
            raise
    
    def get_ttp_statistics(self, threat_feed: ThreatFeed = None) -> Dict[str, Any]:
        """Get TTP statistics"""
        try:
            if threat_feed:
                ttps = self.repository.get_by_threat_feed(threat_feed)
                scope = f"feed '{threat_feed.name}'"
            else:
                ttps = self.repository.get_all()
                scope = "all feeds"
            
            # Calculate statistics
            total_count = len(ttps)
            
            # Group by tactics and platforms
            tactic_counts = {}
            platform_counts = {}
            
            for ttp in ttps:
                # Count tactics
                for tactic in ttp.x_mitre_tactics:
                    tactic_counts[tactic] = tactic_counts.get(tactic, 0) + 1
                
                # Count platforms
                for platform in ttp.x_mitre_platforms:
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            stats = {
                'scope': scope,
                'total_ttps': total_count,
                'tactic_distribution': tactic_counts,
                'platform_distribution': platform_counts,
                'mitre_coverage': self._calculate_mitre_coverage(ttps)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get TTP statistics: {e}")
            raise
    
    def create_stix_object(self, ttp: TTPData) -> Dict[str, Any]:
        """Create STIX object from TTP"""
        try:
            stix_data = self.stix_creator.create_from_domain_model(ttp)
            
            # Validate STIX object
            stix_obj = StixObject(stix_data)
            validator = StixValidationDecorator(stix_obj)
            
            if validator.validate():
                return stix_data
            else:
                validation_results = validator.get_validation_results()
                logger.warning(f"STIX object validation warnings: {validation_results['warnings']}")
                if validation_results['errors']:
                    raise ValidationError(f"STIX object validation failed: {validation_results['errors']}")
                return stix_data
                
        except Exception as e:
            logger.error(f"Failed to create STIX object for TTP {ttp.id}: {e}")
            raise
    
    def _validate_ttp_data(self, ttp_data: Dict[str, Any]):
        """Validate TTP data"""
        required_fields = ['name']
        
        for field in required_fields:
            if field not in ttp_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate name length
        if len(ttp_data['name']) < 3:
            raise ValidationError("TTP name must be at least 3 characters long")
        
        # Validate kill chain phases
        kill_chain_phases = ttp_data.get('kill_chain_phases', [])
        if kill_chain_phases and not isinstance(kill_chain_phases, list):
            raise ValidationError("Kill chain phases must be a list")
        
        # Validate MITRE fields
        for field in ['x_mitre_platforms', 'x_mitre_tactics', 'x_mitre_techniques']:
            value = ttp_data.get(field, [])
            if value and not isinstance(value, list):
                raise ValidationError(f"{field} must be a list")
    
    def _map_mitre_kill_chain(self, mitre_phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map MITRE kill chain phases to STIX format"""
        mapped_phases = []
        
        for phase in mitre_phases:
            if isinstance(phase, dict):
                mapped_phase = {
                    'kill_chain_name': phase.get('kill_chain_name', 'mitre-attack'),
                    'phase_name': phase.get('phase_name', '')
                }
                mapped_phases.append(mapped_phase)
            elif isinstance(phase, str):
                # If just a string, assume it's a phase name
                mapped_phase = {
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': phase
                }
                mapped_phases.append(mapped_phase)
        
        return mapped_phases
    
    def _create_mitre_references(self, mitre_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create external references for MITRE data"""
        references = []
        
        # Add MITRE ATT&CK reference
        mitre_id = mitre_data.get('external_id') or mitre_data.get('id')
        if mitre_id:
            references.append({
                'source_name': 'mitre-attack',
                'external_id': mitre_id,
                'url': f"https://attack.mitre.org/techniques/{mitre_id}/"
            })
        
        # Add any additional references
        additional_refs = mitre_data.get('external_references', [])
        if isinstance(additional_refs, list):
            references.extend(additional_refs)
        
        return references
    
    def _calculate_mitre_coverage(self, ttps: List[TTPData]) -> Dict[str, Any]:
        """Calculate MITRE ATT&CK framework coverage"""
        # This is a simplified version - in practice, you'd want to compare
        # against the full MITRE ATT&CK framework
        
        unique_tactics = set()
        unique_techniques = set()
        
        for ttp in ttps:
            unique_tactics.update(ttp.x_mitre_tactics)
            unique_techniques.update(ttp.x_mitre_techniques)
        
        # Known MITRE tactics (as of ATT&CK v13)
        known_tactics = {
            'reconnaissance', 'resource-development', 'initial-access',
            'execution', 'persistence', 'privilege-escalation',
            'defense-evasion', 'credential-access', 'discovery',
            'lateral-movement', 'collection', 'command-and-control',
            'exfiltration', 'impact'
        }
        
        coverage = {
            'tactics_covered': len(unique_tactics),
            'techniques_covered': len(unique_techniques),
            'tactic_coverage_percentage': round((len(unique_tactics) / len(known_tactics)) * 100, 2),
            'covered_tactics': list(unique_tactics),
            'missing_tactics': list(known_tactics - unique_tactics)
        }
        
        return coverage