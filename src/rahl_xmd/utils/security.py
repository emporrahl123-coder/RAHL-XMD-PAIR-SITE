"""
Security utilities for RAHL XMD.
"""

import hashlib
import hmac
import base64
import secrets
from typing import Optional, Union
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class SecurityManager:
    """Manage security operations for RAHL XMD."""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize security manager.
        
        Args:
            secret_key: Optional secret key for encryption
        """
        self.secret_key = secret_key or self._generate_secret_key()
        self.fernet = self._create_fernet(self.secret_key)
    
    @staticmethod
    def _generate_secret_key() -> str:
        """Generate a random secret key."""
        return secrets.token_urlsafe(32)
    
    def _create_fernet(self, password: str) -> Fernet:
        """Create Fernet instance from password."""
        # Derive key from password
        salt = b'rahl_xmd_salt_'  # In production, use random salt stored securely
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return Fernet(key)
    
    def encrypt_data(self, data: Union[str, dict]) -> str:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (string or dict)
        
        Returns:
            Encrypted string
        """
        if isinstance(data, dict):
            data = json.dumps(data)
        
        encrypted = self.fernet.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt_data(self, encrypted_data: str) -> Union[str, dict]:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted string
        
        Returns:
            Decrypted data (parsed as dict if possible, otherwise string)
        """
        decrypted = self.fernet.decrypt(encrypted_data.encode()).decode()
        
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return decrypted
    
    def generate_secure_hash(self, data: str, salt: Optional[str] = None) -> str:
        """
        Generate secure hash of data.
        
        Args:
            data: Data to hash
            salt: Optional salt
        
        Returns:
            Hashed string
        """
        if salt:
            data = salt + data
        
        # Use SHA-256
        return hashlib.sha256(data.encode()).hexdigest()
    
    def generate_hmac(self, data: str, key: Optional[str] = None) -> str:
        """
        Generate HMAC for data.
        
        Args:
            data: Data to sign
            key: Optional key (uses secret_key if not provided)
        
        Returns:
            HMAC string
        """
        key = key or self.secret_key
        return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()
    
    def verify_hmac(self, data: str, signature: str, key: Optional[str] = None) -> bool:
        """
        Verify HMAC signature.
        
        Args:
            data: Original data
            signature: HMAC signature
            key: Optional key
        
        Returns:
            True if signature is valid
        """
        expected = self.generate_hmac(data, key)
        return hmac.compare_digest(expected, signature)
    
    def generate_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure token.
        
        Args:
            length: Token length
        
        Returns:
            Token string
        """
        return secrets.token_urlsafe(length)
    
    def generate_code(self, length: int = 8, 
                     chars: str = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789") -> str:
        """
        Generate secure code (excludes similar characters).
        
        Args:
            length: Code length
            chars: Character set to use
        
        Returns:
            Code string
        """
        return ''.join(secrets.choice(chars) for _ in range(length))


# Global instance
_default_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get or create default security manager."""
    global _default_security_manager
    if _default_security_manager is None:
        _default_security_manager = SecurityManager()
    return _default_security_manager


def generate_secure_hash(data: str, salt: Optional[str] = None) -> str:
    """Generate secure hash."""
    return get_security_manager().generate_secure_hash(data, salt)


def encrypt_data(data: Union[str, dict]) -> str:
    """Encrypt data."""
    return get_security_manager().encrypt_data(data)


def decrypt_data(encrypted_data: str) -> Union[str, dict]:
    """Decrypt data."""
    return get_security_manager().decrypt_data(encrypted_data)


def generate_token(length: int = 32) -> str:
    """Generate secure token."""
    return get_security_manager().generate_token(length)


def generate_code(length: int = 8) -> str:
    """Generate secure code."""
    return get_security_manager().generate_code(length)
