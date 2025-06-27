"""
Logging utilities for CRISP platform
"""
import logging
from typing import Optional


def get_ip_address(request) -> Optional[str]:
    """
    Extract IP address from Django request object.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        IP address as string or None if not found
    """
    if not request:
        return None
        
    # Check for forwarded IP first (common in load balancer setups)
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(',')[0].strip()
    
    # Check for real IP header
    real_ip = request.META.get('HTTP_X_REAL_IP')
    if real_ip:
        return real_ip.strip()
    
    # Fall back to remote address
    return request.META.get('REMOTE_ADDR')


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with standard formatting.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_security_event(logger: logging.Logger, event_type: str, 
                      user_id: Optional[int], ip_address: Optional[str], 
                      details: Optional[str] = None):
    """
    Log security-related events with standard format.
    
    Args:
        logger: Logger instance
        event_type: Type of security event
        user_id: User ID if available
        ip_address: IP address of request
        details: Additional details about the event
    """
    message = f"SECURITY_EVENT: {event_type}"
    
    if user_id:
        message += f" | User: {user_id}"
    
    if ip_address:
        message += f" | IP: {ip_address}"
    
    if details:
        message += f" | Details: {details}"
    
    logger.warning(message)