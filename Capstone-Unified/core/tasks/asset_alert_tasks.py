"""
Asset Alert Continuous Monitoring Tasks
Provides periodic and on-demand asset alert correlation and monitoring.
"""

import logging
import time
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from celery import shared_task
from settings.celery import app

from core.models.models import AssetInventory, Organization, Indicator, CustomAlert
from core.services.asset_alert_service import AssetBasedAlertService
from core.services.indicator_service import IndicatorService

logger = logging.getLogger(__name__)


@app.task(name='continuous_asset_monitoring', bind=True)
def continuous_asset_monitoring(self, hours_back=1):
    """
    Continuously monitor for new indicators and correlate with all organization assets.
    This task runs periodically to ensure real-time asset-based alerting.

    Args:
        hours_back (int): How many hours back to check for new indicators
    """
    task_id = self.request.id

    try:
        logger.info(f"Starting continuous asset monitoring (Task ID: {task_id})")

        # Set task status in cache
        task_key = f"asset_monitoring_task_{task_id}"
        cache.set(task_key, {
            'status': 'running',
            'start_time': timezone.now().isoformat(),
            'progress': 0
        }, timeout=3600)

        # Get recent indicators
        cutoff_time = timezone.now() - timedelta(hours=hours_back)
        recent_indicators = Indicator.objects.filter(
            created_at__gte=cutoff_time
        ).select_related('threat_feed').order_by('-created_at')

        if not recent_indicators.exists():
            logger.info("No recent indicators found for asset correlation")
            cache.set(task_key, {
                'status': 'completed',
                'message': 'No recent indicators to process',
                'completion_time': timezone.now().isoformat()
            }, timeout=3600)
            return {'status': 'completed', 'indicators_processed': 0, 'alerts_generated': 0}

        # Update progress
        cache.set(task_key, {
            'status': 'processing',
            'start_time': timezone.now().isoformat(),
            'progress': 25,
            'indicators_found': recent_indicators.count()
        }, timeout=3600)

        # Initialize service
        alert_service = AssetBasedAlertService()

        # Process indicators and generate alerts
        indicators_list = list(recent_indicators[:1000])  # Limit for performance
        logger.info(f"Processing {len(indicators_list)} recent indicators for asset correlation")

        cache.set(task_key, {
            'status': 'processing',
            'start_time': timezone.now().isoformat(),
            'progress': 50,
            'message': 'Correlating indicators with assets...'
        }, timeout=3600)

        # Process all indicators against all organizations
        generated_alerts = alert_service.process_new_indicators(indicators_list)

        # Update final status
        cache.set(task_key, {
            'status': 'completed',
            'completion_time': timezone.now().isoformat(),
            'progress': 100,
            'indicators_processed': len(indicators_list),
            'alerts_generated': len(generated_alerts)
        }, timeout=3600)

        logger.info(f"Continuous asset monitoring completed. Generated {len(generated_alerts)} alerts from {len(indicators_list)} indicators")

        return {
            'status': 'completed',
            'indicators_processed': len(indicators_list),
            'alerts_generated': len(generated_alerts),
            'execution_time_seconds': (timezone.now() - cutoff_time).total_seconds()
        }

    except Exception as e:
        logger.error(f"Error in continuous asset monitoring: {e}")
        if 'task_key' in locals():
            cache.set(task_key, {
                'status': 'failed',
                'error': str(e),
                'completion_time': timezone.now().isoformat()
            }, timeout=3600)
        raise


