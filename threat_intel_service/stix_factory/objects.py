import uuid
import json
from datetime import datetime
import stix2
from typing import Dict, Any, List, Optional, Union

def create_stix_bundle(objects, bundle_id=None):
    """
    Create a STIX 2.1 bundle from a list of STIX objects.
    
    Args:
        objects: List of STIX objects (can be dicts or stix2 objects)
        bundle_id: Optional ID for the bundle, generated if not provided
        
    Returns:
        STIX Bundle object
    """
    if not bundle_id:
        bundle_id = f"bundle--{str(uuid.uuid4())}"
        
    # Convert all objects to dictionaries if they're stix2 objects
    obj_dicts = []
    for obj in objects:
        if isinstance(obj, stix2.base._STIXBase):
            obj_dicts.append(json.loads(obj.serialize()))
        else:
            obj_dicts.append(obj)
    
    # Create the bundle
    bundle = {
        "type": "bundle",
        "id": bundle_id,
        "objects": obj_dicts,
        "spec_version": "2.1"
    }
    
    return bundle

def create_indicator(pattern, pattern_type="stix", name=None, description=None, 
                    valid_from=None, valid_until=None, indicator_types=None, 
                    kill_chain_phases=None, confidence=None, labels=None,
                    created_by_ref=None, object_marking_refs=None):
    """
    Create a STIX 2.1 Indicator object.
    
    Args:
        pattern: The STIX pattern
        pattern_type: Type of pattern (default: "stix")
        name: Name of the indicator (optional)
        description: Description (optional)
        valid_from: Start of validity time (default: current time)
        valid_until: End of validity time (optional)
        indicator_types: List of indicator types (optional)
        kill_chain_phases: List of kill chain phases (optional)
        confidence: Confidence level 0-100 (optional)
        labels: List of labels (optional)
        created_by_ref: ID of the creator identity (optional)
        object_marking_refs: List of marking definition IDs (optional)
        
    Returns:
        STIX Indicator object
    """
    # Set default values
    if valid_from is None:
        valid_from = datetime.utcnow()
        
    # Create kwargs dict with only defined parameters
    kwargs = {"pattern": pattern, "pattern_type": pattern_type, "valid_from": valid_from}
    
    if name is not None:
        kwargs["name"] = name
    if description is not None:
        kwargs["description"] = description
    if valid_until is not None:
        kwargs["valid_until"] = valid_until
    if indicator_types is not None:
        kwargs["indicator_types"] = indicator_types
    if kill_chain_phases is not None:
        kwargs["kill_chain_phases"] = kill_chain_phases
    if confidence is not None:
        kwargs["confidence"] = confidence
    if labels is not None:
        kwargs["labels"] = labels
    if created_by_ref is not None:
        kwargs["created_by_ref"] = created_by_ref
    if object_marking_refs is not None:
        kwargs["object_marking_refs"] = object_marking_refs
        
    return stix2.v21.Indicator(**kwargs)

def create_malware(name=None, is_family=False, description=None, malware_types=None,
                kill_chain_phases=None, first_seen=None, last_seen=None,
                operating_system_refs=None, architecture_execution_envs=None,
                implementation_languages=None, capabilities=None, sample_refs=None,
                created_by_ref=None, object_marking_refs=None, labels=None):
    """
    Create a STIX 2.1 Malware object.
    
    Args:
        name: Name of the malware (optional)
        is_family: Whether this is a malware family (default: False)
        description: Description (optional)
        malware_types: List of malware types (optional)
        kill_chain_phases: List of kill chain phases (optional)
        first_seen: Time first seen (optional)
        last_seen: Time last seen (optional)
        operating_system_refs: List of operating system references (optional)
        architecture_execution_envs: List of architecture execution environments (optional)
        implementation_languages: List of implementation languages (optional)
        capabilities: List of capabilities (optional)
        sample_refs: List of sample references (optional)
        created_by_ref: ID of the creator identity (optional)
        object_marking_refs: List of marking definition IDs (optional)
        labels: List of labels (optional)
        
    Returns:
        STIX Malware object
    """
    # Create kwargs dict with only defined parameters
    kwargs = {"is_family": is_family}
    
    if name is not None:
        kwargs["name"] = name
    if description is not None:
        kwargs["description"] = description
    if malware_types is not None:
        kwargs["malware_types"] = malware_types
    if kill_chain_phases is not None:
        kwargs["kill_chain_phases"] = kill_chain_phases
    if first_seen is not None:
        kwargs["first_seen"] = first_seen
    if last_seen is not None:
        kwargs["last_seen"] = last_seen
    if operating_system_refs is not None:
        kwargs["operating_system_refs"] = operating_system_refs
    if architecture_execution_envs is not None:
        kwargs["architecture_execution_envs"] = architecture_execution_envs
    if implementation_languages is not None:
        kwargs["implementation_languages"] = implementation_languages
    if capabilities is not None:
        kwargs["capabilities"] = capabilities
    if sample_refs is not None:
        kwargs["sample_refs"] = sample_refs
    if created_by_ref is not None:
        kwargs["created_by_ref"] = created_by_ref
    if object_marking_refs is not None:
        kwargs["object_marking_refs"] = object_marking_refs
    if labels is not None:
        kwargs["labels"] = labels
        
    return stix2.v21.Malware(**kwargs)

