from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Set, Optional, Union
import re
import uuid
import ipaddress
import hashlib
import copy
import json # Ensure json is imported
from django.conf import settings
import logging

# Import anonymization algorithms
from .algorithms import (
    anonymize_ip_address,
    anonymize_domain_name,
    anonymize_email_address,
    anonymize_url,
    anonymize_file_hash,
    anonymize_registry_key,
    anonymize_stix_pattern,
    redact_text_field
)

logger = logging.getLogger(__name__)

class AnonymizationStrategy(ABC):
    """
    Abstract base class for anonymization strategies (Strategy Pattern - SRS 7.3.3).
    """
    # Fields considered highly sensitive and their default anonymization function if not overridden
    # The 'level' passed to these functions will be determined by the strategy (e.g., 'partial', 'full')
    SENSITIVE_FIELD_HANDLERS = {
        # General PII / Identifiers
        "name": lambda val, level: f"Anonymized Object ({str(uuid.uuid4())[:8]})" if level == 'full' else f"Redacted Name ({hashlib.md5(str(val).encode()).hexdigest()[:6]})",
        "description": lambda val, level: redact_text_field(val, level),
        "contact_information": lambda val, level: "[CONTACT_INFO_REDACTED]", # Always fully redact
        "aliases": lambda val_list, level: [f"Alias-{i+1}" for i in range(len(val_list))] if isinstance(val_list, list) else "[REDACTED_ALIAS]",

        # Network Observables / Patterns
        "pattern": lambda val, level: anonymize_stix_pattern(val, level), # For indicator patterns
        "src_ip": lambda val, level: anonymize_ip_address(val, level), # hypothetical field
        "dest_ip": lambda val, level: anonymize_ip_address(val, level), # hypothetical field
        "domain_name": lambda val, level: anonymize_domain_name(val, level), # hypothetical field
        "url": lambda val, level: anonymize_url(val, level), # hypothetical field
        "email_address": lambda val, level: anonymize_email_address(val, level), # hypothetical field

        # File Observables
        "file_hash_md5": lambda val, level: anonymize_file_hash(val, "MD5", level), # hypothetical
        "file_hash_sha256": lambda val, level: anonymize_file_hash(val, "SHA256", level), # hypothetical

        # STIX Specific
        "created_by_ref": lambda val, level: f"identity--{hashlib.sha256(str(val).encode()).hexdigest()[:32]}" if level == 'full' else val, # Keep if partial, hash if full
        "object_marking_refs": lambda val_list, level: val_list, # Markings are usually kept or filtered by policy, not anonymized here
        "external_references": lambda val_list, level: AnonymizationStrategy._anonymize_external_references_list(val_list, level),

        # Malware Specific
        "sample_refs": lambda val_list, level: [f"sample--{hashlib.sha256(str(ref).encode()).hexdigest()[:32]}" for ref in val_list] if isinstance(val_list, list) else "[REDACTED_SAMPLE_REFS]",

        # Threat Actor Specific
        "goals": lambda val_list, level: [redact_text_field(goal, level) for goal in val_list] if isinstance(val_list, list) else redact_text_field(str(val_list), level),
        "primary_motivation": lambda val, level: redact_text_field(val, level),
        "secondary_motivations": lambda val_list, level: [redact_text_field(motive, level) for motive in val_list] if isinstance(val_list, list) else redact_text_field(str(val_list), level),
        "resource_level": lambda val, level: val, # Often kept for context
        "sophistication": lambda val, level: val, # Often kept for context
    }


    @staticmethod
    def _anonymize_external_references_list(references: List[Dict[str, Any]], level: str) -> List[Dict[str, Any]]:
        anonymized_refs = []
        if not isinstance(references, list):
            return ["[INVALID_EXTERNAL_REFERENCES_FORMAT]"]

        for ref in references:
            if not isinstance(ref, dict):
                anonymized_refs.append({"anonymized_reference_item": "[INVALID_FORMAT]"})
                continue

            anon_ref = copy.deepcopy(ref)
            if "url" in anon_ref:
                anon_ref["url"] = anonymize_url(anon_ref["url"], level)
            if "description" in anon_ref:
                anon_ref["description"] = redact_text_field(anon_ref["description"], level)
            if "external_id" in anon_ref and level == 'full': # e.g. MITRE IDs are usually kept
                pass # anon_ref["external_id"] = f"ANON_ID_{hashlib.md5(str(anon_ref['external_id']).encode()).hexdigest()[:6]}"
            if "source_name" in anon_ref: # Source name can be sensitive
                anon_ref["source_name"] = redact_text_field(anon_ref["source_name"], level if level == 'full' else 'partial') # More aggressive for source_name
            anonymized_refs.append(anon_ref)
        return anonymized_refs


    @abstractmethod
    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.5, strategy_level: str = 'partial') -> Dict[str, Any]:
        """
        Anonymize a STIX object.
        Args:
            stix_input: Original STIX object (dict or JSON string).
            trust_level: Trust level (0.0 to 1.0). Not directly used by all strategies but available.
            strategy_level: The effective anonymization intensity ('none', 'partial', 'full') for this call.
        Returns:
            Anonymized STIX object as a dictionary.
        """
        pass

    def get_effectiveness_score(self) -> float:
        """Returns analytical value preservation score (0.0 to 1.0)."""
        raise NotImplementedError

    def _get_stix_dict(self, stix_input: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """Converts STIX input to a dictionary if it's a JSON string."""
        if isinstance(stix_input, str):
            try:
                return json.loads(stix_input)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse STIX JSON string: {e}. Input (first 100 chars): {stix_input[:100]}")
                raise ValueError(f"Invalid STIX JSON input: {e}")
        elif isinstance(stix_input, dict):
            return stix_input
        else:
            raise TypeError(f"STIX input must be a dictionary or JSON string, got {type(stix_input)}.")

    def _anonymize_field_value(self, field_name: str, original_value: Any, stix_type: str, strategy_level: str) -> Any:
        """Anonymizes a single field's value based on its name and the strategy level."""
        handler = self.SENSITIVE_FIELD_HANDLERS.get(field_name)
        if handler:
            return handler(original_value, strategy_level)

        # Default handling for common STIX types if no specific handler
        if isinstance(original_value, str):
            return redact_text_field(original_value, strategy_level)
        elif isinstance(original_value, list) and strategy_level == 'full':
            return [f"[ANON_LIST_ITEM_{i+1}]" for i in range(len(original_value))]
        return original_value # Return as is if no specific rule and not simple text


class NoAnonymizationStrategy(AnonymizationStrategy):
    """Strategy that performs no anonymization."""
    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 1.0, strategy_level: str = 'none') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        return copy.deepcopy(stix_object_dict)

    def get_effectiveness_score(self) -> float:
        return 1.0  # Preserves 100% analytical value


