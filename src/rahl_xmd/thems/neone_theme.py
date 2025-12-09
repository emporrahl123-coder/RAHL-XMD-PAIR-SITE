"""
Neon theme for RAHL XMD pairing system.
"""

from typing import Tuple, List
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import random
import math

from .base_theme import BaseTheme
from ..core.animation_engine import AnimationType


class NeonTheme(BaseTheme):
    """Neon theme with vibrant glowing effects."""
    
    def __init__(self):
        super().__init__()
        self.name = "neon"
        self.description = "Vibrant neon colors with glowing effects"
        self.animation_type = AnimationType.PULSE
        self.is_animated = True
        
        # Neon color palette
        self.colors = {
            "primary": (0, 255, 255),    # Cyan
            "secondary": (255, 0, 255),   # Magenta
            "accent": (255, 255, 0),      # Yellow
            "background": (10, 10, 20),   # Dark blue
            "glow": (200, 200, 255),      # Light purple glow
        }
    
    @property
    def primary_color(self) -> Tuple[int, int, int]:
        return self.colors["primary"]
    
    @property
    def secondary_color(self) -> Tuple[int, int, int]:
        return self.colors["secondary"]
    
    @property
    def background_color(self) -> Tuple[int, int, int]:
        return self.colors["background"]
    
    def apply_theme(self, image: Image.Image) -> Image.Image:
        """Apply neon effect to image."""
        img_array = np.array(image)
        
        # Convert to HSV for better color manipulation
        hsv_img = image.convert('HSV')
        hsv_array = np.array(hsv_img)
        
        # Enhance saturation
        hsv_array[:, :, 1] = np.clip(hsv_array[:, :, 1] * 1.5, 0, 255)
        
        # Shift hue toward neon colors
        hue_shift = 180  # Shift toward cyan/magenta
        hsv_array[:, :, 0] = (hsv_array[:, :, 0] + hue_shift) % 255
        
        # Increase value (brightness)
        hsv_array[:, :, 2] = np.clip(hsv_array[:, :, 2] * 1.3, 0, 255)
        
        # Convert back to RGB
        enhanced_img = Image.fromarray(hsv_array, 'HSV').convert('RGB')
        
        # Apply glow effect
        glow = enhanced_img.filter(ImageFilter.GaussianBlur(radius=2))
        
        # Blend original with glow
        result = Image.blend(enhanced_img, glow, 0.3)
        
        return result
    
    def generate_background(self, width: int, height: int) -> Image.Image:
        """Generate neon grid background."""
        # Create base background
        background = Image.new('RGB', (width, height), self.background_color)
        draw = ImageDraw.Draw(background)
        
        # Draw neon grid
        grid_size = 50
        grid_color = (30, 30, 60, 100)
        glow_color = (100, 100, 200, 50)
        
        # Vertical lines
        for x in range(0, width, grid_size):
            # Base line
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
            
            # Glow effect
            for offset in range(1, 4):
                alpha = int(50 / offset)
                glow_line = (grid_color[0] + offset * 20,
                           grid_color[1] + offset * 20,
                           grid_color[2] + offset * 30,
                           alpha)
                draw.line([(x + offset, 0), (x + offset, height)], 
                         fill=glow_line, width=1)
                draw.line([(x - offset, 0), (x - offset, height)], 
                         fill=glow_line, width=1)
        
        # Horizontal lines
        for y in range(0, height, grid_size):
            # Base line
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
            
            # Glow effect
            for offset in range(1, 4):
                alpha = int(50 / offset)
                glow_line = (grid_color[0] + offset * 20,
                           grid_color[1] + offset * 20,
                           grid_color[2] + offset * 30,
                           alpha)
                draw.line([(0, y + offset), (width, y + offset)], 
                         fill=glow_line, width=1)
                draw.line([(0, y - offset), (width, y - offset)], 
                         fill=glow_line, width=1)
        
        # Add random neon dots
        dot_count = (width * height) // 5000
        for _ in range(dot_count):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            # Random neon color
            colors = [self.primary_color, self.secondary_color, self.colors["accent"]]
            color = random.choice(colors)
            
            # Draw dot with glow
            radius = random.randint(2, 5)
            for r in range(radius, 0, -1):
                alpha = int(200 * (r / radius))
                glow_color = (*color, alpha)
                
                left = x - r
                top = y - r
                right = x + r
                bottom = y + r
                
                draw.ellipse([left, top, right, bottom], 
                            fill=glow_color, outline=None)
        
        # Add scan lines
        scan_spacing = 4
        for y in range(0, height, scan_spacing):
            alpha = random.randint(10, 30)
            draw.line([(0, y), (width, y)], 
                     fill=(0, 255, 255, alpha), width=1)
        
        return background
    
    def create_glow_effect(self, text: str, font_size: int = 48) -> Image.Image:
        """Create glowing text effect."""
        from PIL import ImageFont
        
        # Create text image
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text size
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Create canvas with padding for glow
        padding = 20
        canvas_width = text_width + padding * 2
        canvas_height = text_height + padding * 2
        
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # Draw glow layers
        glow_layers = 10
        for i in range(glow_layers, 0, -1):
            alpha = int(50 * (i / glow_layers))
            glow_color = (*self.primary_color, alpha)
            
            # Draw text with offset for glow
            offset = glow_layers - i
            x = padding + offset
            y = padding + offset
            
            draw.text((x, y), text, fill=glow_color, font=font)
        
        # Draw main text
        draw.text((padding, padding), text, 
                 fill=self.primary_color, font=font)
        
        return canvas
