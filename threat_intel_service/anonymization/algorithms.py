"""
Implementation of specific anonymization algorithms for STIX objects.
These algorithms are used by the anonymization strategies.
Focus on preserving analytical value while removing identifiable information.
"""
import re
import uuid
import hashlib
import ipaddress
from typing import Dict, Any, List, Set, Tuple, Optional, Union
from urllib.parse import urlparse, urlunparse

# --- Anonymization Functions for PII and Sensitive Identifiers ---

def anonymize_ip_address(ip_str: str, level: str = 'partial') -> str:
    """
    Anonymize an IP address.
    'partial': Zeroes out the host portion. For /24 IPv4, last octet. For /64 IPv6, last 64 bits.
    'full':    Replaces with a generic private IP or generic IPv6.

    Args:
        ip_str: IP address string.
        level: 'partial' or 'full'.

    Returns:
        Anonymized IP address string.
    """
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if level == 'full':
            return '10.0.0.1' if ip_obj.version == 4 else '2001:db8::1'

        # Partial anonymization
        if ip_obj.version == 4:
            # Common practice: zero out the last octet for /24 equivalent
            network = ipaddress.IPv4Network(f"{ip_str}/24", strict=False)
            return str(network.network_address) # Returns x.y.z.0
        elif ip_obj.version == 6:
            # Common practice: zero out the last 64 bits (interface identifier) for /64 equivalent
            network = ipaddress.IPv6Network(f"{ip_str}/64", strict=False)
            return str(network.network_address) # Returns a.b.c.d::
    except ValueError:
        # If not a valid IP, return a generic placeholder or original based on policy
        return "invalid_ip_format"
    return ip_str # Fallback

def anonymize_domain_name(domain: str, level: str = 'partial') -> str:
    """
    Anonymize a domain name.
    'partial': Replaces subdomain parts with 'anon-[hash]', keeps TLD. e.g., www.example.com -> anon-xxxx.example.com
    'full':    Replaces with 'anonymized.example.com'.

    Args:
        domain: Domain name string.
        level: 'partial' or 'full'.

    Returns:
        Anonymized domain name string.
    """
    if level == 'full':
        return "anonymized.example.com"

    parts = domain.split('.')
    if len(parts) > 2:  # e.g., sub.example.com
        subdomain_hash = hashlib.md5(parts[0].encode()).hexdigest()[:6]
        return f"anon-{subdomain_hash}.{'.'.join(parts[1:])}"
    elif len(parts) == 2: # e.g., example.com
        # Could anonymize the SLD or keep it if TLD is generic like .com
        # For partial, let's keep SLD for now if TLD isn't country-specific or highly revealing
        return domain # Or anonymize SLD: f"anon-{hashlib.md5(parts[0].encode()).hexdigest()[:6]}.{parts[1]}"
    return "anonymized.domain" # Fallback for single part or invalid

def anonymize_email_address(email: str, level: str = 'partial') -> str:
    """
    Anonymize an email address.
    'partial': Replaces local-part with 'anonuser-[hash]@[domain]'.
    'full':    Replaces with 'user@anonymized.example.com'.

    Args:
        email: Email address string.
        level: 'partial' or 'full'.

    Returns:
        Anonymized email address string.
    """
    if level == 'full':
        return "user@anonymized.example.com"

    parts = email.split('@')
    if len(parts) == 2:
        local_part, domain_part = parts
        local_hash = hashlib.md5(local_part.encode()).hexdigest()[:8]
        return f"anonuser-{local_hash}@{anonymize_domain_name(domain_part, level='partial')}" # Anonymize domain too
    return "anonymized.email"

def anonymize_url(url_str: str, level: str = 'partial') -> str:
    """
    Anonymize a URL.
    'partial': Anonymizes domain, replaces path & query with generic placeholders.
    'full':    Replaces with 'https://anonymized.example.com/path'.

    Args:
        url_str: URL string.
        level: 'partial' or 'full'.

    Returns:
        Anonymized URL string.
    """
    if level == 'full':
        return "https://anonymized.example.com/path"
    try:
        parsed_url = urlparse(url_str)
        anonymized_netloc = anonymize_domain_name(parsed_url.hostname, level='partial') if parsed_url.hostname else "anonymized.host"
        # Keep scheme, anonymize netloc, generic path, no query/fragment
        return urlunparse((parsed_url.scheme, anonymized_netloc, "/anonymized_path", "", "", ""))
    except Exception: # Broad catch for any parsing errors
        return "https://anonymized.example.com/invalid_url_format"

