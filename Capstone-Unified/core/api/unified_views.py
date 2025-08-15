"""
Unified API Views for CRISP Integration

These views combine functionality from both Core and Trust systems while preserving
ALL existing API functionality and response formats.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from django.http import Http404

from .permissions import (
    IsAuthenticated, IsPublisher, IsAdmin, IsViewer,
    ThreatIntelligencePermission, TrustManagementPermission,
    UserManagementPermission, OrganizationBasedPermission
)
from .response_utils import (
    UnifiedResponseFormatter, LegacyResponseHandler,
    get_user_context, filter_by_organization,
    get_organization_accessible_data
)

# Import models from both systems
from core.models.models import ThreatFeed, Indicator, TTPData, Collection, Organization as CoreOrganization
from core.serializers.threat_feed_serializer import ThreatFeedSerializer

# Import Trust system models and services
try:
    from core_ut.user_management.models.user_models import CustomUser, Organization as TrustOrganization
    from core_ut.trust.models.trust_models import TrustRelationship, TrustGroup
    from core_ut.user_management.services.user_service import UserService
    from core_ut.trust.services.trust_service import TrustService
    TRUST_SYSTEM_AVAILABLE = True
except ImportError:
    TRUST_SYSTEM_AVAILABLE = False

import logging

logger = logging.getLogger(__name__)


class UnifiedThreatFeedViewSet(viewsets.ModelViewSet):
    """
    Unified Threat Feed ViewSet that preserves ALL Core system functionality
    while adding Trust system authentication and organization-based access control.
    """
    
    queryset = ThreatFeed.objects.all()
    serializer_class = ThreatFeedSerializer
    permission_classes = [ThreatIntelligencePermission]
    
    def get_queryset(self):
        """Filter queryset based on user's organization and permissions"""
        queryset = super().get_queryset()
        
        # Preserve Core system behavior for backward compatibility
        if not TRUST_SYSTEM_AVAILABLE:
            return queryset
        
        # Apply organization-based filtering for Trust system users
        return filter_by_organization(queryset, self.request.user, "owner")
    
    @action(detail=False, methods=['get'])
    def external(self, request):
        """
        Get all external threat feeds.
        Preserves exact Core system API response format.
        """
        try:
            external_feeds = self.get_queryset().filter(is_external=True)
            serializer = self.get_serializer(external_feeds, many=True)
            
            # Preserve original Core system response format
            return LegacyResponseHandler.threat_feed_response(serializer.data, "external")
            
        except Exception as e:
            logger.error(f"Error retrieving external feeds: {str(e)}")
            return UnifiedResponseFormatter.error_response(
                message="Failed to retrieve external feeds",
                details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                preserve_format=True
            )
    
    @action(detail=False, methods=['get'])
    def available_collections(self, request):
        """
        Get available TAXII collections from configured sources.
        Preserves exact Core system API response format.
        """
        try:
            from core.services.otx_taxii_service import OTXTaxiiService
            service = OTXTaxiiService()
            collections = service.get_collections()
            
            # Preserve original Core system response format
            return LegacyResponseHandler.core_system_response(collections)
            
        except Exception as e:
            logger.error(f"Error retrieving collections: {str(e)}")
            return Response(
                {"error": "Failed to retrieve collections", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """
        Consume indicators from a specific threat feed.
        Preserves exact Core system API behavior and response format.
        """
        logger.info(f"CONSUME API CALLED for feed ID: {pk}")
        
        try:
            # Get feed with organization-aware filtering
            feed = get_object_or_404(self.get_queryset(), pk=pk)
            logger.info(f"Found feed: {feed.name}, collection: {feed.taxii_collection_id}")
            
            # Parse parameters (preserve Core system parameter handling)
            limit_param = request.query_params.get('limit')
            batch_size = request.query_params.get('batch_size', 100)
            force_days = request.query_params.get('force_days')
            
            # Validate parameters (preserve Core system validation)
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
            
            logger.info(f"Parameters: limit={limit}, force_days={force_days}, batch_size={batch_size}")
            
            # Use OTXTaxiiService (preserve Core system service usage)
            from core.services.otx_taxii_service import OTXTaxiiService
            service = OTXTaxiiService()
            
            # Handle async processing (preserve Core system async behavior)
            if request.query_params.get('async', '').lower() == 'true':
                try:
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
                except ImportError:
                    # Celery not available, fall back to synchronous processing
                    pass
            
            # Process the feed
            stats = service.consume_feed(feed)
            
            # Format response (preserve Core system response format)
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

            return LegacyResponseHandler.threat_feed_response(formatted_stats, "consume")
            
        except Http404:
            return Response(
                {"error": "Threat feed not found or not accessible"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error consuming feed: {str(e)}")
            return Response(
                {"error": "Failed to consume feed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get the status of the threat feed.
        Preserves exact Core system API response format.
        """
        try:
            feed = get_object_or_404(self.get_queryset(), pk=pk)
            
            # Get counts with organization-aware filtering
            indicator_queryset = Indicator.objects.filter(threat_feed_id=pk)
            ttp_queryset = TTPData.objects.filter(threat_feed_id=pk)
            
            # Apply organization filtering if Trust system is available
            if TRUST_SYSTEM_AVAILABLE and hasattr(request.user, 'organization'):
                # Filter by accessible organizations
                pass  # Indicators and TTPs inherit organization from their feed
            
            indicator_count = indicator_queryset.count()
            ttp_count = ttp_queryset.count()
            
            # Get the most recent indicator
            latest_indicator = indicator_queryset.order_by('-created_at').first()
            latest_date = latest_indicator.created_at if latest_indicator else None
            
            response_data = {
                "name": feed.name,
                "is_external": feed.is_external,
                "is_active": feed.is_active,
                "last_sync": feed.last_sync,
                "indicator_count": indicator_count,
                "ttp_count": ttp_count,
                "latest_indicator_date": latest_date
            }
            
            return LegacyResponseHandler.threat_feed_response(response_data, "status")
            
        except Http404:
            return Response(
                {"error": "Threat feed not found or not accessible"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting feed status: {str(e)}")
            return Response(
                {"error": "Failed to get feed status", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def test_connection(self, request, pk=None):
        """
        Test TAXII connection without consuming.
        Preserves exact Core system API behavior.
        """
        try:
            feed = get_object_or_404(self.get_queryset(), pk=pk)
            
            from core.services.otx_taxii_service import OTXTaxiiService
            service = OTXTaxiiService()
            
            # Test getting collections
            collections = service.get_collections()
            
            return Response({
                "status": "success",
                "feed_name": feed.name,
                "collections_found": len(collections),
                "collections": collections[:3]
            })
            
        except Http404:
            return Response(
                {"error": "Threat feed not found or not accessible"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({
                "status": "error", 
                "error": str(e)
            }, status=500)


class UnifiedDashboardViewSet(viewsets.ViewSet):
    """
    Unified dashboard that combines data from both Core and Trust systems.
    """
    
    permission_classes = [IsViewer]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get comprehensive dashboard overview combining both systems.
        """
        try:
            user = request.user
            dashboard_data = {
                "user_info": get_user_context(request),
                "threat_intelligence": self._get_threat_intelligence_summary(user),
                "organization": self._get_organization_summary(user),
                "trust_relationships": self._get_trust_summary(user) if TRUST_SYSTEM_AVAILABLE else {},
                "recent_activity": self._get_recent_activity(user),
            }
            
            return UnifiedResponseFormatter.success_response(
                data=dashboard_data,
                message="Dashboard data retrieved successfully",
                meta={"data_sources": ["core", "trust"] if TRUST_SYSTEM_AVAILABLE else ["core"]}
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {str(e)}")
            return UnifiedResponseFormatter.error_response(
                message="Failed to retrieve dashboard data",
                details=str(e)
            )
    
    def _get_threat_intelligence_summary(self, user):
        """Get threat intelligence summary for user's organization"""
        try:
            feeds = filter_by_organization(ThreatFeed.objects.all(), user, "owner")
            indicators = Indicator.objects.filter(threat_feed__in=feeds) if feeds.exists() else Indicator.objects.none()
            ttps = TTPData.objects.filter(threat_feed__in=feeds) if feeds.exists() else TTPData.objects.none()
            
            return {
                "total_feeds": feeds.count(),
                "active_feeds": feeds.filter(is_active=True).count(),
                "total_indicators": indicators.count(),
                "total_ttps": ttps.count(),
                "recent_indicators": indicators.order_by('-created_at')[:5].count()
            }
        except Exception as e:
            logger.error(f"Error getting threat intelligence summary: {str(e)}")
            return {}
    
    def _get_organization_summary(self, user):
        """Get organization summary"""
        if not hasattr(user, 'organization') or not user.organization:
            return {"has_organization": False}
        
        org = user.organization
        return {
            "has_organization": True,
            "name": org.name,
            "id": str(org.id),
            "domain": getattr(org, 'domain', ''),
            "is_publisher": getattr(org, 'is_publisher', False),
        }
    
    def _get_trust_summary(self, user):
        """Get trust relationship summary"""
        if not TRUST_SYSTEM_AVAILABLE or not hasattr(user, 'organization') or not user.organization:
            return {}
        
        try:
            trust_service = TrustService()
            relationships = trust_service.get_trust_relationships(user)
            
            if relationships.get('success'):
                trust_data = relationships.get('relationships', [])
                return {
                    "total_relationships": len(trust_data),
                    "active_relationships": len([r for r in trust_data if r.get('is_active')]),
                    "outgoing_relationships": len([r for r in trust_data if r.get('relationship_type') == 'outgoing']),
                    "incoming_relationships": len([r for r in trust_data if r.get('relationship_type') == 'incoming']),
                }
            
            return {"total_relationships": 0}
            
        except Exception as e:
            logger.error(f"Error getting trust summary: {str(e)}")
            return {}
    
    def _get_recent_activity(self, user):
        """Get recent activity summary"""
        try:
            activity = []
            
            # Recent threat feed updates
            recent_feeds = filter_by_organization(
                ThreatFeed.objects.filter(last_sync__isnull=False).order_by('-last_sync')[:5],
                user, "owner"
            )
            
            for feed in recent_feeds:
                activity.append({
                    "type": "threat_feed_sync",
                    "description": f"Threat feed '{feed.name}' synchronized",
                    "timestamp": feed.last_sync,
                    "feed_id": feed.id
                })
            
            # Sort by timestamp
            activity.sort(key=lambda x: x['timestamp'] if x['timestamp'] else timezone.now(), reverse=True)
            
            return activity[:10]  # Return last 10 activities
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {str(e)}")
            return []


class UnifiedCollectionViewSet(viewsets.ModelViewSet):
    """
    Unified Collection ViewSet for STIX collections.
    Preserves Core system functionality while adding Trust system access control.
    """
    
    queryset = Collection.objects.all()
    permission_classes = [ThreatIntelligencePermission]
    
    def get_queryset(self):
        """Filter collections based on user's organization"""
        queryset = super().get_queryset()
        return filter_by_organization(queryset, self.request.user, "owner")
    
    @action(detail=True, methods=['get'])
    def objects(self, request, pk=None):
        """Get STIX objects from a collection"""
        try:
            collection = get_object_or_404(self.get_queryset(), pk=pk)
            
            # Get STIX objects with organization filtering
            stix_objects = collection.stix_objects.all()
            
            # Apply additional filtering based on user's accessible organizations
            if TRUST_SYSTEM_AVAILABLE:
                stix_objects = get_organization_accessible_data(
                    request.user, stix_objects.model, "source_organization"
                ).filter(id__in=stix_objects.values_list('id', flat=True))
            
            # Format objects for response
            objects_data = []
            for obj in stix_objects[:100]:  # Limit to 100 objects per request
                objects_data.append({
                    "id": str(obj.id),
                    "stix_id": obj.stix_id,
                    "stix_type": obj.stix_type,
                    "created": obj.created,
                    "modified": obj.modified,
                    "labels": obj.labels,
                    "confidence": obj.confidence
                })
            
            return UnifiedResponseFormatter.success_response(
                data={
                    "collection_id": str(collection.id),
                    "collection_title": collection.title,
                    "objects": objects_data,
                    "total_objects": stix_objects.count()
                }
            )
            
        except Http404:
            return UnifiedResponseFormatter.error_response(
                message="Collection not found or not accessible",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting collection objects: {str(e)}")
            return UnifiedResponseFormatter.error_response(
                message="Failed to retrieve collection objects",
                details=str(e)
            )
    
    @action(detail=True, methods=['post'])
    def generate_bundle(self, request, pk=None):
        """Generate STIX bundle from collection"""
        try:
            collection = get_object_or_404(self.get_queryset(), pk=pk)
            
            # Generate bundle with organization-aware filtering
            bundle = collection.generate_bundle(
                requesting_org=getattr(request.user, 'organization', None)
            )
            
            return UnifiedResponseFormatter.success_response(
                data=bundle,
                message="Bundle generated successfully"
            )
            
        except Http404:
            return UnifiedResponseFormatter.error_response(
                message="Collection not found or not accessible",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error generating bundle: {str(e)}")
            return UnifiedResponseFormatter.error_response(
                message="Failed to generate bundle",
                details=str(e)
            )