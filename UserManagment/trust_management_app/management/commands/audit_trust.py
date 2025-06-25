from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import json

from ...models import (
    TrustRelationship, TrustGroup, TrustGroupMembership, 
    TrustLog, TrustLevel, SharingPolicy
)


class Command(BaseCommand):
    """
    Management command to audit trust relationships and generate reports.
    Provides comprehensive analysis of trust configuration and activity.
    """
    
    help = 'Audit trust relationships and generate security reports'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--report-type',
            choices=['summary', 'detailed', 'security', 'activity', 'all'],
            default='summary',
            help='Type of audit report to generate',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to include in activity reports (default: 30)',
        )
        parser.add_argument(
            '--organization',
            help='Focus audit on specific organization (UUID)',
        )
        parser.add_argument(
            '--output-format',
            choices=['text', 'json'],
            default='text',
            help='Output format for the report',
        )
        parser.add_argument(
            '--save-to-file',
            help='Save report to specified file path',
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        report_data = {}
        
        if options['report_type'] in ['summary', 'all']:
            report_data['summary'] = self.generate_summary_report()
        
        if options['report_type'] in ['detailed', 'all']:
            report_data['detailed'] = self.generate_detailed_report(options.get('organization'))
        
        if options['report_type'] in ['security', 'all']:
            report_data['security'] = self.generate_security_report(options['days'])
        
        if options['report_type'] in ['activity', 'all']:
            report_data['activity'] = self.generate_activity_report(options['days'])
        
        # Output the report
        if options['output_format'] == 'json':
            output = json.dumps(report_data, indent=2, default=str)
        else:
            output = self.format_text_report(report_data, options['report_type'])
        
        if options['save_to_file']:
            with open(options['save_to_file'], 'w') as f:
                f.write(output)
            self.stdout.write(f"Report saved to {options['save_to_file']}")
        else:
            self.stdout.write(output)
    
    def generate_summary_report(self):
        """Generate summary statistics."""
        now = timezone.now()
        
        # Basic counts
        total_relationships = TrustRelationship.objects.count()
        active_relationships = TrustRelationship.objects.filter(
            is_active=True, 
            status='active'
        ).count()
        
        pending_relationships = TrustRelationship.objects.filter(
            status='pending'
        ).count()
        
        total_groups = TrustGroup.objects.count()
        active_groups = TrustGroup.objects.filter(is_active=True).count()
        
        total_memberships = TrustGroupMembership.objects.count()
        active_memberships = TrustGroupMembership.objects.filter(is_active=True).count()
        
        # Trust level distribution
        trust_level_distribution = TrustRelationship.objects.filter(
            is_active=True
        ).values('trust_level__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Relationship type distribution
        relationship_type_distribution = TrustRelationship.objects.filter(
            is_active=True
        ).values('relationship_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent activity (last 7 days)
        week_ago = now - timedelta(days=7)
        recent_relationships = TrustRelationship.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        recent_group_joins = TrustGroupMembership.objects.filter(
            joined_at__gte=week_ago
        ).count()
        
        return {
            'timestamp': now,
            'relationships': {
                'total': total_relationships,
                'active': active_relationships,
                'pending': pending_relationships,
                'activation_rate': round(active_relationships / max(total_relationships, 1) * 100, 2)
            },
            'groups': {
                'total': total_groups,
                'active': active_groups,
                'total_memberships': total_memberships,
                'active_memberships': active_memberships
            },
            'trust_level_distribution': list(trust_level_distribution),
            'relationship_type_distribution': list(relationship_type_distribution),
            'recent_activity': {
                'new_relationships_7d': recent_relationships,
                'new_group_memberships_7d': recent_group_joins
            }
        }
    
    def generate_detailed_report(self, organization=None):
        """Generate detailed relationship analysis."""
        relationships_query = TrustRelationship.objects.select_related('trust_level')
        
        if organization:
            relationships_query = relationships_query.filter(
                Q(source_organization=organization) | 
                Q(target_organization=organization)
            )
        
        relationships = relationships_query.all()
        
        # Analyze relationships
        analysis = {
            'total_analyzed': len(relationships),
            'by_status': {},
            'by_trust_level': {},
            'by_type': {},
            'expiring_soon': [],
            'inactive_relationships': [],
            'approval_pending': []
        }
        
        now = timezone.now()
        month_from_now = now + timedelta(days=30)
        
        for rel in relationships:
            # Status analysis
            status = rel.status
            analysis['by_status'][status] = analysis['by_status'].get(status, 0) + 1
            
            # Trust level analysis
            trust_level = rel.trust_level.name
            analysis['by_trust_level'][trust_level] = analysis['by_trust_level'].get(trust_level, 0) + 1
            
            # Type analysis
            rel_type = rel.relationship_type
            analysis['by_type'][rel_type] = analysis['by_type'].get(rel_type, 0) + 1
            
            # Check for expiring relationships
            if rel.valid_until and rel.valid_until <= month_from_now and rel.is_active:
                analysis['expiring_soon'].append({
                    'id': str(rel.id),
                    'source': rel.source_organization,
                    'target': rel.target_organization,
                    'expires': rel.valid_until,
                    'trust_level': trust_level
                })
            
            # Check for inactive relationships
            if not rel.is_active or rel.status in ['suspended', 'revoked']:
                analysis['inactive_relationships'].append({
                    'id': str(rel.id),
                    'source': rel.source_organization,
                    'target': rel.target_organization,
                    'status': rel.status,
                    'last_modified': rel.updated_at
                })
            
            # Check for pending approvals
            if rel.status == 'pending':
                analysis['approval_pending'].append({
                    'id': str(rel.id),
                    'source': rel.source_organization,
                    'target': rel.target_organization,
                    'created': rel.created_at,
                    'source_approved': rel.approved_by_source,
                    'target_approved': rel.approved_by_target
                })
        
        return analysis
    
    def generate_security_report(self, days):
        """Generate security-focused analysis."""
        now = timezone.now()
        cutoff_date = now - timedelta(days=days)
        
        # Failed operations
        failed_logs = TrustLog.objects.filter(
            timestamp__gte=cutoff_date,
            success=False
        ).values('action', 'failure_reason').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Suspicious patterns
        suspicious_patterns = []
        
        # Multiple failed access attempts
        access_denied_logs = TrustLog.objects.filter(
            timestamp__gte=cutoff_date,
            action='access_denied'
        ).values('source_organization').annotate(
            count=Count('id')
        ).filter(count__gte=10).order_by('-count')
        
        for pattern in access_denied_logs:
            suspicious_patterns.append({
                'type': 'multiple_access_denied',
                'organization': pattern['source_organization'],
                'count': pattern['count'],
                'description': f"Organization had {pattern['count']} access denied events"
            })
        
        # Rapid relationship changes
        rapid_changes = TrustLog.objects.filter(
            timestamp__gte=cutoff_date,
            action__in=['relationship_created', 'relationship_revoked']
        ).values('source_organization').annotate(
            count=Count('id')
        ).filter(count__gte=5).order_by('-count')
        
        for pattern in rapid_changes:
            suspicious_patterns.append({
                'type': 'rapid_relationship_changes',
                'organization': pattern['source_organization'],
                'count': pattern['count'],
                'description': f"Organization had {pattern['count']} rapid relationship changes"
            })
        
        # Recently revoked relationships
        recent_revocations = TrustRelationship.objects.filter(
            revoked_at__gte=cutoff_date
        ).select_related('trust_level')
        
        revocation_analysis = []
        for rel in recent_revocations:
            revocation_analysis.append({
                'id': str(rel.id),
                'source': rel.source_organization,
                'target': rel.target_organization,
                'trust_level': rel.trust_level.name,
                'revoked_at': rel.revoked_at,
                'revoked_by': rel.revoked_by,
                'reason': rel.notes.split('Revoked: ')[-1] if 'Revoked: ' in rel.notes else 'No reason provided'
            })
        
        return {
            'analysis_period_days': days,
            'failed_operations': list(failed_logs),
            'suspicious_patterns': suspicious_patterns,
            'recent_revocations': revocation_analysis,
            'security_metrics': {
                'total_failed_operations': sum(log['count'] for log in failed_logs),
                'organizations_with_suspicious_activity': len(suspicious_patterns),
                'recent_revocations_count': len(revocation_analysis)
            }
        }
    
    def generate_activity_report(self, days):
        """Generate activity analysis."""
        now = timezone.now()
        cutoff_date = now - timedelta(days=days)
        
        # Activity by action type
        activity_by_action = TrustLog.objects.filter(
            timestamp__gte=cutoff_date
        ).values('action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Most active organizations
        most_active_orgs = TrustLog.objects.filter(
            timestamp__gte=cutoff_date
        ).values('source_organization').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Daily activity trend
        daily_activity = TrustLog.objects.filter(
            timestamp__gte=cutoff_date
        ).extra(
            select={'day': 'DATE(timestamp)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # New relationships created
        new_relationships = TrustRelationship.objects.filter(
            created_at__gte=cutoff_date
        ).count()
        
        # New group memberships
        new_memberships = TrustGroupMembership.objects.filter(
            joined_at__gte=cutoff_date
        ).count()
        
        # Intelligence access events
        access_events = TrustLog.objects.filter(
            timestamp__gte=cutoff_date,
            action__in=['access_granted', 'access_denied']
        ).values('action').annotate(
            count=Count('id')
        )
        
        return {
            'analysis_period_days': days,
            'activity_by_action': list(activity_by_action),
            'most_active_organizations': list(most_active_orgs),
            'daily_activity_trend': list(daily_activity),
            'summary_metrics': {
                'new_relationships': new_relationships,
                'new_group_memberships': new_memberships,
                'total_log_entries': TrustLog.objects.filter(timestamp__gte=cutoff_date).count()
            },
            'intelligence_access': list(access_events)
        }
    
    def format_text_report(self, report_data, report_type):
        """Format report data as readable text."""
        output = []
        output.append("=" * 60)
        output.append("CRISP Trust Management Audit Report")
        output.append("=" * 60)
        output.append(f"Generated: {timezone.now()}")
        output.append(f"Report Type: {report_type}")
        output.append("")
        
        if 'summary' in report_data:
            output.append("SUMMARY REPORT")
            output.append("-" * 20)
            summary = report_data['summary']
            
            output.append(f"Trust Relationships:")
            output.append(f"  Total: {summary['relationships']['total']}")
            output.append(f"  Active: {summary['relationships']['active']}")
            output.append(f"  Pending: {summary['relationships']['pending']}")
            output.append(f"  Activation Rate: {summary['relationships']['activation_rate']}%")
            output.append("")
            
            output.append(f"Trust Groups:")
            output.append(f"  Total: {summary['groups']['total']}")
            output.append(f"  Active: {summary['groups']['active']}")
            output.append(f"  Total Memberships: {summary['groups']['total_memberships']}")
            output.append(f"  Active Memberships: {summary['groups']['active_memberships']}")
            output.append("")
            
            if summary['trust_level_distribution']:
                output.append("Trust Level Distribution:")
                for item in summary['trust_level_distribution']:
                    output.append(f"  {item['trust_level__name']}: {item['count']}")
                output.append("")
            
            output.append(f"Recent Activity (7 days):")
            output.append(f"  New Relationships: {summary['recent_activity']['new_relationships_7d']}")
            output.append(f"  New Group Memberships: {summary['recent_activity']['new_group_memberships_7d']}")
            output.append("")
        
        if 'security' in report_data:
            output.append("SECURITY ANALYSIS")
            output.append("-" * 20)
            security = report_data['security']
            
            if security['failed_operations']:
                output.append("Failed Operations:")
                for op in security['failed_operations']:
                    output.append(f"  {op['action']}: {op['count']} failures")
                output.append("")
            
            if security['suspicious_patterns']:
                output.append("Suspicious Patterns:")
                for pattern in security['suspicious_patterns']:
                    output.append(f"  {pattern['type']}: {pattern['description']}")
                output.append("")
            
            if security['recent_revocations']:
                output.append("Recent Revocations:")
                for rev in security['recent_revocations']:
                    output.append(f"  {rev['source']} -> {rev['target']}: {rev['reason']}")
                output.append("")
        
        if 'activity' in report_data:
            output.append("ACTIVITY ANALYSIS")
            output.append("-" * 20)
            activity = report_data['activity']
            
            output.append("Activity Summary:")
            output.append(f"  New Relationships: {activity['summary_metrics']['new_relationships']}")
            output.append(f"  New Memberships: {activity['summary_metrics']['new_group_memberships']}")
            output.append(f"  Total Log Entries: {activity['summary_metrics']['total_log_entries']}")
            output.append("")
            
            if activity['most_active_organizations']:
                output.append("Most Active Organizations:")
                for org in activity['most_active_organizations'][:5]:
                    output.append(f"  {org['source_organization']}: {org['count']} activities")
                output.append("")
        
        return "\n".join(output)