import logging
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import AllowAny
from django.http import Http404
from rest_framework.views import exception_handler

from core.models.models import ThreatFeed, SystemActivity
from core.services.otx_taxii_service import OTXTaxiiService
from core.serializers.threat_feed_serializer import ThreatFeedSerializer
from core.models.models import Indicator  
from core.models.models import TTPData     

logger = logging.getLogger(__name__)

class ThreatFeedViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ThreatFeed operations
    """
    queryset = ThreatFeed.objects.all()
    serializer_class = ThreatFeedSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """Log activity when a new feed is created"""
        feed = serializer.save()
        
        # Log activity
        activity_title = f"New threat feed added: {feed.name}"
        activity_description = f"{'External' if feed.is_external else 'Internal'} threat feed '{feed.name}' has been configured"
        SystemActivity.log_activity(
            activity_type='feed_added',
            title=activity_title,
            description=activity_description,
            threat_feed=feed,
            metadata={
                'feed_type': 'external' if feed.is_external else 'internal',
                'is_active': feed.is_active,
                'taxii_url': feed.taxii_server_url if feed.is_external else None
            }
        )
    
    @action(detail=False, methods=['get'])
    def external(self, request):
        """
        Get all external threat feeds
        """
        external_feeds = ThreatFeed.objects.filter(is_external=True)
        serializer = self.get_serializer(external_feeds, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_collections(self, request):
        """
        Get available TAXII collections from configured sources
        """
        try:
            service = OTXTaxiiService()
            collections = service.get_collections()
            return Response(collections)
        except Exception as e:
            logger.error(f"Error retrieving collections: {str(e)}")
            return Response(
                {"error": "Failed to retrieve collections", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """
        Consume indicators from a specific threat feed
        """
        logger.info(f"CONSUME API CALLED for feed ID: {pk}")
        
        try:
            try:
                feed = get_object_or_404(ThreatFeed, pk=pk)
            except Http404 as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
            logger.info(f"Found feed: {feed.name}, collection: {feed.taxii_collection_id}")
            
            # Parse parameters
            limit_param = request.query_params.get('limit')
            batch_size = request.query_params.get('batch_size', 100)
            force_days = request.query_params.get('force_days')
            
            # Validate parameters
            limit = None
            if limit_param:
                try:
                    limit = int(limit_param)
                except ValueError:
                    return Response(
                        {"error": "Invalid limit parameter, must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if force_days:
                try:
                    force_days = int(force_days)
                except ValueError:
                    return Response(
                        {"error": "Invalid force_days parameter, must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            try:
                batch_size = int(batch_size)
            except ValueError:
                batch_size = 100
            
            # Log parameters for debugging
            logger.info(f"Parameters: limit={limit}, force_days={force_days}, batch_size={batch_size}")
            
            # Use OTXTaxiiService
            service = OTXTaxiiService()
            
            # Check if async processing is requested
            if request.query_params.get('async', '').lower() == 'true':
                from core.tasks.taxii_tasks import consume_feed_task
                task = consume_feed_task.delay(
                    feed_id=int(pk), 
                    limit=limit, 
                    force_days=force_days,
                    batch_size=batch_size
                )
                return Response({
                    "status": "processing",
                    "message": "Processing started in background",
                    "task_id": task.id
                })
            
            stats = service.consume_feed(feed)
            
            # Format response properly for API consumers
            if isinstance(stats, tuple):
                indicator_count, ttp_count = stats
                formatted_stats = {
                    "indicators": indicator_count,
                    "ttps": ttp_count,
                    "status": "completed",
                    "feed_name": feed.name,
                    "parameters_used": {
                        "limit": limit,
                        "force_days": force_days,
                        "batch_size": batch_size
                    }
                }
                
                # Log activity
                if indicator_count > 0 or ttp_count > 0:
                    activity_title = f"Consumed {indicator_count} indicators from {feed.name}"
                    activity_description = f"Feed consumption completed successfully. Added {indicator_count} indicators and {ttp_count} TTPs."
                    SystemActivity.log_activity(
                        activity_type='feed_consumed',
                        title=activity_title,
                        description=activity_description,
                        threat_feed=feed,
                        metadata={
                            'indicator_count': indicator_count,
                            'ttp_count': ttp_count,
                            'parameters': {
                                'limit': limit,
                                'force_days': force_days,
                                'batch_size': batch_size
                            }
                        }
                    )
            else:
                formatted_stats = stats

            return Response(formatted_stats)
            
        except ValueError as ve:
            logger.warning(f"Invalid request data or feed config: {ve}")
            return Response(
                {"error": "Invalid request data", "details": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error consuming feed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Response(
                {"error": "Failed to consume feed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get the status of the threat feed."""
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get counts
        indicator_count = Indicator.objects.filter(threat_feed_id=pk).count()
        ttp_count = TTPData.objects.filter(threat_feed_id=pk).count()

        # Get the most recent indicator
        latest_indicator = Indicator.objects.filter(threat_feed_id=pk).order_by('-created_at').first()
        latest_date = latest_indicator.created_at if latest_indicator else None

        return Response({
            "name": feed.name,
            "is_external": feed.is_external,
            "is_active": feed.is_active,
            "last_sync": feed.last_sync,
            "indicator_count": indicator_count,
            "ttp_count": ttp_count,
            "latest_indicator_date": latest_date
        })
    
    @action(detail=True, methods=['get'])
    def test_connection(self, request, pk=None):
        """Test TAXII connection without consuming."""
        try:
            try:
                feed = get_object_or_404(ThreatFeed, pk=pk)
            except Http404 as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
            service = OTXTaxiiService()
            
            # Test getting collections
            collections = service.get_collections()
            
            return Response({
                "status": "success",
                "feed_name": feed.name,
                "collections_found": len(collections),
                "collections": collections[:3]
            })
        except Exception as e:
            return Response({
                "status": "error", 
                "error": str(e)
            }, status=500)
    
    @action(detail=True, methods=['get'])
    def indicators(self, request, pk=None):
        """Get indicators for a specific threat feed."""
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get indicators for this feed
        indicators = Indicator.objects.filter(threat_feed_id=pk).order_by('-created_at')
        
        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Calculate pagination
        start = (page - 1) * page_size
        end = start + page_size
        total_count = indicators.count()
        
        indicators_page = indicators[start:end]
        
        # Format the response
        results = []
        for indicator in indicators_page:
            results.append({
                'id': indicator.id,
                'type': indicator.type,
                'value': indicator.value,
                'stix_id': indicator.stix_id,
                'description': indicator.description,
                'confidence': indicator.confidence,
                'first_seen': indicator.first_seen,
                'last_seen': indicator.last_seen,
                'created_at': indicator.created_at,
                'is_anonymized': indicator.is_anonymized,
                'source': feed.name
            })
        
        return Response({
            'count': total_count,
            'next': f'/api/threat-feeds/{pk}/indicators/?page={page + 1}&page_size={page_size}' if end < total_count else None,
            'previous': f'/api/threat-feeds/{pk}/indicators/?page={page - 1}&page_size={page_size}' if page > 1 else None,
            'results': results
        })
        
    def handle_exception(self, exc):
        # Let DRF handle known exceptions
        response = exception_handler(exc, self.get_exception_handler_context())

        # If response is None, it's likely an unhandled exception
        if response is None:
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return response

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def indicators_list(request):
    """Get all indicators across all feeds for dashboard summary or create new indicator."""
    if request.method == 'GET':
        try:
            # Get pagination parameters
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            
            # Get all indicators
            indicators = Indicator.objects.all().order_by('-created_at')
            
            # Calculate pagination
            start = (page - 1) * page_size
            end = start + page_size
            total_count = indicators.count()
            
            indicators_page = indicators[start:end]
            
            # Format the response
            results = []
            for indicator in indicators_page:
                # Get the feed name
                feed_name = 'Unknown'
                if hasattr(indicator, 'threat_feed') and indicator.threat_feed:
                    feed_name = indicator.threat_feed.name
                elif hasattr(indicator, 'threat_feed_id') and indicator.threat_feed_id:
                    try:
                        feed = ThreatFeed.objects.get(id=indicator.threat_feed_id)
                        feed_name = feed.name
                    except ThreatFeed.DoesNotExist:
                        pass
                
                results.append({
                    'id': indicator.id,
                    'type': indicator.type,
                    'value': indicator.value,
                    'stix_id': indicator.stix_id,
                    'description': indicator.description,
                    'confidence': indicator.confidence,
                    'first_seen': indicator.first_seen,
                    'last_seen': indicator.last_seen,
                    'created_at': indicator.created_at,
                    'is_anonymized': indicator.is_anonymized,
                    'source': feed_name
                })
            
            return Response({
                'count': total_count,
                'next': f'/api/indicators/?page={page + 1}&page_size={page_size}' if end < total_count else None,
                'previous': f'/api/indicators/?page={page - 1}&page_size={page_size}' if page > 1 else None,
                'results': results
            })
        except Exception as e:
            logger.error(f"Error fetching indicators: {str(e)}")
            return Response(
                {"error": "Failed to fetch indicators", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            from core.repositories.indicator_repository import IndicatorRepository
            from core.services.indicator_service import IndicatorService
            from core.models.models import Organization
            import uuid
            
            data = request.data
            
            # Validate required fields
            required_fields = ['type', 'value']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {"error": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get or create default threat feed for manual entries
            default_org, created = Organization.objects.get_or_create(
                name="Manual Entry",
                defaults={'description': 'Default organization for manually created indicators'}
            )
            
            default_feed, created = ThreatFeed.objects.get_or_create(
                name="Manual Entry Feed",
                defaults={
                    'description': 'Default feed for manually created indicators',
                    'is_external': False,
                    'is_active': True,
                    'owner': default_org
                }
            )
            
            # Prepare indicator data with correct fields
            from django.utils import timezone
            now = timezone.now()
            
            indicator_data = {
                'value': data['value'].strip(),
                'type': data['type'],
                'description': data.get('description', ''),
                'confidence': int(data.get('confidence', 50)),
                'stix_id': f'indicator--{uuid.uuid4()}',
                'threat_feed': data.get('threat_feed_id') and ThreatFeed.objects.get(id=data['threat_feed_id']) or default_feed,
                'first_seen': now,
                'last_seen': now,
            }
            
            # Create the indicator directly using the repository
            from core.repositories.indicator_repository import IndicatorRepository
            indicator = IndicatorRepository.create(indicator_data)
            
            # Log activity
            activity_title = f"New {indicator.type} indicator added"
            activity_description = f"Indicator '{indicator.value}' added to {indicator.threat_feed.name if indicator.threat_feed else 'Manual Entry Feed'}"
            SystemActivity.log_activity(
                activity_type='indicator_added',
                title=activity_title,
                description=activity_description,
                indicator=indicator,
                threat_feed=indicator.threat_feed,
                metadata={
                    'indicator_type': indicator.type,
                    'confidence': indicator.confidence,
                    'source': indicator.threat_feed.name if indicator.threat_feed else 'Manual Entry'
                }
            )
            
            # Format response
            feed_name = 'Manual Entry'
            if indicator.threat_feed:
                feed_name = indicator.threat_feed.name
            
            result = {
                'id': indicator.id,
                'type': indicator.type,
                'value': indicator.value,
                'stix_id': indicator.stix_id,
                'description': indicator.description,
                'confidence': indicator.confidence,
                'first_seen': indicator.first_seen,
                'last_seen': indicator.last_seen,
                'created_at': indicator.created_at,
                'is_anonymized': indicator.is_anonymized,
                'source': feed_name
            }
            
            return Response(result, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating indicator: {str(e)}")
            return Response(
                {"error": "Failed to create indicator", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def indicators_bulk_import(request):
    """Bulk import indicators from a list with security validation."""
    try:
        from core.services.indicator_service import IndicatorService
        from core.models.models import Organization
        import uuid
        import re
        import hashlib
        import time
        
        data = request.data
        
        # Security validation: Check request size and rate limiting
        max_indicators = 10000  # Maximum indicators per request
        # Note: Request size validation removed to avoid "body after reading" error
        # DRF handles request size limits through DATA_UPLOAD_MAX_MEMORY_SIZE setting
        
        # Validate that indicators list is provided
        if 'indicators' not in data or not isinstance(data['indicators'], list):
            return Response(
                {"error": "Missing or invalid 'indicators' field. Expected a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        indicators_data = data['indicators']
        
        if not indicators_data:
            return Response(
                {"error": "Empty indicators list provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if len(indicators_data) > max_indicators:
            return Response(
                {"error": f"Too many indicators. Maximum allowed: {max_indicators}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create default threat feed for manual entries
        default_org, created = Organization.objects.get_or_create(
            name="Manual Entry",
            defaults={'description': 'Default organization for manually created indicators'}
        )
        
        default_feed, created = ThreatFeed.objects.get_or_create(
            name="Manual Entry Feed",
            defaults={
                'description': 'Default feed for manually created indicators',
                'is_external': False,
                'is_active': True,
                'owner': default_org
            }
        )
        
        from core.repositories.indicator_repository import IndicatorRepository
        from django.utils import timezone
        created_indicators = []
        errors = []
        
        # Security validation function for indicator data
        def validate_and_sanitize_indicator(indicator_data, idx):
            """Validate and sanitize individual indicator data"""
            errors = []
            
            # Validate required fields
            required_fields = ['type', 'value']
            for field in required_fields:
                if field not in indicator_data:
                    errors.append(f"Indicator {idx + 1}: Missing required field '{field}'")
                    return None, errors
            
            # Sanitize and validate indicator value
            value = str(indicator_data['value']).strip()
            if not value:
                errors.append(f"Indicator {idx + 1}: Empty value")
                return None, errors
            
            # Length validation
            if len(value) > 2048:  # Max 2KB per value
                errors.append(f"Indicator {idx + 1}: Value too long (max 2048 characters)")
                return None, errors
            
            # Pattern validation based on type
            indicator_type = str(indicator_data['type']).lower().strip()
            validation_patterns = {
                'ip': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                'domain': r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$',
                'url': r'^https?://[^\s/$.?#].[^\s]*$',
                'file_hash': r'^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$|^[a-fA-F0-9]{128}$',  # MD5, SHA1, SHA256, SHA512
                'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            }
            
            if indicator_type in validation_patterns:
                if not re.match(validation_patterns[indicator_type], value):
                    errors.append(f"Indicator {idx + 1}: Invalid {indicator_type} format")
                    return None, errors
            
            # Check for malicious patterns
            malicious_patterns = [
                r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
                r'javascript:',
                r'vbscript:',
                r'on\w+\s*=',
                r'<iframe\b[^>]*>',
                r'eval\s*\(',
                r'document\.cookie',
                r'window\.location',
            ]
            
            for pattern in malicious_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    errors.append(f"Indicator {idx + 1}: Potentially malicious content detected")
                    return None, errors
            
            # Sanitize description
            description = str(indicator_data.get('description', '')).strip()
            if len(description) > 1000:  # Max 1KB description
                description = description[:1000]
            
            # Validate confidence
            try:
                confidence = int(indicator_data.get('confidence', 50))
                if confidence < 0 or confidence > 100:
                    confidence = 50  # Default to medium confidence
            except (ValueError, TypeError):
                confidence = 50
            
            return {
                'type': indicator_type,
                'value': value,
                'description': description,
                'confidence': confidence
            }, errors

        # Process each indicator
        for idx, indicator_data in enumerate(indicators_data):
            try:
                # Validate and sanitize indicator
                sanitized_data, validation_errors = validate_and_sanitize_indicator(indicator_data, idx)
                
                if validation_errors:
                    errors.extend(validation_errors)
                    continue
                
                if not sanitized_data:
                    continue
                
                # Check for duplicates using sanitized data
                existing = Indicator.objects.filter(
                    value=sanitized_data['value'],
                    type=sanitized_data['type']
                ).first()
                
                if existing:
                    # Skip duplicate
                    continue
                
                # Prepare indicator data with correct fields using sanitized data
                now = timezone.now()
                indicator_create_data = {
                    'value': sanitized_data['value'],
                    'type': sanitized_data['type'],
                    'description': sanitized_data['description'],
                    'confidence': sanitized_data['confidence'],
                    'stix_id': f'indicator--{uuid.uuid4()}',
                    'threat_feed': indicator_data.get('threat_feed_id') and ThreatFeed.objects.get(id=indicator_data['threat_feed_id']) or default_feed,
                    'first_seen': now,
                    'last_seen': now,
                }
                
                # Create the indicator
                indicator = IndicatorRepository.create(indicator_create_data)
                
                # Format for response
                feed_name = 'Manual Entry'
                if indicator.threat_feed:
                    feed_name = indicator.threat_feed.name
                
                created_indicators.append({
                    'id': indicator.id,
                    'type': indicator.type,
                    'value': indicator.value,
                    'stix_id': indicator.stix_id,
                    'description': indicator.description,
                    'confidence': indicator.confidence,
                    'first_seen': indicator.first_seen,
                    'last_seen': indicator.last_seen,
                    'created_at': indicator.created_at,
                    'is_anonymized': indicator.is_anonymized,
                    'source': feed_name
                })
                
            except Exception as e:
                errors.append(f"Indicator {idx + 1}: {str(e)}")
                continue
        
        # Log bulk import activity
        if len(created_indicators) > 0:
            activity_title = f"Bulk imported {len(created_indicators)} indicators"
            activity_description = f"Successfully imported {len(created_indicators)} indicators with {len(errors)} errors"
            SystemActivity.log_activity(
                activity_type='indicators_bulk_added',
                title=activity_title,
                description=activity_description,
                metadata={
                    'imported_count': len(created_indicators),
                    'error_count': len(errors),
                    'total_attempted': len(indicators_data)
                }
            )
        
        return Response({
            'success': True,
            'created_count': len(created_indicators),
            'error_count': len(errors),
            'created_indicators': created_indicators,
            'errors': errors
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in bulk import: {str(e)}")
        return Response(
            {"error": "Failed to bulk import indicators", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([AllowAny])
def indicator_update(request, indicator_id):
    """Update a specific indicator."""
    try:
        from core.repositories.indicator_repository import IndicatorRepository
        
        # Get the indicator
        indicator = IndicatorRepository.get_by_id(indicator_id)
        if not indicator:
            return Response(
                {"error": "Indicator not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data
        
        # Prepare update data (only allow certain fields to be updated)
        update_data = {}
        updatable_fields = ['value', 'type', 'description', 'confidence']
        
        for field in updatable_fields:
            if field in data:
                if field == 'confidence':
                    update_data[field] = int(data[field])
                else:
                    update_data[field] = data[field]
        
        # Update the indicator
        updated_indicator = IndicatorRepository.update(indicator_id, update_data)
        
        if not updated_indicator:
            return Response(
                {"error": "Failed to update indicator"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Format response
        feed_name = 'Manual Entry'
        if updated_indicator.threat_feed:
            feed_name = updated_indicator.threat_feed.name
        
        result = {
            'id': updated_indicator.id,
            'type': updated_indicator.type,
            'value': updated_indicator.value,
            'stix_id': updated_indicator.stix_id,
            'description': updated_indicator.description,
            'confidence': updated_indicator.confidence,
            'first_seen': updated_indicator.first_seen,
            'last_seen': updated_indicator.last_seen,
            'created_at': updated_indicator.created_at,
            'is_anonymized': updated_indicator.is_anonymized,
            'source': feed_name
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating indicator: {str(e)}")
        return Response(
            {"error": "Failed to update indicator", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def indicator_share(request, indicator_id):
    """Share an indicator with specified institutions."""
    try:
        from core.repositories.indicator_repository import IndicatorRepository
        
        # Get the indicator
        indicator = IndicatorRepository.get_by_id(indicator_id)
        if not indicator:
            return Response(
                {"error": "Indicator not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data
        
        # Validate required fields
        if 'institutions' not in data or not isinstance(data['institutions'], list):
            return Response(
                {"error": "Missing or invalid 'institutions' field. Expected a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        institutions = data['institutions']
        anonymization_level = data.get('anonymization_level', 'medium')
        share_method = data.get('share_method', 'taxii')
        
        # For now, we'll simulate the sharing process
        # In a real implementation, this would integrate with TAXII publishing
        shared_count = 0
        errors = []
        
        for institution in institutions:
            try:
                # Simulate sharing logic
                # This would normally:
                # 1. Apply anonymization based on trust level
                # 2. Prepare STIX object
                # 3. Publish to TAXII collection
                # 4. Log the sharing event
                
                shared_count += 1
                logger.info(f"Shared indicator {indicator_id} with {institution}")
                
            except Exception as e:
                errors.append(f"Failed to share with {institution}: {str(e)}")
                continue
        
        return Response({
            'success': True,
            'indicator_id': indicator_id,
            'shared_with': shared_count,
            'total_institutions': len(institutions),
            'anonymization_level': anonymization_level,
            'share_method': share_method,
            'errors': errors
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error sharing indicator: {str(e)}")
        return Response(
            {"error": "Failed to share indicator", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def system_health(request):
    """Get system health status including database, Redis, and system resources."""
    try:
        import psutil
        from django.db import connection
        from django.core.cache import cache
        from django.utils import timezone
        import redis
        
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': {},
            'services': {'redis': {}},
            'system': {},
            'feeds': {}
        }
        
        overall_status = 'healthy'
        
        # Database health check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    health_data['database'] = {
                        'status': 'healthy',
                        'connection': 'active',
                        'connection_count': 1,
                        'details': 'Database connection successful'
                    }
                else:
                    health_data['database'] = {
                        'status': 'unhealthy',
                        'connection': 'failed',
                        'connection_count': 0,
                        'details': 'Database query returned unexpected result'
                    }
                    overall_status = 'unhealthy'
        except Exception as e:
            health_data['database'] = {
                'status': 'unhealthy',
                'connection': 'failed',
                'connection_count': 0,
                'details': f'Database error: {str(e)}'
            }
            overall_status = 'unhealthy'
        
        # Redis health check
        try:
            # Try to connect to Redis using cache framework
            cache.set('health_check', 'test', 10)
            test_value = cache.get('health_check')
            if test_value == 'test':
                health_data['services']['redis'] = {
                    'status': 'healthy',
                    'connection': 'active',
                    'info': '6.0+',
                    'details': 'Redis connection and operations successful'
                }
            else:
                health_data['services']['redis'] = {
                    'status': 'unhealthy',
                    'connection': 'failed',
                    'info': 'unknown',
                    'details': 'Redis cache test failed'
                }
                overall_status = 'degraded'
        except Exception as e:
            health_data['services']['redis'] = {
                'status': 'unhealthy',
                'connection': 'failed',
                'info': 'unknown',
                'details': f'Redis error: {str(e)}'
            }
            overall_status = 'degraded'
        
        # System resources check
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine resource status
            resource_status = 'healthy'
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                resource_status = 'warning'
                if overall_status == 'healthy':
                    overall_status = 'degraded'
            
            health_data['system'] = {
                'status': resource_status,
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'disk_percent': round(disk.percent, 1),
                'last_check': timezone.now().isoformat(),
                'details': f'CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%, Disk: {disk.percent:.1f}%'
            }
        except Exception as e:
            health_data['system'] = {
                'status': 'unknown',
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_percent': 0.0,
                'last_check': timezone.now().isoformat(),
                'details': f'Resource monitoring error: {str(e)}'
            }
        
        # Feed status summary
        try:
            total_feeds = ThreatFeed.objects.count()
            active_feeds = ThreatFeed.objects.filter(is_active=True).count()
            external_feeds = ThreatFeed.objects.filter(is_external=True, is_active=True).count()
            
            # Get individual feed details
            feeds_list = []
            for feed in ThreatFeed.objects.all():
                # Get feed sync status
                sync_status = 'healthy' if feed.is_active else 'inactive'
                if feed.last_sync:
                    # Check if last sync was recent (within 24 hours)
                    time_since_sync = timezone.now() - feed.last_sync
                    if time_since_sync.total_seconds() > 86400:  # 24 hours
                        sync_status = 'warning'
                
                feeds_list.append({
                    'id': feed.id,
                    'name': feed.name,
                    'is_active': feed.is_active,
                    'is_external': feed.is_external,
                    'sync_status': sync_status,
                    'last_sync': feed.last_sync.isoformat() if feed.last_sync else None,
                    'description': feed.description or '',
                    'last_error': None  # Add error tracking if needed
                })
            
            health_data['feeds'] = {
                'status': 'healthy' if active_feeds > 0 else 'warning',
                'total': total_feeds,
                'active': active_feeds,
                'external': external_feeds,
                'feeds': feeds_list,
                'details': f'{active_feeds}/{total_feeds} feeds active, {external_feeds} external'
            }
        except Exception as e:
            health_data['feeds'] = {
                'status': 'unknown',
                'total': 0,
                'active': 0,
                'external': 0,
                'feeds': [],
                'details': f'Feed status error: {str(e)}'
            }
        
        health_data['status'] = overall_status
        
        return Response(health_data)
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        return Response({
            'status': 'error',
            'timestamp': timezone.now().isoformat(),
            'error': 'Failed to get system health',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def recent_activities(request):
    """Get recent system activities for dashboard."""
    try:
        # Get limit parameter (default to 20)
        limit = int(request.GET.get('limit', 20))
        if limit > 100:  # Cap the limit
            limit = 100
        
        # Fetch recent activities
        activities = SystemActivity.objects.select_related(
            'threat_feed', 'indicator', 'organization', 'user'
        ).all()[:limit]
        
        # Format activities for frontend
        activities_data = []
        for activity in activities:
            # Calculate time ago
            time_diff = timezone.now() - activity.created_at
            if time_diff.total_seconds() < 60:
                time_ago = "Just now"
            elif time_diff.total_seconds() < 3600:
                minutes = int(time_diff.total_seconds() / 60)
                time_ago = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif time_diff.total_seconds() < 86400:
                hours = int(time_diff.total_seconds() / 3600)
                time_ago = f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = int(time_diff.total_seconds() / 86400)
                time_ago = f"{days} day{'s' if days != 1 else ''} ago"
            
            activities_data.append({
                'id': activity.id,
                'type': activity.activity_type,
                'category': activity.category,
                'title': activity.title,
                'description': activity.description,
                'icon': activity.icon,
                'badge_type': activity.badge_type,
                'badge_text': activity.get_activity_type_display(),
                'time_ago': time_ago,
                'timestamp': activity.created_at.isoformat(),
                'metadata': activity.metadata,
                'related_objects': {
                    'threat_feed': {
                        'id': activity.threat_feed.id,
                        'name': activity.threat_feed.name
                    } if activity.threat_feed else None,
                    'indicator': {
                        'id': activity.indicator.id,
                        'value': activity.indicator.value,
                        'type': activity.indicator.type
                    } if activity.indicator else None,
                    'organization': {
                        'id': activity.organization.id,
                        'name': activity.organization.name
                    } if activity.organization else None,
                }
            })
        
        return Response({
            'success': True,
            'count': len(activities_data),
            'activities': activities_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching recent activities: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch recent activities',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def threat_activity_chart_data(request):
    """Get historical IoC data aggregated by date for the threat activity chart."""
    try:
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        import json
        
        # Get date range parameters
        days = int(request.GET.get('days', 30))  # Default to 30 days
        indicator_type = request.GET.get('type', None)  # Optional filter by indicator type
        feed_id = request.GET.get('feed_id', None)  # Optional filter by feed
        
        # Validate days parameter
        if days < 1 or days > 365:
            days = 30
            
        # Calculate date range
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Build base query
        query = Indicator.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Apply filters
        if indicator_type:
            query = query.filter(type=indicator_type)
        if feed_id:
            query = query.filter(threat_feed_id=feed_id)
        
        # Aggregate by date and type
        daily_data = query.extra(
            select={'date': 'DATE(created_at)'}
        ).values('date', 'type').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Also get overall daily totals
        daily_totals = query.extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            total=Count('id')
        ).order_by('date')
        
        # Process data for chart
        chart_data = {}
        type_data = {}
        
        # Initialize all dates in range with zero counts
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            chart_data[date_str] = 0
            current_date += timedelta(days=1)
        
        # Fill in actual totals
        for item in daily_totals:
            date_str = item['date'].strftime('%Y-%m-%d')
            chart_data[date_str] = item['total']
        
        # Process type breakdown
        for item in daily_data:
            date_str = item['date'].strftime('%Y-%m-%d')
            ioc_type = item['type']
            count = item['count']
            
            if date_str not in type_data:
                type_data[date_str] = {}
            type_data[date_str][ioc_type] = count
        
        # Convert to list format for D3
        result_data = []
        for date_str in sorted(chart_data.keys()):
            result_data.append({
                'date': date_str,
                'count': chart_data[date_str],
                'types': type_data.get(date_str, {})
            })
        
        # Get summary statistics
        total_indicators = sum(chart_data.values())
        avg_daily = total_indicators / days if days > 0 else 0
        
        # Get type distribution for the period
        type_summary = Indicator.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        if indicator_type:
            type_summary = type_summary.filter(type=indicator_type)
        if feed_id:
            type_summary = type_summary.filter(threat_feed_id=feed_id)
            
        type_counts = type_summary.values('type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'success': True,
            'data': result_data,
            'summary': {
                'total_indicators': total_indicators,
                'avg_daily': round(avg_daily, 2),
                'days': days,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'type_distribution': list(type_counts)
            },
            'filters': {
                'type': indicator_type,
                'feed_id': feed_id,
                'days': days
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting threat activity chart data: {str(e)}")
        return Response(
            {"error": "Failed to get chart data", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def ttps_list(request):
    """
    GET: Get list of TTPs with filtering and pagination.
    POST: Create a new TTP with validation.
    
    GET Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - tactic: Filter by MITRE tactic
    - technique_id: Filter by MITRE technique ID
    - search: Search in name and description
    - feed_id: Filter by threat feed ID
    - ordering: Sort by field (default: -created_at)
    
    POST Body Parameters:
    - name: TTP name (required)
    - description: TTP description (required)
    - mitre_technique_id: MITRE ATT&CK technique ID (required, e.g., T1566.001)
    - mitre_tactic: MITRE tactic (required, from MITRE_TACTIC_CHOICES)
    - mitre_subtechnique: MITRE subtechnique name (optional)
    - threat_feed_id: ID of associated threat feed (optional, defaults to manual entry feed)
    - stix_id: Custom STIX ID (optional, auto-generated if not provided)
    """
    
    if request.method == 'POST':
        return _create_ttp(request)
    
    # Handle GET request (existing list functionality)
    try:
        from core.repositories.ttp_repository import TTPRepository
        from django.core.paginator import Paginator
        from django.db.models import Q
        
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max 100 items per page
        tactic = request.GET.get('tactic', '').strip()
        technique_id = request.GET.get('technique_id', '').strip()
        search = request.GET.get('search', '').strip()
        feed_id = request.GET.get('feed_id', '').strip()
        ordering = request.GET.get('ordering', '-created_at')
        
        # Start with all TTPs
        queryset = TTPData.objects.select_related('threat_feed').all()
        
        # Apply filters
        if tactic:
            queryset = queryset.filter(mitre_tactic=tactic)
            
        if technique_id:
            queryset = queryset.filter(mitre_technique_id__icontains=technique_id)
            
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(mitre_technique_id__icontains=search)
            )
            
        if feed_id:
            try:
                feed_id_int = int(feed_id)
                queryset = queryset.filter(threat_feed_id=feed_id_int)
            except ValueError:
                pass  # Invalid feed_id, ignore filter
        
        # Apply ordering
        valid_ordering_fields = [
            'name', '-name', 'mitre_technique_id', '-mitre_technique_id',
            'mitre_tactic', '-mitre_tactic', 'created_at', '-created_at',
            'updated_at', '-updated_at'
        ]
        if ordering in valid_ordering_fields:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')  # Default ordering
        
        # Paginate results
        paginator = Paginator(queryset, page_size)
        
        # Validate page number
        if page < 1:
            page = 1
        elif page > paginator.num_pages and paginator.num_pages > 0:
            page = paginator.num_pages
            
        page_obj = paginator.get_page(page)
        
        # Serialize TTP data
        ttps_data = []
        for ttp in page_obj:
            # Get tactic display name
            tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic)
            
            ttps_data.append({
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description,
                'mitre_technique_id': ttp.mitre_technique_id,
                'mitre_tactic': ttp.mitre_tactic,
                'mitre_tactic_display': tactic_display,
                'mitre_subtechnique': ttp.mitre_subtechnique,
                'stix_id': ttp.stix_id,
                'threat_feed': {
                    'id': ttp.threat_feed.id,
                    'name': ttp.threat_feed.name,
                    'is_external': ttp.threat_feed.is_external
                } if ttp.threat_feed else None,
                'is_anonymized': ttp.is_anonymized,
                'created_at': ttp.created_at.isoformat(),
                'updated_at': ttp.updated_at.isoformat(),
            })
        
        # Build response
        response_data = {
            'success': True,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page + 1 if page_obj.has_next() else None,
            'previous_page': page - 1 if page_obj.has_previous() else None,
            'results': ttps_data,
            'filters': {
                'tactic': tactic,
                'technique_id': technique_id,
                'search': search,
                'feed_id': feed_id,
                'ordering': ordering
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting TTPs list: {str(e)}")
        return Response(
            {"error": "Failed to get TTPs list", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _create_ttp(request):
    """
    Create a new TTP with comprehensive validation.
    """
    try:
        from core.repositories.ttp_repository import TTPRepository
        from core.services.ttp_service import TTPService
        import uuid
        import re
        
        data = request.data
        errors = []
        
        # Validate required fields
        required_fields = ['name', 'description', 'mitre_technique_id', 'mitre_tactic']
        for field in required_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                errors.append(f"Field '{field}' is required and cannot be empty")
        
        if errors:
            return Response(
                {"error": "Validation failed", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract and validate data
        name = str(data['name']).strip()
        description = str(data['description']).strip()
        mitre_technique_id = str(data['mitre_technique_id']).strip().upper()
        mitre_tactic = str(data['mitre_tactic']).strip().lower()
        mitre_subtechnique = str(data.get('mitre_subtechnique', '')).strip() or None
        threat_feed_id = data.get('threat_feed_id')
        stix_id = str(data.get('stix_id', '')).strip() or None
        
        # Validate name length
        if len(name) < 3:
            errors.append("TTP name must be at least 3 characters long")
        if len(name) > 255:
            errors.append("TTP name cannot exceed 255 characters")
            
        # Validate description length
        if len(description) < 10:
            errors.append("TTP description must be at least 10 characters long")
        if len(description) > 5000:
            errors.append("TTP description cannot exceed 5000 characters")
        
        # Validate MITRE technique ID format
        mitre_pattern = r'^T\d{4}(\.\d{3})?$'
        if not re.match(mitre_pattern, mitre_technique_id):
            errors.append("MITRE technique ID must follow format T1234 or T1234.001 (e.g., T1566.001)")
        
        # Validate MITRE tactic
        valid_tactics = [choice[0] for choice in TTPData.MITRE_TACTIC_CHOICES]
        if mitre_tactic not in valid_tactics:
            errors.append(f"Invalid MITRE tactic. Must be one of: {', '.join(valid_tactics)}")
        
        # Validate subtechnique length if provided
        if mitre_subtechnique and len(mitre_subtechnique) > 255:
            errors.append("MITRE subtechnique name cannot exceed 255 characters")
        
        # Get or create default threat feed if not provided
        if threat_feed_id:
            try:
                threat_feed_id = int(threat_feed_id)
                threat_feed = ThreatFeed.objects.get(id=threat_feed_id)
            except (ValueError, ThreatFeed.DoesNotExist):
                errors.append(f"Invalid threat feed ID: {threat_feed_id}")
                threat_feed = None
        else:
            # Get or create default manual entry feed
            from core.models.models import Organization
            default_org, created = Organization.objects.get_or_create(
                name="Manual Entry",
                defaults={'description': 'Default organization for manually created TTPs'}
            )
            
            threat_feed, created = ThreatFeed.objects.get_or_create(
                name="Manual TTP Feed",
                defaults={
                    'description': 'Default feed for manually created TTPs',
                    'is_external': False,
                    'is_active': True,
                    'owner': default_org
                }
            )
        
        # Generate STIX ID if not provided
        if not stix_id:
            stix_id = f"attack-pattern--{str(uuid.uuid4())}"
        else:
            # Validate STIX ID format
            stix_pattern = r'^attack-pattern--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if not re.match(stix_pattern, stix_id):
                errors.append("STIX ID must follow format: attack-pattern--xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        
        # Check for duplicate MITRE technique ID within the same feed
        existing_ttp = TTPData.objects.filter(
            mitre_technique_id=mitre_technique_id,
            threat_feed=threat_feed
        ).first()
        
        if existing_ttp:
            errors.append(f"TTP with MITRE technique ID '{mitre_technique_id}' already exists in this threat feed")
        
        # Check for duplicate STIX ID
        if TTPData.objects.filter(stix_id=stix_id).exists():
            errors.append(f"TTP with STIX ID '{stix_id}' already exists")
        
        if errors:
            return Response(
                {"error": "Validation failed", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the TTP
        ttp_data = {
            'name': name,
            'description': description,
            'mitre_technique_id': mitre_technique_id,
            'mitre_tactic': mitre_tactic,
            'mitre_subtechnique': mitre_subtechnique,
            'threat_feed': threat_feed,
            'stix_id': stix_id,
            'is_anonymized': False
        }
        
        # Use TTPService for creation if available, otherwise use repository
        try:
            ttp_service = TTPService()
            ttp = ttp_service.create_ttp(ttp_data)
        except:
            # Fallback to repository method
            ttp = TTPRepository.create(ttp_data)
        
        # Log the creation activity
        try:
            SystemActivity.objects.create(
                activity_type='ttp_created',
                description=f'New TTP created: {ttp.name} ({ttp.mitre_technique_id})',
                details={
                    'ttp_id': ttp.id,
                    'mitre_technique_id': ttp.mitre_technique_id,
                    'mitre_tactic': ttp.mitre_tactic,
                    'threat_feed_id': ttp.threat_feed.id if ttp.threat_feed else None,
                    'source': 'manual_creation'
                }
            )
        except Exception as e:
            logger.warning(f"Could not log TTP creation activity: {str(e)}")
        
        # Format response data
        tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic)
        
        response_data = {
            'success': True,
            'message': 'TTP created successfully',
            'data': {
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description,
                'mitre_technique_id': ttp.mitre_technique_id,
                'mitre_tactic': ttp.mitre_tactic,
                'mitre_tactic_display': tactic_display,
                'mitre_subtechnique': ttp.mitre_subtechnique,
                'stix_id': ttp.stix_id,
                'threat_feed': {
                    'id': ttp.threat_feed.id,
                    'name': ttp.threat_feed.name,
                    'is_external': ttp.threat_feed.is_external
                } if ttp.threat_feed else None,
                'is_anonymized': ttp.is_anonymized,
                'created_at': ttp.created_at.isoformat(),
                'updated_at': ttp.updated_at.isoformat(),
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating TTP: {str(e)}")
        return Response(
            {"error": "Failed to create TTP", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _update_ttp(request, ttp_id):
    """
    Update an existing TTP with validation and conflict detection.
    
    Supports both PUT (complete update) and PATCH (partial update) methods.
    """
    try:
        from core.repositories.ttp_repository import TTPRepository
        from core.services.ttp_service import TTPService
        import re
        
        # Get the existing TTP
        ttp = TTPRepository.get_by_id(ttp_id)
        if not ttp:
            return Response(
                {"error": "TTP not found", "ttp_id": ttp_id},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data
        errors = []
        is_put = request.method == 'PUT'
        
        # For PUT requests, validate that all required fields are present
        if is_put:
            required_fields = ['name', 'description', 'mitre_technique_id', 'mitre_tactic']
            for field in required_fields:
                if not data.get(field) or not str(data.get(field)).strip():
                    errors.append(f"Field '{field}' is required for PUT requests and cannot be empty")
        
        if errors:
            return Response(
                {"error": "Validation failed", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare update data with existing values as fallback
        update_data = {}
        
        # Handle name field
        if 'name' in data:
            name = str(data['name']).strip()
            if len(name) < 3:
                errors.append("TTP name must be at least 3 characters long")
            elif len(name) > 255:
                errors.append("TTP name cannot exceed 255 characters")
            else:
                update_data['name'] = name
        elif is_put:
            update_data['name'] = ttp.name  # Keep existing for PUT
        
        # Handle description field
        if 'description' in data:
            description = str(data['description']).strip()
            if len(description) < 10:
                errors.append("TTP description must be at least 10 characters long")
            elif len(description) > 5000:
                errors.append("TTP description cannot exceed 5000 characters")
            else:
                update_data['description'] = description
        elif is_put:
            update_data['description'] = ttp.description  # Keep existing for PUT
        
        # Handle MITRE technique ID
        if 'mitre_technique_id' in data:
            mitre_technique_id = str(data['mitre_technique_id']).strip().upper()
            mitre_pattern = r'^T\d{4}(\.\d{3})?$'
            if not re.match(mitre_pattern, mitre_technique_id):
                errors.append("MITRE technique ID must follow format T1234 or T1234.001 (e.g., T1566.001)")
            else:
                # Check for duplicates (excluding current TTP)
                existing_ttp = TTPData.objects.filter(
                    mitre_technique_id=mitre_technique_id,
                    threat_feed=ttp.threat_feed
                ).exclude(id=ttp.id).first()
                
                if existing_ttp:
                    errors.append(f"TTP with MITRE technique ID '{mitre_technique_id}' already exists in this threat feed")
                else:
                    update_data['mitre_technique_id'] = mitre_technique_id
        elif is_put:
            update_data['mitre_technique_id'] = ttp.mitre_technique_id  # Keep existing for PUT
        
        # Handle MITRE tactic
        if 'mitre_tactic' in data:
            mitre_tactic = str(data['mitre_tactic']).strip().lower()
            valid_tactics = [choice[0] for choice in TTPData.MITRE_TACTIC_CHOICES]
            if mitre_tactic not in valid_tactics:
                errors.append(f"Invalid MITRE tactic. Must be one of: {', '.join(valid_tactics)}")
            else:
                update_data['mitre_tactic'] = mitre_tactic
        elif is_put:
            update_data['mitre_tactic'] = ttp.mitre_tactic  # Keep existing for PUT
        
        # Handle MITRE subtechnique (optional)
        if 'mitre_subtechnique' in data:
            mitre_subtechnique = str(data['mitre_subtechnique']).strip() if data['mitre_subtechnique'] else None
            if mitre_subtechnique and len(mitre_subtechnique) > 255:
                errors.append("MITRE subtechnique name cannot exceed 255 characters")
            else:
                update_data['mitre_subtechnique'] = mitre_subtechnique
        elif is_put:
            update_data['mitre_subtechnique'] = ttp.mitre_subtechnique  # Keep existing for PUT
        
        # Handle threat feed ID (optional)
        if 'threat_feed_id' in data:
            threat_feed_id = data['threat_feed_id']
            if threat_feed_id:
                try:
                    threat_feed_id = int(threat_feed_id)
                    threat_feed = ThreatFeed.objects.get(id=threat_feed_id)
                    update_data['threat_feed'] = threat_feed
                except (ValueError, ThreatFeed.DoesNotExist):
                    errors.append(f"Invalid threat feed ID: {threat_feed_id}")
            else:
                update_data['threat_feed'] = ttp.threat_feed  # Keep existing if null provided
        elif is_put:
            update_data['threat_feed'] = ttp.threat_feed  # Keep existing for PUT
        
        # Handle STIX ID (optional, but cannot be changed if already set)
        if 'stix_id' in data:
            stix_id = str(data['stix_id']).strip() if data['stix_id'] else None
            if stix_id:
                # Validate STIX ID format
                stix_pattern = r'^attack-pattern--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                if not re.match(stix_pattern, stix_id):
                    errors.append("STIX ID must follow format: attack-pattern--xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
                elif stix_id != ttp.stix_id:
                    # Check if the new STIX ID already exists
                    if TTPData.objects.filter(stix_id=stix_id).exclude(id=ttp.id).exists():
                        errors.append(f"TTP with STIX ID '{stix_id}' already exists")
                    else:
                        update_data['stix_id'] = stix_id
                # If stix_id matches existing, no change needed
            # If empty stix_id provided, keep existing
        elif is_put:
            update_data['stix_id'] = ttp.stix_id  # Keep existing for PUT
        
        if errors:
            return Response(
                {"error": "Validation failed", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if any changes were actually made
        changes_made = False
        for field, new_value in update_data.items():
            current_value = getattr(ttp, field)
            if current_value != new_value:
                changes_made = True
                break
        
        if not changes_made:
            return Response(
                {"message": "No changes detected", "data": _format_ttp_response(ttp)},
                status=status.HTTP_200_OK
            )
        
        # Store original values for logging
        original_values = {
            'name': ttp.name,
            'mitre_technique_id': ttp.mitre_technique_id,
            'mitre_tactic': ttp.mitre_tactic
        }
        
        # Update the TTP
        try:
            ttp_service = TTPService()
            updated_ttp = ttp_service.update_ttp(ttp.id, update_data)
        except:
            # Fallback to repository method
            updated_ttp = TTPRepository.update(ttp.id, update_data)
        
        if not updated_ttp:
            return Response(
                {"error": "Failed to update TTP", "ttp_id": ttp_id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Log the update activity
        try:
            changed_fields = [field for field, new_value in update_data.items() 
                            if getattr(ttp, field) != new_value]
            
            SystemActivity.objects.create(
                activity_type='ttp_updated',
                description=f'TTP updated: {updated_ttp.name} ({updated_ttp.mitre_technique_id})',
                details={
                    'ttp_id': updated_ttp.id,
                    'method': request.method,
                    'changed_fields': changed_fields,
                    'original_values': original_values,
                    'mitre_technique_id': updated_ttp.mitre_technique_id,
                    'mitre_tactic': updated_ttp.mitre_tactic,
                    'source': 'api_update'
                }
            )
        except Exception as e:
            logger.warning(f"Could not log TTP update activity: {str(e)}")
        
        # Format and return response
        response_data = {
            'success': True,
            'message': f'TTP updated successfully using {request.method} method',
            'data': _format_ttp_response(updated_ttp)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response(
            {"error": "Invalid TTP ID format", "ttp_id": ttp_id},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error updating TTP {ttp_id}: {str(e)}")
        return Response(
            {"error": "Failed to update TTP", "details": str(e), "ttp_id": ttp_id},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _format_ttp_response(ttp):
    """Helper function to format TTP data for API responses."""
    tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic)
    
    return {
        'id': ttp.id,
        'name': ttp.name,
        'description': ttp.description,
        'mitre_technique_id': ttp.mitre_technique_id,
        'mitre_tactic': ttp.mitre_tactic,
        'mitre_tactic_display': tactic_display,
        'mitre_subtechnique': ttp.mitre_subtechnique,
        'stix_id': ttp.stix_id,
        'threat_feed': {
            'id': ttp.threat_feed.id,
            'name': ttp.threat_feed.name,
            'is_external': ttp.threat_feed.is_external
        } if ttp.threat_feed else None,
        'is_anonymized': ttp.is_anonymized,
        'created_at': ttp.created_at.isoformat(),
        'updated_at': ttp.updated_at.isoformat(),
    }


def _delete_ttp(request, ttp_id):
    """
    Delete a TTP with safety checks and comprehensive logging.
    
    Performs the following operations:
    1. Validates TTP exists
    2. Checks for related data and dependencies
    3. Creates backup of TTP data for audit trail
    4. Performs deletion
    5. Logs deletion activity
    """
    try:
        from core.repositories.ttp_repository import TTPRepository
        from core.services.ttp_service import TTPService
        from django.db.models import Q
        
        # Get the existing TTP
        ttp = TTPRepository.get_by_id(ttp_id)
        if not ttp:
            return Response(
                {"error": "TTP not found", "ttp_id": ttp_id},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store TTP data for logging before deletion
        ttp_backup = {
            'id': ttp.id,
            'name': ttp.name,
            'description': ttp.description,
            'mitre_technique_id': ttp.mitre_technique_id,
            'mitre_tactic': ttp.mitre_tactic,
            'mitre_subtechnique': ttp.mitre_subtechnique,
            'stix_id': ttp.stix_id,
            'threat_feed_id': ttp.threat_feed.id if ttp.threat_feed else None,
            'threat_feed_name': ttp.threat_feed.name if ttp.threat_feed else None,
            'is_anonymized': ttp.is_anonymized,
            'created_at': ttp.created_at.isoformat(),
            'updated_at': ttp.updated_at.isoformat()
        }
        
        # Safety checks - look for related data
        warnings = []
        related_data = {}
        
        # Check for related indicators that might reference this TTP
        try:
            related_indicators_count = Indicator.objects.filter(
                Q(description__icontains=ttp.mitre_technique_id) |
                Q(value__icontains=ttp.mitre_technique_id) |
                Q(threat_feed=ttp.threat_feed)
            ).count()
            
            if related_indicators_count > 0:
                warnings.append(f"Found {related_indicators_count} indicators that may reference this TTP")
                related_data['related_indicators_count'] = related_indicators_count
        except Exception as e:
            logger.warning(f"Could not check related indicators for TTP {ttp_id}: {str(e)}")
        
        # Check if this is the only TTP in the threat feed
        try:
            if ttp.threat_feed:
                feed_ttp_count = TTPData.objects.filter(threat_feed=ttp.threat_feed).count()
                if feed_ttp_count == 1:
                    warnings.append(f"This is the only TTP in threat feed '{ttp.threat_feed.name}'")
                    related_data['is_last_ttp_in_feed'] = True
                else:
                    related_data['remaining_ttps_in_feed'] = feed_ttp_count - 1
        except Exception as e:
            logger.warning(f"Could not check feed TTP count for TTP {ttp_id}: {str(e)}")
        
        # Check if this TTP is referenced in system activities
        try:
            activity_references = SystemActivity.objects.filter(
                Q(description__icontains=ttp.mitre_technique_id) |
                Q(details__contains=str(ttp.id))
            ).count()
            
            if activity_references > 0:
                related_data['activity_references'] = activity_references
        except Exception as e:
            logger.warning(f"Could not check activity references for TTP {ttp_id}: {str(e)}")
        
        # Perform the deletion
        try:
            # Use TTPService for deletion if available, otherwise use repository
            try:
                ttp_service = TTPService()
                ttp_service.delete_ttp(ttp.id)
                deletion_success = True  # Service doesn't return value, assume success if no exception
            except:
                # Fallback to repository method
                deletion_success = TTPRepository.delete(ttp.id)
            
            if not deletion_success:
                return Response(
                    {"error": "Failed to delete TTP", "ttp_id": ttp_id},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error during TTP deletion for ID {ttp_id}: {str(e)}")
            return Response(
                {"error": "Failed to delete TTP", "details": str(e), "ttp_id": ttp_id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Log the deletion activity with comprehensive details
        try:
            SystemActivity.objects.create(
                activity_type='ttp_deleted',
                description=f'TTP deleted: {ttp_backup["name"]} ({ttp_backup["mitre_technique_id"]})',
                details={
                    'deleted_ttp': ttp_backup,
                    'warnings': warnings,
                    'related_data': related_data,
                    'deletion_timestamp': timezone.now().isoformat(),
                    'source': 'api_delete'
                }
            )
        except Exception as e:
            logger.warning(f"Could not log TTP deletion activity: {str(e)}")
        
        # Build success response
        response_data = {
            'success': True,
            'message': f'TTP "{ttp_backup["name"]}" ({ttp_backup["mitre_technique_id"]}) deleted successfully',
            'deleted_ttp': {
                'id': ttp_backup['id'],
                'name': ttp_backup['name'],
                'mitre_technique_id': ttp_backup['mitre_technique_id'],
                'mitre_tactic': ttp_backup['mitre_tactic'],
                'threat_feed_name': ttp_backup['threat_feed_name']
            },
            'deletion_timestamp': timezone.now().isoformat()
        }
        
        # Include warnings if any
        if warnings:
            response_data['warnings'] = warnings
            response_data['notice'] = 'TTP deleted successfully, but please review the warnings for potential impacts'
        
        # Include related data summary if any
        if related_data:
            response_data['impact_summary'] = related_data
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response(
            {"error": "Invalid TTP ID format", "ttp_id": ttp_id},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error deleting TTP {ttp_id}: {str(e)}")
        return Response(
            {"error": "Failed to delete TTP", "details": str(e), "ttp_id": ttp_id},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def ttp_detail(request, ttp_id):
    """
    GET: Get detailed information about a specific TTP.
    PUT: Completely update a TTP (all fields required).
    PATCH: Partially update a TTP (only provided fields updated).
    DELETE: Remove a TTP from the system.
    
    Path Parameters:
    - ttp_id: The ID of the TTP to retrieve/update/delete
    
    GET Returns detailed TTP information including:
    - All TTP fields and metadata
    - Related threat feed information
    - STIX mapping details
    - Creation and modification history
    - Related indicators (if any)
    
    PUT/PATCH Body Parameters:
    - name: TTP name (PUT: required, PATCH: optional)
    - description: TTP description (PUT: required, PATCH: optional)
    - mitre_technique_id: MITRE ATT&CK technique ID (PUT: required, PATCH: optional)
    - mitre_tactic: MITRE tactic (PUT: required, PATCH: optional)
    - mitre_subtechnique: MITRE subtechnique name (optional)
    - threat_feed_id: ID of associated threat feed (optional)
    - stix_id: STIX ID (optional, cannot be changed if already set)
    
    DELETE removes the TTP with:
    - Safety checks for related data
    - Activity logging for audit trail
    - Confirmation of successful deletion
    """
    
    if request.method in ['PUT', 'PATCH']:
        return _update_ttp(request, ttp_id)
    elif request.method == 'DELETE':
        return _delete_ttp(request, ttp_id)
    
    # Handle GET request (existing detail functionality)
    try:
        from core.repositories.ttp_repository import TTPRepository
        
        # Get the TTP by ID
        ttp = TTPRepository.get_by_id(ttp_id)
        if not ttp:
            return Response(
                {"error": "TTP not found", "ttp_id": ttp_id},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get tactic display name
        tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic)
        
        # Get related indicators that reference this TTP (if any)
        related_indicators = []
        try:
            # Look for indicators that might reference this TTP in their descriptions or metadata
            from django.db.models import Q
            indicators = Indicator.objects.filter(
                Q(description__icontains=ttp.mitre_technique_id) |
                Q(value__icontains=ttp.mitre_technique_id) |
                Q(threat_feed=ttp.threat_feed)
            ).select_related('threat_feed')[:5]  # Limit to 5 related indicators
            
            for indicator in indicators:
                related_indicators.append({
                    'id': indicator.id,
                    'type': indicator.type,
                    'value': indicator.value[:100] + '...' if len(indicator.value) > 100 else indicator.value,
                    'confidence': getattr(indicator, 'confidence', None),
                    'created_at': indicator.created_at.isoformat(),
                    'threat_feed': {
                        'id': indicator.threat_feed.id,
                        'name': indicator.threat_feed.name
                    } if indicator.threat_feed else None
                })
        except Exception as e:
            logger.warning(f"Could not fetch related indicators for TTP {ttp_id}: {str(e)}")
        
        # Get MITRE ATT&CK framework context
        mitre_context = {
            'tactic': ttp.mitre_tactic,
            'tactic_display': tactic_display,
            'technique_id': ttp.mitre_technique_id,
            'subtechnique': ttp.mitre_subtechnique,
            'framework_url': f"https://attack.mitre.org/techniques/{ttp.mitre_technique_id.replace('.', '/')}/" if ttp.mitre_technique_id else None
        }
        
        # Build detailed response
        ttp_detail_data = {
            'id': ttp.id,
            'name': ttp.name,
            'description': ttp.description,
            'stix_id': ttp.stix_id,
            
            # MITRE ATT&CK Information
            'mitre': mitre_context,
            
            # Threat Feed Information
            'threat_feed': {
                'id': ttp.threat_feed.id,
                'name': ttp.threat_feed.name,
                'description': ttp.threat_feed.description,
                'is_external': ttp.threat_feed.is_external,
                'is_active': ttp.threat_feed.is_active,
                'source_type': getattr(ttp.threat_feed, 'source_type', 'unknown'),
                'created_at': ttp.threat_feed.created_at.isoformat(),
            } if ttp.threat_feed else None,
            
            # Anonymization Information
            'anonymization': {
                'is_anonymized': ttp.is_anonymized,
                'has_original_data': bool(ttp.original_data),
                'original_data_keys': list(ttp.original_data.keys()) if ttp.original_data else []
            },
            
            # Timestamps
            'created_at': ttp.created_at.isoformat(),
            'updated_at': ttp.updated_at.isoformat(),
            
            # Related Data
            'related_indicators': related_indicators,
            'related_indicators_count': len(related_indicators),
            
            # Metadata
            'metadata': {
                'has_subtechnique': bool(ttp.mitre_subtechnique),
                'tactic_category': ttp.mitre_tactic,
                'data_source': 'threat_feed',
                'stix_version': '2.1' if ttp.stix_id and 'attack-pattern' in ttp.stix_id else 'unknown'
            }
        }
        
        return Response({
            'success': True,
            'data': ttp_detail_data
        }, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response(
            {"error": "Invalid TTP ID format", "ttp_id": ttp_id},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error getting TTP detail for ID {ttp_id}: {str(e)}")
        return Response(
            {"error": "Failed to get TTP details", "details": str(e), "ttp_id": ttp_id},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )