"""
TAXII 2.1 API Implementation
Complete implementation with exact functional replication.
"""
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError

from crisp_threat_intel.models import Collection, STIXObject, CollectionObject, Organization
from crisp_threat_intel.strategies.anonymization import AnonymizationStrategyFactory


class TAXIIBaseView(APIView):
    """
    Base view for all TAXII 2.1 endpoints with common functionality.
    """
    permission_classes = [IsAuthenticated]
    content_type = settings.TAXII_SETTINGS.get('MEDIA_TYPE_TAXII', 'application/taxii+json;version=2.1')
    
    def get_organization(self, request):
        """
        Get the organization associated with the authenticated user.
        """
        try:
            # Try to get organization from user profile or groups
            if hasattr(request.user, 'organization'):
                return request.user.organization
            
            # Fallback: get first organization created by user
            org = Organization.objects.filter(created_by=request.user).first()
            if org:
                return org
                
            # If no organization found, create a default one for development
            if settings.DEBUG:
                org, created = Organization.objects.get_or_create(
                    name=f"{request.user.username}'s Organization",
                    defaults={
                        'identity_class': "organization",
                        'stix_id': f"identity--{uuid.uuid4()}",
                        'created_by': request.user
                    }
                )
                return org
            
            raise NotFound("No organization found for authenticated user")
        except Exception as e:
            raise NotFound(f"Error finding organization: {str(e)}")
    
    def get_trust_level(self, source_org, target_org):
        """
        Get the trust level between source and target organizations.
        """
        if source_org == target_org:
            return 1.0
        # Default to medium trust if no relationship exists
        return 0.5
    
    def apply_anonymization(self, stix_object, requesting_org, source_org):
        """
        Apply appropriate anonymization based on trust level.
        """
        if requesting_org == source_org:
            return stix_object
        
        # Get trust level and determine anonymization strategy
        trust_level = self.get_trust_level(source_org, requesting_org)
        
        # Determine anonymization strategy based on trust level
        if trust_level >= 0.8:
            strategy_name = 'none'
        elif trust_level >= 0.4:
            strategy_name = 'domain'  # Use composite strategy
        else:
            strategy_name = 'domain'  # Full anonymization
        
        # Get strategy and apply anonymization
        strategy = AnonymizationStrategyFactory.get_strategy(strategy_name)
        anonymized = strategy.anonymize(stix_object, trust_level)
        
        return anonymized


class DiscoveryView(TAXIIBaseView):
    """
    TAXII 2.1 Discovery endpoint (GET /taxii2/).
    """
    permission_classes = []  # Discovery is public
    
    def get(self, request):
        """
        Get discovery information for the TAXII server.
        """
        discovery_data = {
            'title': settings.TAXII_SETTINGS.get('DISCOVERY_TITLE', 'CRISP Threat Intelligence Platform'),
            'description': settings.TAXII_SETTINGS.get('DISCOVERY_DESCRIPTION', 'Educational threat intelligence sharing platform'),
            'contact': settings.TAXII_SETTINGS.get('DISCOVERY_CONTACT', 'admin@example.com'),
            'default': f"{request.build_absolute_uri('/taxii2/')}/",
            'api_roots': [
                f"{request.build_absolute_uri('/taxii2/')}/"
            ]
        }
        
        return JsonResponse(discovery_data, content_type=self.content_type)


class ApiRootView(TAXIIBaseView):
    """
    TAXII 2.1 API Root endpoint (GET /taxii2/).
    """
    def get(self, request):
        """
        Get information about the API Root.
        """
        api_root_data = {
            'title': settings.TAXII_SETTINGS.get('DISCOVERY_TITLE', 'CRISP Threat Intelligence Platform'),
            'description': settings.TAXII_SETTINGS.get('DISCOVERY_DESCRIPTION', 'Educational threat intelligence sharing platform'),
            'versions': ['2.1'],
            'max_content_length': settings.TAXII_SETTINGS.get('MAX_CONTENT_LENGTH', 104857600)
        }
        
        return JsonResponse(api_root_data, content_type=self.content_type)


