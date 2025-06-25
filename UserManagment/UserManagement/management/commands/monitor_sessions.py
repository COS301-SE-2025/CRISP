from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from UserManagement.models import UserSession, CustomUser
from UserManagement.services.session_service import SessionManagementService


class Command(BaseCommand):
    help = 'Monitor and display user session information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Show sessions for specific username only'
        )
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active sessions'
        )
        parser.add_argument(
            '--expired-only',
            action='store_true',
            help='Show only expired sessions'
        )
        parser.add_argument(
            '--recent-hours',
            type=int,
            default=24,
            help='Show sessions with activity in last N hours (default: 24)'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed session information'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Watch mode - refresh every 30 seconds'
        )

    def handle(self, *args, **options):
        if options['watch']:
            self._watch_mode(options)
        else:
            self._single_display(options)

    def _single_display(self, options):
        """Single session display"""
        self.stdout.write(
            self.style.SUCCESS('📊 CRISP Session Monitor')
        )
        self.stdout.write('=' * 60)
        
        self._show_session_overview(options)
        self._show_session_details(options)

    def _watch_mode(self, options):
        """Watch mode with periodic refresh"""
        import time
        import os
        
        self.stdout.write(
            self.style.SUCCESS('👀 CRISP Session Monitor - Watch Mode')
        )
        self.stdout.write('Press Ctrl+C to exit')
        
        try:
            while True:
                # Clear screen (works on most terminals)
                os.system('clear' if os.name == 'posix' else 'cls')
                
                self.stdout.write(
                    self.style.SUCCESS(f'📊 CRISP Session Monitor - {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
                )
                self.stdout.write('=' * 60)
                
                self._show_session_overview(options)
                self._show_session_details(options)
                
                self.stdout.write('\n⏰ Refreshing in 30 seconds... (Press Ctrl+C to exit)')
                time.sleep(30)
                
        except KeyboardInterrupt:
            self.stdout.write('\n\n👋 Exiting watch mode')

    def _show_session_overview(self, options):
        """Show session statistics overview"""
        try:
            # Get base queryset
            queryset = UserSession.objects.all()
            
            if options['username']:
                try:
                    user = CustomUser.objects.get(username=options['username'])
                    queryset = queryset.filter(user=user)
                    self.stdout.write(f"🎯 Filtering for user: {options['username']}")
                except CustomUser.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"❌ User not found: {options['username']}")
                    )
                    return

            # Calculate statistics
            total_sessions = queryset.count()
            active_sessions = queryset.filter(is_active=True).count()
            
            # Expired sessions
            expired_sessions = queryset.filter(
                expires_at__lt=timezone.now(),
                is_active=True
            ).count()
            
            # Recent activity
            recent_cutoff = timezone.now() - timedelta(hours=options['recent_hours'])
            recent_sessions = queryset.filter(
                last_activity__gte=recent_cutoff,
                is_active=True
            ).count()
            
            # Trusted devices
            trusted_sessions = queryset.filter(
                is_trusted_device=True,
                is_active=True
            ).count()

            # Display overview
            self.stdout.write('\n📈 Session Overview:')
            self.stdout.write(f'  📊 Total Sessions: {total_sessions}')
            self.stdout.write(f'  ✅ Active Sessions: {active_sessions}')
            self.stdout.write(f'  ❌ Inactive Sessions: {total_sessions - active_sessions}')
            self.stdout.write(f'  ⏰ Expired Sessions: {expired_sessions}')
            self.stdout.write(f'  🔥 Recent Activity ({options["recent_hours"]}h): {recent_sessions}')
            self.stdout.write(f'  🛡️  Trusted Device Sessions: {trusted_sessions}')

            # Show unique users if not filtering by username
            if not options['username']:
                unique_users = queryset.filter(is_active=True).values('user').distinct().count()
                self.stdout.write(f'  👥 Unique Active Users: {unique_users}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error getting overview: {str(e)}')
            )

    def _show_session_details(self, options):
        """Show detailed session information"""
        try:
            # Get sessions based on options
            queryset = UserSession.objects.all()
            
            if options['username']:
                try:
                    user = CustomUser.objects.get(username=options['username'])
                    queryset = queryset.filter(user=user)
                except CustomUser.DoesNotExist:
                    return

            if options['active_only']:
                queryset = queryset.filter(is_active=True)
                title = '✅ Active Sessions'
            elif options['expired_only']:
                queryset = queryset.filter(expires_at__lt=timezone.now(), is_active=True)
                title = '⏰ Expired Sessions'
            else:
                title = '📋 All Sessions'

            # Order by most recent activity
            sessions = queryset.order_by('-last_activity')[:20]  # Limit to 20 most recent

            if not sessions.exists():
                self.stdout.write(f'\n{title}:')
                self.stdout.write('  No sessions found matching criteria')
                return

            self.stdout.write(f'\n{title}:')
            
            if options['detailed']:
                self._show_detailed_sessions(sessions)
            else:
                self._show_summary_sessions(sessions)

            # Show if there are more sessions
            total_matching = queryset.count()
            if total_matching > 20:
                self.stdout.write(f'  ... and {total_matching - 20} more sessions')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error getting session details: {str(e)}')
            )

    def _show_summary_sessions(self, sessions):
        """Show sessions in summary format"""
        self.stdout.write('  ' + '-' * 80)
        self.stdout.write('  {:<20} {:<15} {:<10} {:<20} {:<10}'.format(
            'Username', 'IP Address', 'Status', 'Last Activity', 'Trusted'
        ))
        self.stdout.write('  ' + '-' * 80)
        
        for session in sessions:
            # Status
            if not session.is_active:
                status = '❌ Inactive'
            elif session.is_expired:
                status = '⏰ Expired'
            else:
                status = '✅ Active'
            
            # Last activity
            time_diff = timezone.now() - session.last_activity
            if time_diff.total_seconds() < 3600:  # Less than 1 hour
                activity = f'{int(time_diff.total_seconds() / 60)}m ago'
            elif time_diff.total_seconds() < 86400:  # Less than 1 day
                activity = f'{int(time_diff.total_seconds() / 3600)}h ago'
            else:
                activity = f'{int(time_diff.days)}d ago'
            
            # Trusted device
            trusted = '🛡️  Yes' if session.is_trusted_device else '❌ No'
            
            self.stdout.write('  {:<20} {:<15} {:<10} {:<20} {:<10}'.format(
                session.user.username[:19],
                session.ip_address,
                status[:9],
                activity,
                trusted[:9]
            ))

    def _show_detailed_sessions(self, sessions):
        """Show sessions in detailed format"""
        for i, session in enumerate(sessions, 1):
            self.stdout.write(f'\n  📍 Session {i}:')
            self.stdout.write(f'    👤 User: {session.user.username}')
            self.stdout.write(f'    📧 Email: {session.user.email}')
            self.stdout.write(f'    🏢 Organization: {session.user.organization.name if session.user.organization else "N/A"}')
            self.stdout.write(f'    🌐 IP Address: {session.ip_address}')
            
            # Status with details
            if not session.is_active:
                status = '❌ Inactive'
            elif session.is_expired:
                status = f'⏰ Expired (since {session.expires_at.strftime("%Y-%m-%d %H:%M")})'
            else:
                expires_in = session.expires_at - timezone.now()
                if expires_in.total_seconds() < 3600:
                    expires_str = f'{int(expires_in.total_seconds() / 60)}m'
                else:
                    expires_str = f'{int(expires_in.total_seconds() / 3600)}h'
                status = f'✅ Active (expires in {expires_str})'
            
            self.stdout.write(f'    📊 Status: {status}')
            self.stdout.write(f'    🛡️  Trusted Device: {"Yes" if session.is_trusted_device else "No"}')
            self.stdout.write(f'    ⏰ Created: {session.created_at.strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write(f'    🔄 Last Activity: {session.last_activity.strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write(f'    ⌛ Expires: {session.expires_at.strftime("%Y-%m-%d %H:%M:%S")}')
            
            # Device info if available
            if session.device_info:
                device_info = session.device_info
                if isinstance(device_info, dict):
                    if 'browser' in device_info:
                        self.stdout.write(f'    🌐 Browser: {device_info.get("browser", "Unknown")}')
                    if 'os' in device_info:
                        self.stdout.write(f'    💻 OS: {device_info.get("os", "Unknown")}')
            
            self.stdout.write(f'    🔑 Session ID: {session.id}')

    def _get_session_health_check(self):
        """Get session health indicators"""
        now = timezone.now()
        
        # Sessions that should be cleaned up
        expired_active = UserSession.objects.filter(
            expires_at__lt=now,
            is_active=True
        ).count()
        
        # Sessions inactive for more than 24 hours
        inactive_cutoff = now - timedelta(hours=24)
        long_inactive = UserSession.objects.filter(
            last_activity__lt=inactive_cutoff,
            is_active=True
        ).count()
        
        # Recently created sessions (last hour)
        recent_cutoff = now - timedelta(hours=1)
        recent_logins = UserSession.objects.filter(
            created_at__gte=recent_cutoff
        ).count()
        
        return {
            'expired_active': expired_active,
            'long_inactive': long_inactive,
            'recent_logins': recent_logins
        }