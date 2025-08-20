"""
Core utilities with exact functional replication from threat_intel_service.
"""
import uuid
import json
import csv
import io
from typing import Dict, List, Any, Union, Optional
import datetime
import logging

import stix2
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Organization, STIXObject, Collection, CollectionObject, Feed, Identity
import sys
import os

# Add core patterns strategy to path
core_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core', 'patterns', 'strategy')
sys.path.append(core_path)

try:
    from core.patterns.strategy.context import AnonymizationContext
    from core.patterns.strategy.enums import AnonymizationLevel
    from core.patterns.strategy.exceptions import AnonymizationError
except ImportError:
    # Fallback for development
    from enum import Enum
    
    class AnonymizationLevel(Enum):
        NONE = "none"
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        FULL = "full"
    
    class AnonymizationContext:
        def execute_anonymization(self, data, data_type, level):
            return f"[ANON:{level}]{data}"
        
        def anonymize_stix_object(self, stix_data, level):
            """Fallback STIX object anonymization"""
            import copy
            import json
            result = copy.deepcopy(stix_data)
            result['x_crisp_anonymized'] = True
            result['x_crisp_anonymization_level'] = level.value if hasattr(level, 'value') else str(level)
            result['x_crisp_trust_level'] = 0.5  # Default fallback trust level
            result['x_crisp_source_org'] = 'Unknown Organization'
            result['x_crisp_original_id'] = result.get('id', 'unknown')
            if 'pattern' in result:
                result['pattern'] = f"[ANON:{level}]{result['pattern']}"
            return json.dumps(result)
    
    class AnonymizationError(Exception):
        pass
from .factories.stix_factory import STIXObjectFactory

logger = logging.getLogger(__name__)


def get_or_create_identity(organization: Organization) -> Dict[str, Any]:
    """
    Get or create a STIX Identity SDO dictionary for an organization.
    This also ensures a core.models.Identity and a core.models.STIXObject
    of type 'identity' exist and are consistent with the organization's details.

    Args:
        organization: The core.models.Organization instance.

    Returns:
        A dictionary representing the STIX Identity SDO.
    """
    # Step 1: Determine the canonical STIX ID for this organization's identity.
    canonical_stix_id = None
    if organization.stix_id and organization.stix_id.startswith("identity--"):
        canonical_stix_id = organization.stix_id
    else:
        # Ensure a core.models.Identity record exists or create one.
        identity_model, model_created = Identity.objects.get_or_create(
            organization=organization,
            defaults={
                "name": organization.name,
                "identity_class": organization.identity_class or "organization",
            }
        )
        if identity_model.stix_id and identity_model.stix_id.startswith("identity--"):
            canonical_stix_id = identity_model.stix_id
        else:
            canonical_stix_id = f"identity--{str(uuid.uuid4())}"

    # Step 2: Ensure consistency across Organization and Identity models for this STIX ID.
    if organization.stix_id != canonical_stix_id:
        organization.stix_id = canonical_stix_id
        organization.save(update_fields=['stix_id'])
        logger.debug(f"Updated Organization {organization.name} STIX ID to {canonical_stix_id}")

    identity_model, _ = Identity.objects.update_or_create(
        organization=organization,
        defaults={
            "stix_id": canonical_stix_id,
            "name": organization.name,
            "identity_class": organization.identity_class or "organization",
        }
    )
    logger.debug(f"Ensured core.models.Identity for {organization.name} with STIX ID {canonical_stix_id}")

    # Step 3: Construct the STIX Identity SDO dictionary.
    current_time_utc = timezone.now()
    identity_sdo_data = {
        "type": "identity",
        "id": canonical_stix_id,
        "spec_version": "2.1",
        "name": organization.name,
        "identity_class": organization.identity_class or "organization",
        "created": stix2.utils.format_datetime(organization.created_at if organization.created_at else current_time_utc),
        "modified": stix2.utils.format_datetime(current_time_utc),
    }
    if organization.description:
        identity_sdo_data["description"] = organization.description
    if organization.sectors:
        identity_sdo_data["sectors"] = organization.sectors if isinstance(organization.sectors, list) else [organization.sectors]
    
    contact_info_parts = []
    if organization.contact_email:
        contact_info_parts.append(f"Email: {organization.contact_email}")
    if organization.website:
        contact_info_parts.append(f"Website: {organization.website}")
    if contact_info_parts:
        identity_sdo_data["contact_information"] = ", ".join(contact_info_parts)

    # Step 4: Ensure a STIXObject of type 'identity' exists and its raw_data is current.
    stix_object_defaults = {
        'stix_type': "identity",
        'spec_version': "2.1",
        'created': parse_datetime(identity_sdo_data['created']) or current_time_utc,
        'modified': current_time_utc,
        'raw_data': identity_sdo_data,
        'source_organization': organization,
    }
    stix_object_identity, created_sdo_db = STIXObject.objects.update_or_create(
        stix_id=canonical_stix_id,
        defaults=stix_object_defaults
    )
    if not created_sdo_db and stix_object_identity.raw_data != identity_sdo_data:
        stix_object_identity.raw_data = identity_sdo_data
        stix_object_identity.modified = current_time_utc
        stix_object_identity.save()
        logger.debug(f"Updated STIXObject raw_data for identity {canonical_stix_id}")
    else:
        logger.debug(f"Ensured STIXObject for identity {canonical_stix_id} ({'Created' if created_sdo_db else 'Exists'})")

    return identity_sdo_data


