import uuid
import json
import csv
import io
from typing import Dict, List, Any, Union, Optional
import datetime
import stix2
from django.conf import settings
from django.utils import timezone

from core.models import Organization, STIXObject, Collection, CollectionObject, Feed, Identity
from stix_factory.factory import STIXObjectFactoryRegistry
from anonymization.strategy import AnonymizationStrategyFactory


def get_or_create_identity(organization: Organization) -> Dict[str, Any]:
    """
    Get or create a STIX Identity object for an organization.
    
    Args:
        organization: The organization to create an identity for
        
    Returns:
        STIX Identity object as a dictionary
    """
    identity, created = Identity.objects.get_or_create(
        organization=organization,
        defaults={
            "stix_id": f"identity--{uuid.uuid4()}",
            "identity_class": "organization",
            "name": organization.name,
        },
    )
    
    # Check if organization already has a STIX ID
    if organization.stix_id:
        # Try to find existing Identity object
        try:
            stix_object = STIXObject.objects.get(stix_id=organization.stix_id)
            return stix_object.to_stix()
        except STIXObject.DoesNotExist:
            # Create new Identity object with existing ID
            identity_id = organization.stix_id
    else:
        # Generate new ID
        identity_id = f"identity--{str(uuid.uuid4())}"
        organization.stix_id = identity_id
        organization.save()
    
    # Create STIX Identity object
    identity_data = {
        "type": "identity",
        "id": identity_id,
        "spec_version": "2.1",
        "name": organization.name,
        "identity_class": organization.identity_class or "organization",
        "created": stix2.utils.format_datetime(timezone.now()),
        "modified": stix2.utils.format_datetime(timezone.now())
    }
    
    # Add optional fields
    if organization.description:
        identity_data["description"] = organization.description
    
    if organization.sectors:
        identity_data["sectors"] = organization.sectors
    
    if organization.contact_email:
        identity_data["contact_information"] = f"Email: {organization.contact_email}"
        if organization.website:
            identity_data["contact_information"] += f", Website: {organization.website}"
    elif organization.website:
        identity_data["contact_information"] = f"Website: {organization.website}"
    
    # Create the STIX object
    stix_object = STIXObject.objects.create(
        stix_id=identity_id,
        stix_type="identity",
        spec_version="2.1",
        created=timezone.now(),
        modified=timezone.now(),
        raw_data=identity_data,
        source_organization=organization
    )
    
    return identity_data


def generate_bundle_from_collection(collection: Collection, 
                                   filters: Optional[Dict[str, Any]] = None,
                                   requesting_organization: Optional[Organization] = None) -> Dict[str, Any]:
    """
    Generate a STIX bundle from a collection.
    
    Args:
        collection: The collection to generate a bundle from
        filters: Optional filters to apply to objects
        requesting_organization: The organization requesting the bundle (for anonymization)
        
    Returns:
        STIX Bundle as a dictionary
    """
    # Get all objects in the collection
    collection_objects = CollectionObject.objects.filter(collection=collection)
    stix_object_ids = collection_objects.values_list('stix_object', flat=True)
    stix_objects = STIXObject.objects.filter(id__in=stix_object_ids)
    
    # Apply filters if provided
    if filters:
        for key, value in filters.items():
            if key == 'stix_type':
                stix_objects = stix_objects.filter(stix_type=value)
            elif key == 'created_after':
                stix_objects = stix_objects.filter(created__gte=value)
            elif key == 'created_before':
                stix_objects = stix_objects.filter(created__lte=value)
            elif key == 'modified_after':
                stix_objects = stix_objects.filter(modified__gte=value)
            elif key == 'modified_before':
                stix_objects = stix_objects.filter(modified__lte=value)
    
    # Create list of STIX objects
    bundle_objects = []
    
    # Add identity of collection owner
    owner_identity = get_or_create_identity(collection.owner)
    bundle_objects.append(owner_identity)
    
    # Process each STIX object
    for obj in stix_objects:
        stix_data = obj.to_stix()
        
        # Apply anonymization if needed
        if requesting_organization and obj.source_organization != requesting_organization:
            # Get trust relationship
            from trust.models import TrustRelationship
            try:
                trust = TrustRelationship.objects.get(
                    source_organization=obj.source_organization,
                    target_organization=requesting_organization
                )
                
                # Apply anonymization based on trust level
                strategy = AnonymizationStrategyFactory.get_strategy(trust.anonymization_strategy)
                stix_data = strategy.anonymize(stix_data, trust.trust_level)
                
            except TrustRelationship.DoesNotExist:
                # No trust relationship, apply default anonymization
                strategy = AnonymizationStrategyFactory.get_default_strategy()
                stix_data = strategy.anonymize(stix_data, 0.0)  # Zero trust level
        
        # Add to bundle
        bundle_objects.append(stix_data)
    
    # Create bundle
    bundle = {
        "type": "bundle",
        "id": f"bundle--{str(uuid.uuid4())}",
        "objects": bundle_objects,
        "spec_version": "2.1"
    }
    
    return bundle


