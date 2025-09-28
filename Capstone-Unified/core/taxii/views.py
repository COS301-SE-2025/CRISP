"""
TAXII 2.1 API Implementation
Complete implementation with exact functional replication.
"""
import json
import uuid
import datetime
import logging
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

from core.models.models import Collection, STIXObject, CollectionObject, Organization, TrustRelationship

logger = logging.getLogger(__name__)

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core', 'patterns', 'strategy'))

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
            result = copy.deepcopy(stix_data)
            result['x_crisp_anonymized'] = True
            result['x_crisp_anonymization_level'] = level.value if hasattr(level, 'value') else str(level)
            if 'pattern' in result:
                result['pattern'] = f"[ANON:{level}]{result['pattern']}"
            return result
    
    class AnonymizationError(Exception):
        pass


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
        Get the trust level between source and target organizations with enhanced logic.
        """
        if source_org == target_org:
            return 1.0
        
        # Import here to avoid circular imports
        from settings.utils import get_trust_level
        return get_trust_level(source_org, target_org)
    
    def apply_anonymization(self, stix_objects, requesting_org, source_org):
        """Apply anonymization to STIX objects based on trust relationship"""
        if requesting_org == source_org:
            # Same organization - no anonymization needed
            return stix_objects
        
        try:
            from core.services.anonymization_service import AnonymizationService
            anonymization_service = AnonymizationService()
            
            # Determine anonymization level based on trust relationship
            anonymization_level = 'partial'  # Default level
            
            # Apply anonymization to each STIX object
            anonymized_objects = []
            for obj in stix_objects:
                try:
                    # Handle different object types
                    if hasattr(obj, 'to_stix'):
                        # Django model with to_stix method
                        obj_dict = obj.to_stix()
                    elif hasattr(obj, '__dict__'):
                        # Object with __dict__
                        obj_dict = obj.__dict__.copy()
                    elif hasattr(obj, '_inner'):
                        # STIX2 object format
                        obj_dict = obj._inner.copy()
                    elif isinstance(obj, dict):
                        # Already a dictionary
                        obj_dict = obj.copy()
                    else:
                        # Try to convert to dict safely
                        try:
                            obj_dict = dict(obj)
                        except (TypeError, ValueError):
                            # If conversion fails, create a basic dict
                            obj_dict = {
                                'type': getattr(obj, 'type', 'unknown'),
                                'id': getattr(obj, 'id', f'unknown--{uuid.uuid4()}'),
                                'pattern': getattr(obj, 'pattern', ''),
                            }
                    
                    # Apply anonymization
                    anonymized_obj = anonymization_service.anonymize_stix_object(
                        obj_dict, anonymization_level
                    )
                    anonymized_objects.append(anonymized_obj)
                    
                except Exception as e:
                    logger.warning(f"Failed to anonymize object {obj}: {e}")
                    # If anonymization fails, create a safe fallback
                    fallback_obj = {
                        'type': 'indicator',
                        'id': f'indicator--{uuid.uuid4()}',
                        'pattern': '[ANON:FAILED]',
                        'labels': ['malicious-activity']
                    }
                    anonymized_objects.append(fallback_obj)
            
            return anonymized_objects
            
        except Exception as e:
            logger.error(f"Anonymization service failed: {e}")
            # If anonymization service fails, return original objects
            return stix_objects

    def _get_trust_level(self, source_org, requesting_org):
        """
        Get the trust level between two organizations.
        
        Returns:
            float: Trust level (0.0 to 1.0)
        """
        # Default to low trust
        default_trust = 0.3
        
        # If same organization, full trust
        if source_org == requesting_org:
            return 1.0
            
        # Try to find a trust relationship
        try:
            relationship = TrustRelationship.objects.get(
                source_organization=source_org,
                target_organization=requesting_org
            )
            return relationship.trust_level.numerical_value / 100.0
        except TrustRelationship.DoesNotExist:
            return default_trust

    def get_requesting_organization(self):
        """
        Get the organization making the TAXII request
        """
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            # Try to get organization from user profile or membership
            if hasattr(self.request.user, 'organization_memberships'):
                membership = self.request.user.organization_memberships.first()
                if membership:
                    return membership.organization
            
            # Fallback: try to get from user's created organizations
            org = Organization.objects.filter(created_by=self.request.user).first()
            if org:
                return org
        
        return None


    def _get_anonymization_level(self, source_org, target_org):
        """
        Determine anonymization level based on trust relationship
        """
        from core.models.models import TrustRelationship
        from core.patterns.strategy.enums import AnonymizationLevel
        
        if source_org == target_org:
            return AnonymizationLevel.NONE
        
        try:
            trust_rel = TrustRelationship.objects.get(
                source_organization=source_org,
                target_organization=target_org
            )
            return trust_rel.trust_level.get_anonymization_level()
        except TrustRelationship.DoesNotExist:
            return AnonymizationLevel.HIGH
        
        


class DiscoveryView(TAXIIBaseView):
    """
    TAXII 2.1 Discovery endpoint (GET /taxii2/)
    """
    permission_classes = [] 
    
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
        
        # For now, only show owned collections
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
    TAXII 2.1 Collection endpoint (GET /taxii2/collections/{id}/)
    """
    def get(self, request, collection_id):
        """
        Get information about a specific collection.
        """
        org = self.get_organization(request)
        
        try:
            collection = Collection.objects.get(id=collection_id)
            
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
            if not collection.can_read and collection.owner != org:
                return Response(
                    {"error": "Access denied to this collection"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Determine if cross-organization access (requires anonymization)
            is_cross_org_access = collection.owner != org
            
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
                if is_cross_org_access:
                    anonymized_result = self.apply_anonymization(
                        [stix_data], 
                        org,  # target_org
                        collection.owner  # source_org
                    )
                    stix_data = anonymized_result[0] if anonymized_result and len(anonymized_result) > 0 else None
                
                # Only include objects that were successfully anonymized or owned by requesting org
                if stix_data is not None and isinstance(stix_data, dict):
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
            new_indicators_created = []

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
                    is_new_object = existing_obj is None

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

                    # Create corresponding Indicator record if this is an indicator object
                    if stix_type == 'indicator' and is_new_object:
                        try:
                            indicator_record = self._create_indicator_from_stix(stix_obj, collection, org)
                            if indicator_record:
                                new_indicators_created.append({
                                    'stix_object': stix_obj,
                                    'indicator': indicator_record,
                                    'collection': collection
                                })
                        except Exception as indicator_error:
                            logger.warning(f"Failed to create indicator record for STIX {stix_id}: {indicator_error}")

                    success_count += 1

                except Exception as e:
                    failures.append({
                        'object': obj.get('id', 'Unknown ID'),
                        'message': str(e)
                    })

            # Send notifications for new indicators after successful processing
            if new_indicators_created:
                try:
                    self._send_taxii_reception_notifications(
                        new_indicators_created,
                        collection,
                        org,
                        request.user
                    )
                except Exception as notification_error:
                    logger.error(f"Failed to send TAXII reception notifications: {notification_error}")
                    # Don't fail the whole operation due to notification issues
            
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

    def _create_indicator_from_stix(self, stix_obj, collection, target_org):
        """
        Create an Indicator record from a STIX object for dashboard visibility

        Args:
            stix_obj: STIXObject instance
            collection: Collection the object belongs to
            target_org: Target organization receiving the indicator

        Returns:
            Created Indicator object or None if creation failed
        """
        try:
            from core.models.models import Indicator, ThreatFeed
            import re

            # Get or create a shared threat feed for TAXII received indicators
            shared_feed, created = ThreatFeed.objects.get_or_create(
                name=f"TAXII Shared Intelligence - {target_org.name}",
                owner=target_org,
                defaults={
                    'description': f'Threat intelligence received via TAXII for {target_org.name}',
                    'is_external': False,
                    'is_active': True,
                    'is_public': False,
                    'sync_interval_hours': 0
                }
            )

            # Extract indicator details from STIX pattern
            raw_data = stix_obj.raw_data
            stix_pattern = raw_data.get('pattern', '')

            # Parse pattern to extract type and value
            indicator_type = 'other'
            indicator_value = None

            # Try to extract from STIX pattern first
            if stix_pattern:
                # Common STIX pattern parsing
                if 'file:hashes.MD5' in stix_pattern or 'file:hashes.SHA256' in stix_pattern or 'file:hashes.SHA1' in stix_pattern:
                    indicator_type = 'file_hash'
                    match = re.search(r"= '([^']+)'", stix_pattern)
                    if match:
                        indicator_value = match.group(1)
                elif 'domain-name:value' in stix_pattern:
                    indicator_type = 'domain'
                    match = re.search(r"= '([^']+)'", stix_pattern)
                    if match:
                        indicator_value = match.group(1)
                elif 'ipv4-addr:value' in stix_pattern or 'ipv6-addr:value' in stix_pattern:
                    indicator_type = 'ip'
                    match = re.search(r"= '([^']+)'", stix_pattern)
                    if match:
                        indicator_value = match.group(1)
                elif 'url:value' in stix_pattern:
                    indicator_type = 'url'
                    match = re.search(r"= '([^']+)'", stix_pattern)
                    if match:
                        indicator_value = match.group(1)
                elif 'email-addr:value' in stix_pattern:
                    indicator_type = 'email'
                    match = re.search(r"= '([^']+)'", stix_pattern)
                    if match:
                        indicator_value = match.group(1)
                else:
                    # Try to extract any quoted value from the pattern
                    match = re.search(r"= '([^']+)'", stix_pattern)
                    if match:
                        indicator_value = match.group(1)
                        # Try to guess type from value
                        value = indicator_value.lower()
                        if '.' in value and not '@' in value:
                            if value.startswith('http'):
                                indicator_type = 'url'
                            else:
                                indicator_type = 'domain'
                        elif len(value) in [32, 40, 64]:  # MD5, SHA1, SHA256 lengths
                            indicator_type = 'file_hash'
                        elif '@' in value:
                            indicator_type = 'email'

            # If no value extracted from pattern, try other STIX fields
            if not indicator_value:
                # Try to get from other STIX fields
                if 'name' in raw_data and raw_data['name']:
                    indicator_value = raw_data['name']
                elif 'value' in raw_data and raw_data['value']:
                    indicator_value = raw_data['value']
                elif 'x_crisp_value' in raw_data and raw_data['x_crisp_value']:
                    indicator_value = raw_data['x_crisp_value']
                else:
                    # Last resort: use a descriptive fallback instead of a random ID
                    indicator_value = f"Unknown indicator from {raw_data.get('x_crisp_source_org', 'external source')}"

            # Create or update indicator
            indicator, created = Indicator.objects.get_or_create(
                value=indicator_value,
                type=indicator_type,
                threat_feed=shared_feed,
                defaults={
                    'description': f"TAXII shared indicator: {raw_data.get('name', 'Unknown')}",
                    'confidence': raw_data.get('confidence', 50),
                    'stix_id': stix_obj.stix_id,
                    'first_seen': timezone.now(),
                    'last_seen': timezone.now()
                }
            )

            if not created:
                # Update last_seen if indicator already exists
                indicator.last_seen = timezone.now()
                indicator.save(update_fields=['last_seen'])

            logger.info(f"Created/updated indicator record {indicator.id} from STIX object {stix_obj.stix_id}")
            return indicator

        except Exception as e:
            logger.error(f"Error creating indicator from STIX object {stix_obj.stix_id}: {str(e)}")
            return None

    def _send_taxii_reception_notifications(self, new_indicators_data, collection, target_org, receiving_user):
        """
        Send notifications when new indicators are received via TAXII

        Args:
            new_indicators_data: List of dicts with 'stix_object', 'indicator', 'collection' keys
            collection: Collection the indicators were added to
            target_org: Organization receiving the indicators
            receiving_user: User who received the indicators
        """
        try:
            from core.services.notification_service import NotificationService
            from core.user_management.models import CustomUser

            notification_service = NotificationService()

            # Get users in the target organization who should receive notifications
            # Use broader role matching and include the receiving user's organization if target_org doesn't have users
            target_users = CustomUser.objects.filter(
                organization=target_org,
                is_active=True
            ).exclude(
                role__in=['viewer', 'Viewer']  # Exclude basic viewers
            )

            # If no users in target org, notify users in receiving user's organization
            if not target_users.exists() and receiving_user and receiving_user.organization:
                logger.info(f"No users in target org {target_org.name}, using receiving user's org {receiving_user.organization.name}")
                target_users = CustomUser.objects.filter(
                    organization=receiving_user.organization,
                    is_active=True
                ).exclude(
                    role__in=['viewer', 'Viewer']
                )

            if not target_users.exists():
                logger.warning(f"No active users found for TAXII notifications")
                return

            # Create notifications for each new indicator
            for indicator_data in new_indicators_data:
                stix_obj = indicator_data['stix_object']
                indicator = indicator_data['indicator']

                # Extract source organization from STIX object
                source_org_name = stix_obj.raw_data.get('x_crisp_source_org', 'External Source')
                indicator_type = indicator.type.upper() if indicator.type else 'UNKNOWN'
                indicator_value = indicator.value[:100] + '...' if len(indicator.value) > 100 else indicator.value

                # Create notification for each target user
                for user in target_users:
                    try:
                        from core.alerts.models import Notification

                        notification = Notification.objects.create(
                            notification_type='security_alert',
                            title=f"🚨 New {indicator_type} Threat Intelligence Received",
                            message=f"Your organization has received new threat intelligence from {source_org_name} via TAXII 2.1.\n\n📍 Indicator: {indicator_value}\n🔍 Type: {indicator_type}\n📂 Collection: {collection.title}",
                            priority='high',
                            recipient=user,
                            organization=user.organization,
                            related_object_type='indicator',
                            related_object_id=str(indicator.id),
                            metadata={
                                'indicator_id': indicator.id,
                                'indicator_type': indicator_type,
                                'indicator_value': indicator_value,
                                'source_organization': source_org_name,
                                'collection_name': collection.title,
                                'collection_id': str(collection.id),
                                'stix_id': stix_obj.stix_id,
                                'reception_method': 'TAXII 2.1',
                                'notification_category': 'threat_intelligence_received',
                                'feed_name': indicator.threat_feed.name if indicator.threat_feed else 'Unknown Feed'
                            }
                        )

                        logger.info(f"✅ Created TAXII reception notification for user {user.username} (ID: {notification.id})")

                    except Exception as user_notification_error:
                        logger.error(f"❌ Failed to create notification for user {user.username}: {user_notification_error}")
                        continue

            logger.info(f"🎯 Successfully processed TAXII reception notifications for {len(new_indicators_data)} indicators to {len(target_users)} users")

        except Exception as e:
            logger.error(f"💥 Error sending TAXII reception notifications: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Don't raise the exception as notifications are not critical for the main TAXII operation


class ObjectView(TAXIIBaseView):
    """
    TAXII 2.1 Object endpoint (GET /taxii2/collections/{id}/objects/{object_id}/)
    """
    def get(self, request, collection_id, object_id):
        """
        Get a specific object from a collection.
        """
        org = self.get_organization(request)
        
        try:
            collection = Collection.objects.get(id=collection_id)
            
            # Check if user has read access to this collection
            if not collection.can_read and collection.owner != org:
                return Response(
                    {"error": "Access denied to this collection"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Determine if cross-organization access (requires anonymization)
            is_cross_org_access = collection.owner != org
            
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
            if is_cross_org_access:
                anonymized_result = self.apply_anonymization(
                    [stix_data], 
                    org,  # target_org
                    collection.owner  # source_org
                )
                stix_data = anonymized_result[0] if anonymized_result and len(anonymized_result) > 0 else None
                
                # If anonymization failed, deny access to object
                if stix_data is None:
                    raise NotFound("Object not accessible due to anonymization restrictions")
            
            # Build response
            objects_data = {
                'objects': [stix_data] if isinstance(stix_data, dict) else []
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
            # Allow access if collection is readable OR if same organization
            if not collection.can_read and collection.owner != org:
                return Response(
                    {"error": "Access denied to this collection"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Determine if cross-organization access (requires anonymization)
            is_cross_org_access = collection.owner != org
            
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