@app.task(name='sync_asset_inventory', bind=True)
def sync_asset_inventory(self, organization_id=None):
    """
    Sync and validate asset inventory for organizations.
    Updates asset fingerprints and ensures assets are ready for correlation.

    Args:
        organization_id (str): Optional specific organization ID to sync
    """
    task_id = self.request.id

    try:
        logger.info(f"Starting asset inventory sync (Task ID: {task_id})")

        task_key = f"asset_sync_task_{task_id}"
        cache.set(task_key, {
            'status': 'running',
            'start_time': timezone.now().isoformat(),
            'progress': 0
        }, timeout=3600)

        # Get organizations to sync
        if organization_id:
            organizations = Organization.objects.filter(id=organization_id, is_active=True)
        else:
            organizations = Organization.objects.filter(is_active=True)

        if not organizations.exists():
            logger.info("No organizations found for asset sync")
            return {'status': 'completed', 'organizations_processed': 0}

        total_orgs = organizations.count()
        processed_orgs = 0
        total_assets_updated = 0

        cache.set(task_key, {
            'status': 'processing',
            'start_time': timezone.now().isoformat(),
            'progress': 25,
            'total_organizations': total_orgs
        }, timeout=3600)

        for org in organizations:
            try:
                logger.info(f"Syncing assets for organization: {org.name}")

                # Get all assets for this organization
                assets = AssetInventory.objects.filter(organization=org)

                updated_count = 0
                for asset in assets:
                    try:
                        # Update asset fingerprints
                        old_fingerprints = asset.fingerprints
                        asset.generate_fingerprints()

                        # Update last_seen timestamp
                        asset.last_seen = timezone.now()
                        asset.save(update_fields=['fingerprints', 'last_seen', 'updated_at'])

                        # Log if fingerprints changed
                        if old_fingerprints != asset.fingerprints:
                            logger.debug(f"Updated fingerprints for asset {asset.name}")

                        updated_count += 1

                    except Exception as e:
                        logger.warning(f"Error updating asset {asset.name}: {e}")

                total_assets_updated += updated_count
                processed_orgs += 1

                # Update progress
                progress = 25 + (processed_orgs / total_orgs) * 75
                cache.set(task_key, {
                    'status': 'processing',
                    'start_time': timezone.now().isoformat(),
                    'progress': progress,
                    'organizations_processed': processed_orgs,
                    'current_organization': org.name,
                    'assets_updated': total_assets_updated
                }, timeout=3600)

                logger.info(f"Synced {updated_count} assets for {org.name}")

            except Exception as e:
                logger.error(f"Error syncing organization {org.name}: {e}")
                continue

        # Final status
        cache.set(task_key, {
            'status': 'completed',
            'completion_time': timezone.now().isoformat(),
            'progress': 100,
            'organizations_processed': processed_orgs,
            'total_assets_updated': total_assets_updated
        }, timeout=3600)

        logger.info(f"Asset inventory sync completed. Processed {processed_orgs} organizations, updated {total_assets_updated} assets")

        return {
            'status': 'completed',
            'organizations_processed': processed_orgs,
            'total_assets_updated': total_assets_updated
        }

    except Exception as e:
        logger.error(f"Error in asset inventory sync: {e}")
        if 'task_key' in locals():
            cache.set(task_key, {
                'status': 'failed',
                'error': str(e),
                'completion_time': timezone.now().isoformat()
            }, timeout=3600)
        raise


@app.task(name='process_organization_alerts', bind=True)
def process_organization_alerts(self, organization_id, hours_back=24):
    """
    Process alerts for a specific organization against recent indicators.

    Args:
        organization_id (str): Organization ID to process
        hours_back (int): Hours back to check for indicators
    """
    task_id = self.request.id

    try:
        logger.info(f"Processing alerts for organization {organization_id} (Task ID: {task_id})")

        task_key = f"org_alerts_task_{task_id}"
        cache.set(task_key, {
            'status': 'running',
            'start_time': timezone.now().isoformat(),
            'organization_id': organization_id,
            'progress': 0
        }, timeout=3600)

        # Get organization
        try:
            organization = Organization.objects.get(id=organization_id, is_active=True)
        except Organization.DoesNotExist:
            logger.error(f"Organization {organization_id} not found or not active")
            cache.set(task_key, {
                'status': 'failed',
                'error': 'Organization not found or not active'
            }, timeout=3600)
            return {'status': 'failed', 'error': 'Organization not found'}

        # Check if organization has alert-enabled assets
        asset_count = AssetInventory.objects.filter(
            organization=organization,
            alert_enabled=True
        ).count()

        if asset_count == 0:
            logger.info(f"No alert-enabled assets found for {organization.name}")
            cache.set(task_key, {
                'status': 'completed',
                'message': 'No alert-enabled assets found',
                'completion_time': timezone.now().isoformat()
            }, timeout=3600)
            return {'status': 'completed', 'alerts_generated': 0, 'reason': 'no_assets'}

        cache.set(task_key, {
            'status': 'processing',
            'start_time': timezone.now().isoformat(),
            'organization_name': organization.name,
            'asset_count': asset_count,
            'progress': 25
        }, timeout=3600)

        # Get recent indicators
        cutoff_time = timezone.now() - timedelta(hours=hours_back)
        recent_indicators = Indicator.objects.filter(
            created_at__gte=cutoff_time
        ).order_by('-created_at')[:500]  # Limit for performance

        if not recent_indicators:
            logger.info(f"No recent indicators found for {organization.name}")
            cache.set(task_key, {
                'status': 'completed',
                'message': 'No recent indicators to process',
                'completion_time': timezone.now().isoformat()
            }, timeout=3600)
            return {'status': 'completed', 'alerts_generated': 0, 'reason': 'no_indicators'}

        cache.set(task_key, {
            'status': 'processing',
            'start_time': timezone.now().isoformat(),
            'organization_name': organization.name,
            'indicators_found': len(recent_indicators),
            'progress': 50
        }, timeout=3600)

        # Process indicators for this organization
        alert_service = AssetBasedAlertService()
        generated_alerts = alert_service.process_indicators_for_organization(
            list(recent_indicators), organization
        )

        cache.set(task_key, {
            'status': 'completed',
            'completion_time': timezone.now().isoformat(),
            'organization_name': organization.name,
            'indicators_processed': len(recent_indicators),
            'alerts_generated': len(generated_alerts),
            'progress': 100
        }, timeout=3600)

        logger.info(f"Generated {len(generated_alerts)} alerts for {organization.name} from {len(recent_indicators)} indicators")

        return {
            'status': 'completed',
            'organization': organization.name,
            'indicators_processed': len(recent_indicators),
            'alerts_generated': len(generated_alerts)
        }

    except Exception as e:
        logger.error(f"Error processing alerts for organization {organization_id}: {e}")
        if 'task_key' in locals():
            cache.set(task_key, {
                'status': 'failed',
                'error': str(e),
                'completion_time': timezone.now().isoformat()
            }, timeout=3600)
        raise


