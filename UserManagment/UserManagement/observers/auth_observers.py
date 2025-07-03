from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from typing import Dict, List
import logging
from ..models import CustomUser, AuthenticationLog


logger = logging.getLogger(__name__)


class AuthenticationObserver(ABC):
    """Observer for authentication events following CRISP Observer pattern"""
    
    @abstractmethod
    def notify(self, event_type: str, user: CustomUser, event_data: Dict) -> None:
        """
        Handle authentication event notification
        
        Args:
            event_type: Type of authentication event
            user: User associated with the event
            event_data: Additional event data including IP, user agent, etc.
        """
        pass


class SecurityAuditObserver(AuthenticationObserver):
    """Logs security events for audit purposes"""
    
    def __init__(self):
        self.security_logger = logging.getLogger('crisp.security')
    
    def notify(self, event_type: str, user: CustomUser, event_data: Dict) -> None:
        """Log security events"""
        try:
            log_data = {
                'event_type': event_type,
                'user_id': str(user.id) if user else None,
                'username': user.username if user else event_data.get('username', 'unknown'),
                'organization': user.organization.name if user and user.organization else 'unknown',
                'ip_address': event_data.get('ip_address', 'unknown'),
                'user_agent': event_data.get('user_agent', 'unknown'),
                'timestamp': timezone.now().isoformat(),
                'success': event_data.get('success', False),
                'failure_reason': event_data.get('failure_reason'),
                'additional_data': event_data.get('additional_data', {})
            }
            
            # Log to security audit log
            if event_data.get('success', False):
                self.security_logger.info(f"SECURITY_EVENT: {log_data}")
            else:
                self.security_logger.warning(f"SECURITY_VIOLATION: {log_data}")
                
            # Additional logging for critical events
            if event_type in ['account_locked', 'multiple_failed_logins', 'suspicious_activity']:
                self.security_logger.critical(f"CRITICAL_SECURITY_EVENT: {log_data}")
                
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")


class AccountLockoutObserver(AuthenticationObserver):
    """Handles account lockout logic and notifications"""
    
    def notify(self, event_type: str, user: CustomUser, event_data: Dict) -> None:
        """Handle account lockout events"""
        if not user:
            return
            
        try:
            if event_type == 'login_failed':
                self._handle_failed_login(user, event_data)
            elif event_type == 'account_locked':
                self._handle_account_locked(user, event_data)
            elif event_type == 'suspicious_activity':
                self._handle_suspicious_activity(user, event_data)
                
        except Exception as e:
            logger.error(f"Failed to handle account lockout event: {e}")
    
    def _handle_failed_login(self, user: CustomUser, event_data: Dict) -> None:
        """Handle failed login attempts"""
        # Check if user is approaching lockout threshold
        if user.failed_login_attempts >= 3:  # Warning at 3 attempts (locks at 5)
            # Notify user of approaching lockout
            self._send_security_warning(user, event_data)
            
            # Log as suspicious if many attempts from different IPs
            if self._is_suspicious_activity(user, event_data):
                # Trigger suspicious activity handling
                self.notify('suspicious_activity', user, event_data)
    
    def _handle_account_locked(self, user: CustomUser, event_data: Dict) -> None:
        """Handle account lockout"""
        # Send lockout notification
        self._send_lockout_notification(user, event_data)
        
        # Notify organization admins
        self._notify_organization_admins(user, event_data)
    
    def _handle_suspicious_activity(self, user: CustomUser, event_data: Dict) -> None:
        """Handle suspicious activity detection"""
        # Immediately lock account for suspicious activity
        user.lock_account(duration_minutes=60)  # Lock for 1 hour
        
        # Log critical security event
        AuthenticationLog.log_authentication_event(
            user=user,
            action='account_locked',
            ip_address=event_data.get('ip_address', 'unknown'),
            user_agent=event_data.get('user_agent', 'unknown'),
            success=True,
            additional_data={
                'reason': 'suspicious_activity',
                'trigger_event': event_data
            }
        )
        
        # Send immediate security alert
        self._send_security_alert(user, event_data)
    
    def _is_suspicious_activity(self, user: CustomUser, event_data: Dict) -> bool:
        """Detect suspicious activity patterns"""
        # Check for multiple failed attempts from different IPs in short time
        recent_logs = AuthenticationLog.objects.filter(
            user=user,
            action='login_failed',
            timestamp__gte=timezone.now() - timezone.timedelta(minutes=15)
        ).values_list('ip_address', flat=True)
        
        unique_ips = set(recent_logs)
        return len(unique_ips) > 2  # Multiple IPs in short time is suspicious
    
    def _send_security_warning(self, user: CustomUser, event_data: Dict) -> None:
        """Send security warning to user"""
        # Implementation would send email/notification
        logger.warning(f"Security warning sent to {user.username}")
    
    def _send_lockout_notification(self, user: CustomUser, event_data: Dict) -> None:
        """Send account lockout notification"""
        # Implementation would send email/notification
        logger.warning(f"Lockout notification sent to {user.username}")
    
    def _send_security_alert(self, user: CustomUser, event_data: Dict) -> None:
        """Send immediate security alert"""
        # Implementation would send urgent notification
        logger.critical(f"Security alert sent for {user.username}")
    
    def _notify_organization_admins(self, user: CustomUser, event_data: Dict) -> None:
        """Notify organization administrators of lockout"""
        if not user.organization:
            return
            
        org_admins = CustomUser.objects.filter(
            organization=user.organization,
            role='BlueVisionAdmin',
            is_active=True
        )
        
        for admin in org_admins:
            # Implementation would send notification to admin
            logger.info(f"Lockout notification sent to admin {admin.username}")


