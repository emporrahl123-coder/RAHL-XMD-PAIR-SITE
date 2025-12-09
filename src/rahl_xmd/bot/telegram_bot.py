"""
Telegram bot integration for RAHL XMD pairing system.
"""

import asyncio
from typing import Optional, Dict, Any
import json
from datetime import datetime
import io
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

from ..core.pairing_system import PairingSystem, CodeTheme, PairingStatus
from ..core.qr_generator import QRGenerator
from ..core.animation_engine import AnimationEngine
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class RAHLTelegramBot:
    """Telegram bot for RAHL XMD pairing system."""
    
    def __init__(self, 
                 token: str,
                 data_dir: str = "telegram_data"):
        """
        Initialize Telegram bot.
        
        Args:
            token: Telegram bot token
            data_dir: Data directory for Telegram-specific data
        """
        self.token = token
        self.pairing_system = PairingSystem(data_dir=data_dir)
        self.qr_generator = QRGenerator()
        self.animation_engine = AnimationEngine(qr_generator=self.qr_generator)
        
        # User mapping (Telegram ID -> RAHL XMD user ID)
        self.user_mapping: Dict[int, str] = {}
        
        # Load user mapping
        self._load_user_mapping()
        
        # Create application
        self.application = Application.builder().token(token).build()
        
        # Register handlers
        self._register_handlers()
    
    def _load_user_mapping(self) -> None:
        """Load Telegram user mapping from file."""
        try:
            mapping_file = self.pairing_system.data_dir / "telegram_users.json"
            if mapping_file.exists():
                with open(mapping_file, 'r') as f:
                    self.user_mapping = json.load(f)
                    # Convert keys back to integers
                    self.user_mapping = {int(k): v for k, v in self.user_mapping.items()}
                logger.info(f"Loaded {len(self.user_mapping)} user mappings")
        except Exception as e:
            logger.error(f"Failed to load user mapping: {e}")
    
    def _save_user_mapping(self) -> None:
        """Save Telegram user mapping to file."""
        try:
            mapping_file = self.pairing_system.data_dir / "telegram_users.json"
            with open(mapping_file, 'w') as f:
                json.dump(self.user_mapping, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user mapping: {e}")
    
    def _get_or_create_user_id(self, telegram_user) -> str:
        """
        Get or