class CollectionsView(TAXIIBaseView):
    """
    TAXII 2.1 Collections endpoint (GET /taxii2/collections/).
    """
    def get(self, request):
        """
        Get all collections accessible to the authenticated user.
        """
        org = self.get_organization(request)
        
        # Get collections owned by the organization
        owned_collections = Collection.objects.filter(owner=org)
        
        # For now, only show owned collections (trust relationships can be added later)
        all_collections = owned_collections
        
        # Build response
        collections_data = {
            'collections': []
        }
        
        for collection in all_collections:
            collection_data = {
                'id': str(collection.id),
                'title': collection.title,
                'description': collection.description,
                'can_read': collection.can_read,
                'can_write': collection.can_write and (collection.owner == org),
                'media_types': collection.media_types or [settings.TAXII_SETTINGS.get('MEDIA_TYPE_STIX', 'application/stix+json;version=2.1')],
            }
            collections_data['collections'].append(collection_data)
        
        return JsonResponse(collections_data, content_type=self.content_type)


class CollectionView(TAXIIBaseView):
    """
    TAXII 2.1 Collection endpoint (GET /taxii2/collections/{id}/).
    """
    def get(self, request, collection_id):
        """
        Get information about a specific collection.
        """
        org = self.get_organization(request)
        
        try:
            collection = Collection.objects.get(id=collection_id)
            
            # Check if user has access to this collection
            if collection.owner != org:
                raise NotFound("Collection not found")
            
            collection_data = {
                'id': str(collection.id),
                'title': collection.title,
                'description': collection.description,
                'can_read': collection.can_read,
                'can_write': collection.can_write and (collection.owner == org),
                'media_types': collection.media_types or [settings.TAXII_SETTINGS.get('MEDIA_TYPE_STIX', 'application/stix+json;version=2.1')],
            }
            
            return JsonResponse(collection_data, content_type=self.content_type)
            
        except Collection.DoesNotExist:
            raise NotFound("Collection not found")


