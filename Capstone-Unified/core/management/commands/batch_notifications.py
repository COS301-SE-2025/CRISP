"""
Management command for batch notification operations
"""

from django.core.management.base import BaseCommand
from core.services.batch_notification_service import batch_notification_service


class Command(BaseCommand):
    help = 'Manage batch notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-all',
            action='store_true',
            help='Force send all pending batch notifications',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show status of pending batch notifications',
        )

    def handle(self, *args, **options):
        if options['send_all']:
            self.stdout.write('Forcing send of all pending batch notifications...')
            batch_notification_service.force_send_all_batches()
            self.stdout.write(
                self.style.SUCCESS('All pending batch notifications sent')
            )
        
        if options['status']:
            pending = batch_notification_service.get_pending_batches()
            
            if not pending:
                self.stdout.write('No pending batch notifications')
            else:
                self.stdout.write(f'Pending batch notifications: {len(pending)}')
                for feed_id, batch_info in pending.items():
                    self.stdout.write(
                        f"  Feed: {batch_info['feed_name']}\n"
                        f"    New indicators: {batch_info['new_indicators']}\n"
                        f"    Updated indicators: {batch_info['updated_indicators']}\n"
                        f"    First change: {batch_info['first_change_time']}\n"
                        f"    Last change: {batch_info['last_change_time']}"
                    )
        
        if not options['send_all'] and not options['status']:
            self.stdout.write('Use --help to see available options')