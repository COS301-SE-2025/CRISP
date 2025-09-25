"""
Asset-Based Alert Service for CRISP WOW Factor #1
Implements custom alert generation based on client asset inventories and IoC correlation.
"""

import logging
import uuid
import re
import ipaddress
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction, models
from django.contrib.auth import get_user_model

from core.models.models import AssetInventory, CustomAlert, Indicator, TTPData, Organization
from core.services.notification_service import NotificationService
from core.services.email_service import UnifiedEmailService
from core.services.indicator_service import IndicatorService
from core.services.multi_channel_alert_service import MultiChannelAlertService

User = get_user_model()
logger = logging.getLogger(__name__)


class AssetBasedAlertService:
    """
    Service for generating custom alerts based on IoC correlation with client asset inventories.
    Implements the WOW Factor #1 requirement for personalized threat intelligence.
    """

    def __init__(self):
        self.notification_service = NotificationService()
        self.email_service = UnifiedEmailService()
        self.indicator_service = IndicatorService()
        self.multi_channel_service = MultiChannelAlertService()

    def process_new_indicators(self, indicators: List[Indicator]) -> List[CustomAlert]:
        """
        Process new indicators and generate asset-based alerts for all organizations.

        Args:
            indicators: List of new indicators to process

        Returns:
            List of generated custom alerts
        """
        generated_alerts = []

        try:
            # Get all organizations with asset inventories
            orgs_with_assets = Organization.objects.filter(
                asset_inventory__alert_enabled=True,
                is_active=True
            ).distinct()

            logger.info(f"Processing {len(indicators)} indicators against {orgs_with_assets.count()} organizations")

            for organization in orgs_with_assets:
                org_alerts = self._process_indicators_for_organization(indicators, organization)
                generated_alerts.extend(org_alerts)

            logger.info(f"Generated {len(generated_alerts)} total custom alerts")
            return generated_alerts

        except Exception as e:
            logger.error(f"Error processing new indicators for asset correlation: {e}")
            return []

    def process_indicators_for_organization(self, indicators: List[Indicator],
                                          organization: Organization) -> List[CustomAlert]:
        """
        Public wrapper for processing indicators for a specific organization.

        Args:
            indicators: List of indicators to process
            organization: Target organization

        Returns:
            List of generated custom alerts
        """
        return self._process_indicators_for_organization(indicators, organization)

    def _process_indicators_for_organization(self, indicators: List[Indicator],
                                           organization: Organization) -> List[CustomAlert]:
        """
        Process indicators against a specific organization's asset inventory.

        Args:
            indicators: List of indicators to check
            organization: Organization to check against

        Returns:
            List of generated custom alerts
        """
        alerts = []

        try:
            # Get organization's assets with alert enabled
            assets = AssetInventory.objects.filter(
                organization=organization,
                alert_enabled=True
            ).select_related('organization')

            if not assets.exists():
                logger.debug(f"No alert-enabled assets found for organization {organization.name}")
                return []

            logger.debug(f"Checking {len(indicators)} indicators against {assets.count()} assets for {organization.name}")

            for indicator in indicators:
                matched_assets = self._correlate_indicator_with_assets(indicator, assets)

                if matched_assets:
                    alert = self._generate_custom_alert(
                        indicator=indicator,
                        matched_assets=matched_assets,
                        organization=organization
                    )
                    if alert:
                        alerts.append(alert)

            logger.info(f"Generated {len(alerts)} alerts for organization {organization.name}")
            return alerts

        except Exception as e:
            logger.error(f"Error processing indicators for organization {organization.name}: {e}")
            return []

    def _correlate_indicator_with_assets(self, indicator: Indicator,
                                       assets: List[AssetInventory]) -> List[AssetInventory]:
        """
        Correlate a single indicator with asset inventory to find matches.

        Args:
            indicator: Indicator to check
            assets: List of assets to check against

        Returns:
            List of matching assets
        """
        matched_assets = []

        try:
            # Extract relevant patterns from indicator
            indicator_patterns = self._extract_indicator_patterns(indicator)

            for asset in assets:
                if self._asset_matches_patterns(asset, indicator_patterns):
                    matched_assets.append(asset)
                    logger.debug(f"Asset {asset.name} matches indicator {indicator.id}")

            return matched_assets

        except Exception as e:
            logger.warning(f"Error correlating indicator {indicator.id} with assets: {e}")
            return []

    def _extract_indicator_patterns(self, indicator: Indicator) -> Dict[str, List[str]]:
        """
        Extract relevant patterns from an indicator for asset correlation.

        Args:
            indicator: Indicator to extract patterns from

        Returns:
            Dictionary of pattern types and values
        """
        patterns = {
            'ip_addresses': [],
            'domains': [],
            'urls': [],
            'file_hashes': [],
            'email_addresses': [],
            'software_names': []
        }

        try:
            # Extract from pattern field
            pattern_text = getattr(indicator, 'pattern', '') or ''
            value_text = getattr(indicator, 'value', '') or ''

            # Combine pattern and value for analysis
            combined_text = f"{pattern_text} {value_text}".lower()

            # IP addresses
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            patterns['ip_addresses'] = re.findall(ip_pattern, combined_text)

            # Domain names
            domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\b'
            patterns['domains'] = re.findall(domain_pattern, combined_text)

            # URLs
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            patterns['urls'] = re.findall(url_pattern, combined_text)

            # File hashes (MD5, SHA1, SHA256)
            hash_pattern = r'\b[a-f0-9]{32,64}\b'
            patterns['file_hashes'] = re.findall(hash_pattern, combined_text)

            # Email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            patterns['email_addresses'] = re.findall(email_pattern, combined_text)

            # Extract from indicator type and labels
            indicator_type = getattr(indicator, 'type', '') or ''
            labels = getattr(indicator, 'labels', []) or []

            # Add software patterns based on labels
            software_labels = [label for label in labels if 'software' in label.lower() or 'malware' in label.lower()]
            patterns['software_names'].extend(software_labels)

            # Remove duplicates and empty values
            for key in patterns:
                patterns[key] = list(set(filter(None, patterns[key])))

            logger.debug(f"Extracted patterns from indicator {indicator.id}: {patterns}")
            return patterns

        except Exception as e:
            logger.warning(f"Error extracting patterns from indicator {indicator.id}: {e}")
            return patterns

    def _asset_matches_patterns(self, asset: AssetInventory, patterns: Dict[str, List[str]]) -> bool:
        """
        Check if an asset matches any of the extracted patterns.

        Args:
            asset: Asset to check
            patterns: Dictionary of pattern types and values

        Returns:
            True if asset matches any pattern
        """
        try:
            asset_value = asset.asset_value.lower()
            asset_type = asset.asset_type

            # Check based on asset type
            if asset_type == 'ip_range':
                return self._check_ip_range_match(asset_value, patterns['ip_addresses'])

            elif asset_type in ['domain', 'subdomain', 'email_domain']:
                domains_and_urls = patterns.get('domains', []) + patterns.get('urls', [])
                return self._check_domain_match(asset_value, domains_and_urls)

            elif asset_type == 'software':
                return self._check_software_match(asset_value, patterns['software_names'])

            elif asset_type == 'service':
                # Check if service runs on targeted IPs or domains
                return (self._check_domain_match(asset_value, patterns['domains']) or
                        self._check_ip_range_match(asset_value, patterns['ip_addresses']))

            # For other asset types, do basic string matching
            for pattern_list in patterns.values():
                for pattern in pattern_list:
                    if pattern.lower() in asset_value or asset_value in pattern.lower():
                        return True

            return False

        except Exception as e:
            logger.warning(f"Error checking asset {asset.id} against patterns: {e}")
            return False

    def _check_ip_range_match(self, asset_ip_range: str, target_ips: List[str]) -> bool:
        """Check if any target IPs fall within asset IP range."""
        try:
            for target_ip in target_ips:
                try:
                    target_addr = ipaddress.ip_address(target_ip)

                    # Handle CIDR notation
                    if '/' in asset_ip_range:
                        asset_network = ipaddress.ip_network(asset_ip_range, strict=False)
                        if target_addr in asset_network:
                            return True

                    # Handle IP range (e.g., 192.168.1.1-192.168.1.100)
                    elif '-' in asset_ip_range:
                        start_ip, end_ip = asset_ip_range.split('-')
                        start_addr = ipaddress.ip_address(start_ip.strip())
                        end_addr = ipaddress.ip_address(end_ip.strip())
                        if start_addr <= target_addr <= end_addr:
                            return True

                    # Handle single IP
                    else:
                        asset_addr = ipaddress.ip_address(asset_ip_range)
                        if target_addr == asset_addr:
                            return True

                except (ipaddress.AddressValueError, ValueError):
                    continue

            return False

        except Exception as e:
            logger.warning(f"Error checking IP range match: {e}")
            return False

    def _check_domain_match(self, asset_domain: str, target_domains: List[str]) -> bool:
        """Check if asset domain matches any target domains."""
        try:
            asset_domain = asset_domain.lower().strip()

            for target_domain in target_domains:
                target_domain = target_domain.lower().strip()

                # Extract domain from URL if needed
                if target_domain.startswith('http'):
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(target_domain)
                        target_domain = parsed.netloc
                    except:
                        continue

                # Exact match
                if asset_domain == target_domain:
                    return True

                # Subdomain match
                if target_domain.endswith(f".{asset_domain}") or asset_domain.endswith(f".{target_domain}"):
                    return True

                # Wildcard subdomain match
                if asset_domain.startswith('*.'):
                    base_domain = asset_domain[2:]
                    if target_domain == base_domain or target_domain.endswith(f".{base_domain}"):
                        return True

            return False

        except Exception as e:
            logger.warning(f"Error checking domain match: {e}")
            return False

    def _check_software_match(self, asset_software: str, target_software: List[str]) -> bool:
        """Check if asset software matches any target software."""
        try:
            asset_software = asset_software.lower().strip()

            for target in target_software:
                target = target.lower().strip()

                # Exact match
                if asset_software == target:
                    return True

                # Partial match (either direction)
                if target in asset_software or asset_software in target:
                    return True

                # Check individual words
                asset_words = asset_software.split()
                target_words = target.split()

                for asset_word in asset_words:
                    for target_word in target_words:
                        if len(asset_word) > 3 and len(target_word) > 3:
                            if asset_word in target_word or target_word in asset_word:
                                return True

            return False

        except Exception as e:
            logger.warning(f"Error checking software match: {e}")
            return False

    def _generate_custom_alert(self, indicator: Indicator, matched_assets: List[AssetInventory],
                             organization: Organization) -> Optional[CustomAlert]:
        """
        Generate a custom alert for matched assets and indicator.

        Args:
            indicator: Triggering indicator
            matched_assets: List of matching assets
            organization: Target organization

        Returns:
            Generated CustomAlert or None if generation failed
        """
        try:
            with transaction.atomic():
                # Calculate alert properties
                severity, relevance_score = self._calculate_alert_severity(matched_assets, indicator)
                confidence_score = self._calculate_confidence_score(indicator, matched_assets)

                # Generate unique alert ID
                alert_id = f"ASSET-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

                # Create alert title and description
                asset_summary = self._generate_asset_summary(matched_assets)
                title = f"Threat Detected: {indicator.type} targeting {asset_summary['summary']}"
                description = self._generate_alert_description(indicator, matched_assets, asset_summary)

                # Create the custom alert
                alert = CustomAlert.objects.create(
                    alert_id=alert_id,
                    title=title,
                    description=description,
                    alert_type='infrastructure_targeted',
                    severity=severity,
                    organization=organization,
                    confidence_score=confidence_score,
                    relevance_score=relevance_score,
                    detected_at=timezone.now(),
                    response_actions=self._generate_response_actions(matched_assets, indicator),
                    metadata={
                        'indicator_id': str(indicator.id),
                        'indicator_type': indicator.type,
                        'indicator_pattern': getattr(indicator, 'pattern', ''),
                        'matched_asset_count': len(matched_assets),
                        'asset_criticalities': [asset.criticality for asset in matched_assets],
                        'generation_timestamp': timezone.now().isoformat()
                    }
                )

                # Associate with matched assets and source indicator
                alert.matched_assets.set(matched_assets)
                alert.source_indicators.add(indicator)

                # Determine affected users
                affected_users = self._get_affected_users(organization, matched_assets)
                alert.affected_users.set(affected_users)

                logger.info(f"Generated custom alert {alert_id} for organization {organization.name}")

                # Send notifications
                self._send_alert_notifications(alert)

                return alert

        except Exception as e:
            logger.error(f"Error generating custom alert for organization {organization.name}: {e}")
            return None

    def _calculate_alert_severity(self, matched_assets: List[AssetInventory],
                                indicator: Indicator) -> Tuple[str, float]:
        """Calculate alert severity and relevance score based on asset criticality."""
        try:
            if not matched_assets:
                return 'low', 0.1

            # Get highest criticality among matched assets
            criticality_scores = {
                'low': 1,
                'medium': 2,
                'high': 3,
                'critical': 4
            }

            max_criticality = max(
                criticality_scores.get(asset.criticality, 1)
                for asset in matched_assets
            )

            # Count critical and high value assets
            critical_count = sum(1 for asset in matched_assets if asset.criticality == 'critical')
            high_count = sum(1 for asset in matched_assets if asset.criticality == 'high')

            # Calculate relevance score
            relevance_score = min(1.0, (
                (critical_count * 0.4) +
                (high_count * 0.3) +
                (len(matched_assets) * 0.1)
            ))

            # Determine severity
            if critical_count > 0:
                severity = 'critical'
            elif max_criticality >= 3:  # high
                severity = 'high'
            elif max_criticality >= 2:  # medium
                severity = 'medium'
            else:
                severity = 'low'

            return severity, relevance_score

        except Exception as e:
            logger.warning(f"Error calculating alert severity: {e}")
            return 'medium', 0.5

    def _calculate_confidence_score(self, indicator: Indicator,
                                  matched_assets: List[AssetInventory]) -> float:
        """Calculate confidence score for the alert."""
        try:
            base_confidence = 0.5

            # Increase confidence based on indicator quality
            if hasattr(indicator, 'confidence') and indicator.confidence:
                base_confidence = max(base_confidence, indicator.confidence / 100.0)

            # Increase confidence based on number of matched assets
            asset_boost = min(0.3, len(matched_assets) * 0.1)

            # Increase confidence if critical assets are involved
            critical_assets = [asset for asset in matched_assets if asset.criticality == 'critical']
            critical_boost = min(0.2, len(critical_assets) * 0.1)

            return min(1.0, base_confidence + asset_boost + critical_boost)

        except Exception as e:
            logger.warning(f"Error calculating confidence score: {e}")
            return 0.5

    def _generate_asset_summary(self, matched_assets: List[AssetInventory]) -> Dict[str, Any]:
        """Generate a summary of matched assets."""
        try:
            total_count = len(matched_assets)

            # Count by type
            type_counts = {}
            for asset in matched_assets:
                asset_type = asset.get_asset_type_display()
                type_counts[asset_type] = type_counts.get(asset_type, 0) + 1

            # Count by criticality
            criticality_counts = {}
            for asset in matched_assets:
                criticality = asset.get_criticality_display()
                criticality_counts[criticality] = criticality_counts.get(criticality, 0) + 1

            # Generate summary text
            if total_count == 1:
                summary = f"1 {matched_assets[0].get_asset_type_display().lower()}"
            else:
                top_type = max(type_counts, key=type_counts.get)
                summary = f"{total_count} assets ({top_type}s)"

            return {
                'summary': summary,
                'total_count': total_count,
                'by_type': type_counts,
                'by_criticality': criticality_counts
            }

        except Exception as e:
            logger.warning(f"Error generating asset summary: {e}")
            return {'summary': f"{len(matched_assets)} assets", 'total_count': len(matched_assets)}

    def _generate_alert_description(self, indicator: Indicator, matched_assets: List[AssetInventory],
                                  asset_summary: Dict[str, Any]) -> str:
        """Generate detailed alert description."""
        try:
            description_parts = []

            # Threat overview
            indicator_type = getattr(indicator, 'type', 'Unknown')
            description_parts.append(
                f"A {indicator_type} indicator has been detected that specifically targets "
                f"infrastructure assets belonging to your organization."
            )

            # Asset impact
            critical_assets = [asset for asset in matched_assets if asset.criticality == 'critical']
            if critical_assets:
                description_parts.append(
                    f"⚠️ CRITICAL: {len(critical_assets)} critical asset(s) are potentially targeted."
                )

            # Asset details
            description_parts.append(f"Affected Assets ({asset_summary['total_count']}):")
            for asset in matched_assets[:5]:  # Limit to first 5 assets
                description_parts.append(
                    f"• {asset.name} ({asset.get_asset_type_display()}) - "
                    f"{asset.get_criticality_display()} criticality"
                )

            if len(matched_assets) > 5:
                description_parts.append(f"• ... and {len(matched_assets) - 5} more assets")

            # Indicator details
            pattern = getattr(indicator, 'pattern', '')
            if pattern:
                description_parts.append(f"Threat Pattern: {pattern}")

            # Recommended actions
            description_parts.append("\nImmediate Actions Recommended:")
            description_parts.append("1. Review and validate affected assets")
            description_parts.append("2. Implement additional monitoring")
            description_parts.append("3. Consider blocking identified indicators")

            return "\n".join(description_parts)

        except Exception as e:
            logger.warning(f"Error generating alert description: {e}")
            return f"Threat detected targeting {len(matched_assets)} organizational assets."

    def _generate_response_actions(self, matched_assets: List[AssetInventory],
                                 indicator: Indicator) -> List[Dict[str, Any]]:
        """Generate recommended response actions."""
        try:
            actions = []

            # Asset-specific actions
            critical_assets = [asset for asset in matched_assets if asset.criticality == 'critical']
            if critical_assets:
                actions.append({
                    'priority': 'high',
                    'action': 'isolate_critical_assets',
                    'title': 'Isolate Critical Assets',
                    'description': f'Consider isolating {len(critical_assets)} critical assets for investigation',
                    'assets': [str(asset.id) for asset in critical_assets]
                })

            # Monitoring actions
            actions.append({
                'priority': 'medium',
                'action': 'enhance_monitoring',
                'title': 'Enhance Monitoring',
                'description': 'Increase monitoring on affected assets and related infrastructure',
                'assets': [str(asset.id) for asset in matched_assets]
            })

            # Indicator blocking
            pattern = getattr(indicator, 'pattern', '')
            if pattern:
                actions.append({
                    'priority': 'medium',
                    'action': 'block_indicator',
                    'title': 'Block Threat Indicator',
                    'description': f'Consider blocking indicator: {pattern}',
                    'indicator_id': str(indicator.id)
                })

            return actions

        except Exception as e:
            logger.warning(f"Error generating response actions: {e}")
            return []

    def _get_affected_users(self, organization: Organization,
                          matched_assets: List[AssetInventory]) -> List[User]:
        """Get users who should receive this alert."""
        try:
            affected_users = []

            # Get organization admins and security personnel
            org_users = User.objects.filter(
                organization=organization,
                is_active=True
            )

            # Include users based on roles and preferences
            for user in org_users:
                # Include admins
                if user.role in ['BlueVisionAdmin', 'publisher']:
                    affected_users.append(user)
                    continue

                # Include users who created any of the matched assets
                user_assets = [asset for asset in matched_assets if asset.created_by == user]
                if user_assets:
                    affected_users.append(user)
                    continue

                # For now, include all organization users in alerts
                # TODO: Add user profile preferences when available
                affected_users.append(user)

            # Also include global BlueVisionAdmin users who should see all alerts
            global_admins = User.objects.filter(
                role='BlueVisionAdmin',
                is_active=True
            ).exclude(
                id__in=[user.id for user in affected_users]  # Avoid duplicates
            )

            for admin in global_admins:
                affected_users.append(admin)

            logger.info(f"Alert recipients for {organization.name}: {len(affected_users)} users (including global admins)")

            return list(set(affected_users))  # Remove duplicates

        except Exception as e:
            logger.warning(f"Error getting affected users: {e}")
            # Return organization users as fallback
            try:
                return list(User.objects.filter(organization=organization, is_active=True))
            except:
                return []

    def _send_alert_notifications(self, alert: CustomAlert):
        """Send notifications for the generated alert."""
        try:
            # Determine delivery channels based on organization preferences and asset criticality
            delivery_channels = self._determine_delivery_channels(alert)

            # Send multi-channel notifications
            delivery_results = self.multi_channel_service.deliver_alert(alert, delivery_channels)

            # Send in-app notifications
            for user in alert.affected_users.all():
                self.notification_service.create_threat_alert_notification(
                    title=f"Asset-Based Alert: {alert.title}",
                    message=f"Custom alert {alert.alert_id} has been generated for threats targeting your infrastructure.",
                    recipients=[user],
                    priority=alert.severity,
                    metadata={
                        'alert_id': alert.alert_id,
                        'alert_type': alert.alert_type,
                        'matched_asset_count': alert.matched_assets.count(),
                        'confidence_score': alert.confidence_score,
                        'delivery_results': delivery_results
                    },
                    send_emails=False  # Email handled by multi-channel service
                )

            # Update alert delivery channels and status
            alert.delivery_channels = delivery_channels
            alert.save(update_fields=['delivery_channels'])

            logger.info(f"Sent multi-channel notifications for alert {alert.alert_id} to {alert.affected_users.count()} users via {len(delivery_channels)} channels")

        except Exception as e:
            logger.error(f"Error sending alert notifications for {alert.alert_id}: {e}")

    def _determine_delivery_channels(self, alert: CustomAlert) -> List[str]:
        """Determine appropriate delivery channels based on alert severity and organization preferences."""
        try:
            channels = ['email']  # Default channel

            # Get organization preferences
            org_metadata = getattr(alert.organization, 'metadata', {}) or {}
            if isinstance(org_metadata, str):
                try:
                    import json
                    org_metadata = json.loads(org_metadata)
                except:
                    org_metadata = {}
            org_prefs = org_metadata.get('notification_preferences', {})

            # Always include email
            if org_prefs.get('email_enabled', True):
                channels.append('email')

            # Add additional channels based on severity
            if alert.severity in ['critical', 'high']:
                # High priority alerts get additional channels
                if org_prefs.get('sms_enabled', False):
                    channels.append('sms')

                if org_prefs.get('slack_enabled', False):
                    channels.append('slack')

                # Critical alerts also get webhook and ticketing
                if alert.severity == 'critical':
                    if org_prefs.get('webhook_enabled', False):
                        channels.append('webhook')

                    if org_prefs.get('servicenow_enabled', False):
                        channels.append('servicenow')
                    elif org_prefs.get('jira_enabled', False):
                        channels.append('jira')

            # Check if critical assets are involved
            critical_assets = alert.matched_assets.filter(criticality='critical')
            if critical_assets.exists():
                # Critical asset involvement escalates notification channels
                if 'sms' not in channels and org_prefs.get('sms_enabled', False):
                    channels.append('sms')
                if 'slack' not in channels and org_prefs.get('slack_enabled', False):
                    channels.append('slack')

            # Remove duplicates and return
            return list(set(channels))

        except Exception as e:
            logger.warning(f"Error determining delivery channels: {e}")
            return ['email']  # Fallback to email only

    def get_organization_alerts(self, organization: Organization,
                              days: int = 30, status: str = None) -> List[CustomAlert]:
        """Get custom alerts for an organization."""
        try:
            queryset = CustomAlert.objects.filter(
                organization=organization,
                created_at__gte=timezone.now() - timedelta(days=days)
            ).order_by('-detected_at')

            if status:
                queryset = queryset.filter(status=status)

            return list(queryset.select_related('organization').prefetch_related(
                'matched_assets', 'source_indicators', 'affected_users'
            ))

        except Exception as e:
            logger.error(f"Error getting alerts for organization {organization.name}: {e}")
            return []

    def get_alert_statistics(self, organization: Organization = None) -> Dict[str, Any]:
        """Get comprehensive alert generation statistics."""
        try:
            queryset = CustomAlert.objects.all()
            asset_queryset = AssetInventory.objects.all()

            if organization:
                queryset = queryset.filter(organization=organization)
                asset_queryset = asset_queryset.filter(organization=organization)

            # Last 30 days
            recent_queryset = queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            )

            # Last 7 days for trends
            week_queryset = queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            )

            # Asset statistics
            total_assets = asset_queryset.count()
            alert_enabled_assets = asset_queryset.filter(alert_enabled=True).count()
            critical_assets = asset_queryset.filter(criticality='critical').count()

            stats = {
                'alert_statistics': {
                    'total_alerts': queryset.count(),
                    'recent_alerts': recent_queryset.count(),
                    'weekly_alerts': week_queryset.count(),
                    'by_severity': {},
                    'by_status': {},
                    'avg_confidence': 0.0,
                    'avg_relevance': 0.0,
                    'critical_alerts_today': recent_queryset.filter(
                        severity='critical',
                        created_at__gte=timezone.now() - timedelta(days=1)
                    ).count()
                },
                'asset_statistics': {
                    'total_assets': total_assets,
                    'alert_enabled_assets': alert_enabled_assets,
                    'critical_assets': critical_assets,
                    'alert_coverage_percentage': round(
                        (alert_enabled_assets / total_assets * 100) if total_assets > 0 else 0, 1
                    ),
                    'by_type': {},
                    'by_criticality': {}
                },
                'threat_correlation': {
                    'last_correlation_run': self._get_last_correlation_timestamp(organization),
                    'active_threats': self._get_active_threat_count(organization),
                    'correlation_accuracy': self._calculate_correlation_accuracy(organization)
                }
            }

            # Count alerts by severity
            for severity_choice in CustomAlert.SEVERITY_CHOICES:
                severity = severity_choice[0]
                count = recent_queryset.filter(severity=severity).count()
                stats['alert_statistics']['by_severity'][severity] = count

            # Count alerts by status
            for status_choice in CustomAlert.STATUS_CHOICES:
                status_val = status_choice[0]
                count = recent_queryset.filter(status=status_val).count()
                stats['alert_statistics']['by_status'][status_val] = count

            # Asset counts by type
            for type_choice in AssetInventory.ASSET_TYPE_CHOICES:
                asset_type = type_choice[0]
                count = asset_queryset.filter(asset_type=asset_type).count()
                if count > 0:
                    stats['asset_statistics']['by_type'][asset_type] = count

            # Asset counts by criticality
            for crit_choice in AssetInventory.CRITICALITY_CHOICES:
                criticality = crit_choice[0]
                count = asset_queryset.filter(criticality=criticality).count()
                if count > 0:
                    stats['asset_statistics']['by_criticality'][criticality] = count

            # Calculate averages
            if recent_queryset.exists():
                avg_scores = recent_queryset.aggregate(
                    avg_confidence=models.Avg('confidence_score'),
                    avg_relevance=models.Avg('relevance_score')
                )
                stats['alert_statistics']['avg_confidence'] = round(avg_scores['avg_confidence'] or 0.0, 2)
                stats['alert_statistics']['avg_relevance'] = round(avg_scores['avg_relevance'] or 0.0, 2)

            return stats

        except Exception as e:
            logger.error(f"Error getting alert statistics: {e}")
            return {}

    def _get_last_correlation_timestamp(self, organization: Organization = None) -> str:
        """Get timestamp of last correlation run."""
        try:
            queryset = CustomAlert.objects.all()
            if organization:
                queryset = queryset.filter(organization=organization)

            last_alert = queryset.order_by('-created_at').first()
            if last_alert:
                return last_alert.created_at.isoformat()
            return None
        except:
            return None

    def _get_active_threat_count(self, organization: Organization = None) -> int:
        """Get count of active threats."""
        try:
            # Count unique threat indicators in last 24 hours
            recent_alerts = CustomAlert.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=1)
            )
            if organization:
                recent_alerts = recent_alerts.filter(organization=organization)

            return recent_alerts.values('source_indicators').distinct().count()
        except:
            return 0

    def _calculate_correlation_accuracy(self, organization: Organization = None) -> float:
        """Calculate correlation accuracy based on alert feedback."""
        try:
            # Simple accuracy based on alert status progression
            alerts = CustomAlert.objects.all()
            if organization:
                alerts = alerts.filter(organization=organization)

            total_alerts = alerts.count()
            if total_alerts == 0:
                return 0.0

            # Consider resolved alerts as accurate correlations
            accurate_alerts = alerts.filter(status__in=['resolved', 'investigating']).count()
            return round((accurate_alerts / total_alerts) * 100, 1)
        except:
            return 0.0

    def trigger_correlation_for_organization(self, organization: Organization, days: int = 1) -> Dict[str, Any]:
        """Manually trigger correlation for a specific organization."""
        try:
            # Get recent indicators
            cutoff_date = timezone.now() - timedelta(days=days)
            recent_indicators = Indicator.objects.filter(
                created_at__gte=cutoff_date
            ).order_by('-created_at')[:100]  # Limit for performance

            if not recent_indicators.exists():
                return {
                    'success': False,
                    'message': 'No recent indicators found for correlation',
                    'alerts_generated': 0
                }

            # Process indicators for this organization
            alerts = self._process_indicators_for_organization(
                list(recent_indicators), organization
            )

            logger.info(f"Manual correlation triggered for {organization.name}: {len(alerts)} alerts generated")

            return {
                'success': True,
                'message': f'Correlation completed successfully',
                'alerts_generated': len(alerts),
                'indicators_processed': recent_indicators.count(),
                'organization': organization.name,
                'time_range_days': days
            }

        except Exception as e:
            logger.error(f"Error triggering correlation for {organization.name}: {e}")
            return {
                'success': False,
                'message': f'Correlation failed: {str(e)}',
                'alerts_generated': 0
            }

    def get_alert_details(self, alert_id: str, organization: Organization) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific alert."""
        try:
            alert = CustomAlert.objects.select_related('organization').prefetch_related(
                'matched_assets', 'source_indicators', 'affected_users'
            ).get(id=alert_id, organization=organization)

            return {
                'id': str(alert.id),
                'alert_id': alert.alert_id,
                'title': alert.title,
                'description': alert.description,
                'alert_type': alert.alert_type,
                'alert_type_display': alert.get_alert_type_display(),
                'severity': alert.severity,
                'severity_display': alert.get_severity_display(),
                'status': alert.status,
                'status_display': alert.get_status_display(),
                'confidence_score': alert.confidence_score,
                'relevance_score': alert.relevance_score,
                'detected_at': alert.detected_at.isoformat(),
                'created_at': alert.created_at.isoformat(),
                'updated_at': alert.updated_at.isoformat(),
                'delivery_channels': alert.delivery_channels,
                'response_actions': alert.response_actions,
                'metadata': alert.metadata,
                'matched_assets': [
                    {
                        'id': str(asset.id),
                        'name': asset.name,
                        'asset_type': asset.asset_type,
                        'asset_type_display': asset.get_asset_type_display(),
                        'asset_value': asset.asset_value,
                        'criticality': asset.criticality,
                        'criticality_display': asset.get_criticality_display()
                    }
                    for asset in alert.matched_assets.all()
                ],
                'source_indicators': [
                    {
                        'id': str(indicator.id),
                        'type': indicator.type,
                        'value': indicator.value,
                        'pattern': getattr(indicator, 'pattern', ''),
                        'confidence': getattr(indicator, 'confidence', 0)
                    }
                    for indicator in alert.source_indicators.all()
                ],
                'affected_users': [
                    {
                        'id': str(user.id),
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    }
                    for user in alert.affected_users.all()
                ]
            }

        except CustomAlert.DoesNotExist:
            logger.warning(f"Alert {alert_id} not found for organization {organization.name}")
            return None
        except Exception as e:
            logger.error(f"Error getting alert details for {alert_id}: {e}")
            return None

    def update_alert_status(self, alert_id: str, action: str, organization: Organization, user) -> Dict[str, Any]:
        """Update alert status based on user action."""
        try:
            alert = CustomAlert.objects.get(id=alert_id, organization=organization)

            status_mapping = {
                'acknowledge': 'investigating',
                'resolve': 'resolved',
                'dismiss': 'dismissed',
                'escalate': 'escalated'
            }

            if action not in status_mapping:
                return {
                    'success': False,
                    'message': f'Invalid action: {action}'
                }

            old_status = alert.status
            alert.status = status_mapping[action]
            alert.save(update_fields=['status', 'updated_at'])

            # Log the status change
            logger.info(f"Alert {alert.alert_id} status changed from {old_status} to {alert.status} by {user.username}")

            # Add to metadata for audit trail
            if not alert.metadata:
                alert.metadata = {}
            if 'status_history' not in alert.metadata:
                alert.metadata['status_history'] = []

            alert.metadata['status_history'].append({
                'timestamp': timezone.now().isoformat(),
                'user': user.username,
                'action': action,
                'old_status': old_status,
                'new_status': alert.status
            })
            alert.save(update_fields=['metadata'])

            return {
                'success': True,
                'message': f'Alert {action}d successfully',
                'old_status': old_status,
                'new_status': alert.status
            }

        except CustomAlert.DoesNotExist:
            return {
                'success': False,
                'message': 'Alert not found'
            }
        except Exception as e:
            logger.error(f"Error updating alert status: {e}")
            return {
                'success': False,
                'message': f'Failed to update alert: {str(e)}'
            }