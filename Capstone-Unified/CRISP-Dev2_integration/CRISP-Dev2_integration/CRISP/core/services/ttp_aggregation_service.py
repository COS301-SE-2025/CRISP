"""
TTP Aggregation Service

This service provides business logic for calculating technique frequencies, trends,
and statistical analysis of TTPs across different dimensions (time, threat feeds, tactics).
"""

import logging
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
from django.utils import timezone
from django.db.models import Count, Q, Avg, Min, Max, Sum
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.core.cache import cache
from core.models.models import TTPData, ThreatFeed
import statistics
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TrendPoint:
    """Data class representing a single point in a trend analysis"""
    date: str
    value: int
    percentage_change: Optional[float] = None
    moving_average: Optional[float] = None


@dataclass
class FrequencyStats:
    """Data class for frequency statistics"""
    count: int
    percentage: float
    rank: int
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


@dataclass
class TrendAnalysis:
    """Data class for trend analysis results"""
    direction: str  # 'increasing', 'decreasing', 'stable', 'volatile'
    strength: float  # 0-1 scale
    confidence: float  # 0-1 scale
    slope: float
    r_squared: float
    volatility: float


class TTPAggregationService:
    """
    Service for aggregating TTP data and calculating frequencies, trends, and patterns
    """
    
    CACHE_PREFIX = "ttp_aggregation"
    DEFAULT_CACHE_TIMEOUT = 3600  # 1 hour
    
    def __init__(self, cache_timeout: int = None):
        self.cache_timeout = cache_timeout or self.DEFAULT_CACHE_TIMEOUT
    
    def get_technique_frequencies(self, 
                                days: int = 30,
                                threat_feed_id: Optional[int] = None,
                                include_subtechniques: bool = True,
                                min_occurrences: int = 1) -> Dict[str, FrequencyStats]:
        """
        Calculate frequency statistics for MITRE techniques
        
        Args:
            days: Number of days to look back
            threat_feed_id: Optional filter by specific threat feed
            include_subtechniques: Whether to include sub-techniques in counts
            min_occurrences: Minimum occurrences to include in results
            
        Returns:
            Dictionary mapping technique IDs to frequency statistics
        """
        cache_key = f"{self.CACHE_PREFIX}_technique_freq_{days}_{threat_feed_id}_{include_subtechniques}_{min_occurrences}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Build base queryset
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            queryset = TTPData.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                mitre_technique_id__isnull=False
            ).exclude(mitre_technique_id='')
            
            if threat_feed_id:
                queryset = queryset.filter(threat_feed_id=threat_feed_id)
            
            # Group techniques, optionally including subtechniques
            if include_subtechniques:
                # Count exact technique IDs (including subtechniques)
                technique_counts = queryset.values('mitre_technique_id').annotate(
                    count=Count('id'),
                    first_seen=Min('created_at'),
                    last_seen=Max('created_at')
                ).order_by('-count')
            else:
                # Count base techniques only (strip subtechnique suffix)
                from django.db.models import Case, When, Value, CharField
                from django.db.models.functions import Substr, Length, StrIndex
                
                queryset = queryset.extra(
                    select={
                        'base_technique': "CASE WHEN mitre_technique_id LIKE '%.%' THEN SUBSTRING(mitre_technique_id, 1, POSITION('.' IN mitre_technique_id) - 1) ELSE mitre_technique_id END"
                    }
                )
                
                technique_counts = queryset.values('base_technique').annotate(
                    count=Count('id'),
                    first_seen=Min('created_at'),
                    last_seen=Max('created_at')
                ).order_by('-count')
            
            # Filter by minimum occurrences
            technique_counts = technique_counts.filter(count__gte=min_occurrences)
            
            # Calculate total for percentages
            total_count = sum(item['count'] for item in technique_counts)
            
            # Build frequency statistics
            frequencies = {}
            for rank, item in enumerate(technique_counts, 1):
                technique_id = item.get('base_technique') if not include_subtechniques else item['mitre_technique_id']
                
                frequencies[technique_id] = FrequencyStats(
                    count=item['count'],
                    percentage=round((item['count'] / total_count) * 100, 2) if total_count > 0 else 0,
                    rank=rank,
                    first_seen=item['first_seen'],
                    last_seen=item['last_seen']
                )
            
            # Cache the result
            cache.set(cache_key, frequencies, self.cache_timeout)
            return frequencies
            
        except Exception as e:
            logger.error(f"Error calculating technique frequencies: {e}")
            return {}
    
    def get_tactic_frequencies(self,
                             days: int = 30,
                             threat_feed_id: Optional[int] = None,
                             min_occurrences: int = 1) -> Dict[str, FrequencyStats]:
        """
        Calculate frequency statistics for MITRE tactics
        
        Args:
            days: Number of days to look back
            threat_feed_id: Optional filter by specific threat feed
            min_occurrences: Minimum occurrences to include in results
            
        Returns:
            Dictionary mapping tactic IDs to frequency statistics
        """
        cache_key = f"{self.CACHE_PREFIX}_tactic_freq_{days}_{threat_feed_id}_{min_occurrences}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Build base queryset
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            queryset = TTPData.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                mitre_tactic__isnull=False
            ).exclude(mitre_tactic='')
            
            if threat_feed_id:
                queryset = queryset.filter(threat_feed_id=threat_feed_id)
            
            # Count tactics
            tactic_counts = queryset.values('mitre_tactic').annotate(
                count=Count('id'),
                first_seen=Min('created_at'),
                last_seen=Max('created_at')
            ).filter(count__gte=min_occurrences).order_by('-count')
            
            # Calculate total for percentages
            total_count = sum(item['count'] for item in tactic_counts)
            
            # Build frequency statistics
            frequencies = {}
            for rank, item in enumerate(tactic_counts, 1):
                frequencies[item['mitre_tactic']] = FrequencyStats(
                    count=item['count'],
                    percentage=round((item['count'] / total_count) * 100, 2) if total_count > 0 else 0,
                    rank=rank,
                    first_seen=item['first_seen'],
                    last_seen=item['last_seen']
                )
            
            # Cache the result
            cache.set(cache_key, frequencies, self.cache_timeout)
            return frequencies
            
        except Exception as e:
            logger.error(f"Error calculating tactic frequencies: {e}")
            return {}
    
    def get_technique_trends(self,
                           technique_id: str,
                           days: int = 90,
                           granularity: str = 'day',
                           threat_feed_id: Optional[int] = None,
                           moving_average_window: int = 7) -> List[TrendPoint]:
        """
        Calculate time-based trends for a specific technique
        
        Args:
            technique_id: MITRE technique ID
            days: Number of days to analyze
            granularity: Time granularity ('day', 'week', 'month')
            threat_feed_id: Optional filter by specific threat feed
            moving_average_window: Window size for moving average calculation
            
        Returns:
            List of trend points over time
        """
        cache_key = f"{self.CACHE_PREFIX}_technique_trends_{technique_id}_{days}_{granularity}_{threat_feed_id}_{moving_average_window}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return [TrendPoint(**point) for point in cached_result]
        
        try:
            # Build base queryset
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            queryset = TTPData.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                mitre_technique_id=technique_id
            )
            
            if threat_feed_id:
                queryset = queryset.filter(threat_feed_id=threat_feed_id)
            
            # Choose truncation function based on granularity
            truncate_func = {
                'day': TruncDate,
                'week': TruncWeek,
                'month': TruncMonth,
                'year': TruncYear
            }.get(granularity, TruncDate)
            
            # Group by time periods
            time_counts = queryset.annotate(
                period=truncate_func('created_at')
            ).values('period').annotate(
                count=Count('id')
            ).order_by('period')
            
            # Convert to time series
            time_series = {}
            for item in time_counts:
                date_str = item['period'].strftime('%Y-%m-%d')
                time_series[date_str] = item['count']
            
            # Generate complete date range with zero values
            trend_points = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                date_str = current_date.strftime('%Y-%m-%d')
                count = time_series.get(date_str, 0)
                
                trend_points.append(TrendPoint(
                    date=date_str,
                    value=count
                ))
                
                # Move to next period
                if granularity == 'day':
                    current_date += timedelta(days=1)
                elif granularity == 'week':
                    current_date += timedelta(weeks=1)
                elif granularity == 'month':
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                else:  # year
                    current_date = current_date.replace(year=current_date.year + 1)
            
            # Calculate percentage changes and moving averages
            self._calculate_trend_metrics(trend_points, moving_average_window)
            
            # Cache the result (convert to dict for serialization)
            cache_data = [
                {
                    'date': point.date,
                    'value': point.value,
                    'percentage_change': point.percentage_change,
                    'moving_average': point.moving_average
                }
                for point in trend_points
            ]
            cache.set(cache_key, cache_data, self.cache_timeout)
            
            return trend_points
            
        except Exception as e:
            logger.error(f"Error calculating technique trends: {e}")
            return []
    
    def _calculate_trend_metrics(self, trend_points: List[TrendPoint], window_size: int):
        """Calculate percentage changes and moving averages for trend points"""
        values = [point.value for point in trend_points]
        
        # Calculate percentage changes
        for i in range(1, len(trend_points)):
            prev_value = trend_points[i-1].value
            if prev_value > 0:
                change = ((trend_points[i].value - prev_value) / prev_value) * 100
                trend_points[i].percentage_change = round(change, 2)
        
        # Calculate moving averages
        for i in range(len(trend_points)):
            start_idx = max(0, i - window_size + 1)
            window_values = values[start_idx:i+1]
            if window_values:
                trend_points[i].moving_average = round(sum(window_values) / len(window_values), 2)
    
    def analyze_trend_direction(self, trend_points: List[TrendPoint]) -> TrendAnalysis:
        """
        Analyze the overall direction and characteristics of a trend
        
        Args:
            trend_points: List of trend points to analyze
            
        Returns:
            TrendAnalysis object with direction, strength, and confidence metrics
        """
        if len(trend_points) < 3:
            return TrendAnalysis(
                direction='insufficient_data',
                strength=0.0,
                confidence=0.0,
                slope=0.0,
                r_squared=0.0,
                volatility=0.0
            )
        
        try:
            values = [point.value for point in trend_points]
            x_values = list(range(len(values)))
            
            # Calculate linear regression
            if len(values) > 1:
                slope, r_squared = self._calculate_linear_regression(x_values, values)
            else:
                slope, r_squared = 0.0, 0.0
            
            # Determine trend direction
            if abs(slope) < 0.1:
                direction = 'stable'
            elif slope > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            # Calculate trend strength (based on slope magnitude and R²)
            strength = min(abs(slope) * r_squared, 1.0)
            
            # Calculate confidence (based on R² and data points)
            confidence = r_squared * min(len(values) / 30, 1.0)  # More data points = higher confidence
            
            # Calculate volatility (coefficient of variation)
            mean_val = statistics.mean(values) if values else 0
            if mean_val > 0:
                std_val = statistics.stdev(values) if len(values) > 1 else 0
                volatility = std_val / mean_val
            else:
                volatility = 0.0
            
            # Adjust direction for high volatility
            if volatility > 1.0:
                direction = 'volatile'
            
            return TrendAnalysis(
                direction=direction,
                strength=round(strength, 3),
                confidence=round(confidence, 3),
                slope=round(slope, 4),
                r_squared=round(r_squared, 3),
                volatility=round(volatility, 3)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing trend direction: {e}")
            return TrendAnalysis(
                direction='error',
                strength=0.0,
                confidence=0.0,
                slope=0.0,
                r_squared=0.0,
                volatility=0.0
            )
    
    def _calculate_linear_regression(self, x_values: List[int], y_values: List[int]) -> Tuple[float, float]:
        """Calculate linear regression slope and R-squared"""
        try:
            n = len(x_values)
            if n < 2:
                return 0.0, 0.0
            
            # Calculate means
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            # Calculate slope
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                return 0.0, 0.0
            
            slope = numerator / denominator
            
            # Calculate R-squared
            y_pred = [slope * (x - x_mean) + y_mean for x in x_values]
            ss_res = sum((y_values[i] - y_pred[i]) ** 2 for i in range(n))
            ss_tot = sum((y_values[i] - y_mean) ** 2 for i in range(n))
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
            
            return slope, max(0.0, r_squared)  # Ensure R² is non-negative
            
        except Exception as e:
            logger.error(f"Error in linear regression calculation: {e}")
            return 0.0, 0.0
    
    def get_feed_comparison_stats(self,
                                days: int = 30,
                                top_n: int = 10) -> Dict[str, Any]:
        """
        Compare TTP statistics across different threat feeds
        
        Args:
            days: Number of days to analyze
            top_n: Number of top feeds to include
            
        Returns:
            Dictionary with comparative statistics
        """
        cache_key = f"{self.CACHE_PREFIX}_feed_comparison_{days}_{top_n}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Get TTP counts by feed
            feed_stats = TTPData.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).values(
                'threat_feed__id',
                'threat_feed__name',
                'threat_feed__is_external'
            ).annotate(
                ttp_count=Count('id'),
                unique_techniques=Count('mitre_technique_id', distinct=True),
                unique_tactics=Count('mitre_tactic', distinct=True),
                avg_techniques_per_day=Avg('id')  # This will be recalculated properly
            ).order_by('-ttp_count')[:top_n]
            
            # Recalculate daily averages properly
            for feed_stat in feed_stats:
                feed_id = feed_stat['threat_feed__id']
                daily_counts = TTPData.objects.filter(
                    threat_feed_id=feed_id,
                    created_at__gte=start_date,
                    created_at__lte=end_date
                ).extra(
                    select={'day': 'DATE(created_at)'}
                ).values('day').annotate(
                    count=Count('id')
                ).values_list('count', flat=True)
                
                feed_stat['avg_techniques_per_day'] = round(
                    sum(daily_counts) / max(len(daily_counts), 1), 2
                ) if daily_counts else 0
            
            # Calculate top techniques across all feeds
            top_techniques = TTPData.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                mitre_technique_id__isnull=False
            ).exclude(
                mitre_technique_id=''
            ).values('mitre_technique_id').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            # Calculate top tactics
            top_tactics = TTPData.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                mitre_tactic__isnull=False
            ).exclude(
                mitre_tactic=''
            ).values('mitre_tactic').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            result = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'feed_statistics': list(feed_stats),
                'top_techniques': list(top_techniques),
                'top_tactics': list(top_tactics),
                'summary': {
                    'total_feeds_analyzed': len(feed_stats),
                    'total_ttps_in_period': sum(feed['ttp_count'] for feed in feed_stats),
                    'most_active_feed': feed_stats[0]['threat_feed__name'] if feed_stats else None,
                    'most_common_technique': top_techniques[0]['mitre_technique_id'] if top_techniques else None,
                    'most_common_tactic': top_tactics[0]['mitre_tactic'] if top_tactics else None
                }
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_timeout)
            return result
            
        except Exception as e:
            logger.error(f"Error calculating feed comparison stats: {e}")
            return {}
    
    def get_seasonal_patterns(self,
                            technique_id: Optional[str] = None,
                            days: int = 365,
                            granularity: str = 'week') -> Dict[str, Any]:
        """
        Analyze seasonal patterns in TTP occurrence
        
        Args:
            technique_id: Optional specific technique to analyze
            days: Number of days to analyze (minimum 90)
            granularity: Time granularity ('week', 'month')
            
        Returns:
            Dictionary with seasonal pattern analysis
        """
        days = max(days, 90)  # Minimum period for seasonal analysis
        cache_key = f"{self.CACHE_PREFIX}_seasonal_{technique_id}_{days}_{granularity}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Build base queryset
            queryset = TTPData.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            
            if technique_id:
                queryset = queryset.filter(mitre_technique_id=technique_id)
            
            # Group by time periods
            if granularity == 'week':
                time_data = queryset.extra(
                    select={'period': 'EXTRACT(week FROM created_at)'}
                ).values('period').annotate(
                    count=Count('id'),
                    avg_count=Avg('id')
                ).order_by('period')
                period_label = 'Week of Year'
            else:  # month
                time_data = queryset.extra(
                    select={'period': 'EXTRACT(month FROM created_at)'}
                ).values('period').annotate(
                    count=Count('id'),
                    avg_count=Avg('id')
                ).order_by('period')
                period_label = 'Month of Year'
            
            # Calculate seasonal statistics
            periods = list(time_data)
            if not periods:
                return {
                    'seasonal_patterns': [],
                    'peak_period': None,
                    'low_period': None,
                    'seasonality_strength': 0,
                    'total_occurrences': 0,
                    'analysis_period': f"{days} days",
                    'granularity': granularity,
                    'period_label': period_label,
                    'message': 'No data available for the specified period'
                }
            
            counts = [p['count'] for p in periods]
            mean_count = statistics.mean(counts)
            std_count = statistics.stdev(counts) if len(counts) > 1 else 0
            
            # Identify peaks and valleys
            peak_period = max(periods, key=lambda x: x['count'])
            valley_period = min(periods, key=lambda x: x['count'])
            
            # Calculate seasonality strength (coefficient of variation)
            seasonality_strength = (std_count / mean_count) if mean_count > 0 else 0
            
            result = {
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days,
                    'granularity': granularity
                },
                'technique_id': technique_id,
                'period_data': periods,
                'statistics': {
                    'mean_count': round(mean_count, 2),
                    'std_deviation': round(std_count, 2),
                    'seasonality_strength': round(seasonality_strength, 3),
                    'peak_period': {
                        'period': int(peak_period['period']),
                        'count': peak_period['count'],
                        'label': f"{period_label} {int(peak_period['period'])}"
                    },
                    'valley_period': {
                        'period': int(valley_period['period']),
                        'count': valley_period['count'],
                        'label': f"{period_label} {int(valley_period['period'])}"
                    }
                },
                'interpretation': self._interpret_seasonality(seasonality_strength)
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_timeout)
            return result
            
        except Exception as e:
            logger.error(f"Error calculating seasonal patterns: {e}")
            return {'error': f'Failed to calculate seasonal patterns: {str(e)}'}
    
    def _interpret_seasonality(self, strength: float) -> str:
        """Interpret seasonality strength score"""
        if strength < 0.2:
            return "Very low seasonality - consistent activity throughout the period"
        elif strength < 0.5:
            return "Low seasonality - some variation but generally consistent"
        elif strength < 1.0:
            return "Moderate seasonality - noticeable seasonal patterns"
        elif strength < 2.0:
            return "High seasonality - strong seasonal patterns with clear peaks and valleys"
        else:
            return "Very high seasonality - extreme seasonal variation with significant peaks and valleys"
    
    def clear_cache(self, pattern: Optional[str] = None):
        """
        Clear aggregation cache
        
        Args:
            pattern: Optional pattern to match cache keys (default: clear all aggregation cache)
        """
        try:
            if pattern:
                cache_pattern = f"{self.CACHE_PREFIX}_{pattern}*"
            else:
                cache_pattern = f"{self.CACHE_PREFIX}*"
            
            # Note: This is a simplified approach. In production, you might want to use
            # a more sophisticated cache key management system
            cache.delete_many([cache_pattern])
            logger.info(f"Cleared cache with pattern: {cache_pattern}")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")