def create_attack_pattern(name=None, description=None, aliases=None,
                        kill_chain_phases=None, external_references=None,
                        created_by_ref=None, object_marking_refs=None, labels=None):
    """
    Create a STIX 2.1 Attack Pattern object.
    
    Args:
        name: Name of the attack pattern (optional)
        description: Description (optional)
        aliases: List of aliases (optional)
        kill_chain_phases: List of kill chain phases (optional)
        external_references: List of external references (optional)
        created_by_ref: ID of the creator identity (optional)
        object_marking_refs: List of marking definition IDs (optional)
        labels: List of labels (optional)
        
    Returns:
        STIX Attack Pattern object
    """
    # Create kwargs dict with only defined parameters
    kwargs = {}
    
    if name is not None:
        kwargs["name"] = name
    if description is not None:
        kwargs["description"] = description
    if aliases is not None:
        kwargs["aliases"] = aliases
    if kill_chain_phases is not None:
        kwargs["kill_chain_phases"] = kill_chain_phases
    if external_references is not None:
        kwargs["external_references"] = external_references
    if created_by_ref is not None:
        kwargs["created_by_ref"] = created_by_ref
    if object_marking_refs is not None:
        kwargs["object_marking_refs"] = object_marking_refs
    if labels is not None:
        kwargs["labels"] = labels
        
    return stix2.v21.AttackPattern(**kwargs)

def create_threat_actor(name=None, description=None, threat_actor_types=None,
                      aliases=None, first_seen=None, last_seen=None, roles=None,
                      goals=None, sophistication=None, resource_level=None,
                      primary_motivation=None, secondary_motivations=None,
                      created_by_ref=None, object_marking_refs=None, labels=None):
    """
    Create a STIX 2.1 Threat Actor object.
    
    Args:
        name: Name of the threat actor (optional)
        description: Description (optional)
        threat_actor_types: List of threat actor types (optional)
        aliases: List of aliases (optional)
        first_seen: Time first seen (optional)
        last_seen: Time last seen (optional)
        roles: List of roles (optional)
        goals: List of goals (optional)
        sophistication: Level of sophistication (optional)
        resource_level: Level of resources (optional)
        primary_motivation: Primary motivation (optional)
        secondary_motivations: List of secondary motivations (optional)
        created_by_ref: ID of the creator identity (optional)
        object_marking_refs: List of marking definition IDs (optional)
        labels: List of labels (optional)
        
    Returns:
        STIX Threat Actor object
    """
    # Create kwargs dict with only defined parameters
    kwargs = {}
    
    if name is not None:
        kwargs["name"] = name
    if description is not None:
        kwargs["description"] = description
    if threat_actor_types is not None:
        kwargs["threat_actor_types"] = threat_actor_types
    if aliases is not None:
        kwargs["aliases"] = aliases
    if first_seen is not None:
        kwargs["first_seen"] = first_seen
    if last_seen is not None:
        kwargs["last_seen"] = last_seen
    if roles is not None:
        kwargs["roles"] = roles
    if goals is not None:
        kwargs["goals"] = goals
    if sophistication is not None:
        kwargs["sophistication"] = sophistication
    if resource_level is not None:
        kwargs["resource_level"] = resource_level
    if primary_motivation is not None:
        kwargs["primary_motivation"] = primary_motivation
    if secondary_motivations is not None:
        kwargs["secondary_motivations"] = secondary_motivations
    if created_by_ref is not None:
        kwargs["created_by_ref"] = created_by_ref
    if object_marking_refs is not None:
        kwargs["object_marking_refs"] = object_marking_refs
    if labels is not None:
        kwargs["labels"] = labels
        
    return stix2.v21.ThreatActor(**kwargs)

