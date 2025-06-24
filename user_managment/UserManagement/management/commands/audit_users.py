from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ...models import CustomUser, AuthenticationLog, UserSession


class Command(BaseCommand):
    help = 'Audit user accounts and generate security reports'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output-format',
            choices=['text', 'json', 'csv'],
            default='text',
            help='Output format for the audit report'
        )
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help='Include inactive users in the report'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to look back for activity analysis'
        )
        parser.add_argument(
            '--security-focus',
            action='store_true',
            help='Focus on security-related issues'
        )
        parser.add_argument(
            '--export-file',
            type=str,
            help='Export report to file'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting CRISP User Security Audit...')
        )
        
        try:
            # Generate audit report
            audit_data = self.generate_audit_report(options)
            
            # Format and display/export report
            if options['output_format'] == 'json':
                self.output_json_report(audit_data, options.get('export_file'))
            elif options['output_format'] == 'csv':
                self.output_csv_report(audit_data, options.get('export_file'))
            else:
                self.output_text_report(audit_data, options.get('export_file'))
            
            self.stdout.write(
                self.style.SUCCESS('User audit completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Audit failed: {str(e)}')
            )
            raise
    
    def generate_audit_report(self, options):
        """Generate comprehensive audit report"""
        days_back = options['days']
        include_inactive = options['include_inactive']
        security_focus = options['security_focus']
        
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        # Get user queryset
        users_queryset = CustomUser.objects.all()
        if not include_inactive:
            users_queryset = users_queryset.filter(is_active=True)
        
        audit_data = {
            'generated_at': timezone.now().isoformat(),
            'period_days': days_back,
            'include_inactive': include_inactive,
            'summary': {},
            'users': [],
            'security_issues': [],
            'recommendations': []
        }
        
        # Generate summary statistics
        audit_data['summary'] = self.generate_summary_stats(users_queryset, cutoff_date)
        
        # Analyze each user
        for user in users_queryset:
            user_analysis = self.analyze_user(user, cutoff_date, security_focus)
            audit_data['users'].append(user_analysis)
            
            # Collect security issues
            if user_analysis['security_issues']:
                audit_data['security_issues'].extend(user_analysis['security_issues'])
        
        # Generate recommendations
        audit_data['recommendations'] = self.generate_recommendations(audit_data)
        
        return audit_data
    
    def generate_summary_stats(self, users_queryset, cutoff_date):
        """Generate summary statistics"""
        total_users = users_queryset.count()
        active_users = users_queryset.filter(is_active=True).count()
        verified_users = users_queryset.filter(is_verified=True).count()
        locked_users = users_queryset.filter(account_locked_until__gt=timezone.now()).count()
        
        # Role distribution
        role_stats = {}
        for role_choice in CustomUser._meta.get_field('role').choices:
            role = role_choice[0]
            count = users_queryset.filter(role=role).count()
            role_stats[role] = count
        
        # Recent activity
        recent_logins = AuthenticationLog.objects.filter(
            action='login_success',
            timestamp__gte=cutoff_date
        ).values('user').distinct().count()
        
        failed_logins = AuthenticationLog.objects.filter(
            action='login_failed',
            timestamp__gte=cutoff_date
        ).count()
        
        # Active sessions
        active_sessions = UserSession.objects.filter(is_active=True).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'locked_users': locked_users,
            'role_distribution': role_stats,
            'recent_unique_logins': recent_logins,
            'recent_failed_logins': failed_logins,
            'active_sessions': active_sessions
        }
    
    def analyze_user(self, user, cutoff_date, security_focus):
        """Analyze individual user for security and activity"""
        user_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'is_publisher': user.is_publisher,
            'organization': user.organization.name if user.organization else 'None',
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'failed_login_attempts': user.failed_login_attempts,
            'is_locked': user.is_account_locked,
            'two_factor_enabled': user.two_factor_enabled,
            'trusted_devices_count': len(user.trusted_devices),
            'security_issues': []
        }
        
        # Activity analysis
        user_logs = user.auth_logs.filter(timestamp__gte=cutoff_date)
        
        user_data['activity'] = {
            'total_actions': user_logs.count(),
            'successful_logins': user_logs.filter(action='login_success').count(),
            'failed_logins': user_logs.filter(action='login_failed').count(),
            'password_changes': user_logs.filter(action='password_changed').count(),
            'unique_ips': user_logs.values('ip_address').distinct().count(),
            'last_activity': user_logs.order_by('-timestamp').first().timestamp.isoformat() if user_logs.exists() else None
        }
        
        # Active sessions
        active_sessions = user.sessions.filter(is_active=True)
        user_data['active_sessions'] = {
            'count': active_sessions.count(),
            'sessions': [
                {
                    'ip_address': session.ip_address,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'is_trusted': session.is_trusted_device
                }
                for session in active_sessions
            ]
        }
        
        # Security analysis
        if security_focus:
            user_data['security_issues'] = self.analyze_user_security(user, user_logs, cutoff_date)
        
        return user_data
    
    def analyze_user_security(self, user, user_logs, cutoff_date):
        """Analyze user for security issues"""
        issues = []
        
        # Check for unverified users
        if not user.is_verified and user.is_active:
            issues.append({
                'type': 'unverified_user',
                'severity': 'medium',
                'message': 'User is active but not verified by administrator',
                'user_id': str(user.id),
                'username': user.username
            })
        
        # Check for users with many failed login attempts
        if user.failed_login_attempts >= 3:
            issues.append({
                'type': 'multiple_failed_logins',
                'severity': 'high' if user.failed_login_attempts >= 5 else 'medium',
                'message': f'User has {user.failed_login_attempts} failed login attempts',
                'user_id': str(user.id),
                'username': user.username
            })
        
        # Check for inactive users with active sessions
        if not user.is_active:
            active_sessions = user.sessions.filter(is_active=True).count()
            if active_sessions > 0:
                issues.append({
                    'type': 'inactive_user_active_sessions',
                    'severity': 'high',
                    'message': f'Inactive user has {active_sessions} active sessions',
                    'user_id': str(user.id),
                    'username': user.username
                })
        
        # Check for users without 2FA (for high-privilege roles)
        if user.role in ['admin', 'system_admin'] and not user.two_factor_enabled:
            issues.append({
                'type': 'high_privilege_no_2fa',
                'severity': 'high',
                'message': 'High-privilege user without two-factor authentication',
                'user_id': str(user.id),
                'username': user.username
            })
        
        # Check for suspicious login patterns
        failed_logins = user_logs.filter(action='login_failed')
        if failed_logins.count() > 10:
            unique_ips = failed_logins.values('ip_address').distinct().count()
            if unique_ips > 3:
                issues.append({
                    'type': 'suspicious_login_pattern',
                    'severity': 'high',
                    'message': f'Multiple failed logins from {unique_ips} different IPs',
                    'user_id': str(user.id),
                    'username': user.username
                })
        
        # Check for old passwords (no recent password changes)
        last_password_change = user_logs.filter(action='password_changed').order_by('-timestamp').first()
        if not last_password_change:
            # Check account age
            account_age = timezone.now() - user.created_at
            if account_age.days > 90:  # No password change in 90+ days
                issues.append({
                    'type': 'old_password',
                    'severity': 'medium',
                    'message': 'No password change detected in recent history',
                    'user_id': str(user.id),
                    'username': user.username
                })
        
        # Check for users with too many trusted devices
        if len(user.trusted_devices) > 5:
            issues.append({
                'type': 'too_many_trusted_devices',
                'severity': 'medium',
                'message': f'User has {len(user.trusted_devices)} trusted devices',
                'user_id': str(user.id),
                'username': user.username
            })
        
        return issues
    
    def generate_recommendations(self, audit_data):
        """Generate security recommendations based on audit findings"""
        recommendations = []
        
        # Analyze security issues
        issue_types = {}
        for issue in audit_data['security_issues']:
            issue_type = issue['type']
            if issue_type not in issue_types:
                issue_types[issue_type] = 0
            issue_types[issue_type] += 1
        
        # Generate recommendations based on findings
        if issue_types.get('unverified_user', 0) > 0:
            recommendations.append({
                'type': 'process_improvement',
                'priority': 'high',
                'title': 'Verify Unverified Users',
                'description': f'There are {issue_types["unverified_user"]} unverified but active users. Review and verify these accounts or deactivate them.',
                'action_items': [
                    'Review unverified user accounts',
                    'Implement automated verification reminders',
                    'Consider auto-deactivation policy for unverified accounts'
                ]
            })
        
        if issue_types.get('high_privilege_no_2fa', 0) > 0:
            recommendations.append({
                'type': 'security_enhancement',
                'priority': 'critical',
                'title': 'Enforce 2FA for High-Privilege Users',
                'description': f'{issue_types["high_privilege_no_2fa"]} high-privilege users do not have 2FA enabled.',
                'action_items': [
                    'Mandate 2FA for admin and system_admin roles',
                    'Provide 2FA setup guidance and support',
                    'Implement policy enforcement for new admin users'
                ]
            })
        
        if issue_types.get('suspicious_login_pattern', 0) > 0:
            recommendations.append({
                'type': 'security_monitoring',
                'priority': 'high',
                'title': 'Investigate Suspicious Login Patterns',
                'description': f'{issue_types["suspicious_login_pattern"]} users show suspicious login patterns.',
                'action_items': [
                    'Investigate users with multiple failed logins from different IPs',
                    'Consider implementing IP-based restrictions',
                    'Enhance monitoring and alerting for brute force attempts'
                ]
            })
        
        # General recommendations
        if audit_data['summary']['locked_users'] > 0:
            recommendations.append({
                'type': 'account_management',
                'priority': 'medium',
                'title': 'Review Locked Accounts',
                'description': f'There are {audit_data["summary"]["locked_users"]} locked user accounts.',
                'action_items': [
                    'Review locked accounts for legitimate unlock requests',
                    'Investigate causes of account lockouts',
                    'Consider adjusting lockout policies if needed'
                ]
            })
        
        return recommendations
    
    def output_text_report(self, audit_data, export_file=None):
        """Output audit report in text format"""
        output_lines = []
        
        # Header
        output_lines.append("=" * 80)
        output_lines.append("CRISP USER SECURITY AUDIT REPORT")
        output_lines.append("=" * 80)
        output_lines.append(f"Generated: {audit_data['generated_at']}")
        output_lines.append(f"Period: Last {audit_data['period_days']} days")
        output_lines.append("")
        
        # Summary
        summary = audit_data['summary']
        output_lines.append("SUMMARY STATISTICS")
        output_lines.append("-" * 40)
        output_lines.append(f"Total Users: {summary['total_users']}")
        output_lines.append(f"Active Users: {summary['active_users']}")
        output_lines.append(f"Verified Users: {summary['verified_users']}")
        output_lines.append(f"Locked Users: {summary['locked_users']}")
        output_lines.append(f"Recent Unique Logins: {summary['recent_unique_logins']}")
        output_lines.append(f"Recent Failed Logins: {summary['recent_failed_logins']}")
        output_lines.append(f"Active Sessions: {summary['active_sessions']}")
        output_lines.append("")
        
        # Role distribution
        output_lines.append("ROLE DISTRIBUTION")
        output_lines.append("-" * 40)
        for role, count in summary['role_distribution'].items():
            output_lines.append(f"{role}: {count}")
        output_lines.append("")
        
        # Security issues
        if audit_data['security_issues']:
            output_lines.append("SECURITY ISSUES")
            output_lines.append("-" * 40)
            for issue in audit_data['security_issues']:
                output_lines.append(f"[{issue['severity'].upper()}] {issue['username']}: {issue['message']}")
            output_lines.append("")
        
        # Recommendations
        if audit_data['recommendations']:
            output_lines.append("RECOMMENDATIONS")
            output_lines.append("-" * 40)
            for rec in audit_data['recommendations']:
                output_lines.append(f"[{rec['priority'].upper()}] {rec['title']}")
                output_lines.append(f"  {rec['description']}")
                for action in rec['action_items']:
                    output_lines.append(f"  - {action}")
                output_lines.append("")
        
        # Output to file or stdout
        report_text = "\n".join(output_lines)
        
        if export_file:
            with open(export_file, 'w') as f:
                f.write(report_text)
            self.stdout.write(f"Report exported to: {export_file}")
        else:
            self.stdout.write(report_text)
    
    def output_json_report(self, audit_data, export_file=None):
        """Output audit report in JSON format"""
        import json
        
        json_output = json.dumps(audit_data, indent=2, default=str)
        
        if export_file:
            with open(export_file, 'w') as f:
                f.write(json_output)
            self.stdout.write(f"JSON report exported to: {export_file}")
        else:
            self.stdout.write(json_output)
    
    def output_csv_report(self, audit_data, export_file=None):
        """Output audit report in CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write user data
        writer.writerow([
            'Username', 'Email', 'Role', 'Active', 'Verified', 'Publisher',
            'Organization', 'Created', 'Last Login', 'Failed Attempts',
            'Locked', '2FA Enabled', 'Trusted Devices', 'Security Issues'
        ])
        
        for user in audit_data['users']:
            writer.writerow([
                user['username'],
                user['email'],
                user['role'],
                user['is_active'],
                user['is_verified'],
                user['is_publisher'],
                user['organization'],
                user['created_at'],
                user['last_login'] or 'Never',
                user['failed_login_attempts'],
                user['is_locked'],
                user['two_factor_enabled'],
                user['trusted_devices_count'],
                len(user['security_issues'])
            ])
        
        csv_content = output.getvalue()
        
        if export_file:
            with open(export_file, 'w') as f:
                f.write(csv_content)
            self.stdout.write(f"CSV report exported to: {export_file}")
        else:
            self.stdout.write(csv_content)