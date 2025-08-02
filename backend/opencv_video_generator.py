"""
OpenCV-based Video Generation System
Reliable replacement for MoviePy with better stability and performance
"""

import cv2
import numpy as np
import os
import tempfile
import subprocess
import logging
from PIL import Image, ImageDraw
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class OpenCVVideoGenerator:
    """
    Professional video generation using OpenCV and FFmpeg
    Much more stable than MoviePy
    """
    
    def __init__(self):
        self.fps = 30
        self.video_width = 1080
        self.video_height = 1920  # Vertical format
        logger.info(f"🎬 OpenCV Video Generator initialized")
        logger.info(f"📐 Output format: {self.video_width}x{self.video_height} @ {self.fps}fps")
    
    def load_and_resize_image(self, image_path, target_size):
        """Load and resize image using PIL and OpenCV"""
        try:
            # Load with PIL first for better format support
            pil_img = Image.open(image_path)
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            # Resize using PIL
            pil_img = pil_img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to OpenCV format (BGR)
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            logger.info(f"✅ Image loaded and resized: {image_path} -> {target_size}")
            return cv_img
            
        except Exception as e:
            logger.error(f"❌ Failed to load image {image_path}: {str(e)}")
            # Create placeholder
            placeholder = np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
            placeholder[:] = (128, 128, 128)  # Gray
            return placeholder
    
    def create_circular_mask(self, size):
        """Create circular mask for rounded speaker images"""
        mask = np.zeros((size[1], size[0]), dtype=np.uint8)
        center = (size[0]//2, size[1]//2)
        radius = min(size[0], size[1])//2
        cv2.circle(mask, center, radius, 255, -1)
        return mask
    
    def load_background_video(self, video_path):
        """Load background video using OpenCV"""
        try:
            if not os.path.exists(video_path):
                logger.error(f"❌ Background video not found: {video_path}")
                return None, 0
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"❌ Could not open video: {video_path}")
                return None, 0
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            
            logger.info(f"✅ Background video loaded: {video_path}")
            logger.info(f"📊 Video info: {frame_count} frames, {fps} fps, {duration:.2f}s")
            
            return cap, duration
            
        except Exception as e:
            logger.error(f"❌ Failed to load background video: {str(e)}")
            return None, 0
    
    def get_audio_duration(self, audio_path, timeline=None):
        """Get audio duration using timeline first, then fallback methods"""
        
        # Method 1: Use timeline duration (most reliable for our use case)
        if timeline and len(timeline) > 0:
            try:
                max_end_time = max(segment['end_time'] for segment in timeline)
                if max_end_time > 0:
                    logger.info(f"🎵 Audio duration (timeline): {max_end_time:.2f}s")
                    return max_end_time
            except Exception as e:
                logger.warning(f"⚠️ Timeline duration extraction failed: {str(e)}")
        
        # Method 2: Try local ffprobe binary
        try:
            ffprobe_path = './ffprobe' if os.path.exists('./ffprobe') else 'ffprobe'
            cmd = [
                ffprobe_path, '-v', 'quiet', '-print_format', 'json',
                '-show_format', audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data['format']['duration'])
                logger.info(f"🎵 Audio duration (ffprobe): {duration:.2f}s")
                return duration
            else:
                logger.warning(f"⚠️ FFprobe method failed (exit {result.returncode}): {result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️ FFprobe method failed: {str(e)}")
        
        # Method 3: Try using OpenCV to read as video (some audio files work)
        try:
            cap = cv2.VideoCapture(audio_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if fps > 0 and frame_count > 0:
                    duration = frame_count / fps
                    cap.release()
                    logger.info(f"🎵 Audio duration (OpenCV): {duration:.2f}s")
                    return duration
                cap.release()
        except Exception as e:
            logger.warning(f"⚠️ OpenCV method failed: {str(e)}")
        
        # Method 4: Estimate based on file size (much better estimation)
        try:
            file_size = os.path.getsize(audio_path)
            if file_size > 100000:  # If file is larger than 100KB
                # Estimate ~14KB per second for WAV files (rough estimate)
                estimated_duration = file_size / 14000
                logger.warning(f"⚠️ Using file-size-based estimate: {estimated_duration:.2f}s ({file_size} bytes)")
                return estimated_duration
            elif file_size > 50000:  # Smaller file, more conservative estimate
                estimated_duration = 30.0  # Assume at least 30 seconds for decent-sized files
                logger.warning(f"⚠️ Using conservative estimate: {estimated_duration}s")
                return estimated_duration
        except Exception:
            pass
        
        logger.error(f"❌ Could not determine audio duration for {audio_path}")
        return 0
    
    def create_video_with_overlays(self, script_text, audio_path, background_video_path=None, output_path=None):
        """
        Create video with background video and speaker overlays
        Using OpenCV for maximum reliability
        """
        try:
            request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"🎬 [{request_id}] Starting OpenCV video generation")
            
            if not output_path:
                output_path = f"opencv_video_{request_id}.mp4"
            
            # Create speaker timeline first (needed for duration detection)
            from conversational_tts import create_speaker_timeline
            timeline = create_speaker_timeline(script_text)
            logger.info(f"⏰ [{request_id}] Created timeline with {len(timeline)} segments")
            
            # Log timeline details
            if timeline:
                for i, segment in enumerate(timeline):
                    logger.info(f"   Segment {i+1}: {segment['speaker']} ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s)")
            
            # Get audio duration (using timeline as primary source)
            audio_duration = self.get_audio_duration(audio_path, timeline)
            if audio_duration <= 0:
                raise Exception("Could not determine audio duration")
            
            total_frames = int(audio_duration * self.fps)
            logger.info(f"🎬 [{request_id}] Creating {total_frames} frames for {audio_duration:.2f}s")
            
            # Load speaker images
            elon_img = self.load_and_resize_image("../63b84b16d1c5130019f95f8c.webp", (200, 200))
            trump_img = self.load_and_resize_image("../trump-removebg-preview.png", (200, 200))
            
            # Create circular masks for speaker images
            mask = self.create_circular_mask((200, 200))
            
            # Apply circular mask to speaker images
            elon_masked = cv2.bitwise_and(elon_img, elon_img, mask=mask)
            trump_masked = cv2.bitwise_and(trump_img, trump_img, mask=mask)
            
            logger.info(f"✅ [{request_id}] Speaker images loaded and processed")
            
            # Load background video
            background_cap, bg_duration = self.load_background_video(background_video_path or "../minecraft-1.mp4")
            if background_cap is None:
                raise Exception("Could not load background video")
            
            # Create video writer
            temp_video_path = f"temp_video_{request_id}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(temp_video_path, fourcc, self.fps, (self.video_width, self.video_height))
            
            logger.info(f"🎬 [{request_id}] Creating video frames...")
            
            # Generate frames
            for frame_num in range(total_frames):
                current_time = frame_num / self.fps
                
                # Get background frame
                if bg_duration > 0:
                    bg_frame_num = int((current_time % bg_duration) * self.fps)
                    background_cap.set(cv2.CAP_PROP_POS_FRAMES, bg_frame_num)
                    ret, bg_frame = background_cap.read()
                    
                    if ret:
                        # Resize background to fit our video dimensions
                        bg_frame = cv2.resize(bg_frame, (self.video_width, self.video_height))
                    else:
                        # Create solid background if frame read fails
                        bg_frame = np.zeros((self.video_height, self.video_width, 3), dtype=np.uint8)
                        bg_frame[:] = (50, 50, 150)  # Dark blue
                else:
                    # Create solid background
                    bg_frame = np.zeros((self.video_height, self.video_width, 3), dtype=np.uint8)
                    bg_frame[:] = (50, 50, 150)  # Dark blue
                
                # Find current speaker
                current_speaker = None
                for segment in timeline:
                    if segment['start_time'] <= current_time <= segment['end_time']:
                        current_speaker = segment['speaker']
                        break
                
                # Add speaker overlay
                if current_speaker == 'elon':
                    # Position Elon on the right
                    y_pos = 200
                    x_pos = self.video_width - 300  # Right side
                    self._overlay_image(bg_frame, elon_masked, mask, x_pos, y_pos)
                elif current_speaker == 'trump':
                    # Position Trump on the left
                    y_pos = 200
                    x_pos = 100  # Left side
                    self._overlay_image(bg_frame, trump_masked, mask, x_pos, y_pos)
                
                # Write frame
                video_writer.write(bg_frame)
                
                # Progress logging
                if frame_num % (self.fps * 2) == 0:  # Every 2 seconds
                    progress = (frame_num / total_frames) * 100
                    logger.info(f"🎬 [{request_id}] Progress: {progress:.1f}% ({frame_num}/{total_frames} frames)")
            
            # Clean up
            video_writer.release()
            background_cap.release()
            
            logger.info(f"✅ [{request_id}] Video frames generated: {temp_video_path}")
            
            # Combine video with audio using FFmpeg
            logger.info(f"🎵 [{request_id}] Adding audio with FFmpeg...")
            self._add_audio_with_ffmpeg(temp_video_path, audio_path, output_path)
            
            # Clean up temporary video
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            
            # Verify output
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ [{request_id}] Video created successfully: {output_path}")
                logger.info(f"📊 [{request_id}] File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
                return output_path
            else:
                raise Exception("Output video was not created")
                
        except Exception as e:
            logger.error(f"❌ [{request_id}] OpenCV video generation failed: {str(e)}")
            raise Exception(f"OpenCV video generation failed: {str(e)}")
    
    def _overlay_image(self, background, overlay_img, mask, x_pos, y_pos):
        """Overlay image with transparency using mask"""
        try:
            h, w = overlay_img.shape[:2]
            
            # Ensure position is within bounds
            x_pos = max(0, min(x_pos, self.video_width - w))
            y_pos = max(0, min(y_pos, self.video_height - h))
            
            # Region of interest in background
            roi = background[y_pos:y_pos+h, x_pos:x_pos+w]
            
            # Create inverse mask
            mask_inv = cv2.bitwise_not(mask)
            
            # Black out the area of overlay in ROI
            background_masked = cv2.bitwise_and(roi, roi, mask=mask_inv)
            
            # Take only region of overlay from overlay image
            overlay_masked = cv2.bitwise_and(overlay_img, overlay_img, mask=mask)
            
            # Add overlay to background
            combined = cv2.add(background_masked, overlay_masked)
            
            # Replace ROI in background
            background[y_pos:y_pos+h, x_pos:x_pos+w] = combined
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to overlay image at ({x_pos}, {y_pos}): {str(e)}")
    
    def _add_audio_with_ffmpeg(self, video_path, audio_path, output_path):
        """Add audio to video using FFmpeg"""
        try:
            # Use local ffmpeg binary
            ffmpeg_path = './ffmpeg' if os.path.exists('./ffmpeg') else 'ffmpeg'
            cmd = [
                ffmpeg_path, '-y',  # Overwrite output
                '-i', video_path,  # Input video
                '-i', audio_path,  # Input audio
                '-c:v', 'libx264',  # Video codec
                '-c:a', 'aac',  # Audio codec
                '-strict', 'experimental',
                '-shortest',  # Stop when shortest stream ends
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"❌ FFmpeg failed: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr}")
            
            logger.info(f"✅ Audio added successfully with FFmpeg")
            
        except Exception as e:
            logger.error(f"❌ Failed to add audio: {str(e)}")
            raise

# Global instance
video_generator = OpenCVVideoGenerator()

def create_background_video_with_speaker_overlays(script_text, audio_path, background_video_path=None, output_path=None):
    """
    Main function to replace MoviePy video generation
    """
    logger.info("🎬 Using OpenCV-based video generation (MoviePy replacement)")
    return video_generator.create_video_with_overlays(
        script_text=script_text,
        audio_path=audio_path,
        background_video_path=background_video_path,
        output_path=output_path
    )