@app.task(name='cleanup_old_alerts')
def cleanup_old_alerts(days_old=90, batch_size=100):
    """
    Clean up old alerts to prevent database bloat.

    Args:
        days_old (int): Delete alerts older than this many days
        batch_size (int): Number of alerts to delete in each batch
    """
    try:
        logger.info(f"Starting cleanup of alerts older than {days_old} days")

        cutoff_date = timezone.now() - timedelta(days=days_old)

        # Find alerts to delete
        old_alerts = CustomAlert.objects.filter(
            created_at__lt=cutoff_date
        ).order_by('created_at')

        total_count = old_alerts.count()
        if total_count == 0:
            logger.info("No old alerts found for cleanup")
            return {'status': 'completed', 'alerts_deleted': 0}

        deleted_count = 0

        # Delete in batches to avoid memory issues
        while old_alerts.exists():
            batch_ids = list(old_alerts.values_list('id', flat=True)[:batch_size])
            if not batch_ids:
                break

            with transaction.atomic():
                CustomAlert.objects.filter(id__in=batch_ids).delete()
                deleted_count += len(batch_ids)

            logger.info(f"Deleted {deleted_count}/{total_count} old alerts")

            # Brief pause to avoid overwhelming the database
            time.sleep(0.1)

        logger.info(f"Cleanup completed. Deleted {deleted_count} alerts older than {days_old} days")

        return {
            'status': 'completed',
            'alerts_deleted': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as e:
        logger.error(f"Error during alert cleanup: {e}")
        raise


@app.task(name='validate_asset_inventory')
def validate_asset_inventory(organization_id=None):
    """
    Validate asset inventory for consistency and generate warnings for issues.

    Args:
        organization_id (str): Optional specific organization to validate
    """
    try:
        logger.info("Starting asset inventory validation")

        # Get organizations to validate
        if organization_id:
            organizations = Organization.objects.filter(id=organization_id, is_active=True)
        else:
            organizations = Organization.objects.filter(is_active=True)

        validation_results = {
            'organizations_checked': 0,
            'total_assets': 0,
            'issues_found': [],
            'recommendations': []
        }

        for org in organizations:
            org_assets = AssetInventory.objects.filter(organization=org)
            validation_results['organizations_checked'] += 1
            validation_results['total_assets'] += org_assets.count()

            # Check for assets without alert enabled
            no_alert_assets = org_assets.filter(alert_enabled=False).count()
            if no_alert_assets > 0:
                validation_results['issues_found'].append({
                    'organization': org.name,
                    'type': 'alerts_disabled',
                    'count': no_alert_assets,
                    'description': f"{no_alert_assets} assets have alerts disabled"
                })

            # Check for assets without fingerprints
            no_fingerprint_assets = org_assets.filter(fingerprints__isnull=True).count()
            if no_fingerprint_assets > 0:
                validation_results['issues_found'].append({
                    'organization': org.name,
                    'type': 'missing_fingerprints',
                    'count': no_fingerprint_assets,
                    'description': f"{no_fingerprint_assets} assets missing fingerprints"
                })

            # Check for stale assets (not updated in 30 days)
            stale_cutoff = timezone.now() - timedelta(days=30)
            stale_assets = org_assets.filter(updated_at__lt=stale_cutoff).count()
            if stale_assets > 0:
                validation_results['issues_found'].append({
                    'organization': org.name,
                    'type': 'stale_assets',
                    'count': stale_assets,
                    'description': f"{stale_assets} assets not updated in 30+ days"
                })

            # Check for critical assets without monitoring
            unmonitored_critical = org_assets.filter(
                criticality='critical',
                alert_enabled=False
            ).count()
            if unmonitored_critical > 0:
                validation_results['issues_found'].append({
                    'organization': org.name,
                    'type': 'unmonitored_critical',
                    'count': unmonitored_critical,
                    'description': f"{unmonitored_critical} critical assets not monitored",
                    'severity': 'high'
                })

        # Generate recommendations
        if validation_results['issues_found']:
            validation_results['recommendations'] = [
                "Enable alerts on all critical and high-value assets",
                "Run asset sync to update missing fingerprints",
                "Review and update stale asset inventories",
                "Ensure all production assets are properly categorized"
            ]

        logger.info(f"Asset validation completed. Found {len(validation_results['issues_found'])} issues across {validation_results['organizations_checked']} organizations")

        return validation_results

    except Exception as e:
        logger.error(f"Error during asset validation: {e}")
        raise


# Periodic task scheduling helper
@app.task(name='schedule_asset_monitoring_tasks')
def schedule_asset_monitoring_tasks():
    """
    Schedule all asset monitoring related tasks.
    This is a meta-task that triggers other monitoring tasks.
    """
    try:
        logger.info("Scheduling asset monitoring tasks")

        # Schedule continuous monitoring
        continuous_asset_monitoring.delay(hours_back=1)

        # Schedule asset sync for all organizations
        sync_asset_inventory.delay()

        # Schedule validation
        validate_asset_inventory.delay()

        logger.info("Asset monitoring tasks scheduled successfully")

        return {
            'status': 'scheduled',
            'tasks': ['continuous_asset_monitoring', 'sync_asset_inventory', 'validate_asset_inventory']
        }

    except Exception as e:
        logger.error(f"Error scheduling asset monitoring tasks: {e}")
        raise


@app.task(name='emergency_asset_scan')
def emergency_asset_scan(threat_indicator_id=None, organization_id=None):
    """
    Emergency scan for immediate threat correlation with assets.
    Used when high-priority threats are detected.

    Args:
        threat_indicator_id (str): Specific threat indicator to check
        organization_id (str): Optional specific organization to scan
    """
    try:
        logger.info("Starting emergency asset scan")

        # Get the threat indicator
        if threat_indicator_id:
            try:
                indicator = Indicator.objects.get(id=threat_indicator_id)
                indicators = [indicator]
            except Indicator.DoesNotExist:
                logger.error(f"Threat indicator {threat_indicator_id} not found")
                return {'status': 'failed', 'error': 'Indicator not found'}
        else:
            # Use most recent high-confidence indicators
            indicators = list(Indicator.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).order_by('-created_at')[:10])

        if not indicators:
            logger.info("No indicators found for emergency scan")
            return {'status': 'completed', 'alerts_generated': 0}

        alert_service = AssetBasedAlertService()
        total_alerts = 0

        if organization_id:
            # Scan specific organization
            try:
                organization = Organization.objects.get(id=organization_id, is_active=True)
                alerts = alert_service.process_indicators_for_organization(indicators, organization)
                total_alerts = len(alerts)
                logger.info(f"Emergency scan for {organization.name}: {total_alerts} alerts generated")
            except Organization.DoesNotExist:
                return {'status': 'failed', 'error': 'Organization not found'}
        else:
            # Scan all organizations
            alerts = alert_service.process_new_indicators(indicators)
            total_alerts = len(alerts)
            logger.info(f"Emergency scan completed: {total_alerts} alerts generated across all organizations")

        return {
            'status': 'completed',
            'indicators_processed': len(indicators),
            'alerts_generated': total_alerts,
            'scan_type': 'emergency'
        }

    except Exception as e:
        logger.error(f"Error during emergency asset scan: {e}")
        raise