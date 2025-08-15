"""
TTP Search and Filter Service

This service provides comprehensive filtering and search functionality for TTPs (Tactics, Techniques, and Procedures).
Supports filtering by tactic, technique, severity, date range, and full-text search capabilities.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from django.db.models import Q, QuerySet, Count, Case, When, Value, IntegerField
from django.db.models.functions import Lower
from django.core.paginator import Paginator, Page
from django.utils import timezone
from dataclasses import dataclass
from enum import Enum

from core.models.models import TTPData, ThreatFeed

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Enumeration for TTP severity levels"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SortOrder(Enum):
    """Enumeration for sort orders"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class FilterCriteria:
    """Data class representing TTP filter criteria"""
    # Basic filters
    tactics: Optional[List[str]] = None
    techniques: Optional[List[str]] = None
    technique_search: Optional[str] = None  # Partial technique ID search
    severity_levels: Optional[List[SeverityLevel]] = None
    
    # Date range filters
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    
    # Feed filters
    threat_feed_ids: Optional[List[int]] = None
    external_feeds_only: Optional[bool] = None
    active_feeds_only: Optional[bool] = None
    
    # Text search
    search_query: Optional[str] = None
    search_fields: Optional[List[str]] = None  # Fields to search in
    
    # Advanced filters
    has_subtechniques: Optional[bool] = None
    anonymized_only: Optional[bool] = None
    
    # Pagination and sorting
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: SortOrder = SortOrder.DESC


@dataclass
class FilterResult:
    """Data class representing filtered TTP results"""
    ttps: List[Dict[str, Any]]
    total_count: int
    filtered_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    filters_applied: Dict[str, Any]
    statistics: Dict[str, Any]


