"""
Helper functions for RAHL XMD.
"""

import uuid
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import hashlib


def generate_id(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique ID.
    
    Args:
        prefix: ID prefix
        length: ID length (excluding prefix)
    
    Returns:
        Unique ID string
    """
    # Generate random alphanumeric string
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(chars, k=length))
    
    return f"{prefix}{random_part}"


def format_timedelta(delta: timedelta) -> str:
    """
    Format timedelta to human-readable string.
    
    Args:
        delta: Time delta
    
    Returns:
        Formatted string
    """
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        return f"{days}d {hours}h"


def calculate_compatibility(user1_interests: List[str], 
                          user2_interests: List[str],
                          user1_prefs: Dict[str, Any],
                          user2_prefs: Dict[str, Any]) -> float:
    """
    Calculate compatibility score between two users.
    
    Args:
        user1_interests: First user's interests
        user2_interests: Second user's interests
        user1_prefs: First user's preferences
        user2_prefs: Second user's preferences
    
    Returns:
        Compatibility score (0.0 to 1.0)
    """
    score = 0.0
    
    # Interest matching (40%)
    if user1_interests and user2_interests:
        common_interests = set(user1_interests) & set(user2_interests)
        interest_score = len(common_interests) / max(len(user1_interests), 1) * 0.4
        score += interest_score
    
    # Preference matching (30%)
    # Compare age if available
    age1 = user1_prefs.get('age')
    age2 = user2_prefs.get('age')
    if age1 and age2:
        age_diff = abs(age1 - age2)
        if age_diff <= 5:
            score += 0.15
        elif age_diff <= 10:
            score += 0.1
        else:
            score += 0.05
    
    # Timezone matching (10%)
    tz1 = user1_prefs.get('timezone')
    tz2 = user2_prefs.get('timezone')
    if tz1 and tz2 and tz1 == tz2:
        score += 0.1
    
    # Language matching (10%)
    lang1 = user1_prefs.get('language', 'en')
    lang2 = user2_prefs.get('language', 'en')
    if lang1 == lang2:
        score += 0.1
    
    # Random factor for variety (10%)
    random_factor = hash(f"{str(user1_prefs)}{str(user2_prefs)}") % 100 / 1000
    score += random_factor
    
    return min(score, 1.0)


def find_shared_interests(user1_interests: List[str], 
                         user2_interests: List[str]) -> List[str]:
    """
    Find shared interests between two users.
    
    Args:
        user1_interests: First user's interests
        user2_interests: Second user's interests
    
    Returns:
        List of shared interests
    """
    return list(set(user1_interests) & set(user2_interests))


def generate_color_from_string(text: str) -> Tuple[int, int, int]:
    """
    Generate a consistent color from a string.
    
    Args:
        text: Input text
    
    Returns:
        RGB color tuple
    """
    # Generate hash
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Take first 6 characters for color
    color_hex = hash_hex[:6]
    
    # Convert to RGB
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    
    return (r, g, b)


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_duration_string(duration_str: str) -> Optional[timedelta]:
    """
    Parse duration string to timedelta.
    
    Args:
        duration_str: Duration string (e.g., "2h30m", "1d", "45m")
    
    Returns:
        Timedelta or None if invalid
    """
    try:
        # Parse days
        days = 0
        if 'd' in duration_str:
            day_part = duration_str.split('d')[0]
            days = int(day_part)
            duration_str = duration_str.split('d')[1] if 'd' in duration_str[1:] else ''
        
        # Parse hours
        hours = 0
        if 'h' in duration_str:
            hour_part = duration_str.split('h')[0]
            hours = int(hour_part)
            duration_str = duration_str.split('h')[1] if 'h' in duration_str[1:] else ''
        
        # Parse minutes
        minutes = 0
        if 'm' in duration_str:
            minute_part = duration_str.split('m')[0]
            minutes = int(minute_part)
        
        return timedelta(days=days, hours=hours, minutes=minutes)
    
    except (ValueError, IndexError):
        return None


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Filename
    
    Returns:
        File extension (lowercase, without dot)
    """
    return filename.split('.')[-1].lower() if '.' in filename else ''


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem use.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    import re
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250 - len(ext)] + '.' + ext
    
    return filename
