"""
Gmail SMTP Connection Test
File: test_email_datadefenders.py

Detailed debugging script to test Gmail SMTP connection.
Updated to use environment variables for security.
Uses Django's built-in email backend for Gmail SMTP.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def load_env_file(env_path='.env'):
    """Manually load environment variables from .env file"""
    env_vars = {}
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('\'"')  # Remove quotes if present
                    env_vars[key] = value
                    # Also set in os.environ for consistency
                    os.environ[key] = value
    except FileNotFoundError:
        print(f"❌ Error: .env file not found at {env_path}")
        print("   Make sure your .env file is in the same directory as this script")
        return None
    except Exception as e:
        print(f"❌ Error reading .env file: {str(e)}")
        return None
    
    return env_vars


def load_environment():
    """Load environment variables from .env file"""
    # First try to load from .env file
    env_vars = load_env_file()
    if env_vars is None:
        return None
    
    # Get required environment variables for Gmail
    email_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    email_port = int(os.getenv('EMAIL_PORT', '587'))
    email_use_tls = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
    email_host_user = os.getenv('EMAIL_HOST_USER')
    email_host_password = os.getenv('EMAIL_HOST_PASSWORD')
    sender_email = os.getenv('CRISP_SENDER_EMAIL')
    sender_name = os.getenv('CRISP_SENDER_NAME', 'CRISP')
    
    if not email_host_user:
        print("❌ EMAIL_HOST_USER not found in environment variables")
        return None
    
    if not email_host_password:
        print("❌ EMAIL_HOST_PASSWORD not found in environment variables")
        return None
    
    if not sender_email:
        print("❌ CRISP_SENDER_EMAIL not found in environment variables")
        return None
    
    return {
        'email_host': email_host,
        'email_port': email_port,
        'email_use_tls': email_use_tls,
        'email_host_user': email_host_user,
        'email_host_password': email_host_password,
        'sender_email': sender_email,
        'sender_name': sender_name
    }


def test_smtp_connection(config):
    """Test Gmail SMTP connection"""
    
    print("Gmail SMTP Connection Test")
    print("=" * 50)
    print(f"Host: {config['email_host']}")
    print(f"Port: {config['email_port']}")
    print(f"Use TLS: {config['email_use_tls']}")
    print(f"Username: {config['email_host_user']}")
    print(f"Password: {'*' * len(config['email_host_password'])}")
    print(f"Sender Email: {config['sender_email']}")
    print()
    
    try:
        print("🔌 Connecting to Gmail SMTP server...")
        
        # Create SMTP connection
        server = smtplib.SMTP(config['email_host'], config['email_port'])
        
        # Enable debug output
        server.set_debuglevel(1)
        
        print("✅ Connected to SMTP server")
        
        if config['email_use_tls']:
            print("🔐 Starting TLS...")
            server.starttls()
            print("✅ TLS started successfully")
        
        print("🔑 Authenticating...")
        server.login(config['email_host_user'], config['email_host_password'])
        print("✅ Authentication successful")
        
        server.quit()
        print("✅ SMTP connection test passed!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Check your Gmail credentials and App Password")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ Connection failed: {e}")
        print("   Check your network connection and SMTP settings")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def send_test_email(config):
    """Send a test email using Gmail SMTP"""
    
    print("📧 Sending Test Email")
    print("=" * 50)
    
    # Target email for testing
    test_email = "datadefenders.sa@gmail.com"
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🧪 CRISP Gmail SMTP Test - Data Defenders"
        msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
        msg['To'] = test_email
        
        # Create text and HTML versions
        text_body = f"""
Debug Test Email from CRISP

This is a test to verify Gmail SMTP integration.

If you receive this email, Gmail SMTP is working correctly!

