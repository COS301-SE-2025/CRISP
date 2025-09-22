"""
IOC Sharing Service - Handles sharing of indicators of compromise with trusted organizations
"""
import logging
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models.models import (
    Indicator, Organization, STIXObject,
    Collection, CollectionObject, SystemActivity,
    IndicatorSharingRelationship
)
from core.trust_management.models.trust_models import TrustRelationship
from core.services.access_control_service import AccessControlService
from core.services.audit_service import AuditService
from core.services.anonymization_service import AnonymizationService
from core.services.stix_taxii_service import StixTaxiiService

logger = logging.getLogger(__name__)


class IOCSharingService:
    """Service for sharing IOCs with trusted organizations"""

    def __init__(self):
        self.access_control = AccessControlService()
        self.audit_service = AuditService()
        self.anonymization_service = AnonymizationService()
        self.stix_service = StixTaxiiService()

    def generate_share_url(self, indicator_id: int, sharing_user, expiry_hours: int = 24,
                          access_type: str = 'view') -> Dict[str, Any]:
        """
        Generate a secure share URL for an indicator

        Args:
            indicator_id: ID of the indicator to share
            sharing_user: User creating the share
            expiry_hours: Hours until the share expires
            access_type: Type of access (view, download, etc.)

        Returns:
            Dictionary containing share URL and metadata
        """
        try:
            # Get the indicator
            indicator = Indicator.objects.get(id=indicator_id)

            # Check if user can share this indicator
            if not self.access_control.can_share_indicator(sharing_user, indicator):
                raise PermissionError("User does not have permission to share this indicator")

            # Generate secure token
            share_token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(hours=expiry_hours)

            # Create share record
            share_record = {
                'indicator_id': indicator_id,
                'token': share_token,
                'created_by': sharing_user,
                'expires_at': expires_at,
                'access_type': access_type,
                'access_count': 0,
                'is_active': True
            }

            # Store in database (we'll need to create a ShareRecord model)
            # For now, store in system activity with metadata
            SystemActivity.objects.create(
                activity_type='indicator_share_created',
                category='indicator',
                title=f'Share URL generated for indicator {indicator.value[:50]}',
                description=f'Share URL created by {sharing_user.username}',
                indicator=indicator,
                user=sharing_user,
                metadata={
                    'share_token': share_token,
                    'expires_at': expires_at.isoformat(),
                    'access_type': access_type,
                    'expiry_hours': expiry_hours
                }
            )

            # Generate the share URL
            share_url = f"/api/indicators/shared/{share_token}/"

            # Log the activity
            self.audit_service.log_user_action(
                user=sharing_user,
                action='indicator_share_url_generated',
                success=True,
                additional_data={
                    'indicator_id': indicator_id,
                    'share_token': share_token,
                    'expires_in_hours': expiry_hours,
                    'access_type': access_type
                }
            )

            return {
                'success': True,
                'share_url': share_url,
                'share_token': share_token,
                'expires_at': expires_at.isoformat(),
                'access_type': access_type,
                'indicator_type': indicator.type,
                'indicator_value': indicator.value[:100] + '...' if len(indicator.value) > 100 else indicator.value
            }

        except Indicator.DoesNotExist:
            raise ValueError(f"Indicator with ID {indicator_id} not found")
        except Exception as e:
            logger.error(f"Error generating share URL for indicator {indicator_id}: {str(e)}")
            raise

    def access_shared_indicator(self, share_token: str, accessing_user=None) -> Dict[str, Any]:
        """
        Access a shared indicator using its share token

        Args:
            share_token: The share token
            accessing_user: User accessing the share (optional)

        Returns:
            Dictionary containing indicator data if access is allowed
        """
        try:
            # Find the share record
            share_record = SystemActivity.objects.filter(
                activity_type='indicator_share_created',
                metadata__share_token=share_token
            ).first()

            if not share_record:
                raise ValueError("Share token not found or expired")

            # Check if share is still valid
            share_data = share_record.metadata
            expires_at = datetime.fromisoformat(share_data['expires_at'].replace('Z', '+00:00'))

            if timezone.now() > expires_at:
                raise ValueError("Share token has expired")

            # Get the indicator
            indicator = share_record.indicator
            if not indicator:
                raise ValueError("Indicator not found")

            # Increment access count
            share_data['access_count'] = share_data.get('access_count', 0) + 1
            share_record.metadata = share_data
            share_record.save()

            # Apply appropriate anonymization if needed
            indicator_data = self._format_shared_indicator(indicator, accessing_user)

            # Log the access
            self.audit_service.log_security_event(
                action='shared_indicator_accessed',
                user=accessing_user,
                success=True,
                additional_data={
                    'share_token': share_token,
                    'indicator_id': indicator.id,
                    'access_count': share_data['access_count']
                }
            )

            return {
                'success': True,
                'indicator': indicator_data,
                'share_info': {
                    'expires_at': share_data['expires_at'],
                    'access_type': share_data.get('access_type', 'view'),
                    'access_count': share_data['access_count']
                }
            }

        except Exception as e:
            logger.error(f"Error accessing shared indicator with token {share_token}: {str(e)}")
            raise

    def share_indicators_with_organizations(self, indicator_ids: List[int], target_organizations: List[str],
                                          sharing_user, anonymization_level: str = 'medium',
                                          share_method: str = 'taxii') -> Dict[str, Any]:
        """
        Share multiple indicators with specified organizations

        Args:
            indicator_ids: List of indicator IDs to share
            target_organizations: List of organization IDs or names
            sharing_user: User performing the share
            anonymization_level: Level of anonymization to apply
            share_method: Method of sharing (taxii, api, etc.)

        Returns:
            Dictionary containing share results
        """
        results = {
            'success': True,
            'shared_indicators': [],
            'failed_indicators': [],
            'target_organizations': target_organizations,
            'anonymization_level': anonymization_level,
            'share_method': share_method
        }

        try:
            with transaction.atomic():
                for indicator_id in indicator_ids:
                    try:
                        # Get the indicator
                        indicator = Indicator.objects.get(id=indicator_id)

                        # Check sharing permissions
                        if not self.access_control.can_share_indicator(sharing_user, indicator):
                            results['failed_indicators'].append({
                                'indicator_id': indicator_id,
                                'error': 'Insufficient permissions to share this indicator'
                            })
                            continue

                        # Share with each organization
                        org_results = []
                        for org_id in target_organizations:
                            try:
                                org_result = self._share_indicator_with_organization(
                                    indicator, org_id, sharing_user, anonymization_level, share_method
                                )
                                org_results.append(org_result)
                            except Exception as e:
                                org_results.append({
                                    'organization_id': org_id,
                                    'success': False,
                                    'error': str(e)
                                })

                        results['shared_indicators'].append({
                            'indicator_id': indicator_id,
                            'indicator_type': indicator.type,
                            'indicator_value': indicator.value[:50] + '...' if len(indicator.value) > 50 else indicator.value,
                            'organizations': org_results,
                            'success': True
                        })

                    except Indicator.DoesNotExist:
                        results['failed_indicators'].append({
                            'indicator_id': indicator_id,
                            'error': 'Indicator not found'
                        })
                    except Exception as e:
                        results['failed_indicators'].append({
                            'indicator_id': indicator_id,
                            'error': str(e)
                        })

                # Update overall success status
                results['success'] = len(results['failed_indicators']) == 0

                # Log the sharing activity
                self.audit_service.log_user_action(
                    user=sharing_user,
                    action='indicators_shared_bulk',
                    success=results['success'],
                    additional_data={
                        'indicator_count': len(indicator_ids),
                        'successful_shares': len(results['shared_indicators']),
                        'failed_shares': len(results['failed_indicators']),
                        'target_org_count': len(target_organizations),
                        'anonymization_level': anonymization_level,
                        'share_method': share_method
                    }
                )

                return results

        except Exception as e:
            logger.error(f"Error in bulk indicator sharing: {str(e)}")
            results['success'] = False
            results['error'] = str(e)
            return results

    def _share_indicator_with_organization(self, indicator: Indicator, org_id: str,
                                         sharing_user, anonymization_level: str,
                                         share_method: str) -> Dict[str, Any]:
        """
        Share a single indicator with a specific organization

        Args:
            indicator: Indicator to share
            org_id: Target organization ID
            sharing_user: User performing the share
            anonymization_level: Level of anonymization to apply
            share_method: Method of sharing

        Returns:
            Dictionary containing share result for this organization
        """
        try:
            # Get target organization
            target_org = Organization.objects.get(id=org_id)

            # Check trust relationship or create a basic one for sharing
            trust_relationship = TrustRelationship.objects.filter(
                source_organization=sharing_user.organization,
                target_organization=target_org,
                is_active=True,
                status='active'
            ).first()

            if not trust_relationship:
                # For demo purposes, create a basic trust relationship if none exists
                logger.info(f"Creating basic trust relationship between {sharing_user.organization.name} and {target_org.name}")

                # Get default trust level
                from core.trust_management.models.trust_models import TrustLevel
                default_trust_level = TrustLevel.objects.filter(name='basic').first()
                if not default_trust_level:
                    # Create basic trust level if it doesn't exist
                    default_trust_level = TrustLevel.objects.create(
                        name='basic',
                        level='trusted',
                        description='Basic trust level for sharing indicators',
                        numerical_value=50,
                        default_anonymization_level='partial',
                        default_access_level='subscribe',
                        sharing_policies={
                            'allow_indicator_sharing': True,
                            'allow_ttp_sharing': True,
                            'auto_approve_requests': False
                        },
                        is_system_default=True,
                        created_by='system'
                    )

                trust_relationship = TrustRelationship.objects.create(
                    source_organization=sharing_user.organization,
                    target_organization=target_org,
                    trust_level=default_trust_level,
                    relationship_type='bilateral',
                    status='active',
                    is_bilateral=True,
                    is_active=True,
                    anonymization_level='partial',
                    access_level='subscribe',
                    sharing_preferences={
                        'auto_created': True,
                        'purpose': 'indicator_sharing'
                    },
                    notes='Auto-created for indicator sharing'
                )

            # Apply anonymization based on trust level
            anonymized_indicator = self._apply_sharing_anonymization(
                indicator, trust_relationship, anonymization_level
            )

            # Create STIX object for the indicator
            stix_indicator = self._create_stix_indicator(anonymized_indicator, sharing_user.organization)

            # Share based on method
            if share_method == 'taxii':
                share_result = self._share_via_taxii(stix_indicator, target_org, indicator, sharing_user, anonymization_level, share_method)
            elif share_method == 'api':
                share_result = self._share_via_api(stix_indicator, target_org, indicator, sharing_user, anonymization_level, share_method)
            elif share_method == 'email':
                share_result = self._share_via_email(stix_indicator, target_org, indicator, sharing_user, anonymization_level, share_method)
            else:
                raise ValueError(f"Unsupported share method: {share_method}")

            # Record the sharing activity
            SystemActivity.objects.create(
                activity_type='indicator_shared',
                category='indicator',
                title=f'Indicator shared with {target_org.name}',
                description=f'Indicator {indicator.type}: {indicator.value[:50]} shared by {sharing_user.username}',
                indicator=indicator,
                organization=target_org,
                user=sharing_user,
                metadata={
                    'anonymization_level': anonymization_level,
                    'share_method': share_method,
                    'trust_relationship_id': str(trust_relationship.id)
                }
            )

            # Send notifications outside of the main transaction to avoid rollback issues
            try:
                self._send_sharing_notifications(
                    indicator=indicator,
                    target_org=target_org,
                    sharing_user=sharing_user,
                    share_method=share_method,
                    anonymization_level=anonymization_level,
                    stix_indicator=stix_indicator,
                    anonymized_indicator=anonymized_indicator
                )
            except Exception as notification_error:
                # Don't let notification failures stop the sharing process
                logger.error(f"Non-critical error sending notifications: {str(notification_error)}")
                pass

            return {
                'organization_id': org_id,
                'organization_name': target_org.name,
                'success': True,
                'share_method': share_method,
                'anonymization_applied': anonymization_level,
                'stix_id': stix_indicator.get('id', 'unknown')
            }

        except Organization.DoesNotExist:
            raise ValueError(f"Organization with ID {org_id} not found")
        except Exception as e:
            logger.error(f"Error sharing indicator {indicator.id} with organization {org_id}: {str(e)}")
            raise

    def _apply_sharing_anonymization(self, indicator: Indicator, trust_relationship: TrustRelationship,
                                   anonymization_level: str) -> Dict[str, Any]:
        """
        Apply anonymization to indicator based on trust relationship and specified level

        Args:
            indicator: Indicator to anonymize
            trust_relationship: Trust relationship with target organization
            anonymization_level: Requested anonymization level

        Returns:
            Anonymized indicator data
        """
        # Get effective anonymization level based on trust relationship
        effective_level = trust_relationship.get_effective_anonymization_level()

        # Use the more restrictive level
        levels = ['none', 'minimal', 'partial', 'full']
        final_level = max(anonymization_level, effective_level,
                         key=lambda x: levels.index(x) if x in levels else 2)

        # Apply anonymization using the anonymization service
        return self.anonymization_service.anonymize_indicator(indicator, final_level)

    def _create_stix_indicator(self, indicator_data: Dict[str, Any], source_org: Organization) -> Dict[str, Any]:
        """
        Create a STIX indicator object from anonymized indicator data

        Args:
            indicator_data: Anonymized indicator data
            source_org: Source organization

        Returns:
            STIX indicator object
        """
        stix_id = f"indicator--{uuid.uuid4()}"

        # Create STIX indicator
        stix_indicator = {
            'type': 'indicator',
            'id': stix_id,
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'pattern': f"[{indicator_data.get('type', 'file')}:{indicator_data.get('type', 'hashes')}.MD5 = '{indicator_data.get('value', '')}']",
            'labels': ['malicious-activity'],
            'valid_from': timezone.now().isoformat(),
            'x_crisp_source_org': source_org.name,
            'x_crisp_anonymized': indicator_data.get('is_anonymized', False),
            'x_crisp_anonymization_level': indicator_data.get('anonymization_level', 'none')
        }

        # Add confidence if available
        if 'confidence' in indicator_data:
            stix_indicator['confidence'] = indicator_data['confidence']

        # Add description if available
        if 'description' in indicator_data:
            stix_indicator['x_crisp_description'] = indicator_data['description']

        return stix_indicator

    def _share_via_taxii(self, stix_indicator: Dict[str, Any], target_org: Organization,
                        indicator: Indicator, sharing_user, anonymization_level: str,
                        share_method: str) -> Dict[str, Any]:
        """
        Share indicator via TAXII protocol

        Args:
            stix_indicator: STIX indicator object
            target_org: Target organization
            indicator: Original indicator being shared
            sharing_user: User performing the share
            anonymization_level: Level of anonymization applied
            share_method: Method used for sharing

        Returns:
            Share result
        """
        try:
            # Find or create a collection for sharing with this organization
            collection_name = f"shared_with_{target_org.name.lower().replace(' ', '_')}"
            collection, created = Collection.objects.get_or_create(
                alias=collection_name[:50],  # Ensure it fits in the field
                defaults={
                    'title': f'Shared Indicators - {target_org.name}',
                    'description': f'Indicators shared with {target_org.name}',
                    'can_read': True,
                    'can_write': False,
                    'owner': target_org,
                    'media_types': ['application/vnd.oasis.stix+json']
                }
            )

            # Create STIX object in database
            stix_object = STIXObject.objects.create(
                stix_id=stix_indicator['id'],
                stix_type='indicator',
                created=timezone.now(),
                modified=timezone.now(),
                raw_data=stix_indicator,
                source_organization=target_org  # This will be the sharing org in real implementation
            )

            # Add to collection
            CollectionObject.objects.create(
                collection=collection,
                stix_object=stix_object
            )

            # Create sharing relationship instead of duplicating the indicator
            sharing_relationship = self._create_sharing_relationship(
                indicator, target_org, sharing_user, anonymization_level, share_method
            )

            return {
                'method': 'taxii',
                'collection_id': str(collection.id),
                'stix_object_id': str(stix_object.id),
                'sharing_relationship_id': str(sharing_relationship.id) if sharing_relationship else None,
                'success': True
            }

        except Exception as e:
            logger.error(f"Error sharing via TAXII: {str(e)}")
            raise

    def _share_via_api(self, stix_indicator: Dict[str, Any], target_org: Organization,
                      indicator: Indicator, sharing_user, anonymization_level: str,
                      share_method: str) -> Dict[str, Any]:
        """
        Share indicator via API method

        Args:
            stix_indicator: STIX indicator object
            target_org: Target organization
            indicator: Original indicator being shared
            sharing_user: User performing the share
            anonymization_level: Level of anonymization applied
            share_method: Method used for sharing

        Returns:
            Share result
        """
        # Create sharing relationship instead of duplicating the indicator
        sharing_relationship = self._create_sharing_relationship(
            indicator, target_org, sharing_user, anonymization_level, share_method
        )

        return {
            'method': 'api',
            'target_endpoint': f'/api/organizations/{target_org.id}/indicators/',
            'sharing_relationship_id': str(sharing_relationship.id) if sharing_relationship else None,
            'success': True
        }

    def _share_via_email(self, stix_indicator: Dict[str, Any], target_org: Organization,
                        indicator: Indicator, sharing_user, anonymization_level: str,
                        share_method: str) -> Dict[str, Any]:
        """
        Share indicator via email method

        Args:
            stix_indicator: STIX indicator object
            target_org: Target organization
            indicator: Original indicator being shared
            sharing_user: User performing the share
            anonymization_level: Level of anonymization applied
            share_method: Method used for sharing

        Returns:
            Share result
        """
        try:
            # Create sharing relationship instead of duplicating the indicator
            sharing_relationship = self._create_sharing_relationship(
                indicator, target_org, sharing_user, anonymization_level, share_method
            )

            # Email sharing means we only send notifications, no indicator duplication
            return {
                'method': 'email',
                'sharing_relationship_id': str(sharing_relationship.id) if sharing_relationship else None,
                'success': True,
                'note': 'Indicator shared via email notification to organization administrators'
            }

        except Exception as e:
            logger.error(f"Error sharing via email: {str(e)}")
            return {
                'method': 'email',
                'success': False,
                'error': str(e)
            }

    def _format_shared_indicator(self, indicator: Indicator, accessing_user=None) -> Dict[str, Any]:
        """
        Format indicator data for sharing response

        Args:
            indicator: Indicator to format
            accessing_user: User accessing the indicator

        Returns:
            Formatted indicator data
        """
        return {
            'id': indicator.id,
            'type': indicator.type,
            'value': indicator.value,
            'description': getattr(indicator, 'description', ''),
            'confidence': getattr(indicator, 'confidence', 50),
            'first_seen': indicator.first_seen.isoformat() if hasattr(indicator, 'first_seen') and indicator.first_seen else None,
            'last_seen': indicator.last_seen.isoformat() if hasattr(indicator, 'last_seen') and indicator.last_seen else None,
            'threat_feed': {
                'id': indicator.threat_feed.id,
                'name': indicator.threat_feed.name
            } if indicator.threat_feed else None,
            'created_at': indicator.created_at.isoformat(),
            'updated_at': indicator.updated_at.isoformat()
        }

    def get_sharing_permissions(self, user) -> Dict[str, Any]:
        """
        Get sharing permissions for a user

        Args:
            user: User to check permissions for

        Returns:
            Dictionary containing permission information
        """
        try:
            # Get user's organization
            user_org = user.organization if hasattr(user, 'organization') else None
            if not user_org:
                return {
                    'can_share': False,
                    'reason': 'User not associated with an organization'
                }

            # Get trust relationships
            trust_relationships = TrustRelationship.objects.filter(
                source_organization=user_org,
                is_active=True,
                status='active'
            ).select_related('target_organization')

            # Get available organizations to share with
            available_orgs = []
            for relationship in trust_relationships:
                available_orgs.append({
                    'id': str(relationship.target_organization.id),
                    'name': relationship.target_organization.name,
                    'trust_level': relationship.trust_level.name,
                    'access_level': relationship.access_level,
                    'anonymization_level': relationship.anonymization_level
                })

            return {
                'can_share': len(available_orgs) > 0,
                'available_organizations': available_orgs,
                'user_organization': {
                    'id': str(user_org.id),
                    'name': user_org.name,
                    'is_publisher': user_org.is_publisher
                },
                'share_methods': ['taxii', 'api'],
                'anonymization_levels': ['none', 'minimal', 'partial', 'full']
            }

        except Exception as e:
            logger.error(f"Error getting sharing permissions for user {user.username}: {str(e)}")
            return {
                'can_share': False,
                'error': str(e)
            }

    def _send_sharing_notifications(self, indicator: Indicator, target_org: Organization,
                                  sharing_user, share_method: str, anonymization_level: str,
                                  stix_indicator: Dict[str, Any], anonymized_indicator: Dict[str, Any] = None) -> None:
        """
        Send notifications about indicator sharing to target organization

        Args:
            indicator: The shared indicator
            target_org: Target organization receiving the indicator
            sharing_user: User who shared the indicator
            share_method: Method used for sharing (taxii, api, etc.)
            anonymization_level: Level of anonymization applied
            stix_indicator: STIX representation of the indicator
        """
        try:
            from core.services.email_service import UnifiedEmailService
            from core.services.notification_service import NotificationService
            from core.user_management.models import CustomUser

            # Get target organization administrators and publishers
            target_users = CustomUser.objects.filter(
                organization=target_org,
                is_active=True,
                role__in=['admin', 'publisher', 'Admin', 'Publisher', 'OrgAdmin', 'BlueVisionAdmin', 'analyst']
            )

            if not target_users.exists():
                logger.warning(f"No active admins/publishers found for organization {target_org.name}")
                return

            # Prepare notification data - use anonymized indicator if available
            if anonymized_indicator and anonymized_indicator.get('is_anonymized', False):
                indicator_type = anonymized_indicator.get('type', indicator.type).upper() if anonymized_indicator.get('type', indicator.type) else 'UNKNOWN'
                indicator_value = anonymized_indicator.get('value', indicator.value)
                if len(indicator_value) > 50:
                    indicator_value = indicator_value[:50] + '...'
            else:
                indicator_type = indicator.type.upper() if indicator.type else 'UNKNOWN'
                indicator_value = indicator.value[:50] + '...' if len(indicator.value) > 50 else indicator.value

            sharing_org = sharing_user.organization.name if sharing_user.organization else 'Unknown Organization'

            email_service = UnifiedEmailService()
            notification_service = NotificationService()

            # Send email notifications only to users with valid email addresses
            for user in target_users:
                # Validate email address
                if not user.email or not self._is_valid_email(user.email):
                    logger.warning(f"Skipping user {user.username} - invalid email address: {user.email}")
                    continue

                try:
                    # Create detailed email content
                    subject = f"🚨 CRISP Alert: New {indicator_type} Indicator Shared with {target_org.name}"

                    email_body = f"""
Dear {user.first_name or user.username},

Your organization ({target_org.name}) has received a new threat intelligence indicator through the CRISP platform.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 THREAT INTELLIGENCE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Indicator Information:
   • Type: {indicator_type}
   • Value: {indicator_value}
   • Confidence Level: {stix_indicator.get('confidence', 50)}%
   • STIX ID: {stix_indicator.get('id', 'N/A')}

📤 Sharing Details:
   • Shared By: {sharing_user.username}
   • Source Organization: {sharing_org}
   • Share Method: {share_method.upper()}
   • Anonymization Level: {anonymization_level.title()}
   • Date/Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🏢 Target Organization: {target_org.name}
   • Recipient: {user.first_name} {user.last_name} ({user.role})
   • Email: {user.email}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Log into the CRISP platform to view full indicator details
2. Check your organization's "IoC Management" page
3. Review and validate the indicator against your systems
4. Share findings or correlations with the source organization if relevant

📍 This indicator is now available in your threat intelligence feeds and can be used to enhance your organization's security posture.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  SECURITY NOTICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This threat intelligence has been shared through a trusted relationship. Please handle this information according to your organization's security policies and any applicable sharing agreements.

Best regards,
CRISP Platform Team

---
This is an automated notification from the CRISP Threat Intelligence Sharing Platform.
For support, please contact your system administrator.
                    """

                    # Send email notification using threat alert method
                    threat_data = {
                        'indicator_type': indicator_type,
                        'indicator_value': indicator_value,
                        'sharing_organization': sharing_org,
                        'sharing_user': sharing_user.username,
                        'share_method': share_method,
                        'anonymization_level': anonymization_level,
                        'stix_id': stix_indicator.get('id', 'N/A'),
                        'message': email_body,
                        'subject': subject
                    }

                    email_result = email_service.send_threat_alert_email(
                        recipients=[user.email],
                        threat_data=threat_data,
                        alert_level='INFO',
                        user=sharing_user
                    )

                    if email_result.get('success'):
                        logger.info(f"Email notification sent to {user.email} about shared indicator")
                    else:
                        logger.warning(f"Failed to send email to {user.email}: {email_result.get('error')}")

                    # Create in-app notification in a separate transaction to avoid rollback
                    try:
                        from core.alerts.models import Notification
                        from django.db import transaction

                        logger.info(f"Attempting to create notification for user {user.username} in organization {target_org.name}")

                        # Use a separate transaction to ensure notification is saved even if other parts fail
                        with transaction.atomic():
                            notification = Notification.objects.create(
                                notification_type='security_alert',
                                title=f"New {indicator_type} Indicator Shared",
                                message=f"Your organization has received new threat intelligence from {sharing_org}. Indicator: {indicator_value}",
                                priority='high',
                                recipient=user,
                                organization=target_org,
                                related_object_type='indicator',
                                related_object_id=str(indicator.id),
                                metadata={
                                    'indicator_id': indicator.id,
                                    'indicator_type': indicator_type,
                                    'indicator_value': indicator_value,
                                    'sharing_organization': sharing_org,
                                    'sharing_user': sharing_user.username,
                                    'share_method': share_method,
                                    'anonymization_level': anonymization_level,
                                    'stix_id': stix_indicator.get('id'),
                                    'notification_category': 'threat_intelligence_shared'
                                }
                            )

                        logger.info(f"✅ In-app notification created successfully for {user.username} (ID: {notification.id})")

                    except Exception as notification_error:
                        logger.error(f"❌ Failed to create in-app notification for {user.username}: {str(notification_error)}")
                        logger.error(f"Notification error details: {type(notification_error).__name__}")
                        import traceback
                        logger.error(f"Full traceback: {traceback.format_exc()}")

                except Exception as user_error:
                    logger.error(f"Error sending notifications to user {user.username}: {str(user_error)}")
                    continue

        except Exception as e:
            logger.error(f"Error sending sharing notifications: {str(e)}")
            # Don't raise the exception as notifications are not critical for the sharing process

    def _create_sharing_relationship(self, indicator: Indicator, target_org: Organization,
                                   sharing_user, anonymization_level: str, share_method: str) -> Optional[IndicatorSharingRelationship]:
        """
        Create a sharing relationship between an indicator and target organization

        Args:
            indicator: Original indicator being shared
            target_org: Target organization
            sharing_user: User performing the share
            anonymization_level: Level of anonymization applied
            share_method: Method used for sharing

        Returns:
            Created IndicatorSharingRelationship object or None if creation failed
        """
        try:
            # Use get_or_create to avoid duplicates
            sharing_relationship, created = IndicatorSharingRelationship.objects.get_or_create(
                indicator=indicator,
                target_organization=target_org,
                defaults={
                    'shared_by_user': sharing_user,
                    'share_method': share_method,
                    'anonymization_level': anonymization_level,
                    'is_active': True,
                    'metadata': {
                        'shared_via': share_method,
                        'original_anonymization_level': anonymization_level,
                        'sharing_timestamp': timezone.now().isoformat()
                    }
                }
            )

            if not created:
                # Update the relationship if it already exists
                sharing_relationship.is_active = True
                sharing_relationship.anonymization_level = anonymization_level
                sharing_relationship.share_method = share_method
                sharing_relationship.metadata.update({
                    'last_shared_at': timezone.now().isoformat(),
                    'updated_anonymization_level': anonymization_level
                })
                sharing_relationship.save()
                logger.info(f"Updated existing sharing relationship {sharing_relationship.id}")
            else:
                logger.info(f"Created new sharing relationship {sharing_relationship.id} for indicator {indicator.id} to organization {target_org.name}")

            return sharing_relationship

        except Exception as e:
            logger.error(f"Error creating sharing relationship: {str(e)}")
            return None

    def get_shared_indicators_for_organization(self, organization: Organization) -> List[Dict[str, Any]]:
        """
        Get all indicators shared with a specific organization

        Args:
            organization: Target organization

        Returns:
            List of shared indicators with metadata
        """
        try:
            sharing_relationships = IndicatorSharingRelationship.objects.filter(
                target_organization=organization,
                is_active=True
            ).select_related('indicator', 'indicator__threat_feed', 'shared_by_user')

            shared_indicators = []
            for relationship in sharing_relationships:
                indicator = relationship.indicator
                shared_indicators.append({
                    'id': indicator.id,
                    'type': indicator.type,
                    'value': indicator.value,
                    'description': indicator.description,
                    'confidence': indicator.confidence,
                    'first_seen': indicator.first_seen.isoformat() if indicator.first_seen else None,
                    'last_seen': indicator.last_seen.isoformat() if indicator.last_seen else None,
                    'threat_feed': {
                        'id': indicator.threat_feed.id,
                        'name': indicator.threat_feed.name,
                        'owner': indicator.threat_feed.owner.name if indicator.threat_feed.owner else None
                    },
                    'created_at': indicator.created_at.isoformat(),
                    'updated_at': indicator.updated_at.isoformat(),
                    'sharing_info': {
                        'shared_at': relationship.shared_at.isoformat(),
                        'shared_by': relationship.shared_by_user.username if relationship.shared_by_user else 'Unknown',
                        'sharing_organization': relationship.shared_by_user.organization.name if relationship.shared_by_user and relationship.shared_by_user.organization else 'Unknown',
                        'share_method': relationship.share_method,
                        'anonymization_level': relationship.anonymization_level,
                        'is_shared': True,
                        'relationship_id': relationship.id
                    }
                })

            return shared_indicators

        except Exception as e:
            logger.error(f"Error getting shared indicators for organization {organization.name}: {str(e)}")
            return []

    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email address format

        Args:
            email: Email address to validate

        Returns:
            Boolean indicating if email is valid
        """
        import re

        if not email or not isinstance(email, str):
            return False

        # Basic email validation pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        # Check if it matches the pattern
        if not re.match(pattern, email):
            return False

        # Additional checks for common invalid patterns
        invalid_patterns = [
            r'\.{2,}',  # Multiple consecutive dots
            r'^\.+',    # Starting with dots
            r'\.+$',    # Ending with dots
            r'@\.+',    # @ followed by dots
            r'\.+@',    # dots followed by @
        ]

        for invalid_pattern in invalid_patterns:
            if re.search(invalid_pattern, email):
                return False

        return True