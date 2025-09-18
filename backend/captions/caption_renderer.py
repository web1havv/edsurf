"""
Caption Rendering Module for Video Generation
Phase 2: Visual Caption Overlays with OpenCV
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import os

logger = logging.getLogger(__name__)

class CaptionRenderer:
    """
    Renders caption overlays on video frames using OpenCV
    """
    
    def __init__(self, video_width: int = 1080, video_height: int = 1920):
        self.video_width = video_width
        self.video_height = video_height
        
        # Calculate scaling factor based on video size (1080p as baseline)
        scale_factor = min(video_width / 1080, video_height / 1920)
        
        # Caption styling settings (scaled to video size)
        self.font = self._get_montserrat_font_path()
        self.font_size = max(16, int(72 * scale_factor))  # Minimum 16px, scaled from 72px baseline
        self.font_thickness = max(1, int(3 * scale_factor))  # Minimum 1px thickness
        self.line_spacing = max(8, int(20 * scale_factor))  # Pixels between lines
        
        # Position settings (bottom third of video) - scaled
        self.caption_top_margin = max(40, int(200 * scale_factor))  # Pixels from bottom
        self.caption_side_margin = max(20, int(60 * scale_factor))  # Pixels from sides
        self.caption_max_width = video_width - (2 * self.caption_side_margin)
        
        # Background settings - scaled
        self.background_padding = max(8, int(15 * scale_factor))  # Padding around text
        self.background_alpha = 0.8       # Background transparency (0-1) - increased for better readability
        self.corner_radius = max(5, int(15 * scale_factor))  # Rounded corners
        
        # Log the calculated settings
        logger.info(f"🎨 Caption renderer initialized for {video_width}x{video_height}")
        logger.info(f"📐 Scale factor: {scale_factor:.2f}")
        logger.info(f"🔤 Font size: {self.font_size}px (thickness: {self.font_thickness})")
        logger.info(f"📍 Margins: top={self.caption_top_margin}px, side={self.caption_side_margin}px")
        logger.info(f"🎨 Background: padding={self.background_padding}px, alpha={self.background_alpha}, radius={self.corner_radius}px")
        
        # Speaker-specific colors (BGR format for OpenCV)
        self.speaker_colors = {
            'elon': {
                'text': (255, 255, 255),   
                'stroke': (0, 255, 0),
                'background': (50, 150, 255), # Blue background
                'accent': (0, 200, 255)       # Light blue accent
            },
            'trump': {
                'text': (255, 255, 255), 
                'stroke': (0, 255, 0),     # White text  
                'background': (50, 50, 200),  # Red background
                'accent': (100, 100, 255)     # Light red accent
            },
            'baburao': {
                'text': (255, 255, 255),
                'stroke': (0, 255, 0),
                'background': (50, 200, 50),  # Green background
                'accent': (100, 255, 100)     # Light green accent
            },
            'samay': {
                'text': (255, 255, 255),
                'stroke': (0, 255, 0),
                'background': (200, 100, 50),  # Orange background
                'accent': (255, 150, 100)     # Light orange accent
            },
            'arpit': {
                'text': (255, 255, 255),
                'stroke': (0, 255, 0),
                'background': (150, 50, 150),  # Purple background
                'accent': (200, 100, 200)     # Light purple accent
            },
            'modi': {
                'text': (255, 255, 255),
                'stroke': (0, 255, 0),
                'background': (0, 100, 200),  # Saffron background (Indian flag colors)
                'accent': (50, 150, 255)     # Light saffron accent
            },
            'mrbeast': {
                'text': (255, 255, 255),
                'stroke': (0, 255, 0),
                'background': (100, 200, 0),  # Green background (MrBeast brand color)
                'accent': (150, 255, 50)     # Light green accent
            },
            'ronaldo': {
                'text': (255, 255, 255),
                'stroke': (0, 255, 0),
                'background': (0, 100, 200),  # Blue background (Portugal/Real Madrid colors)
                'accent': (50, 150, 255)     # Light blue accent
            },
            'ishowspeed': {
                'text': (255, 255, 255),
                'stroke': (0, 255, 0),
                'background': (200, 0, 200),  # Purple background (gaming/streaming theme)
                'accent': (255, 50, 255)     # Light purple accent
            },
            'default': {
                'text': (255, 255, 255),  
                'stroke': (0, 255, 0),    # White text
                'background': (60, 60, 60),   # Dark gray background
                'accent': (150, 150, 150)     # Light gray accent
            }
        }
        
        logger.info(f"🎨 Caption renderer initialized for {video_width}x{video_height}")
    
    def _get_montserrat_font_path(self) -> str:
        """Get Montserrat font path from local fonts directory"""
        try:
            # Path to local Montserrat font files
            base_dir = os.path.dirname(os.path.dirname(__file__))  # Go up to backend/
            font_dir = os.path.join(base_dir, "fonts/Montserrat/static")

            font_path = os.path.join(font_dir, "Montserrat-Bold.ttf")

            if os.path.exists(font_path):
                logger.info(f"✅ Found Montserrat font: {font_path}")
                return font_path
            
        except Exception as e:
            logger.warning(f"⚠️ Error finding Montserrat font: {e}")


    def _get_text_size(self, text: str) -> Tuple[int, int]:
        """Get text size in pixels using PIL for Arial font"""
        try:
            if self.font:
                font = ImageFont.truetype(self.font, self.font_size)
            else:
                font = ImageFont.load_default()
            
            # Create temporary image to measure text
            temp_img = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(temp_img)
            bbox = draw.textbbox((0, 0), text, font=font)
            
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            return width, height
        except Exception as e:
            logger.warning(f"⚠️ PIL text measurement failed: {e}")
            # Fallback to OpenCV measurement
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_DUPLEX, 1.4, self.font_thickness
            )
            return text_width, text_height + baseline

    def _draw_text_with_pil(self, frame: np.ndarray, text: str, position: Tuple[int, int], 
                           color: Tuple[int, int, int]) -> np.ndarray:
        """Draw text using PIL for Arial font support"""
        try:
            if not self.font:
                # Fallback to OpenCV if no font found
                cv2.putText(frame, text, (position[0] + 2, position[1] + 2), 
                           cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 0, 0), 
                           self.font_thickness + 1, cv2.LINE_AA)  # Shadow
                cv2.putText(frame, text, position, cv2.FONT_HERSHEY_DUPLEX, 
                           1.4, color, self.font_thickness, cv2.LINE_AA)
                return frame
            
            # Convert BGR to RGB for PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            draw = ImageDraw.Draw(pil_image)
            
            # Load Arial font
            font = ImageFont.truetype(self.font, self.font_size)
            
            # Convert BGR color to RGB for PIL
            rgb_color = (color[2], color[1], color[0])

            # Adjust position from OpenCV baseline to PIL top-left
            # Get text metrics to adjust Y position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_height = bbox[3] - bbox[1]
            
            # Convert from OpenCV baseline (bottom-left) to PIL top-left
            pil_x = position[0]
            pil_y = position[1] - text_height
            
            # Draw text with shadow for better readability
            shadow_offset = 2
            draw.text((position[0] + shadow_offset, position[1] + shadow_offset), 
                     text, font=font, fill=(0, 0, 0))  # Black shadow
            draw.text(position, text, font=font, fill=rgb_color)
            
            # Convert back to BGR for OpenCV
            frame_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return frame_bgr
            
        except Exception as e:
            logger.warning(f"⚠️ PIL text rendering failed: {e}")
            # Fallback to OpenCV
            cv2.putText(frame, text, (position[0] + 2, position[1] + 2), 
                       cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 0, 0), 
                       self.font_thickness + 1, cv2.LINE_AA)  # Shadow
            cv2.putText(frame, text, position, cv2.FONT_HERSHEY_DUPLEX, 
                       1.4, color, self.font_thickness, cv2.LINE_AA)
            return frame
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """
        Wrap text to fit within max_width pixels
        Returns list of text lines
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width, _ = self._get_text_size(test_line)
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word is too long, use it anyway
                    lines.append(word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _draw_rounded_rectangle(self, frame: np.ndarray, top_left: Tuple[int, int], 
                               bottom_right: Tuple[int, int], color: Tuple[int, int, int], 
                               alpha: float = 1.0) -> None:
        """Draw rounded rectangle with transparency"""
        x1, y1 = top_left
        x2, y2 = bottom_right
        
        # Create overlay for transparency
        overlay = frame.copy()
        
        # Draw main rectangle
        cv2.rectangle(overlay, (x1 + self.corner_radius, y1), 
                     (x2 - self.corner_radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1 + self.corner_radius), 
                     (x2, y2 - self.corner_radius), color, -1)
        
        # Draw corner circles
        cv2.circle(overlay, (x1 + self.corner_radius, y1 + self.corner_radius), 
                  self.corner_radius, color, -1)
        cv2.circle(overlay, (x2 - self.corner_radius, y1 + self.corner_radius), 
                  self.corner_radius, color, -1)
        cv2.circle(overlay, (x1 + self.corner_radius, y2 - self.corner_radius), 
                  self.corner_radius, color, -1)
        cv2.circle(overlay, (x2 - self.corner_radius, y2 - self.corner_radius), 
                  self.corner_radius, color, -1)
        
        # Apply transparency
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    def render_caption(self, frame: np.ndarray, caption_text: str, 
                      speaker: str = 'default') -> np.ndarray:
        """
        Render caption overlay on video frame
        
        Args:
            frame: Video frame (BGR format)
            caption_text: Text to display
            speaker: Speaker name for styling
            
        Returns:
            Frame with caption overlay
        """
        try:
            if not caption_text.strip():
                return frame
            
            # Get speaker colors
            colors = self.speaker_colors.get(speaker, self.speaker_colors['default'])
            
            # Wrap text to fit width
            max_text_width = self.caption_max_width - (2 * self.background_padding)
            text_lines = self._wrap_text(caption_text, max_text_width)
            
            if not text_lines:
                return frame
            
            # Calculate total text dimensions
            line_heights = []
            max_line_width = 0
            
            for line in text_lines:
                line_width, line_height = self._get_text_size(line)
                line_heights.append(line_height)
                max_line_width = max(max_line_width, line_width)
            
            total_text_height = sum(line_heights) + (len(text_lines) - 1) * self.line_spacing
            
            # Calculate background dimensions
            bg_width = max_line_width + (2 * self.background_padding)
            bg_height = total_text_height + (2 * self.background_padding)
            
            # Position background (center horizontally, bottom third vertically)
            bg_x1 = (self.video_width - bg_width) // 2
            bg_y1 = self.caption_top_margin
            bg_x2 = bg_x1 + bg_width
            bg_y2 = bg_y1 + bg_height
            
            # Ensure background is within frame bounds
            bg_x1 = max(self.caption_side_margin, bg_x1)
            bg_x2 = min(self.video_width - self.caption_side_margin, bg_x2)
            bg_y1 = max(0, bg_y1)
            bg_y2 = min(self.video_height, bg_y2)
            
            # Draw background
            self._draw_rounded_rectangle(
                frame, (bg_x1, bg_y1), (bg_x2, bg_y2), 
                colors['background'], self.background_alpha
            )
            
            # Draw text lines
            current_y = bg_y1 + self.background_padding + line_heights[0]
            
            for i, line in enumerate(text_lines):
                line_width, line_height = self._get_text_size(line)
                
                # Center text horizontally within background
                text_x = bg_x1 + (bg_width - line_width) // 2
                text_y = current_y
                
                # Draw text with PIL for Arial font (includes shadow)
                frame = self._draw_text_with_pil(frame, line, (text_x, text_y), colors['text'])
                
                # Move to next line
                if i < len(text_lines) - 1:
                    current_y += line_heights[i] + self.line_spacing
            
            return frame
            
        except Exception as e:
            logger.error(f"❌ Failed to render caption: {str(e)}")
            return frame
    
# Global instance - will be initialized with proper dimensions
caption_renderer = None

def render_caption_on_frame(frame: np.ndarray, caption_text: str, 
                           speaker: str = 'default') -> np.ndarray:
    """
    Main function to render caption on video frame
    """
    global caption_renderer
    
    # Initialize renderer with frame dimensions if not already done
    if caption_renderer is None:
        video_height, video_width = frame.shape[:2]
        logger.info(f"🎨 Initializing caption renderer for video dimensions: {video_width}x{video_height}")
        caption_renderer = CaptionRenderer(video_width, video_height)
    
    return caption_renderer.render_caption(frame, caption_text, speaker)