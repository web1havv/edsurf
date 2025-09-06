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

from captions.caption_processor import enhance_timeline_with_captions, get_current_caption
from captions.caption_renderer import render_caption_on_frame

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
    
    def load_and_resize_image(self, image_path):
        """Load and resize image using PIL and OpenCV"""
        try:
            # Load with PIL first for better format support
            pil_img = Image.open(image_path)

            if pil_img.mode == 'RGBA':
                pass
            elif pil_img.mode == 'LA':
                pil_img = pil_img.convert('RGBA')
            else:
                pil_img = pil_img.convert('RGB')

            # Calculate target height as 40% of screen height
            target_height = int(self.video_height * 0.4)  # 40% of 1920 = 768 pixels

            # Calculate proportional width based on target height
            original_width, original_height = pil_img.size
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)
            target_size = (target_width, target_height)
            
            # Resize using PIL
            pil_img = pil_img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to OpenCV format
            img_array = np.array(pil_img)
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:
                # RGBA image - convert to BGRA for OpenCV
                cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
                logger.info(f"✅ Image loaded with alpha: {image_path} -> {target_size}")
            else:
                # RGB image - convert to BGR for OpenCV
                cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                logger.info(f"✅ Image loaded: {image_path} -> {target_size}")
            
            return cv_img
            
        except Exception as e:
            logger.error(f"❌ Failed to load image {image_path}: {str(e)}")
            # Create placeholder
            placeholder = np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
            placeholder[:] = (128, 128, 128)  # Gray
            return placeholder
    
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

        # Handle None audio_path case - create silent video
        if audio_path is None:
            logger.info("🔇 No audio provided - creating silent video")
            
            # Method 1: Use timeline duration (most reliable for our use case)
            if timeline and len(timeline) > 0:
                try:
                    max_end_time = max(segment['end_time'] for segment in timeline)
                    if max_end_time > 0:
                        logger.info(f"🔇 Silent video duration (timeline): {max_end_time:.2f}s")
                        return max_end_time
                except Exception as e:
                    logger.warning(f"⚠️ Timeline duration extraction failed: {str(e)}")
            
            # Fallback: Use default duration for silent video
            default_duration = 30.0  # 30 seconds default
            logger.info(f"🔇 Using default silent video duration: {default_duration}s")
            return default_duration
        
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
    


    def create_video_with_overlays_and_captions(self, script_text, audio_path, background_video_path=None, output_path=None, speaker_pair="trump_mrbeast", enable_captions=True, timing_data=None):

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
            from conversational_tts import create_speaker_timeline_with_timing_data
            logger.info(f"🎭 [{request_id}] TIMELINE CREATION - Using speaker_pair: {speaker_pair}")
            timeline = create_speaker_timeline_with_timing_data(script_text, speaker_pair, timing_data)
            logger.info(f"⏰ [{request_id}] Created timeline with {len(timeline)} segments")
            
            # Enhance timeline with caption data if captions are enabled
            enhanced_timeline = None
            captions = []
            if enable_captions:
                enhanced_timeline = enhance_timeline_with_captions(timeline)
                captions = enhanced_timeline['captions']
                logger.info(f"💬 [{request_id}] Enhanced timeline with {len(captions)} caption chunks")
        
            # Get audio duration (using timeline as primary source)
            audio_duration = self.get_audio_duration(audio_path, timeline)
            if audio_duration <= 0:
                raise Exception("Could not determine audio duration")
            
            total_frames = int(audio_duration * self.fps)
            logger.info(f"🎬 [{request_id}] Creating {total_frames} frames for {audio_duration:.2f}s")

            # Load speaker images
            elon_img = self.load_and_resize_image("assets/elon.png")
            trump_img = self.load_and_resize_image("assets/trump.png")
            samay_img = self.load_and_resize_image("assets/samay.png")
            baburao_img = self.load_and_resize_image("assets/baburao.png")
            arpit_img = self.load_and_resize_image("assets/arpit.png")
            mrbeast_img = self.load_and_resize_image("assets/mrbeast.png")


            logger.info(f"✅ [{request_id}] Speaker images loaded and processed")
            
            # Load background video
            background_cap, bg_duration = self.load_background_video(background_video_path or "assets/minecraft-1.mp4")
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
                
                # Determine current speaker from timeline
                current_speaker = None
                for segment in timeline:
                    if segment['start_time'] <= current_time <= segment['end_time']:
                        current_speaker = segment['speaker']
                        break

                # Enhanced smooth cross-fade transitions between speakers
                transition_time = 0.8  # Longer transition for smoother effect
                
                for segment in timeline:
                    speaker = segment['speaker']
                    segment_start = segment['start_time']
                    segment_end = segment['end_time']
                    
                    # Extend transition beyond segment boundaries
                    transition_start = segment_start - transition_time * 0.5  # Start fading in before segment
                    transition_end = segment_end + transition_time * 0.5    # Continue fading out after segment
                    
                    alpha = 0.0
                    
                    if transition_start <= current_time <= transition_end:
                        if current_time < segment_start:
                            # Pre-fade in (before segment officially starts)
                            progress = (current_time - transition_start) / (transition_time * 0.5)
                            alpha = max(0.0, min(1.0, progress))
                        elif current_time <= segment_end:
                            # Full visibility during segment
                            fade_in_progress = min(1.0, (current_time - segment_start) / (transition_time * 0.5))
                            fade_out_progress = min(1.0, (segment_end - current_time) / (transition_time * 0.5))
                            alpha = min(fade_in_progress, fade_out_progress)
                            alpha = max(0.7, alpha)  # Minimum visibility during main segment
                        else:
                            # Post-fade out (after segment officially ends)
                            progress = 1.0 - ((current_time - segment_end) / (transition_time * 0.5))
                            alpha = max(0.0, min(1.0, progress))
                
                # Add speaker overlay
                if current_speaker == 'samay':
                    img_height = samay_img.shape[0]
                    img_width = samay_img.shape[1]
                    y_pos = self.video_height - img_height  # Bottom of screen
                    x_pos = self.video_width - img_width - 50  # Right side with margin
                    self._overlay_image(bg_frame, samay_img, x_pos, y_pos)
                elif current_speaker == 'elon':
                    img_height = elon_img.shape[0]
                    img_width = elon_img.shape[1]
                    y_pos = self.video_height - img_height  # Bottom of screen
                    x_pos = self.video_width - img_width - 50  # Right side with margin
                    self._overlay_image(bg_frame, elon_img, x_pos, y_pos)
                elif current_speaker == 'trump':
                    img_height = trump_img.shape[0]
                    img_width = trump_img.shape[1]
                    y_pos = self.video_height - img_height  # Bottom of screen
                    x_pos = 50  # Left side with margin
                    self._overlay_image(bg_frame, trump_img, x_pos, y_pos)
                elif current_speaker == 'baburao':
                    img_height = baburao_img.shape[0]
                    img_width = baburao_img.shape[1]
                    y_pos = self.video_height - img_height  # Bottom of screen
                    x_pos = 50  # Left side with margin
                    self._overlay_image(bg_frame, baburao_img, x_pos, y_pos)
                elif current_speaker == 'arpit':
                    img_height = arpit_img.shape[0]
                    img_width = arpit_img.shape[1]
                    y_pos = self.video_height - img_height  # Bottom of screen
                    x_pos = 50  # Left side with margin
                    self._overlay_image(bg_frame, arpit_img, x_pos, y_pos)
                elif current_speaker == 'mrbeast':
                    img_height = mrbeast_img.shape[0]
                    img_width = mrbeast_img.shape[1]
                    y_pos = self.video_height - img_height  # Bottom of screen
                    x_pos = self.video_width - img_width - 50  # Right side with margin
                    self._overlay_image(bg_frame, mrbeast_img, x_pos, y_pos)

                
                # 🆕 ADD CAPTION OVERLAY (if enabled)
                if enable_captions and captions:
                    current_caption = get_current_caption(current_time, captions)
                    if current_caption:
                        caption_text = current_caption['text']
                        caption_speaker = current_caption['speaker']
                        bg_frame = render_caption_on_frame(bg_frame, caption_text, caption_speaker)
            

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
            
            if audio_path is None:
                # Silent video - just copy the temp video to final output
                logger.info(f"🔇 [{request_id}] Creating silent video - no audio to add")
                self._create_silent_video(temp_video_path, output_path)
            else:
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

    def _overlay_image(self, background, overlay_img, x_pos, y_pos):
        """Overlay image"""

        try:
            # Get overlay dimensions
            if len(overlay_img.shape) == 3 and overlay_img.shape[2] == 4:
                # Image has alpha channel (BGRA)
                h, w = overlay_img.shape[:2]
                has_alpha = True
                logger.debug(f"🎭 Overlaying transparent image at ({x_pos}, {y_pos})")
            else:
                # Image is opaque (BGR)
                h, w = overlay_img.shape[:2]
                has_alpha = False
                logger.debug(f"🖼️ Overlaying opaque image at ({x_pos}, {y_pos})")
            
            # Ensure position is within bounds
            x_pos = max(0, min(x_pos, self.video_width - w))
            y_pos = max(0, min(y_pos, self.video_height - h))

            # Get the region of interest from background
            roi = background[y_pos:y_pos+h, x_pos:x_pos+w]

            if has_alpha:
                # 🔧 FIX: Proper alpha blending for transparent images
                overlay_bgr = overlay_img[:, :, :3]  # BGR channels
                alpha = overlay_img[:, :, 3] / 255.0  # Alpha channel (0-1)
                
                # Create 3-channel alpha mask
                alpha_3ch = np.dstack([alpha, alpha, alpha])
                
                # Alpha blend: result = foreground * alpha + background * (1 - alpha)
                blended = (overlay_bgr * alpha_3ch + roi * (1 - alpha_3ch)).astype(np.uint8)
                
                # Update background with blended result
                background[y_pos:y_pos+h, x_pos:x_pos+w] = blended
                
            else:
                # Opaque image - direct replacement (existing behavior)
                background[y_pos:y_pos+h, x_pos:x_pos+w] = overlay_img
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to overlay image at ({x_pos}, {y_pos}): {str(e)}")
    
    def _overlay_image_with_alpha(self, background, overlay_img, mask, x_pos, y_pos, alpha):
        """Overlay image with transparency using mask and alpha blending for smooth transitions"""
        try:
            h, w = overlay_img.shape[:2]
            
            # Ensure position is within bounds
            x_pos = max(0, min(x_pos, self.video_width - w))
            y_pos = max(0, min(y_pos, self.video_height - h))
            
            # Region of interest in background
            roi = background[y_pos:y_pos+h, x_pos:x_pos+w]
            
            # Apply alpha to the overlay image
            overlay_alpha = overlay_img.astype(float) * alpha
            
            # Create alpha mask for smooth blending
            alpha_mask = (mask.astype(float) / 255.0) * alpha
            alpha_mask_3ch = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
            
            # Blend the images
            blended = roi.astype(float) * (1 - alpha_mask_3ch) + overlay_alpha * alpha_mask_3ch
            
            # Convert back to uint8
            background[y_pos:y_pos+h, x_pos:x_pos+w] = blended.astype(np.uint8)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to overlay image with alpha at ({x_pos}, {y_pos}): {str(e)}")
    
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

    def _create_silent_video(self, video_path, output_path):
        """Convert video to final format without audio using FFmpeg"""
        try:
            # Use local ffmpeg binary
            ffmpeg_path = './ffmpeg' if os.path.exists('./ffmpeg') else 'ffmpeg'
            cmd = [
                ffmpeg_path, '-y',      # Overwrite output
                '-i', video_path,       # Input video only
                '-c:v', 'libx264',      # Video codec (same as audio version)
                '-an',                  # No audio stream
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"❌ FFmpeg failed: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr}")
            
            logger.info(f"✅ Silent video created successfully with FFmpeg")
            
        except Exception as e:
            logger.error(f"❌ Failed to create silent video: {str(e)}")
            raise