class TTPFilterService:
    """
    Service for filtering and searching TTPs with advanced capabilities
    """
    
    # Default search fields for text search
    DEFAULT_SEARCH_FIELDS = ['name', 'description', 'mitre_technique_id', 'mitre_subtechnique']
    
    # Valid sort fields
    VALID_SORT_FIELDS = [
        'id', 'name', 'mitre_technique_id', 'mitre_tactic', 'created_at', 
        'updated_at', 'threat_feed__name', 'severity_score'
    ]
    
    # Severity mapping for techniques (this could be moved to database later)
    TECHNIQUE_SEVERITY_MAP = {
        # Critical techniques
        'T1566': SeverityLevel.CRITICAL,  # Phishing
        'T1190': SeverityLevel.CRITICAL,  # Exploit Public-Facing Application
        'T1078': SeverityLevel.CRITICAL,  # Valid Accounts
        'T1055': SeverityLevel.CRITICAL,  # Process Injection
        
        # High severity techniques
        'T1003': SeverityLevel.HIGH,      # OS Credential Dumping
        'T1021': SeverityLevel.HIGH,      # Remote Services
        'T1068': SeverityLevel.HIGH,      # Exploitation for Privilege Escalation
        'T1210': SeverityLevel.HIGH,      # Exploitation of Remote Services
        'T1574': SeverityLevel.HIGH,      # Hijack Execution Flow
        
        # Medium severity (most techniques)
        'T1082': SeverityLevel.MEDIUM,    # System Information Discovery
        'T1083': SeverityLevel.MEDIUM,    # File and Directory Discovery
        'T1057': SeverityLevel.MEDIUM,    # Process Discovery
        'T1018': SeverityLevel.MEDIUM,    # Remote System Discovery
        
        # Low severity
        'T1124': SeverityLevel.LOW,       # System Time Discovery
        'T1614': SeverityLevel.LOW,       # System Language Discovery
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def filter_ttps(self, criteria: FilterCriteria) -> FilterResult:
        """
        Filter TTPs based on provided criteria
        
        Args:
            criteria: FilterCriteria object with filter parameters
            
        Returns:
            FilterResult object with filtered results and metadata
        """
        try:
            # Start with base queryset
            queryset = self._build_base_queryset()
            
            # Get total count before filtering
            total_count = queryset.count()
            
            # Apply filters
            queryset = self._apply_filters(queryset, criteria)
            
            # Get filtered count
            filtered_count = queryset.count()
            
            # Apply sorting
            queryset = self._apply_sorting(queryset, criteria)
            
            # Apply pagination
            paginator = Paginator(queryset, criteria.page_size)
            
            # Validate page number
            page = max(1, min(criteria.page, paginator.num_pages if paginator.num_pages > 0 else 1))
            page_obj = paginator.get_page(page)
            
            # Serialize results
            ttps_data = self._serialize_ttps(page_obj.object_list)
            
            # Calculate statistics
            statistics = self._calculate_statistics(queryset, criteria)
            
            return FilterResult(
                ttps=ttps_data,
                total_count=total_count,
                filtered_count=filtered_count,
                page=page,
                page_size=criteria.page_size,
                total_pages=paginator.num_pages,
                has_next=page_obj.has_next(),
                has_previous=page_obj.has_previous(),
                filters_applied=self._get_applied_filters(criteria),
                statistics=statistics
            )
            
        except Exception as e:
            self.logger.error(f"Error filtering TTPs: {e}")
            return FilterResult(
                ttps=[],
                total_count=0,
                filtered_count=0,
                page=1,
                page_size=criteria.page_size,
                total_pages=0,
                has_next=False,
                has_previous=False,
                filters_applied={},
                statistics={}
            )
    
    def _build_base_queryset(self) -> QuerySet:
        """Build the base queryset with optimizations"""
        return TTPData.objects.select_related('threat_feed').annotate(
            # Add computed severity score for sorting
            severity_score=Case(
                When(mitre_technique_id__startswith='T1566', then=Value(4)),  # Critical
                When(mitre_technique_id__startswith='T1190', then=Value(4)),
                When(mitre_technique_id__startswith='T1078', then=Value(4)),
                When(mitre_technique_id__startswith='T1055', then=Value(4)),
                When(mitre_technique_id__startswith='T1003', then=Value(3)),  # High
                When(mitre_technique_id__startswith='T1021', then=Value(3)),
                When(mitre_technique_id__startswith='T1068', then=Value(3)),
                When(mitre_technique_id__startswith='T1210', then=Value(3)),
                When(mitre_technique_id__startswith='T1574', then=Value(3)),
                When(mitre_technique_id__startswith='T1124', then=Value(1)),  # Low
                When(mitre_technique_id__startswith='T1614', then=Value(1)),
                default=Value(2),  # Medium
                output_field=IntegerField()
            )
        )
    
    def _apply_filters(self, queryset: QuerySet, criteria: FilterCriteria) -> QuerySet:
        """Apply all filters to the queryset"""
        
        # Filter by tactics
        if criteria.tactics:
            queryset = queryset.filter(mitre_tactic__in=criteria.tactics)
        
        # Filter by techniques (exact matches)
        if criteria.techniques:
            queryset = queryset.filter(mitre_technique_id__in=criteria.techniques)
        
        # Filter by technique search (partial matches)
        if criteria.technique_search:
            queryset = queryset.filter(
                mitre_technique_id__icontains=criteria.technique_search
            )
        
        # Filter by severity levels
        if criteria.severity_levels:
            severity_conditions = Q()
            for severity in criteria.severity_levels:
                severity_conditions |= self._build_severity_condition(severity)
            queryset = queryset.filter(severity_conditions)
        
        # Filter by date ranges
        if criteria.date_from:
            queryset = queryset.filter(created_at__gte=criteria.date_from)
        
        if criteria.date_to:
            queryset = queryset.filter(created_at__lte=criteria.date_to)
        
        if criteria.created_after:
            queryset = queryset.filter(created_at__gte=criteria.created_after)
        
        if criteria.created_before:
            queryset = queryset.filter(created_at__lte=criteria.created_before)
        
        if criteria.updated_after:
            queryset = queryset.filter(updated_at__gte=criteria.updated_after)
        
        if criteria.updated_before:
            queryset = queryset.filter(updated_at__lte=criteria.updated_before)
        
        # Filter by threat feeds
        if criteria.threat_feed_ids:
            queryset = queryset.filter(threat_feed_id__in=criteria.threat_feed_ids)
        
        if criteria.external_feeds_only is not None:
            queryset = queryset.filter(threat_feed__is_external=criteria.external_feeds_only)
        
        if criteria.active_feeds_only is not None:
            queryset = queryset.filter(threat_feed__is_active=criteria.active_feeds_only)
        
        # Text search across multiple fields
        if criteria.search_query:
            search_fields = criteria.search_fields or self.DEFAULT_SEARCH_FIELDS
            search_conditions = Q()
            
            for field in search_fields:
                if field == 'name':
                    search_conditions |= Q(name__icontains=criteria.search_query)
                elif field == 'description':
                    search_conditions |= Q(description__icontains=criteria.search_query)
                elif field == 'mitre_technique_id':
                    search_conditions |= Q(mitre_technique_id__icontains=criteria.search_query)
                elif field == 'mitre_subtechnique':
                    search_conditions |= Q(mitre_subtechnique__icontains=criteria.search_query)
                elif field == 'threat_feed':
                    search_conditions |= Q(threat_feed__name__icontains=criteria.search_query)
            
            queryset = queryset.filter(search_conditions)
        
        # Advanced filters
        if criteria.has_subtechniques is not None:
            if criteria.has_subtechniques:
                queryset = queryset.exclude(mitre_subtechnique__isnull=True).exclude(mitre_subtechnique='')
            else:
                queryset = queryset.filter(Q(mitre_subtechnique__isnull=True) | Q(mitre_subtechnique=''))
        
        if criteria.anonymized_only is not None:
            queryset = queryset.filter(is_anonymized=criteria.anonymized_only)
        
        return queryset
    
    def _build_severity_condition(self, severity: SeverityLevel) -> Q:
        """Build Q object for severity filtering"""
        conditions = Q()
        
        # Map severity levels to technique patterns
        if severity == SeverityLevel.CRITICAL:
            conditions |= Q(mitre_technique_id__startswith='T1566')  # Phishing
            conditions |= Q(mitre_technique_id__startswith='T1190')  # Exploit Public-Facing Application
            conditions |= Q(mitre_technique_id__startswith='T1078')  # Valid Accounts
            conditions |= Q(mitre_technique_id__startswith='T1055')  # Process Injection
        
        elif severity == SeverityLevel.HIGH:
            conditions |= Q(mitre_technique_id__startswith='T1003')  # OS Credential Dumping
            conditions |= Q(mitre_technique_id__startswith='T1021')  # Remote Services
            conditions |= Q(mitre_technique_id__startswith='T1068')  # Exploitation for Privilege Escalation
            conditions |= Q(mitre_technique_id__startswith='T1210')  # Exploitation of Remote Services
            conditions |= Q(mitre_technique_id__startswith='T1574')  # Hijack Execution Flow
        
        elif severity == SeverityLevel.LOW:
            conditions |= Q(mitre_technique_id__startswith='T1124')  # System Time Discovery
            conditions |= Q(mitre_technique_id__startswith='T1614')  # System Language Discovery
        
        elif severity == SeverityLevel.MEDIUM:
            # Medium severity includes many common techniques
            medium_techniques = ['T1082', 'T1083', 'T1057', 'T1018', 'T1016', 'T1033', 'T1087']
            for technique in medium_techniques:
                conditions |= Q(mitre_technique_id__startswith=technique)
        
        # If no specific patterns match, include by name/description keywords
        if severity == SeverityLevel.CRITICAL:
            conditions |= Q(description__icontains='critical')
            conditions |= Q(description__icontains='exploit')
            conditions |= Q(description__icontains='privilege escalation')
        
        return conditions
    
    def _apply_sorting(self, queryset: QuerySet, criteria: FilterCriteria) -> QuerySet:
        """Apply sorting to the queryset"""
        if criteria.sort_by not in self.VALID_SORT_FIELDS:
            criteria.sort_by = 'created_at'
        
        order_prefix = '-' if criteria.sort_order == SortOrder.DESC else ''
        order_field = f"{order_prefix}{criteria.sort_by}"
        
        return queryset.order_by(order_field)
    
    def _serialize_ttps(self, ttps: QuerySet) -> List[Dict[str, Any]]:
        """Serialize TTP objects to dictionaries"""
        serialized_ttps = []
        
        for ttp in ttps:
            # Determine severity based on technique
            severity = self._get_technique_severity(ttp.mitre_technique_id)
            
            # Get tactic display name - try to get from model choices
            tactic_display = ttp.mitre_tactic
            if hasattr(TTPData, 'MITRE_TACTIC_CHOICES'):
                tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(
                    ttp.mitre_tactic, ttp.mitre_tactic
                ) if ttp.mitre_tactic else None
            
            serialized_ttps.append({
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description,
                'mitre_technique_id': ttp.mitre_technique_id,
                'mitre_tactic': ttp.mitre_tactic,
                'mitre_tactic_display': tactic_display,
                'mitre_subtechnique': getattr(ttp, 'mitre_subtechnique', ''),
                'stix_id': ttp.stix_id,
                'is_anonymized': getattr(ttp, 'is_anonymized', False),
                'created_at': ttp.created_at.isoformat() if ttp.created_at else None,
                'updated_at': ttp.updated_at.isoformat() if ttp.updated_at else None,
                'threat_feed': {
                    'id': ttp.threat_feed.id,
                    'name': ttp.threat_feed.name,
                    'is_external': getattr(ttp.threat_feed, 'is_external', False),
                    'is_active': getattr(ttp.threat_feed, 'is_active', True)
                } if ttp.threat_feed else None,
                'severity': severity.value,
                'severity_score': getattr(ttp, 'severity_score', 2),
                'has_subtechnique': bool(getattr(ttp, 'mitre_subtechnique', '') and getattr(ttp, 'mitre_subtechnique', '').strip())
            })
        
        return serialized_ttps
    
    def _get_technique_severity(self, technique_id: str) -> SeverityLevel:
        """Determine severity level for a technique ID"""
        if not technique_id:
            return SeverityLevel.MEDIUM
        
        # Check for exact matches first
        for tech_pattern, severity in self.TECHNIQUE_SEVERITY_MAP.items():
            if technique_id.startswith(tech_pattern):
                return severity
        
        # Default to medium severity
        return SeverityLevel.MEDIUM
    
    def _calculate_statistics(self, queryset: QuerySet, criteria: FilterCriteria) -> Dict[str, Any]:
        """Calculate statistics for the filtered results"""
        try:
            # Tactic distribution
            tactic_stats = queryset.values('mitre_tactic').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Technique distribution (top 10)
            technique_stats = queryset.values('mitre_technique_id').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            # Severity distribution
            severity_stats = {}
            for severity in SeverityLevel:
                count = queryset.filter(
                    self._build_severity_condition(severity)
                ).count()
                severity_stats[severity.value] = count
            
            # Feed distribution
            feed_stats = queryset.values(
                'threat_feed__id', 'threat_feed__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            # Time-based statistics
            now = timezone.now()
            recent_stats = {
                'last_24h': queryset.filter(created_at__gte=now - timedelta(hours=24)).count(),
                'last_week': queryset.filter(created_at__gte=now - timedelta(days=7)).count(),
                'last_month': queryset.filter(created_at__gte=now - timedelta(days=30)).count()
            }
            
            return {
                'tactic_distribution': list(tactic_stats),
                'top_techniques': list(technique_stats),
                'severity_distribution': severity_stats,
                'feed_distribution': list(feed_stats),
                'recent_activity': recent_stats,
                'has_subtechniques_count': queryset.exclude(
                    Q(mitre_subtechnique__isnull=True) | Q(mitre_subtechnique='')
                ).count(),
                'anonymized_count': queryset.filter(is_anonymized=True).count() if queryset.filter(is_anonymized=True).exists() else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def _get_applied_filters(self, criteria: FilterCriteria) -> Dict[str, Any]:
        """Get a summary of applied filters"""
        applied = {}
        
        if criteria.tactics:
            applied['tactics'] = criteria.tactics
        if criteria.techniques:
            applied['techniques'] = criteria.techniques
        if criteria.technique_search:
            applied['technique_search'] = criteria.technique_search
        if criteria.severity_levels:
            applied['severity_levels'] = [s.value for s in criteria.severity_levels]
        if criteria.date_from:
            applied['date_from'] = criteria.date_from.isoformat()
        if criteria.date_to:
            applied['date_to'] = criteria.date_to.isoformat()
        if criteria.threat_feed_ids:
            applied['threat_feed_ids'] = criteria.threat_feed_ids
        if criteria.search_query:
            applied['search_query'] = criteria.search_query
        if criteria.external_feeds_only is not None:
            applied['external_feeds_only'] = criteria.external_feeds_only
        if criteria.active_feeds_only is not None:
            applied['active_feeds_only'] = criteria.active_feeds_only
        if criteria.has_subtechniques is not None:
            applied['has_subtechniques'] = criteria.has_subtechniques
        if criteria.anonymized_only is not None:
            applied['anonymized_only'] = criteria.anonymized_only
        
        applied['sort_by'] = criteria.sort_by
        applied['sort_order'] = criteria.sort_order.value
        
        return applied
    
    def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options for UI components"""
        try:
            # Get all available tactics
            tactics = list(TTPData.objects.values_list(
                'mitre_tactic', flat=True
            ).distinct().exclude(
                mitre_tactic__isnull=True
            ).exclude(mitre_tactic=''))
            
            tactic_choices = []
            for tactic in tactics:
                # Try to get display name from choices if available
                display_name = tactic
                if hasattr(TTPData, 'MITRE_TACTIC_CHOICES'):
                    display_name = dict(TTPData.MITRE_TACTIC_CHOICES).get(tactic, tactic)
                
                tactic_choices.append({
                    'value': tactic,
                    'label': display_name,
                    'count': TTPData.objects.filter(mitre_tactic=tactic).count()
                })
            
            # Get top techniques
            top_techniques = list(TTPData.objects.values(
                'mitre_technique_id'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:50])
            
            # Get available threat feeds
            threat_feeds = list(ThreatFeed.objects.values(
                'id', 'name'
            ).annotate(
                ttp_count=Count('ttps')
            ).filter(ttp_count__gt=0).order_by('name'))
            
            # Severity levels
            severity_levels = [
                {'value': level.value, 'label': level.value.title()}
                for level in SeverityLevel
            ]
            
            return {
                'tactics': sorted(tactic_choices, key=lambda x: x['label']),
                'top_techniques': top_techniques,
                'threat_feeds': threat_feeds,
                'severity_levels': severity_levels,
                'sort_fields': [
                    {'value': field, 'label': field.replace('_', ' ').title()}
                    for field in self.VALID_SORT_FIELDS
                ],
                'search_fields': [
                    {'value': field, 'label': field.replace('_', ' ').title()}
                    for field in self.DEFAULT_SEARCH_FIELDS
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting filter options: {e}")
            return {}
    
    def build_criteria_from_request(self, request) -> FilterCriteria:
        """Build FilterCriteria from Django request parameters"""
        try:
            # Parse basic parameters
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)
            
            # Parse filter parameters
            tactics = self._parse_list_param(request.GET.get('tactics'))
            techniques = self._parse_list_param(request.GET.get('techniques'))
            technique_search = request.GET.get('technique_search', '').strip()
            
            # Parse severity levels
            severity_param = request.GET.get('severity_levels')
            severity_levels = None
            if severity_param:
                try:
                    severity_values = self._parse_list_param(severity_param)
                    severity_levels = [
                        SeverityLevel(s) for s in severity_values 
                        if s in [level.value for level in SeverityLevel]
                    ]
                except ValueError:
                    severity_levels = None
            
            # Parse date parameters
            date_from = self._parse_datetime(request.GET.get('date_from'))
            date_to = self._parse_datetime(request.GET.get('date_to'))
            created_after = self._parse_datetime(request.GET.get('created_after'))
            created_before = self._parse_datetime(request.GET.get('created_before'))
            
            # Parse feed parameters
            threat_feed_ids = self._parse_int_list(request.GET.get('threat_feed_ids'))
            external_feeds_only = self._parse_bool(request.GET.get('external_feeds_only'))
            active_feeds_only = self._parse_bool(request.GET.get('active_feeds_only'))
            
            # Parse search parameters
            search_query = request.GET.get('search', '').strip()
            search_fields = self._parse_list_param(request.GET.get('search_fields'))
            
            # Parse advanced parameters
            has_subtechniques = self._parse_bool(request.GET.get('has_subtechniques'))
            anonymized_only = self._parse_bool(request.GET.get('anonymized_only'))
            
            # Parse sorting parameters
            sort_by = request.GET.get('sort_by', 'created_at')
            sort_order_str = request.GET.get('sort_order', 'desc').lower()
            sort_order = SortOrder.DESC if sort_order_str == 'desc' else SortOrder.ASC
            
            return FilterCriteria(
                tactics=tactics,
                techniques=techniques,
                technique_search=technique_search,
                severity_levels=severity_levels,
                date_from=date_from,
                date_to=date_to,
                created_after=created_after,
                created_before=created_before,
                threat_feed_ids=threat_feed_ids,
                external_feeds_only=external_feeds_only,
                active_feeds_only=active_feeds_only,
                search_query=search_query,
                search_fields=search_fields,
                has_subtechniques=has_subtechniques,
                anonymized_only=anonymized_only,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
        except Exception as e:
            self.logger.error(f"Error building criteria from request: {e}")
            return FilterCriteria()  # Return default criteria
    
    def _parse_list_param(self, param: str) -> Optional[List[str]]:
        """Parse comma-separated list parameter"""
        if not param:
            return None
        return [item.strip() for item in param.split(',') if item.strip()]
    
    def _parse_int_list(self, param: str) -> Optional[List[int]]:
        """Parse comma-separated integer list parameter"""
        if not param:
            return None
        try:
            return [int(item.strip()) for item in param.split(',') if item.strip()]
        except ValueError:
            return None
    
    def _parse_bool(self, param: str) -> Optional[bool]:
        """Parse boolean parameter"""
        if not param:
            return None
        return param.lower() in ('true', '1', 'yes', 'on')
    
    def _parse_datetime(self, param: str) -> Optional[datetime]:
        """Parse datetime parameter (ISO format)"""
        if not param:
            return None
        try:
            from dateutil import parser
            return parser.isoparse(param)
        except:
            try:
                return datetime.fromisoformat(param.replace('Z', '+00:00'))
            except:
                return None