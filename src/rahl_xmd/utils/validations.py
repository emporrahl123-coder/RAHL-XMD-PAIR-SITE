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
    if not isinstance(code