# Global instance
video_generator = OpenCVVideoGenerator()

def create_background_video_with_speaker_overlays(script_text, audio_path, background_video_path=None, output_path=None, speaker_pair="trump_mrbeast", timing_data=None):
    """
    Main function to replace MoviePy video generation
    """
    logger.info("🎬 Using OpenCV-based video generation (MoviePy replacement)")


    logger.info(f"🎭 WRAPPER FUNCTION - Received speaker_pair: {speaker_pair}")
    return video_generator.create_video_with_overlays_and_captions(
        script_text=script_text,
        audio_path=audio_path,
        background_video_path=background_video_path,
        output_path=output_path,
        speaker_pair=speaker_pair,
        enable_captions=True,
        timing_data=timing_data
    )

# Add this simple test function to opencv_video_generator.py

def test_video_overlay():
    """
    Generate and test a fresh video with speaker overlays
    Creates a new video each time with current image loading (including placeholders if images missing)
    """
    import subprocess
    import platform
    from datetime import datetime
    from conversational_tts import generate_conversational_voiceover
    
    try:
        logger.info("🧪 Generating fresh video with speaker overlays...")
        
        # Create a simple test script for Elon-Trump conversation
        test_script = """You know, I've been thinking about how we can revolutionize social media and make it more efficient. 

That's fantastic, Elon! We need the best technology, the most incredible innovations. Make it huge!

Exactly. With neural interfaces and sustainable technology, we could create something unprecedented.

Absolutely tremendous! The American people deserve the best platforms, the most amazing user experience. We're going to make social media great again!"""
        
        logger.info("📝 Test script created for Elon-Trump conversation")
        logger.info(f"📄 Script length: {len(test_script)} characters")
        
        # Step 1: Generate conversational audio
        logger.info("🎵 Generating fresh conversational audio...")
        audio_path = None
        # audio_path = generate_conversational_voiceover(test_script)
        # logger.info(f"✅ Audio generated: {audio_path}")
        
        # Step 2: Create video with speaker overlays (this will use current image loading including placeholders)
        logger.info("🎬 Creating fresh video with speaker overlays...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_output_path = f"outputs/test_fresh_video_{timestamp}.mp4"
        
        # Ensure outputs directory exists (Render-compatible)
        os.makedirs("outputs", exist_ok=True)
        
        video_path = create_background_video_with_speaker_overlays(
            script_text=test_script,
            audio_path=audio_path,
            output_path=video_output_path
        )
        
        if not video_path or not os.path.exists(video_path):
            logger.error("❌ Failed to generate fresh video")
            return False
            
        file_size = os.path.getsize(video_path)
        logger.info(f"✅ Fresh video generated: {video_path}")
        logger.info(f"📊 File size: {file_size/1024/1024:.2f} MB")
        logger.info("🎭 Video includes speaker overlays (real images or placeholders if missing)")
        
        # Step 3: Open the fresh video with system default player
        system = platform.system()
        
        if system == "Darwin":  # macOS
            subprocess.run(["open", video_path])
            logger.info("🎬 Opening fresh video with macOS default player...")
            
        elif system == "Windows":
            subprocess.run(["start", video_path], shell=True)
            logger.info("🎬 Opening fresh video with Windows default player...")
            
        elif system == "Linux":
            subprocess.run(["xdg-open", video_path])
            logger.info("🎬 Opening fresh video with Linux default player...")
            
        else:
            logger.warning(f"⚠️ Unsupported system: {system}")
            logger.info(f"💡 Manually open: {video_path}")
            return False
        
        logger.info("✅ Fresh video should now be playing - check your video player!")
        logger.info("🔄 Each run generates a completely new video with current image loading")
        logger.info(f"📝 Generated video: {os.path.basename(video_path)}")
        
        # Clean up temporary audio file
        try:
            if audio_path and os.path.exists(audio_path) and audio_path != video_path:
                os.remove(audio_path)
                logger.debug(f"🗑️ Cleaned up temporary audio file: {audio_path}")
        except Exception as cleanup_error:
            logger.warning(f"⚠️ Could not clean up audio file: {cleanup_error}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate fresh video overlay: {str(e)}")
        logger.error(f"🔧 Error details: {type(e).__name__}: {e}")
        return False
