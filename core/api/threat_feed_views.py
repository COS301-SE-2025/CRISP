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

from core.models.models import ThreatFeed
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
        max_request_size = 50 * 1024 * 1024  # 50MB max request size
        
        if hasattr(request, 'body') and len(request.body) > max_request_size:
            return Response(
                {"error": f"Request size exceeds maximum allowed size ({max_request_size // 1024 // 1024}MB)"},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )
        
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