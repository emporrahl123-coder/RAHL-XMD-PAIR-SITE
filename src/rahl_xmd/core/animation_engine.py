"""
Animation engine for creating animated QR codes and effects.
"""

from PIL import Image, ImageDraw, ImageSequence
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
import math
from enum import Enum
import random

from .pairing_system import CodeTheme
from .qr_generator import QRGenerator


class AnimationType(str, Enum):
    """Types of animations."""
    PULSE = "pulse"
    ROTATE = "rotate"
    GLITCH = "glitch"
    RAIN = "rain"
    WAVE = "wave"
    SCAN = "scan"
    FADE = "fade"
    SPARKLE = "sparkle"


class AnimationEngine:
    """Creates animated QR codes and effects."""
    
    def __init__(self, 
                 qr_generator: Optional[QRGenerator] = None,
                 default_fps: int = 10,
                 default_duration: float = 3.0):
        """
        Initialize animation engine.
        
        Args:
            qr_generator: QRGenerator instance
            default_fps: Default frames per second
            default_duration: Default animation duration in seconds
        """
        self.qr_generator = qr_generator or QRGenerator()
        self.default_fps = default_fps
        self.default_duration = default_duration
    
    def create_animated_qr(self,
                          pairing_code: Any,  # PairingCode or similar
                          animation_type: AnimationType = AnimationType.PULSE,
                          fps: Optional[int] = None,
                          duration: Optional[float] = None,
                          loop: bool = True) -> List[Image.Image]:
        """
        Create animated QR code frames.
        
        Args:
            pairing_code: PairingCode object
            animation_type: Type of animation
            fps: Frames per second
            duration: Duration in seconds
            loop: Whether animation loops
        
        Returns:
            List of PIL Image frames
        """
        fps = fps or self.default_fps
        duration = duration or self.default_duration
        total_frames = int(fps * duration)
        
        # Generate base QR code
        base_qr = self.qr_generator.generate_qr_code(pairing_code)
        
        # Create frames based on animation type
        frames = []
        
        if animation_type == AnimationType.PULSE:
            frames = self._create_pulse_animation(base_qr, total_frames)
        elif animation_type == AnimationType.ROTATE:
            frames = self._create_rotate_animation(base_qr, total_frames)
        elif animation_type == AnimationType.GLITCH:
            frames = self._create_glitch_animation(base_qr, total_frames)
        elif animation_type == AnimationType.RAIN:
            frames = self._create_rain_animation(base_qr, total_frames)
        elif animation_type == AnimationType.WAVE:
            frames = self._create_wave_animation(base_qr, total_frames)
        elif animation_type == AnimationType.SCAN:
            frames = self._create_scan_animation(base_qr, total_frames)
        elif animation_type == AnimationType.FADE:
            frames = self._create_fade_animation(base_qr, total_frames)
        elif animation_type == AnimationType.SPARKLE:
            frames = self._create_sparkle_animation(base_qr, total_frames)
        else:
            # Default: pulse animation
            frames = self._create_pulse_animation(base_qr, total_frames)
        
        # If not looping, add fade out at the end
        if not loop and len(frames) > 1:
            frames.extend(self._create_fade_out(frames[-1], fps // 2))
        
        return frames
    
    def _create_pulse_animation(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create pulsing animation."""
        img_array = np.array(base_img)
        result_frames = []
        
        for i in range(frames):
            # Calculate pulse intensity
            pulse = 0.7 + 0.3 * math.sin(2 * math.pi * i / frames)
            
            # Apply pulse to non-background pixels
            frame_array = img_array.copy()
            
            # Find non-background pixels (assuming background is light)
            brightness = np.mean(frame_array, axis=2)
            mask = brightness < 200  # Darker pixels are QR code
            
            # Apply pulse to QR code pixels
            for channel in range(3):
                channel_data = frame_array[:, :, channel]
                channel_data[mask] = np.clip(channel_data[mask] * pulse, 0, 255)
            
            frame = Image.fromarray(frame_array.astype(np.uint8))
            result_frames.append(frame)
        
        return result_frames
    
    def _create_rotate_animation(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create rotating animation."""
        result_frames = []
        
        for i in range(frames):
            angle = (360 * i / frames) % 360
            
            # Rotate image
            rotated = base_img.rotate(angle, expand=False, fillcolor=(255, 255, 255))
            
            # Keep original size
            if rotated.size != base_img.size:
                # Crop to center
                left = (rotated.width - base_img.width) // 2
                top = (rotated.height - base_img.height) // 2
                right = left + base_img.width
                bottom = top + base_img.height
                rotated = rotated.crop((left, top, right, bottom))
            
            result_frames.append(rotated)
        
        return result_frames
    
    def _create_glitch_animation(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create glitch effect animation."""
        img_array = np.array(base_img)
        height, width, _ = img_array.shape
        result_frames = []
        
        for i in range(frames):
            frame_array = img_array.copy()
            
            # Random glitch effects
            if random.random() < 0.3:
                # Horizontal shift
                shift = random.randint(-5, 5)
                if shift != 0:
                    frame_array = np.roll(frame_array, shift, axis=1)
            
            if random.random() < 0.2:
                # Color channel shift
                channel_shift = random.randint(-3, 3)
                for channel in range(3):
                    if random.random() < 0.5:
                        frame_array[:, :, channel] = np.roll(
                            frame_array[:, :, channel], 
                            channel_shift, 
                            axis=random.randint(0, 1)
                        )
            
            if random.random() < 0.1:
                # Pixelation effect
                block_size = random.randint(2, 4)
                h_blocks = height // block_size
                w_blocks = width // block_size
                
                for h in range(h_blocks):
                    for w in range(w_blocks):
                        h_start = h * block_size
                        w_start = w * block_size
                        block = frame_array[h_start:h_start+block_size, 
                                          w_start:w_start+block_size]
                        avg_color = np.mean(block, axis=(0, 1))
                        frame_array[h_start:h_start+block_size, 
                                  w_start:w_start+block_size] = avg_color
            
            frame = Image.fromarray(frame_array.astype(np.uint8))
            result_frames.append(frame)
        
        return result_frames
    
    def _create_rain_animation(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create matrix-style rain animation."""
        img_array = np.array(base_img)
        height, width, _ = img_array.shape
        result_frames = []
        
        # Initialize rain drops
        drop_count = width // 10
        drops = []
        for _ in range(drop_count):
            drops.append({
                'x': random.randint(0, width - 1),
                'y': random.randint(-height, -1),
                'speed': random.uniform(2, 5),
                'length': random.randint(5, 15)
            })
        
        for frame_num in range(frames):
            frame_array = img_array.copy()
            
            # Update and draw drops
            for drop in drops:
                # Update position
                drop['y'] += drop['speed']
                
                # Reset if off screen
                if drop['y'] > height:
                    drop['y'] = random.randint(-height, -1)
                    drop['x'] = random.randint(0, width - 1)
                
                # Draw drop
                for i in range(drop['length']):
                    y_pos = int(drop['y']) - i
                    if 0 <= y_pos < height and 0 <= drop['x'] < width:
                        # Fade intensity
                        intensity = 255 * (1 - i / drop['length'])
                        
                        # Matrix green color
                        if random.random() < 0.8:  # Main drop
                            frame_array[y_pos, drop['x']] = [0, int(intensity), 0]
                        else:  # Trail
                            frame_array[y_pos, drop['x']] = [0, int(intensity * 0.5), 0]
            
            frame = Image.fromarray(frame_array.astype(np.uint8))
            result_frames.append(frame)
        
        return result_frames
    
    def _create_wave_animation(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create wave distortion animation."""
        img_array = np.array(base_img)
        height, width, _ = img_array.shape
        result_frames = []
        
        for i in range(frames):
            frame_array = np.zeros_like(img_array)
            
            # Calculate wave parameters
            wave_phase = 2 * math.pi * i / frames
            amplitude = 5 * math.sin(wave_phase * 2)
            frequency = 0.05
            
            # Apply wave distortion
            for y in range(height):
                for x in range(width):
                    # Calculate source position with wave distortion
                    offset = amplitude * math.sin(y * frequency + wave_phase)
                    src_x = int(x + offset)
                    src_y = y
                    
                    # Clamp to image bounds
                    src_x = max(0, min(width - 1, src_x))
                    src_y = max(0, min(height - 1, src_y))
                    
                    # Copy pixel
                    frame_array[y, x] = img_array[src_y, src_x]
            
            frame = Image.fromarray(frame_array.astype(np.uint8))
            result_frames.append(frame)
        
        return result_frames
    
    def _create_scan_animation(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create scanning line animation."""
        img_array = np.array(base_img)
        height, width, _ = img_array.shape
        result_frames = []
        
        for i in range(frames):
            frame_array = img_array.copy()
            
            # Calculate scan line position
            scan_y = int(height * i / frames)
            scan_height = height // 10
            
            # Draw scan line effect
            for y in range(max(0, scan_y - scan_height), min(height, scan_y + scan_height)):
                # Calculate intensity (bell curve)
                distance = abs(y - scan_y) / scan_height
                intensity = max(0, 1 - distance * distance)
                
                # Apply highlight to scan line
                for x in range(width):
                    if random.random() < intensity * 0.3:
                        # Add highlight
                        highlight = np.array([100, 100, 100]) * intensity
                        frame_array[y, x] = np.clip(frame_array[y, x] + highlight, 0, 255)
            
            frame = Image.fromarray(frame_array.astype(np.uint8))
            result_frames.append(frame)
        
        return result_frames
    
    def _create_fade_animation(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create fade in/out animation."""
        result_frames = []
        
        # Fade in
        fade_in_frames = frames // 3
        for i in range(fade_in_frames):
            alpha = i / fade_in_frames
            faded = self._apply_alpha(base_img, alpha)
            result_frames.append(faded)
        
        # Full opacity
        full_frames = frames // 3
        for _ in range(full_frames):
            result_frames.append(base_img.copy())
        
        # Fade out
        fade_out_frames = frames - fade_in_frames - full_frames
        for i in range(fade_out_frames):
            alpha = 1 - i / fade_out_frames
            faded = self._apply_alpha(base_img, alpha)
            result_frames.append(faded)
        
        return result_frames
    
    def _create_sparkle_animation(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create sparkle animation."""
        img_array = np.array(base_img)
        height, width, _ = img_array.shape
        result_frames = []
        
        # Generate sparkles
        sparkle_count = (height * width) // 500
        sparkles = []
        for _ in range(sparkle_count):
            sparkles.append({
                'x': random.randint(0, width - 1),
                'y': random.randint(0, height - 1),
                'size': random.uniform(1, 3),
                'intensity': random.uniform(0.5, 1),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.1, 0.3)
            })
        
        for frame_num in range(frames):
            frame_array = img_array.copy()
            
            # Update and draw sparkles
            for sparkle in sparkles:
                # Calculate brightness
                brightness = (math.sin(sparkle['phase'] + frame_num * sparkle['speed']) + 1) / 2
                brightness *= sparkle['intensity']
                
                # Draw sparkle
                sparkle_size = int(sparkle['size'])
                for dx in range(-sparkle_size, sparkle_size + 1):
                    for dy in range(-sparkle_size, sparkle_size + 1):
                        x = sparkle['x'] + dx
                        y = sparkle['y'] + dy
                        
                        if 0 <= x < width and 0 <= y < height:
                            # Calculate distance from center
                            dist = math.sqrt(dx*dx + dy*dy) / sparkle_size
                            if dist <= 1:
                                # Sparkle color (white with theme tint)
                                sparkle_color = np.array([255, 255, 255]) * brightness
                                
                                # Blend with background
                                alpha = 1 - dist  # Fade at edges
                                frame_array[y, x] = np.clip(
                                    frame_array[y, x] * (1 - alpha) + sparkle_color * alpha,
                                    0, 255
                                )
            
            frame = Image.fromarray(frame_array.astype(np.uint8))
            result_frames.append(frame)
        
        return result_frames
    
    def _create_fade_out(self, base_img: Image.Image, frames: int) -> List[Image.Image]:
        """Create fade out sequence."""
        result_frames = []
        
        for i in range(frames):
            alpha = 1 - i / frames
            faded = self._apply_alpha(base_img, alpha)
            result_frames.append(faded)
        
        return result_frames
    
    def _apply_alpha(self, img: Image.Image, alpha: float) -> Image.Image:
        """Apply alpha transparency to image."""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create alpha channel
        alpha_channel = Image.new('L', img.size, int(alpha * 255))
        
        # Apply alpha
        img_with_alpha = img.copy()
        img_with_alpha.putalpha(alpha_channel)
        
        return img_with_alpha
    
    def save_animated_gif(self,
                         frames: List[Image.Image],
                         filepath: str,
                         duration: int = 100,
                         loop: bool = True) -> None:
        """
        Save frames as animated GIF.
        
        Args:
            frames: List of image frames
            filepath: Output file path
            duration: Frame duration in milliseconds
            loop: Whether GIF loops
        """
        if not frames:
            raise ValueError("No frames to save")
        
        # Convert duration to ms per frame
        frame_duration = duration
        
        # Save as GIF
        frames[0].save(
            filepath,
            save_all=True,
            append_images=frames[1:],
            duration=frame_duration,
            loop=0 if loop else 1,
            optimize=True
        )
    
    def create_theme_animation(self,
                              pairing_code: Any,
                              theme: CodeTheme,
                              animation_type: Optional[AnimationType] = None) -> List[Image.Image]:
        """
        Create animation based on theme.
        
        Args:
            pairing_code: PairingCode object
            theme: Code theme
            animation_type: Override default animation type
        
        Returns:
            List of image frames
        """
        # Map themes to default animations
        theme_animations = {
            CodeTheme.NEON: AnimationType.PULSE,
            CodeTheme.CYBERPUNK: AnimationType.GLITCH,
            CodeTheme.MATRIX: AnimationType.RAIN,
            CodeTheme.AURORA: AnimationType.WAVE,
            CodeTheme.HOLOGRAM: AnimationType.SCAN,
            CodeTheme.DEFAULT: AnimationType.FADE
        }
        
        anim_type = animation_type or theme_animations.get(theme, AnimationType.PULSE)
        
        return self.create_animated_qr(
            pairing_code,
            animation_type=anim_type,
            fps=self.default_fps,
            duration=self.default_duration
        )