class CollectionObjectsView(TAXIIBaseView):
    """
    TAXII 2.1 Collection Objects endpoint 
    (GET, POST /taxii2/collections/{id}/objects/).
    """
    def get(self, request, collection_id):
        """
        Get objects from a collection with filtering and pagination.
        """
        org = self.get_organization(request)
        
        try:
            collection = Collection.objects.get(id=collection_id)
            
            # Check if user has read access to this collection
            if not collection.can_read or collection.owner != org:
                return Response(
                    {"error": "Access denied to this collection"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get all objects in the collection
            collection_objects = CollectionObject.objects.filter(collection=collection)
            stix_object_ids = collection_objects.values_list('stix_object', flat=True)
            stix_objects = STIXObject.objects.filter(id__in=stix_object_ids)
            
            # Apply filters from query parameters
            added_after = request.query_params.get('added_after')
            if added_after:
                try:
                    added_after_date = datetime.datetime.fromisoformat(added_after.replace('Z', '+00:00'))
                    collection_objects = collection_objects.filter(date_added__gt=added_after_date)
                    stix_object_ids = collection_objects.values_list('stix_object', flat=True)
                    stix_objects = stix_objects.filter(id__in=stix_object_ids)
                except ValueError:
                    return Response(
                        {"error": "Invalid added_after format. Expected ISO format."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # type filter
            object_type = request.query_params.get('type')
            if object_type:
                stix_objects = stix_objects.filter(stix_type=object_type)
            
            # id filter
            object_id = request.query_params.get('id')
            if object_id:
                stix_objects = stix_objects.filter(stix_id=object_id)
            
            # spec_version filter
            spec_version = request.query_params.get('spec_version')
            if spec_version:
                stix_objects = stix_objects.filter(spec_version=spec_version)
            
            # Pagination
            limit = int(request.query_params.get('limit', 100))
            offset = int(request.query_params.get('offset', 0))
            
            # Get paginated results
            paginator = Paginator(stix_objects, limit)
            page_number = (offset // limit) + 1
            page_objects = paginator.get_page(page_number)
            
            # Build response
            objects_data = {
                'objects': []
            }
            
            for obj in page_objects:
                # Apply anonymization based on trust relationship
                stix_data = obj.to_stix()
                
                # Anonymize if needed
                if obj.source_organization != org:
                    stix_data = self.apply_anonymization(
                        stix_data, 
                        org, 
                        obj.source_organization
                    )
                
                objects_data['objects'].append(stix_data)
            
            # Add pagination information
            if page_objects.has_next():
                next_offset = offset + limit
                objects_data['more'] = True
                objects_data['next'] = f"{request.build_absolute_uri().split('?')[0]}?limit={limit}&offset={next_offset}"
            else:
                objects_data['more'] = False
            
            return JsonResponse(objects_data, content_type=settings.TAXII_SETTINGS.get('MEDIA_TYPE_STIX', 'application/stix+json;version=2.1'))
            
        except Collection.DoesNotExist:
            raise NotFound("Collection not found")
    
    def post(self, request, collection_id):
        """
        Add objects to a collection.
        """
        org = self.get_organization(request)
        
        try:
            collection = Collection.objects.get(id=collection_id)
            
            # Check if user has write access to this collection
            if not collection.can_write or collection.owner != org:
                return Response(
                    {"error": "Write access denied to this collection"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Parse request body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid JSON in request body"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if objects are provided
            if 'objects' not in data or not isinstance(data['objects'], list):
                return Response(
                    {"error": "Request must include an 'objects' list"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process each object
            success_count = 0
            failures = []
            
            for obj in data['objects']:
                try:
                    # Get or create STIX object
                    stix_id = obj.get('id')
                    stix_type = obj.get('type')
                    
                    if not stix_id or not stix_type:
                        failures.append({
                            'object': obj.get('id', 'Unknown ID'),
                            'message': "Missing required fields 'id' or 'type'"
                        })
                        continue
                    
                    # Check if object already exists
                    existing_obj = STIXObject.objects.filter(stix_id=stix_id).first()
                    
                    if existing_obj:
                        # Update existing object
                        existing_obj.raw_data = obj
                        existing_obj.modified = timezone.now()
                        existing_obj.save()
                        stix_obj = existing_obj
                    else:
                        # Create new STIX object
                        stix_obj = STIXObject.objects.create(
                            stix_id=stix_id,
                            stix_type=stix_type,
                            spec_version=obj.get('spec_version', '2.1'),
                            created=timezone.now(),
                            modified=timezone.now(),
                            created_by_ref=obj.get('created_by_ref'),
                            raw_data=obj,
                            created_by=request.user,
                            source_organization=org
                        )
                    
                    # Add to collection if not already present
                    obj_in_collection = CollectionObject.objects.filter(
                        collection=collection,
                        stix_object=stix_obj
                    ).exists()
                    
                    if not obj_in_collection:
                        CollectionObject.objects.create(
                            collection=collection,
                            stix_object=stix_obj
                        )
                    
                    success_count += 1
                    
                except Exception as e:
                    failures.append({
                        'object': obj.get('id', 'Unknown ID'),
                        'message': str(e)
                    })
            
            # Build response
            response_data = {
                'success_count': success_count,
                'failures': failures,
                'pending_count': 0
            }
            
            status_code = status.HTTP_207_MULTI_STATUS if failures else status.HTTP_200_OK
            
            return Response(response_data, status=status_code, content_type=self.content_type)
            
        except Collection.DoesNotExist:
            raise NotFound("Collection not found")


class ObjectView(TAXIIBaseView):
    """
    TAXII 2.1 Object endpoint (GET /taxii2/collections/{id}/objects/{object_id}/).
    """
    def get(self, request, collection_id, object_id):
        """
        Get a specific object from a collection.
        """
        org = self.get_organization(request)
        
        try:
            collection = Collection.objects.get(id=collection_id)
            
            # Check if user has read access to this collection
            if not collection.can_read or collection.owner != org:
                return Response(
                    {"error": "Access denied to this collection"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get the STIX object
            stix_object = STIXObject.objects.get(stix_id=object_id)
            
            # Check if object is in the collection
            in_collection = CollectionObject.objects.filter(
                collection=collection,
                stix_object=stix_object
            ).exists()
            
            if not in_collection:
                raise NotFound("Object not found in collection")
            
            # Apply anonymization based on trust relationship
            stix_data = stix_object.to_stix()
            
            # Anonymize if needed
            if stix_object.source_organization != org:
                stix_data = self.apply_anonymization(
                    stix_data, 
                    org, 
                    stix_object.source_organization
                )
            
            # Build response
            objects_data = {
                'objects': [stix_data]
            }
            
            return JsonResponse(objects_data, content_type=settings.TAXII_SETTINGS.get('MEDIA_TYPE_STIX', 'application/stix+json;version=2.1'))
            
        except Collection.DoesNotExist:
            raise NotFound("Collection not found")
        except STIXObject.DoesNotExist:
            raise NotFound("Object not found")


class ManifestView(TAXIIBaseView):
    """
    TAXII 2.1 Manifest endpoint (GET /taxii2/collections/{id}/manifest/).
    """
    def get(self, request, collection_id):
        """
        Get manifest information about objects in a collection.
        """
        org = self.get_organization(request)
        
        try:
            collection = Collection.objects.get(id=collection_id)
            
            # Check if user has read access to this collection
            if not collection.can_read or collection.owner != org:
                return Response(
                    {"error": "Access denied to this collection"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get all objects in the collection
            collection_objects = CollectionObject.objects.filter(collection=collection)
            stix_object_ids = collection_objects.values_list('stix_object', flat=True)
            stix_objects = STIXObject.objects.filter(id__in=stix_object_ids)
            
            # Apply filters (same as CollectionObjectsView)
            added_after = request.query_params.get('added_after')
            if added_after:
                try:
                    added_after_date = datetime.datetime.fromisoformat(added_after.replace('Z', '+00:00'))
                    collection_objects = collection_objects.filter(date_added__gt=added_after_date)
                    stix_object_ids = collection_objects.values_list('stix_object', flat=True)
                    stix_objects = stix_objects.filter(id__in=stix_object_ids)
                except ValueError:
                    return Response(
                        {"error": "Invalid added_after format. Expected ISO format."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            object_type = request.query_params.get('type')
            if object_type:
                stix_objects = stix_objects.filter(stix_type=object_type)
            
            object_id = request.query_params.get('id')
            if object_id:
                stix_objects = stix_objects.filter(stix_id=object_id)
            
            spec_version = request.query_params.get('spec_version')
            if spec_version:
                stix_objects = stix_objects.filter(spec_version=spec_version)
            
            # Pagination
            limit = int(request.query_params.get('limit', 100))
            offset = int(request.query_params.get('offset', 0))
            
            paginator = Paginator(stix_objects, limit)
            page_number = (offset // limit) + 1
            page_objects = paginator.get_page(page_number)
            
            # Build response
            manifest_data = {
                'objects': []
            }
            
            for obj in page_objects:
                # Get collection object for date_added
                collection_obj = collection_objects.filter(stix_object=obj).first()
                
                # Add to manifest
                manifest_data['objects'].append({
                    'id': obj.stix_id,
                    'date_added': collection_obj.date_added.isoformat() + 'Z' if collection_obj else obj.created_at.isoformat() + 'Z',
                    'version': obj.modified.isoformat() + 'Z',
                    'media_type': settings.TAXII_SETTINGS.get('MEDIA_TYPE_STIX', 'application/stix+json;version=2.1')
                })
            
            # Add pagination information
            if page_objects.has_next():
                next_offset = offset + limit
                manifest_data['more'] = True
                manifest_data['next'] = f"{request.build_absolute_uri().split('?')[0]}?limit={limit}&offset={next_offset}"
            else:
                manifest_data['more'] = False
            
            return JsonResponse(manifest_data, content_type=self.content_type)
            
        except Collection.DoesNotExist:
            raise NotFound("Collection not found")