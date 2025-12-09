"""
Aurora theme for RAHL XMD pairing system.
"""

from typing import Tuple
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import random
import math

from .base_theme import BaseTheme
from ..core.animation_engine import AnimationType


class AuroraTheme(BaseTheme):
    """Aurora theme with northern lights color shifting."""
    
    def __init__(self):
        super().__init__()
        self.name = "aurora"
        self.description = "Northern lights with color shifting effects"
        self.animation_type = AnimationType.WAVE
        self.is_animated = True
        
        # Aurora color palette
        self.colors = {
            "primary": (255, 95, 162),   # Pink
            "secondary": (95, 255, 242), # Cyan
            "accent": (162, 95, 255),    # Purple
            "background": (10, 20, 40),  # Dark blue
            "aurora": (0, 255, 200),     # Teal
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
        """Apply aurora color shifting effect to image."""
        img_array = np.array(image)
        
        # Create color shift based on pixel position
        height, width, _ = img_array.shape
        
        for y in range(height):
            for x in range(width):
                # Calculate phase based on position
                x_phase = x / width * 2 * math.pi
                y_phase = y / height * 2 * math.pi
                
                # Create color shift
                r_shift = math.sin(x_phase + y_phase) * 50
                g_shift = math.cos(x_phase) * 50
                b_shift = math.sin(y_phase) * 50
                
                # Apply shift
                img_array[y, x, 0] = np.clip(img_array[y, x, 0] + r_shift, 0, 255)
                img_array[y, x, 1] = np.clip(img_array[y, x, 1] + g_shift, 0, 255)
                img_array[y, x, 2] = np.clip(img_array[y, x, 2] + b_shift, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def generate_background(self, width: int, height: int) -> Image.Image:
        """Generate aurora borealis background."""
        # Create gradient background
        background = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(background)
        
        # Draw vertical gradient from dark blue to purple
        for y in range(height):
            ratio = y / height
            
            # Gradient from dark blue to purple
            r = int(self.background_color[0] * (1 - ratio) + 40 * ratio)
            g = int(self.background_color[1] * (1 - ratio) + 20 * ratio)
            b = int(self.background_color[2] * (1 - ratio) + 60 * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Create aurora layers
        aurora_layers = 5
        for layer in range(aurora_layers):
            # Create aurora layer
            aurora_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            aurora_draw = ImageDraw.Draw(aurora_layer)
            
            # Layer properties
            layer_height = height // 3
            layer_y = height // 2 + (layer - aurora_layers // 2) * 30
            
            # Create wavy aurora
            wave_count = 5
            for wave in range(wave_count):
                wave_x = width * wave / wave_count
                wave_width = width / wave_count
                
                # Draw wavy line
                points = []
                for i in range(int(wave_width)):
                    x = wave_x + i
                    # Sine wave for aurora shape
                    y_offset = math.sin(x / 50 + layer * 0.5) * 30
                    y_offset += math.cos(x / 30) * 20
                    y = layer_y + y_offset
                    
                    # Add some randomness
                    y += random.randint(-5, 5)
                    
                    points.append((x, y))
                
                # Draw smooth curve through points
                if len(p
