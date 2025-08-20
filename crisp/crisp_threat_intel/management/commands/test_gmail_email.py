
"""
Django management command to test Gmail email integration.
Usage: python manage.py test_gmail_email
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Test Gmail email integration with CRISP observer system'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Gmail Email Integration...'))
        
        try:
            sender_email = os.getenv('CRISP_SENDER_EMAIL')
            sender_name = os.getenv('CRISP_SENDER_NAME', 'CRISP Platform')
            recipient = os.getenv('DEFAULT_ADMIN_EMAIL', os.getenv('EMAIL_HOST_USER'))
            
            subject = "CRISP Django Gmail Test"
            text_message = "This is a test email from CRISP Django application using Gmail SMTP."
            html_message = f"""
            <html>
            <body>
                <h2>CRISP Django Gmail Test</h2>
                <p>This is a test email from CRISP Django application using Gmail SMTP.</p>
                <p><strong>Configuration:</strong></p>
                <ul>
                    <li>Email Host: {settings.EMAIL_HOST}</li>
                    <li>Email Port: {settings.EMAIL_PORT}</li>
                    <li>Use TLS: {settings.EMAIL_USE_TLS}</li>
                    <li>Host User: {settings.EMAIL_HOST_USER}</li>
                </ul>
                <p style="color: green;"><strong>✅ Django Gmail integration working!</strong></p>
            </body>
            </html>
            """
            
            # Send HTML email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=f"{sender_name} <{sender_email}>",
                to=[recipient]
            )
            msg.attach_alternative(html_message, "text/html")
            
            result = msg.send()
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Test email sent successfully to {recipient}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Failed to send email')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )
