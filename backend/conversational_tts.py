import numpy as np
import soundfile as sf
import os
import tempfile
import logging
import re
import requests
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Voice IDs for different speakers
TRUMP_VOICE_ID = "ANHNqAseXGR3gBQps4vo"  # Current Trump voice
ELON_VOICE_ID = "5p344brGATMrJ2N3FKFT"   # Elon Musk voice from ElevenLabs

def parse_conversational_script(script_text):
    """
    Parse a conversational script and separate it into alternating speakers
    Returns a list of tuples: [(speaker, text), (speaker, text), ...]
    """
    try:
        logger.info("🔍 Parsing conversational script for speaker separation")
        logger.info(f"📝 Script length: {len(script_text)} characters")
        
        # Split by sentences and alternate speakers
        sentences = re.split(r'[.!?]+', script_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Combine sentences into longer segments (6-8 total segments)
        target_segments = 6  # Aim for 6 segments total
        sentences_per_segment = max(1, len(sentences) // target_segments)
        
        # Alternate between speakers (Elon starts first)
        speakers = []
        current_speaker = "elon"
        current_segment = ""
        segment_count = 0
        
        for i, sentence in enumerate(sentences):
            if sentence:
                current_segment += sentence + ". "
                
                # Create a segment when we have enough sentences or reach the end
                if (len(current_segment.strip()) > 50 and 
                    (i + 1) % sentences_per_segment == 0) or i == len(sentences) - 1:
                    
                    if current_segment.strip():
                        speakers.append((current_speaker, current_segment.strip()))
                        segment_count += 1
                        # Switch speaker
                        current_speaker = "trump" if current_speaker == "elon" else "elon"
                        current_segment = ""
        
        # If we still have too many segments, combine some
        if len(speakers) > 8:
            combined_speakers = []
            for i in range(0, len(speakers), 2):
                if i + 1 < len(speakers):
                    # Combine two segments from the same speaker
                    combined_text = speakers[i][1] + " " + speakers[i+1][1]
                    combined_speakers.append((speakers[i][0], combined_text))
                else:
                    combined_speakers.append(speakers[i])
            speakers = combined_speakers
        
        logger.info(f"✅ Parsed script into {len(speakers)} speaker segments")
        logger.debug(f"📝 Speaker breakdown: {speakers[:3]}...")  # Show first 3 segments
        
        return speakers
    except Exception as e:
        logger.error(f"❌ Failed to parse conversational script: {str(e)}")
        raise Exception(f"Failed to parse conversational script: {str(e)}")

def generate_elevenlabs_voice_segment(text, voice_id, output_path):
    """Generate voice segment using ElevenLabs API"""
    try:
        logger.info(f"🎤 Generating voice segment with voice ID: {voice_id}")
        logger.info(f"📝 Text: {text[:50]}...")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.getenv("ELEVENLABS_API_KEY", "")
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        logger.info("🌐 Sending request to ElevenLabs API...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ Voice segment generated successfully")
            logger.info(f"📊 File size: {file_size} bytes")
            return True
        else:
            logger.warning(f"⚠️ ElevenLabs failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ElevenLabs error: {str(e)}")
        return False

def batch_generate_elevenlabs_voice_segments(segments_data, output_dir):
    """
    Batch generate multiple voice segments using ElevenLabs API with better error handling
    segments_data: list of (text, voice_id, output_filename) tuples
    """
    try:
        logger.info(f"🎤 Batch generating {len(segments_data)} voice segments")
        
        # Process in smaller batches to avoid rate limits
        batch_size = 3  # Process 3 segments at a time
        successful_segments = []
        
        for i in range(0, len(segments_data), batch_size):
            batch = segments_data[i:i + batch_size]
            logger.info(f"🎤 Processing batch {i//batch_size + 1}/{(len(segments_data) + batch_size - 1)//batch_size}")
            
            for j, (text, voice_id, filename) in enumerate(batch):
                segment_index = i + j
                output_path = os.path.join(output_dir, filename)
                
                logger.info(f"🎤 Generating segment {segment_index + 1}/{len(segments_data)} with voice ID: {voice_id}")
                logger.info(f"📝 Text: {text[:50]}...")
                
                # Make API request
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": os.getenv("ELEVENLABS_API_KEY", "")
                }
                
                data = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
                
                try:
                    logger.info("🌐 Sending request to ElevenLabs API...")
                    response = requests.post(url, json=data, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        
                        file_size = os.path.getsize(output_path)
                        logger.info(f"✅ Voice segment generated successfully")
                        logger.info(f"📊 File size: {file_size} bytes")
                        
                        # Extract speaker from filename
                        speaker = "elon" if "elon" in filename else "trump"
                        successful_segments.append((speaker, output_path))
                        
                    elif response.status_code == 401:
                        error_data = response.json()
                        if "quota_exceeded" in str(error_data):
                            logger.error(f"❌ ElevenLabs quota exceeded: {error_data}")
                            logger.error("💡 Consider upgrading your ElevenLabs plan or using a different API key")
                            break
                        else:
                            logger.warning(f"⚠️ ElevenLabs authentication failed: {response.status_code} - {response.text}")
                            continue
                            
                    elif response.status_code == 429:
                        logger.warning(f"⚠️ Rate limit hit, waiting 2 seconds...")
                        import time
                        time.sleep(2)
                        continue
                        
                    else:
                        logger.warning(f"⚠️ ElevenLabs failed: {response.status_code} - {response.text}")
                        continue
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"⚠️ Request timeout for segment {segment_index + 1}, retrying...")
                    import time
                    time.sleep(1)
                    continue
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate segment {segment_index + 1}: {str(e)}")
                    continue
                
                # Small delay between requests to be respectful
                import time
                time.sleep(0.5)
            
            # Delay between batches
            if i + batch_size < len(segments_data):
                logger.info("⏳ Waiting 1 second between batches...")
                import time
                time.sleep(1)
        
        logger.info(f"✅ Successfully generated {len(successful_segments)} out of {len(segments_data)} segments")
        return successful_segments
        
    except Exception as e:
        logger.error(f"❌ Failed to batch generate voice segments: {str(e)}")
        return []

def combine_audio_segments(segments, output_path):
    """
    Combine multiple audio segments into one file using ffmpeg
    segments: list of (speaker, audio_path) tuples
    """
    try:
        logger.info(f"🔗 Combining {len(segments)} audio segments")
        
        # Create a temporary file list for ffmpeg
        file_list_path = tempfile.mktemp(suffix=".txt")
        
        with open(file_list_path, 'w') as f:
            for speaker, audio_path in segments:
                if os.path.exists(audio_path):
                    # Escape the path for ffmpeg
                    escaped_path = audio_path.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
        
        # Use ffmpeg to concatenate all audio files
        import subprocess
        
        cmd = [
            './ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list_path,
            '-c', 'copy',
            output_path,
            '-y'  # Overwrite output file
        ]
        
        logger.info(f"🎵 Running ffmpeg command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ Audio segments combined successfully using ffmpeg")
            logger.info(f"📊 Combined file size: {file_size} bytes")
            
            # Clean up temporary file list
            try:
                os.remove(file_list_path)
            except:
                pass
                
            return True
        else:
            logger.error(f"❌ ffmpeg failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to combine audio segments: {str(e)}")
        return False

def generate_conversational_voiceover(script_text, output_path=None):
    """
    Generate conversational audio with alternating speakers (optimized version)
    """
    try:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🎵 [{request_id}] Starting optimized conversational voiceover generation")
        logger.info(f"📝 [{request_id}] Script length: {len(script_text)} characters")
        
        if not output_path:
            output_path = tempfile.mktemp(suffix=".wav")
            logger.info(f"📁 [{request_id}] Using temporary output path: {output_path}")
        
        # Parse script into speaker segments
        logger.info(f"🔍 [{request_id}] Parsing script for speaker separation...")
        speaker_segments = parse_conversational_script(script_text)
        
        # Prepare batch data for ElevenLabs
        logger.info(f"🎤 [{request_id}] Preparing batch requests for ElevenLabs...")
        batch_data = []
        
        for i, (speaker, text) in enumerate(speaker_segments):
            voice_id = ELON_VOICE_ID if speaker == "elon" else TRUMP_VOICE_ID
            filename = f"segment_{i+1}_{speaker}.wav"
            batch_data.append((text, voice_id, filename))
        
        # Create temporary directory for segments
        temp_dir = tempfile.mkdtemp()
        logger.info(f"📁 [{request_id}] Using temporary directory: {temp_dir}")
        
        # Batch generate all voice segments
        audio_segments = batch_generate_elevenlabs_voice_segments(batch_data, temp_dir)
        
        if not audio_segments:
            logger.error(f"❌ [{request_id}] No audio segments were generated successfully")
            raise Exception("No audio segments were generated")
        
        # Combine all segments
        logger.info(f"🔗 [{request_id}] Combining {len(audio_segments)} audio segments...")
        if combine_audio_segments(audio_segments, output_path):
            logger.info(f"✅ [{request_id}] Conversational voiceover generated successfully")
            
            # Clean up temporary segment files
            for speaker, segment_path in audio_segments:
                try:
                    os.remove(segment_path)
                    logger.debug(f"🗑️ [{request_id}] Removed temporary segment: {segment_path}")
                except Exception as e:
                    logger.warning(f"⚠️ [{request_id}] Failed to remove temporary file {segment_path}: {str(e)}")
            
            # Clean up temporary directory
            try:
                import shutil
                shutil.rmtree(temp_dir)
                logger.debug(f"🗑️ [{request_id}] Removed temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"⚠️ [{request_id}] Failed to remove temporary directory {temp_dir}: {str(e)}")
            
            return output_path
        else:
            raise Exception("Failed to combine audio segments")
            
    except Exception as e:
        logger.error(f"❌ [{request_id}] Failed to generate conversational voiceover: {str(e)}")
        logger.error(f"❌ [{request_id}] Error type: {type(e).__name__}")
        raise Exception(f"Failed to generate conversational voiceover: {str(e)}")

def create_speaker_timeline(script_text):
    """
    Create a timeline of when each speaker is talking
    Returns list of (speaker, start_time, end_time, text) tuples
    """
    try:
        logger.info("⏰ Creating speaker timeline")
        
        # Parse script into speaker segments
        speaker_segments = parse_conversational_script(script_text)
        
        timeline = []
        current_time = 0.0
        
        for speaker, text in speaker_segments:
            # Estimate duration (roughly 0.5 seconds per word)
            word_count = len(text.split())
            duration = word_count * 0.5
            
            timeline.append({
                'speaker': speaker,
                'start_time': current_time,
                'end_time': current_time + duration,
                'text': text
            })
            
            current_time += duration + 0.2  # Add 0.2s pause between speakers
        
        logger.info(f"✅ Created timeline with {len(timeline)} segments")
        return timeline
        
    except Exception as e:
        logger.error(f"❌ Failed to create speaker timeline: {str(e)}")
        raise Exception(f"Failed to create speaker timeline: {str(e)}") 