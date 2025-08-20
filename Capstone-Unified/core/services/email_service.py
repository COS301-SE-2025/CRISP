"""
Unified Email Service - Trust-aware email notifications
Merges Gmail SMTP capabilities with Django email system and trust-based recipient filtering
"""

import smtplib
import logging
import os
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from datetime import datetime
from core.models.models import CustomUser, Organization, AuthenticationLog
from .access_control_service import AccessControlService
from .audit_service import AuditService

logger = logging.getLogger(__name__)

class UnifiedEmailService:
    """
    Unified email service with trust-aware recipient filtering and multiple delivery methods.
    Supports both Django email system and direct Gmail SMTP with comprehensive logging.
    """
    
    def __init__(self):
        """Initialize the unified email service"""
        self.access_control = AccessControlService()
        self.audit_service = AuditService()
        
        # Email configuration
        self.email_host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.email_port = getattr(settings, 'EMAIL_PORT', 587)
        self.email_use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
        self.email_use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
        self.email_host_user = getattr(settings, 'EMAIL_HOST_USER', None)
        self.email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        
        # Default sender information
        self.default_sender = {
            'name': getattr(settings, 'CRISP_SENDER_NAME', 'CRISP Threat Intelligence'),
            'email': getattr(settings, 'CRISP_SENDER_EMAIL', self.email_host_user or 'noreply@crisp-system.org')
        }
        
        # Environment fallbacks
        if not self.email_host_user:
            self.email_host_user = os.getenv('EMAIL_HOST_USER')
        if not self.email_host_password:
            self.email_host_password = os.getenv('EMAIL_HOST_PASSWORD')
    
    def send_user_invitation_email(self, email: str, organization: Organization, 
                                  inviter: CustomUser, invitation_token: str) -> Dict[str, Any]:
        """
        Send user invitation email with trust-aware content
        
        Args:
            email: Invitee email address
            organization: Organization inviting the user
            inviter: User sending the invitation
            invitation_token: Secure invitation token
            
        Returns:
            Dictionary with send result
        """
        try:
            # Check if inviter can send invitations
            if not self.access_control.can_invite_to_organization(inviter, organization):
                return {
                    'success': False,
                    'message': 'Insufficient permissions to send invitations',
                    'error_type': 'permission_denied'
                }
            
            subject = f"Invitation to join {organization.name} on CRISP"
            
            # Generate invitation URL (in production this would be the actual domain)
            invitation_url = f"https://crisp-platform.org/accept-invitation?token={invitation_token}"
            
            # Generate HTML content
            html_content = self._generate_invitation_html(
                email, organization, inviter, invitation_url
            )
            
            # Generate text content
            text_content = self._generate_invitation_text(
                email, organization, inviter, invitation_url
            )
            
            # Send email
            result = self._send_email_with_fallback(
                to_emails=[email],
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                email_type='user_invitation',
                user=inviter
            )
            
            # Log the invitation email
            if result['success']:
                self.audit_service.log_user_action(
                    user=inviter,
                    action='invitation_email_sent',
                    success=True,
                    additional_data={
                        'invitee_email': email,
                        'organization_id': str(organization.id),
                        'organization_name': organization.name
                    }
                )
            else:
                self.audit_service.log_security_event(
                    action='invitation_email_failed',
                    user=inviter,
                    success=False,
                    failure_reason=result.get('message', 'Unknown error'),
                    additional_data={
                        'invitee_email': email,
                        'organization_id': str(organization.id)
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending invitation email: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send invitation email: {str(e)}',
                'error_type': 'system_error'
            }
    
    def send_password_reset_email(self, user: CustomUser, reset_token: str) -> Dict[str, Any]:
        """
        Send password reset email
        
        Args:
            user: User requesting password reset
            reset_token: Secure reset token
            
        Returns:
            Dictionary with send result
        """
        try:
            subject = "Password Reset Request - CRISP Platform"
            
            # Generate reset URL (in production this would be the actual domain)
            reset_url = f"https://crisp-platform.org/reset-password?token={reset_token}"
            
            # Generate HTML content
            html_content = self._generate_password_reset_html(user, reset_url)
            
            # Generate text content
            text_content = self._generate_password_reset_text(user, reset_url)
            
            # Send email
            result = self._send_email_with_fallback(
                to_emails=[user.email],
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                email_type='password_reset',
                user=user
            )
            
            # Log the password reset email
            if result['success']:
                self.audit_service.log_user_action(
                    user=user,
                    action='password_reset_email_sent',
                    success=True,
                    additional_data={'email': user.email}
                )
            else:
                self.audit_service.log_security_event(
                    action='password_reset_email_failed',
                    user=user,
                    success=False,
                    failure_reason=result.get('message', 'Unknown error'),
                    additional_data={'email': user.email}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send password reset email: {str(e)}',
                'error_type': 'system_error'
            }
    
    def send_threat_alert_email(self, recipients: List[str], threat_data: Dict[str, Any],
                               alert_level: str = 'HIGH', user: CustomUser = None) -> Dict[str, Any]:
        """
        Send threat alert email with trust-aware recipient filtering
        
        Args:
            recipients: List of email addresses
            threat_data: Dictionary containing threat information
            alert_level: Alert severity level
            user: User sending the alert (for permissions)
            
        Returns:
            Dictionary with send result
        """
        try:
            # Filter recipients based on trust relationships if user is provided
            if user:
                filtered_recipients = self._filter_recipients_by_trust(recipients, user)
                if not filtered_recipients:
                    return {
                        'success': False,
                        'message': 'No authorized recipients for threat alert',
                        'error_type': 'no_recipients'
                    }
                recipients = filtered_recipients
            
            subject = f"[CRISP Alert - {alert_level}] {threat_data.get('title', 'Security Threat Detected')}"
            
            # Generate HTML content
            html_content = self._generate_threat_alert_html(threat_data, alert_level)
            
            # Generate text content
            text_content = self._generate_threat_alert_text(threat_data, alert_level)
            
            # Send email
            result = self._send_email_with_fallback(
                to_emails=recipients,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                email_type='threat_alert',
                priority=alert_level.lower(),
                user=user
            )
            
            # Log the threat alert
            if result['success']:
                self.audit_service.log_security_event(
                    action='threat_alert_sent',
                    user=user,
                    success=True,
                    severity=alert_level.lower(),
                    additional_data={
                        'recipients_count': len(recipients),
                        'threat_type': threat_data.get('threat_type'),
                        'alert_level': alert_level
                    }
                )
            else:
                self.audit_service.log_security_event(
                    action='threat_alert_failed',
                    user=user,
                    success=False,
                    failure_reason=result.get('message', 'Unknown error'),
                    severity='high',
                    additional_data={
                        'intended_recipients': len(recipients),
                        'threat_type': threat_data.get('threat_type')
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending threat alert email: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send threat alert: {str(e)}',
                'error_type': 'system_error'
            }
    
    def send_feed_update_notification(self, recipients: List[str], feed_name: str,
                                    update_summary: Dict[str, Any], user: CustomUser = None) -> Dict[str, Any]:
        """
        Send feed update notification with trust-aware filtering
        
        Args:
            recipients: List of email addresses
            feed_name: Name of the updated threat feed
            update_summary: Summary of feed updates
            user: User sending the notification
            
        Returns:
            Dictionary with send result
        """
        try:
            # Filter recipients based on trust relationships if user is provided
            if user:
                filtered_recipients = self._filter_recipients_by_trust(recipients, user)
                if not filtered_recipients:
                    return {
                        'success': False,
                        'message': 'No authorized recipients for feed notification',
                        'error_type': 'no_recipients'
                    }
                recipients = filtered_recipients
            
            subject = f"[CRISP] Threat Feed Update: {feed_name}"
            
            # Generate HTML content
            html_content = self._generate_feed_update_html(feed_name, update_summary)
            
            # Generate text content
            text_content = self._generate_feed_update_text(feed_name, update_summary)
            
            # Send email
            result = self._send_email_with_fallback(
                to_emails=recipients,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                email_type='feed_notification',
                user=user
            )
            
            # Log the feed notification
            if result['success']:
                self.audit_service.log_user_action(
                    user=user,
                    action='feed_notification_sent',
                    success=True,
                    additional_data={
                        'feed_name': feed_name,
                        'recipients_count': len(recipients),
                        'update_summary': update_summary
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending feed notification: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send feed notification: {str(e)}',
                'error_type': 'system_error'
            }
    
    def _send_email_with_fallback(self, to_emails: List[str], subject: str, 
                                 html_content: str, text_content: str = None,
                                 email_type: str = 'system_notification',
                                 priority: str = 'medium', user: CustomUser = None) -> Dict[str, Any]:
        """
        Send email with multiple fallback methods: Django -> Gmail SMTP -> Simple text
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content
            text_content: Plain text content
            email_type: Type of email for logging
            priority: Email priority
            user: User sending the email
            
        Returns:
            Dictionary with send result
        """
        # Try Django email system first
        try:
            return self._send_email_django(to_emails, subject, html_content, text_content)
        except Exception as django_error:
            logger.warning(f"Django email failed, trying Gmail SMTP: {str(django_error)}")
            
            # Fallback to Gmail SMTP
            try:
                return self._send_email_smtp(to_emails, subject, html_content, text_content)
            except Exception as smtp_error:
                logger.warning(f"Gmail SMTP failed, trying simple text: {str(smtp_error)}")
                
                # Final fallback to simple text email
                try:
                    return self._send_simple_email(to_emails, subject, text_content or html_content)
                except Exception as simple_error:
                    logger.error(f"All email methods failed: {str(simple_error)}")
                    return {
                        'success': False,
                        'message': f'All email delivery methods failed. Last error: {str(simple_error)}',
                        'error_type': 'delivery_failure'
                    }
    
    def _send_email_django(self, to_emails: List[str], subject: str, 
                          html_content: str, text_content: str = None) -> Dict[str, Any]:
        """Send email using Django's email system"""
        from_email = f"{self.default_sender['name']} <{self.default_sender['email']}>"
        
        # Use EmailMultiAlternatives for HTML + text email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content or html_content,
            from_email=from_email,
            to=to_emails
        )
        
        if html_content and text_content:
            msg.attach_alternative(html_content, "text/html")
        
        result = msg.send()
        
        if result:
            return {
                'success': True,
                'message': f'Email sent successfully via Django to {len(to_emails)} recipients',
                'method': 'django',
                'recipients': len(to_emails)
            }
        else:
            raise Exception("Django send() returned 0")
    
    def _send_email_smtp(self, to_emails: List[str], subject: str, 
                        html_content: str, text_content: str = None) -> Dict[str, Any]:
        """Send email using direct Gmail SMTP"""
        if not self.email_host_user or not self.email_host_password:
            raise Exception("Gmail SMTP credentials not configured")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.default_sender['name']} <{self.default_sender['email']}>"
        msg['To'] = ', '.join(to_emails)
        
        # Add text content
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        # Add HTML content
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Send email
        if self.email_use_ssl:
            import ssl
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(self.email_host, self.email_port, context=context)
        else:
            server = smtplib.SMTP(self.email_host, self.email_port)
            if self.email_use_tls:
                server.starttls()
        
        server.login(self.email_host_user, self.email_host_password)
        server.send_message(msg)
        server.quit()
        
        return {
            'success': True,
            'message': f'Email sent successfully via Gmail SMTP to {len(to_emails)} recipients',
            'method': 'smtp',
            'recipients': len(to_emails)
        }
    
    def _send_simple_email(self, to_emails: List[str], subject: str, content: str) -> Dict[str, Any]:
        """Send simple text email as final fallback"""
        from_email = self.default_sender['email']
        
        result = send_mail(
            subject=subject,
            message=content,
            from_email=from_email,
            recipient_list=to_emails,
            fail_silently=False
        )
        
        if result:
            return {
                'success': True,
                'message': f'Simple email sent successfully to {len(to_emails)} recipients',
                'method': 'simple',
                'recipients': len(to_emails)
            }
        else:
            raise Exception("Simple email send() returned 0")
    
    def _filter_recipients_by_trust(self, recipients: List[str], user: CustomUser) -> List[str]:
        """
        Filter email recipients based on trust relationships
        
        Args:
            recipients: List of email addresses
            user: User sending the email
            
        Returns:
            Filtered list of authorized recipients
        """
        if not user or user.role == 'BlueVisionAdmin':
            # BlueVision admins can email anyone
            return recipients
        
        try:
            # Get accessible organizations for the user
            accessible_orgs = self.access_control.get_accessible_organizations(user)
            accessible_org_ids = {str(org.id) for org in accessible_orgs}
            
            # Filter recipients by checking if their organizations are accessible
            filtered_recipients = []
            for email in recipients:
                try:
                    # Find user by email
                    recipient_user = CustomUser.objects.get(email=email, is_active=True)
                    if (recipient_user.organization and 
                        str(recipient_user.organization.id) in accessible_org_ids):
                        filtered_recipients.append(email)
                except CustomUser.DoesNotExist:
                    # External email addresses (not CRISP users) are allowed for admins and publishers
                    if user.role in ['admin', 'publisher']:
                        filtered_recipients.append(email)
            
            return filtered_recipients
            
        except Exception as e:
            logger.error(f"Error filtering recipients by trust: {str(e)}")
            # If filtering fails, only allow internal organization for safety
            return [] if user.role == 'viewer' else recipients
    
    def _generate_invitation_html(self, email: str, organization: Organization, 
                                 inviter: CustomUser, invitation_url: str) -> str:
        """Generate HTML content for user invitations"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CRISP Invitation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .invitation-box {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .accept-button {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 15px 0; }}
                .accept-button:hover {{ background: #0056b3; }}
                .footer {{ background: #343a40; color: white; padding: 15px; text-align: center; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 You're Invited to CRISP</h1>
                    <p>Cyber Risk Information Sharing Platform</p>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p><strong>{inviter.get_full_name() or inviter.username}</strong> has invited you to join <strong>{organization.name}</strong> on the CRISP platform.</p>
                    
                    <div class="invitation-box">
                        <h3>Join {organization.name}</h3>
                        <p>Organization Type: {organization.get_organization_type_display()}</p>
                        <a href="{invitation_url}" class="accept-button">Accept Invitation</a>
                    </div>
                    
                    <p><strong>What is CRISP?</strong></p>
                    <p>CRISP is a secure threat intelligence sharing platform that enables organizations to collaborate and share cybersecurity information while maintaining appropriate trust levels and anonymization.</p>
                    
                    <p><strong>Getting Started:</strong></p>
                    <ul>
                        <li>Click the "Accept Invitation" button above</li>
                        <li>Create your account and set up your profile</li>
                        <li>Start accessing threat intelligence feeds</li>
                        <li>Collaborate with trusted organizations</li>
                    </ul>
                    
                    <p><em>This invitation will expire in 7 days.</em></p>
                </div>
                <div class="footer">
                    <p>CRISP - Cyber Risk Information Sharing Platform</p>
                    <p>This invitation was sent by {inviter.get_full_name() or inviter.username} from {organization.name}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_invitation_text(self, email: str, organization: Organization, 
                                 inviter: CustomUser, invitation_url: str) -> str:
        """Generate plain text content for user invitations"""
        return f"""
CRISP PLATFORM INVITATION
{'='*50}

Hello,

{inviter.get_full_name() or inviter.username} has invited you to join {organization.name} on the CRISP platform.

ORGANIZATION DETAILS:
- Name: {organization.name}
- Type: {organization.get_organization_type_display()}

WHAT IS CRISP?
CRISP is a secure threat intelligence sharing platform that enables organizations to collaborate and share cybersecurity information while maintaining appropriate trust levels and anonymization.

TO ACCEPT THIS INVITATION:
Please visit the following link to create your account:
{invitation_url}

GETTING STARTED:
1. Click the invitation link above
2. Create your account and set up your profile
3. Start accessing threat intelligence feeds
4. Collaborate with trusted organizations

This invitation will expire in 7 days.

---
CRISP - Cyber Risk Information Sharing Platform
This invitation was sent by {inviter.get_full_name() or inviter.username} from {organization.name}
        """
    
    def _generate_password_reset_html(self, user: CustomUser, reset_url: str) -> str:
        """Generate HTML content for password reset"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CRISP Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .reset-box {{ background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .reset-button {{ display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 15px 0; }}
                .reset-button:hover {{ background: #1e7e34; }}
                .security-note {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ffc107; }}
                .footer {{ background: #343a40; color: white; padding: 15px; text-align: center; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                    <p>CRISP Platform</p>
                </div>
                <div class="content">
                    <p>Hello {user.get_full_name() or user.username},</p>
                    <p>We received a request to reset your password for your CRISP account.</p>
                    
                    <div class="reset-box">
                        <h3>Reset Your Password</h3>
                        <p>Click the button below to create a new password:</p>
                        <a href="{reset_url}" class="reset-button">Reset Password</a>
                    </div>
                    
                    <div class="security-note">
                        <h4>🛡️ Security Information</h4>
                        <ul>
                            <li>This reset link will expire in 24 hours</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>For security, this link can only be used once</li>
                            <li>Contact support if you continue having issues</li>
                        </ul>
                    </div>
                    
                    <p><strong>Account Details:</strong></p>
                    <ul>
                        <li>Username: {user.username}</li>
                        <li>Email: {user.email}</li>
                        <li>Organization: {user.organization.name if user.organization else 'None'}</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>CRISP - Cyber Risk Information Sharing Platform</p>
                    <p>If you didn't request this password reset, please contact support immediately.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_password_reset_text(self, user: CustomUser, reset_url: str) -> str:
        """Generate plain text content for password reset"""
        return f"""
CRISP PASSWORD RESET REQUEST
{'='*50}

Hello {user.get_full_name() or user.username},

We received a request to reset your password for your CRISP account.

TO RESET YOUR PASSWORD:
Please visit the following link:
{reset_url}

SECURITY INFORMATION:
- This reset link will expire in 24 hours
- If you didn't request this reset, please ignore this email
- For security, this link can only be used once
- Contact support if you continue having issues

ACCOUNT DETAILS:
- Username: {user.username}
- Email: {user.email}
- Organization: {user.organization.name if user.organization else 'None'}

---
CRISP - Cyber Risk Information Sharing Platform
If you didn't request this password reset, please contact support immediately.
        """
    
    def _generate_threat_alert_html(self, threat_data: Dict[str, Any], alert_level: str) -> str:
        """Generate HTML content for threat alerts"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CRISP Threat Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .alert-level {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; }}
                .critical {{ background-color: #dc3545; color: white; }}
                .high {{ background-color: #fd7e14; color: white; }}
                .medium {{ background-color: #ffc107; color: black; }}
                .low {{ background-color: #28a745; color: white; }}
                .threat-details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ background: #343a40; color: white; padding: 15px; text-align: center; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 CRISP Threat Alert</h1>
                    <div class="alert-level {alert_level.lower()}">{alert_level} PRIORITY</div>
                </div>
                <div class="content">
                    <h2>{threat_data.get('title', 'Security Threat Detected')}</h2>
                    <p><strong>Detected:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    
                    <div class="threat-details">
                        <h3>Threat Details</h3>
                        <ul>
                            <li><strong>Type:</strong> {threat_data.get('threat_type', 'Unknown')}</li>
                            <li><strong>Severity:</strong> {threat_data.get('severity', 'Unknown')}</li>
                            <li><strong>Confidence:</strong> {threat_data.get('confidence', 'Unknown')}</li>
                            <li><strong>Source:</strong> {threat_data.get('source', 'Internal')}</li>
                        </ul>
                    </div>
                    
                    <p><strong>Recommended Actions:</strong></p>
                    <ul>
                        <li>Review affected systems immediately</li>
                        <li>Check security logs for related activities</li>
                        <li>Contact security team if suspicious activity found</li>
                        <li>Document any findings in incident response system</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>CRISP - Cyber Risk Information Sharing Platform</p>
                    <p>This is an automated security alert. Respond according to your incident response procedures.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_threat_alert_text(self, threat_data: Dict[str, Any], alert_level: str) -> str:
        """Generate plain text content for threat alerts"""
        return f"""
CRISP THREAT ALERT - {alert_level} PRIORITY
{'='*50}

Threat: {threat_data.get('title', 'Security Threat Detected')}
Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

THREAT DETAILS:
- Type: {threat_data.get('threat_type', 'Unknown')}
- Severity: {threat_data.get('severity', 'Unknown')}
- Confidence: {threat_data.get('confidence', 'Unknown')}
- Source: {threat_data.get('source', 'Internal')}

RECOMMENDED ACTIONS:
1. Review affected systems immediately
2. Check security logs for related activities
3. Contact security team if suspicious activity found
4. Document any findings in incident response system

---
CRISP - Cyber Risk Information Sharing Platform
This is an automated security alert. Respond according to your incident response procedures.
        """
    
    def _generate_feed_update_html(self, feed_name: str, update_summary: Dict[str, Any]) -> str:
        """Generate HTML content for feed updates"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CRISP Feed Update</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .update-summary {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin: 15px 0; }}
                .stat-item {{ text-align: center; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                .stat-number {{ font-size: 1.5em; font-weight: bold; color: #007bff; }}
                .footer {{ background: #343a40; color: white; padding: 15px; text-align: center; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Feed Update Notification</h1>
                    <p>{feed_name}</p>
                </div>
                <div class="content">
                    <h2>New Threat Intelligence Available</h2>
                    <p>The threat feed "{feed_name}" has been updated with new intelligence data.</p>
                    
                    <div class="update-summary">
                        <h3>Update Summary</h3>
                        <div class="stats">
                            <div class="stat-item">
                                <div class="stat-number">{update_summary.get('new_indicators', 0)}</div>
                                <div>New Indicators</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{update_summary.get('new_ttps', 0)}</div>
                                <div>New TTPs</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{update_summary.get('updated_items', 0)}</div>
                                <div>Updated Items</div>
                            </div>
                        </div>
                    </div>
                    
                    <p><strong>Last Updated:</strong> {update_summary.get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))}</p>
                    <p><strong>Update Source:</strong> {update_summary.get('source', 'Internal')}</p>
                    
                    <p>You can access the updated feed data through your CRISP dashboard.</p>
                </div>
                <div class="footer">
                    <p>CRISP - Cyber Risk Information Sharing Platform</p>
                    <p>This is an automated notification. You can manage your subscription preferences in your account settings.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_feed_update_text(self, feed_name: str, update_summary: Dict[str, Any]) -> str:
        """Generate plain text content for feed updates"""
        return f"""
CRISP FEED UPDATE NOTIFICATION
{'='*50}

Feed: {feed_name}
Updated: {update_summary.get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))}

UPDATE SUMMARY:
- New Indicators: {update_summary.get('new_indicators', 0)}
- New TTPs: {update_summary.get('new_ttps', 0)}
- Updated Items: {update_summary.get('updated_items', 0)}
- Source: {update_summary.get('source', 'Internal')}

You can access the updated feed data through your CRISP dashboard.

---
CRISP - Cyber Risk Information Sharing Platform
This is an automated notification. You can manage your subscription preferences in your account settings.
        """