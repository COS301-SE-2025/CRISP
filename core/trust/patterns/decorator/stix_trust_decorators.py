from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import hashlib
import logging
from datetime import datetime
from django.utils import timezone

from ..factory.stix_trust_factory import StixTrustObject
from ..strategy.access_control_strategies import AnonymizationContext

logger = logging.getLogger(__name__)


class StixTrustObjectComponent(ABC):
    """
    Abstract component interface for STIX trust objects.
    Implements the Component interface from the Decorator pattern.
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        pass
    
    @abstractmethod
    def to_json(self) -> str:
        """Convert to JSON representation."""
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """Get the STIX object type."""
        pass
    
    @abstractmethod
    def get_id(self) -> str:
        """Get the STIX object ID."""
        pass


class ConcreteStixTrustComponent(StixTrustObjectComponent):
    """
    Concrete implementation of STIX trust object component.
    Wraps StixTrustObject to provide decorator interface.
    """
    
    def __init__(self, stix_object: StixTrustObject):
        self._stix_object = stix_object
    
    def to_dict(self) -> Dict[str, Any]:
        return self._stix_object.to_dict()
    
    def to_json(self) -> str:
        return self._stix_object.to_json()
    
    def get_type(self) -> str:
        return self._stix_object.type
    
    def get_id(self) -> str:
        return self._stix_object.id
    
    def get_stix_object(self) -> StixTrustObject:
        """Get the underlying STIX object."""
        return self._stix_object


class StixTrustDecorator(StixTrustObjectComponent):
    """
    Abstract base decorator for STIX trust objects.
    Implements the Decorator pattern from CRISP domain model.
    """
    
    def __init__(self, component: StixTrustObjectComponent):
        self._component = component
    
    def to_dict(self) -> Dict[str, Any]:
        return self._component.to_dict()
    
    def to_json(self) -> str:
        return self._component.to_json()
    
    def get_type(self) -> str:
        return self._component.get_type()
    
    def get_id(self) -> str:
        return self._component.get_id()


class StixTrustValidationDecorator(StixTrustDecorator):
    """
    Decorator that adds validation capabilities to STIX trust objects.
    Ensures objects conform to STIX specifications and trust requirements.
    """
    
    def __init__(self, component: StixTrustObjectComponent, strict_mode: bool = True):
        super().__init__(component)
        self.strict_mode = strict_mode
        self._validation_errors = []
        self._validation_warnings = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Return validated dictionary representation."""
        data = super().to_dict()
        
        # Validate the object
        is_valid, errors, warnings = self.validate(data)
        
        if not is_valid and self.strict_mode:
            raise ValueError(f"STIX trust object validation failed: {errors}")
        
        # Add validation metadata
        data["x_crisp_validation"] = {
            "validated": True,
            "validation_timestamp": timezone.now().isoformat(),
            "is_valid": is_valid,
            "strict_mode": self.strict_mode,
            "errors": errors,
            "warnings": warnings
        }
        
        if not is_valid:
            logger.warning(f"STIX trust object {self.get_id()} has validation issues: {errors}")
        
        return data
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str], List[str]]:
        """
        Validate STIX trust object against specifications.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Required STIX fields validation
        required_fields = ["type", "spec_version", "id", "created", "modified"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # STIX ID format validation
        if "id" in data:
            stix_id = data["id"]
            if "--" not in stix_id:
                errors.append(f"Invalid STIX ID format: {stix_id}")
            else:
                id_type, id_uuid = stix_id.split("--", 1)
                if id_type != data.get("type"):
                    errors.append(f"STIX ID type mismatch: {id_type} vs {data.get('type')}")
        
        # Spec version validation
        if "spec_version" in data:
            if data["spec_version"] not in ["2.0", "2.1"]:
                warnings.append(f"Unusual STIX spec version: {data['spec_version']}")
        
        # Timestamp validation
        for timestamp_field in ["created", "modified"]:
            if timestamp_field in data:
                try:
                    # Try to parse the timestamp
                    datetime.fromisoformat(data[timestamp_field].replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"Invalid timestamp format for {timestamp_field}: {data[timestamp_field]}")
        
        # Trust-specific validations
        self._validate_trust_extensions(data, errors, warnings)
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    def _validate_trust_extensions(self, data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate trust-specific extension fields."""
        
        # Validate trust relationship extension
        if "x_crisp_trust_relationship" in data:
            trust_ext = data["x_crisp_trust_relationship"]
            
            required_trust_fields = [
                "source_organization", "target_organization", "trust_level",
                "relationship_type", "status", "anonymization_level", "access_level"
            ]
            
            for field in required_trust_fields:
                if field not in trust_ext:
                    errors.append(f"Missing required trust relationship field: {field}")
            
            # Validate enum values
            if "relationship_type" in trust_ext:
                valid_types = ["bilateral", "community", "hierarchical", "federation"]
                if trust_ext["relationship_type"] not in valid_types:
                    errors.append(f"Invalid relationship_type: {trust_ext['relationship_type']}")
            
            if "status" in trust_ext:
                valid_statuses = ["pending", "active", "suspended", "revoked", "expired"]
                if trust_ext["status"] not in valid_statuses:
                    errors.append(f"Invalid status: {trust_ext['status']}")
        
        # Validate trust group extension
        if "x_crisp_trust_group" in data:
            group_ext = data["x_crisp_trust_group"]
            
            required_group_fields = ["group_type", "is_public", "requires_approval", "is_active"]
            
            for field in required_group_fields:
                if field not in group_ext:
                    errors.append(f"Missing required trust group field: {field}")
            
            # Validate member count consistency
            if "member_count" in group_ext and "members" in group_ext:
                actual_count = len(group_ext["members"])
                declared_count = group_ext["member_count"]
                if actual_count != declared_count:
                    warnings.append(f"Member count mismatch: declared={declared_count}, actual={actual_count}")
        
        # Validate trust level extension
        if "x_crisp_trust_level" in data:
            level_ext = data["x_crisp_trust_level"]
            
            required_level_fields = ["level", "numerical_value", "default_anonymization_level", "default_access_level"]
            
            for field in required_level_fields:
                if field not in level_ext:
                    errors.append(f"Missing required trust level field: {field}")
            
            # Validate numerical value range
            if "numerical_value" in level_ext:
                value = level_ext["numerical_value"]
                if not isinstance(value, (int, float)) or value < 0 or value > 100:
                    errors.append(f"Invalid numerical_value: must be between 0-100, got {value}")
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors from last validation."""
        return self._validation_errors.copy()
    
    def get_validation_warnings(self) -> List[str]:
        """Get validation warnings from last validation."""
        return self._validation_warnings.copy()


class StixTrustAnonymizationDecorator(StixTrustDecorator):
    """
    Decorator that adds anonymization capabilities to STIX trust objects.
    Applies trust-based anonymization strategies.
    """
    
    def __init__(self, component: StixTrustObjectComponent, 
                 anonymization_context: Optional[AnonymizationContext] = None,
                 anonymization_level: str = "partial"):
        super().__init__(component)
        self.anonymization_context = anonymization_context
        self.anonymization_level = anonymization_level
    
    def to_dict(self) -> Dict[str, Any]:
        """Return anonymized dictionary representation."""
        data = super().to_dict()
        
        # Apply anonymization
        anonymized_data = self._apply_anonymization(data)
        
        # Add anonymization metadata
        anonymized_data["x_crisp_anonymization"] = {
            "anonymized": True,
            "anonymization_timestamp": timezone.now().isoformat(),
            "anonymization_level": self.anonymization_level,
            "original_id_hash": hashlib.sha256(data.get("id", "").encode()).hexdigest()[:16]
        }
        
        return anonymized_data
    
    def _apply_anonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply anonymization to the STIX object data."""
        anonymized_data = data.copy()
        
        if self.anonymization_level == "none":
            return anonymized_data
        
        # Get anonymization strategy from context
        if self.anonymization_context:
            strategy = self.anonymization_context.get_strategy_for_trust_level(self.anonymization_level)
            anonymized_data = strategy.anonymize(anonymized_data, {
                'trust_relationship': self.anonymization_context.trust_relationship,
                'sharing_policy': getattr(self.anonymization_context, 'sharing_policy', {})
            })
        else:
            # Apply default anonymization
            anonymized_data = self._apply_default_anonymization(anonymized_data)
        
        return anonymized_data
    
    def _apply_default_anonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default anonymization rules."""
        anonymized_data = data.copy()
        
        if self.anonymization_level in ["minimal", "partial", "full"]:
            # Remove or anonymize created_by_ref
            if "created_by_ref" in anonymized_data:
                anonymized_data["created_by_ref"] = self._anonymize_identity_ref(
                    anonymized_data["created_by_ref"]
                )
            
            # Anonymize trust extensions based on level
            self._anonymize_trust_extensions(anonymized_data)
        
        return anonymized_data
    
    def _anonymize_identity_ref(self, identity_ref: str) -> str:
        """Anonymize identity reference."""
        return f"identity--{hashlib.sha256(identity_ref.encode()).hexdigest()[:8]}"
    
    def _anonymize_trust_extensions(self, data: Dict[str, Any]):
        """Anonymize trust-specific extension fields."""
        
        # Anonymize trust relationship data
        if "x_crisp_trust_relationship" in data:
            trust_ext = data["x_crisp_trust_relationship"]
            
            if self.anonymization_level in ["partial", "full"]:
                # Hash organization IDs
                if "source_organization" in trust_ext:
                    trust_ext["source_organization"] = self._hash_organization_id(
                        trust_ext["source_organization"]
                    )
                if "target_organization" in trust_ext:
                    trust_ext["target_organization"] = self._hash_organization_id(
                        trust_ext["target_organization"]
                    )
            
            if self.anonymization_level == "full":
                # Remove detailed sharing preferences and metadata
                trust_ext.pop("sharing_preferences", None)
                trust_ext.pop("metadata", None)
                trust_ext.pop("approved_by_source_user", None)
                trust_ext.pop("approved_by_target_user", None)
        
        # Anonymize trust group data
        if "x_crisp_trust_group" in data:
            group_ext = data["x_crisp_trust_group"]
            
            if self.anonymization_level in ["partial", "full"]:
                # Anonymize member details
                if "members" in group_ext:
                    for member in group_ext["members"]:
                        if "organization" in member:
                            member["organization"] = self._hash_organization_id(
                                member["organization"]
                            )
                
                # Anonymize administrators
                if "administrators" in group_ext:
                    group_ext["administrators"] = [
                        self._hash_organization_id(admin_id) 
                        for admin_id in group_ext["administrators"]
                    ]
            
            if self.anonymization_level == "full":
                # Remove detailed policies
                group_ext.pop("group_policies", None)
                group_ext.pop("created_by", None)
    
    def _hash_organization_id(self, org_id: str) -> str:
        """Hash organization ID for anonymization."""
        return f"org-{hashlib.sha256(org_id.encode()).hexdigest()[:12]}"


class StixTrustEnrichmentDecorator(StixTrustDecorator):
    """
    Decorator that adds enrichment capabilities to STIX trust objects.
    Adds additional context and metadata.
    """
    
    def __init__(self, component: StixTrustObjectComponent, 
                 enrichment_config: Optional[Dict[str, Any]] = None):
        super().__init__(component)
        self.enrichment_config = enrichment_config or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Return enriched dictionary representation."""
        data = super().to_dict()
        
        # Apply enrichment
        enriched_data = self._apply_enrichment(data)
        
        # Add enrichment metadata
        enriched_data["x_crisp_enrichment"] = {
            "enriched": True,
            "enrichment_timestamp": timezone.now().isoformat(),
            "enrichment_version": "1.0",
            "enrichment_sources": self._get_enrichment_sources()
        }
        
        return enriched_data
    
    def _apply_enrichment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply enrichment to the STIX object data."""
        enriched_data = data.copy()
        
        # Add confidence scores
        if self.enrichment_config.get("add_confidence", True):
            enriched_data["confidence"] = self._calculate_confidence(data)
        
        # Add threat level assessment
        if self.enrichment_config.get("add_threat_level", True):
            enriched_data["x_crisp_threat_level"] = self._assess_threat_level(data)
        
        # Add trust metrics
        if self.enrichment_config.get("add_trust_metrics", True):
            enriched_data["x_crisp_trust_metrics"] = self._calculate_trust_metrics(data)
        
        # Add context information
        if self.enrichment_config.get("add_context", True):
            enriched_data["x_crisp_context"] = self._add_context_information(data)
        
        return enriched_data
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> int:
        """Calculate confidence score for the trust relationship."""
        base_confidence = 50
        
        # Increase confidence based on trust level
        if "x_crisp_trust_relationship" in data:
            trust_ext = data["x_crisp_trust_relationship"]
            trust_level = trust_ext.get("trust_level", {})
            numerical_value = trust_level.get("numerical_value", 0)
            base_confidence += int(numerical_value * 0.3)  # Max 30 points from trust level
        
        # Increase confidence if bilateral and fully approved
        if "x_crisp_trust_relationship" in data:
            trust_ext = data["x_crisp_trust_relationship"]
            if trust_ext.get("is_bilateral") and trust_ext.get("approved_by_source") and trust_ext.get("approved_by_target"):
                base_confidence += 20
        
        return min(base_confidence, 100)
    
    def _assess_threat_level(self, data: Dict[str, Any]) -> str:
        """Assess threat level based on trust relationship characteristics."""
        if "x_crisp_trust_relationship" in data:
            trust_ext = data["x_crisp_trust_relationship"]
            trust_level = trust_ext.get("trust_level", {}).get("level", "none")
            
            threat_mapping = {
                "complete": "very-low",
                "high": "low",
                "medium": "medium",
                "low": "high",
                "none": "very-high"
            }
            
            return threat_mapping.get(trust_level, "medium")
        
        return "medium"
    
    def _calculate_trust_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate trust-related metrics."""
        metrics = {
            "trust_score": 0.0,
            "relationship_age_days": 0,
            "stability_score": 0.0
        }
        
        if "x_crisp_trust_relationship" in data:
            trust_ext = data["x_crisp_trust_relationship"]
            
            # Calculate trust score
            trust_level = trust_ext.get("trust_level", {})
            numerical_value = trust_level.get("numerical_value", 0)
            metrics["trust_score"] = numerical_value / 100.0
            
            # Calculate relationship age
            if "created" in data:
                try:
                    created_dt = datetime.fromisoformat(data["created"].replace('Z', '+00:00'))
                    age = timezone.now() - created_dt.replace(tzinfo=timezone.utc)
                    metrics["relationship_age_days"] = age.days
                except ValueError:
                    pass
            
            # Calculate stability score based on status and approvals
            stability = 0.0
            if trust_ext.get("status") == "active":
                stability += 0.4
            if trust_ext.get("approved_by_source"):
                stability += 0.3
            if trust_ext.get("approved_by_target"):
                stability += 0.3
            
            metrics["stability_score"] = stability
        
        return metrics
    
    def _add_context_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add contextual information about the trust relationship."""
        context = {
            "sharing_context": "trust-based-intelligence-sharing",
            "platform": "CRISP",
            "trust_framework_version": "1.0"
        }
        
        # Add relationship context
        if "x_crisp_trust_relationship" in data:
            trust_ext = data["x_crisp_trust_relationship"]
            context["relationship_context"] = {
                "type": trust_ext.get("relationship_type", "unknown"),
                "bilateral": trust_ext.get("is_bilateral", False),
                "community_based": trust_ext.get("relationship_type") == "community"
            }
        
        # Add group context
        if "x_crisp_trust_group" in data:
            group_ext = data["x_crisp_trust_group"]
            context["group_context"] = {
                "community_type": group_ext.get("group_type", "unknown"),
                "public_group": group_ext.get("is_public", False),
                "member_count": group_ext.get("member_count", 0)
            }
        
        return context
    
    def _get_enrichment_sources(self) -> List[str]:
        """Get list of enrichment sources used."""
        sources = ["CRISP Trust Management System"]
        
        if self.enrichment_config.get("add_external_sources", False):
            sources.extend([
                "Trust Level Assessment Engine",
                "Threat Intelligence Context Provider",
                "Relationship Analytics Service"
            ])
        
        return sources


class StixTrustTaxiiExportDecorator(StixTrustDecorator):
    """
    Decorator that adds TAXII export capabilities to STIX trust objects.
    Prepares objects for sharing via TAXII servers.
    """
    
    def __init__(self, component: StixTrustObjectComponent, 
                 collection_id: Optional[str] = None,
                 export_config: Optional[Dict[str, Any]] = None):
        super().__init__(component)
        self.collection_id = collection_id
        self.export_config = export_config or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Return TAXII-ready dictionary representation."""
        data = super().to_dict()
        
        # Apply TAXII export preparation
        taxii_data = self._prepare_for_taxii_export(data)
        
        # Add TAXII export metadata
        taxii_data["x_crisp_taxii_export"] = {
            "export_ready": True,
            "export_timestamp": timezone.now().isoformat(),
            "collection_id": self.collection_id,
            "taxii_version": "2.1",
            "export_format": "STIX 2.1"
        }
        
        return taxii_data
    
    def _prepare_for_taxii_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare STIX object for TAXII export."""
        export_data = data.copy()
        
        # Ensure TAXII-required fields
        self._ensure_taxii_required_fields(export_data)
        
        # Apply export filtering
        if self.export_config.get("filter_sensitive_fields", True):
            export_data = self._filter_sensitive_fields(export_data)
        
        # Add TAXII-specific markings
        if self.export_config.get("add_taxii_markings", True):
            export_data = self._add_taxii_markings(export_data)
        
        # Validate TAXII compliance
        if self.export_config.get("validate_taxii_compliance", True):
            self._validate_taxii_compliance(export_data)
        
        return export_data
    
    def _ensure_taxii_required_fields(self, data: Dict[str, Any]):
        """Ensure all TAXII-required fields are present."""
        # TAXII requires these fields for proper collection management
        if "labels" not in data:
            data["labels"] = ["trust-intelligence"]
        
        # Ensure proper STIX version
        if "spec_version" not in data:
            data["spec_version"] = "2.1"
        
        # Add object marking refs if not present
        if "object_marking_refs" not in data and self.export_config.get("require_markings", False):
            data["object_marking_refs"] = ["marking-definition--f88d31f6-486f-44da-b317-01333bde0b82"]  # TLP:WHITE
    
    def _filter_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out sensitive fields that shouldn't be shared via TAXII."""
        filtered_data = data.copy()
        
        # Remove internal system fields
        internal_fields = [
            "x_crisp_validation",
            "x_crisp_internal_metadata",
            "x_crisp_system_fields"
        ]
        
        for field in internal_fields:
            filtered_data.pop(field, None)
        
        # Filter sensitive trust extension fields
        if "x_crisp_trust_relationship" in filtered_data:
            trust_ext = filtered_data["x_crisp_trust_relationship"]
            
            # Remove internal approval details if configured
            if self.export_config.get("filter_approval_details", False):
                trust_ext.pop("approved_by_source_user", None)
                trust_ext.pop("approved_by_target_user", None)
            
            # Remove detailed sharing preferences if configured
            if self.export_config.get("filter_sharing_preferences", False):
                trust_ext.pop("sharing_preferences", None)
        
        return filtered_data
    
    def _add_taxii_markings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add TAXII-specific marking definitions."""
        marked_data = data.copy()
        
        # Determine TLP marking based on trust level
        tlp_marking = self._determine_tlp_marking(data)
        
        # Add marking references
        if "object_marking_refs" not in marked_data:
            marked_data["object_marking_refs"] = []
        
        if tlp_marking not in marked_data["object_marking_refs"]:
            marked_data["object_marking_refs"].append(tlp_marking)
        
        # Add CRISP-specific marking
        crisp_marking = "marking-definition--crisp-trust-intelligence"
        if crisp_marking not in marked_data["object_marking_refs"]:
            marked_data["object_marking_refs"].append(crisp_marking)
        
        return marked_data
    
    def _determine_tlp_marking(self, data: Dict[str, Any]) -> str:
        """Determine appropriate TLP marking based on trust level."""
        tlp_mappings = {
            "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82": "WHITE",  # TLP:WHITE
            "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da": "GREEN",  # TLP:GREEN
            "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82": "AMBER",  # TLP:AMBER
            "marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed": "RED"    # TLP:RED
        }
        
        # Default to TLP:GREEN
        default_marking = "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da"
        
        if "x_crisp_trust_relationship" in data:
            trust_ext = data["x_crisp_trust_relationship"]
            trust_level = trust_ext.get("trust_level", {}).get("level", "medium")
            
            # Map trust levels to TLP markings
            trust_to_tlp = {
                "complete": "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82",  # WHITE
                "high": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da",     # GREEN
                "medium": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da",   # GREEN
                "low": "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82",      # AMBER (using WHITE placeholder)
                "none": "marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed"     # RED
            }
            
            return trust_to_tlp.get(trust_level, default_marking)
        
        return default_marking
    
    def _validate_taxii_compliance(self, data: Dict[str, Any]):
        """Validate TAXII compliance of the prepared object."""
        errors = []
        
        # Check required STIX fields
        required_fields = ["type", "spec_version", "id", "created", "modified"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing TAXII-required field: {field}")
        
        # Check STIX ID format
        if "id" in data and "--" not in data["id"]:
            errors.append(f"Invalid STIX ID format for TAXII: {data['id']}")
        
        # Check spec version
        if "spec_version" in data and data["spec_version"] not in ["2.0", "2.1"]:
            errors.append(f"Unsupported STIX spec version for TAXII: {data['spec_version']}")
        
        if errors:
            raise ValueError(f"TAXII compliance validation failed: {errors}")
    
    def get_collection_id(self) -> Optional[str]:
        """Get the TAXII collection ID for this object."""
        return self.collection_id
    
    def set_collection_id(self, collection_id: str):
        """Set the TAXII collection ID for this object."""
        self.collection_id = collection_id


# Decorator chain builder for convenience
class StixTrustDecoratorChain:
    """
    Builder class for creating decorator chains for STIX trust objects.
    Provides a fluent interface for applying multiple decorators.
    """
    
    def __init__(self, stix_object: StixTrustObject):
        self._component = ConcreteStixTrustComponent(stix_object)
    
    def validate(self, strict_mode: bool = True) -> 'StixTrustDecoratorChain':
        """Add validation decorator to the chain."""
        self._component = StixTrustValidationDecorator(self._component, strict_mode)
        return self
    
    def anonymize(self, anonymization_context: Optional[AnonymizationContext] = None,
                  anonymization_level: str = "partial") -> 'StixTrustDecoratorChain':
        """Add anonymization decorator to the chain."""
        self._component = StixTrustAnonymizationDecorator(
            self._component, anonymization_context, anonymization_level
        )
        return self
    
    def enrich(self, enrichment_config: Optional[Dict[str, Any]] = None) -> 'StixTrustDecoratorChain':
        """Add enrichment decorator to the chain."""
        self._component = StixTrustEnrichmentDecorator(self._component, enrichment_config)
        return self
    
    def prepare_for_taxii(self, collection_id: Optional[str] = None,
                         export_config: Optional[Dict[str, Any]] = None) -> 'StixTrustDecoratorChain':
        """Add TAXII export decorator to the chain."""
        self._component = StixTrustTaxiiExportDecorator(self._component, collection_id, export_config)
        return self
    
    def build(self) -> StixTrustObjectComponent:
        """Build and return the final decorated component."""
        return self._component