"""
Multi-Channel Alert Delivery Service for CRISP WOW Factor #1
Implements multiple delivery channels: email, SMS, webhooks, Slack, and support ticketing.
"""

import logging
import json
import requests
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from core.models.models import CustomAlert, AssetInventory
from core.services.email_service import UnifiedEmailService

User = get_user_model()
logger = logging.getLogger(__name__)


class MultiChannelAlertService:
    """
    Service for delivering alerts through multiple channels.
    Supports email, SMS, webhooks, Slack, and ticketing systems.
    """

    def __init__(self):
        self.email_service = UnifiedEmailService()

    def deliver_alert(self, alert: CustomAlert, channels: List[str] = None) -> Dict[str, Any]:
        """
        Deliver alert through specified channels.

        Args:
            alert: CustomAlert instance to deliver
            channels: List of delivery channels, defaults to alert.delivery_channels

        Returns:
            Dictionary with delivery results for each channel
        """
        if not channels:
            channels = alert.delivery_channels or ['email']

        delivery_results = {}

        try:
            # Get affected users and their preferences
            users = alert.affected_users.all()

            for channel in channels:
                try:
                    if channel == 'email':
                        result = self._deliver_via_email(alert, users)
                    elif channel == 'sms':
                        result = self._deliver_via_sms(alert, users)
                    elif channel == 'webhook':
                        result = self._deliver_via_webhook(alert)
                    elif channel == 'slack':
                        result = self._deliver_via_slack(alert)
                    elif channel == 'servicenow':
                        result = self._deliver_via_servicenow(alert)
                    elif channel == 'jira':
                        result = self._deliver_via_jira(alert)
                    else:
                        result = {'success': False, 'message': f'Unknown channel: {channel}'}

                    delivery_results[channel] = result
                    logger.info(f"Alert {alert.alert_id} delivery via {channel}: {result['success']}")

                except Exception as e:
                    delivery_results[channel] = {
                        'success': False,
                        'message': f'Delivery failed: {str(e)}'
                    }
                    logger.error(f"Error delivering alert {alert.alert_id} via {channel}: {e}")

            # Update alert delivery status
            self._update_alert_delivery_status(alert, delivery_results)

            return delivery_results

        except Exception as e:
            logger.error(f"Error in deliver_alert for {alert.alert_id}: {e}")
            return {'error': str(e)}

    def _deliver_via_email(self, alert: CustomAlert, users: List[User]) -> Dict[str, Any]:
        """Deliver alert via email."""
        try:
            email_addresses = []
            for user in users:
                # Include all users for now, since profile model might not exist
                if user.email:
                    email_addresses.append(user.email)

            if not email_addresses:
                return {'success': False, 'message': 'No users with email addresses found'}

            # Generate email content
            subject = f"🚨 CRISP Alert: {alert.title}"

            # Create rich HTML email content
            context = {
                'alert': alert,
                'asset_summary': alert.get_asset_summary(),
                'organization': alert.organization,
                'timestamp': timezone.now(),
                'alert_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/assets/alerts/{alert.id}"
            }

            html_content = self._generate_alert_email_html(context)
            plain_content = self._generate_alert_email_plain(context)

            # Send email via existing email service
            result = self.email_service.send_custom_email(
                recipients=email_addresses,
                subject=subject,
                html_content=html_content,
                plain_content=plain_content,
                alert_type='asset_based_alert'
            )

            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Email sent'),
                'recipients': len(email_addresses)
            }

        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return {'success': False, 'message': str(e)}

    def _deliver_via_sms(self, alert: CustomAlert, users: List[User]) -> Dict[str, Any]:
        """Deliver alert via SMS using Twilio or similar service."""
        try:
            # Check if SMS is configured
            twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            twilio_from = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

            if not all([twilio_sid, twilio_token, twilio_from]):
                return {'success': False, 'message': 'SMS service not configured'}

            # Get users with phone numbers (SMS profile not available yet)
            sms_recipients = []
            for user in users:
                # For now, SMS is disabled since profile model doesn't exist
                # TODO: Enable when user profile model is available
                pass

            if not sms_recipients:
                return {'success': False, 'message': 'No users with SMS enabled'}

            # Generate SMS content (limited to 160 characters)
            severity_icon = self._get_severity_icon(alert.severity)
            sms_content = (
                f"{severity_icon} CRISP Alert: {alert.title[:80]}... "
                f"Severity: {alert.severity.upper()}. "
                f"Assets: {alert.matched_assets.count()}. "
                f"ID: {alert.alert_id}"
            )[:160]

            sent_count = 0
            failed_count = 0

            # Send SMS to each recipient
            for recipient in sms_recipients:
                try:
                    # Use Twilio API
                    from twilio.rest import Client
                    client = Client(twilio_sid, twilio_token)

                    message = client.messages.create(
                        body=sms_content,
                        from_=twilio_from,
                        to=recipient['phone']
                    )

                    sent_count += 1
                    logger.info(f"SMS sent to {recipient['user'].username}: {message.sid}")

                except Exception as e:
                    failed_count += 1
                    logger.warning(f"Failed to send SMS to {recipient['user'].username}: {e}")

            return {
                'success': sent_count > 0,
                'message': f'SMS sent to {sent_count} recipients, {failed_count} failed',
                'sent_count': sent_count,
                'failed_count': failed_count
            }

        except Exception as e:
            logger.error(f"Error sending SMS alert: {e}")
            return {'success': False, 'message': str(e)}

    def _deliver_via_webhook(self, alert: CustomAlert) -> Dict[str, Any]:
        """Deliver alert via webhook."""
        try:
            webhook_urls = getattr(settings, 'ALERT_WEBHOOK_URLS', [])
            if not webhook_urls:
                # Check organization-specific webhooks
                org_metadata = getattr(alert.organization, 'metadata', {}) or {}
                if isinstance(org_metadata, str):
                    try:
                        import json
                        org_metadata = json.loads(org_metadata)
                    except:
                        org_metadata = {}
                webhook_urls = org_metadata.get('webhook_urls', [])

            if not webhook_urls:
                return {'success': False, 'message': 'No webhook URLs configured'}

            # Prepare webhook payload
            payload = {
                'alert_id': alert.alert_id,
                'title': alert.title,
                'description': alert.description,
                'severity': alert.severity,
                'status': alert.status,
                'alert_type': alert.alert_type,
                'confidence_score': alert.confidence_score,
                'relevance_score': alert.relevance_score,
                'organization': {
                    'id': str(alert.organization.id),
                    'name': alert.organization.name
                },
                'matched_assets': [
                    {
                        'id': str(asset.id),
                        'name': asset.name,
                        'type': asset.asset_type,
                        'value': asset.asset_value,
                        'criticality': asset.criticality
                    }
                    for asset in alert.matched_assets.all()
                ],
                'detected_at': alert.detected_at.isoformat(),
                'response_actions': alert.response_actions,
                'metadata': alert.metadata
            }

            sent_count = 0
            failed_count = 0

            for webhook_url in webhook_urls:
                try:
                    response = requests.post(
                        webhook_url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )

                    if response.status_code in [200, 201, 202]:
                        sent_count += 1
                        logger.info(f"Webhook sent successfully to {webhook_url}")
                    else:
                        failed_count += 1
                        logger.warning(f"Webhook failed to {webhook_url}: {response.status_code}")

                except Exception as e:
                    failed_count += 1
                    logger.warning(f"Webhook failed to {webhook_url}: {e}")

            return {
                'success': sent_count > 0,
                'message': f'Webhook sent to {sent_count} endpoints, {failed_count} failed',
                'sent_count': sent_count,
                'failed_count': failed_count
            }

        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
            return {'success': False, 'message': str(e)}

    def _deliver_via_slack(self, alert: CustomAlert) -> Dict[str, Any]:
        """Deliver alert via Slack webhook."""
        try:
            slack_webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
            if not slack_webhook_url:
                # Check organization-specific Slack webhooks
                org_metadata = getattr(alert.organization, 'metadata', {}) or {}
                if isinstance(org_metadata, str):
                    try:
                        import json
                        org_metadata = json.loads(org_metadata)
                    except:
                        org_metadata = {}
                slack_webhook_url = org_metadata.get('slack_webhook_url')

            if not slack_webhook_url:
                return {'success': False, 'message': 'Slack webhook not configured'}

            # Determine color based on severity
            color_map = {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#28a745',
                'info': '#17a2b8'
            }
            color = color_map.get(alert.severity, '#6c757d')

            # Create Slack message
            asset_summary = alert.get_asset_summary()

            slack_payload = {
                'username': 'CRISP Alert System',
                'icon_emoji': ':warning:',
                'attachments': [
                    {
                        'color': color,
                        'title': f"🎯 Asset-Based Alert: {alert.title}",
                        'title_link': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/assets/alerts/{alert.id}",
                        'text': alert.description,
                        'fields': [
                            {
                                'title': 'Alert ID',
                                'value': alert.alert_id,
                                'short': True
                            },
                            {
                                'title': 'Severity',
                                'value': alert.severity.upper(),
                                'short': True
                            },
                            {
                                'title': 'Matched Assets',
                                'value': str(alert.matched_assets.count()),
                                'short': True
                            },
                            {
                                'title': 'Confidence',
                                'value': f"{round(alert.confidence_score * 100)}%",
                                'short': True
                            },
                            {
                                'title': 'Organization',
                                'value': alert.organization.name,
                                'short': True
                            },
                            {
                                'title': 'Detected',
                                'value': alert.detected_at.strftime('%Y-%m-%d %H:%M UTC'),
                                'short': True
                            }
                        ],
                        'footer': 'CRISP Asset-Based Alert System',
                        'ts': int(alert.detected_at.timestamp())
                    }
                ]
            }

            # Add asset details if critical assets are involved
            critical_assets = [asset for asset in alert.matched_assets.all() if asset.criticality == 'critical']
            if critical_assets:
                critical_asset_text = "⚠️ **Critical Assets Affected:**\n" + "\n".join(
                    f"• {asset.name} ({asset.get_asset_type_display()})"
                    for asset in critical_assets[:5]
                )
                slack_payload['attachments'][0]['fields'].append({
                    'title': 'Critical Assets',
                    'value': critical_asset_text,
                    'short': False
                })

            response = requests.post(
                slack_webhook_url,
                json=slack_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code == 200:
                return {'success': True, 'message': 'Slack notification sent'}
            else:
                return {'success': False, 'message': f'Slack API error: {response.status_code}'}

        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return {'success': False, 'message': str(e)}

    def _deliver_via_servicenow(self, alert: CustomAlert) -> Dict[str, Any]:
        """Create ServiceNow incident for the alert."""
        try:
            # ServiceNow configuration
            snow_instance = getattr(settings, 'SERVICENOW_INSTANCE', None)
            snow_username = getattr(settings, 'SERVICENOW_USERNAME', None)
            snow_password = getattr(settings, 'SERVICENOW_PASSWORD', None)

            if not all([snow_instance, snow_username, snow_password]):
                return {'success': False, 'message': 'ServiceNow not configured'}

            # Map severity to ServiceNow impact/urgency
            severity_map = {
                'critical': {'impact': '1', 'urgency': '1'},
                'high': {'impact': '2', 'urgency': '2'},
                'medium': {'impact': '3', 'urgency': '3'},
                'low': {'impact': '3', 'urgency': '3'},
                'info': {'impact': '3', 'urgency': '3'}
            }

            severity_config = severity_map.get(alert.severity, {'impact': '3', 'urgency': '3'})

            # Create incident data
            incident_data = {
                'short_description': f"CRISP Asset Alert: {alert.title}",
                'description': self._format_servicenow_description(alert),
                'category': 'Security',
                'subcategory': 'Threat Detection',
                'impact': severity_config['impact'],
                'urgency': severity_config['urgency'],
                'assignment_group': getattr(settings, 'SERVICENOW_ASSIGNMENT_GROUP', 'Security Team'),
                'caller_id': snow_username,
                'work_notes': f"Generated by CRISP Asset-Based Alert System. Alert ID: {alert.alert_id}"
            }

            # Send to ServiceNow
            snow_url = f"https://{snow_instance}.service-now.com/api/now/table/incident"

            response = requests.post(
                snow_url,
                json=incident_data,
                auth=(snow_username, snow_password),
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code == 201:
                incident_number = response.json().get('result', {}).get('number')
                return {
                    'success': True,
                    'message': f'ServiceNow incident created: {incident_number}',
                    'incident_number': incident_number
                }
            else:
                return {'success': False, 'message': f'ServiceNow API error: {response.status_code}'}

        except Exception as e:
            logger.error(f"Error creating ServiceNow incident: {e}")
            return {'success': False, 'message': str(e)}

    def _deliver_via_jira(self, alert: CustomAlert) -> Dict[str, Any]:
        """Create JIRA ticket for the alert."""
        try:
            # JIRA configuration
            jira_url = getattr(settings, 'JIRA_URL', None)
            jira_username = getattr(settings, 'JIRA_USERNAME', None)
            jira_token = getattr(settings, 'JIRA_TOKEN', None)
            jira_project = getattr(settings, 'JIRA_PROJECT', None)

            if not all([jira_url, jira_username, jira_token, jira_project]):
                return {'success': False, 'message': 'JIRA not configured'}

            # Map severity to JIRA priority
            priority_map = {
                'critical': 'Highest',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low',
                'info': 'Lowest'
            }

            priority = priority_map.get(alert.severity, 'Medium')

            # Create issue data
            issue_data = {
                'fields': {
                    'project': {'key': jira_project},
                    'summary': f"CRISP Asset Alert: {alert.title}",
                    'description': self._format_jira_description(alert),
                    'issuetype': {'name': 'Task'},  # or 'Bug', 'Story', etc.
                    'priority': {'name': priority},
                    'labels': ['crisp-alert', f'severity-{alert.severity}', 'asset-based']
                }
            }

            # Send to JIRA
            jira_api_url = f"{jira_url}/rest/api/3/issue"

            response = requests.post(
                jira_api_url,
                json=issue_data,
                auth=(jira_username, jira_token),
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code == 201:
                issue_key = response.json().get('key')
                return {
                    'success': True,
                    'message': f'JIRA ticket created: {issue_key}',
                    'issue_key': issue_key
                }
            else:
                return {'success': False, 'message': f'JIRA API error: {response.status_code}'}

        except Exception as e:
            logger.error(f"Error creating JIRA ticket: {e}")
            return {'success': False, 'message': str(e)}

    def _update_alert_delivery_status(self, alert: CustomAlert, delivery_results: Dict[str, Any]):
        """Update alert with delivery status."""
        try:
            delivery_status = alert.delivery_status or {}

            for channel, result in delivery_results.items():
                delivery_status[channel] = {
                    'success': result.get('success', False),
                    'message': result.get('message', ''),
                    'timestamp': timezone.now().isoformat(),
                    'recipients': result.get('recipients', 0)
                }

            alert.delivery_status = delivery_status
            alert.save(update_fields=['delivery_status'])

        except Exception as e:
            logger.error(f"Error updating delivery status for alert {alert.alert_id}: {e}")

    def _generate_alert_email_html(self, context: Dict[str, Any]) -> str:
        """Generate HTML email content for alert."""
        try:
            # Use Django template if available, otherwise generate simple HTML
            html_template = """
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h2 style="color: #dc3545; margin: 0;">🚨 CRISP Asset-Based Alert</h2>
                        <p style="margin: 10px 0 0 0; color: #6c757d;">Custom threat intelligence for your infrastructure</p>
                    </div>

                    <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                        <h3 style="color: #495057; margin-top: 0;">{title}</h3>
                        <p><strong>Alert ID:</strong> {alert_id}</p>
                        <p><strong>Severity:</strong> <span style="color: {severity_color};">{severity}</span></p>
                        <p><strong>Organization:</strong> {organization}</p>
                        <p><strong>Detected:</strong> {detected_at}</p>
                        <p><strong>Confidence:</strong> {confidence}%</p>
                    </div>

                    <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                        <h4 style="color: #495057;">Description</h4>
                        <p>{description}</p>
                    </div>

                    <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                        <h4 style="color: #495057;">Affected Assets ({asset_count})</h4>
                        <p>This alert affects <strong>{asset_count}</strong> assets in your infrastructure.</p>
                        {asset_details}
                    </div>

                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{alert_url}" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            View Alert Details
                        </a>
                    </div>

                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d; font-size: 0.9em;">
                        <p>This alert was generated by the CRISP Asset-Based Alert System</p>
                        <p>Organization: {organization}</p>
                    </div>
                </div>
            </body>
            </html>
            """

            alert = context['alert']
            asset_summary = context['asset_summary']

            severity_colors = {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#28a745',
                'info': '#17a2b8'
            }

            return html_template.format(
                title=alert.title,
                alert_id=alert.alert_id,
                severity=alert.severity.upper(),
                severity_color=severity_colors.get(alert.severity, '#6c757d'),
                organization=alert.organization.name,
                detected_at=alert.detected_at.strftime('%Y-%m-%d %H:%M UTC'),
                confidence=round(alert.confidence_score * 100),
                description=alert.description,
                asset_count=asset_summary['total_count'],
                asset_details=self._format_asset_details_html(asset_summary),
                alert_url=context['alert_url']
            )

        except Exception as e:
            logger.error(f"Error generating HTML email: {e}")
            return f"<html><body><h2>Alert: {context['alert'].title}</h2><p>{context['alert'].description}</p></body></html>"

    def _generate_alert_email_plain(self, context: Dict[str, Any]) -> str:
        """Generate plain text email content for alert."""
        try:
            alert = context['alert']
            asset_summary = context['asset_summary']

            content = f"""
CRISP Asset-Based Alert
=======================

{alert.title}

Alert Details:
- Alert ID: {alert.alert_id}
- Severity: {alert.severity.upper()}
- Organization: {alert.organization.name}
- Detected: {alert.detected_at.strftime('%Y-%m-%d %H:%M UTC')}
- Confidence: {round(alert.confidence_score * 100)}%

Description:
{alert.description}

Affected Assets: {asset_summary['total_count']}
{self._format_asset_details_plain(asset_summary)}

View full alert details: {context['alert_url']}

---
This alert was generated by the CRISP Asset-Based Alert System
Organization: {alert.organization.name}
            """.strip()

            return content

        except Exception as e:
            logger.error(f"Error generating plain email: {e}")
            return f"Alert: {context['alert'].title}\n\n{context['alert'].description}"

    def _format_asset_details_html(self, asset_summary: Dict[str, Any]) -> str:
        """Format asset details for HTML email."""
        if not asset_summary.get('by_criticality'):
            return "<p>No asset details available.</p>"

        html = "<ul>"
        for criticality, count in asset_summary['by_criticality'].items():
            html += f"<li><strong>{criticality.title()}:</strong> {count} assets</li>"
        html += "</ul>"

        return html

    def _format_asset_details_plain(self, asset_summary: Dict[str, Any]) -> str:
        """Format asset details for plain text email."""
        if not asset_summary.get('by_criticality'):
            return "No asset details available."

        details = []
        for criticality, count in asset_summary['by_criticality'].items():
            details.append(f"- {criticality.title()}: {count} assets")

        return "\n".join(details)

    def _format_servicenow_description(self, alert: CustomAlert) -> str:
        """Format description for ServiceNow incident."""
        asset_summary = alert.get_asset_summary()

        description = f"""
Alert Details:
- Alert ID: {alert.alert_id}
- Severity: {alert.severity.upper()}
- Confidence: {round(alert.confidence_score * 100)}%
- Detected: {alert.detected_at.strftime('%Y-%m-%d %H:%M UTC')}

Description:
{alert.description}

Affected Assets ({asset_summary['total_count']}):
"""

        for criticality, count in asset_summary.get('by_criticality', {}).items():
            description += f"\n- {criticality.title()}: {count} assets"

        return description

    def _format_jira_description(self, alert: CustomAlert) -> str:
        """Format description for JIRA ticket."""
        asset_summary = alert.get_asset_summary()

        description = f"""
h2. Alert Details
* *Alert ID:* {alert.alert_id}
* *Severity:* {alert.severity.upper()}
* *Confidence:* {round(alert.confidence_score * 100)}%
* *Detected:* {alert.detected_at.strftime('%Y-%m-%d %H:%M UTC')}

h2. Description
{alert.description}

h2. Affected Assets ({asset_summary['total_count']})
"""

        for criticality, count in asset_summary.get('by_criticality', {}).items():
            description += f"\n* {criticality.title()}: {count} assets"

        return description

    def _get_severity_icon(self, severity: str) -> str:
        """Get emoji icon for severity level."""
        icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
            'info': '🔵'
        }
        return icons.get(severity, '⚪')