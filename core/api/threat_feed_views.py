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
    """Bulk import indicators from a list."""
    try:
        from core.services.indicator_service import IndicatorService
        from core.models.models import Organization
        import uuid
        
        data = request.data
        
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
        
        # Process each indicator
        for idx, indicator_data in enumerate(indicators_data):
            try:
                # Validate required fields
                required_fields = ['type', 'value']
                for field in required_fields:
                    if field not in indicator_data:
                        errors.append(f"Indicator {idx + 1}: Missing required field '{field}'")
                        continue
                
                # Check for duplicates (optional - can be modified based on business logic)
                existing = Indicator.objects.filter(
                    value=indicator_data['value'].strip(),
                    type=indicator_data['type']
                ).first()
                
                if existing:
                    # Skip duplicate
                    continue
                
                # Prepare indicator data with correct fields
                now = timezone.now()
                indicator_create_data = {
                    'value': indicator_data['value'].strip(),
                    'type': indicator_data['type'],
                    'description': indicator_data.get('description', ''),
                    'confidence': int(indicator_data.get('confidence', 50)),
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