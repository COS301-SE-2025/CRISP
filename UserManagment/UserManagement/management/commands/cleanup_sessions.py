from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from UserManagement.models import UserSession, AuthenticationLog
from UserManagement.services.session_service import SessionManagementService


class Command(BaseCommand):
    help = 'Clean up inactive and expired user sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without making changes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup of all expired sessions'
        )
        parser.add_argument(
            '--max-inactive-hours',
            type=int,
            default=24,
            help='Maximum hours of inactivity before marking session as inactive (default: 24)'
        )
        parser.add_argument(
            '--delete-old-sessions',
            action='store_true',
            help='Delete session records older than specified days'
        )
        parser.add_argument(
            '--days-to-keep',
            type=int,
            default=30,
            help='Days to keep old session records (default: 30)'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Clean up sessions for specific username only'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧹 CRISP Session Cleanup Tool')
        )
        self.stdout.write('=' * 50)

        session_service = SessionManagementService()
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No changes will be made')
            )

        # Get statistics before cleanup
        self.stdout.write('\n📊 Pre-cleanup Statistics:')
        self._show_session_stats()

        cleanup_results = {
            'expired_sessions': 0,
            'inactive_sessions': 0,
            'deleted_sessions': 0,
            'errors': 0
        }

        # 1. Clean up expired sessions
        self.stdout.write('\n1️⃣ Cleaning up expired sessions...')
        expired_result = self._cleanup_expired_sessions(session_service, options, dry_run)
        cleanup_results['expired_sessions'] = expired_result

        # 2. Mark inactive sessions
        self.stdout.write('\n2️⃣ Marking inactive sessions...')
        inactive_result = self._mark_inactive_sessions(options, dry_run)
        cleanup_results['inactive_sessions'] = inactive_result

        # 3. Delete old session records (if requested)
        if options['delete_old_sessions']:
            self.stdout.write('\n3️⃣ Deleting old session records...')
            deleted_result = self._delete_old_sessions(options, dry_run)
            cleanup_results['deleted_sessions'] = deleted_result

        # Show final statistics
        self.stdout.write('\n📊 Post-cleanup Statistics:')
        self._show_session_stats()

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ Cleanup Summary:'))
        self.stdout.write(f'  • Expired sessions cleaned: {cleanup_results["expired_sessions"]}')
        self.stdout.write(f'  • Inactive sessions marked: {cleanup_results["inactive_sessions"]}')
        if options['delete_old_sessions']:
            self.stdout.write(f'  • Old sessions deleted: {cleanup_results["deleted_sessions"]}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  This was a dry run. Run without --dry-run to apply changes.')
            )

    def _show_session_stats(self):
        """Show current session statistics"""
        try:
            # Current sessions
            total_sessions = UserSession.objects.count()
            active_sessions = UserSession.objects.filter(is_active=True).count()
            
            # Expired sessions
            expired_sessions = UserSession.objects.filter(
                expires_at__lt=timezone.now(),
                is_active=True
            ).count()
            
            # Inactive sessions (no activity in 24 hours)
            inactive_cutoff = timezone.now() - timedelta(hours=24)
            inactive_sessions = UserSession.objects.filter(
                last_activity__lt=inactive_cutoff,
                is_active=True
            ).count()
            
            # Recent activity
            recent_cutoff = timezone.now() - timedelta(hours=1)
            recent_activity = UserSession.objects.filter(
                last_activity__gte=recent_cutoff,
                is_active=True
            ).count()

            self.stdout.write(f'  📈 Total sessions: {total_sessions}')
            self.stdout.write(f'  ✅ Active sessions: {active_sessions}')
            self.stdout.write(f'  ⏰ Expired sessions: {expired_sessions}')
            self.stdout.write(f'  😴 Inactive sessions (24h+): {inactive_sessions}')
            self.stdout.write(f'  🔥 Recent activity (1h): {recent_activity}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error getting statistics: {str(e)}')
            )

    def _cleanup_expired_sessions(self, session_service, options, dry_run):
        """Clean up expired sessions"""
        try:
            # Get target user if specified
            target_user = None
            if options['username']:
                from UserManagement.models import CustomUser
                try:
                    target_user = CustomUser.objects.get(username=options['username'])
                    self.stdout.write(f'  🎯 Targeting user: {target_user.username}')
                except CustomUser.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ User not found: {options["username"]}')
                    )
                    return 0

            # Find expired sessions
            expired_queryset = UserSession.objects.filter(
                expires_at__lt=timezone.now(),
                is_active=True
            )
            
            if target_user:
                expired_queryset = expired_queryset.filter(user=target_user)

            expired_count = expired_queryset.count()
            
            if expired_count == 0:
                self.stdout.write('  ✅ No expired sessions found')
                return 0

            self.stdout.write(f'  🔍 Found {expired_count} expired sessions')

            if not dry_run:
                # Use the service to clean up
                result = session_service.cleanup_expired_sessions(target_user)
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ {result["sessions_cleaned"]} expired sessions cleaned')
                    )
                    return result['sessions_cleaned']
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Cleanup failed: {result["message"]}')
                    )
                    return 0
            else:
                # Show what would be cleaned up
                for session in expired_queryset[:10]:  # Show first 10
                    self.stdout.write(
                        f'    → {session.user.username} - {session.ip_address} - '
                        f'expired {session.expires_at}'
                    )
                if expired_count > 10:
                    self.stdout.write(f'    ... and {expired_count - 10} more')
                return expired_count

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error cleaning expired sessions: {str(e)}')
            )
            return 0

    def _mark_inactive_sessions(self, options, dry_run):
        """Mark sessions as inactive based on last activity"""
        try:
            max_inactive_hours = options['max_inactive_hours']
            cutoff_time = timezone.now() - timedelta(hours=max_inactive_hours)
            
            # Find sessions with no activity beyond cutoff
            inactive_queryset = UserSession.objects.filter(
                last_activity__lt=cutoff_time,
                is_active=True,
                expires_at__gt=timezone.now()  # Not expired yet
            )
            
            if options['username']:
                from UserManagement.models import CustomUser
                try:
                    target_user = CustomUser.objects.get(username=options['username'])
                    inactive_queryset = inactive_queryset.filter(user=target_user)
                except CustomUser.DoesNotExist:
                    return 0

            inactive_count = inactive_queryset.count()
            
            if inactive_count == 0:
                self.stdout.write(f'  ✅ No inactive sessions found (>{max_inactive_hours}h)')
                return 0

            self.stdout.write(f'  🔍 Found {inactive_count} inactive sessions (>{max_inactive_hours}h)')

            if not dry_run:
                # Mark as inactive and log
                for session in inactive_queryset:
                    session.is_active = False
                    session.save(update_fields=['is_active'])
                    
                    # Log the automatic deactivation
                    AuthenticationLog.log_authentication_event(
                        user=session.user,
                        action='session_auto_deactivated',
                        ip_address=session.ip_address,
                        user_agent='System',
                        success=True,
                        additional_data={
                            'session_id': str(session.id),
                            'last_activity': session.last_activity.isoformat(),
                            'reason': f'inactive_for_{max_inactive_hours}_hours',
                            'auto_cleanup': True
                        }
                    )

                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ {inactive_count} sessions marked as inactive')
                )
                return inactive_count
            else:
                # Show what would be marked inactive
                for session in inactive_queryset[:10]:
                    self.stdout.write(
                        f'    → {session.user.username} - {session.ip_address} - '
                        f'last activity: {session.last_activity}'
                    )
                if inactive_count > 10:
                    self.stdout.write(f'    ... and {inactive_count - 10} more')
                return inactive_count

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error marking inactive sessions: {str(e)}')
            )
            return 0

    def _delete_old_sessions(self, options, dry_run):
        """Delete old session records"""
        try:
            days_to_keep = options['days_to_keep']
            cutoff_date = timezone.now() - timedelta(days=days_to_keep)
            
            old_queryset = UserSession.objects.filter(
                created_at__lt=cutoff_date,
                is_active=False
            )
            
            if options['username']:
                from UserManagement.models import CustomUser
                try:
                    target_user = CustomUser.objects.get(username=options['username'])
                    old_queryset = old_queryset.filter(user=target_user)
                except CustomUser.DoesNotExist:
                    return 0

            old_count = old_queryset.count()
            
            if old_count == 0:
                self.stdout.write(f'  ✅ No old sessions to delete (>{days_to_keep} days)')
                return 0

            self.stdout.write(f'  🔍 Found {old_count} old sessions (>{days_to_keep} days)')

            if not dry_run:
                deleted_count, _ = old_queryset.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ {deleted_count} old sessions deleted')
                )
                return deleted_count
            else:
                self.stdout.write(f'  🗑️  Would delete {old_count} old session records')
                return old_count

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error deleting old sessions: {str(e)}')
            )
            return 0