from moviepy.editor import *
import os
import tempfile
import base64
import logging
from PIL import Image, ImageOps
from datetime import datetime
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

# Speaker photos (you'll need to provide actual photo URLs or base64 data)
ELON_PHOTO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Elon_Musk_Colorado_2022_%28cropped%29.jpg/800px-Elon_Musk_Colorado_2022_%28cropped%29.jpg"
TRUMP_PHOTO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Donald_Trump_official_portrait.jpg/800px-Donald_Trump_official_portrait.jpg"

def download_speaker_photo(url, speaker_name):
    """Download speaker photo from URL"""
    try:
        logger.info(f"📸 Downloading {speaker_name} photo from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert to PIL Image
        img = Image.open(BytesIO(response.content))
        
        # Resize to standard size (1080x1080 for vertical video)
        img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
        
        # Save to temporary file
        temp_path = tempfile.mktemp(suffix=f"_{speaker_name}.png")
        img.save(temp_path, "PNG")
        
        logger.info(f"✅ {speaker_name} photo downloaded and saved: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"❌ Failed to download {speaker_name} photo: {str(e)}")
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
        
        # Download speaker photos
        elon_photo_path = download_speaker_photo(ELON_PHOTO_URL, "elon")
        trump_photo_path = download_speaker_photo(TRUMP_PHOTO_URL, "trump")
        
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
            img_clip = ImageClip(image_path).set_duration(end_time - start_time)
            img_clip = img_clip.set_start(start_time)
            
            video_clips.append(img_clip)
            logger.info(f"🎬 [{request_id}] Created clip for {speaker} from {start_time:.2f}s to {end_time:.2f}s")
        
        # Combine all video clips
        logger.info(f"🔗 [{request_id}] Combining video clips...")
        if video_clips:
            final_video = CompositeVideoClip(video_clips, size=(1080, 1080))
            final_video = final_video.set_duration(duration)
            final_video = final_video.set_audio(audio)
        else:
            logger.warning(f"⚠️ [{request_id}] No video clips created, using placeholder")
            # Create placeholder video
            placeholder_img = Image.new('RGB', (1080, 1080), color='black')
            placeholder_path = tempfile.mktemp(suffix="_placeholder.png")
            placeholder_img.save(placeholder_path, "PNG")
            
            final_video = ImageClip(placeholder_path).set_duration(duration)
            final_video = final_video.set_audio(audio)
        
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

def create_conversational_video_with_custom_photos(script_text, audio_path, modi_photo_path, trump_photo_path, output_path=None):
    """
    Create conversational video with custom photo paths
    """
    try:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🎬 [{request_id}] Starting conversational video creation with custom photos")
        
        # Override photo URLs with custom paths
        global MODI_PHOTO_URL, TRUMP_PHOTO_URL
        MODI_PHOTO_URL = modi_photo_path
        TRUMP_PHOTO_URL = trump_photo_path
        
        return create_conversational_video(script_text, audio_path, output_path)
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Failed to create conversational video with custom photos: {str(e)}")
        raise Exception(f"Failed to create conversational video with custom photos: {str(e)}") 