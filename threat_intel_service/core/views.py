import csv
import json
import io
import uuid
from typing import Dict, List, Any, Union
from datetime import datetime

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator

from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.models import Organization, STIXObject, Collection, CollectionObject, Feed
from core.serializers import (
    OrganizationSerializer, STIXObjectSerializer, CollectionSerializer, FeedSerializer,
    STIXIndicatorInputSerializer, STIXMalwareInputSerializer, 
    STIXAttackPatternInputSerializer, STIXThreatActorInputSerializer,
    STIXRelationshipInputSerializer, BulkUploadSerializer
)

from stix_factory.factory import STIXObjectFactoryRegistry
from stix_factory.validators import STIXValidator
from stix_factory.version_handler import STIXVersionHandler, STIXVersionDetector
from anonymization.strategy import AnonymizationStrategyFactory
from audit.models import AuditLog

# STIX input serializer mapping
STIX_INPUT_SERIALIZERS = {
    'indicator': STIXIndicatorInputSerializer,
    'malware': STIXMalwareInputSerializer,
    'attack-pattern': STIXAttackPatternInputSerializer,
    'threat-actor': STIXThreatActorInputSerializer,
    'relationship': STIXRelationshipInputSerializer
}


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Organizations.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]


class STIXObjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for STIX objects.
    """
    queryset = STIXObject.objects.all()
    serializer_class = STIXObjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['stix_type', 'created_by', 'source_organization', 'anonymized']
    search_fields = ['stix_id', 'raw_data']
    ordering_fields = ['created', 'modified', 'created_at', 'confidence']
    ordering = ['-created']
    
    def get_organization(self, request):
        """
        Get the organization associated with the authenticated user.
        """
        # In a real implementation, you would link users to organizations
        # For now, we'll use a dummy approach
        try:
            return Organization.objects.filter(
                id__in=request.user.groups.values_list('name', flat=True)
            ).first()
        except Organization.DoesNotExist:
            # If no organization is found, create a dummy one for development purposes
            # In production, this would raise an exception instead
            if settings.DEBUG:
                return Organization.objects.create(
                    name=f"{request.user.username}'s Organization",
                    identity_class="organization",
                    stix_id=f"identity--{uuid.uuid4()}"
                )
            raise Exception("No organization found for authenticated user")
    
    def perform_create(self, serializer):
        """
        Set the creator and source organization when creating a STIX object.
        """
        organization = self.get_organization(self.request)
        serializer.save(created_by=self.request.user, source_organization=organization)
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='create_stix_object',
            object_id=serializer.instance.stix_id,
            details={
                'stix_type': serializer.instance.stix_type,
                'stix_id': serializer.instance.stix_id
            }
        )
    
    def perform_update(self, serializer):
        """
        Log the update action.
        """
        organization = self.get_organization(self.request)
        serializer.save()
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='update_stix_object',
            object_id=serializer.instance.stix_id,
            details={
                'stix_type': serializer.instance.stix_type,
                'stix_id': serializer.instance.stix_id
            }
        )
    
    def perform_destroy(self, instance):
        """
        Log the delete action.
        """
        organization = self.get_organization(self.request)
        stix_id = instance.stix_id
        stix_type = instance.stix_type
        
        instance.delete()
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='delete_stix_object',
            object_id=stix_id,
            details={
                'stix_type': stix_type,
                'stix_id': stix_id
            }
        )
    
    @action(detail=False, methods=['post'], url_path='create-from-form/(?P<stix_type>[^/.]+)')
    def create_from_form(self, request, stix_type=None):
        """
        Create a STIX object from web form data.
        """
        # Check if the STIX type is supported
        if stix_type not in STIX_INPUT_SERIALIZERS:
            return Response(
                {"error": f"Unsupported STIX type: {stix_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the appropriate serializer
        serializer_class = STIX_INPUT_SERIALIZERS[stix_type]
        input_serializer = serializer_class(data=request.data)
        
        if input_serializer.is_valid():
            # Convert to STIX data
            stix_data = input_serializer.to_stix_data()
            
            # Create STIX object
            organization = self.get_organization(request)
            
            stix_serializer = self.get_serializer(data={'stix_data': stix_data})
            if stix_serializer.is_valid():
                stix_obj = stix_serializer.save(
                    created_by=request.user,
                    source_organization=organization
                )
                
                # Add to collection if specified
                collection_id = request.data.get('collection_id')
                if collection_id:
                    try:
                        collection = Collection.objects.get(id=collection_id)
                        # Check if user's organization owns the collection
                        if collection.owner == organization:
                            CollectionObject.objects.create(
                                collection=collection,
                                stix_object=stix_obj
                            )
                    except Collection.DoesNotExist:
                        pass
                
                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    organization=organization,
                    action_type='create_stix_object',
                    object_id=stix_obj.stix_id,
                    details={
                        'stix_type': stix_obj.stix_type,
                        'stix_id': stix_obj.stix_id,
                        'from_form': True
                    }
                )
                
                return Response(stix_serializer.data, status=status.HTTP_201_CREATED)
            return Response(stix_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def anonymize(self, request, pk=None):
        """
        Create an anonymized version of a STIX object.
        """
        instance = self.get_object()
        organization = self.get_organization(request)
        
        # Get anonymization strategy
        strategy_name = request.data.get('strategy', 'partial')
        trust_level = float(request.data.get('trust_level', 0.5))
        
        # Get strategy and apply anonymization
        strategy = AnonymizationStrategyFactory.get_strategy(strategy_name)
        
        # Get the raw STIX data
        stix_data = instance.to_stix()
        
        # Apply anonymization
        anonymized_data = strategy.anonymize(stix_data, trust_level)
        
        # Create a new STIX object with the anonymized data
        anonymized_data['id'] = f"{instance.stix_type}--{uuid.uuid4()}"
        anonymized_data['created'] = stix_data.get('created')
        anonymized_data['modified'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Create the new object
        serializer = self.get_serializer(data={'stix_data': anonymized_data})
        if serializer.is_valid():
            anonymized_obj = serializer.save(
                created_by=request.user,
                source_organization=organization,
                anonymized=True,
                anonymization_strategy=strategy_name,
                original_object_ref=instance.stix_id
            )
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                organization=organization,
                action_type='anonymize_object',
                object_id=anonymized_obj.stix_id,
                details={
                    'original_object': instance.stix_id,
                    'strategy': strategy_name,
                    'trust_level': trust_level
                }
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def bulk_upload(self, request):
        """
        Bulk upload STIX objects from CSV or JSON file.
        """
        serializer = BulkUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        upload_format = serializer.validated_data.get('format')
        file_obj = serializer.validated_data.get('data')
        mapping = serializer.validated_data.get('mapping', {})
        collection_id = serializer.validated_data.get('collection_id')
        
        organization = self.get_organization(request)
        
        # Process the file based on format
        if upload_format == 'json':
            result = self._process_json_upload(file_obj, organization, collection_id)
        else:  # csv
            result = self._process_csv_upload(file_obj, mapping, organization, collection_id)
        
        return Response(result, status=status.HTTP_207_MULTI_STATUS)
    
    def _process_json_upload(self, file_obj, organization, collection_id=None):
        """
        Process JSON file upload containing STIX objects.
        """
        # Read the file
        try:
            if hasattr(file_obj, 'read'):
                file_content = file_obj.read().decode('utf-8')
            else:
                file_content = file_obj
            
            data = json.loads(file_content)
            
            # Check if it's a STIX bundle or a list of objects
            if isinstance(data, dict) and data.get('type') == 'bundle' and 'objects' in data:
                objects = data['objects']
            elif isinstance(data, list):
                objects = data
            else:
                objects = [data]  # Single object
                
        except Exception as e:
            return {
                'success_count': 0,
                'failure_count': 1,
                'failures': [{'error': f"Error parsing JSON file: {str(e)}"}]
            }
        
        # Process objects
        return self._process_stix_objects(objects, organization, collection_id)
    
    def _process_csv_upload(self, file_obj, mapping, organization, collection_id=None):
        """
        Process CSV file upload and convert to STIX objects using mapping.
        """
        # Check mapping
        if not mapping or not isinstance(mapping, dict):
            return {
                'success_count': 0,
                'failure_count': 1,
                'failures': [{'error': "Invalid mapping configuration for CSV"}]
            }
        
        # Read the CSV file
        try:
            if hasattr(file_obj, 'read'):
                file_content = file_obj.read().decode('utf-8')
            else:
                file_content = file_obj
            
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)
            
        except Exception as e:
            return {
                'success_count': 0,
                'failure_count': 1,
                'failures': [{'error': f"Error parsing CSV file: {str(e)}"}]
            }
        
        # Convert CSV rows to STIX objects
        stix_objects = []
        failures = []
        
        for i, row in enumerate(rows):
            try:
                stix_obj = self._convert_csv_row_to_stix(row, mapping)
                if stix_obj:
                    stix_objects.append(stix_obj)
                else:
                    failures.append({
                        'row': i + 1,
                        'error': "Failed to convert row to STIX object"
                    })
            except Exception as e:
                failures.append({
                    'row': i + 1,
                    'error': str(e)
                })
        
        # Process the converted STIX objects
        result = self._process_stix_objects(stix_objects, organization, collection_id)
        
        # Add CSV-specific failures
        result['failures'].extend(failures)
        result['failure_count'] += len(failures)
        
        return result
    
    def _convert_csv_row_to_stix(self, row, mapping):
        """
        Convert a CSV row to a STIX object using the provided mapping.
        """
        # Get STIX type from mapping
        stix_type = mapping.get('stix_type')
        if not stix_type:
            raise ValueError("Mapping must specify 'stix_type'")
        
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
                        date_obj = datetime.strptime(row[csv_field], date_format)
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
                raise ValueError("Indicator must have a pattern")
        
        if stix_type == 'malware' and 'is_family' not in stix_data:
            stix_data['is_family'] = mapping.get('default_is_family', False)
        
        # Validate the object with its specific serializer
        serializer_class = STIX_INPUT_SERIALIZERS.get(stix_type)
        if not serializer_class:
            raise ValueError(f"Unsupported STIX type: {stix_type}")
            
        serializer = serializer_class(data=stix_data)
        if not serializer.is_valid():
            raise ValueError(f"Invalid STIX data: {serializer.errors}")
            
        return serializer.to_stix_data()
    
    def _process_stix_objects(self, objects, organization, collection_id=None):
        """
        Process a list of STIX objects, creating them in the database.
        Supports multi-version STIX input (1.x, 2.0, 2.1).
        """
        success_count = 0
        failures = []
        created_objects = []
        
        # Initialize multi-version handler
        factory_registry = STIXObjectFactoryRegistry()
        validator = STIXValidator()
        
        # Process each object
        for i, obj in enumerate(objects):
            try:
                # Use multi-version validation
                validation_results = validator.validate_multi_version(obj)
                
                if not validation_results['valid']:
                    failures.append({
                        'index': i,
                        'error': f"STIX validation failed: {validation_results['errors']}",
                        'detected_version': validation_results.get('detected_version', 'unknown'),
                        'conversion_attempted': validation_results.get('converted_to_stix21', False)
                    })
                    continue
                
                # Process through multi-version factory if needed
                try:
                    if validation_results.get('converted_to_stix21', False):
                        # Object was converted, use the processed version
                        processed_result = factory_registry.process_stix_input(obj)
                        
                        # Create each converted object
                        for stix_obj_data in processed_result['objects']:
                            stix_data_dict = json.loads(stix_obj_data.serialize())
                            
                            # Create the object
                            serializer = self.get_serializer(data={'stix_data': stix_data_dict})
                            if serializer.is_valid():
                                with transaction.atomic():
                                    stix_obj = serializer.save(
                                        created_by=self.request.user,
                                        source_organization=organization
                                    )
                                    
                                    # Add to collection if specified
                                    if collection_id:
                                        try:
                                            collection = Collection.objects.get(id=collection_id)
                                            # Check if user's organization owns the collection
                                            if collection.owner == organization:
                                                CollectionObject.objects.create(
                                                    collection=collection,
                                                    stix_object=stix_obj
                                                )
                                        except Collection.DoesNotExist:
                                            pass
                                    
                                    created_objects.append(stix_obj)
                                    success_count += 1
                            else:
                                failures.append({
                                    'index': i,
                                    'error': serializer.errors,
                                    'conversion_notes': processed_result.get('conversion_notes', [])
                                })
                    else:
                        # Object is already STIX 2.1, process normally
                        serializer = self.get_serializer(data={'stix_data': obj})
                        if serializer.is_valid():
                            with transaction.atomic():
                                stix_obj = serializer.save(
                                    created_by=self.request.user,
                                    source_organization=organization
                                )
                                
                                # Add to collection if specified
                                if collection_id:
                                    try:
                                        collection = Collection.objects.get(id=collection_id)
                                        # Check if user's organization owns the collection
                                        if collection.owner == organization:
                                            CollectionObject.objects.create(
                                                collection=collection,
                                                stix_object=stix_obj
                                            )
                                    except Collection.DoesNotExist:
                                        pass
                                
                                created_objects.append(stix_obj)
                                success_count += 1
                        else:
                            failures.append({
                                'index': i,
                                'error': serializer.errors
                            })
                        
                except Exception as conversion_error:
                    failures.append({
                        'index': i,
                        'error': f"Error processing multi-version STIX: {str(conversion_error)}",
                        'detected_version': validation_results.get('detected_version', 'unknown')
                    })
                    
            except Exception as e:
                failures.append({
                    'index': i,
                    'error': f"Unexpected error: {str(e)}"
                })
        
        # Log the bulk upload
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='create_stix_object',
            details={
                'bulk_upload': True,
                'success_count': success_count,
                'failure_count': len(failures),
                'collection_id': collection_id
            }
        )
        
        return {
            'success_count': success_count,
            'failure_count': len(failures),
            'failures': failures,
            'created_objects': [obj.stix_id for obj in created_objects]
        }
    
    @action(detail=False, methods=['post'])
    def validate_stix(self, request):
        """
        Validate STIX data of any supported version (1.x, 2.0, 2.1).
        Returns validation results and version information.
        """
        stix_data = request.data.get('stix_data')
        if not stix_data:
            return Response(
                {"error": "stix_data field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use multi-version validator
        validator = STIXValidator()
        validation_results = validator.validate_multi_version(stix_data)
        
        # Add additional metadata
        validation_results['timestamp'] = timezone.now().isoformat()
        validation_results['validation_notes'] = []
        
        # Add specific notes based on version
        if validation_results.get('converted_to_stix21', False):
            validation_results['validation_notes'].append(
                f"Input STIX {validation_results['detected_version']} was automatically converted to STIX 2.1"
            )
        
        if validation_results.get('conversion_notes'):
            validation_results['validation_notes'].extend(validation_results['conversion_notes'])
        
        return Response(validation_results, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def convert_stix(self, request):
        """
        Convert STIX data from any version to STIX 2.1.
        """
        stix_data = request.data.get('stix_data')
        target_version = request.data.get('target_version', '2.1')
        
        if not stix_data:
            return Response(
                {"error": "stix_data field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if target_version != '2.1':
            return Response(
                {"error": "Currently only conversion to STIX 2.1 is supported"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use version handler for conversion
            version_handler = STIXVersionHandler()
            processed_data = version_handler.process_stix_data(stix_data)
            
            response_data = {
                'original_version': processed_data['original_version'],
                'target_version': processed_data['converted_version'],
                'converted_data': processed_data['stix_data'],
                'conversion_notes': processed_data['conversion_notes'],
                'timestamp': timezone.now().isoformat()
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Conversion failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def process_multi_version(self, request):
        """
        Complete workflow: validate, convert, and optionally create STIX objects.
        Supports STIX 1.x, 2.0, and 2.1 input.
        """
        stix_data = request.data.get('stix_data')
        create_objects = request.data.get('create_objects', False)
        collection_id = request.data.get('collection_id')
        
        if not stix_data:
            return Response(
                {"error": "stix_data field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            organization = self.get_organization(request)
            
            # Step 1: Validate input
            validator = STIXValidator()
            validation_results = validator.validate_multi_version(stix_data)
            
            if not validation_results['valid']:
                return Response({
                    'validation': validation_results,
                    'processing': {'status': 'skipped', 'reason': 'validation_failed'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Step 2: Process through factory
            factory_registry = STIXObjectFactoryRegistry()
            processing_result = factory_registry.process_stix_input(stix_data)
            
            response_data = {
                'validation': validation_results,
                'processing': {
                    'status': 'success',
                    'original_version': processing_result['original_version'],
                    'converted_version': processing_result['converted_version'],
                    'total_objects': processing_result['total_objects'],
                    'conversion_notes': processing_result['conversion_notes']
                },
                'timestamp': timezone.now().isoformat()
            }
            
            # Step 3: Optionally create objects in database
            if create_objects:
                try:
                    # Convert STIX objects to serializable format for processing
                    stix_objects_data = []
                    for stix_obj in processing_result['objects']:
                        stix_objects_data.append(json.loads(stix_obj.serialize()))
                    
                    # Use existing processing method
                    creation_result = self._process_stix_objects(
                        stix_objects_data, 
                        organization, 
                        collection_id
                    )
                    
                    response_data['creation'] = creation_result
                    
                    # Log the action
                    AuditLog.objects.create(
                        user=request.user,
                        organization=organization,
                        action_type='process_multi_version_stix',
                        object_id=None,
                        details={
                            'original_version': processing_result['original_version'],
                            'objects_created': creation_result['success_count'],
                            'objects_failed': creation_result['failure_count']
                        }
                    )
                    
                except Exception as creation_error:
                    response_data['creation'] = {
                        'status': 'failed',
                        'error': str(creation_error)
                    }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Processing failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CollectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Collections.
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['owner', 'can_read', 'can_write']
    search_fields = ['title', 'description', 'alias']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']
    
    def get_organization(self, request):
        """
        Get the organization associated with the authenticated user.
        """
        try:
            return Organization.objects.filter(
                id__in=request.user.groups.values_list('name', flat=True)
            ).first()
        except Organization.DoesNotExist:
            if settings.DEBUG:
                return Organization.objects.create(
                    name=f"{request.user.username}'s Organization",
                    identity_class="organization",
                    stix_id=f"identity--{uuid.uuid4()}"
                )
            raise Exception("No organization found for authenticated user")
    
    def perform_create(self, serializer):
        """
        Set the owner when creating a Collection.
        """
        organization = self.get_organization(self.request)
        serializer.save(owner=organization)
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='create_collection',
            object_id=str(serializer.instance.id),
            details={
                'title': serializer.instance.title
            }
        )
    
    def perform_update(self, serializer):
        """
        Log the update action.
        """
        organization = self.get_organization(self.request)
        serializer.save()
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='update_collection',
            object_id=str(serializer.instance.id),
            details={
                'title': serializer.instance.title
            }
        )
    
    def perform_destroy(self, instance):
        """
        Log the delete action.
        """
        organization = self.get_organization(self.request)
        collection_id = str(instance.id)
        title = instance.title
        
        instance.delete()
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='delete_collection',
            object_id=collection_id,
            details={
                'title': title
            }
        )
    
    @action(detail=True, methods=['post'])
    def add_object(self, request, pk=None):
        """
        Add a STIX object to the collection.
        """
        collection = self.get_object()
        organization = self.get_organization(request)
        
        # Check if user's organization owns the collection
        if collection.owner != organization:
            return Response(
                {"error": "You can only add objects to collections owned by your organization"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the STIX object
        stix_id = request.data.get('stix_id')
        if not stix_id:
            return Response(
                {"error": "STIX object ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stix_object = STIXObject.objects.get(stix_id=stix_id)
            
            # Check if already in collection
            existing = CollectionObject.objects.filter(
                collection=collection,
                stix_object=stix_object
            ).exists()
            
            if existing:
                return Response(
                    {"message": "Object already in collection"},
                    status=status.HTTP_200_OK
                )
            
            # Add to collection
            CollectionObject.objects.create(
                collection=collection,
                stix_object=stix_object
            )
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                organization=organization,
                action_type='add_collection_objects',
                object_id=str(collection.id),
                details={
                    'collection_title': collection.title,
                    'stix_id': stix_id
                }
            )
            
            return Response(
                {"message": "Object added to collection"},
                status=status.HTTP_201_CREATED
            )
            
        except STIXObject.DoesNotExist:
            return Response(
                {"error": "STIX object not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_object(self, request, pk=None):
        """
        Remove a STIX object from the collection.
        """
        collection = self.get_object()
        organization = self.get_organization(request)
        
        # Check if user's organization owns the collection
        if collection.owner != organization:
            return Response(
                {"error": "You can only remove objects from collections owned by your organization"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the STIX object
        stix_id = request.data.get('stix_id')
        if not stix_id:
            return Response(
                {"error": "STIX object ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stix_object = STIXObject.objects.get(stix_id=stix_id)
            
            # Check if in collection
            try:
                collection_object = CollectionObject.objects.get(
                    collection=collection,
                    stix_object=stix_object
                )
                
                # Remove from collection
                collection_object.delete()
                
                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    organization=organization,
                    action_type='remove_collection_objects',
                    object_id=str(collection.id),
                    details={
                        'collection_title': collection.title,
                        'stix_id': stix_id
                    }
                )
                
                return Response(
                    {"message": "Object removed from collection"},
                    status=status.HTTP_200_OK
                )
                
            except CollectionObject.DoesNotExist:
                return Response(
                    {"error": "Object not in collection"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except STIXObject.DoesNotExist:
            return Response(
                {"error": "STIX object not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def objects(self, request, pk=None):
        """
        Get all objects in a collection.
        """
        collection = self.get_object()
        organization = self.get_organization(request)
        
        # Check if user has read access to this collection
        if not collection.can_read:
            return Response(
                {"error": "Access denied to this collection"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all objects in the collection
        collection_objects = CollectionObject.objects.filter(collection=collection)
        stix_object_ids = collection_objects.values_list('stix_object', flat=True)
        stix_objects = STIXObject.objects.filter(id__in=stix_object_ids)
        
        # Apply filters from query parameters
        stix_type = request.query_params.get('type')
        if stix_type:
            stix_objects = stix_objects.filter(stix_type=stix_type)
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        
        paginator = Paginator(stix_objects, page_size)
        page_objects = paginator.get_page(page)
        
        # Serialize and return
        serializer = STIXObjectSerializer(page_objects, many=True)
        
        return Response({
            'count': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page,
            'results': serializer.data
        })


class FeedViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Feeds.
    """
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['collection', 'status', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'last_published']
    ordering = ['name']
    
    def get_organization(self, request):
        """
        Get the organization associated with the authenticated user.
        """
        try:
            return Organization.objects.filter(
                id__in=request.user.groups.values_list('name', flat=True)
            ).first()
        except Organization.DoesNotExist:
            if settings.DEBUG:
                return Organization.objects.create(
                    name=f"{request.user.username}'s Organization",
                    identity_class="organization",
                    stix_id=f"identity--{uuid.uuid4()}"
                )
            raise Exception("No organization found for authenticated user")
    
    def perform_create(self, serializer):
        """
        Set the creator when creating a Feed.
        """
        serializer.save(created_by=self.request.user)
        
        # Log the action
        organization = self.get_organization(self.request)
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='create_feed',
            object_id=str(serializer.instance.id),
            details={
                'name': serializer.instance.name,
                'collection_id': str(serializer.instance.collection.id)
            }
        )
    
    def perform_update(self, serializer):
        """
        Log the update action.
        """
        serializer.save()
        
        # Log the action
        organization = self.get_organization(self.request)
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='update_feed',
            object_id=str(serializer.instance.id),
            details={
                'name': serializer.instance.name
            }
        )
    
    def perform_destroy(self, instance):
        """
        Log the delete action.
        """
        organization = self.get_organization(self.request)
        feed_id = str(instance.id)
        name = instance.name
        
        instance.delete()
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            organization=organization,
            action_type='delete_feed',
            object_id=feed_id,
            details={
                'name': name
            }
        )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Manually publish a feed.
        """
        feed = self.get_object()
        organization = self.get_organization(request)
        
        # Update last_published timestamp
        feed.last_published = timezone.now()
        feed.save()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            organization=organization,
            action_type='publish_feed',
            object_id=str(feed.id),
            details={
                'name': feed.name,
                'collection_id': str(feed.collection.id)
            }
        )
        
        # Return success response
        return Response({
            "message": f"Feed '{feed.name}' published successfully",
            "published_at": feed.last_published
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_feed(request, feed_id):
    """Publish a specific feed"""
    try:
        result = FeedPublishingService.publish_feed(feed_id)
        return Response(result)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_all_feeds(request):
    """Publish all active feeds"""
    try:
        results = FeedPublishingService.publish_all_active_feeds()
        return Response({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=400)

from core.tasks import publish_feed_immediate

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_feed_webhook(request, feed_id):
    """Webhook endpoint for immediate feed publishing"""
    try:
        # Queue immediate publish task
        task = publish_feed_immediate.delay(feed_id)
        
        return Response({
            'status': 'scheduled',
            'task_id': task.id
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=500)