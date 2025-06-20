from typing import List, Dict, Any, Optional
from django.db.models import Q
from django.utils import timezone
from .base import BaseRepository
from ..domain.models import Indicator, ThreatFeed


class IndicatorRepository(BaseRepository[Indicator]):
    """
    Repository for managing indicators
    """
    
    def __init__(self):
        super().__init__(Indicator)
    
    def get_by_threat_feed(self, threat_feed: ThreatFeed) -> List[Indicator]:
        """Get all indicators for a threat feed"""
        return list(self.model_class.objects.filter(threat_feed=threat_feed))
    
    def get_by_stix_id(self, stix_id: str) -> Optional[Indicator]:
        """Get indicator by STIX ID"""
        return self.model_class.objects.filter(stix_id=stix_id).first()
    
    def get_active_indicators(self, threat_feed: ThreatFeed = None) -> List[Indicator]:
        """Get indicators that are currently valid"""
        queryset = self.model_class.objects.filter(
            revoked=False
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gt=timezone.now())
        )
        
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        return list(queryset)
    
    def get_by_pattern(self, pattern: str) -> List[Indicator]:
        """Get indicators by pattern (exact match)"""
        return list(self.model_class.objects.filter(pattern=pattern))
    
    def get_by_labels(self, labels: List[str]) -> List[Indicator]:
        """Get indicators that have any of the specified labels"""
        return list(self.model_class.objects.filter(labels__overlap=labels))
    
    def search(self, query_params: Dict[str, Any]) -> List[Indicator]:
        """Search indicators based on query parameters"""
        queryset = self.model_class.objects.all()
        
        # Filter by threat feed
        if 'threat_feed' in query_params:
            queryset = queryset.filter(threat_feed=query_params['threat_feed'])
        
        # Filter by name (case-insensitive partial match)
        if 'name' in query_params:
            queryset = queryset.filter(name__icontains=query_params['name'])
        
        # Filter by description
        if 'description' in query_params:
            queryset = queryset.filter(description__icontains=query_params['description'])
        
        # Filter by pattern
        if 'pattern' in query_params:
            queryset = queryset.filter(pattern__icontains=query_params['pattern'])
        
        # Filter by labels
        if 'labels' in query_params:
            labels = query_params['labels']
            if isinstance(labels, list):
                queryset = queryset.filter(labels__overlap=labels)
            else:
                queryset = queryset.filter(labels__contains=[labels])
        
        # Filter by confidence range
        if 'min_confidence' in query_params:
            queryset = queryset.filter(confidence__gte=query_params['min_confidence'])
        
        if 'max_confidence' in query_params:
            queryset = queryset.filter(confidence__lte=query_params['max_confidence'])
        
        # Filter by validity period
        if 'valid_from_after' in query_params:
            queryset = queryset.filter(valid_from__gte=query_params['valid_from_after'])
        
        if 'valid_from_before' in query_params:
            queryset = queryset.filter(valid_from__lte=query_params['valid_from_before'])
        
        # Filter by creation date
        if 'created_after' in query_params:
            queryset = queryset.filter(created__gte=query_params['created_after'])
        
        if 'created_before' in query_params:
            queryset = queryset.filter(created__lte=query_params['created_before'])
        
        # Filter by modification date
        if 'modified_after' in query_params:
            queryset = queryset.filter(modified__gte=query_params['modified_after'])
        
        if 'modified_before' in query_params:
            queryset = queryset.filter(modified__lte=query_params['modified_before'])
        
        # Filter by revocation status
        if 'revoked' in query_params:
            queryset = queryset.filter(revoked=query_params['revoked'])
        
        # Filter by anonymization status
        if 'anonymized' in query_params:
            queryset = queryset.filter(anonymized=query_params['anonymized'])
        
        # Filter by creator
        if 'created_by' in query_params:
            queryset = queryset.filter(created_by=query_params['created_by'])
        
        # Filter by STIX creator reference
        if 'created_by_ref' in query_params:
            queryset = queryset.filter(created_by_ref=query_params['created_by_ref'])
        
        # Active indicators only (not revoked and not expired)
        if query_params.get('active_only', False):
            queryset = queryset.filter(
                revoked=False
            ).filter(
                Q(valid_until__isnull=True) | Q(valid_until__gt=timezone.now())
            )
        
        # Text search across multiple fields
        if 'search' in query_params:
            search_term = query_params['search']
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(pattern__icontains=search_term) |
                Q(labels__contains=[search_term])
            )
        
        # Order results
        order_by = query_params.get('order_by', '-created')
        queryset = queryset.order_by(order_by)
        
        # Apply limit
        if 'limit' in query_params:
            queryset = queryset[:query_params['limit']]
        
        return list(queryset)
    
    def get_indicators_by_observable_type(self, observable_type: str) -> List[Indicator]:
        """Get indicators by observable type (extracted from pattern)"""
        return list(self.model_class.objects.filter(pattern__icontains=f"{observable_type}:"))
    
    def get_high_confidence_indicators(self, threshold: int = 80, threat_feed: ThreatFeed = None) -> List[Indicator]:
        """Get high confidence indicators"""
        queryset = self.model_class.objects.filter(confidence__gte=threshold)
        
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        return list(queryset)
    
    def get_recently_created_indicators(self, days: int = 7, threat_feed: ThreatFeed = None) -> List[Indicator]:
        """Get indicators created in the last N days"""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        
        queryset = self.model_class.objects.filter(created__gte=cutoff_date)
        
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        return list(queryset.order_by('-created'))
    
    def get_recently_modified_indicators(self, days: int = 7, threat_feed: ThreatFeed = None) -> List[Indicator]:
        """Get indicators modified in the last N days"""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        
        queryset = self.model_class.objects.filter(modified__gte=cutoff_date)
        
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        return list(queryset.order_by('-modified'))
    
    def get_expiring_indicators(self, days: int = 7, threat_feed: ThreatFeed = None) -> List[Indicator]:
        """Get indicators expiring in the next N days"""
        from datetime import timedelta
        cutoff_date = timezone.now() + timedelta(days=days)
        
        queryset = self.model_class.objects.filter(
            valid_until__isnull=False,
            valid_until__lte=cutoff_date,
            valid_until__gt=timezone.now()
        )
        
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        return list(queryset.order_by('valid_until'))
    
    def get_indicators_statistics(self, threat_feed: ThreatFeed = None) -> Dict[str, Any]:
        """Get indicator statistics"""
        from django.db.models import Count, Avg
        
        queryset = self.model_class.objects.all()
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        stats = queryset.aggregate(
            total_indicators=Count('id'),
            active_indicators=Count('id', filter=Q(revoked=False)),
            revoked_indicators=Count('id', filter=Q(revoked=True)),
            anonymized_indicators=Count('id', filter=Q(anonymized=True)),
            avg_confidence=Avg('confidence'),
            high_confidence_count=Count('id', filter=Q(confidence__gte=80)),
            medium_confidence_count=Count('id', filter=Q(confidence__gte=50, confidence__lt=80)),
            low_confidence_count=Count('id', filter=Q(confidence__lt=50))
        )
        
        # Get label distribution
        label_stats = {}
        for indicator in queryset:
            for label in indicator.labels:
                label_stats[label] = label_stats.get(label, 0) + 1
        
        stats['label_distribution'] = label_stats
        
        return stats
    
    def bulk_update_confidence(self, indicator_ids: List[str], new_confidence: int) -> int:
        """Bulk update confidence for multiple indicators"""
        updated_count = self.model_class.objects.filter(
            id__in=indicator_ids
        ).update(
            confidence=new_confidence,
            modified=timezone.now()
        )
        
        return updated_count
    
    def bulk_revoke_indicators(self, indicator_ids: List[str]) -> int:
        """Bulk revoke multiple indicators"""
        updated_count = self.model_class.objects.filter(
            id__in=indicator_ids
        ).update(
            revoked=True,
            modified=timezone.now()
        )
        
        return updated_count
    
    def find_similar_indicators(self, pattern: str, similarity_threshold: float = 0.8) -> List[Indicator]:
        """Find indicators with similar patterns"""
        # This is a simplified implementation
        # In practice, you might want to use more sophisticated similarity algorithms
        
        # For now, we'll do a simple pattern substring matching
        similar_indicators = []
        
        # Get all indicators for comparison
        all_indicators = self.model_class.objects.all()
        
        for indicator in all_indicators:
            # Simple similarity check - can be enhanced with proper algorithms
            if self._calculate_pattern_similarity(pattern, indicator.pattern) >= similarity_threshold:
                similar_indicators.append(indicator)
        
        return similar_indicators
    
    def _calculate_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between two patterns (simplified implementation)"""
        if not pattern1 or not pattern2:
            return 0.0
        
        # Simple Jaccard similarity based on words
        words1 = set(pattern1.lower().split())
        words2 = set(pattern2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0