Sender: {config['sender_name']} <{config['sender_email']}>
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Data Defenders Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>🧪 CRISP Gmail SMTP Test</h2>
            <p>This is a test to verify Gmail SMTP integration.</p>
            <p><strong>If you receive this email, Gmail SMTP is working correctly!</strong></p>
            <ul>
                <li>Sender: {config['sender_name']} &lt;{config['sender_email']}&gt;</li>
                <li>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
            </ul>
            <p>Data Defenders Team</p>
        </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        print("📨 Sending test email...")
        print(f"   To: {test_email}")
        print(f"   From: {config['sender_name']} <{config['sender_email']}>")
        print()
        
        # Send email
        server = smtplib.SMTP(config['email_host'], config['email_port'])
        if config['email_use_tls']:
            server.starttls()
        
        server.login(config['email_host_user'], config['email_host_password'])
        server.send_message(msg)
        server.quit()
        
        print("✅ SUCCESS! Test email sent successfully!")
        print(f"   Check {test_email} for the test email")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def check_gmail_credentials(config):
    """Validate Gmail credentials format"""
    
    print("🔑 Gmail Credentials Validation")
    print("=" * 50)
    
    email_user = config['email_host_user']
    email_password = config['email_host_password']
    
    print(f"Gmail Address: {email_user}")
    print(f"App Password: {'*' * len(email_password)} ({len(email_password)} chars)")
    print()
    
    # Basic validation
    if not email_user.endswith('@gmail.com'):
        print("⚠️  WARNING: Email should end with @gmail.com")
        return False
    
    if len(email_password) < 10:
        print("⚠️  WARNING: App password seems too short")
        print("   App passwords are usually 16 characters")
        return False
    
    if ' ' not in email_password:
        print("⚠️  WARNING: App password should contain spaces")
        print("   Format: 'xxxx xxxx xxxx xxxx'")
        return False
    
    print("✅ Gmail credentials format looks correct")
    return True


def check_environment_setup():
    """Check if all required environment variables are set"""
    
    print("🌍 Environment Setup Check")
    print("=" * 50)
    
    required_vars = [
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'CRISP_SENDER_EMAIL',
        'CRISP_SENDER_NAME'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                print(f"✅ {var}: {'*' * len(value)} (masked)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    print()
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please ensure these are set in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True


def main():
    """Main function to test Gmail SMTP"""
    
    print("🛡️ CRISP Gmail SMTP Test Tool")
    print("=" * 60)
    print("📧 Testing Gmail SMTP connection and email sending")
    print("🔒 Using environment variables for security")
    print("📁 Reading .env file manually (no external dependencies)")
    print()
    
    try:
        # Load configuration
        config = load_environment()
        if config is None:
            print("❌ Failed to load configuration from .env file")
            return
        
        # Step 1: Check environment setup
        if not check_environment_setup():
            print("❌ Environment setup failed. Please check your .env file.")
            return
        
        print()
        
        # Step 2: Check Gmail credentials format
        check_gmail_credentials(config)
        print()
        
        # Step 3: Test SMTP connection
        connection_success = test_smtp_connection(config)
        print()
        
        if not connection_success:
            print("❌ SMTP connection failed. Fix connection issues before testing email send.")
            return
        
        # Step 4: Send test email
        email_success = send_test_email(config)
        print()
        
        # Summary
        print("📋 TESTING SUMMARY")
        print("=" * 50)
        
        if email_success:
            print("✅ SUCCESS: Test email sent successfully!")
            print("   Your Gmail SMTP integration is working!")
            print("   Check datadefenders.sa@gmail.com for the test email")
        else:
            print("❌ ISSUE: Email sending failed")
            print()
            print("🔧 TROUBLESHOOTING STEPS:")
            print("1. Verify your Gmail App Password is correct")
            print("2. Check if 2-Factor Authentication is enabled on Gmail")
            print("3. Ensure 'Less secure app access' is disabled (use App Passwords)")
            print("4. Try generating a new App Password")
            print("5. Check Gmail security settings")
            print()
            print("🌐 Gmail Security: https://security.google.com/")
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()


