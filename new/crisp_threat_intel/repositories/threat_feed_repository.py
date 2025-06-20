from typing import List, Dict, Any, Optional
from django.db.models import Q
from .base import BaseRepository
from ..domain.models import ThreatFeed, Institution


class ThreatFeedRepository(BaseRepository[ThreatFeed]):
    """
    Repository for managing threat feeds
    """
    
    def __init__(self):
        super().__init__(ThreatFeed)
    
    def get_by_institution(self, institution: Institution) -> List[ThreatFeed]:
        """Get all threat feeds for an institution"""
        return list(self.model_class.objects.filter(institution=institution))
    
    def get_active_feeds(self) -> List[ThreatFeed]:
        """Get all active threat feeds"""
        return list(self.model_class.objects.filter(status='active'))
    
    def get_feeds_for_publishing(self) -> List[ThreatFeed]:
        """Get feeds that are ready for publishing"""
        from django.utils import timezone
        return list(self.model_class.objects.filter(
            status='active',
            next_publish_time__lte=timezone.now()
        ))
    
    def get_by_name(self, name: str, institution: Institution = None) -> Optional[ThreatFeed]:
        """Get threat feed by name, optionally scoped to institution"""
        queryset = self.model_class.objects.filter(name=name)
        if institution:
            queryset = queryset.filter(institution=institution)
        return queryset.first()
    
    def search(self, query_params: Dict[str, Any]) -> List[ThreatFeed]:
        """Search threat feeds based on query parameters"""
        queryset = self.model_class.objects.all()
        
        # Filter by name (case-insensitive partial match)
        if 'name' in query_params:
            queryset = queryset.filter(name__icontains=query_params['name'])
        
        # Filter by institution
        if 'institution' in query_params:
            queryset = queryset.filter(institution=query_params['institution'])
        
        # Filter by status
        if 'status' in query_params:
            queryset = queryset.filter(status=query_params['status'])
        
        # Filter by description
        if 'description' in query_params:
            queryset = queryset.filter(description__icontains=query_params['description'])
        
        # Filter by created date range
        if 'created_after' in query_params:
            queryset = queryset.filter(created_at__gte=query_params['created_after'])
        
        if 'created_before' in query_params:
            queryset = queryset.filter(created_at__lte=query_params['created_before'])
        
        # Filter by update interval
        if 'min_update_interval' in query_params:
            queryset = queryset.filter(update_interval__gte=query_params['min_update_interval'])
        
        if 'max_update_interval' in query_params:
            queryset = queryset.filter(update_interval__lte=query_params['max_update_interval'])
        
        # Filter by error count
        if 'max_error_count' in query_params:
            queryset = queryset.filter(error_count__lte=query_params['max_error_count'])
        
        # Filter by publish count
        if 'min_publish_count' in query_params:
            queryset = queryset.filter(publish_count__gte=query_params['min_publish_count'])
        
        # Text search across multiple fields
        if 'search' in query_params:
            search_term = query_params['search']
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(institution__name__icontains=search_term)
            )
        
        # Order results
        order_by = query_params.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)
        
        # Apply limit
        if 'limit' in query_params:
            queryset = queryset[:query_params['limit']]
        
        return list(queryset)
    
    def get_feeds_with_indicators(self) -> List[ThreatFeed]:
        """Get threat feeds that have indicators"""
        return list(self.model_class.objects.filter(indicators__isnull=False).distinct())
    
    def get_feeds_with_ttps(self) -> List[ThreatFeed]:
        """Get threat feeds that have TTPs"""
        return list(self.model_class.objects.filter(ttp_data__isnull=False).distinct())
    
    def get_feeds_by_subscriber(self, institution: Institution) -> List[ThreatFeed]:
        """Get threat feeds that an institution is subscribed to"""
        return list(self.model_class.objects.filter(
            subscriptions__institution=institution,
            subscriptions__is_active=True
        ))
    
    def get_popular_feeds(self, limit: int = 10) -> List[ThreatFeed]:
        """Get most popular feeds based on subscriber count"""
        from django.db.models import Count
        return list(self.model_class.objects.annotate(
            subscriber_count=Count('subscriptions', filter=Q(subscriptions__is_active=True))
        ).order_by('-subscriber_count')[:limit])
    
    def get_recently_updated_feeds(self, limit: int = 10) -> List[ThreatFeed]:
        """Get recently updated feeds"""
        return list(self.model_class.objects.order_by('-updated_at')[:limit])
    
    def get_feeds_with_errors(self) -> List[ThreatFeed]:
        """Get feeds that have errors"""
        return list(self.model_class.objects.filter(error_count__gt=0))
    
    def update_feed_metrics(self, feed_id: str, metrics: Dict[str, Any]) -> bool:
        """Update feed metrics"""
        try:
            feed = self.get_by_id(feed_id)
            if not feed:
                return False
            
            # Update metrics fields
            if 'publish_count' in metrics:
                feed.publish_count = metrics['publish_count']
            
            if 'error_count' in metrics:
                feed.error_count = metrics['error_count']
            
            if 'last_published_time' in metrics:
                feed.last_published_time = metrics['last_published_time']
            
            if 'last_error' in metrics:
                feed.last_error = metrics['last_error']
            
            if 'status' in metrics:
                feed.status = metrics['status']
            
            feed.save()
            return True
            
        except Exception:
            return False
    
    def get_feeds_statistics(self) -> Dict[str, Any]:
        """Get overall feed statistics"""
        from django.db.models import Count, Avg
        
        stats = self.model_class.objects.aggregate(
            total_feeds=Count('id'),
            active_feeds=Count('id', filter=Q(status='active')),
            paused_feeds=Count('id', filter=Q(status='paused')),
            error_feeds=Count('id', filter=Q(status='error')),
            avg_update_interval=Avg('update_interval'),
            avg_publish_count=Avg('publish_count'),
            avg_error_count=Avg('error_count')
        )
        
        return stats