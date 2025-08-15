"""
Feed validation utilities
"""
from django.core.exceptions import ValidationError
from core.models.models import Feed, ThreatFeed

def validate_feed_config(feed_data):
    """Validate feed configuration before consumption"""
    errors = []
    
    # Handle both dict and model object
    if hasattr(feed_data, 'name'):  # Model object
        name = getattr(feed_data, 'name', None)
        title = getattr(feed_data, 'title', None)
        is_external = getattr(feed_data, 'is_external', False)
        taxii_server_url = getattr(feed_data, 'taxii_server_url', None)
        taxii_collection_id = getattr(feed_data, 'taxii_collection_id', None)
    else:  # Dict object
        name = feed_data.get('name')
        title = feed_data.get('title')
        is_external = feed_data.get('is_external', False)
        taxii_server_url = feed_data.get('taxii_server_url')
        taxii_collection_id = feed_data.get('taxii_collection_id')
    
    if not name and not title:
        errors.append("Feed must have a name or title")
    
    if is_external:
        if not taxii_server_url:
            errors.append("External feeds must have a TAXII server URL")
        if not taxii_collection_id:
            errors.append("External feeds must have a collection ID")
    
    if errors:
        return False, errors
    
    return True, []


def validate_publication_feed(feed_data):
    """
    Validate publication feed configuration
    """
    errors = []
    
    if not feed_data.get('title'):
        errors.append("Publication feed must have a title")
    
    if not feed_data.get('alias'):
        errors.append("Publication feed must have an alias")
    
    if not feed_data.get('collection'):
        errors.append("Publication feed must be associated with a collection")
    
    if errors:
        raise ValidationError(errors)
    
    return True