def create_identity(name, identity_class, description=None, sectors=None,
                   contact_information=None, created_by_ref=None, 
                   object_marking_refs=None, labels=None):
    """
    Create a STIX 2.1 Identity object.
    
    Args:
        name: Name of the identity (required)
        identity_class: Class of this identity (required)
        description: Description (optional)
        sectors: List of sectors (optional)
        contact_information: Contact information (optional)
        created_by_ref: ID of the creator identity (optional)
        object_marking_refs: List of marking definition IDs (optional)
        labels: List of labels (optional)
        
    Returns:
        STIX Identity object
    """
    # Create kwargs dict with only defined parameters
    kwargs = {"name": name, "identity_class": identity_class}
    
    if description is not None:
        kwargs["description"] = description
    if sectors is not None:
        kwargs["sectors"] = sectors
    if contact_information is not None:
        kwargs["contact_information"] = contact_information
    if created_by_ref is not None:
        kwargs["created_by_ref"] = created_by_ref
    if object_marking_refs is not None:
        kwargs["object_marking_refs"] = object_marking_refs
    if labels is not None:
        kwargs["labels"] = labels
        
    return stix2.v21.Identity(**kwargs)

def create_relationship(relationship_type, source_ref, target_ref, description=None,
                       start_time=None, stop_time=None, created_by_ref=None,
                       object_marking_refs=None, labels=None):
    """
    Create a STIX 2.1 Relationship object.
    
    Args:
        relationship_type: Type of relationship (required)
        source_ref: ID of source object (required)
        target_ref: ID of target object (required)
        description: Description (optional)
        start_time: Start time of the relationship (optional)
        stop_time: Stop time of the relationship (optional)
        created_by_ref: ID of the creator identity (optional)
        object_marking_refs: List of marking definition IDs (optional)
        labels: List of labels (optional)
        
    Returns:
        STIX Relationship object
    """
    # Create kwargs dict with only defined parameters
    kwargs = {"relationship_type": relationship_type, "source_ref": source_ref, "target_ref": target_ref}
    
    if description is not None:
        kwargs["description"] = description
    if start_time is not None:
        kwargs["start_time"] = start_time
    if stop_time is not None:
        kwargs["stop_time"] = stop_time
    if created_by_ref is not None:
        kwargs["created_by_ref"] = created_by_ref
    if object_marking_refs is not None:
        kwargs["object_marking_refs"] = object_marking_refs
    if labels is not None:
        kwargs["labels"] = labels
        
    return stix2.v21.Relationship(**kwargs)

def create_marking_definition(definition_type, definition, created_by_ref=None):
    """
    Create a STIX 2.1 Marking Definition object.
    
    Args:
        definition_type: Type of marking definition (required)
        definition: The marking definition (required)
        created_by_ref: ID of the creator identity (optional)
        
    Returns:
        STIX Marking Definition object
    """
    # Create kwargs dict with only defined parameters
    kwargs = {"definition_type": definition_type, "definition": definition}
    
    if created_by_ref is not None:
        kwargs["created_by_ref"] = created_by_ref
        
    return stix2.v21.MarkingDefinition(**kwargs)

def create_tlp_marking(tlp_level):
    """
    Create a TLP marking definition.
    
    Args:
        tlp_level: TLP level (white, green, amber, red)
        
    Returns:
        STIX Marking Definition object with TLP marking
    """
    if tlp_level not in ["white", "green", "amber", "red"]:
        raise ValueError("TLP level must be one of: white, green, amber, red")
        
    definition = {"tlp": tlp_level}
    return create_marking_definition("tlp", definition)