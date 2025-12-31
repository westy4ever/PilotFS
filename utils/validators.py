import os
import re
import shlex

def validate_path(path, must_exist=False, must_be_dir=False, must_be_file=False):
    """
    Validate file path
    
    Args:
        path: Path to validate
        must_exist: If True, path must exist
        must_be_dir: If True, path must be a directory
        must_be_file: If True, path must be a file
    
    Returns:
        bool: True if path is valid
    """
    if not path or not isinstance(path, str):
        return False
    
    # Check for path traversal attempts
    if '..' in path or path.startswith('/etc/passwd') or path.startswith('/etc/shadow'):
        return False
    
    # Check for null bytes
    if '\x00' in path:
        return False
    
    # Check if path exists if required
    if must_exist and not os.path.exists(path):
        return False
    
    # Check if path is directory if required
    if must_be_dir and not os.path.isdir(path):
        return False
    
    # Check if path is file if required
    if must_be_file and not os.path.isfile(path):
        return False
    
    return True

def validate_ip(ip_address):
    """
    Validate IP address
    
    Args:
        ip_address: IP address to validate
    
    Returns:
        bool: True if IP is valid
    """
    if not ip_address or not isinstance(ip_address, str):
        return False
    
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if not re.match(ipv4_pattern, ip_address):
        return False
    
    # Check each octet
    parts = ip_address.split('.')
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    
    return True

def validate_hostname(hostname):
    """
    Validate hostname
    
    Args:
        hostname: Hostname to validate
    
    Returns:
        bool: True if hostname is valid
    """
    if not hostname or not isinstance(hostname, str):
        return False
    
    # Basic hostname pattern
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    
    return bool(re.match(pattern, hostname)) and len(hostname) <= 255

def validate_url(url):
    """
    Validate URL
    
    Args:
        url: URL to validate
    
    Returns:
        bool: True if URL is valid
    """
    if not url or not isinstance(url, str):
        return False
    
    # Basic URL pattern
    pattern = r'^(https?|ftp|file)://.+'
    
    return bool(re.match(pattern, url))

def validate_port(port):
    """
    Validate port number
    
    Args:
        port: Port number to validate
    
    Returns:
        bool: True if port is valid
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False

def sanitize_string(text, max_length=255, allow_special=False):
    """
    Sanitize input string
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        allow_special: Allow special characters
    
    Returns:
        str: Sanitized string or empty string if invalid
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32)
    
    # Truncate to max length
    text = text[:max_length]
    
    if not allow_special:
        # Remove potentially dangerous characters
        dangerous = [';', '|', '&', '$', '`', '>', '<', '!']
        for char in dangerous:
            text = text.replace(char, '')
    
    return text.strip()

def validate_filename(filename):
    """
    Validate filename
    
    Args:
        filename: Filename to validate
    
    Returns:
        bool: True if filename is valid
    """
    if not filename or not isinstance(filename, str):
        return False
    
    # Check for invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\x00']
    for char in invalid_chars:
        if char in filename:
            return False
    
    # Check for reserved names (Windows, but good practice)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        return False
    
    # Check length
    if len(filename) > 255:
        return False
    
    return True

def validate_email(email):
    """
    Validate email address
    
    Args:
        email: Email to validate
    
    Returns:
        bool: True if email is valid
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_integer(value, min_value=None, max_value=None):
    """
    Validate integer
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    
    Returns:
        bool: True if integer is valid
    """
    try:
        num = int(value)
        
        if min_value is not None and num < min_value:
            return False
        
        if max_value is not None and num > max_value:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def validate_float(value, min_value=None, max_value=None):
    """
    Validate float
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    
    Returns:
        bool: True if float is valid
    """
    try:
        num = float(value)
        
        if min_value is not None and num < min_value:
            return False
        
        if max_value is not None and num > max_value:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def escape_shell_argument(arg):
    """
    Escape shell argument to prevent injection
    
    Args:
        arg: Argument to escape
    
    Returns:
        str: Escaped argument
    """
    return shlex.quote(str(arg))

def validate_json(text):
    """
    Validate JSON string
    
    Args:
        text: JSON string to validate
    
    Returns:
        bool: True if JSON is valid
    """
    import json
    
    try:
        json.loads(text)
        return True
    except (ValueError, TypeError):
        return False

def validate_regex(pattern):
    """
    Validate regex pattern
    
    Args:
        pattern: Regex pattern to validate
    
    Returns:
        bool: True if regex is valid
    """
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False