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
                if len(points) > 1:
                    # Create color for this aurora segment
                    hue = (layer * 60 + wave * 40) % 360
                    saturation = 80
                    brightness = 60
                    
                    # Convert HSV to RGB
                    color = self._hsv_to_rgb(hue, saturation, brightness)
                    
                    # Draw thick line with gradient opacity
                    for width_mult in range(5, 0, -1):
                        line_width = width_mult * 2
                        alpha = int(50 / width_mult)
                        
                        # Draw line segment
                        for i in range(len(points) - 1):
                            x1, y1 = points[i]
                            x2, y2 = points[i + 1]
                            
                            aurora_draw.line([(x1, y1), (x2, y2)], 
                                           fill=(*color, alpha), 
                                           width=line_width)
            
            # Apply blur for aurora glow
            aurora_layer = aurora_layer.filter(ImageFilter.GaussianBlur(radius=10))
            
            # Composite onto background
            background = Image.alpha_composite(
                background.convert('RGBA'), 
                aurora_layer
            ).convert('RGB')
        
        # Add stars
        star_count = (width * height) // 1000
        star_draw = ImageDraw.Draw(background)
        
        for _ in range(star_count):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            # Star brightness
            brightness = random.randint(100, 255)
            size = random.randint(1, 3)
            
            # Draw star
            for offset in range(size, 0, -1):
                alpha = int(brightness * (offset / size))
                star_color = (255, 255, 255, alpha)
                
                left = x - offset
                top = y - offset
                right = x + offset
                bottom = y + offset
                
                star_draw.ellipse([left, top, right, bottom], 
                                 fill=star_color, outline=None)
        
        return background
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB."""
        h = h % 360
        s = max(0, min(100, s)) / 100
        v = max(0, min(100, v)) / 100
        
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        
        return (r, g, b)
    
    def create_color_shift_text(self, text: str, font_size: int = 48) -> Image.Image:
        """Create color shifting text."""
        from PIL import ImageFont
        
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
        
        # Create canvas
        canvas = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # Draw text with color gradient
        for x in range(text_width):
            # Calculate color based on position
            hue = (x / text_width) * 360
            color = self._hsv_to_rgb(hue, 80, 100)
            
            # Draw vertical slice
            slice_img = Image.new('RGBA', (1, text_height), (0, 0, 0, 0))
            slice_draw = ImageDraw.Draw(slice_img)
            slice_draw.text((0, 0), text, fill=(*color, 255), font=font)
            
            # Extract slice and apply to canvas
            canvas_slice = slice_img.crop((x, 0, x + 1, text_height))
            canvas.paste(canvas_slice, (x, 0), canvas_slice)
        
        return canvas
