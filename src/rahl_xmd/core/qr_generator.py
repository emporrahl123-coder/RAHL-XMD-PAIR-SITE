"""
QR code generation for RAHL XMD pairing system.
"""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    RoundedModuleDrawer, 
    SquareModuleDrawer,
    CircleModuleDrawer,
    GappedSquareModuleDrawer
)
from qrcode.image.styles.colormasks import (
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    SolidFillColorMask
)
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, List, Dict, Any
import base64
from io import BytesIO
import numpy as np

from .pairing_system import PairingCode, CodeTheme


class QRGenerator:
    """Generates QR codes for pairing codes."""
    
    # Theme color configurations
    THEME_COLORS = {
        CodeTheme.DEFAULT: {
            "fill": (41, 128, 185),  # Blue
            "back": (255, 255, 255),  # White
            "gradient": "radial",
            "drawer": "square"
        },
        CodeTheme.NEON: {
            "fill": (0, 255, 255),    # Cyan
            "back": (10, 10, 20),     # Dark blue
            "gradient": "square",
            "drawer": "rounded"
        },
        CodeTheme.CYBERPUNK: {
            "fill": (0, 255, 157),    # Green cyan
            "back": (20, 10, 40),     # Dark purple
            "gradient": "radial",
            "drawer": "square"
        },
        CodeTheme.MATRIX: {
            "fill": (0, 255, 65),     # Green
            "back": (0, 0, 0),        # Black
            "gradient": "solid",
            "drawer": "square"
        },
        CodeTheme.AURORA: {
            "fill": (255, 95, 162),   # Pink
            "back": (10, 20, 40),     # Dark blue
            "gradient": "radial",
            "drawer": "circle"
        },
        CodeTheme.HOLOGRAM: {
            "fill": (200, 200, 255),  # Light purple
            "back": (30, 30, 50),     # Dark blue
            "gradient": "square",
            "drawer": "gapped"
        }
    }
    
    def __init__(self, 
                 size: int = 400,
                 border: int = 4,
                 error_correction: str = "H",
                 include_logo: bool = True,
                 logo_path: Optional[str] = None):
        """
        Initialize QR generator.
        
        Args:
            size: QR code size in pixels
            border: QR border size
            error_correction: Error correction level (L/M/Q/H)
            include_logo: Whether to include logo
            logo_path: Path to custom logo
        """
        self.size = size
        self.border = border
        self.error_correction = getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction}")
        self.include_logo = include_logo
        self.logo_path = logo_path
        
        # Load default logo if available
        self.logo = None
        if self.include_logo:
            self.logo = self._load_logo(logo_path)
    
    def _load_logo(self, logo_path: Optional[str] = None) -> Optional[Image.Image]:
        """Load logo image."""
        if logo_path:
            try:
                return Image.open(logo_path).convert("RGBA")
            except:
                pass
        
        # Create default RAHL XMD logo
        return self._create_default_logo()
    
    def _create_default_logo(self) -> Image.Image:
        """Create default RAHL XMD logo."""
        logo_size = 80
        logo = Image.new('RGBA', (logo_size, logo_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(logo)
        
        # Draw circle
        center = logo_size // 2
        radius = logo_size // 3
        
        # Outer circle
        draw.ellipse([center - radius, center - radius, 
                     center + radius, center + radius], 
                    outline=(255, 255, 255, 200), width=3)
        
        # Inner circle
        inner_radius = radius // 2
        draw.ellipse([center - inner_radius, center - inner_radius,
                     center + inner_radius, center + inner_radius],
                    outline=(100, 200, 255, 150), width=2)
        
        # Draw XMD letters (simplified)
        # X
        offset = radius // 3
        draw.line([center - offset, center - offset,
                  center + offset, center + offset], 
                 fill=(255, 100, 100, 255), width=2)
        draw.line([center + offset, center - offset,
                  center - offset, center + offset], 
                 fill=(255, 100, 100, 255), width=2)
        
        return logo
    
    def _get_theme_config(self, theme: CodeTheme) -> Dict[str, Any]:
        """Get configuration for a theme."""
        return self.THEME_COLORS.get(theme, self.THEME_COLORS[CodeTheme.DEFAULT])
    
    def _get_module_drawer(self, drawer_type: str):
        """Get module drawer based on type."""
        drawers = {
            "square": SquareModuleDrawer(),
            "rounded": RoundedModuleDrawer(),
            "circle": CircleModuleDrawer(),
            "gapped": GappedSquareModuleDrawer()
        }
        return drawers.get(drawer_type, SquareModuleDrawer())
    
    def _get_color_mask(self, fill_color: Tuple[int, int, int], 
                       back_color: Tuple[int, int, int],
                       gradient_type: str):
        """Get color mask based on gradient type."""
        if gradient_type == "radial":
            return RadialGradiantColorMask(back_color=back_color, 
                                          center_color=fill_color,
                                          edge_color=back_color)
        elif gradient_type == "square":
            return SquareGradiantColorMask(back_color=back_color,
                                          center_color=fill_color,
                                          edge_color=back_color)
        else:
            return SolidFillColorMask(back_color=back_color, 
                                     front_color=fill_color)
    
    def generate_qr_data(self, pairing_code: PairingCode) -> str:
        """
        Generate QR code data string.
        
        Args:
            pairing_code: PairingCode object
        
        Returns:
            Data string for QR code
        """
        return f"RAHLXMD:PAIR:{pairing_code.code}:{pairing_code.owner_id}"
    
    def generate_qr_code(self, 
                        pairing_code: PairingCode,
                        size: Optional[int] = None,
                        add_logo: Optional[bool] = None) -> Image.Image:
        """
        Generate QR code image.
        
        Args:
            pairing_code: PairingCode object
            size: Output size (overrides default)
            add_logo: Whether to add logo (overrides default)
        
        Returns:
            PIL Image object
        """
        # Get theme configuration
        theme_config = self._get_theme_config(pairing_code.theme)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=self.error_correction,
            box_size=10,
            border=self.border,
        )
        
        # Add data
        data = self.generate_qr_data(pairing_code)
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create styled image
        img = qr.make_image(
            image_factory=StyledPilImage,
            color_mask=self._get_color_mask(
                fill_color=theme_config["fill"],
                back_color=theme_config["back"],
                gradient_type=theme_config["gradient"]
            ),
            module_drawer=self._get_module_drawer(theme_config["drawer"]),
            embeded_image=self.logo if (add_logo or self.include_logo) else None
        )
        
        # Resize if needed
        output_size = size or self.size
        if img.size[0] != output_size:
            img = img.resize((output_size, output_size), Image.Resampling.LANCZOS)
        
        return img.convert('RGB')
    
    def generate_qr_with_overlay(self,
                                pairing_code: PairingCode,
                                text: Optional[str] = None,
                                size: Optional[int] = None) -> Image.Image:
        """
        Generate QR code with text overlay.
        
        Args:
            pairing_code: PairingCode object
            text: Text to overlay
            size: Output size
        
        Returns:
            PIL Image with overlay
        """
        # Generate base QR
        qr_img = self.generate_qr_code(pairing_code, size=size)
        
        if not text:
            return qr_img
        
        # Create overlay
        overlay = Image.new('RGBA', qr_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to load font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw text background
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        padding = 10
        bg_width = text_width + padding * 2
        bg_height = text_height + padding * 2
        
        # Position at bottom
        bg_x = (qr_img.width - bg_width) // 2
        bg_y = qr_img.height - bg_height - 20
        
        # Draw rounded rectangle background
        draw.rounded_rectangle(
            [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height],
            radius=10,
            fill=(0, 0, 0, 180)
        )
        
        # Draw text
        text_x = bg_x + padding
        text_y = bg_y + padding
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        
        # Combine with QR
        qr_img = qr_img.convert('RGBA')
        result = Image.alpha_composite(qr_img, overlay)
        
        return result.convert('RGB')
    
    def save_qr_code(self, 
                    pairing_code: PairingCode,
                    filepath: str,
                    format: str = "PNG",
                    **kwargs) -> None:
        """
        Save QR code to file.
        
        Args:
            pairing_code: PairingCode object
            filepath: Output file path
            format: Image format
            **kwargs: Additional arguments for generate_qr_code
        """
        qr_img = self.generate_qr_code(pairing_code, **kwargs)
        qr_img.save(filepath, format=format)
    
    def get_qr_base64(self, 
                     pairing_code: PairingCode,
                     format: str = "PNG",
                     **kwargs) -> str:
        """
        Get QR code as base64 string.
        
        Args:
            pairing_code: PairingCode object
            format: Image format
            **kwargs: Additional arguments for generate_qr_code
        
        Returns:
            Base64 encoded image string
        """
        qr_img = self.generate_qr_code(pairing_code, **kwargs)
        
        buffered = BytesIO()
        qr_img.save(buffered, format=format)
        
        return base64.b64encode(buffered.getvalue()).decode()
    
    def generate_multiple_qrs(self,
                             pairing_codes: List[PairingCode],
                             grid_size: Tuple[int, int] = (3, 3),
                             spacing: int = 20,
                             background: Tuple[int, int, int] = (240, 240, 240)) -> Image.Image:
        """
        Generate grid of multiple QR codes.
        
        Args:
            pairing_codes: List of PairingCode objects
            grid_size: Grid dimensions (cols, rows)
            spacing: Space between QR codes
            background: Background color
        
        Returns:
            Combined image
        """
        cols, rows = grid_size
        qr_size = min(150, self.size // 2)  # Smaller for grid
        
        # Generate individual QR codes
        qr_images = []
        for code in pairing_codes[:cols * rows]:
            qr_img = self.generate_qr_code(code, size=qr_size)
            qr_images.append(qr_img)
        
        # Calculate total size
        total_width = cols * qr_size + (cols + 1) * spacing
        total_height = rows * qr_size + (rows + 1) * spacing
        
        # Create canvas
        canvas = Image.new('RGB', (total_width, total_height), background)
        
        # Paste QR codes
        for i, qr_img in enumerate(qr_images):
            row = i // cols
            col = i % cols
            
            x = spacing + col * (qr_size + spacing)
            y = spacing + row * (qr_size + spacing)
            
            canvas.paste(qr_img, (x, y))
        
        return canvas
