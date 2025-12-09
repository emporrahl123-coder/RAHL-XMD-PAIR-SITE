"""
Core pairing system for RAHL XMD.
Handles user management, pairing logic, and code generation.
"""

import uuid
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import pickle
import hashlib

from ..utils.logger import setup_logger
from ..utils.validators import validate_user_data, validate_pairing_code
from ..utils.security import generate_secure_hash

logger = setup_logger(__name__)


class PairingStatus(str, Enum):
    """Status of a pairing relationship."""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ARCHIVED = "archived"


class CodeTheme(str, Enum):
    """Visual themes for pairing codes."""
    DEFAULT = "default"
    NEON = "neon"
    CYBERPUNK = "cyberpunk"
    MATRIX = "matrix"
    AURORA = "aurora"
    HOLOGRAM = "hologram"


@dataclass
class UserProfile:
    """User profile data structure."""
    user_id: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    is_verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_active'] = self.last_active.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_active'] = datetime.fromisoformat(data['last_active'])
        return cls(**data)


@dataclass
class PairingCode:
    """Pairing code data structure."""
    code: str
    owner_id: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    max_uses: int = 1
    uses_count: int = 0
    theme: CodeTheme = CodeTheme.DEFAULT
    is_animated: bool = True
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set default expiration if not provided."""
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=24)
    
    @property
    def is_valid(self) -> bool:
        """Check if the code is still valid."""
        now = datetime.now()
        return (
            self.is_active and
            self.uses_count < self.max_uses and
            now < self.expires_at
        )
    
    @property
    def time_remaining(self) -> timedelta:
        """Get time remaining until expiration."""
        return max(self.expires_at - datetime.now(), timedelta(0))
    
    def use(self) -> bool:
        """Mark the code as used once."""
        if self.is_valid:
            self.uses_count += 1
            return True
        return False
    
    def revoke(self) -> None:
        """Revoke the code."""
        self.is_active = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        data['theme'] = self.theme.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PairingCode':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        data['theme'] = CodeTheme(data['theme'])
        return cls(**data)


@dataclass
class Pairing:
    """Pairing relationship data structure."""
    pairing_id: str
    user1_id: str
    user2_id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: PairingStatus = PairingStatus.PENDING
    compatibility_score: float = 0.0
    shared_interests: List[str] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if pairing is active."""
        return self.status == PairingStatus.ACTIVE
    
    def update_interaction(self) -> None:
        """Update last interaction time."""
        self.last_interaction = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_interaction'] = self.last_interaction.isoformat()
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pairing':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_interaction'] = datetime.fromisoformat(data['last_interaction'])
        data['status'] = PairingStatus(data['status'])
        return cls(**data)


