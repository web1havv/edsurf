from moviepy import (
    AudioFileClip, 
    ImageClip, 
    CompositeVideoClip, 
    VideoFileClip, 
    concatenate_videoclips, 
    VideoClip
)
import os
import tempfile
import base64
import logging
from PIL import Image, ImageOps, ImageDraw
from datetime import datetime
import requests
from io import BytesIO
import numpy as np

# Import our MoviePy compatibility layer
from moviepy_compat import (
    safe_resize, 
    safe_set_duration, 
    safe_set_start, 
    safe_set_position, 
    safe_set_audio
)

logger = logging.getLogger(__name__)

# Speaker photos - using local files
ELON_PHOTO_PATH = "../63b84b16d1c5130019f95f8c.webp"
TRUMP_PHOTO_PATH = "../trump-removebg-preview.png"

# Background video - using Minecraft video
MINECRAFT_BACKGROUND_PATH = "../minecraft-1.mp4"

def load_speaker_photo(speaker_name):
    """Load speaker photo from local file"""
    try:
        if speaker_name == "elon":
            photo_path = ELON_PHOTO_PATH
        elif speaker_name == "trump":
            photo_path = TRUMP_PHOTO_PATH
        else:
            raise ValueError(f"Unknown speaker: {speaker_name}")
        
        logger.info(f"📸 Loading {speaker_name} photo from: {photo_path}")
        
        if not os.path.exists(photo_path):
            logger.error(f"❌ Photo file not found: {photo_path}")
            raise FileNotFoundError(f"Photo file not found: {photo_path}")
        
        # Load image
        img = Image.open(photo_path)
        
        # Convert to RGB if needed (for webp files)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to standard size (1080x1080 for vertical video)
        img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
        
        # Save to temporary file
        temp_path = tempfile.mktemp(suffix=f"_{speaker_name}.png")
        img.save(temp_path, "PNG")
        
        logger.info(f"✅ {speaker_name} photo loaded and saved: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"❌ Failed to load {speaker_name} photo: {str(e)}")
        # Create a placeholder image
        placeholder = Image.new('RGB', (1080, 1080), color='gray')
        temp_path = tempfile.mktemp(suffix=f"_{speaker_name}_placeholder.png")
        placeholder.save(temp_path, "PNG")
        logger.info(f"📸 Created placeholder for {speaker_name}")
        return temp_path

def create_speaker_clips(timeline, audio_path):
    """
    Create video clips for each speaker based on timeline
    Returns list of (start_time, end_time, speaker, image_path) tuples
    """
    try:
        logger.info("🎬 Creating speaker clips from timeline")
        
        # Load speaker photos from local files
        elon_photo_path = load_speaker_photo("elon")
        trump_photo_path = load_speaker_photo("trump")
        
        speaker_photos = {
            "elon": elon_photo_path,
            "trump": trump_photo_path
        }
        
        clips = []
        for segment in timeline:
            speaker = segment['speaker']
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            if speaker in speaker_photos:
                clips.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'speaker': speaker,
                    'image_path': speaker_photos[speaker]
                })
        
        logger.info(f"✅ Created {len(clips)} speaker clips")
        return clips
        
    except Exception as e:
        logger.error(f"❌ Failed to create speaker clips: {str(e)}")
        raise Exception(f"Failed to create speaker clips: {str(e)}")

