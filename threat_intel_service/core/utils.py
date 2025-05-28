import uuid
import json
import csv
import io
from typing import Dict, List, Any, Union, Optional
import datetime # Keep this for datetime.datetime if used directly elsewhere
import logging # For logging

import stix2 # For stix2.utils and object creation if needed directly
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime # For robust date parsing

# Local app imports
from core.models import Organization, STIXObject, Collection, CollectionObject, Feed, Identity
# Note: AnonymizationStrategyFactory and TrustRelationship might be needed here
# if anonymization logic is deeply embedded in utils that aren't TAXII specific.
# For now, assuming they are primarily used in TAXII views or higher-level services.
from anonymization.strategy import AnonymizationStrategyFactory
# from trust.models import TrustRelationship # Uncomment if needed directly in a util function here

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
    # Prioritize organization.stix_id if already set and valid.
    # Otherwise, use or create one for the associated core.models.Identity.
    canonical_stix_id = None
    if organization.stix_id and organization.stix_id.startswith("identity--"):
        canonical_stix_id = organization.stix_id
    else:
        # Ensure a core.models.Identity record exists or create one.
        # This model might hold additional Django-specific identity info or link to users.
        identity_model, model_created = Identity.objects.get_or_create(
            organization=organization,
            defaults={
                "name": organization.name,
                "identity_class": organization.identity_class or "organization",
                # Let the model's save() or a signal handle stix_id generation if not set
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

    identity_model, _ = Identity.objects.update_or_create( # Use update_or_create for robustness
        organization=organization,
        defaults={
            "stix_id": canonical_stix_id,
            "name": organization.name,
            "identity_class": organization.identity_class or "organization",
            # 'raw_data' on Identity model could store a simple representation if needed
        }
    )
    logger.debug(f"Ensured core.models.Identity for {organization.name} with STIX ID {canonical_stix_id}")


    # Step 3: Construct the STIX Identity SDO dictionary.
    current_time_utc = timezone.now()
    identity_sdo_data = {
        "type": "identity",
        "id": canonical_stix_id, # Use the single, consistent ID
        "spec_version": "2.1",
        "name": organization.name,
        "identity_class": organization.identity_class or "organization", # Default if not set
        "created": stix2.utils.format_datetime(organization.created_at if organization.created_at else current_time_utc), # Use org creation time
        "modified": stix2.utils.format_datetime(current_time_utc),
    }
    if organization.description:
        identity_sdo_data["description"] = organization.description
    if organization.sectors: # Ensure sectors is a list
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
        'created': parse_datetime(identity_sdo_data['created']) or current_time_utc, # Use created from SDO
        'modified': current_time_utc,
        'raw_data': identity_sdo_data,
        'source_organization': organization,
        # 'name': organization.name, # If STIXObject model has a direct 'name' field
        # 'created_by': organization.created_by, # If applicable and desired
    }
    stix_object_identity, created_sdo_db = STIXObject.objects.update_or_create(
        stix_id=canonical_stix_id,
        defaults=stix_object_defaults
    )
    if not created_sdo_db and stix_object_identity.raw_data != identity_sdo_data: # If updated, ensure raw_data is fresh
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
    from trust.utils import get_trust_level, get_anonymization_strategy # Local import to avoid circularity at module level

    logger.info(f"Generating bundle for collection '{collection.title}' (Owner: {collection.owner.name}). Requesting org: {requesting_organization.name if requesting_organization else 'None (Internal View)'}")

    stix_objects_query = collection.stix_objects.all() # Gets STIXObject model instances

    # Apply filters if provided (enhance this as needed)
    if filters:
        if 'stix_type' in filters:
            stix_objects_query = stix_objects_query.filter(stix_type=filters['stix_type'])
        if 'created_after' in filters: # Expects datetime object
            stix_objects_query = stix_objects_query.filter(created__gte=filters['created_after'])
        # Add more filters: modified_since, labels, etc.

    bundle_sdo_objects = []

    # Add identity of the collection owner to the bundle
    owner_identity_sdo = get_or_create_identity(collection.owner)
    bundle_sdo_objects.append(owner_identity_sdo)
    logger.debug(f"Added owner identity {owner_identity_sdo['id']} to bundle.")

    # Process each STIX object from the database
    for db_stix_object in stix_objects_query:
        stix_sdo_data = db_stix_object.to_stix() # Get the raw_data (which is a STIX SDO dict)

        # Apply anonymization if a requesting organization is specified and is different from the object's source
        if requesting_organization and db_stix_object.source_organization != requesting_organization:
            source_org_of_object = db_stix_object.source_organization
            
            # Determine trust and anonymization strategy between object's source and requester
            # These would come from your trust module logic
            trust = get_trust_level(source_org_of_object, requesting_organization)
            anon_strategy_name = get_anonymization_strategy(source_org_of_object, requesting_organization)
            
            logger.debug(f"Anonymizing object {db_stix_object.stix_id} from {source_org_of_object.name} for {requesting_organization.name}. Strategy: {anon_strategy_name}, Trust: {trust}")

            strategy_instance = AnonymizationStrategyFactory.get_strategy(anon_strategy_name)
            stix_sdo_data = strategy_instance.anonymize(stix_sdo_data, trust) # Pass SDO dict
        
        bundle_sdo_objects.append(stix_sdo_data)

    # Create the final STIX Bundle SDO
    bundle_id = f"bundle--{str(uuid.uuid4())}"
    stix_bundle_sdo = {
        "type": "bundle",
        "id": bundle_id,
        "spec_version": "2.1", # Ensure bundle itself has spec_version
        "objects": bundle_sdo_objects,
    }
    logger.info(f"Generated bundle {bundle_id} with {len(bundle_sdo_objects)} objects (incl. owner identity).")
    return stix_bundle_sdo


def process_csv_to_stix(csv_data: str, mapping: Dict[str, Any],
                        organization: Organization) -> List[Dict[str, Any]]:
    # ... (CSV parsing logic remains the same from previous version) ...
    if not csv_data: return []

    import io
    import csv

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
        # Add more mappings as needed
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

        # ... (property mapping logic from previous version) ...
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
            pattern_value_csv_field = mapping.get('pattern_field')       # e.g., 'ioc_value'
            pattern_type_from_csv_field = mapping.get('pattern_type_field') # e.g., 'ioc_type_from_csv'

            ioc_val = row_dict.get(pattern_value_csv_field) if pattern_value_csv_field else None
            csv_pattern_type = row_dict.get(pattern_type_from_csv_field) if pattern_type_from_csv_field else None

            if ioc_val and csv_pattern_type:
                stix_path = CSV_TYPE_TO_STIX_PATH.get(csv_pattern_type.lower().strip())
                if stix_path:
                    stix_sdo['pattern'] = f"[{stix_path} = '{ioc_val}']"
                    stix_sdo['pattern_type'] = 'stix'
                else:
                    logger.warning(f"Row {row_num+1}: Unsupported or unknown CSV pattern type '{csv_pattern_type}' for IOC '{ioc_val}'. Skipping pattern for this indicator.")
                    # Decide if you want to skip the whole indicator or create it without a pattern
                    # For now, we'll let it proceed, and validator should catch missing pattern for indicator.
            elif ioc_val and mapping.get('default_pattern_path'): # Fallback to a default path if only value is given
                 stix_sdo['pattern'] = f"[{mapping['default_pattern_path']} = '{ioc_val}']"
                 stix_sdo['pattern_type'] = 'stix'
            else:
                logger.warning(f"Row {row_num+1}: Insufficient data for indicator pattern (IOC value from '{pattern_value_csv_field}', type from '{pattern_type_from_csv_field}').")
                # Indicator requires a pattern, so this SDO will likely fail validation later if not set.
                # Let's not add it to the list if pattern is crucial and missing.
                if 'pattern' not in stix_sdo: # Check if pattern was actually set
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
    # This needs careful implementation based on how query_parameters are stored and what generate_bundle supports
    # Example: feed.query_parameters = {"type": "indicator", "created_after": "2023-01-01T00:00:00Z"}
    bundle_filters = {}
    if feed.query_parameters:
        for key, value in feed.query_parameters.items():
            if key == "created_after" or key == "modified_since": # Example date filter
                try:
                    bundle_filters[key] = parse_datetime(value) # Ensure datetime object
                except ValueError:
                    logger.warning(f"Invalid date format in query_parameters for feed {feed.id}: {key}={value}")
            else:
                bundle_filters[key] = value
    
    # Generate bundle (requesting_organization=None implies an internal/master view of the data)
    # Anonymization within the bundle will depend on the target audience if this bundle is for external sharing.
    # For now, assume it's the "raw" bundle from the collection owner's perspective.
    # If feeds are for specific external trusted orgs, `requesting_organization` should be set.
    try:
        bundle_sdo = generate_bundle_from_collection(feed.collection, filters=bundle_filters, requesting_organization=None)
    except Exception as e:
        logger.error(f"Error generating bundle for feed '{feed.name}': {e}", exc_info=True)
        feed.last_error = str(e)
        feed.error_count += 1
        feed.status = 'error' # Mark feed as error
        feed.save()
        raise # Re-raise to indicate publishing failure

    # Update feed metadata
    feed.last_published_time = timezone.now()
    feed.last_bundle_id = bundle_sdo['id']
    feed.publish_count += 1
    feed.last_error = None # Clear last error on successful publish
    feed.status = 'active' # Ensure status is active
    
    # Schedule next publish (if applicable, or done by Celery beat task)
    feed.schedule_next_publish() # Assumes this method exists on Feed model
    
    feed.save()

    logger.info(f"Feed '{feed.name}' published successfully. Bundle ID: {bundle_sdo['id']}, {len(bundle_sdo['objects'])} objects.")
    return {
        'feed_id': str(feed.id),
        'feed_name': feed.name,
        'collection_id': str(feed.collection.id),
        'published_at': feed.last_published_time.isoformat(), # Ensure ISO format
        'object_count': len(bundle_sdo['objects']),
        'bundle_id': bundle_sdo['id'],
        'status': 'success'
    }