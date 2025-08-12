"""
Management command for TTP aggregation processing and analysis
"""

from django.core.management.base import BaseCommand
from core.services.ttp_aggregation_service import TTPAggregationService
from core.models.models import TTPData, ThreatFeed
import json
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Process TTP aggregation analysis and generate reports'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--technique-frequencies',
            action='store_true',
            help='Calculate technique frequency statistics'
        )
        parser.add_argument(
            '--tactic-frequencies',
            action='store_true',
            help='Calculate tactic frequency statistics'
        )
        parser.add_argument(
            '--technique-trends',
            type=str,
            help='Calculate trends for specific technique ID'
        )
        parser.add_argument(
            '--feed-comparison',
            action='store_true',
            help='Generate feed comparison statistics'
        )
        parser.add_argument(
            '--seasonal-analysis',
            action='store_true',
            help='Perform seasonal pattern analysis'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze (default: 30)'
        )
        parser.add_argument(
            '--threat-feed-id',
            type=int,
            help='Filter by specific threat feed ID'
        )
        parser.add_argument(
            '--granularity',
            type=str,
            default='day',
            choices=['day', 'week', 'month'],
            help='Time granularity for trend analysis'
        )
        parser.add_argument(
            '--top-n',
            type=int,
            default=10,
            help='Number of top results to show (default: 10)'
        )
        parser.add_argument(
            '--output-file',
            type=str,
            help='Save results to JSON file'
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear aggregation cache before processing'
        )
        parser.add_argument(
            '--generate-report',
            action='store_true',
            help='Generate comprehensive aggregation report'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('TTP Aggregation Analysis'))
        self.stdout.write('=' * 50)
        
        # Initialize aggregation service
        aggregation_service = TTPAggregationService()
        results = {}
        
        # Clear cache if requested
        if options['clear_cache']:
            self.stdout.write('Clearing aggregation cache...')
            aggregation_service.clear_cache()
            self.stdout.write(self.style.SUCCESS('Cache cleared successfully'))
        
        # Process different analysis types
        if options['technique_frequencies']:
            results['technique_frequencies'] = self.analyze_technique_frequencies(
                aggregation_service, options
            )
        
        if options['tactic_frequencies']:
            results['tactic_frequencies'] = self.analyze_tactic_frequencies(
                aggregation_service, options
            )
        
        if options['technique_trends']:
            results['technique_trends'] = self.analyze_technique_trends(
                aggregation_service, options
            )
        
        if options['feed_comparison']:
            results['feed_comparison'] = self.analyze_feed_comparison(
                aggregation_service, options
            )
        
        if options['seasonal_analysis']:
            results['seasonal_analysis'] = self.analyze_seasonal_patterns(
                aggregation_service, options
            )
        
        if options['generate_report']:
            results = self.generate_comprehensive_report(aggregation_service, options)
        
        # Run all analyses if no specific option is provided
        if not any([
            options['technique_frequencies'],
            options['tactic_frequencies'],
            options['technique_trends'],
            options['feed_comparison'],
            options['seasonal_analysis'],
            options['generate_report']
        ]):
            results = self.generate_comprehensive_report(aggregation_service, options)
        
        # Save results to file if requested
        if options['output_file']:
            self.save_results_to_file(results, options['output_file'])
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('TTP Aggregation Analysis Complete'))
    
    def analyze_technique_frequencies(self, service, options):
        """Analyze technique frequencies"""
        self.stdout.write('\n1. Analyzing Technique Frequencies')
        self.stdout.write('-' * 40)
        
        try:
            frequencies = service.get_technique_frequencies(
                days=options['days'],
                threat_feed_id=options.get('threat_feed_id'),
                include_subtechniques=True,
                min_occurrences=1
            )
            
            if not frequencies:
                self.stdout.write('No technique frequency data found')
                return {}
            
            self.stdout.write(f'Found {len(frequencies)} techniques')
            
            # Show top techniques
            sorted_techniques = sorted(
                frequencies.items(),
                key=lambda x: x[1].count,
                reverse=True
            )[:options['top_n']]
            
            self.stdout.write(f'\nTop {len(sorted_techniques)} Techniques:')
            for technique_id, stats in sorted_techniques:
                self.stdout.write(
                    f'  {technique_id}: {stats.count} occurrences '
                    f'({stats.percentage}%) - Rank #{stats.rank}'
                )
            
            # Convert to serializable format
            return {
                technique_id: {
                    'count': stats.count,
                    'percentage': stats.percentage,
                    'rank': stats.rank,
                    'first_seen': stats.first_seen.isoformat() if stats.first_seen else None,
                    'last_seen': stats.last_seen.isoformat() if stats.last_seen else None
                }
                for technique_id, stats in frequencies.items()
            }
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error analyzing technique frequencies: {e}'))
            return {}
    
    def analyze_tactic_frequencies(self, service, options):
        """Analyze tactic frequencies"""
        self.stdout.write('\n2. Analyzing Tactic Frequencies')
        self.stdout.write('-' * 40)
        
        try:
            frequencies = service.get_tactic_frequencies(
                days=options['days'],
                threat_feed_id=options.get('threat_feed_id'),
                min_occurrences=1
            )
            
            if not frequencies:
                self.stdout.write('No tactic frequency data found')
                return {}
            
            self.stdout.write(f'Found {len(frequencies)} tactics')
            
            # Show all tactics
            sorted_tactics = sorted(
                frequencies.items(),
                key=lambda x: x[1].count,
                reverse=True
            )
            
            self.stdout.write('\nTactic Distribution:')
            for tactic_id, stats in sorted_tactics:
                self.stdout.write(
                    f'  {tactic_id}: {stats.count} occurrences '
                    f'({stats.percentage}%) - Rank #{stats.rank}'
                )
            
            # Convert to serializable format
            return {
                tactic_id: {
                    'count': stats.count,
                    'percentage': stats.percentage,
                    'rank': stats.rank,
                    'first_seen': stats.first_seen.isoformat() if stats.first_seen else None,
                    'last_seen': stats.last_seen.isoformat() if stats.last_seen else None
                }
                for tactic_id, stats in frequencies.items()
            }
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error analyzing tactic frequencies: {e}'))
            return {}
    
    def analyze_technique_trends(self, service, options):
        """Analyze technique trends"""
        technique_id = options['technique_trends']
        self.stdout.write(f'\n3. Analyzing Trends for Technique {technique_id}')
        self.stdout.write('-' * 40)
        
        try:
            trend_points = service.get_technique_trends(
                technique_id=technique_id,
                days=options['days'],
                granularity=options['granularity'],
                threat_feed_id=options.get('threat_feed_id'),
                moving_average_window=7
            )
            
            if not trend_points:
                self.stdout.write(f'No trend data found for technique {technique_id}')
                return {}
            
            # Analyze trend direction
            trend_analysis = service.analyze_trend_direction(trend_points)
            
            self.stdout.write(f'Trend Analysis for {technique_id}:')
            self.stdout.write(f'  Direction: {trend_analysis.direction}')
            self.stdout.write(f'  Strength: {trend_analysis.strength:.3f}')
            self.stdout.write(f'  Confidence: {trend_analysis.confidence:.3f}')
            self.stdout.write(f'  Slope: {trend_analysis.slope:.4f}')
            self.stdout.write(f'  R-squared: {trend_analysis.r_squared:.3f}')
            self.stdout.write(f'  Volatility: {trend_analysis.volatility:.3f}')
            
            # Show recent trend points
            recent_points = trend_points[-7:] if len(trend_points) >= 7 else trend_points
            self.stdout.write(f'\nRecent Activity (last {len(recent_points)} periods):')
            for point in recent_points:
                change_str = f' ({point.percentage_change:+.1f}%)' if point.percentage_change is not None else ''
                ma_str = f' MA: {point.moving_average:.1f}' if point.moving_average is not None else ''
                self.stdout.write(f'  {point.date}: {point.value} occurrences{change_str}{ma_str}')
            
            return {
                'technique_id': technique_id,
                'trend_analysis': {
                    'direction': trend_analysis.direction,
                    'strength': trend_analysis.strength,
                    'confidence': trend_analysis.confidence,
                    'slope': trend_analysis.slope,
                    'r_squared': trend_analysis.r_squared,
                    'volatility': trend_analysis.volatility
                },
                'trend_points': [
                    {
                        'date': point.date,
                        'value': point.value,
                        'percentage_change': point.percentage_change,
                        'moving_average': point.moving_average
                    }
                    for point in trend_points
                ]
            }
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error analyzing technique trends: {e}'))
            return {}
    
    def analyze_feed_comparison(self, service, options):
        """Analyze feed comparison statistics"""
        self.stdout.write('\n4. Analyzing Feed Comparison')
        self.stdout.write('-' * 40)
        
        try:
            comparison_stats = service.get_feed_comparison_stats(
                days=options['days'],
                top_n=options['top_n']
            )
            
            if not comparison_stats:
                self.stdout.write('No feed comparison data found')
                return {}
            
            # Display feed statistics
            feed_stats = comparison_stats.get('feed_statistics', [])
            self.stdout.write(f'Analyzed {len(feed_stats)} threat feeds')
            
            self.stdout.write('\nFeed Performance:')
            for feed in feed_stats[:options['top_n']]:
                self.stdout.write(
                    f'  {feed["threat_feed__name"]}: '
                    f'{feed["ttp_count"]} TTPs, '
                    f'{feed["unique_techniques"]} techniques, '
                    f'{feed["unique_tactics"]} tactics, '
                    f'{feed["avg_techniques_per_day"]:.1f} avg/day'
                )
            
            # Display summary
            summary = comparison_stats.get('summary', {})
            self.stdout.write('\nSummary:')
            self.stdout.write(f'  Total TTPs: {summary.get("total_ttps_in_period", 0)}')
            self.stdout.write(f'  Most active feed: {summary.get("most_active_feed", "N/A")}')
            self.stdout.write(f'  Most common technique: {summary.get("most_common_technique", "N/A")}')
            self.stdout.write(f'  Most common tactic: {summary.get("most_common_tactic", "N/A")}')
            
            return comparison_stats
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error analyzing feed comparison: {e}'))
            return {}
    
    def analyze_seasonal_patterns(self, service, options):
        """Analyze seasonal patterns"""
        self.stdout.write('\n5. Analyzing Seasonal Patterns')
        self.stdout.write('-' * 40)
        
        try:
            seasonal_analysis = service.get_seasonal_patterns(
                technique_id=None,  # Analyze all techniques
                days=max(options['days'], 90),  # Minimum 90 days for seasonal analysis
                granularity='week'
            )
            
            if 'error' in seasonal_analysis:
                self.stdout.write(f'Error in seasonal analysis: {seasonal_analysis["error"]}')
                return {}
            
            stats = seasonal_analysis.get('statistics', {})
            self.stdout.write('Seasonal Pattern Analysis:')
            self.stdout.write(f'  Mean count per period: {stats.get("mean_count", 0):.2f}')
            self.stdout.write(f'  Standard deviation: {stats.get("std_deviation", 0):.2f}')
            self.stdout.write(f'  Seasonality strength: {stats.get("seasonality_strength", 0):.3f}')
            
            peak = stats.get('peak_period', {})
            valley = stats.get('valley_period', {})
            self.stdout.write(f'  Peak period: {peak.get("label", "N/A")} ({peak.get("count", 0)} occurrences)')
            self.stdout.write(f'  Valley period: {valley.get("label", "N/A")} ({valley.get("count", 0)} occurrences)')
            
            interpretation = seasonal_analysis.get('interpretation', '')
            self.stdout.write(f'  Interpretation: {interpretation}')
            
            return seasonal_analysis
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error analyzing seasonal patterns: {e}'))
            return {}
    
    def generate_comprehensive_report(self, service, options):
        """Generate a comprehensive aggregation report"""
        self.stdout.write('\nGenerating Comprehensive TTP Aggregation Report')
        self.stdout.write('=' * 50)
        
        report = {
            'generated_at': timezone.now().isoformat(),
            'analysis_period': {
                'days': options['days'],
                'threat_feed_id': options.get('threat_feed_id'),
                'granularity': options['granularity']
            }
        }
        
        # Get database statistics
        total_ttps = TTPData.objects.count()
        recent_ttps = TTPData.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=options['days'])
        ).count()
        
        self.stdout.write(f'Database Overview:')
        self.stdout.write(f'  Total TTPs: {total_ttps}')
        self.stdout.write(f'  Recent TTPs ({options["days"]} days): {recent_ttps}')
        
        report['database_overview'] = {
            'total_ttps': total_ttps,
            'recent_ttps': recent_ttps
        }
        
        # Generate all analyses
        report['technique_frequencies'] = self.analyze_technique_frequencies(service, options)
        report['tactic_frequencies'] = self.analyze_tactic_frequencies(service, options)
        report['feed_comparison'] = self.analyze_feed_comparison(service, options)
        report['seasonal_analysis'] = self.analyze_seasonal_patterns(service, options)
        
        return report
    
    def save_results_to_file(self, results, filename):
        """Save results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.stdout.write(f'\nResults saved to: {filename}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error saving results to file: {e}'))