def anonymize_file_hash(hash_value: str, hash_type: Optional[str] = None, level: str = 'partial') -> str:
    """
    Anonymize a file hash.
    'partial': Replaces with a derived hash of the same length, prefixed 'anon:'. This is NOT a true anonymization
               that hides the original, but a placeholder. Real anonymization would omit or generalize.
    'full':    Replaces with a generic placeholder like 'anon:[HASH_TYPE_ANONYMIZED]'.

    Args:
        hash_value: Hash string.
        hash_type: Type of hash (e.g., 'MD5', 'SHA256'). Used for 'full' anonymization placeholder.
        level: 'partial' or 'full'.

    Returns:
        Anonymized hash string.
    """
    if level == 'full':
        ht = hash_type.upper() if hash_type else "HASH"
        return f"anon:[{ht}_VALUE_REMOVED]"

    # Partial: Create a derived placeholder. This is more for indicating redaction
    # while maintaining format if absolutely necessary for some systems, not for true privacy.
    # A better partial approach for hashes might be to generalize (e.g., "known_malware_hash_type_sha256")
    # or omit entirely.
    # For this implementation, we generate a new hash of the original to act as a *consistent* placeholder.
    if not hash_value: return ""
    derived_hash = hashlib.sha256(f"SALT_FOR_ANON_{hash_value}".encode()).hexdigest()
    return f"anon:{derived_hash[:len(hash_value)]}" # Truncate to original length

def anonymize_registry_key(key_path: str, level: str = 'partial') -> str:
    """
    Anonymize a registry key path.
    'partial': Anonymizes specific value names or user-specific parts.
    'full':    Replaces with a generic path.

    Args:
        key_path: Registry key path string.
        level: 'partial' or 'full'.

    Returns:
        Anonymized registry key path string.
    """
    if level == 'full':
        return "HKEY_LOCAL_MACHINE\\Software\\Anonymized\\Key"

    # Partial: Look for user-specific parts or highly variable parts
    # Example: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\RandomApp ->
    #          HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\[ANON_APP_NAME]
    # This requires more sophisticated regex based on common registry structures.
    # For now, a simpler approach:
    parts = key_path.split('\\')
    if len(parts) > 3: # If it's a somewhat deep path
        # Anonymize the last part if it seems like a specific entry
        if not any(kw in parts[-1].upper() for kw in ['WINDOWS', 'MICROSOFT', 'SYSTEM', 'SOFTWARE', 'CLASSES', 'USERS']):
            parts[-1] = f"[ANON_VALUE_{hashlib.md5(parts[-1].encode()).hexdigest()[:6]}]"
    return '\\'.join(parts)

# --- STIX Pattern Anonymization ---

def _anonymize_pattern_comparison_expression(comp_expr: str, level: str) -> str:
    """Anonymizes a single comparison expression within a STIX pattern."""
    # Regex to find observable_type:object_path = 'value' or LIKE 'value' or IN ('v1', 'v2')
    # This is a simplified regex and might need to be more robust for all STIX path/operator cases.
    # It focuses on the RHS literal value.
    match = re.match(r"([\w\-\.]+:\S+)\s*([=><!]|LIKE|IN)\s*(['\"].*?['\"]|\[.*?\]|\d+(\.\d+)?)", comp_expr.strip())
    if not match:
        return comp_expr # Cannot parse, return as is

    lhs, operator, rhs_literal = match.groups()
    rhs_original = rhs_literal # Keep original for processing

    # Remove quotes/brackets for value processing if present
    if (rhs_literal.startswith("'") and rhs_literal.endswith("'")) or \
       (rhs_literal.startswith('"') and rhs_literal.endswith('"')):
        value_to_anonymize = rhs_literal[1:-1]
    elif rhs_literal.startswith('[') and rhs_literal.endswith(']'): # For IN operator
        # Handle IN operator values, e.g. IN ('val1', 'val2')
        # This is a complex case; for now, we'll just anonymize the whole list representation
        return f"{lhs} {operator} [ANON_LIST_VALUES]"
    else:
        value_to_anonymize = rhs_literal


    anonymized_value = value_to_anonymize # Default to original if no specific rule applies

    # Determine anonymization based on object_path (LHS)
    if 'ipv4-addr:value' in lhs or 'ipv6-addr:value' in lhs:
        anonymized_value = anonymize_ip_address(value_to_anonymize, level)
    elif 'domain-name:value' in lhs:
        anonymized_value = anonymize_domain_name(value_to_anonymize, level)
    elif 'email-message:sender_ref.value' in lhs or 'email-addr:value' in lhs: # Assuming email-addr for sender
        anonymized_value = anonymize_email_address(value_to_anonymize, level)
    elif 'url:value' in lhs:
        anonymized_value = anonymize_url(value_to_anonymize, level)
    elif any(hash_type in lhs for hash_type in ['MD5', 'SHA-1', 'SHA-256']): # e.g., file:hashes.MD5
        hash_type_in_pattern = lhs.split('.')[-1] # Get the hash type like MD5 from 'file:hashes.MD5'
        anonymized_value = anonymize_file_hash(value_to_anonymize, hash_type_in_pattern, level)
    elif 'windows-registry-key:key' in lhs:
        anonymized_value = anonymize_registry_key(value_to_anonymize, level)
    # Add more rules for other STIX objects and paths
    # e.g., file:name, user-account:user_id etc.
    elif 'file:name' in lhs and level == 'full':
        anonymized_value = "anonymized_filename.exe"
    elif 'user-account:user_id' in lhs and level == 'full':
        anonymized_value = "anon_user"


    # Re-add quotes if they were originally present
    if (rhs_original.startswith("'") and rhs_original.endswith("'")):
        return f"{lhs} {operator} '{anonymized_value}'"
    elif (rhs_original.startswith('"') and rhs_original.endswith('"')):
        return f"{lhs} {operator} \"{anonymized_value}\""
    else: # For unquoted literals like numbers
        return f"{lhs} {operator} {anonymized_value}"


