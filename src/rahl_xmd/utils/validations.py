"""
Validation utilities for RAHL XMD.
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from email.utils import parseaddr


def validate_user_data(user_data: Dict[str, Any]) -> bool:
    """
    Validate user registration data.
    
    Args:
        user_data: User data dictionary
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If validation fails
    """
    # Check required fields
    required_fields = ['user_id', 'username']
    for field in required_fields:
        if field not in user_data:
            raise ValueError(f"Missing required field: {field}")
    
    user_id = user_data['user_id']
    username = user_data['username']
    
    # Validate user_id
    if not isinstance(user_id, str):
        raise ValueError("user_id must be a string")
    if len(user_id) < 3:
        raise ValueError("user_id must be at least 3 characters")
    if len(user_id) > 50:
        raise ValueError("user_id must not exceed 50 characters")
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise ValueError("user_id can only contain letters, numbers, underscores, and hyphens")
    
    # Validate username
    if not isinstance(username, str):
        raise ValueError("username must be a string")
    if len(username) < 2:
        raise ValueError("username must be at least 2 characters")
    if len(username) > 30:
        raise ValueError("username must not exceed 30 characters")
    
    # Validate email if provided
    email = user_data.get('email')
    if email and not validate_email(email):
        raise ValueError("Invalid email address")
    
    # Validate preferences
    preferences = user_data.get('preferences', {})
    if not isinstance(preferences, dict):
        raise ValueError("preferences must be a dictionary")
    
    # Validate interests
    interests = user_data.get('interests', [])
    if not isinstance(interests, list):
        raise ValueError("interests must be a list")
    for interest in interests:
        if not isinstance(interest, str):
            raise ValueError("All interests must be strings")
        if len(interest) > 50:
            raise ValueError("Interest too long (max 50 characters)")
    
    return True


def validate_pairing_code(code: str) -> bool:
    """
    Validate pairing code format.
    
    Args:
        code: Pairing code string
    
    Returns:
        True if valid
    """
    if not isinstance(code, str):
        return False
    
    # Check length
    if len(code) < 6 or len(code) > 20:
        return False
    
    # Alphanumeric with optional separators
    if not re.match(r'^[A-Z0-9][A-Z0-9-]*[A-Z0-9]$', code):
        return False
    
    return True


def validate_email(email: str) -> bool:
    """
    Validate email address.
    
    Args:
        email: Email address string
    
    Returns:
        True if valid
    """
    if not isinstance(email, str):
        return False
    
    # Check format
    parsed = parseaddr(email)
    if '@' not in parsed[1]:
        return False
    
    # Basic regex validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_theme(theme: str) -> bool:
    """
    Validate theme name.
    
    Args:
        theme: Theme name string
    
    Returns:
        True if valid
    """
    valid_themes = {'default', 'neon', 'cyberpunk', 'matrix', 'aurora', 'hologram'}
    return theme.lower() in valid_themes


def validate_duration(duration_hours: int) -> bool:
    """
    Validate duration in hours.
    
    Args:
        duration_hours: Duration in hours
    
    Returns:
        True if valid
    """
    return isinstance(duration_hours, int) and 1 <= duration_hours <= 720  # Max 30 days


def validate_max_uses(max_uses: int) -> bool:
    """
    Validate maximum uses.
    
    Args:
        max_uses: Maximum number of uses
    
    Returns:
        True if valid
    """
    return isinstance(max_uses, int) and 1 <= max_uses <= 1000


def validate_timestamp(timestamp: str) -> bool:
    """
    Validate ISO timestamp.
    
    Args:
        timestamp: ISO format timestamp string
    
    Returns:
        True if valid
    """
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return True
    except (ValueError, TypeError):
        return False


def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate metadata dictionary.
    
    Args:
        metadata: Metadata dictionary
    
    Returns:
        True if valid
    """
    if not isinstance(metadata, dict):
        return False
    
    # Check size limits
    import json
    metadata_json = json.dumps(metadata)
    if len(metadata_json) > 10000:  # 10KB limit
        return False
    
    return True
