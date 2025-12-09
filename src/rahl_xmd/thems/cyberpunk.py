"""
Cyberpunk theme for RAHL XMD pairing system.
"""

from typing import Tuple
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import random
import math

from .base_theme import BaseTheme
from ..core.animation_engine import AnimationType


class CyberpunkTheme(BaseTheme):
    """Cyberpunk theme with futuristic grid and glitch effects."""
    
    def __init__(self):
        super().__init__()
        self.name = "cyberpunk"
        self.description = "Futuristic cyberpunk with grid and glitch effects"
        self.animation_type = AnimationType.GLITCH
        self.is_animated = True
        
        # Cyberpunk color palette
        self.colors = {
            "primary": (0, 255, 157),    # Green cyan
            "secondary": (255, 42, 109),  # Pink
            "accent": (0, 191, 255),      # Blue
            "background": (20, 10, 40),   # Dark purple
            "grid": (0, 200, 255),        # Bright blue grid
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
        """Apply cyberpunk effect to image."""
        img_array = np.array(image)
        
        # Split color channels for glitch effect
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        
        # Apply channel shifts
        shift_amount = random.randint(1, 3)
        r_shifted = np.roll(r, shift_amount, axis=1)
        b_shifted = np.roll(b, -shift_amount, axis=0)
        
        # Create glitched image
        glitched_array = np.stack([r_shifted, g, b_shifted], axis=2)
        
        # Apply color filter
        hsv_img = Image.fromarray(glitched_array).convert('HSV')
        hsv_array = np.array(hsv_img)
        
        # Boost saturation
        hsv_array[:, :, 1] = np.clip(hsv_array[:, :, 1] * 2, 0, 255)
        
        # Shift hue toward cyan/pink
        hue_shift = 90
        hsv_array[:, :, 0] = (hsv_array[:, :, 0] + hue_shift) % 255
        
        # Convert back
        result = Image.fromarray(hsv_array, 'HSV').convert('RGB')
        
        return result
    
    def generate_background(self, width: int, height: int) -> Image.Image:
        """Generate cyberpunk grid background."""
        # Create base background with gradient
        background = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(background)
        
        # Draw vertical gradient
        for y in range(height):
            # Calculate gradient color
            ratio = y / height
            r = int(self.background_color[0] * (1 - ratio) + 0 * ratio)
            g = int(self.background_color[1] * (1 - ratio) + 20 * ratio)
            b = int(self.background_color[2] * (1 - ratio) + 40 * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Draw hexagonal grid
        hex_size = 40
        hex_width = hex_size * 2
        hex_height = int(hex_size * math.sqrt(3))
        
        for x in range(-hex_width, width + hex_width, hex_width):
            for y in range(-hex_height, height + hex_height, hex_height):
                # Calculate hexagon points
                center_x = x + hex_width // 2
                center_y = y + hex_height // 2
                
                points = []
                for i in range(6):
                    angle = math.pi / 3 * i
                    px = center_x + hex_size * math.cos(angle)
                    py = center_y + hex_size * math.sin(angle)
                    points.append((px, py))
                
                # Draw hexagon with glow
                for i in range(3, 0, -1):
                    alpha = int(30 / i)
                    glow_color = (*self.colors["grid"], alpha)
                    
                    # Scale points for glow
                    glow_points = []
                    scale = 1 + i * 0.1
                    for px, py in points:
                        gx = center_x + (px - center_x) * scale
                        gy = center_y + (py - center_y) * scale
                        glow_points.append((gx, gy))
                    
                    draw.polygon(glow_points, outline=glow_color, width=1)
        
        # Add scan lines
        for y in range(0, height, 4):
            alpha = random.randint(5, 15)
            draw.line([(0, y), (width, y)], 
                     fill=(0, 255, 255, alpha), width=1)
        
        # Add random binary code rain
        binary_count = width // 10
        for _ in range(binary_count):
            x = random.randint(0, width - 1)
            y_start = random.randint(-100, 0)
            length = random.randint(5, 15)
            speed = random.uniform(2, 5)
            
            # Draw falling binary
            for i in range(length):
                char_y = int(y_start + i * 10)
                if 0 <= char_y < height:
                    char = random.choice(['0', '1'])
                    color = self.primary_color if random.random() > 0.7 else self.secondary_color
                    alpha = int(255 * (1 - i / length))
                    
                    try:
                        draw.text((x, char_y), char, 
                                 fill=(*color, alpha), 
                                 font=ImageFont.load_default())
                    except:
                        pass
        
        return background
    
    def create_data_matrix(self, text: str) -> Image.Image:
        """Create data matrix visualization."""
        # Convert text to binary
        binary_text = ''.join(format(ord(c), '08b') for c in text)
        
        # Calculate matrix size
        matrix_size = int(math.sqrt(len(binary_text))) + 1
        
        # Create matrix image
        cell_size = 10
        img_size = matrix_size * cell_size
        
        matrix_img = Image.new('RGB', (img_size, img_size), self.background_color)
        draw = ImageDraw.Draw(matrix_img)
        
        # Draw matrix cells
        for i in range(matrix_size):
            for j in range(matrix_size):
                idx = i * matrix_size + j
                if idx < len(binary_text):
                    bit = binary_text[idx]
                    
                    if bit == '1':
                        # Active cell
                        x1 = j * cell_size
                        y1 = i * cell_size
                        x2 = x1 + cell_size
                        y2 = y1 + cell_size
                        
                        # Draw cell with glow
                        draw.rectangle([x1, y1, x2, y2], 
                                      fill=self.primary_color)
                        
                        # Add inner highlight
                        highlight_size = cell_size // 3
                        highlight_x = x1 + (cell_size - highlight_size) // 2
                        highlight_y = y1 + (cell_size - highlight_size) // 2
                        draw.rectangle([highlight_x, highlight_y, 
                                       highlight_x + highlight_size, 
                                       highlight_y + highlight_size],
                                      fill=self.secondary_color)
        
        return matrix_img