def anonymize_stix_pattern(pattern: str, level: str = 'partial') -> str:
    """
    Anonymize a STIX pattern by processing its comparison expressions.
    This is a basic implementation and may not cover all STIX pattern complexities.
    It primarily focuses on anonymizing literal values in comparisons.

    Args:
        pattern: STIX pattern string.
        level: 'partial' or 'full'.

    Returns:
        Anonymized STIX pattern string.
    """
    if not pattern or not isinstance(pattern, str):
        return ""

    # Split pattern by boolean operators (AND, OR, NOT) and observation operators (FOLLOWEDBY)
    # preserving them and the qualifiers like [START t'...' STOP t'...'].
    # This regex is complex and aims to correctly segment the pattern.
    # It looks for operators surrounded by spaces, or qualifiers.
    # It also considers parentheses for grouping.
    # A full STIX pattern parser would be more robust here.
    # For now, we assume simple expressions or expressions joined by AND/OR.
    # We'll split by AND/OR for simplicity, this won't correctly handle FOLLOWEDBY or complex qualifiers.

    # A simpler approach: iterate through expressions if they are clearly separated.
    # Assuming expressions are of the form [type:property qualifier value]
    # This is highly simplified. A proper STIX pattern parser is needed for robustness.
    # For this iteration, we apply anonymization to identifiable literals directly using regex.

    # Anonymize IPs
    pattern = re.sub(r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)",
                     lambda m: anonymize_ip_address(m.group(1), level), pattern)
    # Anonymize Domains
    pattern = re.sub(r"([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.(?:[a-zA-Z]{2,6}|[a-zA-Z0-9\-]{2,}\.[a-zA-Z]{2,}))", # More robust domain regex
                     lambda m: anonymize_domain_name(m.group(1), level), pattern)
    # Anonymize Emails
    pattern = re.sub(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                     lambda m: anonymize_email_address(m.group(1), level), pattern)
    # Anonymize URLs
    pattern = re.sub(r"(?:https?|ftp)://[^\s/$.?#].[^\s]*", # Basic URL regex
                     lambda m: anonymize_url(m.group(1), level), pattern)

    # Anonymize Hashes (example for SHA256, extend for others)
    pattern = re.sub(r"SHA256\s*=\s*'([a-fA-F0-9]{64})'",
                     lambda m: f"SHA256 = '{anonymize_file_hash(m.group(1), 'SHA256', level)}'", pattern)
    pattern = re.sub(r"MD5\s*=\s*'([a-fA-F0-9]{32})'",
                     lambda m: f"MD5 = '{anonymize_file_hash(m.group(1), 'MD5', level)}'", pattern)


    # If level is 'full', make common paths generic
    if level == 'full':
        pattern = re.sub(r"file:hashes\.(MD5|SHA1|SHA256)\s*=",
                         lambda m: f"file:hashes.{m.group(1).upper()} = '[ANONYMIZED_HASH]'", pattern, flags=re.IGNORECASE)
        pattern = re.sub(r"file:name\s*=", "file:name = '[ANONYMIZED_FILENAME]'", pattern, flags=re.IGNORECASE)
        pattern = re.sub(r"user-account:user_id\s*=", "user-account:user_id = '[ANONYMIZED_USER]'", pattern, flags=re.IGNORECASE)

    return pattern


# --- General Text Redaction ---
def redact_text_field(text: str, level: str = 'partial') -> str:
    """
    Redact sensitive information from a generic text field.
    'partial': Applies specific anonymizers (IP, email, URL).
    'full':    Replaces entire text with a placeholder.

    Args:
        text: Text string.
        level: 'partial' or 'full'.

    Returns:
        Redacted text string.
    """
    if not text or not isinstance(text, str):
        return ""

    if level == 'full':
        return "[REDACTED CONTENT]"

    # Partial redaction:
    text = re.sub(r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)", lambda m: anonymize_ip_address(m.group(1), level='partial'), text)
    text = re.sub(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", lambda m: anonymize_email_address(m.group(1), level='partial'), text)
    text = re.sub(r"(?:https?|ftp)://[^\s/$.?#].[^\s]*", lambda m: anonymize_url(m.group(1), level='partial'), text)

    # Redact common PII keywords if it's a free text field like description
    # This is very basic and prone to false positives/negatives.
    # For true PII redaction, NLP tools are usually needed.
    # sensitive_keywords = ['Social Security Number', 'SSN', 'password', 'credit card'] # Example
    # for kw in sensitive_keywords:
    #    text = re.sub(rf'\b{kw}\b.*?(\d+|\w+)\b', f'[{kw} REDACTED]', text, flags=re.IGNORECASE)

    return text