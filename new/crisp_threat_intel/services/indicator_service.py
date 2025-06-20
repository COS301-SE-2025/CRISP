from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
import logging

from ..domain.models import Indicator, ThreatFeed, User
from ..repositories.indicator_repository import IndicatorRepository
from ..factories.stix_object_creator import StixIndicatorCreator
from ..decorators.stix_decorators import StixObject, StixValidationDecorator

logger = logging.getLogger(__name__)


class IndicatorService:
    """
    Service class for managing indicators
    """
    
    def __init__(self):
        self.repository = IndicatorRepository()
        self.stix_creator = StixIndicatorCreator()
    
    def create_indicator(self, threat_feed: ThreatFeed, user: User, indicator_data: Dict[str, Any]) -> Indicator:
        """Create a new indicator"""
        try:
            with transaction.atomic():
                # Validate input data
                self._validate_indicator_data(indicator_data)
                
                # Create indicator
                indicator = Indicator(
                    name=indicator_data['name'],
                    description=indicator_data.get('description', ''),
                    pattern=indicator_data['pattern'],
                    labels=indicator_data.get('labels', ['malicious-activity']),
                    valid_from=indicator_data.get('valid_from', timezone.now()),
                    valid_until=indicator_data.get('valid_until'),
                    confidence=indicator_data.get('confidence', 0),
                    created=timezone.now(),
                    modified=timezone.now(),
                    created_by_ref=indicator_data.get('created_by_ref'),
                    external_references=indicator_data.get('external_references', []),
                    object_marking_refs=indicator_data.get('object_marking_refs', []),
                    threat_feed=threat_feed,
                    created_by=user
                )
                
                # Save to repository
                indicator = self.repository.save(indicator)
                
                logger.info(f"Created indicator '{indicator.name}' in feed '{threat_feed.name}'")
                return indicator
                
        except Exception as e:
            logger.error(f"Failed to create indicator: {e}")
            raise
    
    def get_indicator(self, indicator_id: str) -> Optional[Indicator]:
        """Get an indicator by ID"""
        return self.repository.get_by_id(indicator_id)
    
    def get_indicators_by_feed(self, threat_feed: ThreatFeed) -> List[Indicator]:
        """Get all indicators for a threat feed"""
        return self.repository.get_by_threat_feed(threat_feed)
    
    def update_indicator(self, indicator_id: str, update_data: Dict[str, Any], user: User) -> Indicator:
        """Update an existing indicator"""
        try:
            with transaction.atomic():
                indicator = self.repository.get_by_id(indicator_id)
                if not indicator:
                    raise ValueError(f"Indicator with ID {indicator_id} not found")
                
                # Update fields
                for field, value in update_data.items():
                    if hasattr(indicator, field) and field not in ['id', 'stix_id', 'created_at', 'created_by']:
                        setattr(indicator, field, value)
                
                indicator.modified = timezone.now()
                indicator = self.repository.save(indicator)
                
                logger.info(f"Updated indicator '{indicator.name}'")
                return indicator
                
        except Exception as e:
            logger.error(f"Failed to update indicator {indicator_id}: {e}")
            raise
    
    def delete_indicator(self, indicator_id: str, user: User) -> bool:
        """Delete an indicator"""
        try:
            with transaction.atomic():
                indicator = self.repository.get_by_id(indicator_id)
                if not indicator:
                    raise ValueError(f"Indicator with ID {indicator_id} not found")
                
                indicator_name = indicator.name
                success = self.repository.delete(indicator_id)
                
                if success:
                    logger.info(f"Deleted indicator '{indicator_name}' by user '{user.django_user.username}'")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to delete indicator {indicator_id}: {e}")
            raise
    
    def search_indicators(self, query_params: Dict[str, Any]) -> List[Indicator]:
        """Search indicators based on query parameters"""
        return self.repository.search(query_params)
    
    def validate_indicator_pattern(self, pattern: str, pattern_type: str = 'stix') -> Dict[str, Any]:
        """Validate a STIX pattern"""
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            if pattern_type.lower() != 'stix':
                validation_result['errors'].append(f"Unsupported pattern type: {pattern_type}")
                return validation_result
            
            # Basic STIX pattern validation
            if not pattern or not isinstance(pattern, str):
                validation_result['errors'].append("Pattern cannot be empty")
                return validation_result
            
            # Check for basic STIX pattern structure
            if not re.search(r'\[.*?\]', pattern):
                validation_result['errors'].append("Pattern should contain observation expressions in square brackets")
            
            # Check for valid observable types
            valid_observables = [
                'file', 'ipv4-addr', 'ipv6-addr', 'domain-name', 'url', 'email-addr',
                'email-message', 'windows-registry-key', 'user-account', 'process',
                'software', 'x509-certificate', 'network-traffic'
            ]
            
            pattern_lower = pattern.lower()
            found_observables = [obs for obs in valid_observables if f"{obs}:" in pattern_lower]
            
            if not found_observables:
                validation_result['warnings'].append("Pattern should reference at least one STIX observable type")
            
            # Check for common pattern syntax
            if ' = ' not in pattern and ' LIKE ' not in pattern and ' IN ' not in pattern:
                validation_result['warnings'].append("Pattern should contain comparison operators (=, LIKE, IN)")
            
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['errors'].append(f"Pattern validation error: {str(e)}")
        
        return validation_result
    
    def create_indicator_from_ioc(self, threat_feed: ThreatFeed, user: User, ioc_data: Dict[str, Any]) -> Indicator:
        """Create an indicator from IoC data"""
        try:
            # Convert IoC to STIX pattern
            pattern = self._convert_ioc_to_pattern(ioc_data)
            
            # Determine appropriate labels
            labels = self._determine_labels(ioc_data)
            
            indicator_data = {
                'name': ioc_data.get('name', f"IOC: {ioc_data.get('value', 'Unknown')}"),
                'description': ioc_data.get('description', ''),
                'pattern': pattern,
                'labels': labels,
                'confidence': ioc_data.get('confidence', 50),
                'valid_from': timezone.now(),
                'external_references': ioc_data.get('external_references', [])
            }
            
            return self.create_indicator(threat_feed, user, indicator_data)
            
        except Exception as e:
            logger.error(f"Failed to create indicator from IoC: {e}")
            raise
    
    def bulk_create_indicators(self, threat_feed: ThreatFeed, user: User, indicators_data: List[Dict[str, Any]]) -> List[Indicator]:
        """Create multiple indicators in bulk"""
        created_indicators = []
        errors = []
        
        try:
            with transaction.atomic():
                for i, indicator_data in enumerate(indicators_data):
                    try:
                        indicator = self.create_indicator(threat_feed, user, indicator_data)
                        created_indicators.append(indicator)
                    except Exception as e:
                        errors.append(f"Error creating indicator {i+1}: {str(e)}")
                
                if errors:
                    logger.warning(f"Bulk creation completed with {len(errors)} errors: {errors}")
                
                logger.info(f"Bulk created {len(created_indicators)} indicators in feed '{threat_feed.name}'")
                return created_indicators
                
        except Exception as e:
            logger.error(f"Failed to bulk create indicators: {e}")
            raise
    
    def get_indicator_statistics(self, threat_feed: ThreatFeed = None) -> Dict[str, Any]:
        """Get indicator statistics"""
        try:
            if threat_feed:
                indicators = self.repository.get_by_threat_feed(threat_feed)
                scope = f"feed '{threat_feed.name}'"
            else:
                indicators = self.repository.get_all()
                scope = "all feeds"
            
            # Calculate statistics
            total_count = len(indicators)
            
            # Group by labels
            label_counts = {}
            confidence_sum = 0
            confidence_count = 0
            
            for indicator in indicators:
                for label in indicator.labels:
                    label_counts[label] = label_counts.get(label, 0) + 1
                
                if indicator.confidence > 0:
                    confidence_sum += indicator.confidence
                    confidence_count += 1
            
            avg_confidence = confidence_sum / confidence_count if confidence_count > 0 else 0
            
            stats = {
                'scope': scope,
                'total_indicators': total_count,
                'label_distribution': label_counts,
                'average_confidence': round(avg_confidence, 2),
                'indicators_with_confidence': confidence_count
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get indicator statistics: {e}")
            raise
    
    def create_stix_object(self, indicator: Indicator) -> Dict[str, Any]:
        """Create STIX object from indicator"""
        try:
            stix_data = self.stix_creator.create_from_domain_model(indicator)
            
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
            logger.error(f"Failed to create STIX object for indicator {indicator.id}: {e}")
            raise
    
    def _validate_indicator_data(self, indicator_data: Dict[str, Any]):
        """Validate indicator data"""
        required_fields = ['name', 'pattern']
        
        for field in required_fields:
            if field not in indicator_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate pattern
        pattern_validation = self.validate_indicator_pattern(indicator_data['pattern'])
        if not pattern_validation['is_valid']:
            raise ValidationError(f"Invalid pattern: {pattern_validation['errors']}")
        
        # Validate labels
        labels = indicator_data.get('labels', [])
        if not isinstance(labels, list) or not labels:
            raise ValidationError("Indicator must have at least one label")
        
        # Validate confidence
        confidence = indicator_data.get('confidence', 0)
        if not isinstance(confidence, int) or confidence < 0 or confidence > 100:
            raise ValidationError("Confidence must be an integer between 0 and 100")
    
    def _convert_ioc_to_pattern(self, ioc_data: Dict[str, Any]) -> str:
        """Convert IoC data to STIX pattern"""
        ioc_type = ioc_data.get('type', '').lower()
        value = ioc_data.get('value', '')
        
        if not value:
            raise ValueError("IoC value is required")
        
        # Map IoC types to STIX patterns
        if ioc_type in ['ip', 'ipv4', 'ipv4-addr']:
            return f"[ipv4-addr:value = '{value}']"
        elif ioc_type in ['ipv6', 'ipv6-addr']:
            return f"[ipv6-addr:value = '{value}']"
        elif ioc_type in ['domain', 'domain-name']:
            return f"[domain-name:value = '{value}']"
        elif ioc_type in ['url']:
            return f"[url:value = '{value}']"
        elif ioc_type in ['email', 'email-addr']:
            return f"[email-addr:value = '{value}']"
        elif ioc_type in ['hash', 'md5']:
            return f"[file:hashes.MD5 = '{value}']"
        elif ioc_type in ['sha1']:
            return f"[file:hashes.'SHA-1' = '{value}']"
        elif ioc_type in ['sha256']:
            return f"[file:hashes.'SHA-256' = '{value}']"
        elif ioc_type in ['filename', 'file']:
            return f"[file:name = '{value}']"
        else:
            # Generic pattern for unknown types
            return f"[x-custom:value = '{value}']"
    
    def _determine_labels(self, ioc_data: Dict[str, Any]) -> List[str]:
        """Determine appropriate labels for an indicator based on IoC data"""
        labels = []
        
        # Add default label
        labels.append('malicious-activity')
        
        # Add type-specific labels
        ioc_type = ioc_data.get('type', '').lower()
        if ioc_type in ['ip', 'ipv4', 'ipv6']:
            labels.append('malicious-ip')
        elif ioc_type in ['domain', 'url']:
            labels.append('malicious-domain')
        elif ioc_type in ['email']:
            labels.append('malicious-email')
        elif ioc_type in ['hash', 'md5', 'sha1', 'sha256', 'filename']:
            labels.append('malicious-file')
        
        # Add context-based labels
        description = ioc_data.get('description', '').lower()
        if 'phishing' in description:
            labels.append('phishing')
        elif 'malware' in description:
            labels.append('malware')
        elif 'c2' in description or 'command' in description:
            labels.append('c2')
        elif 'exploit' in description:
            labels.append('exploit')
        
        return list(set(labels))  # Remove duplicates