class NotificationObserver(AuthenticationObserver):
    """Sends notifications for authentication events"""
    
    def notify(self, event_type: str, user: CustomUser, event_data: Dict) -> None:
        """Send appropriate notifications based on event type"""
        try:
            if event_type == 'login_success':
                self._handle_successful_login(user, event_data)
            elif event_type == 'password_changed':
                self._handle_password_changed(user, event_data)
            elif event_type == 'trusted_device_added':
                self._handle_trusted_device_added(user, event_data)
            elif event_type == 'user_created':
                self._handle_user_created(user, event_data)
                
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def _handle_successful_login(self, user: CustomUser, event_data: Dict) -> None:
        """Handle successful login notifications"""
        # Check if login is from new location/device
        if self._is_new_location(user, event_data):
            self._send_new_location_alert(user, event_data)
    
    def _handle_password_changed(self, user: CustomUser, event_data: Dict) -> None:
        """Handle password change notifications"""
        self._send_password_change_notification(user, event_data)
    
    def _handle_trusted_device_added(self, user: CustomUser, event_data: Dict) -> None:
        """Handle trusted device addition notifications"""
        self._send_trusted_device_notification(user, event_data)
    
    def _handle_user_created(self, user: CustomUser, event_data: Dict) -> None:
        """Handle new user creation notifications"""
        if event_data.get('auto_generate_password'):
            self._send_welcome_with_password(user, event_data)
        else:
            self._send_welcome_notification(user, event_data)
    
    def _is_new_location(self, user: CustomUser, event_data: Dict) -> bool:
        """Check if login is from a new location"""
        current_ip = event_data.get('ip_address')
        if not current_ip:
            return False
            
        # Check recent successful logins from different IPs
        recent_ips = AuthenticationLog.objects.filter(
            user=user,
            action='login_success',
            timestamp__gte=timezone.now() - timezone.timedelta(days=30)
        ).values_list('ip_address', flat=True).distinct()
        
        return current_ip not in recent_ips
    
    def _send_new_location_alert(self, user: CustomUser, event_data: Dict) -> None:
        """Send new location login alert"""
        logger.info(f"New location alert sent to {user.username} from {event_data.get('ip_address')}")
    
    def _send_password_change_notification(self, user: CustomUser, event_data: Dict) -> None:
        """Send password change notification"""
        logger.info(f"Password change notification sent to {user.username}")
    
    def _send_trusted_device_notification(self, user: CustomUser, event_data: Dict) -> None:
        """Send trusted device notification"""
        logger.info(f"Trusted device notification sent to {user.username}")
    
    def _send_welcome_notification(self, user: CustomUser, event_data: Dict) -> None:
        """Send welcome notification to new user"""
        logger.info(f"Welcome notification sent to {user.username}")
    
    def _send_welcome_with_password(self, user: CustomUser, event_data: Dict) -> None:
        """Send welcome notification with auto-generated password"""
        logger.info(f"Welcome with password sent to {user.username}")


