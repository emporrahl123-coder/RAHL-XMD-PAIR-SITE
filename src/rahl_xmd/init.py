"""
RAHL XMD Pairing System
An advanced pairing system with animated QR codes and multi-platform support.
"""

__version__ = "1.0.0"
__author__ = "RAHL XMD Team"
__license__ = "MIT"

# Core exports
from .core.pairing_system import PairingSystem, PairingCode, PairingStatus
from .core.code_generator import CodeGenerator
from .core.qr_generator import QRGenerator
from .core.animation_engine import AnimationEngine

# Theme exports
from .themes.base_theme import BaseTheme
from .themes.neon_theme import NeonTheme
from .themes.cyberpunk_theme import CyberpunkTheme
from .themes.matrix_theme import MatrixTheme
from .themes.aurora_theme import AuroraTheme
from .themes.hologram_theme import HologramTheme

# Enums
from .core.pairing_system import CodeTheme

# Bot exports
from .bot.discord_bot import RAHLDiscordBot
from .bot.telegram_bot import RAHLTelegramBot
from .bot.web_bot import RAHLWebBot

# API exports
from .api.fastapi_app import app
from .api.routes import router

__all__ = [
    "PairingSystem",
    "PairingCode",
    "PairingStatus",
    "CodeGenerator",
    "QRGenerator",
    "AnimationEngine",
    "BaseTheme",
    "NeonTheme",
    "CyberpunkTheme",
    "MatrixTheme",
    "AuroraTheme",
    "HologramTheme",
    "CodeTheme",
    "RAHLDiscordBot",
    "RAHLTelegramBot",
    "RAHLWebBot",
    "app",
    "router",
]