def generate_bundle_from_collection(collection: Collection,
                                   filters: Optional[Dict[str, Any]] = None,
                                   requesting_organization: Optional[Organization] = None) -> Dict[str, Any]:
    """
    Generate a STIX bundle from a collection, applying filters and anonymization.
    """
    logger.info(f"Generating bundle for collection '{collection.title}' (Owner: {collection.owner.name}). Requesting org: {requesting_organization.name if requesting_organization else 'None (Internal View)'}")

    stix_objects_query = collection.stix_objects.all()

    # Apply filters if provided
    if filters:
        if 'stix_type' in filters:
            stix_objects_query = stix_objects_query.filter(stix_type=filters['stix_type'])
        if 'created_after' in filters:
            stix_objects_query = stix_objects_query.filter(created__gte=filters['created_after'])

    bundle_sdo_objects = []

    # Add identity of the collection owner to the bundle
    owner_identity_sdo = get_or_create_identity(collection.owner)
    bundle_sdo_objects.append(owner_identity_sdo)
    logger.debug(f"Added owner identity {owner_identity_sdo['id']} to bundle.")

    # Process each STIX object from the database
    for db_stix_object in stix_objects_query:
        stix_sdo_data = db_stix_object.to_stix()

        # Apply anonymization if a requesting organization is specified and is different from the object's source
        if requesting_organization and db_stix_object.source_organization != requesting_organization:
            source_org_of_object = db_stix_object.source_organization
            
            # Determine trust and anonymization level between object's source and requester
            trust = get_trust_level(source_org_of_object, requesting_organization)
            anon_level = get_anonymization_level(source_org_of_object, requesting_organization)
            
            logger.debug(f"Anonymizing object {db_stix_object.stix_id} from {source_org_of_object.name} for {requesting_organization.name}. Level: {anon_level.value}, Trust: {trust}")

            try:
                # Use the advanced anonymization context
                context = AnonymizationContext()
                anonymized_json = context.anonymize_stix_object(stix_sdo_data, anon_level)
                
                # Parse back to dictionary since the method returns JSON string
                stix_sdo_data = json.loads(anonymized_json)
                
                # Mark object as anonymized
                stix_sdo_data['x_crisp_anonymized'] = True
                stix_sdo_data['x_crisp_anonymization_level'] = anon_level.value
                stix_sdo_data['x_crisp_trust_level'] = trust
                stix_sdo_data['x_crisp_source_org'] = source_org_of_object.name
                
            except AnonymizationError as e:
                logger.error(f"Anonymization failed for object {db_stix_object.stix_id}: {e}")
                # Fall back to excluding the object rather than exposing raw data
                continue
        
        bundle_sdo_objects.append(stix_sdo_data)

    # Create the final STIX Bundle SDO
    bundle_id = f"bundle--{str(uuid.uuid4())}"
    stix_bundle_sdo = {
        "type": "bundle",
        "id": bundle_id,
        "spec_version": "2.1",
        "objects": bundle_sdo_objects,
    }
    logger.info(f"Generated bundle {bundle_id} with {len(bundle_sdo_objects)} objects (incl. owner identity).")
    return stix_bundle_sdo


