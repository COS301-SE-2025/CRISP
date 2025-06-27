"""
Trust-based Anonymization Service

This service integrates trust relationships with anonymization strategies
to automatically apply appropriate anonymization levels based on trust between organizations.
"""
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models.trust_models.models import TrustRelationship, TrustLevel, SharingPolicy
from ..models.auth import Organization
from ..models.indicator import Indicator
from ..models.ttp_data import TTPData
from ..models.stix_object import STIXObject
from ..services.trust_service import TrustService
from ..strategies.context import AnonymizationContext
from ..strategies.enums import AnonymizationLevel, DataType

logger = logging.getLogger(__name__)


class TrustAnonymizationService:
    """
    Service that integrates trust relationships with anonymization strategies
    to provide automatic trust-based data anonymization for intelligence sharing.
    """
    
    def __init__(self, trust_service: TrustService = None, anonymization_context: AnonymizationContext = None):
        """
        Initialize the service with trust and anonymization components.
        
        Args:
            trust_service: TrustService for managing trust relationships
            anonymization_context: AnonymizationContext for data anonymization
        """
        self.trust_service = trust_service or TrustService()
        self.anonymization_context = anonymization_context or AnonymizationContext()
    
    def get_trust_based_anonymization_level(self, source_org: Organization, target_org: Organization) -> str:
        """
        Determine the appropriate anonymization level based on trust relationship.
        
        Args:
            source_org: Organization sharing the intelligence
            target_org: Organization receiving the intelligence
            
        Returns:
            str: Anonymization level ('none', 'minimal', 'partial', 'full', 'custom')
        """
        try:
            # Check direct trust relationship
            trust_info = self.trust_service.check_trust_level(str(source_org.id), str(target_org.id))
            
            if trust_info:
                trust_level, relationship = trust_info
                
                # Use relationship-specific anonymization level if set
                if relationship:
                    effective_level = relationship.get_effective_anonymization_level()
                    logger.info(f"Trust-based anonymization level for {source_org.name} -> {target_org.name}: {effective_level}")
                    return effective_level
                
                # Fall back to trust level defaults
                if trust_level:
                    default_level = trust_level.default_anonymization_level
                    logger.info(f"Using trust level default anonymization for {source_org.name} -> {target_org.name}: {default_level}")
                    return default_level
            
            # No trust relationship found - apply maximum anonymization
            logger.warning(f"No trust relationship found between {source_org.name} and {target_org.name}, applying full anonymization")
            return 'full'
            
        except Exception as e:
            logger.error(f"Error determining trust-based anonymization level: {str(e)}")
            # Default to full anonymization on error for security
            return 'full'
    
    def anonymize_indicator_for_organization(self, indicator: Indicator, target_org: Organization) -> Dict[str, Any]:
        """
        Anonymize an indicator based on trust relationship with target organization.
        
        Args:
            indicator: Indicator to anonymize
            target_org: Organization that will receive the indicator
            
        Returns:
            Dict: Anonymized indicator data
        """
        try:
            # Get source organization from indicator's threat feed
            source_org = None
            if indicator.threat_feed and hasattr(indicator.threat_feed, 'owner'):
                source_org = indicator.threat_feed.owner
            
            if not source_org:
                logger.error(f"Cannot determine source organization for indicator {indicator.id}")
                # Apply full anonymization if source is unknown
                anonymization_level = 'full'
            else:
                anonymization_level = self.get_trust_based_anonymization_level(source_org, target_org)
            
            # Convert string level to enum
            level_mapping = {
                'none': AnonymizationLevel.NONE,
                'minimal': AnonymizationLevel.LOW,
                'partial': AnonymizationLevel.MEDIUM,
                'full': AnonymizationLevel.HIGH,
                'custom': AnonymizationLevel.FULL
            }
            
            anon_level = level_mapping.get(anonymization_level, AnonymizationLevel.FULL)
            
            # Anonymize indicator data
            indicator_data = {
                'id': indicator.id,
                'type': indicator.type,
                'value': indicator.value,
                'description': indicator.description or '',
                'confidence': indicator.confidence,
                'first_seen': indicator.first_seen,
                'last_seen': indicator.last_seen,
                'pattern': getattr(indicator, 'pattern', ''),
                'stix_id': indicator.stix_id
            }
            
            # Apply anonymization based on trust level
            anonymized_data = self._anonymize_data_dict(indicator_data, anon_level)
            
            logger.info(f"Anonymized indicator {indicator.id} for organization {target_org.name} with level {anonymization_level}")
            return anonymized_data
            
        except Exception as e:
            logger.error(f"Error anonymizing indicator {indicator.id}: {str(e)}")
            raise
    
    def anonymize_ttp_for_organization(self, ttp: TTPData, target_org: Organization) -> Dict[str, Any]:
        """
        Anonymize a TTP based on trust relationship with target organization.
        
        Args:
            ttp: TTPData to anonymize
            target_org: Organization that will receive the TTP data
            
        Returns:
            Dict: Anonymized TTP data
        """
        try:
            # Get source organization from TTP's threat feed
            source_org = None
            if ttp.threat_feed and hasattr(ttp.threat_feed, 'owner'):
                owner = ttp.threat_feed.owner
                # Check if owner is an Organization or Institution
                if hasattr(owner, 'domain'):  # Organization has domain field
                    source_org = owner
                else:
                    # Institution owner - we need to find corresponding Organization
                    # For now, default to full anonymization for security
                    logger.warning(f"Threat feed owner is Institution, not Organization. Defaulting to full anonymization.")
                    source_org = None
            
            if not source_org:
                logger.error(f"Cannot determine source organization for TTP {ttp.id}")
                anonymization_level = 'full'
            else:
                anonymization_level = self.get_trust_based_anonymization_level(source_org, target_org)
            
            # Convert string level to enum
            level_mapping = {
                'none': AnonymizationLevel.NONE,
                'minimal': AnonymizationLevel.LOW,
                'partial': AnonymizationLevel.MEDIUM,
                'full': AnonymizationLevel.HIGH,
                'custom': AnonymizationLevel.FULL
            }
            
            anon_level = level_mapping.get(anonymization_level, AnonymizationLevel.FULL)
            
            # Prepare TTP data
            ttp_data = {
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description or '',
                'mitre_technique_id': ttp.mitre_technique_id or '',
                'mitre_tactic': ttp.mitre_tactic or '',
                'stix_id': ttp.stix_id
            }
            
            # Apply anonymization
            anonymized_data = self._anonymize_data_dict(ttp_data, anon_level)
            
            logger.info(f"Anonymized TTP {ttp.id} for organization {target_org.name} with level {anonymization_level}")
            return anonymized_data
            
        except Exception as e:
            logger.error(f"Error anonymizing TTP {ttp.id}: {str(e)}")
            raise
    
    def bulk_anonymize_for_organization(self, 
                                      indicators: List[Indicator] = None, 
                                      ttps: List[TTPData] = None, 
                                      target_org: Organization = None) -> Dict[str, List[Dict]]:
        """
        Bulk anonymize indicators and TTPs for a target organization.
        
        Args:
            indicators: List of indicators to anonymize
            ttps: List of TTPs to anonymize
            target_org: Target organization
            
        Returns:
            Dict: Anonymized indicators and TTPs
        """
        result = {
            'indicators': [],
            'ttps': [],
            'stats': {
                'indicators_processed': 0,
                'ttps_processed': 0,
                'errors': 0
            }
        }
        
        # Process indicators
        if indicators:
            for indicator in indicators:
                try:
                    anonymized = self.anonymize_indicator_for_organization(indicator, target_org)
                    result['indicators'].append(anonymized)
                    result['stats']['indicators_processed'] += 1
                except Exception as e:
                    logger.error(f"Error processing indicator {indicator.id}: {str(e)}")
                    result['stats']['errors'] += 1
        
        # Process TTPs
        if ttps:
            for ttp in ttps:
                try:
                    anonymized = self.anonymize_ttp_for_organization(ttp, target_org)
                    result['ttps'].append(anonymized)
                    result['stats']['ttps_processed'] += 1
                except Exception as e:
                    logger.error(f"Error processing TTP {ttp.id}: {str(e)}")
                    result['stats']['errors'] += 1
        
        return result
    
    def get_sharing_organizations_for_data(self, source_org: Organization, 
                                         data_classification: str = 'TLP:WHITE') -> List[Tuple[Organization, str]]:
        """
        Get list of organizations that can receive data from source organization with their anonymization levels.
        
        Args:
            source_org: Source organization
            data_classification: TLP classification of the data
            
        Returns:
            List[Tuple[Organization, str]]: List of (organization, anonymization_level) tuples
        """
        try:
            sharing_data = self.trust_service.get_sharing_organizations(str(source_org.id))
            
            result = []
            for org_id, trust_level, relationship in sharing_data:
                try:
                    target_org = Organization.objects.get(id=org_id)
                    anonymization_level = self.get_trust_based_anonymization_level(source_org, target_org)
                    
                    # Check if organization can receive this classification level
                    if self._can_receive_classification(target_org, data_classification, anonymization_level):
                        result.append((target_org, anonymization_level))
                    
                except Organization.DoesNotExist:
                    logger.warning(f"Organization {org_id} not found")
                    continue
                except Exception as e:
                    logger.error(f"Error processing organization {org_id}: {str(e)}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting sharing organizations for {source_org.name}: {str(e)}")
            return []
    
    def _anonymize_data_dict(self, data: Dict[str, Any], anonymization_level: AnonymizationLevel) -> Dict[str, Any]:
        """
        Apply anonymization to a data dictionary based on anonymization level.
        
        Args:
            data: Data dictionary to anonymize
            anonymization_level: Level of anonymization to apply
            
        Returns:
            Dict: Anonymized data
        """
        anonymized_data = data.copy()
        
        # Apply anonymization to sensitive fields
        sensitive_fields = ['value', 'description', 'pattern']
        
        for field in sensitive_fields:
            if field in anonymized_data and anonymized_data[field]:
                try:
                    # Determine data type for anonymization strategy
                    data_type = self._determine_data_type(field, anonymized_data[field])
                    
                    # Convert string anonymization level to enum
                    if anonymization_level == 'none':
                        anon_level_enum = AnonymizationLevel.NONE
                    elif anonymization_level == 'minimal' or anonymization_level == 'partial':
                        anon_level_enum = AnonymizationLevel.MEDIUM
                    elif anonymization_level == 'full':
                        anon_level_enum = AnonymizationLevel.FULL
                    else:
                        anon_level_enum = AnonymizationLevel.MEDIUM  # Default
                    
                    # Apply anonymization
                    anonymized_value = self.anonymization_context.execute_anonymization(
                        str(anonymized_data[field]), 
                        data_type, 
                        anon_level_enum
                    )
                    
                    anonymized_data[field] = anonymized_value
                    
                except Exception as e:
                    logger.error(f"Error anonymizing field {field}: {str(e)}")
                    # On error, redact the field for security
                    anonymized_data[field] = "[REDACTED]"
        
        return anonymized_data
    
    def _determine_data_type(self, field_name: str, value: str) -> DataType:
        """
        Determine the data type for anonymization strategy selection.
        
        Args:
            field_name: Name of the field
            value: Value to analyze
            
        Returns:
            DataType: Detected data type
        """
        # Simple heuristics to determine data type
        if 'email' in field_name.lower() or '@' in value:
            return DataType.EMAIL
        elif 'ip' in field_name.lower() or self._looks_like_ip(value):
            return DataType.IP
        elif 'domain' in field_name.lower() or self._looks_like_domain(value):
            return DataType.DOMAIN
        elif 'url' in field_name.lower() or value.startswith(('http://', 'https://')):
            return DataType.URL
        else:
            return DataType.TEXT
    
    def _looks_like_ip(self, value: str) -> bool:
        """Check if value looks like an IP address."""
        import re
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        return bool(ip_pattern.match(value.strip()))
    
    def _looks_like_domain(self, value: str) -> bool:
        """Check if value looks like a domain name."""
        import re
        domain_pattern = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(domain_pattern.match(value.strip()))
    
    def _can_receive_classification(self, organization: Organization, 
                                  classification: str, anonymization_level: str) -> bool:
        """
        Check if organization can receive data with given classification and anonymization level.
        
        Args:
            organization: Target organization
            classification: TLP classification
            anonymization_level: Anonymization level being applied
            
        Returns:
            bool: True if organization can receive the data
        """
        # Simple TLP-based access control
        # In a real implementation, this would check organization clearance levels
        tlp_hierarchy = {
            'TLP:RED': 4,
            'TLP:AMBER': 3,
            'TLP:GREEN': 2,
            'TLP:WHITE': 1
        }
        
        # For now, allow all organizations to receive WHITE and GREEN data
        # More restrictive classifications would require additional checks
        classification_level = tlp_hierarchy.get(classification, 1)
        return classification_level <= 2  # Allow WHITE and GREEN