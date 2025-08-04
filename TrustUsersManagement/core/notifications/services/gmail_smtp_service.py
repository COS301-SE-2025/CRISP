"""
Gmail SMTP Email Service
File: core/services/gmail_smtp_service.py

Service for sending email notifications via Gmail SMTP.
"""

import smtplib
import logging
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)


class GmailSMTPService:
    """
    Service for sending emails via Gmail SMTP.
    """
    
    def __init__(self, email_host_user: str = None, email_host_password: str = None):
        """
        Initialize Gmail SMTP service.
        
        Args:
            email_host_user: Gmail username (defaults to settings.EMAIL_HOST_USER)
            email_host_password: Gmail app password (defaults to settings.EMAIL_HOST_PASSWORD)
        """
        self.email_host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.email_port = getattr(settings, 'EMAIL_PORT', 587)
        self.email_use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
        self.email_use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
        self.email_host_user = email_host_user or getattr(settings, 'EMAIL_HOST_USER', None)
        self.email_host_password = email_host_password or getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        
        # Default sender information
        self.default_sender = {
            'name': getattr(settings, 'CRISP_SENDER_NAME', 'CRISP Threat Intelligence'),
            'email': getattr(settings, 'CRISP_SENDER_EMAIL', self.email_host_user)
        }
    
    def send_email(self, to_emails: List[str], subject: str, html_content: str, 
                   text_content: str = None, sender_name: str = None, 
                   sender_email: str = None, email_type: str = 'system_notification',
                   alert_id: str = None, priority: str = None, user=None) -> Dict[str, Any]:
        """
        Send an email via Gmail SMTP.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            sender_name: Sender name (optional, uses default)
            sender_email: Sender email (optional, uses default)
            email_type: Type of email (threat_alert, feed_notification, etc.)
            alert_id: Alert ID for tracking
            priority: Email priority
            user: User sending the email
            
        Returns:
            Dictionary with send result
        """
        # Create email log entry
        email_log = None
        try:
            from core.alerts.models import EmailLog
            email_log = EmailLog.objects.create(
                email_type=email_type,
                recipient_emails=to_emails,
                sender_email=sender_email or self.default_sender['email'],
                subject=subject,
                alert_id=alert_id,
                priority=priority,
                sent_by=user,
                organization=user.organization if user else None,
                status='pending'
            )
        except Exception as log_error:
            # Don't fail email sending if logging fails
            pass
        
        try:
            # Validate recipients
            if not to_emails or not any(email.strip() for email in to_emails):
                # Update email log on failure
                if email_log:
                    try:
                        email_log.status = 'failed'
                        email_log.error_message = 'No recipients provided'
                        email_log.save()
                    except:
                        pass
                        
                logger.error("No recipients provided")
                return {
                    'success': False,
                    'message': 'No recipients provided',
                    'error_type': 'validation'
                }
            
            # Validate content
            if not html_content and not text_content:
                # Update email log on failure
                if email_log:
                    try:
                        email_log.status = 'failed'
                        email_log.error_message = 'No content provided'
                        email_log.save()
                    except:
                        pass
                        
                logger.error("No content provided")
                return {
                    'success': False,
                    'message': 'No content provided',
                    'error_type': 'validation'
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{sender_name or self.default_sender['name']} <{sender_email or self.default_sender['email']}>"
            msg['To'] = ', '.join(to_emails)
            
            # Add text content if provided
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
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                server = smtplib.SMTP_SSL(self.email_host, self.email_port, context=context)
            else:
                server = smtplib.SMTP(self.email_host, self.email_port)
                if self.email_use_tls:
                    server.starttls()
            
            server.login(self.email_host_user, self.email_host_password)
            server.send_message(msg)
            server.quit()
            
            # Update email log on success
            if email_log:
                try:
                    email_log.status = 'sent'
                    email_log.save()
                except:
                    pass
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return {
                'success': True,
                'message': 'Email sent successfully',
                'recipients': len(to_emails)
            }
            
        except smtplib.SMTPAuthenticationError as e:
            # Update email log on failure
            if email_log:
                try:
                    email_log.status = 'failed'
                    email_log.error_message = f'Authentication failed: {str(e)}'
                    email_log.save()
                except:
                    pass
            
            logger.error(f"Authentication failed: {str(e)}")
            return {
                'success': False,
                'message': f'Authentication failed: {str(e)}',
                'error_type': 'authentication'
            }
        except smtplib.SMTPConnectError as e:
            # Update email log on failure
            if email_log:
                try:
                    email_log.status = 'failed'
                    email_log.error_message = f'Connection failed: {str(e)}'
                    email_log.save()
                except:
                    pass
                    
            logger.error(f"Connection failed: {str(e)}")
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'error_type': 'connection'
            }
        except Exception as e:
            # Update email log on failure
            if email_log:
                try:
                    email_log.status = 'failed'
                    email_log.error_message = f'Unexpected error: {str(e)}'
                    email_log.save()
                except:
                    pass
                    
            logger.error(f"Unexpected error sending email: {str(e)}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}',
                'error_type': 'unknown'
            }
    
    def send_threat_alert_email(self, recipient_emails: List[str], alert_data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """
        Send a threat alert email.
        
        Args:
            recipient_emails: List of recipient email addresses
            alert_data: Alert data containing threat information
            
        Returns:
            Dictionary with send result
        """
        alert_type = alert_data.get('alert_type', 'Unknown Alert')
        priority = alert_data.get('priority', 'medium')
        
        # Create subject based on priority
        priority_prefix = {
            'critical': '🚨 CRITICAL',
            'high': '⚠️ HIGH',
            'medium': '📊 MEDIUM',
            'low': '📝 LOW',
            'info': 'ℹ️ INFO'
        }.get(priority, '📊')
        
        subject = f"{priority_prefix} CRISP Threat Alert: {alert_type}"
        
        # Generate HTML content
        html_content = self._generate_threat_alert_html(alert_data)
        
        # Generate text content
        text_content = self._generate_threat_alert_text(alert_data)
        
        return self.send_email(
            to_emails=recipient_emails,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            email_type='threat_alert',
            alert_id=alert_data.get('alert_id'),
            priority=priority,
            user=user
        )
    
    def send_feed_notification_email(self, recipient_emails: List[str], notification_data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """
        Send a feed notification email.
        
        Args:
            recipient_emails: List of recipient email addresses
            notification_data: Notification data
            
        Returns:
            Dictionary with send result
        """
        notification_type = notification_data.get('notification_type', 'Feed Update')
        feed_name = notification_data.get('feed_name', 'Unknown Feed')
        
        subject = f"CRISP Feed Notification: {notification_type} - {feed_name}"
        
        # Generate HTML content
        html_content = self._generate_feed_notification_html(notification_data)
        
        # Generate text content
        text_content = self._generate_feed_notification_text(notification_data)
        
        return self.send_email(
            to_emails=recipient_emails,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            email_type='feed_notification',
            alert_id=notification_data.get('notification_id'),
            priority='medium',
            user=user
        )
    
    def _generate_threat_alert_html(self, alert_data: Dict[str, Any]) -> str:
        """Generate HTML content for threat alert email."""
        alert_type = alert_data.get('alert_type', 'Unknown Alert')
        priority = alert_data.get('priority', 'medium')
        generated_at = alert_data.get('generated_at', timezone.now())
        data = alert_data.get('data', {})
        
        # Priority color mapping
        priority_colors = {
            'critical': '#dc3545',  # Red
            'high': '#fd7e14',      # Orange
            'medium': '#ffc107',    # Yellow
            'low': '#28a745',       # Green
            'info': '#17a2b8'       # Blue
        }
        
        priority_color = priority_colors.get(priority, '#6c757d')
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CRISP Threat Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: {priority_color}; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .alert-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .detail-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .footer {{ background-color: #e9ecef; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; color: #6c757d; }}
                .priority-badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; background-color: {priority_color}; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ CRISP Threat Alert</h1>
                    <p>Cyber Risk Information Sharing Platform</p>
                </div>
                
                <div class="content">
                    <div class="alert-details">
                        <div class="detail-row">
                            <span class="label">Alert Type:</span>
                            <span class="value">{alert_type}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Priority:</span>
                            <span class="priority-badge">{priority}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Generated:</span>
                            <span class="value">{generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Alert ID:</span>
                            <span class="value">{alert_data.get('alert_id', 'N/A')}</span>
                        </div>
                    </div>
                    
                    <h3>Alert Details:</h3>
                    <div class="alert-details">
        """
        
        # Add specific alert details based on type
        if alert_type == 'high_severity_indicator':
            html_template += f"""
                        <div class="detail-row">
                            <span class="label">Feed:</span>
                            <span class="value">{data.get('feed_name', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Indicator Type:</span>
                            <span class="value">{data.get('indicator_type', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Indicator Value:</span>
                            <span class="value" style="font-family: monospace; background-color: #e9ecef; padding: 2px 4px;">{data.get('indicator_value', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Severity:</span>
                            <span class="value">{data.get('severity', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Confidence:</span>
                            <span class="value">{data.get('confidence', 'N/A')}</span>
                        </div>
            """
        elif alert_type == 'critical_ttp':
            html_template += f"""
                        <div class="detail-row">
                            <span class="label">Feed:</span>
                            <span class="value">{data.get('feed_name', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">TTP Name:</span>
                            <span class="value">{data.get('ttp_name', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Tactic:</span>
                            <span class="value">{data.get('tactic', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Technique:</span>
                            <span class="value">{data.get('technique', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">MITRE Technique:</span>
                            <span class="value">{data.get('mitre_technique', 'N/A')}</span>
                        </div>
            """
        elif alert_type == 'bulk_indicator_activity':
            html_template += f"""
                        <div class="detail-row">
                            <span class="label">Feed ID:</span>
                            <span class="value">{data.get('feed_id', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Indicator Count:</span>
                            <span class="value">{data.get('indicator_count', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Time Window:</span>
                            <span class="value">{data.get('time_window_minutes', 'N/A')} minutes</span>
                        </div>
            """
        
        html_template += """
                    </div>
                    
                    <p><strong>Action Required:</strong></p>
                    <ul>
                        <li>Review the threat details in your CRISP dashboard</li>
                        <li>Assess impact on your organization's infrastructure</li>
                        <li>Implement appropriate security measures</li>
                        <li>Share relevant information with your security team</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from CRISP (Cyber Risk Information Sharing Platform)</p>
                    <p>If you no longer wish to receive these alerts, please contact your system administrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_threat_alert_text(self, alert_data: Dict[str, Any]) -> str:
        """Generate plain text content for threat alert email."""
        alert_type = alert_data.get('alert_type', 'Unknown Alert')
        priority = alert_data.get('priority', 'medium')
        generated_at = alert_data.get('generated_at', timezone.now())
        data = alert_data.get('data', {})
        
        text_content = f"""
CRISP THREAT ALERT
==================

Alert Type: {alert_type}
Priority: {priority.upper()}
Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
Alert ID: {alert_data.get('alert_id', 'N/A')}

ALERT DETAILS:
"""
        
        # Add specific details based on alert type
        if alert_type == 'high_severity_indicator':
            text_content += f"""
Feed: {data.get('feed_name', 'N/A')}
Indicator Type: {data.get('indicator_type', 'N/A')}
Indicator Value: {data.get('indicator_value', 'N/A')}
Severity: {data.get('severity', 'N/A')}
Confidence: {data.get('confidence', 'N/A')}
"""
        elif alert_type == 'critical_ttp':
            text_content += f"""
Feed: {data.get('feed_name', 'N/A')}
TTP Name: {data.get('ttp_name', 'N/A')}
Tactic: {data.get('tactic', 'N/A')}
Technique: {data.get('technique', 'N/A')}
MITRE Technique: {data.get('mitre_technique', 'N/A')}
"""
        elif alert_type == 'bulk_indicator_activity':
            text_content += f"""
Feed ID: {data.get('feed_id', 'N/A')}
Indicator Count: {data.get('indicator_count', 'N/A')}
Time Window: {data.get('time_window_minutes', 'N/A')} minutes
"""
        
        text_content += """

ACTION REQUIRED:
- Review the threat details in your CRISP dashboard
- Assess impact on your organization's infrastructure
- Implement appropriate security measures
- Share relevant information with your security team

---
This is an automated message from CRISP (Cyber Risk Information Sharing Platform)
If you no longer wish to receive these alerts, please contact your system administrator
"""
        
        return text_content
    
    def _generate_feed_notification_html(self, notification_data: Dict[str, Any]) -> str:
        """Generate HTML content for feed notification email."""
        notification_type = notification_data.get('notification_type', 'Feed Update')
        feed_name = notification_data.get('feed_name', 'Unknown Feed')
        timestamp = notification_data.get('timestamp', timezone.now())
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CRISP Feed Notification</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #17a2b8; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .notification-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .detail-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .footer {{ background-color: #e9ecef; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 CRISP Feed Notification</h1>
                    <p>Cyber Risk Information Sharing Platform</p>
                </div>
                
                <div class="content">
                    <div class="notification-details">
                        <div class="detail-row">
                            <span class="label">Notification Type:</span>
                            <span class="value">{notification_type}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Feed Name:</span>
                            <span class="value">{feed_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Timestamp:</span>
                            <span class="value">{timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
                        </div>
                    </div>
                    
                    <p>A threat intelligence feed you're subscribed to has been updated. Please log into your CRISP dashboard to review the latest threat information.</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from CRISP (Cyber Risk Information Sharing Platform)</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_feed_notification_text(self, notification_data: Dict[str, Any]) -> str:
        """Generate plain text content for feed notification email."""
        notification_type = notification_data.get('notification_type', 'Feed Update')
        feed_name = notification_data.get('feed_name', 'Unknown Feed')
        timestamp = notification_data.get('timestamp', timezone.now())
        
        text_content = f"""
CRISP FEED NOTIFICATION
======================

Notification Type: {notification_type}
Feed Name: {feed_name}
Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

A threat intelligence feed you're subscribed to has been updated. 
Please log into your CRISP dashboard to review the latest threat information.

---
This is an automated message from CRISP (Cyber Risk Information Sharing Platform)
"""
        
        return text_content
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Gmail SMTP connection.
        
        Returns:
            Dictionary with connection test result
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Testing Gmail connection - Host: {self.email_host}, Port: {self.email_port}, SSL: {self.email_use_ssl}, User: {self.email_host_user}")
            
            # Use SSL or TLS based on configuration
            if self.email_use_ssl:
                logger.info("Using SMTP_SSL connection")
                import ssl
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                server = smtplib.SMTP_SSL(self.email_host, self.email_port, context=context, timeout=30)
            else:
                logger.info("Using regular SMTP connection")
                server = smtplib.SMTP(self.email_host, self.email_port, timeout=30)
                if self.email_use_tls:
                    logger.info("Starting TLS")
                    server.starttls()
            
            logger.info("Attempting login...")
            server.login(self.email_host_user, self.email_host_password)
            logger.info("Login successful, closing connection")
            server.quit()
            
            return {
                'success': True,
                'message': 'Gmail SMTP connection successful',
                'status': 'online'
            }
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication Error: {str(e)}")
            return {
                'success': False,
                'message': f'Authentication failed: {str(e)}',
                'status': 'error'
            }
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP Connection Error: {str(e)}")
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'status': 'error'
            }
        except ConnectionRefusedError as e:
            logger.error(f"Connection Refused Error: {str(e)}")
            return {
                'success': False,
                'message': f'Connection refused: {str(e)}',
                'status': 'error'
            }
        except Exception as e:
            logger.error(f"Gmail SMTP connection error: {str(e)}")
            return {
                'success': False,
                'message': f'Gmail SMTP connection error: {str(e)}',
                'status': 'error'
            }
    
    def send_password_reset_email(self, user, reset_token: str) -> Dict[str, Any]:
        """
        Send password reset email (SRS R1.1.3)
        
        Args:
            user: CustomUser instance
            reset_token: Secure reset token
            
        Returns:
            Dictionary with send result
        """
        from django.conf import settings
        
        reset_link = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password/{reset_token}"
        
        subject = "CRISP - Password Reset Request"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9f9f9;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">CRISP Password Reset</h1>
                <p style="color: #e8f4fd; margin: 10px 0 0 0;">Cyber Risk Information Sharing Platform</p>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <p style="font-size: 18px; color: #2c3e50; margin-bottom: 20px;">Hello {user.get_full_name() or user.username},</p>
                
                <p style="color: #555; line-height: 1.6; margin-bottom: 25px;">
                    You requested a password reset for your CRISP account at <strong>{user.organization.name if hasattr(user, 'organization') and user.organization else 'your organization'}</strong>.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(52,152,219,0.3);">
                        Reset Password
                    </a>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 25px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        <strong>Security Notice:</strong> This link expires in 24 hours for security reasons. 
                        If you didn't request this reset, please ignore this email.
                    </p>
                </div>
                
                <p style="color: #777; font-size: 14px; margin-top: 30px;">
                    For security reasons, please do not share this link with anyone.
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
                <p>CRISP - Cyber Risk Information Sharing Platform</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        CRISP Password Reset Request
        
        Hello {user.get_full_name() or user.username},
        
        You requested a password reset for your CRISP account.
        
        Please click the following link to reset your password:
        {reset_link}
        
        This link expires in 24 hours for security reasons.
        
        If you didn't request this reset, please ignore this email.
        
        CRISP - Cyber Risk Information Sharing Platform
        """
        
        return self.send_email(
            to_emails=[user.email],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            email_type='password_reset',
            user=user
        )
    
    def send_user_invitation_email(self, email: str, organization, inviter, invitation_token: str) -> Dict[str, Any]:
        """
        Send user invitation email (SRS R1.2.2)
        
        Args:
            email: Recipient email address
            organization: Organization instance
            inviter: User who sent the invitation
            invitation_token: Secure invitation token
            
        Returns:
            Dictionary with send result
        """
        from django.conf import settings
        
        invite_link = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/accept-invitation/{invitation_token}"
        
        subject = f"Invitation to join {organization.name} on CRISP"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9f9f9;">
            <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🛡️ You're Invited to CRISP</h1>
                <p style="color: #d5f4e6; margin: 10px 0 0 0;">Cyber Risk Information Sharing Platform</p>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <p style="font-size: 18px; color: #2c3e50; margin-bottom: 20px;">Hello,</p>
                
                <p style="color: #555; line-height: 1.6; margin-bottom: 25px;">
                    <strong>{inviter.get_full_name() or inviter.username}</strong> from <strong>{organization.name}</strong> has invited you to join the CRISP Threat Intelligence Platform.
                </p>
                
                <div style="background: #e8f8f5; border-left: 4px solid #27ae60; padding: 20px; margin: 25px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #27ae60;">About CRISP</h3>
                    <p style="margin: 0; color: #555; font-size: 14px;">
                        CRISP enables educational institutions to share cyber threat intelligence securely, 
                        helping protect against emerging threats through collaborative defense.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invite_link}" style="background: #27ae60; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(39,174,96,0.3);">
                        Accept Invitation
                    </a>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 25px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        <strong>Note:</strong> This invitation expires in 7 days. 
                        You'll be able to create your account and set up your password after accepting.
                    </p>
                </div>
                
                <p style="color: #777; font-size: 14px; margin-top: 30px;">
                    If you have any questions, please contact {inviter.email}.
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
                <p>CRISP - Cyber Risk Information Sharing Platform</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        You're Invited to Join CRISP
        
        Hello,
        
        {inviter.get_full_name() or inviter.username} from {organization.name} has invited you to join the CRISP Threat Intelligence Platform.
        
        CRISP enables educational institutions to share cyber threat intelligence securely, helping protect against emerging threats through collaborative defense.
        
        Please click the following link to accept your invitation:
        {invite_link}
        
        This invitation expires in 7 days.
        
        If you have any questions, please contact {inviter.email}.
        
        CRISP - Cyber Risk Information Sharing Platform
        """
        
        return self.send_email(
            to_emails=[email],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            email_type='user_invitation'
        )
    
    def send_account_locked_email(self, user) -> Dict[str, Any]:
        """
        Send account lockout notification email (SRS R1.1.4)
        
        Args:
            user: CustomUser instance
            
        Returns:
            Dictionary with send result
        """
        from django.conf import settings
        
        subject = "CRISP - Account Temporarily Locked"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9f9f9;">
            <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🔒 Account Locked</h1>
                <p style="color: #fce4ec; margin: 10px 0 0 0;">Security Alert</p>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <p style="font-size: 18px; color: #2c3e50; margin-bottom: 20px;">Hello {user.get_full_name() or user.username},</p>
                
                <p style="color: #555; line-height: 1.6; margin-bottom: 25px;">
                    Your CRISP account has been temporarily locked due to multiple failed login attempts.
                </p>
                
                <div style="background: #ffebee; border-left: 4px solid #e74c3c; padding: 20px; margin: 25px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #e74c3c;">Security Information</h3>
                    <p style="margin: 0 0 10px 0; color: #555; font-size: 14px;">
                        <strong>Lockout Duration:</strong> 30 minutes
                    </p>
                    <p style="margin: 0; color: #555; font-size: 14px;">
                        <strong>Account Status:</strong> Temporarily restricted
                    </p>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 25px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        <strong>What to do:</strong> Please wait 30 minutes before attempting to log in again. 
                        If you suspect unauthorized access, contact your organization administrator immediately.
                    </p>
                </div>
                
                <p style="color: #777; font-size: 14px; margin-top: 30px;">
                    If this wasn't you, please contact your organization's IT security team.
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
                <p>CRISP - Cyber Risk Information Sharing Platform</p>
                <p>This is an automated security notification.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        CRISP Account Temporarily Locked
        
        Hello {user.get_full_name() or user.username},
        
        Your CRISP account has been temporarily locked due to multiple failed login attempts.
        
        Security Information:
        - Lockout Duration: 30 minutes
        - Account Status: Temporarily restricted
        
        Please wait 30 minutes before attempting to log in again.
        
        If you suspect unauthorized access or if this wasn't you, please contact your organization administrator immediately.
        
        CRISP - Cyber Risk Information Sharing Platform
        """
        
        return self.send_email(
            to_emails=[user.email],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            email_type='security_alert',
            user=user
        )
    
    def send_feed_subscription_confirmation(self, user, feed_name: str) -> Dict[str, Any]:
        """
        Send feed subscription confirmation email (User Story 1)
        
        Args:
            user: CustomUser instance
            feed_name: Name of the threat feed
            
        Returns:
            Dictionary with send result
        """
        from django.conf import settings
        
        dashboard_link = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/dashboard"
        
        subject = f"CRISP - Subscription Confirmed: {feed_name}"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9f9f9;">
            <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">✅ Subscription Confirmed</h1>
                <p style="color: #dbeafe; margin: 10px 0 0 0;">Threat Intelligence Feed</p>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <p style="font-size: 18px; color: #2c3e50; margin-bottom: 20px;">Hello {user.get_full_name() or user.username},</p>
                
                <p style="color: #555; line-height: 1.6; margin-bottom: 25px;">
                    You have successfully subscribed to the <strong>{feed_name}</strong> threat intelligence feed.
                </p>
                
                <div style="background: #e8f4fd; border-left: 4px solid #3498db; padding: 20px; margin: 25px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #3498db;">What happens next?</h3>
                    <ul style="margin: 0; color: #555; font-size: 14px; padding-left: 20px;">
                        <li>You'll receive threat intelligence updates from this feed</li>
                        <li>Critical threats will be sent immediately via email</li>
                        <li>Regular updates will be batched based on your preferences</li>
                        <li>You can manage your subscriptions in your dashboard</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{dashboard_link}" style="background: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(52,152,219,0.3);">
                        View Dashboard
                    </a>
                </div>
                
                <p style="color: #777; font-size: 14px; margin-top: 30px;">
                    You can unsubscribe from this feed at any time through your dashboard settings.
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
                <p>CRISP - Cyber Risk Information Sharing Platform</p>
                <p>This is an automated confirmation message.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        CRISP Subscription Confirmed
        
        Hello {user.get_full_name() or user.username},
        
        You have successfully subscribed to the {feed_name} threat intelligence feed.
        
        What happens next?
        - You'll receive threat intelligence updates from this feed
        - Critical threats will be sent immediately via email
        - Regular updates will be batched based on your preferences
        - You can manage your subscriptions in your dashboard
        
        View your dashboard: {dashboard_link}
        
        You can unsubscribe from this feed at any time through your dashboard settings.
        
        CRISP - Cyber Risk Information Sharing Platform
        """
        
        return self.send_email(
            to_emails=[user.email],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            email_type='feed_subscription_confirmation',
            user=user
        )