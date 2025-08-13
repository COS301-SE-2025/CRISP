import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from core.models.models import Indicator
from rest_framework import serializers
from django.db import models

logger = logging.getLogger(__name__)

class IndicatorSerializer(serializers.ModelSerializer):
    """Serializer for Indicator objects"""
    
    class Meta:
        model = Indicator
        fields = [
            'id', 'type', 'value', 'description', 'confidence', 
            'first_seen', 'last_seen', 'is_anonymized', 'stix_id',
            'hash_type', 'threat_feed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'first_seen', 'last_seen', 'created_at', 'updated_at', 'stix_id', 'threat_feed']

class IndicatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Indicator operations - full CRUD with authentication
    """
    queryset = Indicator.objects.all().order_by('-first_seen')
    serializer_class = IndicatorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter indicators based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by type
        indicator_type = self.request.query_params.get('type', None)
        if indicator_type:
            queryset = queryset.filter(type=indicator_type)
        
        # Filter by confidence
        min_confidence = self.request.query_params.get('min_confidence', None)
        if min_confidence:
            try:
                queryset = queryset.filter(confidence__gte=int(min_confidence))
            except ValueError:
                pass
        
        # Filter by date range
        days = self.request.query_params.get('days', None)
        if days:
            try:
                days_ago = timezone.now() - timedelta(days=int(days))
                queryset = queryset.filter(first_seen__gte=days_ago)
            except ValueError:
                pass
        
        # Search in value and description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(value__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available indicator types"""
        types = Indicator.objects.values_list('type', flat=True).distinct()
        return Response(list(types))
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get indicator statistics"""
        total = Indicator.objects.count()
        
        # Count by type
        type_counts = {}
        for indicator_type in Indicator.objects.values_list('type', flat=True).distinct():
            type_counts[indicator_type] = Indicator.objects.filter(type=indicator_type).count()
        
        # Recent indicators (last 24 hours)
        yesterday = timezone.now() - timedelta(days=1)
        recent_count = Indicator.objects.filter(first_seen__gte=yesterday).count()
        
        # High confidence indicators
        high_confidence = Indicator.objects.filter(confidence__gte=80).count()
        
        return Response({
            'total': total,
            'types': type_counts,
            'recent_24h': recent_count,
            'high_confidence': high_confidence,
            'last_updated': timezone.now()
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent indicators"""
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        
        indicators = Indicator.objects.filter(
            first_seen__gte=since
        ).order_by('-first_seen')[:100]  # Limit to 100 for performance
        
        serializer = self.get_serializer(indicators, many=True)
        return Response({
            'count': indicators.count(),
            'days': days,
            'indicators': serializer.data
        })