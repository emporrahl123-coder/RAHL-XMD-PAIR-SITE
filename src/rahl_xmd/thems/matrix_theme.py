"""
Matrix theme for RAHL XMD pairing system.
"""

from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
import math

from .base_theme import BaseTheme
from ..core.animation_engine import AnimationType


class MatrixTheme(BaseTheme):
    """Matrix theme with green code rain effect."""
    
    def __init__(self):
        super().__init__()
        self.name = "matrix"
        self.description = "Green code rain from The Matrix"
        self.animation_type = AnimationType.RAIN
        self.is_animated = True
        
        # Matrix color palette
        self.colors = {
            "primary": (0, 255, 65),     # Bright green
            "secondary": (0, 180, 45),   # Medium green
            "accent": (0, 100, 25),      # Dark green
            "background": (0, 0, 0),     # Black
            "text": (0, 255, 0),         # Green text
        }
        
        # Character set for code rain
        self.matrix_chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
    
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
        """Apply matrix effect to image."""
        # Convert to green scale
        img_array = np.array(image)
        
        # Calculate luminance
        luminance = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
        
        # Map luminance to green colors
        green_array = np.zeros_like(img_array)
        
        # Bright areas become bright green
        mask_bright = luminance > 200
        green_array[mask_bright] = self.primary_color
        
        # Medium areas become medium green
        mask_medium = (luminance > 100) & (luminance <= 200)
        green_array[mask_medium] = self.secondary_color
        
        # Dark areas become dark green
        mask_dark = luminance <= 100
        green_array[mask_dark] = self.colors["accent"]
        
        # Add some noise for matrix effect
        noise = np.random.randint(-20, 20, green_array.shape[:2])
        for i in range(3):
            green_array[:, :, i] = np.clip(green_array[:, :, i] + noise, 0, 255)
        
        return Image.fromarray(green_array.astype(np.uint8))
    
    def generate_background(self, width: int, height: int) -> Image.Image:
        """Generate matrix code rain background."""
        # Create black background
        background = Image.new('RGB', (width, height), self.background_color)
        
        # We'll create the rain in the animation
        # For static background, just add some random characters
        draw = ImageDraw.Draw(background)
        
        # Try to load a monospace font
        try:
            font = ImageFont.truetype("consola.ttf", 14)
        except:
            try:
                font = ImageFont.truetype("courier.ttf", 14)
            except:
                font = ImageFont.load_default()
        
        # Add some random characters
        char_count = (width * height) // 1000
        for _ in range(char_count):
            x = random.randint(0, width - 20)
            y = random.randint(0, height - 20)
            char = random.choice(self.matrix_chars)
            
            # Random brightness
            brightness = random.randint(50, 255)
            color = (0, brightness, 0)
            
            draw.text((x, y), char, fill=color, font=font)
        
        # Add scan lines
        for y in range(0, height, 3):
            alpha = random.randint(5, 20)
            draw.line([(0, y), (width, y)], 
                     fill=(0, 100, 0, alpha), width=1)
        
        return background
    
    def create_code_rain_frame(self, 
                              width: int, 
                              height: int,
                              frame_num: int,
                              drops: list) -> Tuple[Image.Image, list]:
        """Create a single frame of code rain animation."""
        # Create background
        frame = Image.new('RGB', (width, height), self.background_color)
        draw = ImageDraw.Draw(frame)
        
        # Try to load font
        try:
            font = ImageFont.truetype("consola.ttf", 16)
        except:
            try:
                font = ImageFont.truetype("courier.ttf", 16)
            except:
                font = ImageFont.load_default()
        
        # Update drops
        for drop in drops:
            # Update position
            drop['y'] += drop['speed']
            drop['age'] += 1
            
            # Reset if off screen
            if drop['y'] > height + drop['length'] * 20:
                drop['y'] = random.randint(-200, -20)
                drop['x'] = random.randint(0, width - 1)
                drop['speed'] = random.uniform(2, 6)
                drop['length'] = random.randint(5, 15)
                drop['age'] = 0
            
            # Draw drop
            for i in range(drop['length']):
                y_pos = int(drop['y']) - i * 20
                
                if 0 <= y_pos < height:
                    # Calculate brightness (head is brightest)
                    brightness = 255 * (1 - i / drop['length'])
                    
                    # Head character (bright)
                    if i == 0:
                        char = random.choice(['@', '#', '$', '%', '&'])
                        color = (0, int(brightness), 0)
                    # Body characters
                    else:
                        char = random.choice(self.matrix_chars)
                        color = (0, int(brightness * 0.7), 0)
                    
                    # Draw character
                    draw.text((drop['x'], y_pos), char, 
                             fill=color, font=font)
        
        return frame, drops
    
    def initialize_code_rain(self, width: int, height: int) -> list:
        """Initialize code rain drops."""
        drops = []
        drop_count = width // 15
        
        for _ in range(drop_count):
            drops.append({
                'x': random.randint(0, width - 1),
                'y': random.randint(-200, -20),
                'speed': random.uniform(2, 6),
                'length': random.randint(5, 15),
                'age': 0
            })
        
        return drops
    
    def create_matrix_text(self, text: str, font_size: int = 36) -> Image.Image:
        """Create matrix-style text."""
        from PIL import ImageFont
        
        try:
            font = ImageFont.truetype("consola.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("courier.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Calculate text size
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Create canvas
        canvas = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # Draw text with vertical streaks
        for x_offset in range(-2, 3):
            for y_offset in range(-2, 3):
                if x_offset == 0 and y_offset == 0:
                    continue
                
                alpha = 30
                color = (0, 100, 0, alpha)
                draw.text((x_offset, y_offset), text, 
                         fill=color, font=font)
        
        # Draw main text
        draw.text((0, 0), text, fill=self.primary_color, font=font)
        
        # Add flickering effect
        flicker_mask = Image.new('L', (text_width, text_height), 255)
        flicker_draw = ImageDraw.Draw(flicker_mask)
        
        # Randomly darken some pixels
        for _ in range(text_width * text_height // 10):
            x = random.randint(0, text_width - 1)
            y = random.randint(0, text_height - 1)
            flicker_draw.point((x, y), fill=random.randint(150, 255))
        
        canvas.putalpha(flicker_mask)
        
        return canvas