def process_csv_to_stix(csv_data: str, mapping: Dict[str, Any],
                        organization: Organization) -> List[Dict[str, Any]]:
    """
    Process CSV data and convert to STIX objects.
    """
    if not csv_data:
        return []

    csvfile = io.StringIO(csv_data)
    csv_delimiter = mapping.get('csv_delimiter', ',')
    csv_reader = csv.DictReader(csvfile, delimiter=csv_delimiter)
    try:
        rows = list(csv_reader)
    except csv.Error as e:
        logger.error(f"CSV parsing error: {e}. CSV data (first 500 chars): {csv_data[:500]}")
        raise ValueError(f"Invalid CSV data: {e}")

    stix_type_from_mapping = mapping.get('stix_type')
    if not stix_type_from_mapping:
        raise ValueError("Mapping must specify a 'stix_type' for CSV processing.")

    processed_stix_sdo_list = []
    organization_identity_sdo = get_or_create_identity(organization)

    # Define a mapping from simple CSV types to STIX observable property paths
    CSV_TYPE_TO_STIX_PATH = {
        'ipv4-addr': 'ipv4-addr:value',
        'ipv6-addr': 'ipv6-addr:value',
        'domain-name': 'domain-name:value',
        'url': 'url:value',
        'file-md5': 'file:hashes.MD5',
        'file-sha1': 'file:hashes.SHA-1',
        'file-sha256': 'file:hashes.SHA-256',
        'email-addr': 'email-addr:value',
    }

    for row_num, row_dict in enumerate(rows):
        current_time_stix = stix2.utils.format_datetime(timezone.now())
        stix_sdo = {
            'type': stix_type_from_mapping,
            'id': f"{stix_type_from_mapping}--{str(uuid.uuid4())}",
            'spec_version': '2.1',
            'created': current_time_stix,
            'modified': current_time_stix,
            'created_by_ref': organization_identity_sdo['id'],
        }

        # Process property mappings
        for stix_property_name, csv_column_name in mapping.get('properties', {}).items():
            if csv_column_name in row_dict and row_dict[csv_column_name]:
                value = row_dict[csv_column_name]
                if stix_property_name in ['labels', 'indicator_types', 'malware_types', 'threat_actor_types', 'aliases', 'goals', 'secondary_motivations', 'roles', 'sectors', 'kill_chain_phases.phase_name']:
                    list_delimiter = mapping.get('list_delimiter', ',')
                    stix_sdo[stix_property_name] = [v.strip() for v in value.split(list_delimiter) if v.strip()]
                elif stix_property_name in ['valid_from', 'valid_until', 'first_seen', 'last_seen']:
                    try:
                        dt_obj = parse_datetime(value) or datetime.datetime.strptime(value, mapping.get('date_format', '%Y-%m-%d'))
                        stix_sdo[stix_property_name] = stix2.utils.format_datetime(dt_obj)
                    except ValueError:
                        logger.warning(f"Row {row_num+1}: Invalid date '{value}' for '{stix_property_name}'. Using original value.")
                        stix_sdo[stix_property_name] = value
                elif stix_property_name == 'confidence':
                    try:
                        stix_sdo[stix_property_name] = int(value)
                    except ValueError:
                        logger.warning(f"Row {row_num+1}: Invalid confidence '{value}'. Skipping field.")
                elif stix_property_name == 'is_family' and isinstance(value, str):
                    stix_sdo[stix_property_name] = value.lower() in ['true', '1', 'yes', 't']
                else:
                    stix_sdo[stix_property_name] = value

        if stix_type_from_mapping == 'indicator':
            pattern_value_csv_field = mapping.get('pattern_field')
            pattern_type_from_csv_field = mapping.get('pattern_type_field')

            ioc_val = row_dict.get(pattern_value_csv_field) if pattern_value_csv_field else None
            csv_pattern_type = row_dict.get(pattern_type_from_csv_field) if pattern_type_from_csv_field else None

            if ioc_val and csv_pattern_type:
                stix_path = CSV_TYPE_TO_STIX_PATH.get(csv_pattern_type.lower().strip())
                if stix_path:
                    stix_sdo['pattern'] = f"[{stix_path} = '{ioc_val}']"
                    stix_sdo['pattern_type'] = 'stix'
                else:
                    logger.warning(f"Row {row_num+1}: Unsupported or unknown CSV pattern type '{csv_pattern_type}' for IOC '{ioc_val}'. Skipping pattern for this indicator.")
            elif ioc_val and mapping.get('default_pattern_path'):
                 stix_sdo['pattern'] = f"[{mapping['default_pattern_path']} = '{ioc_val}']"
                 stix_sdo['pattern_type'] = 'stix'
            else:
                logger.warning(f"Row {row_num+1}: Insufficient data for indicator pattern (IOC value from '{pattern_value_csv_field}', type from '{pattern_type_from_csv_field}').")
                if 'pattern' not in stix_sdo:
                    logger.warning(f"Row {row_num+1}: Pattern could not be constructed. Skipping this row for indicator creation.")
                    continue

            if 'valid_from' not in stix_sdo:
                stix_sdo['valid_from'] = current_time_stix

        if stix_type_from_mapping == 'malware' and 'is_family' not in stix_sdo:
            stix_sdo['is_family'] = mapping.get('default_is_family', False)

        processed_stix_sdo_list.append(stix_sdo)

    logger.info(f"Processed {len(rows)} CSV rows, generated {len(processed_stix_sdo_list)} STIX SDO dictionaries.")
    return processed_stix_sdo_list


