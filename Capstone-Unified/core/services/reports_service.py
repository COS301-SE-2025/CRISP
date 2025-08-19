"""
Reports Service - Analytics and report generation for threat intelligence data
Handles sector-specific analysis, trend computation, and trust network insights
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from django.db.models import Q, Count, Avg, Max, Min
from django.utils import timezone
from core.models.models import Organization, Indicator, TTPData, TrustRelationship, ThreatFeed
from .access_control_service import AccessControlService
from .trust_service import TrustService

logger = logging.getLogger(__name__)

class ReportsService:
    """
    Service for generating threat intelligence reports with sector-specific analytics.
    Integrates IoC data, TTP analysis, organization information, and trust relationships.
    """
    
    def __init__(self):
        self.access_control = AccessControlService()
        self.trust_service = TrustService()
    
    def generate_education_sector_analysis(self, start_date: Optional[datetime] = None, 
                                         end_date: Optional[datetime] = None,
                                         organization_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive education sector threat analysis report.
        
        Args:
            start_date: Analysis start date (default: 30 days ago)
            end_date: Analysis end date (default: today)
            organization_ids: Specific organizations to analyze (optional)
            
        Returns:
            Dict containing complete report data
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = timezone.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            logger.info(f"Generating education sector analysis for {start_date} to {end_date}")
            
            # Get educational organizations
            education_orgs = self._get_educational_organizations(organization_ids)
            education_org_ids = [str(org.id) for org in education_orgs]
            
            # Collect threat intelligence data
            indicators = self._get_sector_indicators(education_org_ids, start_date, end_date)
            ttps = self._get_sector_ttps(education_org_ids, start_date, end_date)
            
            # Analyze trust relationships
            trust_data = self._analyze_trust_relationships(education_orgs)
            
            # Generate statistics
            statistics = self._calculate_education_statistics(
                education_orgs, indicators, ttps, trust_data
            )
            
            # Generate temporal trends
            temporal_trends = self._generate_temporal_trends(indicators, ttps, start_date, end_date)
            
            # Analyze threat patterns
            threat_patterns = self._analyze_threat_patterns(indicators, ttps)
            
            # Compile final report
            report = {
                'id': f'education-analysis-{end_date.strftime("%Y-%m-%d")}',
                'title': 'Education Sector Threat Analysis',
                'type': 'Sector Analysis',
                'sector_focus': 'educational',
                'date': end_date.strftime('%B %d, %Y'),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'views': self._calculate_report_views(),  # Mock for now
                'statistics': statistics,
                'description': self._generate_report_description(statistics),
                'temporal_trends': temporal_trends,
                'threat_patterns': threat_patterns,
                'trust_insights': trust_data,
                'organizations_analyzed': len(education_orgs),
                'data_summary': {
                    'indicators_analyzed': len(indicators),
                    'ttps_analyzed': len(ttps),
                    'trust_relationships': len(trust_data.get('relationships', []))
                }
            }
            
            logger.info(f"Successfully generated education sector report with {len(indicators)} indicators and {len(ttps)} TTPs")
            return report
            
        except Exception as e:
            logger.error(f"Error generating education sector analysis: {str(e)}")
            raise
    
    def _get_educational_organizations(self, organization_ids: Optional[List[str]] = None) -> List[Organization]:
        """Get educational organizations for analysis."""
        queryset = Organization.objects.filter(
            organization_type='educational',
            is_active=True
        )
        
        if organization_ids:
            queryset = queryset.filter(id__in=organization_ids)
        
        return list(queryset)
    
    def _get_sector_indicators(self, org_ids: List[str], start_date: datetime, end_date: datetime) -> List[Indicator]:
        """Get IoC indicators associated with educational organizations."""
        try:
            # Get threat feeds belonging to educational organizations
            threat_feeds = ThreatFeed.objects.filter(
                owner_id__in=org_ids,
                is_active=True
            )
            
            feed_ids = [str(tf.id) for tf in threat_feeds]
            
            # Get indicators from these feeds within date range
            indicators = Indicator.objects.filter(
                threat_feed_id__in=feed_ids,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).select_related('threat_feed')
            
            return list(indicators)
            
        except Exception as e:
            logger.error(f"Error fetching sector indicators: {str(e)}")
            return []
    
    def _get_sector_ttps(self, org_ids: List[str], start_date: datetime, end_date: datetime) -> List[TTPData]:
        """Get TTP data associated with educational organizations."""
        try:
            # Get TTPs associated with educational organizations' threat feeds
            threat_feeds = ThreatFeed.objects.filter(
                owner_id__in=org_ids,
                is_active=True
            )
            
            feed_ids = [str(tf.id) for tf in threat_feeds]
            
            # Get TTPs from these feeds within date range
            ttps = TTPData.objects.filter(
                threat_feed_id__in=feed_ids,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).select_related('threat_feed')
            
            return list(ttps)
            
        except Exception as e:
            logger.error(f"Error fetching sector TTPs: {str(e)}")
            return []
    
    def _analyze_trust_relationships(self, organizations: List[Organization]) -> Dict[str, Any]:
        """Analyze trust relationships within the education sector."""
        try:
            org_ids = [str(org.id) for org in organizations]
            
            # Get trust relationships involving educational organizations
            trust_relationships = TrustRelationship.objects.filter(
                Q(source_organization_id__in=org_ids) | Q(target_organization_id__in=org_ids),
                status='active'
            ).select_related('source_organization', 'target_organization', 'trust_level')
            
            # Calculate trust network metrics
            total_relationships = trust_relationships.count()
            internal_relationships = trust_relationships.filter(
                source_organization_id__in=org_ids,
                target_organization_id__in=org_ids
            ).count()
            
            # Trust level distribution
            trust_levels = {}
            for tr in trust_relationships:
                level = tr.trust_level.name if tr.trust_level else 'Unknown'
                trust_levels[level] = trust_levels.get(level, 0) + 1
            
            return {
                'total_relationships': total_relationships,
                'internal_relationships': internal_relationships,
                'external_relationships': total_relationships - internal_relationships,
                'trust_level_distribution': trust_levels,
                'relationships': [
                    {
                        'source': tr.source_organization.name,
                        'target': tr.target_organization.name,
                        'trust_level': tr.trust_level.name if tr.trust_level else 'Unknown',
                        'status': tr.status
                    }
                    for tr in trust_relationships
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trust relationships: {str(e)}")
            return {'total_relationships': 0, 'relationships': []}
    
    def _calculate_education_statistics(self, organizations: List[Organization], 
                                      indicators: List[Indicator], 
                                      ttps: List[TTPData],
                                      trust_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Calculate key statistics for education sector report."""
        
        # Count unique TTPs (techniques)
        unique_techniques = len(set([
            ttp.mitre_technique_id for ttp in ttps if ttp.mitre_technique_id
        ]))
        
        # Determine severity based on indicators and TTPs
        high_severity_indicators = sum(1 for ind in indicators if getattr(ind, 'severity', 'medium').lower() in ['high', 'critical'])
        severity = 'High' if high_severity_indicators > len(indicators) * 0.3 else 'Medium'
        if len(indicators) == 0:
            severity = 'Low'
        
        return [
            {
                'label': 'Institutions Targeted',
                'value': str(len(organizations))
            },
            {
                'label': 'Related IoCs',
                'value': str(len(indicators))
            },
            {
                'label': 'TTPs Identified',
                'value': str(unique_techniques)
            },
            {
                'label': 'Severity',
                'value': severity
            }
        ]
    
    def _generate_temporal_trends(self, indicators: List[Indicator], ttps: List[TTPData], 
                                 start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate temporal trend data for visualization."""
        try:
            # Create daily buckets
            trends = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                day_start = datetime.combine(current_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                day_end = day_start + timedelta(days=1)
                
                # Count indicators and TTPs for this day
                day_indicators = [ind for ind in indicators if day_start <= ind.created_at < day_end]
                day_ttps = [ttp for ttp in ttps if day_start <= ttp.created_at < day_end]
                
                trends.append({
                    'date': current_date.isoformat(),
                    'indicators': len(day_indicators),
                    'ttps': len(day_ttps),
                    'total_events': len(day_indicators) + len(day_ttps)
                })
                
                current_date += timedelta(days=1)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error generating temporal trends: {str(e)}")
            return []
    
    def _analyze_threat_patterns(self, indicators: List[Indicator], ttps: List[TTPData]) -> Dict[str, Any]:
        """Analyze threat patterns and correlations."""
        try:
            # Indicator type distribution
            indicator_types = {}
            for ind in indicators:
                ioc_type = getattr(ind, 'type', 'unknown')
                indicator_types[ioc_type] = indicator_types.get(ioc_type, 0) + 1
            
            # TTP tactic distribution
            tactic_distribution = {}
            for ttp in ttps:
                tactic = getattr(ttp, 'tactic', 'unknown')
                if tactic and tactic != 'unknown':
                    tactic_distribution[tactic] = tactic_distribution.get(tactic, 0) + 1
            
            return {
                'indicator_type_distribution': indicator_types,
                'tactic_distribution': tactic_distribution,
                'most_common_ioc_type': max(indicator_types.items(), key=lambda x: x[1])[0] if indicator_types else 'none',
                'most_common_tactic': max(tactic_distribution.items(), key=lambda x: x[1])[0] if tactic_distribution else 'none'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing threat patterns: {str(e)}")
            return {'indicator_type_distribution': {}, 'tactic_distribution': {}}
    
    def _generate_report_description(self, statistics: List[Dict[str, str]]) -> str:
        """Generate a dynamic description based on the report statistics."""
        
        # Extract values from statistics
        stats_dict = {stat['label']: stat['value'] for stat in statistics}
        institutions = stats_dict.get('Institutions Targeted', '0')
        iocs = stats_dict.get('Related IoCs', '0')
        severity = stats_dict.get('Severity', 'Medium')
        
        if severity.lower() == 'high':
            severity_desc = "a significant threat campaign"
        elif severity.lower() == 'critical':
            severity_desc = "a critical security incident"
        else:
            severity_desc = "moderate threat activity"
        
        description = (
            f"Analysis of {severity_desc} targeting {institutions} educational institutions "
            f"with {iocs} indicators of compromise identified. This report provides "
            f"comprehensive insights into attack patterns, trust relationship effectiveness, "
            f"and threat intelligence sharing within the education sector."
        )
        
        return description
    
    def _calculate_report_views(self) -> int:
        """Calculate/mock report view count."""
        # For now, return a realistic mock value
        # In production, this would track actual view counts
        import random
        return random.randint(50, 300)
    
    def generate_financial_sector_analysis(self, start_date: Optional[datetime] = None, 
                                          end_date: Optional[datetime] = None,
                                          organization_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive financial sector threat analysis report.
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = timezone.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            logger.info(f"Generating financial sector analysis for {start_date} to {end_date}")
            
            # Get financial organizations
            financial_orgs = self._get_organizations_by_type('private', organization_ids)  # Most financial are private
            financial_org_ids = [str(org.id) for org in financial_orgs]
            
            # Collect threat intelligence data
            indicators = self._get_sector_indicators(financial_org_ids, start_date, end_date)
            ttps = self._get_sector_ttps(financial_org_ids, start_date, end_date)
            
            # Analyze trust relationships
            trust_data = self._analyze_trust_relationships(financial_orgs)
            
            # Generate statistics
            statistics = self._calculate_sector_statistics(
                financial_orgs, indicators, ttps, trust_data, 'Financial'
            )
            
            # Generate temporal trends
            temporal_trends = self._generate_temporal_trends(indicators, ttps, start_date, end_date)
            
            # Analyze threat patterns
            threat_patterns = self._analyze_threat_patterns(indicators, ttps)
            
            # Compile final report
            report = {
                'id': f'financial-analysis-{end_date.strftime("%Y-%m-%d")}',
                'title': 'Financial Sector Threat Landscape',
                'type': 'Sector Analysis',
                'sector_focus': 'financial',
                'date': end_date.strftime('%B %d, %Y'),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'views': self._calculate_report_views(),
                'statistics': statistics,
                'description': self._generate_sector_description(statistics, 'financial'),
                'temporal_trends': temporal_trends,
                'threat_patterns': threat_patterns,
                'trust_insights': trust_data,
                'organizations_analyzed': len(financial_orgs),
                'data_summary': {
                    'indicators_analyzed': len(indicators),
                    'ttps_analyzed': len(ttps),
                    'trust_relationships': len(trust_data.get('relationships', []))
                }
            }
            
            logger.info(f"Successfully generated financial sector report with {len(indicators)} indicators and {len(ttps)} TTPs")
            return report
            
        except Exception as e:
            logger.error(f"Error generating financial sector analysis: {str(e)}")
            raise
    
    def generate_government_sector_analysis(self, start_date: Optional[datetime] = None, 
                                           end_date: Optional[datetime] = None,
                                           organization_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive government sector threat analysis report.
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = timezone.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            logger.info(f"Generating government sector analysis for {start_date} to {end_date}")
            
            # Get government organizations
            government_orgs = self._get_organizations_by_type('government', organization_ids)
            government_org_ids = [str(org.id) for org in government_orgs]
            
            # Collect threat intelligence data
            indicators = self._get_sector_indicators(government_org_ids, start_date, end_date)
            ttps = self._get_sector_ttps(government_org_ids, start_date, end_date)
            
            # Analyze trust relationships
            trust_data = self._analyze_trust_relationships(government_orgs)
            
            # Generate statistics
            statistics = self._calculate_sector_statistics(
                government_orgs, indicators, ttps, trust_data, 'Government'
            )
            
            # Generate temporal trends
            temporal_trends = self._generate_temporal_trends(indicators, ttps, start_date, end_date)
            
            # Analyze threat patterns
            threat_patterns = self._analyze_threat_patterns(indicators, ttps)
            
            # Compile final report
            report = {
                'id': f'government-analysis-{end_date.strftime("%Y-%m-%d")}',
                'title': 'Government Sector Security Assessment',
                'type': 'Sector Analysis',
                'sector_focus': 'government',
                'date': end_date.strftime('%B %d, %Y'),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'views': self._calculate_report_views(),
                'statistics': statistics,
                'description': self._generate_sector_description(statistics, 'government'),
                'temporal_trends': temporal_trends,
                'threat_patterns': threat_patterns,
                'trust_insights': trust_data,
                'organizations_analyzed': len(government_orgs),
                'data_summary': {
                    'indicators_analyzed': len(indicators),
                    'ttps_analyzed': len(ttps),
                    'trust_relationships': len(trust_data.get('relationships', []))
                }
            }
            
            logger.info(f"Successfully generated government sector report with {len(indicators)} indicators and {len(ttps)} TTPs")
            return report
            
        except Exception as e:
            logger.error(f"Error generating government sector analysis: {str(e)}")
            raise

    def _get_organizations_by_type(self, org_type: str, organization_ids: Optional[List[str]] = None) -> List[Organization]:
        """Get organizations by type for analysis."""
        queryset = Organization.objects.filter(
            organization_type=org_type,
            is_active=True
        )
        
        if organization_ids:
            queryset = queryset.filter(id__in=organization_ids)
        
        return list(queryset)
    
    def _calculate_sector_statistics(self, organizations: List[Organization], 
                                   indicators: List[Indicator], 
                                   ttps: List[TTPData],
                                   trust_data: Dict[str, Any],
                                   sector_name: str) -> List[Dict[str, str]]:
        """Calculate key statistics for any sector report."""
        
        # Count unique TTPs (techniques)
        unique_techniques = len(set([
            ttp.mitre_technique_id for ttp in ttps if ttp.mitre_technique_id
        ]))
        
        # Determine severity based on indicators and TTPs
        high_severity_indicators = sum(1 for ind in indicators if getattr(ind, 'severity', 'medium').lower() in ['high', 'critical'])
        severity = 'High' if high_severity_indicators > len(indicators) * 0.3 else 'Medium'
        if len(indicators) == 0:
            severity = 'Low'
        
        # Sector-specific label for organizations
        if sector_name.lower() == 'financial':
            org_label = 'Institutions Affected'
        elif sector_name.lower() == 'government':
            org_label = 'Agencies Targeted'
        else:
            org_label = 'Organizations Targeted'
        
        return [
            {
                'label': org_label,
                'value': str(len(organizations))
            },
            {
                'label': 'IoCs Analyzed',
                'value': str(len(indicators))
            },
            {
                'label': 'TTPs Identified',
                'value': str(unique_techniques)
            },
            {
                'label': 'Severity',
                'value': severity
            }
        ]
    
    def _generate_sector_description(self, statistics: List[Dict[str, str]], sector: str) -> str:
        """Generate a dynamic description based on the sector and statistics."""
        
        # Extract values from statistics
        stats_dict = {stat['label']: stat['value'] for stat in statistics}
        orgs = list(stats_dict.values())[0] if statistics else '0'  # First stat is always organization count
        iocs = stats_dict.get('IoCs Analyzed', '0')
        severity = stats_dict.get('Severity', 'Medium')
        
        if severity.lower() == 'high':
            severity_desc = "significant security threats"
        elif severity.lower() == 'critical':
            severity_desc = "critical security incidents"
        else:
            severity_desc = "moderate threat activity"
        
        sector_descriptions = {
            'financial': f"Comprehensive analysis of {severity_desc} targeting {orgs} financial institutions "
                        f"with {iocs} indicators identified. This report focuses on banking trojans, "
                        f"ATM malware, and sophisticated financial crimes affecting the sector.",
            'government': f"Security assessment of {severity_desc} affecting {orgs} government agencies "
                         f"with {iocs} threat indicators analyzed. This report examines nation-state "
                         f"activities, infrastructure threats, and public sector cybersecurity posture.",
            'educational': f"Analysis of {severity_desc} targeting {orgs} educational institutions "
                          f"with {iocs} indicators of compromise identified. This report provides "
                          f"comprehensive insights into attack patterns and threat intelligence sharing."
        }
        
        return sector_descriptions.get(sector, f"Sector analysis with {iocs} indicators across {orgs} organizations.")

    def get_available_report_types(self) -> List[Dict[str, str]]:
        """Get list of available report types."""
        return [
            {
                'id': 'education-sector-analysis',
                'title': 'Education Sector Analysis',
                'description': 'Threat intelligence analysis for educational institutions'
            },
            {
                'id': 'financial-sector-analysis', 
                'title': 'Financial Sector Analysis',
                'description': 'Banking and financial services threat landscape'
            },
            {
                'id': 'government-sector-analysis',
                'title': 'Government Sector Analysis', 
                'description': 'Public sector and government threat assessment'
            }
        ]