class PairingSystem:
    """Main pairing system class."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the pairing system.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Storage dictionaries
        self.users: Dict[str, UserProfile] = {}
        self.codes: Dict[str, PairingCode] = {}
        self.pairings: Dict[str, Pairing] = {}
        self.user_pairings: Dict[str, List[str]] = {}
        
        # Load existing data
        self._load_data()
        
        logger.info("Pairing system initialized")
    
    def _get_file_path(self, filename: str) -> Path:
        """Get full path for data file."""
        return self.data_dir / filename
    
    def _load_data(self) -> None:
        """Load data from disk."""
        try:
            # Load users
            users_file = self._get_file_path("users.json")
            if users_file.exists():
                with open(users_file, 'r') as f:
                    users_data = json.load(f)
                    self.users = {uid: UserProfile.from_dict(data) 
                                 for uid, data in users_data.items()}
            
            # Load codes
            codes_file = self._get_file_path("codes.json")
            if codes_file.exists():
                with open(codes_file, 'r') as f:
                    codes_data = json.load(f)
                    self.codes = {code: PairingCode.from_dict(data) 
                                 for code, data in codes_data.items()}
            
            # Load pairings
            pairings_file = self._get_file_path("pairings.json")
            if pairings_file.exists():
                with open(pairings_file, 'r') as f:
                    pairings_data = json.load(f)
                    self.pairings = {pid: Pairing.from_dict(data) 
                                    for pid, data in pairings_data.items()}
            
            # Rebuild user_pairings index
            self.user_pairings = {}
            for pairing_id, pairing in self.pairings.items():
                for user_id in [pairing.user1_id, pairing.user2_id]:
                    if user_id not in self.user_pairings:
                        self.user_pairings[user_id] = []
                    self.user_pairings[user_id].append(pairing_id)
            
            logger.info(f"Loaded {len(self.users)} users, {len(self.codes)} codes, "
                       f"{len(self.pairings)} pairings")
        
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
    
    def _save_data(self) -> None:
        """Save data to disk."""
        try:
            # Save users
            users_file = self._get_file_path("users.json")
            users_data = {uid: user.to_dict() for uid, user in self.users.items()}
            with open(users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            
            # Save codes
            codes_file = self._get_file_path("codes.json")
            codes_data = {code: pc.to_dict() for code, pc in self.codes.items()}
            with open(codes_file, 'w') as f:
                json.dump(codes_data, f, indent=2)
            
            # Save pairings
            pairings_file = self._get_file_path("pairings.json")
            pairings_data = {pid: pairing.to_dict() for pid, pairing in self.pairings.items()}
            with open(pairings_file, 'w') as f:
                json.dump(pairings_data, f, indent=2)
            
            logger.debug("Data saved successfully")
        
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
    
    def register_user(self, user_id: str, username: str, **kwargs) -> UserProfile:
        """
        Register a new user.
        
        Args:
            user_id: Unique user identifier
            username: Display name
            **kwargs: Additional user data
        
        Returns:
            UserProfile object
        
        Raises:
            ValueError: If user already exists or data is invalid
        """
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        # Validate user data
        user_data = {
            "user_id": user_id,
            "username": username,
            **kwargs
        }
        validate_user_data(user_data)
        
        # Create user profile
        user = UserProfile(
            user_id=user_id,
            username=username,
            email=kwargs.get('email'),
            avatar_url=kwargs.get('avatar_url'),
            preferences=kwargs.get('preferences', {}),
            interests=kwargs.get('interests', []),
            is_verified=kwargs.get('is_verified', False)
        )
        
        self.users[user_id] = user
        self.user_pairings[user_id] = []
        self._save_data()
        
        logger.info(f"User registered: {username} ({user_id})")
        return user
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        """Update user profile."""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        
        # Update allowed fields
        allowed_fields = ['username', 'email', 'avatar_url', 'preferences', 
                         'interests', 'is_verified']
        for field in allowed_fields:
            if field in kwargs:
                setattr(user, field, kwargs[field])
        
        user.last_active = datetime.now()
        self._save_data()
        
        logger.debug(f"User updated: {user_id}")
        return user
    
    def generate_pairing_code(self, owner_id: str, 
                            max_uses: int = 1,
                            expires_hours: int = 24,
                            theme: CodeTheme = CodeTheme.DEFAULT,
                            is_animated: bool = True,
                            metadata: Optional[Dict] = None) -> PairingCode:
        """
        Generate a new pairing code.
        
        Args:
            owner_id: User ID of code owner
            max_uses: Maximum number of times code can be used
            expires_hours: Hours until code expires
            theme: Visual theme for the code
            is_animated: Whether to generate animated QR
            metadata: Additional metadata
        
        Returns:
            PairingCode object
        
        Raises:
            ValueError: If owner doesn't exist
        """
        if owner_id not in self.users:
            raise ValueError(f"User {owner_id} not found")
        
        # Generate unique code
        while True:
            code = ''.join([str(uuid.uuid4().int % 10) for _ in range(8)])
            if code not in self.codes:
                break
        
        # Create pairing code
        pairing_code = PairingCode(
            code=code,
            owner_id=owner_id,
            max_uses=max_uses,
            expires_at=datetime.now() + timedelta(hours=expires_hours),
            theme=theme,
            is_animated=is_animated,
            metadata=metadata or {}
        )
        
        self.codes[code] = pairing_code
        self._save_data()
        
        logger.info(f"Pairing code generated: {code} for user {owner_id}")
        return pairing_code
    
    def get_pairing_code(self, code: str) -> Optional[PairingCode]:
        """Get pairing code by value."""
        return self.codes.get(code)
    
    def use_pairing_code(self, code: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Use a pairing code to create a pairing.
        
        Args:
            code: Pairing code
            user_id: User ID of the person using the code
        
        Returns:
            Tuple of (success, message_or_pairing_id)
        """
        pairing_code = self.get_pairing_code(code)
        
        if not pairing_code:
            return False, "Invalid pairing code"
        
        if not pairing_code.is_valid:
            return False, "Pairing code has expired or been used"
        
        if pairing_code.owner_id == user_id:
            return False, "Cannot pair with yourself"
        
        # Check if users are already paired
        existing_pairing = self._find_existing_pairing(pairing_code.owner_id, user_id)
        if existing_pairing:
            return False, "Users are already paired"
        
        # Mark code as used
        if not pairing_code.use():
            return False, "Pairing code usage limit reached"
        
        # Calculate compatibility
        user1 = self.users[pairing_code.owner_id]
        user2 = self.users[user_id]
        compatibility_score = self._calculate_compatibility(user1, user2)
        shared_interests = self._find_shared_interests(user1, user2)
        
        # Create pairing
        pairing_id = str(uuid.uuid4())
        pairing = Pairing(
            pairing_id=pairing_id,
            user1_id=pairing_code.owner_id,
            user2_id=user_id,
            compatibility_score=compatibility_score,
            shared_interests=shared_interests,
            status=PairingStatus.ACTIVE
        )
        
        self.pairings[pairing_id] = pairing
        
        # Update user pairings index
        self.user_pairings[pairing_code.owner_id].append(pairing_id)
        self.user_pairings[user_id].append(pairing_id)
        
        self._save_data()
        
        logger.info(f"Pairing created: {pairing_id} between {pairing_code.owner_id} and {user_id}")
        return True, pairing_id
    
    def _find_existing_pairing(self, user1_id: str, user2_id: str) -> Optional[str]:
        """Find existing pairing between two users."""
        user1_pairings = self.user_pairings.get(user1_id, [])
        
        for pairing_id in user1_pairings:
            pairing = self.pairings[pairing_id]
            if (pairing.user1_id == user2_id or pairing.user2_id == user2_id) and pairing.is_active:
                return pairing_id
        
        return None
    
    def _calculate_compatibility(self, user1: UserProfile, user2: UserProfile) -> float:
        """Calculate compatibility score between two users."""
        score = 0.0
        
        # Interest matching (40%)
        common_interests = set(user1.interests) & set(user2.interests)
        if user1.interests:
            interest_score = len(common_interests) / len(user1.interests) * 0.4
            score += interest_score
        
        # Preference matching (30%)
        # This can be customized based on your preference structure
        pref_score = 0.15  # Base preference score
        score += pref_score
        
        # Activity level (20%)
        activity_diff = abs((user1.last_active - user2.last_active).total_seconds())
        activity_score = max(0, 1 - activity_diff / 86400) * 0.2  # 24 hours
        score += activity_score
        
        # Random factor for variety (10%)
        random_factor = hash(f"{user1.user_id}{user2.user_id}") % 100 / 1000
        score += random_factor
        
        return min(score, 1.0)
    
    def _find_shared_interests(self, user1: UserProfile, user2: UserProfile) -> List[str]:
        """Find shared interests between two users."""
        return list(set(user1.interests) & set(user2.interests))
    
    def get_user_pairings(self, user_id: str, 
                         status: Optional[PairingStatus] = None) -> List[Pairing]:
        """Get all pairings for a user."""
        if user_id not in self.user_pairings:
            return []
        
        pairings = []
        for pairing_id in self.user_pairings[user_id]:
            pairing = self.pairings.get(pairing_id)
            if pairing:
                if status is None or pairing.status == status:
                    pairings.append(pairing)
        
        return sorted(pairings, key=lambda p: p.last_interaction, reverse=True)
    
    def get_pairing(self, pairing_id: str) -> Optional[Pairing]:
        """Get pairing by ID."""
        return self.pairings.get(pairing_id)
    
    def update_pairing_status(self, pairing_id: str, 
                            status: PairingStatus) -> Optional[Pairing]:
        """Update pairing status."""
        pairing = self.pairings.get(pairing_id)
        if not pairing:
            return None
        
        pairing.status = status
        pairing.last_interaction = datetime.now()
        self._save_data()
        
        logger.info(f"Pairing {pairing_id} status updated to {status}")
        return pairing
    
    def delete_pairing(self, pairing_id: str) -> bool:
        """Delete a pairing."""
        if pairing_id not in self.pairings:
            return False
        
        pairing = self.pairings[pairing_id]
        
        # Remove from user pairings index
        for user_id in [pairing.user1_id, pairing.user2_id]:
            if user_id in self.user_pairings:
                self.user_pairings[user_id] = [
                    pid for pid in self.user_pairings[user_id] 
                    if pid != pairing_id
                ]
        
        # Remove pairing
        del self.pairings[pairing_id]
        self._save_data()
        
        logger.info(f"Pairing deleted: {pairing_id}")
        return True
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a user."""
        if user_id not in self.users:
            return {}
        
        pairings = self.get_user_pairings(user_id)
        active_pairings = [p for p in pairings if p.is_active]
        codes = [code for code in self.codes.values() if code.owner_id == user_id]
        
        return {
            "user_id": user_id,
            "total_pairings": len(pairings),
            "active_pairings": len(active_pairings),
            "codes_generated": len(codes),
            "active_codes": len([c for c in codes if c.is_valid]),
            "compatibility_avg": (
                sum(p.compatibility_score for p in active_pairings) / 
                len(active_pairings) if active_pairings else 0
            ),
            "most_common_interest": self._find_most_common_interest(user_id)
        }
    
    def _find_most_common_interest(self, user_id: str) -> Optional[str]:
        """Find user's most common interest among pairings."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        interest_counts = {}
        pairings = self.get_user_pairings(user_id)
        
        for pairing in pairings:
            other_id = pairing.user2_id if pairing.user1_id == user_id else pairing.user1_id
            other_user = self.users.get(other_id)
            if other_user:
                for interest in user.interests:
                    if interest in other_user.interests:
                        interest_counts[interest] = interest_counts.get(interest, 0) + 1
        
        return max(interest_counts.items(), key=lambda x: x[1])[0] if interest_counts else None
    
    def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired codes and pairings."""
        now = datetime.now()
        
        # Expire old codes
        expired_codes = []
        for code, pairing_code in list(self.codes.items()):
            if now > pairing_code.expires_at:
                pairing_code.is_active = False
                expired_codes.append(code)
        
        # Archive inactive pairings (older than 30 days)
        archived_pairings = []
        thirty_days_ago = now - timedelta(days=30)
        
        for pairing_id, pairing in list(self.pairings.items()):
            if (pairing.status != PairingStatus.ACTIVE and 
                pairing.last_interaction < thirty_days_ago):
                pairing.status = PairingStatus.ARCHIVED
                archived_pairings.append(pairing_id)
        
        if expired_codes or archived_pairings:
            self._save_data()
        
        return {
            "expired_codes": len(expired_codes),
            "archived_pairings": len(archived_pairings)
        }
    
    def export_data(self, filepath: str = "rahl_xmd_export.json") -> bool:
        """Export all data to JSON file."""
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "version": "1.0",
                "users": {uid: user.to_dict() for uid, user in self.users.items()},
                "codes": {code: pc.to_dict() for code, pc in self.codes.items()},
                "pairings": {pid: pairing.to_dict() for pid, pairing in self.pairings.items()}
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Data exported to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def import_data(self, filepath: str) -> bool:
        """Import data from JSON file."""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)
            
            # Clear existing data
            self.users.clear()
            self.codes.clear()
            self.pairings.clear()
            self.user_pairings.clear()
            
            # Import users
            for uid, user_data in import_data.get("users", {}).items():
                self.users[uid] = UserProfile.from_dict(user_data)
                self.user_pairings[uid] = []
            
            # Import codes
            for code, code_data in import_data.get("codes", {}).items():
                self.codes[code] = PairingCode.from_dict(code_data)
            
            # Import pairings
            for pid, pairing_data in import_data.get("pairings", {}).items():
                pairing = Pairing.from_dict(pairing_data)
                self.pairings[pid] = pairing
                
                # Update user pairings index
                for user_id in [pairing.user1_id, pairing.user2_id]:
                    if user_id not in self.user_pairings:
                        self.user_pairings[user_id] = []
                    self.user_pairings[user_id].append(pid)
            
            self._save_data()
            
            logger.info(f"Data imported from {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False