def create_conversational_video(script_text, audio_path, output_path=None):
    """
    Create a conversational video with speaker photos appearing when they speak
    """
    try:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🎬 [{request_id}] Starting conversational video creation")
        logger.info(f"📝 [{request_id}] Script length: {len(script_text)} characters")
        logger.info(f"🎵 [{request_id}] Audio path: {audio_path}")
        
        if not output_path:
            output_path = tempfile.mktemp(suffix=".mp4")
            logger.info(f"📁 [{request_id}] Using temporary output path: {output_path}")
        
        # Import the conversational TTS module to get timeline
        from conversational_tts import create_speaker_timeline
        
        # Create speaker timeline
        logger.info(f"⏰ [{request_id}] Creating speaker timeline...")
        timeline = create_speaker_timeline(script_text)
        
        # Create speaker clips
        logger.info(f"🎬 [{request_id}] Creating speaker clips...")
        speaker_clips = create_speaker_clips(timeline, audio_path)
        
        # Load audio
        logger.info(f"🎵 [{request_id}] Loading audio file...")
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        logger.info(f"🎵 [{request_id}] Audio loaded, duration: {duration:.2f}s")
        
        # Create video clips for each speaker segment
        logger.info(f"🎬 [{request_id}] Creating video clips for each speaker...")
        video_clips = []
        
        for clip_info in speaker_clips:
            start_time = clip_info['start_time']
            end_time = clip_info['end_time']
            speaker = clip_info['speaker']
            image_path = clip_info['image_path']
            
            # Create image clip for this time period
            img_clip = ImageClip(image_path)
            img_clip = safe_set_duration(img_clip, end_time - start_time)
            img_clip = safe_set_start(img_clip, start_time)
            
            video_clips.append(img_clip)
            logger.info(f"🎬 [{request_id}] Created clip for {speaker} from {start_time:.2f}s to {end_time:.2f}s")
        
        # Combine all video clips
        logger.info(f"🔗 [{request_id}] Combining video clips...")
        if video_clips:
            final_video = CompositeVideoClip(video_clips, size=(1080, 1080))
            final_video = safe_set_duration(final_video, duration)
            final_video = safe_set_audio(final_video, audio)
        else:
            logger.warning(f"⚠️ [{request_id}] No video clips created, using placeholder")
            # Create placeholder video
            placeholder_img = Image.new('RGB', (1080, 1080), color='black')
            placeholder_path = tempfile.mktemp(suffix="_placeholder.png")
            placeholder_img.save(placeholder_path, "PNG")
            
            final_video = ImageClip(placeholder_path)
            final_video = safe_set_duration(final_video, duration)
            final_video = safe_set_audio(final_video, audio)
        
        # Write video file
        logger.info(f"💾 [{request_id}] Writing video to: {output_path}")
        logger.info(f"🎬 [{request_id}] Video encoding settings: fps=30, codec=libx264, audio_codec=aac")
        
        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Check if video was created successfully
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ [{request_id}] Video file created successfully: {output_path}")
            logger.info(f"📊 [{request_id}] Video file size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        else:
            logger.error(f"❌ [{request_id}] Video file was not created: {output_path}")
            raise Exception("Video file was not created")
        
        # Clean up temporary files
        logger.info(f"🧹 [{request_id}] Cleaning up temporary files...")
        for clip_info in speaker_clips:
            try:
                os.remove(clip_info['image_path'])
                logger.debug(f"🗑️ [{request_id}] Removed temporary file: {clip_info['image_path']}")
            except Exception as e:
                logger.warning(f"⚠️ [{request_id}] Failed to remove temporary file {clip_info['image_path']}: {str(e)}")
        
        logger.info(f"✅ [{request_id}] Conversational video creation completed successfully!")
        return output_path
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Failed to create conversational video: {str(e)}")
        logger.error(f"❌ [{request_id}] Error type: {type(e).__name__}")
        raise Exception(f"Failed to create conversational video: {str(e)}")

def create_conversational_video_with_custom_photos(script_text, audio_path, elon_photo_path, trump_photo_path, output_path=None):
    """
    Create conversational video with custom photo paths
    """
    try:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🎬 [{request_id}] Starting conversational video creation with custom photos")
        
        # Override photo paths with custom paths
        global ELON_PHOTO_PATH, TRUMP_PHOTO_PATH
        ELON_PHOTO_PATH = elon_photo_path
        TRUMP_PHOTO_PATH = trump_photo_path
        
        return create_conversational_video(script_text, audio_path, output_path)
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Failed to create conversational video with custom photos: {str(e)}")
        raise Exception(f"Failed to create conversational video with custom photos: {str(e)}")

def create_background_video_with_speaker_overlays(script_text, audio_path, background_video_path=None, output_path=None):
    """
    Create video with background video and small speaker images that pop up when speaking
    - Background video runs continuously
    - Trump image appears small on the left when Trump speaks
    - Elon image appears small on the right when Elon speaks
    - Images are small and don't cover the full screen
    """
    try:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🎬 [{request_id}] Starting background video with speaker overlays creation")
        logger.info(f"📝 [{request_id}] Script length: {len(script_text)} characters")
        logger.info(f"🎵 [{request_id}] Audio path: {audio_path}")
        
        if not output_path:
            output_path = tempfile.mktemp(suffix=".mp4")
            logger.info(f"📁 [{request_id}] Using temporary output path: {output_path}")
        
        # Import the conversational TTS module to get timeline
        from conversational_tts import create_speaker_timeline
        
        # Check Minecraft background video
        check_minecraft_background()
        
        # Create speaker timeline
        logger.info(f"⏰ [{request_id}] Creating speaker timeline...")
        timeline = create_speaker_timeline(script_text)
        
        # Load speaker photos from local files
        logger.info(f"📸 [{request_id}] Loading speaker photos from local files...")
        elon_photo_path = load_speaker_photo("elon")
        trump_photo_path = load_speaker_photo("trump")
        
        # Load audio
        logger.info(f"🎵 [{request_id}] Loading audio file...")
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        logger.info(f"🎵 [{request_id}] Audio loaded, duration: {duration:.2f}s")
        
        # Create or use background video
        if background_video_path and os.path.exists(background_video_path):
            logger.info(f"🎬 [{request_id}] Using provided background video: {background_video_path}")
            background_video = VideoFileClip(background_video_path)
            # Loop background video if it's shorter than audio duration
            if background_video.duration < duration:
                loops_needed = int(duration / background_video.duration) + 1
                background_video = concatenate_videoclips([background_video] * loops_needed)
            background_video = safe_set_duration(background_video, duration)
        elif os.path.exists(MINECRAFT_BACKGROUND_PATH):
            logger.info(f"🎬 [{request_id}] Using Minecraft background video: {MINECRAFT_BACKGROUND_PATH}")
            background_video = VideoFileClip(MINECRAFT_BACKGROUND_PATH)
            # Loop background video if it's shorter than audio duration
            if background_video.duration < duration:
                loops_needed = int(duration / background_video.duration) + 1
                background_video = concatenate_videoclips([background_video] * loops_needed)
            background_video = safe_set_duration(background_video, duration)
        else:
            logger.info(f"🎬 [{request_id}] Creating animated background video")
            # Create animated background (gradient animation)
            background_video = create_animated_background(duration)
        
        # Resize background video to 1080x1920 (vertical format)
        background_video = safe_resize(background_video, (1080, 1920))
        
        # Create speaker overlay clips
        logger.info(f"🎬 [{request_id}] Creating speaker overlay clips...")
        overlay_clips = []
        
        for segment in timeline:
            start_time = segment['start_time']
            end_time = segment['end_time']
            speaker = segment['speaker']
            
            # Choose photo based on speaker
            if speaker == 'trump':
                photo_path = trump_photo_path
                position = 'left'  # Trump on left
            elif speaker == 'elon':
                photo_path = elon_photo_path
                position = 'right'  # Elon on right
            else:
                continue  # Skip unknown speakers
            
            # Create small speaker image clip
            speaker_clip = create_small_speaker_overlay(photo_path, position, end_time - start_time)
            speaker_clip = safe_set_start(speaker_clip, start_time)
            overlay_clips.append(speaker_clip)
            
            logger.info(f"🎬 [{request_id}] Created overlay for {speaker} on {position} from {start_time:.2f}s to {end_time:.2f}s")
        
        # Combine background video with overlays
        logger.info(f"🔗 [{request_id}] Combining background video with overlays...")
        final_video = CompositeVideoClip([background_video] + overlay_clips, size=(1080, 1920))
        final_video = safe_set_duration(final_video, duration)
        final_video = safe_set_audio(final_video, audio)
        
        # Write video file
        logger.info(f"💾 [{request_id}] Writing video to: {output_path}")
        logger.info(f"🎬 [{request_id}] Video encoding settings: fps=30, codec=libx264, audio_codec=aac")
        
        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Check if video was created successfully
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ [{request_id}] Video file created successfully: {output_path}")
            logger.info(f"📊 [{request_id}] Video file size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        else:
            logger.error(f"❌ [{request_id}] Video file was not created: {output_path}")
            raise Exception("Video file was not created")
        
        # Clean up temporary files
        logger.info(f"🧹 [{request_id}] Cleaning up temporary files...")
        try:
            os.remove(elon_photo_path)
            os.remove(trump_photo_path)
            logger.debug(f"🗑️ [{request_id}] Removed temporary photo files")
        except Exception as e:
            logger.warning(f"⚠️ [{request_id}] Failed to remove temporary files: {str(e)}")
        
        logger.info(f"✅ [{request_id}] Background video with speaker overlays creation completed successfully!")
        return output_path
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Failed to create background video with speaker overlays: {str(e)}")
        logger.error(f"❌ [{request_id}] Error type: {type(e).__name__}")
        raise Exception(f"Failed to create background video with speaker overlays: {str(e)}")

def create_small_speaker_overlay(photo_path, position, duration):
    """
    Create a small speaker overlay image clip
    - position: 'left' for Trump, 'right' for Elon
    - Returns a small image clip positioned on the side
    """
    try:
        # Load and resize speaker photo to small size
        img = Image.open(photo_path)
        
        # Make it small (200x200 pixels)
        small_size = (200, 200)
        img = img.resize(small_size, Image.Resampling.LANCZOS)
        
        # Create circular mask for rounded corners
        mask = Image.new('L', small_size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, small_size[0], small_size[1]), fill=255)
        
        # Apply mask to image
        output = Image.new('RGBA', small_size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        # Save to temporary file
        temp_path = tempfile.mktemp(suffix="_small_speaker.png")
        output.save(temp_path, "PNG")
        
        # Create video clip
        clip = ImageClip(temp_path)
        clip = safe_set_duration(clip, duration)
        
        # Position the clip
        if position == 'left':
            # Position on left side, 100px from left edge, 200px from top
            clip = safe_set_position(clip, (100, 200))
        else:  # right
            # Position on right side, 780px from left edge (1080-200-100), 200px from top
            clip = safe_set_position(clip, (780, 200))
        
        return clip
        
    except Exception as e:
        logger.error(f"❌ Failed to create small speaker overlay: {str(e)}")
        # Create placeholder
        placeholder = Image.new('RGB', (200, 200), color='gray')
        temp_path = tempfile.mktemp(suffix="_placeholder_small.png")
        placeholder.save(temp_path, "PNG")
        
        clip = ImageClip(temp_path)
        clip = safe_set_duration(clip, duration)
        if position == 'left':
            clip = safe_set_position(clip, (100, 200))
        else:
            clip = safe_set_position(clip, (780, 200))
        
        return clip

def create_animated_background(duration):
    """
    Create an animated background video with gradient animation
    """
    try:
        # Create animated gradient background
        def make_frame(t):
            # Create gradient animation
            frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
            
            # Animate gradient colors
            hue = (t * 30) % 360  # Rotate through colors
            r = int(128 + 127 * np.sin(hue * np.pi / 180))
            g = int(128 + 127 * np.sin((hue + 120) * np.pi / 180))
            b = int(128 + 127 * np.sin((hue + 240) * np.pi / 180))
            
            # Create gradient from top to bottom
            for y in range(1920):
                intensity = 1 - (y / 1920)
                frame[y, :, 0] = int(r * intensity)
                frame[y, :, 1] = int(g * intensity)
                frame[y, :, 2] = int(b * intensity)
            
            return frame
        
        # Create video clip
        background = VideoClip(make_frame, duration=duration)
        return background
        
    except Exception as e:
        logger.error(f"❌ Failed to create animated background: {str(e)}")
        # Create simple solid color background
        def make_frame(t):
            frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
            frame[:, :, 0] = 50   # Dark blue
            frame[:, :, 1] = 50
            frame[:, :, 2] = 150
            return frame
        
        background = VideoClip(make_frame, duration=duration)
        return background

def check_minecraft_background():
    """
    Check if Minecraft background video exists and log status
    """
    try:
        if os.path.exists(MINECRAFT_BACKGROUND_PATH):
            file_size = os.path.getsize(MINECRAFT_BACKGROUND_PATH)
            logger.info(f"✅ Minecraft background video found: {MINECRAFT_BACKGROUND_PATH}")
            logger.info(f"📊 File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
            return True
        else:
            logger.warning(f"⚠️ Minecraft background video not found: {MINECRAFT_BACKGROUND_PATH}")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking Minecraft background: {str(e)}")
        return False 