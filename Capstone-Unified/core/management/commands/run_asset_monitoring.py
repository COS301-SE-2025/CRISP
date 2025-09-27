"""
Management command to run asset monitoring tasks.
Provides both one-time and continuous monitoring capabilities.
"""

import time
import signal
import sys
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from core.tasks.asset_alert_tasks import (
    continuous_asset_monitoring,
    sync_asset_inventory,
    process_organization_alerts,
    validate_asset_inventory,
    emergency_asset_scan,
    cleanup_old_alerts
)
from core.models.models import Organization


class Command(BaseCommand):
    help = 'Run asset monitoring and alerting tasks'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.stdout.write(
                self.style.WARNING(f'Received signal {signum}. Shutting down gracefully...')
            )
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            choices=['once', 'continuous', 'emergency', 'sync', 'validate', 'cleanup'],
            default='once',
            help='Monitoring mode to run'
        )

        parser.add_argument(
            '--organization',
            type=str,
            help='Specific organization ID to process'
        )

        parser.add_argument(
            '--hours-back',
            type=int,
            default=1,
            help='Hours back to check for indicators (default: 1)'
        )

        parser.add_argument(
            '--interval',
            type=int,
            default=300,  # 5 minutes
            help='Interval in seconds for continuous mode (default: 300)'
        )

        parser.add_argument(
            '--max-iterations',
            type=int,
            default=0,
            help='Maximum iterations for continuous mode (0 = unlimited)'
        )

        parser.add_argument(
            '--cleanup-days',
            type=int,
            default=90,
            help='Days old for alert cleanup (default: 90)'
        )

        parser.add_argument(
            '--threat-indicator',
            type=str,
            help='Specific threat indicator ID for emergency scan'
        )

    def handle(self, *args, **options):
        mode = options['mode']

        self.stdout.write(
            self.style.SUCCESS(f'Starting asset monitoring in {mode} mode...')
        )

        try:
            if mode == 'once':
                self.run_once(options)
            elif mode == 'continuous':
                self.run_continuous(options)
            elif mode == 'emergency':
                self.run_emergency(options)
            elif mode == 'sync':
                self.run_sync(options)
            elif mode == 'validate':
                self.run_validate(options)
            elif mode == 'cleanup':
                self.run_cleanup(options)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Monitoring stopped by user.')
            )
        except Exception as e:
            raise CommandError(f'Asset monitoring failed: {e}')

    def run_once(self, options):
        """Run asset monitoring once"""
        hours_back = options['hours_back']
        organization_id = options.get('organization')

        self.stdout.write(f'Running one-time asset monitoring (last {hours_back} hours)...')

        if organization_id:
            # Process specific organization
            try:
                org = Organization.objects.get(id=organization_id)
                self.stdout.write(f'Processing organization: {org.name}')

                result = process_organization_alerts.delay(organization_id, hours_back)

                # Wait for completion and show results
                task_result = result.get(timeout=600)  # 10 minute timeout

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Generated {task_result.get("alerts_generated", 0)} alerts '
                        f'from {task_result.get("indicators_processed", 0)} indicators'
                    )
                )

            except Organization.DoesNotExist:
                raise CommandError(f'Organization with ID {organization_id} not found')

        else:
            # Process all organizations
            result = continuous_asset_monitoring.delay(hours_back)

            # Wait for completion and show results
            task_result = result.get(timeout=600)  # 10 minute timeout

            self.stdout.write(
                self.style.SUCCESS(
                    f'Generated {task_result.get("alerts_generated", 0)} alerts '
                    f'from {task_result.get("indicators_processed", 0)} indicators '
                    f'across all organizations'
                )
            )

    def run_continuous(self, options):
        """Run continuous asset monitoring"""
        interval = options['interval']
        max_iterations = options['max_iterations']
        hours_back = options['hours_back']

        self.stdout.write(
            f'Starting continuous monitoring (interval: {interval}s, hours back: {hours_back})'
        )

        iteration = 0

        while self.running:
            try:
                iteration += 1

                self.stdout.write(
                    f'[{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}] '
                    f'Running monitoring iteration {iteration}...'
                )

                # Run monitoring task
                result = continuous_asset_monitoring.delay(hours_back)

                # Don't wait for completion in continuous mode to avoid blocking
                # Just log that it was started
                self.stdout.write(f'Started monitoring task: {result.id}')

                # Check if we should stop
                if max_iterations > 0 and iteration >= max_iterations:
                    self.stdout.write(
                        self.style.SUCCESS(f'Completed {max_iterations} iterations.')
                    )
                    break

                # Wait for next iteration
                if self.running:
                    self.stdout.write(f'Waiting {interval} seconds until next iteration...')
                    for i in range(interval):
                        if not self.running:
                            break
                        time.sleep(1)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error in iteration {iteration}: {e}')
                )
                # Continue running even if one iteration fails
                time.sleep(interval)

    def run_emergency(self, options):
        """Run emergency asset scan"""
        threat_indicator = options.get('threat_indicator')
        organization_id = options.get('organization')

        self.stdout.write(
            self.style.WARNING('Running EMERGENCY asset scan...')
        )

        result = emergency_asset_scan.delay(
            threat_indicator_id=threat_indicator,
            organization_id=organization_id
        )

        # Wait for completion
        task_result = result.get(timeout=300)  # 5 minute timeout

        self.stdout.write(
            self.style.SUCCESS(
                f'Emergency scan completed. '
                f'Generated {task_result.get("alerts_generated", 0)} alerts '
                f'from {task_result.get("indicators_processed", 0)} indicators'
            )
        )

    def run_sync(self, options):
        """Run asset inventory sync"""
        organization_id = options.get('organization')

        self.stdout.write('Running asset inventory sync...')

        result = sync_asset_inventory.delay(organization_id)

        # Wait for completion
        task_result = result.get(timeout=600)  # 10 minute timeout

        self.stdout.write(
            self.style.SUCCESS(
                f'Asset sync completed. '
                f'Processed {task_result.get("organizations_processed", 0)} organizations, '
                f'updated {task_result.get("total_assets_updated", 0)} assets'
            )
        )

    def run_validate(self, options):
        """Run asset inventory validation"""
        organization_id = options.get('organization')

        self.stdout.write('Running asset inventory validation...')

        result = validate_asset_inventory.delay(organization_id)

        # Wait for completion
        task_result = result.get(timeout=300)  # 5 minute timeout

        issues = task_result.get('issues_found', [])

        self.stdout.write(
            self.style.SUCCESS(
                f'Validation completed. '
                f'Checked {task_result.get("organizations_checked", 0)} organizations, '
                f'found {len(issues)} issues'
            )
        )

        if issues:
            self.stdout.write(self.style.WARNING('Issues found:'))
            for issue in issues:
                severity = issue.get('severity', 'medium')
                style = self.style.ERROR if severity == 'high' else self.style.WARNING
                self.stdout.write(
                    style(f'  - {issue["organization"]}: {issue["description"]}')
                )

    def run_cleanup(self, options):
        """Run alert cleanup"""
        cleanup_days = options['cleanup_days']

        self.stdout.write(f'Running alert cleanup (older than {cleanup_days} days)...')

        result = cleanup_old_alerts.delay(cleanup_days)

        # Wait for completion
        task_result = result.get(timeout=600)  # 10 minute timeout

        self.stdout.write(
            self.style.SUCCESS(
                f'Cleanup completed. '
                f'Deleted {task_result.get("alerts_deleted", 0)} old alerts'
            )
        )