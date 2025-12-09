"""
Base theme class for RAHL XMD pairing system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List
from PIL import Image, ImageDraw
import numpy as np

from ..core.animation_engine import AnimationType
from ..core.pairing_system import CodeTheme


class BaseTheme(ABC):
    """Abstract base class for all themes."""
    
    def __init__(self):
        self.name = "base"
        self.description = "Base theme"
        self.colors: Dict[str, Tuple[int, int, int]] = {}
        self.animation_type = AnimationType.FADE
        self.is_animated = True
    
    @property
    @abstractmethod
    def primary_color(self) -> Tuple[int, int, int]:
        """Get primary color for this theme."""
        pass
    
    @property
    @abstractmethod
    def secondary_color(self) -> Tuple[int, int, int]:
        """Get secondary color for this theme."""
        pass
    
    @property
    @abstractmethod
    def background_color(self) -> Tuple[int, int, int]:
        """Get background color for this theme."""
        pass
    
    @abstractmethod
    def apply_theme(self, image: Image.Image) -> Image.Image:
        """
        Apply theme to an image.
        
        Args:
            image: PIL Image to theme
        
        Returns:
            Themed image
        """
        pass
    
    @abstractmethod
    def generate_background(self, width: int, height: int) -> Image.Image:
        """
        Generate themed background.
        
        Args:
            width: Background width
            height: Background height
        
        Returns:
            Themed background image
        """
        pass
    
    def generate_card(self, 
                     qr_code: Image.Image,
                     pairing_code: str,
                     user_name: str,
                     expiry_time: str) -> Image.Image:
        """
        Generate themed pairing card with QR code.
        
        Args:
            qr_code: QR code image
            pairing_code: Pairing code string
            user_name: User's name
            expiry_time: Expiry time string
        
        Returns:
            Complete pairing card image
        """
        # Create canvas
        card_width = max(600, qr_code.width + 200)
        card_height = max(400, qr_code.height + 200)
        
        # Create background
        background = self.generate_background(card_width, card_height)
        
        # Create overlay with content
        overlay = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Add QR code
        qr_x = (card_width - qr_code.width) // 2
        qr_y = 50
        overlay.paste(qr_code, (qr_x, qr_y))
        
        # Add pairing code
        code_font_size = 40
        try:
            code_font = ImageFont.truetype("arial.ttf", code_font_size)
        except:
            code_font = ImageFont.load_default()
        
        code_bbox = draw.textbbox((0, 0), pairing_code, font=code_font)
        code_width = code_bbox[2] - code_bbox[0]
        code_x = (card_width - code_width) // 2
        code_y = qr_y + qr_code.height + 20
        
        draw.text((code_x, code_y), pairing_code, 
                 fill=self.primary_color, font=code_font)
        
        # Add user name
        name_font_size = 24
        try:
            name_font = ImageFont.truetype("arial.ttf", name_font_size)
        except:
            name_font = ImageFont.load_default()
        
        name_text = f"Shared by: {user_name}"
        name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (card_width - name_width) // 2
        name_y = code_y + code_font_size + 10
        
        draw.text((name_x, name_y), name_text, 
                 fill=self.secondary_color, font=name_font)
        
        # Add expiry time
        expiry_text = f"Expires: {expiry_time}"
        expiry_bbox = draw.textbbox((0, 0), expiry_text, font=name_font)
        expiry_width = expiry_bbox[2] - expiry_bbox[0]
        expiry_x = (card_width - expiry_width) // 2
        expiry_y = name_y + name_font_size + 10
        
        draw.text((expiry_x, expiry_y), expiry_text, 
                 fill=self.secondary_color, font=name_font)
        
        # Add footer
        footer_text = "RAHL XMD Pairing System"
        footer_font_size = 16
        try:
            footer_font = ImageFont.truetype("arial.ttf", footer_font_size)
        except:
            footer_font = ImageFont.load_default()
        
        footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (card_width - footer_width) // 2
        footer_y = card_height - 40
        
        draw.text((footer_x, footer_y), footer_text, 
                 fill=self.secondary_color, font=footer_font)
        
        # Combine background and overlay
        result = Image.alpha_composite(background.convert('RGBA'), overlay)
        return result.convert('RGB')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "colors": self.colors,
            "animation_type": self.animation_type.value,
            "is_animated": self.is_animated
        }
