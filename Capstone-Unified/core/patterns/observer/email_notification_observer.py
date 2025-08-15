import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """
    Email notification service using Django's built-in email system with Gmail SMTP
    All sensitive credentials stored in environment variables
    """
    
    def __init__(self):
        """Initialize the email service with environment variables"""
        self.from_address = os.getenv('CRISP_SENDER_EMAIL', 'noreply@crisp-system.org')
        self.from_name = os.getenv('CRISP_SENDER_NAME', 'CRISP Platform')
        self.default_admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@crisp-system.org')
        
        # Gmail SMTP configuration (handled by Django settings)
        self.email_host_user = os.getenv('EMAIL_HOST_USER')
        self.email_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        
        # Validate required configuration
        if not self.email_host_user:
            logger.warning("EMAIL_HOST_USER not found in environment variables")
            logger.info("Email notifications will use Django's default email configuration")
    
    def send_threat_alert_email(self, 
                               recipients: List[str], 
                               threat_data: Dict[str, Any],
                               alert_level: str = 'HIGH') -> bool:
        """
        Send threat alert email to specified recipients
        
        Args:
            recipients: List of email addresses
            threat_data: Dictionary containing threat information
            alert_level: Alert severity level
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = f"[CRISP Alert - {alert_level}] {threat_data.get('title', 'Security Threat Detected')}"
            
            # Generate HTML content
            html_content = self._generate_threat_alert_html(threat_data, alert_level)
            
            # Generate plain text content
            text_content = self._generate_threat_alert_text(threat_data, alert_level)
            
            return self._send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_content,
                text_body=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send threat alert email: {str(e)}")
            return False
    
    def send_feed_update_notification(self,
                                    recipients: List[str],
                                    feed_name: str,
                                    update_summary: Dict[str, Any]) -> bool:
        """
        Send feed update notification email
        
        Args:
            recipients: List of email addresses
            feed_name: Name of the updated threat feed
            update_summary: Summary of feed updates
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = f"[CRISP] Threat Feed Update: {feed_name}"
            
            # Generate HTML content
            html_content = self._generate_feed_update_html(feed_name, update_summary)
            
            # Generate plain text content
            text_content = self._generate_feed_update_text(feed_name, update_summary)
            
            return self._send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_content,
                text_body=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send feed update notification: {str(e)}")
            return False
    
    def _send_email(self,
                   recipients: List[str],
                   subject: str,
                   html_body: str,
                   text_body: str) -> bool:
        """
        Send email using Django's built-in email system with Gmail SMTP
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            html_body: HTML email content
            text_body: Plain text email content
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            logger.info(f"Sending email to {len(recipients)} recipients: {subject}")
            
            # Create email with both HTML and text versions
            from_email = f"{self.from_name} <{self.from_address}>"
            
            # Use Django's EmailMultiAlternatives for HTML + text email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,  # Plain text version
                from_email=from_email,
                to=recipients
            )
            
            # Attach HTML version
            msg.attach_alternative(html_body, "text/html")
            
            # Send the email
            result = msg.send()
            
            if result:
                logger.info(f"Email sent successfully to {len(recipients)} recipients")
                return True
            else:
                logger.error("Failed to send email - Django send() returned 0")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            
            # Fallback to simple text email
            try:
                logger.info("Attempting fallback to simple text email...")
                result = send_mail(
                    subject=subject,
                    message=text_body,
                    from_email=from_email,
                    recipient_list=recipients,
                    fail_silently=False
                )
                
                if result:
                    logger.info(f"Fallback email sent successfully to {len(recipients)} recipients")
                    return True
                else:
                    logger.error("Fallback email also failed")
                    return False
                    
            except Exception as fallback_e:
                logger.error(f"Fallback email error: {str(fallback_e)}")
                return False
    
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
                .high {{ background-color: #dc3545; color: white; }}
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
                    <p>This is an automated security alert. Do not reply to this email.</p>
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
This is an automated security alert. Do not reply to this email.
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


class EmailNotificationObserver:
    """
    Observer implementation for email notifications in the CRISP Observer pattern
    """
    
    def __init__(self, email_service: Optional[EmailNotificationService] = None):
        """Initialize with email service"""
        self.email_service = email_service or EmailNotificationService()
        self.notification_preferences = {}
        
    def update(self, subject, event_data: Dict[str, Any]):
        """
        Observer update method called when threat feeds change
        
        Args:
            subject: The subject (ThreatFeed) that changed
            event_data: Dictionary containing event information
        """
        try:
            event_type = event_data.get('event_type')
            
            if event_type == 'indicator_added':
                self._handle_indicator_added(subject, event_data)
            elif event_type == 'ttp_added':
                self._handle_ttp_added(subject, event_data)
            elif event_type == 'feed_published':
                self._handle_feed_published(subject, event_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error processing email notification: {str(e)}")
    
    def _handle_indicator_added(self, subject, event_data: Dict[str, Any]):
        """Handle new indicator notifications"""
        indicator = event_data.get('indicator')
        if not indicator:
            return
            
        # Check if this is a high-priority indicator requiring immediate alert
        if indicator.get('severity') in ['HIGH', 'CRITICAL']:
            recipients = self._get_alert_recipients(subject)
            
            threat_data = {
                'title': f"High-Priority Indicator: {indicator.get('value', 'Unknown')}",
                'threat_type': indicator.get('type', 'Unknown'),
                'severity': indicator.get('severity', 'Unknown'),
                'confidence': indicator.get('confidence', 'Unknown'),
                'source': subject.name if hasattr(subject, 'name') else 'Unknown'
            }
            
            self.email_service.send_threat_alert_email(
                recipients=recipients,
                threat_data=threat_data,
                alert_level=indicator.get('severity', 'HIGH')
            )
    
    def _handle_ttp_added(self, subject, event_data: Dict[str, Any]):
        """Handle new TTP notifications"""
        ttp = event_data.get('ttp')
        if not ttp:
            return
            
        # TTPs usually don't require immediate alerts unless they're critical
        if ttp.get('severity') == 'CRITICAL':
            recipients = self._get_alert_recipients(subject)
            
            threat_data = {
                'title': f"Critical TTP Detected: {ttp.get('name', 'Unknown')}",
                'threat_type': 'TTP',
                'severity': ttp.get('severity', 'Unknown'),
                'confidence': ttp.get('confidence', 'Unknown'),
                'source': subject.name if hasattr(subject, 'name') else 'Unknown'
            }
            
            self.email_service.send_threat_alert_email(
                recipients=recipients,
                threat_data=threat_data,
                alert_level='CRITICAL'
            )
    
    def _handle_feed_published(self, subject, event_data: Dict[str, Any]):
        """Handle feed publication notifications"""
        recipients = self._get_subscriber_emails(subject)
        
        update_summary = {
            'new_indicators': event_data.get('indicators_count', 0),
            'new_ttps': event_data.get('ttps_count', 0),
            'updated_items': event_data.get('updated_count', 0),
            'last_updated': event_data.get('timestamp', datetime.now().isoformat()),
            'source': subject.name if hasattr(subject, 'name') else 'Unknown'
        }
        
        self.email_service.send_feed_update_notification(
            recipients=recipients,
            feed_name=subject.name if hasattr(subject, 'name') else 'Unknown Feed',
            update_summary=update_summary
        )
    
    def _get_alert_recipients(self, subject) -> List[str]:
        """Get email addresses for high-priority alerts"""
        recipients = [os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@crisp-system.org')]
        
        if hasattr(subject, 'alert_recipients'):
            recipients.extend(subject.alert_recipients)
        
        return list(set(recipients))
    
    def _get_subscriber_emails(self, subject) -> List[str]:
        """Get email addresses for feed subscribers"""
        recipients = []
        
        if hasattr(subject, 'subscribers'):
            for subscriber in subject.subscribers:
                if hasattr(subscriber, 'email'):
                    recipients.append(subscriber.email)
        
        if not recipients:
            recipients = [os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@crisp-system.org')]
        
        return recipients