"""
MITRE ATT&CK Integration Service - Pulls real TTP data from MITRE ATT&CK framework
"""
import json
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction

from core.models.models import ThreatFeed, TTPData, SystemActivity

logger = logging.getLogger(__name__)


class MITREIntegrationService:
    """Service for integrating with MITRE ATT&CK framework"""

    def __init__(self):
        self.mitre_enterprise_url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        self.mitre_mobile_url = "https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json"
        self.mitre_ics_url = "https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json"

    def sync_mitre_enterprise_data(self, threat_feed: ThreatFeed) -> Dict[str, Any]:
        """
        Sync MITRE ATT&CK Enterprise data from the official GitHub repository

        Args:
            threat_feed: ThreatFeed to store the MITRE data

        Returns:
            Dictionary containing sync results
        """
        results = {
            'feed_name': threat_feed.name,
            'sync_timestamp': timezone.now().isoformat(),
            'success': False,
            'techniques_synced': 0,
            'tactics_synced': 0,
            'existing_updated': 0,
            'new_created': 0,
            'errors': []
        }

        try:
            # Download MITRE ATT&CK Enterprise data
            logger.info(f"Downloading MITRE ATT&CK Enterprise data from {self.mitre_enterprise_url}")
            response = requests.get(self.mitre_enterprise_url, timeout=30)
            response.raise_for_status()

            mitre_data = response.json()

            # Extract objects from STIX bundle
            if 'objects' not in mitre_data:
                results['errors'].append('Invalid MITRE data format - no objects found')
                return results

            # Process attack patterns (techniques)
            techniques = [obj for obj in mitre_data['objects'] if obj.get('type') == 'attack-pattern']
            tactics = [obj for obj in mitre_data['objects'] if obj.get('type') == 'x-mitre-tactic']

            logger.info(f"Found {len(techniques)} techniques and {len(tactics)} tactics")

            with transaction.atomic():
                # Process techniques
                for technique in techniques:
                    try:
                        processed_ttp = self._process_mitre_technique(technique, threat_feed)
                        if processed_ttp:
                            if processed_ttp['action'] == 'created':
                                results['new_created'] += 1
                            elif processed_ttp['action'] == 'updated':
                                results['existing_updated'] += 1
                            results['techniques_synced'] += 1
                    except Exception as e:
                        logger.error(f"Error processing technique {technique.get('name', 'unknown')}: {str(e)}")
                        results['errors'].append(f"Technique {technique.get('name', 'unknown')}: {str(e)}")

                # Store tactic information for reference
                results['tactics_synced'] = len(tactics)

                # Update feed sync information
                threat_feed.last_sync = timezone.now()
                threat_feed.sync_count = threat_feed.sync_count + 1
                threat_feed.last_error = None
                threat_feed.save()

                results['success'] = True

                # Log the sync activity
                SystemActivity.objects.create(
                    activity_type='mitre_sync',
                    category='threat_feed',
                    title=f'MITRE ATT&CK sync completed for {threat_feed.name}',
                    description=f'Synced {results["techniques_synced"]} techniques, {results["new_created"]} new, {results["existing_updated"]} updated',
                    threat_feed=threat_feed,
                    metadata=results
                )

                logger.info(f"MITRE sync completed: {results['techniques_synced']} techniques synced")

        except requests.RequestException as e:
            error_msg = f"Failed to download MITRE data: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)

            # Update feed error
            threat_feed.last_error = error_msg
            threat_feed.save()

        except Exception as e:
            error_msg = f"Unexpected error during MITRE sync: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)

            # Update feed error
            threat_feed.last_error = error_msg
            threat_feed.save()

        return results

    def _process_mitre_technique(self, technique: Dict[str, Any], threat_feed: ThreatFeed) -> Optional[Dict[str, Any]]:
        """
        Process a single MITRE technique and create/update TTP record

        Args:
            technique: MITRE technique object from STIX data
            threat_feed: ThreatFeed to associate with the TTP

        Returns:
            Dictionary containing processing result
        """
        try:
            # Extract technique information
            technique_id = self._extract_mitre_id(technique)
            if not technique_id:
                return None

            name = technique.get('name', f'MITRE Technique {technique_id}')
            description = technique.get('description', '')

            # Extract tactics from kill chain phases
            tactics = self._extract_tactics(technique)
            primary_tactic = tactics[0] if tactics else 'unknown'

            # Extract additional metadata
            creation_date = technique.get('created', timezone.now().isoformat())
            modified_date = technique.get('modified', creation_date)

            # Check if TTP already exists (check both by technique ID and STIX ID to avoid duplicates)
            stix_id = technique.get('id')
            existing_ttp = TTPData.objects.filter(
                mitre_technique_id=technique_id,
                threat_feed=threat_feed
            ).first()

            # Also check for STIX ID conflicts across all feeds
            if stix_id and not existing_ttp:
                stix_conflict = TTPData.objects.filter(stix_id=stix_id).first()
                if stix_conflict:
                    # Skip this technique due to STIX ID conflict
                    logger.warning(f"Skipping {technique_id} due to STIX ID conflict: {stix_id}")
                    return None

            if existing_ttp:
                # Update existing TTP
                existing_ttp.name = name
                existing_ttp.description = description
                existing_ttp.mitre_tactic = primary_tactic
                existing_ttp.updated_at = timezone.now()

                # Update STIX ID if not set
                if not existing_ttp.stix_id:
                    existing_ttp.stix_id = technique.get('id')

                existing_ttp.save()

                return {
                    'action': 'updated',
                    'technique_id': technique_id,
                    'name': name,
                    'ttp_id': existing_ttp.id
                }
            else:
                # Create new TTP
                new_ttp = TTPData.objects.create(
                    name=name,
                    description=description[:5000],  # Truncate if too long
                    mitre_technique_id=technique_id,
                    mitre_tactic=primary_tactic,
                    threat_feed=threat_feed,
                    stix_id=technique.get('id'),
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )

                return {
                    'action': 'created',
                    'technique_id': technique_id,
                    'name': name,
                    'ttp_id': new_ttp.id
                }

        except Exception as e:
            logger.error(f"Error processing technique {technique.get('name', 'unknown')}: {str(e)}")
            raise

    def _extract_mitre_id(self, technique: Dict[str, Any]) -> Optional[str]:
        """Extract MITRE technique ID from external references"""
        external_refs = technique.get('external_references', [])

        for ref in external_refs:
            if ref.get('source_name') == 'mitre-attack':
                return ref.get('external_id')

        return None

    def _extract_tactics(self, technique: Dict[str, Any]) -> List[str]:
        """Extract tactics from kill chain phases"""
        kill_chain_phases = technique.get('kill_chain_phases', [])
        tactics = []

        for phase in kill_chain_phases:
            if phase.get('kill_chain_name') == 'mitre-attack':
                tactic = phase.get('phase_name')
                if tactic:
                    # Convert to our tactic format
                    normalized_tactic = tactic.replace('-', '_')
                    tactics.append(normalized_tactic)

        return tactics

    def get_mitre_technique_details(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific MITRE technique

        Args:
            technique_id: MITRE technique ID (e.g., T1055)

        Returns:
            Dictionary containing technique details or None if not found
        """
        try:
            # This could be enhanced to use the MITRE ATT&CK API when available
            # For now, we'll return details from our database
            ttp = TTPData.objects.filter(mitre_technique_id=technique_id).first()

            if ttp:
                return {
                    'technique_id': ttp.mitre_technique_id,
                    'name': ttp.name,
                    'description': ttp.description,
                    'tactic': ttp.mitre_tactic,
                    'url': f'https://attack.mitre.org/techniques/{technique_id.replace(".", "/")}/',
                    'last_updated': ttp.updated_at.isoformat() if ttp.updated_at else None
                }

            return None

        except Exception as e:
            logger.error(f"Error getting MITRE technique details for {technique_id}: {str(e)}")
            return None

    def sync_all_mitre_feeds(self) -> Dict[str, Any]:
        """
        Sync all MITRE-related threat feeds

        Returns:
            Dictionary containing overall sync results
        """
        results = {
            'total_feeds_synced': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'total_techniques': 0,
            'sync_timestamp': timezone.now().isoformat(),
            'feed_results': []
        }

        # Find all MITRE feeds
        mitre_feeds = ThreatFeed.objects.filter(
            name__icontains='MITRE',
            is_active=True
        )

        for feed in mitre_feeds:
            logger.info(f"Syncing MITRE feed: {feed.name}")

            try:
                feed_result = self.sync_mitre_enterprise_data(feed)
                results['feed_results'].append(feed_result)
                results['total_feeds_synced'] += 1

                if feed_result['success']:
                    results['successful_syncs'] += 1
                    results['total_techniques'] += feed_result['techniques_synced']
                else:
                    results['failed_syncs'] += 1

            except Exception as e:
                logger.error(f"Error syncing feed {feed.name}: {str(e)}")
                results['failed_syncs'] += 1
                results['feed_results'].append({
                    'feed_name': feed.name,
                    'success': False,
                    'error': str(e)
                })

        # Log overall sync activity
        SystemActivity.objects.create(
            activity_type='bulk_mitre_sync',
            category='system',
            title='Bulk MITRE ATT&CK sync completed',
            description=f'Synced {results["total_feeds_synced"]} MITRE feeds, {results["total_techniques"]} techniques total',
            metadata=results
        )

        return results

    def validate_mitre_data_freshness(self) -> Dict[str, Any]:
        """
        Check if MITRE data needs updating based on last sync time

        Returns:
            Dictionary containing freshness validation results
        """
        validation_results = {
            'needs_update': [],
            'up_to_date': [],
            'never_synced': [],
            'recommendations': []
        }

        mitre_feeds = ThreatFeed.objects.filter(
            name__icontains='MITRE',
            is_active=True
        )

        for feed in mitre_feeds:
            if not feed.last_sync:
                validation_results['never_synced'].append({
                    'feed_name': feed.name,
                    'recommendation': 'Run initial sync immediately'
                })
            else:
                hours_since_sync = (timezone.now() - feed.last_sync).total_seconds() / 3600

                if hours_since_sync > feed.sync_interval_hours:
                    validation_results['needs_update'].append({
                        'feed_name': feed.name,
                        'hours_since_sync': round(hours_since_sync, 1),
                        'sync_interval': feed.sync_interval_hours,
                        'recommendation': f'Update recommended (last sync {round(hours_since_sync, 1)} hours ago)'
                    })
                else:
                    validation_results['up_to_date'].append({
                        'feed_name': feed.name,
                        'hours_since_sync': round(hours_since_sync, 1),
                        'next_sync_in': round(feed.sync_interval_hours - hours_since_sync, 1)
                    })

        # Generate recommendations
        if validation_results['never_synced']:
            validation_results['recommendations'].append(
                f"{len(validation_results['never_synced'])} MITRE feeds have never been synced - run initial sync"
            )

        if validation_results['needs_update']:
            validation_results['recommendations'].append(
                f"{len(validation_results['needs_update'])} MITRE feeds need updating"
            )

        return validation_results