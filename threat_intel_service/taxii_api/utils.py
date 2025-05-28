"""
Utility functions for TAXII API endpoints.
"""
import uuid
import json
from typing import Dict, List, Any, Union, Optional
from datetime import datetime
import stix2
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from core.models import Organization, STIXObject, Collection, CollectionObject


def get_request_headers(request) -> Dict[str, str]:
    """
    Extract relevant headers from request.
    
    Args:
        request: Django request object
        
    Returns:
        Dictionary of relevant headers
    """
    headers = {}
    
    # Extract content type
    content_type = request.META.get('CONTENT_TYPE', '')
    if content_type:
        headers['Content-Type'] = content_type
    
    # Extract Accept header
    accept = request.META.get('HTTP_ACCEPT', '')
    if accept:
        headers['Accept'] = accept
    
    # Extract X-TAXII headers
    for key, value in request.META.items():
        if key.startswith('HTTP_X_TAXII_'):
            header_name = key[5:].replace('_', '-').title()
            headers[header_name] = value
    
    return headers


def validate_content_type(request, expected_type: str) -> bool:
    """
    Validate that the request content type matches the expected type.
    
    Args:
        request: Django request object
        expected_type: Expected content type
        
    Returns:
        True if content type matches, False otherwise
    """
    content_type = request.META.get('CONTENT_TYPE', '')
    return content_type.startswith(expected_type)


def validate_accept_header(request, expected_type: str) -> bool:
    """
    Validate that the request Accept header matches the expected type.
    
    Args:
        request: Django request object
        expected_type: Expected Accept header
        
    Returns:
        True if Accept header matches, False otherwise
    """
    accept = request.META.get('HTTP_ACCEPT', '')
    
    # If no Accept header is provided, assume default
    if not accept:
        return True
        
    # Check if any of the accepted types match the expected type
    accept_types = [t.strip() for t in accept.split(',')]
    for accept_type in accept_types:
        if accept_type.startswith(expected_type) or accept_type == '*/*':
            return True
            
    return False


def create_taxii_response(data: Dict[str, Any], media_type: str = None) -> HttpResponse:
    """
    Create an HTTP response with the appropriate TAXII headers.
    
    Args:
        data: Response data
        media_type: Media type for response
        
    Returns:
        Django HttpResponse object
    """
    if media_type is None:
        media_type = settings.TAXII_SETTINGS.get('MEDIA_TYPE_TAXII', 'application/taxii+json;version=2.1')
        
    response = HttpResponse(
        json.dumps(data),
        content_type=media_type
    )
    
    # Add TAXII headers
    response['X-TAXII-Date-Added-First'] = datetime.now().isoformat() + 'Z'
    response['X-TAXII-Date-Added-Last'] = datetime.now().isoformat() + 'Z'
    
    return response


def create_taxii_error_response(
    title: str, 
    description: str = None, 
    error_code: str = None,
    http_status: int = 400
) -> HttpResponse:
    """
    Create an HTTP response for a TAXII error.
    
    Args:
        title: Error title
        description: Error description
        error_code: Error code
        http_status: HTTP status code
        
    Returns:
        Django HttpResponse object
    """
    error_data = {
        'title': title,
        'error_id': str(uuid.uuid4()),
        'http_status': http_status
    }
    
    if description:
        error_data['description'] = description
        
    if error_code:
        error_data['error_code'] = error_code
        
    media_type = settings.TAXII_SETTINGS.get('MEDIA_TYPE_TAXII', 'application/taxii+json;version=2.1')
    
    response = HttpResponse(
        json.dumps(error_data),
        content_type=media_type,
        status=http_status
    )
    
    return response


def get_stix_bundle_from_request(request) -> Dict[str, Any]:
    """
    Extract a STIX bundle from a request.
    
    Args:
        request: Django request object
        
    Returns:
        STIX bundle as dictionary
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        # Check if it's a STIX bundle
        if isinstance(data, dict) and data.get('type') == 'bundle' and 'objects' in data:
            return data
            
        # Check if it's a STIX object
        if isinstance(data, dict) and 'type' in data and 'id' in data:
            # Wrap in a bundle
            return {
                'type': 'bundle',
                'id': f'bundle--{str(uuid.uuid4())}',
                'objects': [data],
                'spec_version': '2.1'
            }
            
        # Check if it's a list of STIX objects
        if isinstance(data, list) and all('type' in obj and 'id' in obj for obj in data):
            # Wrap in a bundle
            return {
                'type': 'bundle',
                'id': f'bundle--{str(uuid.uuid4())}',
                'objects': data,
                'spec_version': '2.1'
            }
            
        raise ValueError("Invalid STIX data")
        
    except Exception as e:
        raise ValueError(f"Error parsing STIX data: {str(e)}")


def parse_taxii_filters(request) -> Dict[str, Any]:
    """
    Parse TAXII filters from request query parameters.
    
    Args:
        request: Django request object
        
    Returns:
        Dictionary of filters
    """
    filters = {}
    
    # added_after filter
    added_after = request.GET.get('added_after')
    if added_after:
        try:
            added_after_date = datetime.fromisoformat(added_after.replace('Z', '+00:00'))
            filters['added_after'] = added_after_date
        except ValueError:
            pass
    
    # STIX object type filter
    object_type = request.GET.get('type')
    if object_type:
        filters['stix_type'] = object_type
    
    # STIX object ID filter
    object_id = request.GET.get('id')
    if object_id:
        filters['stix_id'] = object_id
    
    # STIX spec version filter
    spec_version = request.GET.get('spec_version')
    if spec_version:
        filters['spec_version'] = spec_version
    
    # version filter
    version = request.GET.get('version')
    if version:
        if version == 'first':
            filters['version'] = 'first'
        elif version == 'last':
            filters['version'] = 'last'
        elif version == 'all':
            filters['version'] = 'all'
        elif version:
            try:
                # version is an ISO datetime
                version_date = datetime.fromisoformat(version.replace('Z', '+00:00'))
                filters['version'] = version_date
            except ValueError:
                pass
    
    # pagination filters
    limit = request.GET.get('limit')
    if limit:
        try:
            filters['limit'] = int(limit)
        except ValueError:
            filters['limit'] = 100
    else:
        filters['limit'] = 100
    
    offset = request.GET.get('offset')
    if offset:
        try:
            filters['offset'] = int(offset)
        except ValueError:
            filters['offset'] = 0
    else:
        filters['offset'] = 0
    
    return filters


def get_taxii_pagination_info(count: int, limit: int, offset: int, request) -> Dict[str, Any]:
    """
    Generate pagination info for TAXII responses.
    
    Args:
        count: Total number of objects
        limit: Number of objects per page
        offset: Offset from the beginning
        request: Django request object
        
    Returns:
        Dictionary with pagination info
    """
    pagination = {}
    
    # Check if there are more objects
    if offset + limit < count:
        pagination['more'] = True
        
        # Generate next URL
        next_offset = offset + limit
        base_url = request.build_absolute_uri().split('?')[0]
        
        # Copy query parameters
        query_params = request.GET.copy()
        query_params['limit'] = limit
        query_params['offset'] = next_offset
        
        # Build query string
        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        pagination['next'] = f"{base_url}?{query_string}"
    else:
        pagination['more'] = False
    
    return pagination