class PartialAnonymizationStrategy(AnonymizationStrategy):
    """Strategy that selectively anonymizes fields."""
    # Fields to target for partial anonymization. Others might be kept as is.
    PARTIAL_ANON_TARGET_FIELDS = [
        "name", "description", "pattern", "created_by_ref", "external_references",
        "contact_information", "aliases", "sample_refs", "goals",
        "primary_motivation", "secondary_motivations"
        # Note: IP addresses, domains, URLs, emails within 'pattern' or specific observable fields
        # are handled by the anonymize_stix_pattern or specific SENSITIVE_FIELD_HANDLERS.
    ]

    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.5, strategy_level: str = 'partial') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        anonymized_stix_object = copy.deepcopy(stix_object_dict)
        stix_type = anonymized_stix_object.get('type', 'unknown')

        for field_name, original_value in anonymized_stix_object.items():
            if field_name in self.PARTIAL_ANON_TARGET_FIELDS:
                anonymized_stix_object[field_name] = self._anonymize_field_value(
                    field_name, original_value, stix_type, strategy_level='partial' # Force 'partial' level for these
                )
        return anonymized_stix_object

    def get_effectiveness_score(self) -> float:
        # SEC1.7 target. Actual score depends on precise field handling.
        return 0.95


class FullAnonymizationStrategy(AnonymizationStrategy):
    """Strategy that aggressively anonymizes most fields."""
    # Fields to completely remove or heavily obfuscate in full anonymization.
    # Core STIX structural fields like id, type, spec_version, created, modified are usually preserved.
    FULL_ANON_REPLACE_FIELDS = [
        "name", "description", "created_by_ref", "external_references",
        "object_marking_refs", "granular_markings", "labels", "confidence",
        "contact_information", "aliases", "roles", "goals", "sophistication",
        "resource_level", "primary_motivation", "secondary_motivations",
        "first_seen", "last_seen", "malware_types", "architecture_execution_envs",
        "implementation_languages", "capabilities", "sample_refs",
        # Relationship specific (source_ref, target_ref are structurally important but content can be hinted)
        "source_ref", "target_ref", "relationship_type" # these are preserved structurally but target content is anonymized
    ]


    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.0, strategy_level: str = 'full') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        anonymized_stix_object = {} # Start fresh to only include allowed/anonymized fields
        stix_type = stix_object_dict.get('type', 'unknown')

        # Preserve essential STIX structural fields
        for essential_field in ['id', 'type', 'spec_version', 'created', 'modified']:
            if essential_field in stix_object_dict:
                anonymized_stix_object[essential_field] = stix_object_dict[essential_field]
            else: # Should not happen for valid STIX
                 anonymized_stix_object[essential_field] = f"[MISSING_ESSENTIAL_{essential_field.upper()}]"


        # Handle type-specific structural fields that need to exist but with anonymized content
        if stix_type == "indicator":
            anonymized_stix_object["pattern_type"] = stix_object_dict.get("pattern_type", "stix") # Keep pattern_type
            anonymized_stix_object["pattern"] = self._anonymize_field_value("pattern", stix_object_dict.get("pattern","[PATTERN_UNAVAILABLE]"), stix_type, strategy_level='full')
            anonymized_stix_object["valid_from"] = stix_object_dict.get("valid_from", anonymized_stix_object["created"]) # Default valid_from
            if "valid_until" in stix_object_dict: # Optional field
                 anonymized_stix_object["valid_until"] = stix_object_dict["valid_until"]

        elif stix_type == "malware":
            anonymized_stix_object["is_family"] = stix_object_dict.get("is_family", False)

        elif stix_type == "identity":
            anonymized_stix_object["identity_class"] = stix_object_dict.get("identity_class", "unknown")
            anonymized_stix_object["name"] = self._anonymize_field_value("name", stix_object_dict.get("name", "Unknown Identity"), stix_type, strategy_level='full')


        elif stix_type == "relationship":
            anonymized_stix_object["relationship_type"] = stix_object_dict.get("relationship_type", "unknown")
            # Anonymize refs by creating placeholder STIX IDs based on original type + hash
            src_ref = stix_object_dict.get("source_ref", "unknown--00000000-0000-0000-0000-000000000000")
            tgt_ref = stix_object_dict.get("target_ref", "unknown--00000000-0000-0000-0000-000000000000")
            anonymized_stix_object["source_ref"] = f"{src_ref.split('--')[0]}--{hashlib.sha256(src_ref.encode()).hexdigest()[:32]}"
            anonymized_stix_object["target_ref"] = f"{tgt_ref.split('--')[0]}--{hashlib.sha256(tgt_ref.encode()).hexdigest()[:32]}"


        # For all other fields in the original object, if they are in FULL_ANON_REPLACE_FIELDS,
        # apply full anonymization. If not, they are omitted unless explicitly preserved above.
        for field_name, original_value in stix_object_dict.items():
            if field_name not in anonymized_stix_object: # If not already handled (e.g. essential or type-specific structural)
                 anonymized_stix_object[field_name] = self._anonymize_field_value(
                    field_name, original_value, stix_type, strategy_level='full'
                )
        return anonymized_stix_object

    def get_effectiveness_score(self) -> float:
        # Full anonymization significantly reduces detail, adjust score accordingly
        return 0.80


