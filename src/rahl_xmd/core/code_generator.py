"""
Code generation utilities for RAHL XMD pairing system.
"""

import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum

from .pairing_system import CodeTheme, PairingCode


class CodeFormat(str, Enum):
    """Code format options."""
    ALPHANUMERIC = "alphanumeric"
    NUMERIC = "numeric"
    HEXADECIMAL = "hex"
    CUSTOM = "custom"


class CodeGenerator:
    """Generates and manages pairing codes."""
    
    def __init__(self, 
                 default_length: int = 8,
                 default_format: CodeFormat = CodeFormat.ALPHANUMERIC,
                 exclude_similar: bool = True):
        """
        Initialize code generator.
        
        Args:
            default_length: Default code length
            default_format: Default code format
            exclude_similar: Exclude similar characters (1/l/I, 0/O)
        """
        self.default_length = default_length
        self.default_format = default_format
        self.exclude_similar = exclude_similar
        
        # Character sets
        self._char_sets = {
            CodeFormat.ALPHANUMERIC: {
                'all': string.ascii_uppercase + string.digits,
                'excluded': '01IO' if exclude_similar else ''
            },
            CodeFormat.NUMERIC: {
                'all': string.digits,
                'excluded': '01' if exclude_similar else ''
            },
            CodeFormat.HEXADECIMAL: {
                'all': string.hexdigits.upper(),
                'excluded': ''
            }
        }
    
    def generate_code(self, 
                     length: Optional[int] = None,
                     code_format: Optional[CodeFormat] = None,
                     prefix: str = "",
                     suffix: str = "",
                     separator: str = "-",
                     groups: int = 1) -> str:
        """
        Generate a random code.
        
        Args:
            length: Code length (excluding prefix/suffix)
            code_format: Code format
            prefix: Code prefix
            suffix: Code suffix
            separator: Group separator
            groups: Number of groups
        
        Returns:
            Generated code string
        """
        length = length or self.default_length
        code_format = code_format or self.default_format
        
        if code_format == CodeFormat.CUSTOM:
            raise ValueError("Custom format requires custom character set")
        
        # Get character set
        char_set_info = self._char_sets[code_format]
        chars = char_set_info['all']
        
        if self.exclude_similar and char_set_info['excluded']:
            chars = ''.join(c for c in chars if c not in char_set_info['excluded'])
        
        if not chars:
            raise ValueError("No characters available in the selected format")
        
        # Generate code
        if groups > 1:
            group_length = length // groups
            remainder = length % groups
            code_parts = []
            
            for i in range(groups):
                part_length = group_length + (1 if i < remainder else 0)
                part = ''.join(random.choices(chars, k=part_length))
                code_parts.append(part)
            
            code = separator.join(code_parts)
        else:
            code = ''.join(random.choices(chars, k=length))
        
        return prefix + code + suffix
    
    def generate_batch(self, 
                      count: int,
                      length: Optional[int] = None,
                      code_format: Optional[CodeFormat] = None,
                      **kwargs) -> List[str]:
        """
        Generate a batch of unique codes.
        
        Args:
            count: Number of codes to generate
            length: Code length
            code_format: Code format
            **kwargs: Additional parameters for generate_code
        
        Returns:
            List of unique codes
        """
        codes = set()
        attempts = 0
        max_attempts = count * 10
        
        while len(codes) < count and attempts < max_attempts:
            code = self.generate_code(length, code_format, **kwargs)
            codes.add(code)
            attempts += 1
        
        if len(codes) < count:
            raise RuntimeError(f"Failed to generate {count} unique codes after {max_attempts} attempts")
        
        return list(codes)
    
    def validate_code_format(self, 
                           code: str,
                           length: Optional[int] = None,
                           code_format: Optional[CodeFormat] = None,
                           prefix: str = "",
                           suffix: str = "") -> bool:
        """
        Validate code format.
        
        Args:
            code: Code to validate
            length: Expected length
            code_format: Expected format
            prefix: Expected prefix
            suffix: Expected suffix
        
        Returns:
            True if code format is valid
        """
        # Check prefix and suffix
        if not code.startswith(prefix) or not code.endswith(suffix):
            return False
        
        # Extract core code
        core_code = code[len(prefix):-len(suffix)] if suffix else code[len(prefix):]
        
        # Check length
        if length and len(core_code) != length:
            return False
        
        # Check format
        if code_format and code_format != CodeFormat.CUSTOM:
            char_set_info = self._char_sets[code_format]
            allowed_chars = set(char_set_info['all'])
            
            if self.exclude_similar and char_set_info['excluded']:
                allowed_chars -= set(char_set_info['excluded'])
            
            return all(c in allowed_chars for c in core_code)
        
        return True
    
    def generate_secure_code(self, 
                           seed: str,
                           length: int = 16,
                           iterations: int = 1000) -> str:
        """
        Generate a deterministic secure code from a seed.
        
        Args:
            seed: Seed string
            length: Code length
            iterations: Number of hash iterations
        
        Returns:
            Secure code string
        """
        # Start with seed hash
        current_hash = hashlib.sha256(seed.encode()).hexdigest().upper()
        
        # Iterative hashing
        for _ in range(iterations - 1):
            current_hash = hashlib.sha256(current_hash.encode()).hexdigest().upper()
        
        # Take first 'length' characters
        return current_hash[:length]
    
    def create_pairing_code(self,
                           owner_id: str,
                           code: Optional[str] = None,
                           max_uses: int = 1,
                           expires_hours: int = 24,
                           theme: CodeTheme = CodeTheme.DEFAULT,
                           is_animated: bool = True,
                           metadata: Optional[Dict] = None) -> PairingCode:
        """
        Create a PairingCode object.
        
        Args:
            owner_id: User ID of code owner
            code: Custom code (generated if None)
            max_uses: Maximum uses
            expires_hours: Hours until expiration
            theme: Visual theme
            is_animated: Whether animated
            metadata: Additional metadata
        
        Returns:
            PairingCode object
        """
        if code is None:
            code = self.generate_code()
        
        return PairingCode(
            code=code,
            owner_id=owner_id,
            max_uses=max_uses,
            expires_at=datetime.now() + timedelta(hours=expires_hours),
            theme=theme,
            is_animated=is_animated,
            metadata=metadata or {}
        )
    
    def generate_readable_code(self, 
                             word_list: Optional[List[str]] = None,
                             word_count: int = 2,
                             separator: str = "-") -> str:
        """
        Generate a human-readable code using words.
        
        Args:
            word_list: List of words to choose from
            word_count: Number of words
            separator: Word separator
        
        Returns:
            Readable code
        """
        if word_list is None:
            # Default word list (common, easy to spell)
            word_list = [
                "RED", "BLUE", "GREEN", "GOLD", "SILVER",
                "STAR", "MOON", "SUN", "SKY", "OCEAN",
                "LION", "EAGLE", "DRAGON", "PHOENIX", "WOLF",
                "FIRE", "ICE", "WIND", "EARTH", "WATER",
                "ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA",
                "NOVA", "QUANTUM", "COSMIC", "GALAXY", "STAR"
            ]
        
        words = random.sample(word_list, min(word_count, len(word_list)))
        return separator.join(words)
