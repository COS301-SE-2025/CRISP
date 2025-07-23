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
                   sender_email: str = None) -> Dict[str, Any]:
        """
        Send an email via Gmail SMTP.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            sender_name: Sender name (optional, uses default)
            sender_email: Sender email (optional, uses default)
            
        Returns:
            Dictionary with send result
        """
        try:
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
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return {
                'success': True,
                'message': 'Email sent successfully',
                'recipients': len(to_emails)
            }
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Authentication failed: {str(e)}")
            return {
                'success': False,
                'message': f'Authentication failed: {str(e)}',
                'error_type': 'authentication'
            }
        except smtplib.SMTPConnectError as e:
            logger.error(f"Connection failed: {str(e)}")
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'error_type': 'connection'
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}',
                'error_type': 'unknown'
            }
    
    def send_threat_alert_email(self, recipient_emails: List[str], alert_data: Dict[str, Any]) -> Dict[str, Any]:
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
            text_content=text_content
        )
    
    def send_feed_notification_email(self, recipient_emails: List[str], notification_data: Dict[str, Any]) -> Dict[str, Any]:
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
            text_content=text_content
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