class AnonymizationStrategyFactory:
    """Factory for creating anonymization strategies."""
    _strategies = {
        'none': NoAnonymizationStrategy,
        'partial': PartialAnonymizationStrategy,
        'full': FullAnonymizationStrategy,
    }

    @classmethod
    def get_strategy(cls, strategy_name: str) -> AnonymizationStrategy:
        """Gets an instance of the specified anonymization strategy."""
        strategy_name_lower = strategy_name.lower()
        strategy_class = cls._strategies.get(strategy_name_lower)
        if not strategy_class:
            logger.warning(f"Unknown anonymization strategy requested: '{strategy_name}'. Falling back to default.")
            return cls.get_default_strategy()
        return strategy_class()

    @classmethod
    def get_default_strategy(cls) -> AnonymizationStrategy:
        """Gets the default anonymization strategy from settings."""
        # Ensure ANONYMIZATION_SETTINGS and DEFAULT_STRATEGY are in django settings
        # (e.g., settings.ANONYMIZATION_SETTINGS = {'DEFAULT_STRATEGY': 'partial'})
        default_strategy_name = getattr(settings, 'ANONYMIZATION_SETTINGS', {}).get('DEFAULT_STRATEGY', 'partial')
        return cls.get_strategy(default_strategy_name)

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """Registers a new anonymization strategy."""
        if not issubclass(strategy_class, AnonymizationStrategy):
            raise ValueError("Strategy class must inherit from AnonymizationStrategy.")
        cls._strategies[name.lower()] = strategy_class