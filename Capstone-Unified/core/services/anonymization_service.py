"""
Anonymization Service - Handles anonymization of threat intelligence data
"""
import logging
import hashlib
import re
import uuid
from typing import Dict, Any, List, Optional
from django.utils import timezone

from core.models.models import Indicator, TTPData

logger = logging.getLogger(__name__)


class AnonymizationService:
    """Service for anonymizing threat intelligence data"""

    def __init__(self):
        self.sensitive_patterns = [
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP addresses
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            r'\b(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?\b',  # URLs/Domains
        ]

    def anonymize_indicator(self, indicator: Indicator, anonymization_level: str) -> Dict[str, Any]:
        """
        Anonymize an indicator based on the specified level

        Args:
            indicator: Indicator to anonymize
            anonymization_level: Level of anonymization (none, minimal, partial, full)

        Returns:
            Anonymized indicator data
        """
        try:
            # Start with basic indicator data
            data = {
                'id': indicator.id,
                'type': indicator.type,
                'value': indicator.value,
                'description': getattr(indicator, 'description', ''),
                'confidence': getattr(indicator, 'confidence', 50),
                'first_seen': indicator.first_seen.isoformat() if hasattr(indicator, 'first_seen') and indicator.first_seen else None,
                'last_seen': indicator.last_seen.isoformat() if hasattr(indicator, 'last_seen') and indicator.last_seen else None,
                'created_at': indicator.created_at.isoformat(),
                'updated_at': indicator.updated_at.isoformat(),
                'is_anonymized': False,
                'anonymization_level': anonymization_level
            }

            if anonymization_level == 'none':
                return data

            elif anonymization_level == 'minimal':
                data = self._apply_minimal_anonymization(data, indicator)

            elif anonymization_level == 'partial':
                data = self._apply_partial_anonymization(data, indicator)

            elif anonymization_level == 'full':
                data = self._apply_full_anonymization(data, indicator)

            data['is_anonymized'] = True
            return data

        except Exception as e:
            logger.error(f"Error anonymizing indicator {indicator.id}: {str(e)}")
            raise

    def anonymize_ttp(self, ttp_data: Dict[str, Any], anonymization_level: str) -> Dict[str, Any]:
        """
        Anonymize TTP data based on the specified level

        Args:
            ttp_data: TTP data to anonymize
            anonymization_level: Level of anonymization (none, minimal, partial, full)

        Returns:
            Anonymized TTP data
        """
        try:
            if anonymization_level == 'none':
                return ttp_data

            anonymized_data = ttp_data.copy()
            anonymized_data['is_anonymized'] = True
            anonymized_data['anonymization_level'] = anonymization_level

            if anonymization_level == 'minimal':
                # Minimal anonymization - remove sensitive context
                anonymized_data = self._apply_minimal_ttp_anonymization(anonymized_data)

            elif anonymization_level == 'partial':
                # Partial anonymization - remove more identifying information
                anonymized_data = self._apply_partial_ttp_anonymization(anonymized_data)

            elif anonymization_level == 'full':
                # Full anonymization - keep only essential technique information
                anonymized_data = self._apply_full_ttp_anonymization(anonymized_data)

            return anonymized_data

        except Exception as e:
            logger.error(f"Error anonymizing TTP data: {str(e)}")
            raise

    def _apply_minimal_anonymization(self, data: Dict[str, Any], indicator: Indicator) -> Dict[str, Any]:
        """Apply minimal anonymization - remove only highly sensitive data"""
        # Remove specific attribution information
        if 'description' in data and data['description']:
            data['description'] = self._anonymize_text(data['description'], level='minimal')

        # Reduce confidence slightly
        if data.get('confidence', 0) > 80:
            data['confidence'] = 80

        # Generalize timestamps to day level
        if data.get('first_seen'):
            first_seen_date = data['first_seen'][:10]  # Keep only date part
            data['first_seen'] = first_seen_date + 'T00:00:00Z'

        if data.get('last_seen'):
            last_seen_date = data['last_seen'][:10]  # Keep only date part
            data['last_seen'] = last_seen_date + 'T00:00:00Z'

        return data

    def _apply_partial_anonymization(self, data: Dict[str, Any], indicator: Indicator) -> Dict[str, Any]:
        """Apply partial anonymization - remove moderately sensitive data"""
        # Apply minimal anonymization first
        data = self._apply_minimal_anonymization(data, indicator)

        # Further anonymize based on indicator type
        if indicator.type == 'ip':
            data['value'] = self._anonymize_ip_address(data['value'], level='partial')
        elif indicator.type == 'domain':
            data['value'] = self._anonymize_domain(data['value'], level='partial')
        elif indicator.type == 'url':
            data['value'] = self._anonymize_url(data['value'], level='partial')
        elif indicator.type in ['md5', 'sha1', 'sha256', 'file_hash']:
            # For hashes, we can provide a truncated version
            data['value'] = data['value'][:8] + '...' if len(data['value']) > 8 else data['value']

        # Further reduce confidence
        if data.get('confidence', 0) > 60:
            data['confidence'] = 60

        # More aggressive description anonymization
        if data.get('description'):
            data['description'] = self._anonymize_text(data['description'], level='partial')

        return data

    def _apply_full_anonymization(self, data: Dict[str, Any], indicator: Indicator) -> Dict[str, Any]:
        """Apply full anonymization - heavily anonymize the data"""
        # Keep only essential information
        anonymized_data = {
            'id': f"anon-{hashlib.md5(str(indicator.id).encode()).hexdigest()[:8]}",
            'type': indicator.type,
            'value': self._fully_anonymize_value(data['value'], indicator.type),
            'description': 'Anonymized threat indicator',
            'confidence': min(data.get('confidence', 50), 40),
            'first_seen': None,
            'last_seen': None,
            'created_at': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat(),
            'is_anonymized': True,
            'anonymization_level': 'full'
        }

        return anonymized_data

    def _apply_minimal_ttp_anonymization(self, ttp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply minimal TTP anonymization"""
        sensitive_fields = ['internal_context', 'source_attribution', 'campaign_details']
        for field in sensitive_fields:
            ttp_data.pop(field, None)

        # Anonymize description
        if 'description' in ttp_data and ttp_data['description']:
            ttp_data['description'] = self._anonymize_text(ttp_data['description'], level='minimal')

        return ttp_data

    def _apply_partial_ttp_anonymization(self, ttp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply partial TTP anonymization"""
        # Apply minimal first
        ttp_data = self._apply_minimal_ttp_anonymization(ttp_data)

        # Remove additional fields
        additional_fields = ['specific_targets', 'tool_details', 'infrastructure_details']
        for field in additional_fields:
            ttp_data.pop(field, None)

        # Further anonymize description
        if 'description' in ttp_data and ttp_data['description']:
            ttp_data['description'] = self._anonymize_text(ttp_data['description'], level='partial')

        return ttp_data

    def _apply_full_ttp_anonymization(self, ttp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply full TTP anonymization"""
        # Keep only essential MITRE ATT&CK information
        essential_fields = ['mitre_technique_id', 'mitre_tactic', 'name']
        anonymized_data = {field: ttp_data.get(field) for field in essential_fields if ttp_data.get(field)}

        # Add generic description
        anonymized_data['description'] = f"Technique {ttp_data.get('mitre_technique_id', 'unknown')} observed in threat intelligence"
        anonymized_data['is_anonymized'] = True
        anonymized_data['anonymization_level'] = 'full'

        return anonymized_data

    def _anonymize_text(self, text: str, level: str) -> str:
        """Anonymize text content based on level"""
        if not text:
            return text

        anonymized_text = text

        if level == 'minimal':
            # Replace specific IPs, emails, domains with placeholders
            for pattern in self.sensitive_patterns:
                anonymized_text = re.sub(pattern, '[REDACTED]', anonymized_text)

        elif level == 'partial':
            # More aggressive anonymization
            for pattern in self.sensitive_patterns:
                anonymized_text = re.sub(pattern, '[ANONYMIZED]', anonymized_text)

            # Remove specific organization names (simple approach)
            org_patterns = [
                r'\b[A-Z][a-z]+\s+(?:Corp|Inc|LLC|Ltd|Company)\b',
                r'\b[A-Z]{2,}\b'  # Acronyms that might be organization names
            ]
            for pattern in org_patterns:
                anonymized_text = re.sub(pattern, '[ORG]', anonymized_text)

        elif level == 'full':
            # Replace with generic description
            return 'Generic threat intelligence description'

        return anonymized_text

    def _anonymize_ip_address(self, ip: str, level: str) -> str:
        """Anonymize IP address based on level"""
        try:
            parts = ip.split('.')
            if len(parts) == 4:
                if level == 'partial':
                    # Keep first two octets
                    return f"{parts[0]}.{parts[1]}.xxx.xxx"
                elif level == 'full':
                    return "xxx.xxx.xxx.xxx"
        except:
            pass
        return "[IP_ADDRESS]"

    def _anonymize_domain(self, domain: str, level: str) -> str:
        """Anonymize domain based on level"""
        try:
            parts = domain.split('.')
            if len(parts) >= 2:
                if level == 'partial':
                    # Keep TLD and domain structure
                    return f"[DOMAIN].{parts[-1]}"
                elif level == 'full':
                    return "[DOMAIN]"
        except:
            pass
        return "[DOMAIN]"

    def _anonymize_url(self, url: str, level: str) -> str:
        """Anonymize URL based on level"""
        if level == 'partial':
            # Keep protocol and basic structure
            if url.startswith('http'):
                return re.sub(r'://[^/]+', '://[DOMAIN]', url)
            return '[URL]'
        elif level == 'full':
            return '[URL]'
        return url

    def _fully_anonymize_value(self, value: str, indicator_type: str) -> str:
        """Fully anonymize an indicator value"""
        if indicator_type == 'ip':
            return 'xxx.xxx.xxx.xxx'
        elif indicator_type == 'domain':
            return '[DOMAIN]'
        elif indicator_type == 'url':
            return '[URL]'
        elif indicator_type == 'email':
            return '[EMAIL]'
        elif indicator_type in ['md5', 'sha1', 'sha256', 'file_hash']:
            return f"[{indicator_type.upper()}_HASH]"
        else:
            return f"[{indicator_type.upper()}]"

    def create_anonymization_mapping(self, original_value: str, anonymized_value: str,
                                   mapping_type: str = 'indicator') -> str:
        """
        Create a mapping ID for tracking anonymized values

        Args:
            original_value: Original value
            anonymized_value: Anonymized value
            mapping_type: Type of mapping (indicator, ttp, etc.)

        Returns:
            Mapping ID for tracking purposes
        """
        mapping_id = hashlib.sha256(f"{mapping_type}:{original_value}".encode()).hexdigest()[:16]

        # In a real implementation, you might store this mapping in a secure database
        # For audit purposes while maintaining anonymization
        logger.debug(f"Created anonymization mapping {mapping_id} for {mapping_type}")

        return mapping_id

    def get_anonymization_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of what anonymization was applied

        Args:
            data: Anonymized data

        Returns:
            Summary of anonymization applied
        """
        return {
            'is_anonymized': data.get('is_anonymized', False),
            'anonymization_level': data.get('anonymization_level', 'none'),
            'anonymization_timestamp': timezone.now().isoformat(),
            'fields_modified': self._get_modified_fields(data),
            'data_retention_policy': 'Applied according to trust relationship'
        }

    def _get_modified_fields(self, data: Dict[str, Any]) -> List[str]:
        """Get list of fields that were modified during anonymization"""
        modified_fields = []

        if data.get('is_anonymized', False):
            # These fields are typically modified during anonymization
            potential_fields = ['value', 'description', 'confidence', 'first_seen', 'last_seen']

            for field in potential_fields:
                if field in data:
                    # Check if the value contains anonymization markers
                    value_str = str(data[field])
                    if any(marker in value_str for marker in ['[REDACTED]', '[ANONYMIZED]', '[DOMAIN]', 'xxx']):
                        modified_fields.append(field)

        return modified_fields