def publish_feed(feed: Feed) -> Dict[str, Any]:
    """
    Publish a feed: generates a STIX bundle from its collection and updates feed metadata.
    This assumes the feed is active and due for publishing.
    """
    if not isinstance(feed, Feed):
        raise TypeError("publish_feed expects a core.models.Feed instance.")

    logger.info(f"Attempting to publish feed '{feed.name}' (ID: {feed.id}). Collection: '{feed.collection.title}'")

    # Convert query parameters from feed model to filters for bundle generation
    bundle_filters = {}
    if feed.query_parameters:
        for key, value in feed.query_parameters.items():
            if key == "created_after" or key == "modified_since":
                try:
                    bundle_filters[key] = parse_datetime(value)
                except ValueError:
                    logger.warning(f"Invalid date format in query_parameters for feed {feed.id}: {key}={value}")
            else:
                bundle_filters[key] = value
    
    # Generate bundle
    try:
        bundle_sdo = generate_bundle_from_collection(feed.collection, filters=bundle_filters, requesting_organization=None)
    except Exception as e:
        logger.error(f"Error generating bundle for feed '{feed.name}': {e}", exc_info=True)
        feed.last_error = str(e)
        feed.error_count += 1
        feed.status = 'error'
        feed.save()
        raise

    # Update feed metadata
    feed.last_published_time = timezone.now()
    feed.last_bundle_id = bundle_sdo['id']
    feed.publish_count += 1
    feed.last_error = None
    feed.status = 'active'
    
    # Schedule next publish
    feed.schedule_next_publish()
    
    feed.save()

    logger.info(f"Feed '{feed.name}' published successfully. Bundle ID: {bundle_sdo['id']}, {len(bundle_sdo['objects'])} objects.")
    return {
        'feed_id': str(feed.id),
        'feed_name': feed.name,
        'collection_id': str(feed.collection.id),
        'published_at': feed.last_published_time.isoformat(),
        'object_count': len(bundle_sdo['objects']),
        'bundle_id': bundle_sdo['id'],
        'status': 'success'
    }


def get_trust_level(source_org: Organization, target_org: Organization) -> float:
    """
    Get trust level between organizations with enhanced logic.
    """
    if source_org == target_org:
        return 1.0
    
    # Check for explicit trust relationships
    try:
        from .models import TrustRelationship
        relationship = TrustRelationship.objects.get(
            source_organization=source_org,
            target_organization=target_org
        )
        return relationship.trust_level
    except (ImportError, TrustRelationship.DoesNotExist):
        pass
    
    # Default trust based on organization types
    if hasattr(source_org, 'organization_type') and hasattr(target_org, 'organization_type'):
        if source_org.organization_type == target_org.organization_type == 'university':
            return 0.7  # Higher trust between universities
        elif 'university' in [source_org.organization_type, target_org.organization_type]:
            return 0.6  # Medium-high trust with universities
    
    return 0.5  # Default medium trust


def get_anonymization_level(source_org: Organization, target_org: Organization) -> AnonymizationLevel:
    """
    Get anonymization level based on trust relationship.
    """
    trust_level = get_trust_level(source_org, target_org)
    
    if trust_level >= 0.9:
        return AnonymizationLevel.NONE
    elif trust_level >= 0.7:
        return AnonymizationLevel.LOW
    elif trust_level >= 0.5:
        return AnonymizationLevel.MEDIUM
    elif trust_level >= 0.3:
        return AnonymizationLevel.HIGH
    else:
        return AnonymizationLevel.FULL