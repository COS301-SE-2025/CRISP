"""
Reports Service - Analytics and report generation for threat intelligence data
Handles sector-specific analysis, trend computation, and trust network insights
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from django.db.models import Q, Count, Avg, Max, Min
from django.utils import timezone
from core.models.models import Organization, Indicator, TTPData, TrustRelationship, ThreatFeed, Report
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

    def _persist_report(self, report_type: str, report_data: Dict[str, Any],
                       generated_by, organization, parameters: Dict[str, Any] = None,
                       start_date: datetime = None, end_date: datetime = None) -> Report:
        """
        Persist a generated report to the database.

        Args:
            report_type: Type of report (education_sector, financial_sector, etc.)
            report_data: Complete report data dictionary
            generated_by: User who generated the report
            organization: Organization the report belongs to
            parameters: Parameters used to generate the report
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            Saved Report instance
        """
        try:
            # Check for recent duplicate reports to prevent multiple submissions
            from django.utils import timezone
            cutoff_time = timezone.now() - timezone.timedelta(seconds=30)  # 30 second window

            recent_report = Report.objects.filter(
                report_type=report_type,
                generated_by=generated_by,
                organization=organization,
                created_at__gte=cutoff_time
            ).first()

            if recent_report:
                logger.info(f"Returning existing recent report {recent_report.id} to prevent duplicate")
                return recent_report

            # Extract basic information
            title = report_data.get('title', f'{report_type.replace("_", " ").title()} Report')
            description = report_data.get('description', '')

            # Prepare data sources and counts
            data_sources = report_data.get('meta', {}).get('data_sources', [])
            data_counts = report_data.get('data_summary', {})

            # Create report instance
            report = Report.objects.create(
                title=title,
                report_type=report_type,
                description=description,
                report_data=report_data,
                parameters=parameters or {},
                generated_by=generated_by,
                organization=organization,
                status='completed',
                analysis_start_date=start_date,
                analysis_end_date=end_date,
                data_sources=data_sources,
                data_counts=data_counts,
                available_formats=['json', 'pdf', 'csv'],
                tags=[report_type.split('_')[0], 'threat_intelligence', 'analysis'],
                metadata={
                    'generated_at': datetime.now().isoformat(),
                    'generation_method': 'automated',
                    'version': '1.0'
                }
            )

            logger.info(f"Successfully persisted report {report.id} of type {report_type}")
            return report

        except Exception as e:
            logger.error(f"Error persisting report: {str(e)}")
            # Create report with error status
            report = Report.objects.create(
                title=f"Failed {report_type.replace('_', ' ').title()} Report",
                report_type=report_type,
                description=f"Report generation failed: {str(e)}",
                report_data={},
                parameters=parameters or {},
                generated_by=generated_by,
                organization=organization,
                status='error',
                error_message=str(e),
                analysis_start_date=start_date,
                analysis_end_date=end_date
            )
            return report

    def get_reports_for_organization(self, organization, user=None, report_type: str = None,
                                   limit: int = None, include_shared: bool = True) -> List[Report]:
        """
        Get reports for an organization with optional filtering.

        Args:
            organization: Organization to get reports for
            user: User making the request (for access control)
            report_type: Filter by specific report type
            limit: Limit number of results
            include_shared: Include reports shared with this organization

        Returns:
            List of Report objects
        """
        try:
            # Base query for organization's own reports
            queryset = Report.objects.filter(organization=organization)

            # Add sector reports (public threat intelligence) - these should be visible to all organizations
            sector_report_types = ['education_sector', 'financial_sector', 'government_sector']
            sector_reports = Report.objects.filter(report_type__in=sector_report_types).exclude(organization=organization)
            if sector_reports.exists():
                queryset = queryset.union(sector_reports)

            # Add shared reports if requested
            if include_shared:
                shared_reports = Report.objects.filter(
                    shared_with_organizations=organization
                ).exclude(organization=organization).exclude(report_type__in=sector_report_types)
                if shared_reports.exists():
                    queryset = queryset.union(shared_reports)

            # Filter by report type
            if report_type:
                queryset = queryset.filter(report_type=report_type)

            # Order by creation date
            queryset = queryset.order_by('-created_at')

            # Apply limit
            if limit:
                queryset = queryset[:limit]

            return list(queryset)

        except Exception as e:
            logger.error(f"Error fetching reports for organization {organization.id}: {str(e)}")
            return []

    def get_report_by_id(self, report_id: str, user=None) -> Optional[Report]:
        """
        Get a specific report by ID with access control.

        Args:
            report_id: UUID of the report
            user: User making the request

        Returns:
            Report instance or None
        """
        try:
            report = Report.objects.get(id=report_id)

            # Check access permissions
            if user and not report.can_be_accessed_by(user):
                logger.warning(f"User {user.username} attempted to access unauthorized report {report_id}")
                return None

            # Increment view count
            report.increment_view_count()

            return report

        except Report.DoesNotExist:
            logger.warning(f"Report {report_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching report {report_id}: {str(e)}")
            return None
    
    def generate_education_sector_analysis(self, start_date: Optional[datetime] = None,
                                         end_date: Optional[datetime] = None,
                                         organization_ids: Optional[List[str]] = None,
                                         generated_by=None, organization=None,
                                         persist: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive education sector threat analysis report.

        Args:
            start_date: Analysis start date (default: 30 days ago)
            end_date: Analysis end date (default: today)
            organization_ids: Specific organizations to analyze (optional)
            generated_by: User who generated the report (for persistence)
            organization: Organization the report belongs to (for persistence)
            persist: Whether to persist the report to database (default: True)

        Returns:
            Dict containing complete report data with persistent report info if persisted
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
                },
                'indicators': [
                    {
                        'id': str(ind.id),
                        'type': getattr(ind, 'type', 'unknown'),
                        'value': getattr(ind, 'value', 'N/A'),
                        'severity': getattr(ind, 'severity', 'medium'),
                        'first_seen': getattr(ind, 'first_seen', ind.created_at).isoformat() if hasattr(ind, 'first_seen') else ind.created_at.isoformat(),
                        'created_at': ind.created_at.isoformat(),
                        'source': getattr(ind, 'source', 'Internal')
                    } for ind in indicators
                ],
                'ttps': [
                    {
                        'id': str(ttp.id),
                        'technique': getattr(ttp, 'technique', getattr(ttp, 'name', 'Unknown')),
                        'mitre_technique_id': getattr(ttp, 'mitre_technique_id', 'N/A'),
                        'tactic': getattr(ttp, 'tactic', 'Unknown'),
                        'description': getattr(ttp, 'description', 'No description available'),
                        'created_at': ttp.created_at.isoformat()
                    } for ttp in ttps
                ]
            }

            # Persist report if requested and parameters provided
            if persist and generated_by and organization:
                try:
                    parameters = {
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None,
                        'organization_ids': organization_ids,
                        'report_type': 'education_sector'
                    }

                    persistent_report = self._persist_report(
                        report_type='education_sector',
                        report_data=report,
                        generated_by=generated_by,
                        organization=organization,
                        parameters=parameters,
                        start_date=start_date,
                        end_date=end_date
                    )

                    # Add persistence information to report
                    report['persistent_report_id'] = str(persistent_report.id)
                    report['persistent_report_url'] = f"/api/reports/{persistent_report.id}/"
                    report['persistent'] = True
                    report['view_count'] = persistent_report.view_count

                    logger.info(f"Successfully persisted education sector report {persistent_report.id}")

                except Exception as persist_error:
                    logger.error(f"Error persisting report: {str(persist_error)}")
                    report['persistent'] = False
                    report['persistence_error'] = str(persist_error)
            else:
                report['persistent'] = False

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
        """Get IoC indicators from all active threat feeds (not limited to organization-owned feeds)."""
        try:
            # Get all active threat feeds (including external feeds like AlienVault)
            # This ensures we include indicators from external sources that benefit all organizations
            threat_feeds = ThreatFeed.objects.filter(
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
        """Get TTP data from all active threat feeds (not limited to organization-owned feeds)."""
        try:
            # Get all active threat feeds (including external feeds like AlienVault)
            # This ensures we include TTPs from external sources that benefit all organizations
            threat_feeds = ThreatFeed.objects.filter(
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
                                          organization_ids: Optional[List[str]] = None,
                                          generated_by=None, organization=None,
                                          persist: bool = True) -> Dict[str, Any]:
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
                },
                'indicators': [
                    {
                        'id': str(ind.id),
                        'type': getattr(ind, 'type', 'unknown'),
                        'value': getattr(ind, 'value', 'N/A'),
                        'severity': getattr(ind, 'severity', 'medium'),
                        'first_seen': getattr(ind, 'first_seen', ind.created_at).isoformat() if hasattr(ind, 'first_seen') else ind.created_at.isoformat(),
                        'created_at': ind.created_at.isoformat(),
                        'source': getattr(ind, 'source', 'Internal')
                    } for ind in indicators
                ],
                'ttps': [
                    {
                        'id': str(ttp.id),
                        'technique': getattr(ttp, 'technique', getattr(ttp, 'name', 'Unknown')),
                        'mitre_technique_id': getattr(ttp, 'mitre_technique_id', 'N/A'),
                        'tactic': getattr(ttp, 'tactic', 'Unknown'),
                        'description': getattr(ttp, 'description', 'No description available'),
                        'created_at': ttp.created_at.isoformat()
                    } for ttp in ttps
                ]
            }

            # Persist report if requested and parameters provided
            if persist and generated_by and organization:
                try:
                    parameters = {
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None,
                        'organization_ids': organization_ids,
                        'report_type': 'financial_sector'
                    }

                    persistent_report = self._persist_report(
                        report_type='financial_sector',
                        report_data=report,
                        generated_by=generated_by,
                        organization=organization,
                        parameters=parameters,
                        start_date=start_date,
                        end_date=end_date
                    )

                    # Add persistence information to report
                    report['persistent_report_id'] = str(persistent_report.id)
                    report['persistent_report_url'] = f"/api/reports/{persistent_report.id}/"
                    report['persistent'] = True
                    report['view_count'] = persistent_report.view_count

                    logger.info(f"Successfully persisted financial sector report {persistent_report.id}")

                except Exception as persist_error:
                    logger.error(f"Error persisting report: {str(persist_error)}")
                    report['persistent'] = False
                    report['persistence_error'] = str(persist_error)
            else:
                report['persistent'] = False

            logger.info(f"Successfully generated financial sector report with {len(indicators)} indicators and {len(ttps)} TTPs")
            return report
            
        except Exception as e:
            logger.error(f"Error generating financial sector analysis: {str(e)}")
            raise
    
    def generate_government_sector_analysis(self, start_date: Optional[datetime] = None,
                                           end_date: Optional[datetime] = None,
                                           organization_ids: Optional[List[str]] = None,
                                           generated_by=None, organization=None,
                                           persist: bool = True) -> Dict[str, Any]:
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
                },
                'indicators': [
                    {
                        'id': str(ind.id),
                        'type': getattr(ind, 'type', 'unknown'),
                        'value': getattr(ind, 'value', 'N/A'),
                        'severity': getattr(ind, 'severity', 'medium'),
                        'first_seen': getattr(ind, 'first_seen', ind.created_at).isoformat() if hasattr(ind, 'first_seen') else ind.created_at.isoformat(),
                        'created_at': ind.created_at.isoformat(),
                        'source': getattr(ind, 'source', 'Internal')
                    } for ind in indicators
                ],
                'ttps': [
                    {
                        'id': str(ttp.id),
                        'technique': getattr(ttp, 'technique', getattr(ttp, 'name', 'Unknown')),
                        'mitre_technique_id': getattr(ttp, 'mitre_technique_id', 'N/A'),
                        'tactic': getattr(ttp, 'tactic', 'Unknown'),
                        'description': getattr(ttp, 'description', 'No description available'),
                        'created_at': ttp.created_at.isoformat()
                    } for ttp in ttps
                ]
            }

            # Persist report if requested and parameters provided
            if persist and generated_by and organization:
                try:
                    parameters = {
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None,
                        'organization_ids': organization_ids,
                        'report_type': 'government_sector'
                    }

                    persistent_report = self._persist_report(
                        report_type='government_sector',
                        report_data=report,
                        generated_by=generated_by,
                        organization=organization,
                        parameters=parameters,
                        start_date=start_date,
                        end_date=end_date
                    )

                    # Add persistence information to report
                    report['persistent_report_id'] = str(persistent_report.id)
                    report['persistent_report_url'] = f"/api/reports/{persistent_report.id}/"
                    report['persistent'] = True
                    report['view_count'] = persistent_report.view_count

                    logger.info(f"Successfully persisted government sector report {persistent_report.id}")

                except Exception as persist_error:
                    logger.error(f"Error persisting report: {str(persist_error)}")
                    report['persistent'] = False
                    report['persistence_error'] = str(persist_error)
            else:
                report['persistent'] = False

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