class SecurityAlertObserver(AuthenticationObserver):
    """Observer that sends security alerts for suspicious activities"""
    
    def notify(self, event_type: str, user: CustomUser, event_data: Dict) -> None:
        """Send security alerts for specific events"""
        if event_type in ['account_locked', 'password_reset', 'multiple_failed_logins']:
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            username = user.username if user else event_data.get('username', 'Unknown')
            
            # In a real implementation, this would send actual alerts
            print(f"[{timestamp}] 🚨 Security Alert: {event_type} for user: {username}")
            logger.warning(f"Security alert: {event_type} for user {username}")


class NewLocationAlertObserver(AuthenticationObserver):
    """Observer that alerts users when they log in from a new location"""
    
    def notify(self, event_type: str, user: CustomUser, event_data: Dict) -> None:
        """Send new location alerts"""
        if event_type == 'login_success' and user:
            ip_address = event_data.get('ip_address', 'unknown')
            
            # Simple check - in reality this would use IP geolocation
            # For testing, we'll check if this is a different IP than the last login
            if hasattr(user, '_last_login_ip') and user._last_login_ip != ip_address:
                print(f"New location alert sent to {user.username} from {ip_address}")
                logger.info(f"New location alert for {user.username} from {ip_address}")
            
            # Store the IP for next time (in memory for testing)
            user._last_login_ip = ip_address


class ConsoleLoggingObserver(AuthenticationObserver):
    """Observer that logs authentication events to console with colored output"""
    
    # ANSI color codes
    GREEN = '\033[92m'  # Green
    RED = '\033[91m'    # Red
    YELLOW = '\033[93m' # Yellow
    RESET = '\033[0m'   # Reset to default
    
    def notify(self, event_type: str, user: CustomUser, event_data: Dict) -> None:
        """Log authentication events to console with color coding"""
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        username = user.username if user else event_data.get('username', 'Unknown')
        
        # Check if this is a test result
        if event_data.get('is_test_result'):
            test_name = event_data.get('test_name', 'Unknown Test')
            if event_data.get('success', False):
                print(f"{self.GREEN}[{timestamp}] ✓ TEST PASSED: {test_name}{self.RESET}")
            else:
                error_msg = event_data.get('error_message', 'Test failed')
                print(f"{self.RED}[{timestamp}] ✗ TEST FAILED: {test_name} - {error_msg}{self.RESET}")
        elif event_type == 'login_success':
            print(f"{self.GREEN}[{timestamp}] ✓ Login successful for user: {username}{self.RESET}")
        elif event_type == 'login_failed':
            print(f"{self.RED}[{timestamp}] ✗ Login failed for user: {username}{self.RESET}")
        elif event_type == 'password_changed':
            print(f"{self.GREEN}[{timestamp}] ✓ Password changed for user: {username}{self.RESET}")
        elif event_type in ['account_locked', 'suspicious_activity']:
            print(f"{self.RED}[{timestamp}] ⚠ {event_type.replace('_', ' ').title()} for user: {username}{self.RESET}")
        else:
            print(f"{self.YELLOW}[{timestamp}] ℹ Authentication event '{event_type}' for user: {username}{self.RESET}")


class AuthenticationEventSubject:
    """Subject for authentication events (Publisher in Observer pattern)"""
    
    def __init__(self):
        self._observers: List[AuthenticationObserver] = []
        self._setup_default_observers()
    
    def _setup_default_observers(self) -> None:
        """Setup default observers"""
        self.attach(SecurityAuditObserver())
        self.attach(AccountLockoutObserver())
        self.attach(NotificationObserver())
        self.attach(ConsoleLoggingObserver())
    
    def attach(self, observer: AuthenticationObserver) -> None:
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: AuthenticationObserver) -> None:
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def register_observer(self, observer: AuthenticationObserver) -> None:
        """Register an observer (alias for attach for test compatibility)"""
        self.attach(observer)
    
    def deregister_observer(self, observer: AuthenticationObserver) -> None:
        """Deregister an observer (alias for detach for test compatibility)"""
        self.detach(observer)
    
    def unregister_observer(self, observer: AuthenticationObserver) -> None:
        """Unregister an observer (alias for detach for test compatibility)"""
        self.detach(observer)
    
    def notify_observers(self, event_type: str, user: CustomUser, event_data: Dict) -> None:
        """Notify all observers of an authentication event"""
        for observer in self._observers:
            try:
                observer.notify(event_type, user, event_data)
            except Exception as e:
                logger.error(f"Observer {observer.__class__.__name__} failed: {e}")


# Global authentication event subject
auth_event_subject = AuthenticationEventSubject()