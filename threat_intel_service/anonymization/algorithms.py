"""
Implementation of specific anonymization algorithms for STIX objects.
These algorithms are used by the anonymization strategies.
"""
import re
import uuid
import hashlib
import ipaddress
from typing import Dict, Any, List, Set, Tuple, Optional


def anonymize_ip_address(ip_str: str) -> str:
    """
    Anonymize an IP address while preserving network information.
    
    For IPv4:
    - Private IPs: Keep first 3 octets, replace last octet with 'x'
    - Public IPs: Keep first 2 octets, replace last 2 with 'x.x'
    
    For IPv6:
    - Keep first 4 hextets, replace last 4 with 'x:x:x:x'
    
    Args:
        ip_str: IP address as string
        
    Returns:
        Anonymized IP address
    """
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        
        if isinstance(ip_obj, ipaddress.IPv4Address):
            if ip_obj.is_private:
                # For private IPs, keep first 3 octets
                parts = ip_str.split('.')
                return f"{parts[0]}.{parts[1]}.{parts[2]}.x"
            else:
                # For public IPs, keep first 2 octets
                parts = ip_str.split('.')
                return f"{parts[0]}.{parts[1]}.x.x"
                
        elif isinstance(ip_obj, ipaddress.IPv6Address):
            # For IPv6, keep first 4 hextets
            parts = ip_str.split(':')
            if len(parts) > 4:
                return f"{':'.join(parts[:4])}:x:x:x:x"
            else:
                # Handle compressed IPv6 addresses
                return f"{':'.join(parts[:2])}:x:x:x"
    except:
        # If we can't parse the IP, return as is
        return ip_str


def anonymize_domain(domain: str) -> str:
    """
    Anonymize a domain name while preserving TLD.
    
    Args:
        domain: Domain name
        
    Returns:
        Anonymized domain name
    """
    parts = domain.split('.')
    if len(parts) > 1:
        # Keep TLD and domain type, anonymize specific name
        domain_hash = hashlib.md5(parts[0].encode()).hexdigest()[:6]
        return f"anon-{domain_hash}.{'.'.join(parts[1:])}"
    return domain


def anonymize_email(email: str) -> str:
    """
    Anonymize an email address while preserving domain.
    
    Args:
        email: Email address
        
    Returns:
        Anonymized email address
    """
    parts = email.split('@')
    if len(parts) == 2:
        username, domain = parts
        username_hash = hashlib.md5(username.encode()).hexdigest()[:8]
        return f"anon-{username_hash}@{domain}"
    return email


def anonymize_url(url: str) -> str:
    """
    Anonymize a URL while preserving domain and protocol.
    
    Args:
        url: URL string
        
    Returns:
        Anonymized URL
    """
    try:
        # Extract protocol and domain
        match = re.match(r'^(https?://)([\w.-]+)(\/.*)?$', url)
        if match:
            protocol, domain, path = match.groups()
            # Keep protocol and domain, anonymize path
            return f"{protocol}{domain}/anonymized"
    except:
        pass
    
    return url


def anonymize_hash(hash_value: str, hash_type: Optional[str] = None) -> str:
    """
    Anonymize a file hash while preserving length and type.
    
    Args:
        hash_value: Hash string
        hash_type: Type of hash (MD5, SHA-1, etc.)
        
    Returns:
        Anonymized hash value
    """
    # Create a new hash of same length but derived from original
    new_hash = hashlib.sha256(hash_value.encode()).hexdigest()
    if len(hash_value) < len(new_hash):
        new_hash = new_hash[:len(hash_value)]
    return new_hash


def anonymize_pattern(pattern: str, level: str = 'partial') -> str:
    """
    Anonymize a STIX pattern based on anonymization level.
    
    Args:
        pattern: STIX pattern string
        level: Anonymization level ('partial' or 'full')
        
    Returns:
        Anonymized pattern
    """
    if level == 'full':
        # Replace IP addresses with anonymized versions
        pattern = re.sub(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', '10.0.0.x', pattern)
        
        # Replace domain names
        pattern = re.sub(r'([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)', 
                        'anonymized.domain.tld', pattern)
        
        # Replace file hashes
        pattern = re.sub(r'(MD5|SHA-1|SHA-256|SHA-512|SHA3-256)=\'([a-fA-F0-9]+)\'', 
                        lambda m: f"{m.group(1)}='{'0' * len(m.group(2))}'", pattern, 
                        flags=re.IGNORECASE)
        
        # Replace email addresses
        pattern = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 
                        'anonymized@example.com', pattern)
        
        # Replace URL paths
        pattern = re.sub(r'https?://[^\s\'"]+', 'https://anonymized.example.com/path', pattern)
        
    else:  # partial anonymization
        # Anonymize IP addresses
        pattern = re.sub(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', 
                        lambda m: anonymize_ip_address(m.group(1)), pattern)
        
        # Anonymize domain names but preserve TLDs
        pattern = re.sub(r'([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)', 
                        lambda m: anonymize_domain(m.group(1)), pattern)
        
        # Anonymize file hashes but preserve type
        pattern = re.sub(r'(MD5|SHA-1|SHA-256|SHA-512|SHA3-256)=\'([a-fA-F0-9]+)\'', 
                        lambda m: f"{m.group(1)}='{anonymize_hash(m.group(2))}'", pattern, 
                        flags=re.IGNORECASE)
        
        # Anonymize email addresses
        pattern = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', 
                        lambda m: anonymize_email(m.group(1)), pattern)
        
        # Anonymize URLs but preserve domain
        pattern = re.sub(r'(https?://[^\s\'"]+)', 
                        lambda m: anonymize_url(m.group(1)), pattern)
    
    return pattern


def redact_sensitive_info(text: str) -> str:
    """
    Redact potentially sensitive information from text.
    
    Args:
        text: Text to redact
        
    Returns:
        Redacted text
    """
    # Redact email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 
                 '[REDACTED EMAIL]', text)
    
    # Redact IP addresses
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 
                 '[REDACTED IP]', text)
    
    # Redact URLs
    text = re.sub(r'https?://[^\s<>"]+|www\.[^\s<>"]+', 
                 '[REDACTED URL]', text)
    
    # Redact potential personally identifiable names
    # (capitalized words that aren't at start of sentence)
    text = re.sub(r'(?<![.!?]\s)(?<!\n)(?<!\A)\b[A-Z][a-zA-Z]+\b', 
                 '[REDACTED NAME]', text)
    
    # Redact phone numbers
    text = re.sub(r'\b(\+\d{1,3}[\s-])?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', 
                 '[REDACTED PHONE]', text)
    
    return text