def process_csv_to_stix(csv_data: str, mapping: Dict[str, Any], 
                        organization: Organization) -> List[Dict[str, Any]]:
    """
    Process CSV data to STIX objects using mapping.
    
    Args:
        csv_data: CSV data as string
        mapping: Mapping configuration
        organization: Source organization
        
    Returns:
        List of STIX objects as dictionaries
    """
    # Parse CSV
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(csv_reader)
    
    # Get STIX type from mapping
    stix_type = mapping.get('stix_type')
    if not stix_type:
        raise ValueError("Mapping must specify 'stix_type'")
    
    # Create STIX objects
    stix_objects = []
    
    for row in rows:
        # Create base STIX object
        stix_data = {
            'type': stix_type,
            'id': f"{stix_type}--{uuid.uuid4()}"
        }
        
        # Map CSV fields to STIX properties
        for stix_prop, csv_field in mapping.get('properties', {}).items():
            if csv_field in row and row[csv_field]:
                # Handle special cases
                if stix_prop in ['labels', 'indicator_types', 'malware_types', 'threat_actor_types', 'aliases', 'goals']:
                    # These properties are lists - split CSV value by delimiter
                    delimiter = mapping.get('list_delimiter', ',')
                    stix_data[stix_prop] = [v.strip() for v in row[csv_field].split(delimiter) if v.strip()]
                elif stix_prop in ['valid_from', 'valid_until', 'first_seen', 'last_seen']:
                    # Handle date fields
                    date_format = mapping.get('date_format', '%Y-%m-%d')
                    try:
                        date_obj = datetime.datetime.strptime(row[csv_field], date_format)
                        stix_data[stix_prop] = date_obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    except ValueError:
                        # Skip invalid dates
                        pass
                else:
                    # Regular field
                    stix_data[stix_prop] = row[csv_field]
        
        # Add required fields for specific types
        if stix_type == 'indicator' and 'pattern' not in stix_data:
            # Try to construct pattern from indicator fields
            pattern_field = mapping.get('pattern_field')
            pattern_prefix = mapping.get('pattern_prefix', "[file:name = '")
            pattern_suffix = mapping.get('pattern_suffix', "']")
            
            if pattern_field and pattern_field in row and row[pattern_field]:
                stix_data['pattern'] = f"{pattern_prefix}{row[pattern_field]}{pattern_suffix}"
                stix_data['pattern_type'] = 'stix'
            else:
                continue  # Skip this row, pattern is required
        
        if stix_type == 'malware' and 'is_family' not in stix_data:
            stix_data['is_family'] = mapping.get('default_is_family', False)
        
        # Set created_by_ref to organization's identity
        identity = get_or_create_identity(organization)
        stix_data['created_by_ref'] = identity['id']
        
        # Set created/modified timestamps
        if 'created' not in stix_data:
            stix_data['created'] = stix2.utils.format_datetime(timezone.now())
        if 'modified' not in stix_data:
            stix_data['modified'] = stix2.utils.format_datetime(timezone.now())
        
        # Validate and create STIX object
        try:
            stix_obj = STIXObjectFactoryRegistry.create_object(stix_data)
            stix_objects.append(stix_obj.serialize())
        except Exception as e:
            # Skip invalid objects
            continue
    
    return stix_objects


def publish_feed(feed: Feed) -> Dict[str, Any]:
    """
    Publish a feed by generating a STIX bundle from its collection.
    
    Args:
        feed: The feed to publish
        
    Returns:
        Dictionary with publish results
    """
    # Get collection
    collection = feed.collection
    
    # Convert query parameters to filters
    filters = feed.query_parameters
    
    # Generate bundle
    bundle = generate_bundle_from_collection(collection, filters)
    
    # Update feed status
    feed.last_published_time = timezone.now()
    feed.last_bundle_id = bundle['id']
    feed.save()
    
    return {
        'feed_id': str(feed.id),
        'feed_name': feed.name,
        'collection_id': str(collection.id),
        'published_at': feed.last_published_time,
        'object_count': len(bundle['objects']),
        'bundle_id': bundle['id']
    }