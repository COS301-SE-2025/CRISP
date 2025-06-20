"""
TAXII Service for CRISP Threat Intelligence Platform

This service implements the TAXII 2.1 specification for threat intelligence sharing
using the CRISP design patterns (Service Layer, Repository Layer, Strategy Pattern).
"""

import json
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone as dt_timezone
from urllib.parse import urljoin

from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import Http404
from django.core.exceptions import PermissionDenied

from ..domain.models import (
    Institution, User, Collection, STIXObject, AuditLog,
    TrustRelationship, CollectionAccess
)
from ..repositories.base import BaseRepository
from ..strategies.anonymization_strategy import AnonymizationContext
from ..config.security import get_security_config

logger = logging.getLogger(__name__)

class TAXIIServiceError(Exception):
    """Base exception for TAXII service errors"""
    pass

class TAXIIAuthenticationError(TAXIIServiceError):
    """Authentication failed"""
    pass

class TAXIIAuthorizationError(TAXIIServiceError):
    """Authorization failed"""
    pass

class TAXIIValidationError(TAXIIServiceError):
    """STIX/TAXII validation failed"""
    pass

class TAXIIService:
    """
    TAXII 2.1 Service implementing the service layer pattern
    
    This service handles all TAXII operations including:
    - Server discovery
    - Collection management
    - Object retrieval and filtering
    - Bundle creation and publication
    - Access control and trust-based anonymization
    """
    
    def __init__(self):
        """Initialize TAXII service with dependencies"""
        self.security_config = get_security_config()
        self.anonymization_context = AnonymizationContext()
        
        # TAXII specification compliance
        self.taxii_version = "2.1"
        self.media_types = [
            "application/taxii+json;version=2.1",
            "application/stix+json;version=2.1"
        ]
        
        # Service configuration
        self.max_content_length = 10 * 1024 * 1024  # 10MB
        self.default_page_size = 20
        self.max_page_size = 100
    
    def get_discovery_information(self, request_institution: Institution) -> Dict[str, Any]:
        """
        Get TAXII server discovery information
        
        Args:
            request_institution: Institution making the request
            
        Returns:
            TAXII discovery response
        """
        try:
            # Log discovery request
            AuditLog.log_action(
                institution=request_institution,
                action='read',
                resource_type='taxii_discovery',
                details={'endpoint': 'discovery'}
            )
            
            return {
                "title": "CRISP Threat Intelligence Platform TAXII Server",
                "description": "TAXII 2.1 server for sharing threat intelligence",
                "contact": self.security_config.get('contact_email', 'admin@crisp-platform.org'),
                "default": f"/taxii2/api/",
                "api_roots": [
                    f"/taxii2/api/"
                ]
            }
            
        except Exception as e:
            logger.error(f"Discovery request failed: {e}")
            raise TAXIIServiceError(f"Discovery failed: {e}")
    
    def get_api_root_information(self, request_institution: Institution) -> Dict[str, Any]:
        """
        Get API root information
        
        Args:
            request_institution: Institution making the request
            
        Returns:
            API root information
        """
        try:
            # Get collections accessible to this institution
            accessible_collections = self._get_accessible_collections(request_institution)
            
            # Log API root request
            AuditLog.log_action(
                institution=request_institution,
                action='read',
                resource_type='taxii_api_root',
                details={'collections_count': len(accessible_collections)}
            )
            
            return {
                "title": "CRISP TAXII API Root",
                "description": "Primary API root for CRISP threat intelligence sharing",
                "versions": ["taxii-2.1"],
                "max_content_length": self.max_content_length
            }
            
        except Exception as e:
            logger.error(f"API root request failed: {e}")
            raise TAXIIServiceError(f"API root request failed: {e}")
    
    def get_collections(self, request_institution: Institution, 
                       request_user: User = None) -> Dict[str, Any]:
        """
        Get collections accessible to the requesting institution
        
        Args:
            request_institution: Institution making the request
            request_user: User making the request (optional)
            
        Returns:
            TAXII collections response
        """
        try:
            collections = []
            accessible_collections = self._get_accessible_collections(request_institution)
            
            for collection in accessible_collections:
                # Check specific access permissions
                can_read = collection.can_access(request_institution, 'read')
                can_write = collection.can_access(request_institution, 'write')
                
                if can_read:
                    collections.append({
                        "id": collection.collection_id,
                        "title": collection.title,
                        "description": collection.description,
                        "can_read": can_read,
                        "can_write": can_write,
                        "media_types": collection.media_types
                    })
            
            # Log collections request
            AuditLog.log_action(
                user=request_user,
                institution=request_institution,
                action='read',
                resource_type='taxii_collections',
                details={'collections_returned': len(collections)}
            )
            
            return {
                "collections": collections
            }
            
        except Exception as e:
            logger.error(f"Collections request failed: {e}")
            raise TAXIIServiceError(f"Collections request failed: {e}")
    
    def get_collection(self, collection_id: str, request_institution: Institution,
                      request_user: User = None) -> Dict[str, Any]:
        """
        Get specific collection information
        
        Args:
            collection_id: Collection identifier
            request_institution: Institution making the request
            request_user: User making the request (optional)
            
        Returns:
            TAXII collection response
        """
        try:
            collection = self._get_collection_or_404(collection_id)
            
            # Check access permissions
            if not collection.can_access(request_institution, 'read'):
                raise TAXIIAuthorizationError("Access denied to collection")
            
            # Log collection request
            AuditLog.log_action(
                user=request_user,
                institution=request_institution,
                action='read',
                resource_type='taxii_collection',
                resource_id=collection_id
            )
            
            return collection.to_taxii_collection()
            
        except Collection.DoesNotExist:
            raise Http404("Collection not found")
        except Exception as e:
            logger.error(f"Collection request failed: {e}")
            raise TAXIIServiceError(f"Collection request failed: {e}")
    
    def get_objects(self, collection_id: str, request_institution: Institution,
                   filters: Dict[str, Any] = None, limit: int = None,
                   added_after: datetime = None, next_param: str = None,
                   request_user: User = None) -> Dict[str, Any]:
        """
        Get STIX objects from collection with filtering and pagination
        
        Args:
            collection_id: Collection identifier
            request_institution: Institution making the request
            filters: TAXII filters (type, id, etc.)
            limit: Maximum number of objects to return
            added_after: Filter objects added after this date
            next_param: Pagination parameter
            request_user: User making the request (optional)
            
        Returns:
            TAXII objects response with anonymization applied
        """
        try:
            collection = self._get_collection_or_404(collection_id)
            
            # Check access permissions
            if not collection.can_access(request_institution, 'read'):
                raise TAXIIAuthorizationError("Access denied to collection")
            
            # Build query
            queryset = STIXObject.objects.filter(collection=collection, revoked=False)
            
            # Apply filters
            if filters:
                queryset = self._apply_stix_filters(queryset, filters)
            
            if added_after:
                queryset = queryset.filter(created_at__gt=added_after)
            
            # Handle pagination
            page_size = min(limit or self.default_page_size, self.max_page_size)
            paginator = Paginator(queryset.order_by('-created_at'), page_size)
            
            page_number = self._decode_next_param(next_param) if next_param else 1
            page_obj = paginator.get_page(page_number)
            
            # Get trust level for anonymization
            trust_level = request_institution.get_trust_level_for(collection.institution)
            
            # Process objects with anonymization
            objects = []
            for stix_obj in page_obj:
                # Apply anonymization based on trust level
                anonymized_data = self._anonymize_stix_object(
                    stix_obj.raw_data, 
                    trust_level, 
                    request_institution
                )
                objects.append(anonymized_data)
            
            # Prepare response
            response = {
                "objects": objects
            }
            
            # Add pagination info
            if page_obj.has_next():
                response["next"] = self._encode_next_param(page_obj.next_page_number())
            
            if page_obj.has_previous():
                response["x-taxii-date-added-first"] = page_obj[0].created_at.isoformat()
            
            if objects:
                response["x-taxii-date-added-last"] = page_obj[-1].created_at.isoformat()
            
            # Log objects request
            AuditLog.log_action(
                user=request_user,
                institution=request_institution,
                action='read',
                resource_type='taxii_objects',
                resource_id=collection_id,
                details={
                    'objects_returned': len(objects),
                    'trust_level': trust_level,
                    'filters_applied': filters,
                    'page': page_number
                }
            )
            
            return response
            
        except Collection.DoesNotExist:
            raise Http404("Collection not found")
        except Exception as e:
            logger.error(f"Objects request failed: {e}")
            raise TAXIIServiceError(f"Objects request failed: {e}")
    
    def get_object(self, collection_id: str, object_id: str, 
                  request_institution: Institution, request_user: User = None) -> Dict[str, Any]:
        """
        Get specific STIX object from collection
        
        Args:
            collection_id: Collection identifier
            object_id: STIX object identifier
            request_institution: Institution making the request
            request_user: User making the request (optional)
            
        Returns:
            STIX object with anonymization applied
        """
        try:
            collection = self._get_collection_or_404(collection_id)
            
            # Check access permissions
            if not collection.can_access(request_institution, 'read'):
                raise TAXIIAuthorizationError("Access denied to collection")
            
            # Get STIX object
            try:
                stix_obj = STIXObject.objects.get(
                    collection=collection,
                    stix_id=object_id,
                    revoked=False
                )
            except STIXObject.DoesNotExist:
                raise Http404("Object not found")
            
            # Get trust level and apply anonymization
            trust_level = request_institution.get_trust_level_for(collection.institution)
            anonymized_data = self._anonymize_stix_object(
                stix_obj.raw_data, 
                trust_level, 
                request_institution
            )
            
            # Log object request
            AuditLog.log_action(
                user=request_user,
                institution=request_institution,
                action='read',
                resource_type='taxii_object',
                resource_id=object_id,
                details={
                    'collection_id': collection_id,
                    'trust_level': trust_level
                }
            )
            
            return anonymized_data
            
        except Collection.DoesNotExist:
            raise Http404("Collection not found")
        except Exception as e:
            logger.error(f"Object request failed: {e}")
            raise TAXIIServiceError(f"Object request failed: {e}")
    
    def add_objects(self, collection_id: str, objects: List[Dict[str, Any]],
                   request_institution: Institution, request_user: User = None) -> Dict[str, Any]:
        """
        Add STIX objects to collection
        
        Args:
            collection_id: Collection identifier
            objects: List of STIX objects to add
            request_institution: Institution making the request
            request_user: User making the request (optional)
            
        Returns:
            TAXII status response
        """
        try:
            collection = self._get_collection_or_404(collection_id)
            
            # Check write permissions
            if not collection.can_access(request_institution, 'write'):
                raise TAXIIAuthorizationError("Write access denied to collection")
            
            successes = []
            failures = []
            
            with transaction.atomic():
                for obj_data in objects:
                    try:
                        # Validate STIX object
                        self._validate_stix_object(obj_data)
                        
                        # Create or update STIX object
                        stix_obj, created = STIXObject.objects.update_or_create(
                            stix_id=obj_data['id'],
                            defaults={
                                'stix_type': obj_data['type'],
                                'raw_data': obj_data,
                                'institution': request_institution,
                                'collection': collection,
                                'created_by': request_user
                            }
                        )
                        
                        successes.append({
                            "id": obj_data['id'],
                            "version": obj_data.get('modified', obj_data.get('created'))
                        })
                        
                    except Exception as e:
                        failures.append({
                            "id": obj_data.get('id', 'unknown'),
                            "message": str(e)
                        })
            
            # Log add objects request
            AuditLog.log_action(
                user=request_user,
                institution=request_institution,
                action='create',
                resource_type='taxii_objects',
                resource_id=collection_id,
                details={
                    'objects_added': len(successes),
                    'objects_failed': len(failures),
                    'total_objects': len(objects)
                }
            )
            
            response = {
                "id": str(uuid.uuid4()),
                "status": "complete",
                "request_timestamp": timezone.now().isoformat(),
                "total_count": len(objects),
                "success_count": len(successes),
                "failure_count": len(failures)
            }
            
            if successes:
                response["successes"] = successes
            
            if failures:
                response["failures"] = failures
            
            return response
            
        except Collection.DoesNotExist:
            raise Http404("Collection not found")
        except Exception as e:
            logger.error(f"Add objects failed: {e}")
            raise TAXIIServiceError(f"Add objects failed: {e}")
    
    def get_manifest(self, collection_id: str, request_institution: Institution,
                    filters: Dict[str, Any] = None, added_after: datetime = None,
                    limit: int = None, next_param: str = None,
                    request_user: User = None) -> Dict[str, Any]:
        """
        Get manifest of objects in collection
        
        Args:
            collection_id: Collection identifier
            request_institution: Institution making the request
            filters: TAXII filters
            added_after: Filter objects added after this date
            limit: Maximum number of manifest entries
            next_param: Pagination parameter
            request_user: User making the request (optional)
            
        Returns:
            TAXII manifest response
        """
        try:
            collection = self._get_collection_or_404(collection_id)
            
            # Check access permissions
            if not collection.can_access(request_institution, 'read'):
                raise TAXIIAuthorizationError("Access denied to collection")
            
            # Build query
            queryset = STIXObject.objects.filter(collection=collection, revoked=False)
            
            # Apply filters
            if filters:
                queryset = self._apply_stix_filters(queryset, filters)
            
            if added_after:
                queryset = queryset.filter(created_at__gt=added_after)
            
            # Handle pagination
            page_size = min(limit or self.default_page_size, self.max_page_size)
            paginator = Paginator(queryset.order_by('-created_at'), page_size)
            
            page_number = self._decode_next_param(next_param) if next_param else 1
            page_obj = paginator.get_page(page_number)
            
            # Build manifest entries
            objects = []
            for stix_obj in page_obj:
                objects.append({
                    "id": stix_obj.stix_id,
                    "date_added": stix_obj.created_at.isoformat(),
                    "version": stix_obj.modified_time.isoformat(),
                    "media_type": "application/stix+json;version=2.1"
                })
            
            # Prepare response
            response = {
                "objects": objects
            }
            
            # Add pagination info
            if page_obj.has_next():
                response["next"] = self._encode_next_param(page_obj.next_page_number())
            
            # Log manifest request
            AuditLog.log_action(
                user=request_user,
                institution=request_institution,
                action='read',
                resource_type='taxii_manifest',
                resource_id=collection_id,
                details={
                    'objects_returned': len(objects),
                    'filters_applied': filters,
                    'page': page_number
                }
            )
            
            return response
            
        except Collection.DoesNotExist:
            raise Http404("Collection not found")
        except Exception as e:
            logger.error(f"Manifest request failed: {e}")
            raise TAXIIServiceError(f"Manifest request failed: {e}")
    
    def create_collection(self, title: str, description: str, 
                         institution: Institution, user: User,
                         can_read: bool = True, can_write: bool = False,
                         is_public: bool = False) -> Collection:
        """
        Create a new TAXII collection
        
        Args:
            title: Collection title
            description: Collection description
            institution: Owning institution
            user: User creating the collection
            can_read: Whether collection supports reading
            can_write: Whether collection supports writing
            is_public: Whether collection is publicly accessible
            
        Returns:
            Created collection
        """
        try:
            with transaction.atomic():
                collection = Collection.objects.create(
                    title=title,
                    description=description,
                    institution=institution,
                    can_read=can_read,
                    can_write=can_write,
                    is_public=is_public,
                    created_by=user
                )
                
                # Log collection creation
                AuditLog.log_action(
                    user=user,
                    institution=institution,
                    action='create',
                    resource_type='taxii_collection',
                    resource_id=collection.collection_id,
                    details={
                        'title': title,
                        'can_read': can_read,
                        'can_write': can_write,
                        'is_public': is_public
                    }
                )
                
                return collection
                
        except Exception as e:
            logger.error(f"Collection creation failed: {e}")
            raise TAXIIServiceError(f"Collection creation failed: {e}")
    
    # Helper methods
    
    def _get_accessible_collections(self, institution: Institution) -> List[Collection]:
        """Get collections accessible to institution"""
        # Own collections
        own_collections = Collection.objects.filter(institution=institution)
        
        # Public collections
        public_collections = Collection.objects.filter(is_public=True, can_read=True)
        
        # Explicitly authorized collections
        authorized_collections = Collection.objects.filter(
            authorized_institutions=institution,
            collectionaccess__is_active=True
        )
        
        # Combine and deduplicate
        all_collections = set(own_collections) | set(public_collections) | set(authorized_collections)
        return list(all_collections)
    
    def _get_collection_or_404(self, collection_id: str) -> Collection:
        """Get collection or raise 404"""
        try:
            return Collection.objects.get(collection_id=collection_id)
        except Collection.DoesNotExist:
            raise Http404("Collection not found")
    
    def _apply_stix_filters(self, queryset, filters: Dict[str, Any]):
        """Apply STIX filters to queryset"""
        if 'type' in filters:
            types = filters['type'] if isinstance(filters['type'], list) else [filters['type']]
            queryset = queryset.filter(stix_type__in=types)
        
        if 'id' in filters:
            ids = filters['id'] if isinstance(filters['id'], list) else [filters['id']]
            queryset = queryset.filter(stix_id__in=ids)
        
        if 'added_after' in filters:
            added_after = datetime.fromisoformat(filters['added_after'].replace('Z', '+00:00'))
            queryset = queryset.filter(created_at__gt=added_after)
        
        return queryset
    
    def _anonymize_stix_object(self, stix_data: Dict[str, Any], 
                              trust_level: float, 
                              requesting_institution: Institution) -> Dict[str, Any]:
        """Apply anonymization based on trust level"""
        # Determine anonymization strategy based on trust level
        if trust_level >= 0.8:
            strategy_name = 'none'  # High trust, no anonymization
        elif trust_level >= 0.5:
            strategy_name = 'partial'  # Medium trust, partial anonymization
        else:
            strategy_name = 'full'  # Low/no trust, full anonymization
        
        # Apply anonymization using strategy pattern
        return self.anonymization_context.anonymize_stix_object(
            stix_data, 
            strategy_name,
            requesting_institution
        )
    
    def _validate_stix_object(self, obj_data: Dict[str, Any]):
        """Validate STIX object"""
        required_fields = ['type', 'id', 'created', 'modified']
        
        for field in required_fields:
            if field not in obj_data:
                raise TAXIIValidationError(f"Missing required field: {field}")
        
        # Additional STIX validation can be added here
        if self.security_config.get('stix_validation_strict', True):
            # Implement strict STIX validation
            pass
    
    def _encode_next_param(self, page_number: int) -> str:
        """Encode pagination parameter"""
        import base64
        return base64.b64encode(f"page:{page_number}".encode()).decode()
    
    def _decode_next_param(self, next_param: str) -> int:
        """Decode pagination parameter"""
        try:
            import base64
            decoded = base64.b64decode(next_param.encode()).decode()
            if decoded.startswith("page:"):
                return int(decoded.split(":")[1])
            return 1
        except Exception:
            return 1