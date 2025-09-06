import numpy as np
import soundfile as sf
import os
import tempfile
import logging
import re
import requests
import subprocess
import shutil
from datetime import datetime
import json, base64

logger = logging.getLogger(__name__)

def check_ffmpeg_availability():
    """Check if FFmpeg is available and log the version"""
    try:
        # Try system ffmpeg first
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"✅ System FFmpeg available: {version_line}")
            return 'ffmpeg'
    except Exception as e:
        logger.warning(f"⚠️ System FFmpeg not available: {str(e)}")
    
    try:
        # Try local ffmpeg binary
        if os.path.exists('./ffmpeg') and os.access('./ffmpeg', os.X_OK):
            result = subprocess.run(['./ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                logger.info(f"✅ Local FFmpeg available: {version_line}")
                return './ffmpeg'
    except Exception as e:
        logger.warning(f"⚠️ Local FFmpeg not available: {str(e)}")
    
    logger.error("❌ No FFmpeg binary found! Audio processing will fail.")
    return None

# ————————————————————————————————————————————————————————————————
# Hindi → English-phonetic preprocessor for better TTS pronunciation
# Applies only to Samay/Arpit content where Hindi words must sound authentic
# Keeps English words intact; rewrites common Hindi words to phonetic spellings
# Add/adjust mappings as needed based on listening tests
def apply_hindi_phonetics(raw_text: str) -> str:
    try:
        text = raw_text
        # Minimal, high-signal rules. Keep English words intact. Nudge Hindi words.
        rules = {
            r"\bye\b": "yeh",
            r"\bmain\b": "mein",
            r"\bnahi\b": "nahee",
            r"\bnahin\b": "naheen",
            r"\bdimag\b": "dimaag",
            r"\bbhai\b": "bhaai",
            r"\bmadarchod\b": "maadarchod",
            r"\bgandu\b": "gaandu",
            r"\bbhosdike\b": "bhosdike",
            r"\bchutiya\b": "chutiya",
            r"\blund\b": "lund",
            r"\bchut\b": "chut",
        }
        for pattern, repl in rules.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text
    except Exception:
        return raw_text

# Speaker Configuration with Multiple API Keys and Voice IDs
SPEAKER_CONFIG = {
    "trump": {
        "voice_id": "QiOhBK5MwP4D5C5CJeuJ",  # Trump voice from ElevenLabs
        "api_key_env": "ELEVENLABS_API_KEY_TRUMP",  # Separate API key for Trump
        "fallback_api_key_env": "ELEVENLABS_API_KEY"  # Fallback to main key
    },
    "elon": {
        "voice_id": "uTsZKELdeD1KQZz4M45o",   # Elon Musk voice from ElevenLabs
        "api_key_env": "ELEVENLABS_API_KEY_ELON",   # Separate API key for Elon
        "fallback_api_key_env": "ELEVENLABS_API_KEY"  # Fallback to main key
    },
    "samay": {
        "voice_id": "RMR2Ot6xWMuSGGQU6bbx",  # Correct Samay Raina voice ID
        "api_key_env": "ELEVENLABS_API_KEY_SAMAY_ARPIT",  # API key for Samay & Arpit
        "fallback_api_key_env": "ELEVENLABS_API_KEY"  # Fallback to main key
    },
    "baburao": {
        "voice_id": "o76izsJbtLZKHDxpMquz",  # Baburao voice ID
        "api_key_env": "ELEVENLABS_API_KEY_BABURAO_SAMAY",  # New API key for Baburao & Samay
        "fallback_api_key_env": "ELEVENLABS_API_KEY"  # Fallback to main key
    },
    "arpit": {
        "voice_id": "rz6PPOBEqHlbITNfwIgo",  # Arpit Bala voice ID
        "api_key_env": "ELEVENLABS_API_KEY_SAMAY_ARPIT",  # New API key for Samay & Arpit
        "fallback_api_key_env": "ELEVENLABS_API_KEY"  # Fallback to main key
    },
    "mrbeast": {
        "voice_id": "frBOG9T06d0Zw1PEvoZN",  # MrBeast voice ID
        "api_key_env": "ELEVENLABS_API_KEY_TRUMP_MRBEAST",  # API key for Trump & MrBeast
        "fallback_api_key_env": "ELEVENLABS_API_KEY"  # Fallback to main key
    }
}

# Speaker Pair Configurations for Frontend
SPEAKER_PAIRS = {
    "trump_elon": {
        "name": "Trump & Elon",
        "speakers": ["elon", "trump"],  # Fixed: Elon speaks first to match script generation
        "description": "Political discussions with tech innovation"
    },
    "baburao_samay": {
        "name": "Baburao & Samay",
        "speakers": ["baburao", "samay"], 
        "description": "Comedy legend meets chess master insights"
    },
    "samay_arpit": {
        "name": "Samay & Arpit",
        "speakers": ["samay", "arpit"],
        "description": "Chess master meets comedy king with adult humor"
    },
    "trump_mrbeast": {
        "name": "Trump & MrBeast",
        "speakers": ["trump", "mrbeast"],
        "description": "Political discussions with philanthropy and entertainment"
    }
}

# Legacy voice IDs for backward compatibility
TRUMP_VOICE_ID = SPEAKER_CONFIG["trump"]["voice_id"]
ELON_VOICE_ID = SPEAKER_CONFIG["elon"]["voice_id"]

def parse_conversational_script(script_text, speaker_pair="trump_mrbeast"):
    """
    Parse a conversational script and separate it into speakers
    Supports both explicit speaker format (**Speaker:** text) and auto-alternating
    
    Args:
        script_text: The text to parse
        speaker_pair: Key from SPEAKER_PAIRS (e.g., "trump_elon", "baburao_samay", "samay_arpit")
    
    Returns a list of tuples: [(speaker, text), (speaker, text), ...]
    """
    try:
        logger.info("🔍 Parsing conversational script for speaker separation")
        logger.info(f"📝 Script length: {len(script_text)} characters")
        
        # Check if script has explicit speaker markers (e.g., **Trump:** format)
        speaker_pattern = r'\*\*([^*]+):\*\*\s*([^*]+?)(?=\*\*[^*]+:\*\*|\Z)'
        explicit_speakers = re.findall(speaker_pattern, script_text, re.DOTALL)
        
        if explicit_speakers:
            logger.info("📢 Found explicit speaker markers in script")
            speakers = []
            for speaker_name, text in explicit_speakers:
                # Normalize speaker names to lowercase for consistency
                speaker_name = speaker_name.lower().strip()
                text = text.strip()
                
                if text:  # Only add non-empty text
                    speakers.append((speaker_name, text))
                    logger.info(f"   📝 {speaker_name}: {len(text)} characters")
            
            logger.info(f"✅ Parsed script into {len(speakers)} explicit speaker segments")
            return speakers
        
        # Fallback to auto-alternating system for scripts without explicit speakers
        logger.info("🔄 No explicit speakers found, using auto-alternating system")
        
        # Split by double line breaks first (for paragraph-style segments)
        paragraphs = [p.strip() for p in script_text.split('\n\n') if p.strip()]
        
        if paragraphs and len(paragraphs) >= 2:
            # Use paragraph-based splitting for better segment control
            logger.info(f"📝 Found {len(paragraphs)} dialogue paragraphs")
            segments = paragraphs
        else:
            # Fallback: split by sentences and alternate speakers  
            segments = re.split(r'[.!?]+', script_text)
            segments = [s.strip() for s in segments if s.strip()]
            logger.info(f"📝 Using sentence-based splitting: {len(segments)} segments")
        
        # Combine into longer segments if needed (6-8 total segments)
        target_segments = 6  # Aim for 6 segments total
        if len(segments) > target_segments * 2:
            # Too many segments, combine them
            segments_per_chunk = max(1, len(segments) // target_segments)
        else:
            segments_per_chunk = 1
        
        # Alternate between speakers from selected pair
        speakers = []
        if speaker_pair in SPEAKER_PAIRS:
            pair_speakers = SPEAKER_PAIRS[speaker_pair]["speakers"]
        else:
            # Fallback to trump-elon
            pair_speakers = ["elon", "trump"]  # Fixed fallback order too
            logger.warning(f"Unknown speaker pair '{speaker_pair}', using elon-trump")
        
        logger.info(f"🎭 SPEAKER ASSIGNMENT DEBUG for {speaker_pair}:")
        logger.info(f"🎭 - Speaker order: {pair_speakers}")
        logger.info(f"🎭 - First speaker will be: {pair_speakers[0]}")
        logger.info(f"🎭 - Second speaker will be: {pair_speakers[1]}")
        
        current_speaker = pair_speakers[0]
        current_segment = ""
        segment_count = 0
        
        for i, segment in enumerate(segments):
            if segment:
                current_segment += segment + " "
                
                # Create a segment when we have enough content or reach the end
                if (len(current_segment.strip()) > 50 and 
                    (i + 1) % segments_per_chunk == 0) or i == len(segments) - 1:
                    
                    if current_segment.strip():
                        speakers.append((current_speaker, current_segment.strip()))
                        segment_count += 1
                        logger.info(f"🎭 Segment {segment_count}: {current_speaker} -> '{current_segment.strip()[:50]}...'")
                        # Switch to next speaker in pair
                        current_index = pair_speakers.index(current_speaker)
                        next_index = (current_index + 1) % len(pair_speakers)
                        current_speaker = pair_speakers[next_index]
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

def get_api_key_for_speaker(speaker_name):
    """Get the appropriate API key for a specific speaker"""
    try:
        # Special handling for Baburao with specific API key
        if speaker_name == "baburao":
            # Use the specific API key for Baburao
            new_api_key = "sk_f800d01dcf584b4a637e0363c12430d7c5f32a6289b0785f"
            logger.info(f"🔑 Using Baburao ElevenLabs API key for {speaker_name}")
            return new_api_key
        
        # Special handling for Samay & Arpit with correct API key
        if speaker_name in ["samay", "arpit"]:
            # Use the correct API key for Samay & Arpit
            new_api_key = "sk_bb59a7b4c0fd35a30feb318885007b58558e2c366a64d687"
            logger.info(f"🔑 Using correct ElevenLabs API key for {speaker_name}")
            return new_api_key
        
        # Special handling for Trump & MrBeast with specific API key
        if speaker_name in ["trump", "mrbeast"]:
            # Use the provided API key for Trump & MrBeast
            trump_mrbeast_api_key = "sk_94096d8a0eef902dccfb2c9e5c371ee0b30730f49e7bae63"
            logger.info(f"🔑 Using Trump & MrBeast ElevenLabs API key for {speaker_name}")
            return trump_mrbeast_api_key
        
        if speaker_name in SPEAKER_CONFIG:
            config = SPEAKER_CONFIG[speaker_name]
            # Try speaker-specific API key first
            api_key = os.getenv(config["api_key_env"], "")
            if api_key:
                logger.info(f"🔑 Using speaker-specific API key for {speaker_name}")
                return api_key
            
            # Fallback to main API key
            fallback_key = os.getenv(config["fallback_api_key_env"], "")
            if fallback_key:
                logger.info(f"🔑 Using fallback API key for {speaker_name}")
                return fallback_key
        
        # Default fallback - use the new general API key
        default_key = "sk_94096d8a0eef902dccfb2c9e5c371ee0b30730f49e7bae63"
        if default_key:
            logger.info(f"🔑 Using default API key for {speaker_name}")
            return default_key
        
        logger.warning(f"⚠️ No API key found for speaker {speaker_name}")
        return ""
        
    except Exception as e:
        logger.error(f"❌ Error getting API key for {speaker_name}: {str(e)}")
        return "sk_94096d8a0eef902dccfb2c9e5c371ee0b30730f49e7bae63"



def generate_voice_segment(text, voice_id, output_path, speaker_name=None):
    """Generate voice segment using ElevenLabs API"""
    try:
        # Use ElevenLabs for all speakers
        logger.info(f"🎤 Using ElevenLabs for speaker: {speaker_name}")
        return generate_elevenlabs_voice_segment(text, voice_id, output_path, speaker_name)
        
    except Exception as e:
        logger.error(f"❌ Error generating voice segment for {speaker_name}: {str(e)}")
        return False

def generate_elevenlabs_voice_segment(text, voice_id, output_path, speaker_name=None):
    """Generate voice segment using ElevenLabs API with speaker-specific API key"""
    try:
        logger.info(f"🎤 Generating voice segment for speaker: {speaker_name}")
        logger.info(f"🆔 Voice ID: {voice_id}")
        logger.info(f"📝 Text: {text[:50]}...")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
        
        # Get appropriate API key for this speaker
        api_key = get_api_key_for_speaker(speaker_name) if speaker_name else "sk_94096d8a0eef902dccfb2c9e5c371ee0b30730f49e7bae63"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Apply Hindi phonetic preprocessing for Samay/Arpit to improve TTS
        processed_text = text
        if speaker_name in ["samay", "arpit"]:
            try:
                before = text
                processed_text = apply_hindi_phonetics(text)
                logger.info(f"🗣️ Applied Hindi phonetics for {speaker_name}: before='{before[:80]}...' after='{processed_text[:80]}...'")
            except Exception as e:
                logger.warning(f"⚠️ Failed to apply phonetics for {speaker_name}: {e}")

        data = {
            "text": processed_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        logger.info("🌐 Sending request to ElevenLabs API...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()

            audio_data = base64.b64decode(result['audio_base64'])
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ Voice segment generated successfully")
            logger.info(f"📊 File size: {file_size} bytes")
            return {
                'success': True,
                'audio_path': output_path,
                'timing_data': result['alignment']
            }
        else:
            logger.warning(f"⚠️ ElevenLabs failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ElevenLabs error: {str(e)}")
        return False

def batch_generate_voice_segments(segments_data, output_dir):
    """
    Batch generate multiple voice segments using ElevenLabs
    """
    try:
        logger.info(f"🎤 Starting batch voice generation for {len(segments_data)} segments")
        
        successful_segments = []
        timing_data_collection = []
        
        for segment_index, (text, voice_id, filename, speaker_name) in enumerate(segments_data):
            try:
                logger.info(f"🎤 Processing segment {segment_index + 1}/{len(segments_data)} for {speaker_name}")
                
                output_path = os.path.join(output_dir, filename)
                
                # Apply Hindi phonetics for Samay/Arpit before sending
                processed_text = text
                if speaker_name in ["samay", "arpit"]:
                    try:
                        processed_text = apply_hindi_phonetics(text)
                        logger.info(f"🔤 Applied Hindi phonetics for {speaker_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Batch phonetics failed for {speaker_name}: {e}")
                
                # Use the unified voice generation function
                success = generate_voice_segment(processed_text, voice_id, output_path, speaker_name)
                
                if success:
                    # Extract speaker from filename
                    speaker = speaker_name  # Use the actual speaker name passed in
                    successful_segments.append((speaker, output_path))
                    
                    # For ElevenLabs speakers, we'll get real timing data from the response
                    timing_data_collection.append({
                        'speaker': speaker,
                        'text': text,
                        'timing_data': None,  # Will be filled by ElevenLabs response
                        'segment_index': segment_index
                    })
                    
                    logger.info(f"✅ Voice segment generated successfully for {speaker}")
                else:
                    logger.warning(f"⚠️ Failed to generate segment {segment_index + 1} for {speaker_name}")
                    continue
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to generate segment {segment_index + 1}: {str(e)}")
                continue
        
        logger.info(f"✅ Batch generation completed: {len(successful_segments)}/{len(segments_data)} segments successful")
        return successful_segments, timing_data_collection
        
    except Exception as e:
        logger.error(f"❌ Batch voice generation failed: {str(e)}")
        return [], []

def batch_generate_elevenlabs_voice_segments(segments_data, output_dir):
    """
    Batch generate multiple voice segments using ElevenLabs API with better error handling
    segments_data: list of (text, voice_id, output_filename, speaker_name) tuples
    """
    try:
        logger.info(f"🎤 Batch generating {len(segments_data)} voice segments")
        
        # Process in smaller batches to avoid rate limits
        batch_size = 3  # Process 3 segments at a time
        successful_segments = []
        timing_data_collection = []
        
        for i in range(0, len(segments_data), batch_size):
            batch = segments_data[i:i + batch_size]
            logger.info(f"🎤 Processing batch {i//batch_size + 1}/{(len(segments_data) + batch_size - 1)//batch_size}")
            
            for j, segment_data in enumerate(batch):
                # Handle both old and new tuple formats for backward compatibility
                if len(segment_data) == 4:
                    text, voice_id, filename, speaker_name = segment_data
                else:
                    text, voice_id, filename = segment_data
                    speaker_name = None
                
                segment_index = i + j
                output_path = os.path.join(output_dir, filename)
                
                logger.info(f"🎤 Generating segment {segment_index + 1}/{len(segments_data)} for speaker: {speaker_name}")
                logger.info(f"🆔 Voice ID: {voice_id}")
                logger.info(f"📝 Text: {text[:50]}...")
                
                # Make API request with speaker-specific API key
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
                
                # Apply Hindi phonetics for Samay/Arpit before sending
                processed_text = text
                if speaker_name in ["samay", "arpit"]:
                    try:
                        before = text
                        processed_text = apply_hindi_phonetics(text)
                        logger.info(f"🗣️ Batch phonetics for {speaker_name}: before='{before[:80]}...' after='{processed_text[:80]}...'")
                    except Exception as e:
                        logger.warning(f"⚠️ Batch phonetics failed for {speaker_name}: {e}")

                # Get appropriate API key for this speaker
                api_key = get_api_key_for_speaker(speaker_name) if speaker_name else "sk_94096d8a0eef902dccfb2c9e5c371ee0b30730f49e7bae63"
                
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": api_key
                }
                
                data = {
                    "text": processed_text,
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
                        result = response.json()
                        
                        # 🔍 DEBUG: Check timing data specifically
                        alignment = result.get('alignment')
    
                    if alignment:
                        audio_data = base64.b64decode(result['audio_base64'])
                        with open(output_path, 'wb') as f:
                            f.write(audio_data)
                        
                        file_size = os.path.getsize(output_path)
                        logger.info(f"✅ Voice segment generated successfully")
                        logger.info(f"📊 File size: {file_size} bytes")
                        
                        # Extract speaker from filename
                        speaker = speaker_name  # Use the actual speaker name passed in
                        successful_segments.append((speaker, output_path))

                        timing_data_collection.append({
                            'speaker': speaker,
                            'text': text,
                            'timing_data': result['alignment'],
                            'segment_index': segment_index
                        })

                        logger.info(f"🔍 DEBUG: Added to timing_data_collection: speaker={speaker}, has_alignment={result.get('alignment') is not None}")
                        
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
        return successful_segments, timing_data_collection
        
    except Exception as e:
        logger.error(f"❌ Failed to batch generate voice segments: {str(e)}")
        return ([], [])

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
        
        # Use FFmpeg availability check
        ffmpeg_cmd = check_ffmpeg_availability()
        if ffmpeg_cmd is None:
            raise Exception("FFmpeg is not available on this system")
        
        cmd = [
            ffmpeg_cmd,
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list_path,
            '-c', 'copy',
            output_path,
            '-y'  # Overwrite output file
        ]
        
        logger.info(f"🎵 Running ffmpeg command: {' '.join(cmd)}")
        logger.info(f"🔧 Using FFmpeg binary: {ffmpeg_cmd}")
        
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
            logger.error(f"❌ ffmpeg failed with return code: {result.returncode}")
            logger.error(f"❌ ffmpeg stderr: {result.stderr}")
            logger.error(f"❌ ffmpeg stdout: {result.stdout}")
            logger.error(f"❌ Command that failed: {' '.join(cmd)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to combine audio segments: {str(e)}")
        return False

def generate_conversational_voiceover(script_text, output_path=None, speaker_pair="trump_mrbeast"):
    """
    Generate conversational audio with alternating speakers (optimized version)
    
    Args:
        script_text: The script to convert to audio
        output_path: Where to save the audio file
        speaker_pair: Which speaker pair to use (trump_elon, baburao_samay, samay_arpit)
    """
    try:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🎵 [{request_id}] Starting optimized conversational voiceover generation")
        logger.info(f"📝 [{request_id}] Script length: {len(script_text)} characters")
        
        if not output_path:
            output_path = tempfile.mktemp(suffix=".wav")
            logger.info(f"📁 [{request_id}] Using temporary output path: {output_path}")
        
        # Parse script into speaker segments with selected pair
        logger.info(f"🔍 [{request_id}] Parsing script for speaker separation...")
        logger.info(f"🎭 [{request_id}] Using speaker pair: {speaker_pair}")
        speaker_segments = parse_conversational_script(script_text, speaker_pair)
        
        # Prepare batch data for ElevenLabs
        logger.info(f"🎤 [{request_id}] Preparing batch requests for ElevenLabs...")
        batch_data = []
        
        for i, (speaker, text) in enumerate(speaker_segments):
            # Get voice ID from speaker configuration
            if speaker in SPEAKER_CONFIG:
                voice_id = SPEAKER_CONFIG[speaker]["voice_id"]
            else:
                # Fallback to legacy system for unknown speakers
                voice_id = ELON_VOICE_ID if speaker == "elon" else TRUMP_VOICE_ID
                logger.warning(f"⚠️ [{request_id}] Unknown speaker '{speaker}', using fallback voice ID")
            
            filename = f"segment_{i+1}_{speaker}.wav"
            # Include speaker name in the batch data for API key selection
            batch_data.append((text, voice_id, filename, speaker))
        
        # Create temporary directory for segments
        temp_dir = tempfile.mkdtemp()
        logger.info(f"📁 [{request_id}] Using temporary directory: {temp_dir}")
        
        # Batch generate all voice segments using unified voice generation
        audio_segments, timing_data = batch_generate_voice_segments(batch_data, temp_dir)
        
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
                shutil.rmtree(temp_dir)
                logger.debug(f"🗑️ [{request_id}] Removed temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"⚠️ [{request_id}] Failed to remove temporary directory {temp_dir}: {str(e)}")
            
            return output_path, timing_data
        else:
            raise Exception("Failed to combine audio segments")
            
    except Exception as e:
        logger.error(f"❌ [{request_id}] Failed to generate conversational voiceover: {str(e)}")
        logger.error(f"❌ [{request_id}] Error type: {type(e).__name__}")
        raise Exception(f"Failed to generate conversational voiceover: {str(e)}")

def create_speaker_timeline_with_timing_data(script_text, speaker_pair="trump_mrbeast", timing_data=None):
    """
    Create a timeline using real timing data from ElevenLabs or fallback to estimated timing
    """
    try:
        logger.info("⏰ Creating speaker timeline with real timing data")
        
        timeline = []
        current_time = 0.0
        
        # Handle case where timing_data is None or empty
        if not timing_data:
            logger.warning("⚠️ No timing data provided, creating timeline from script text")
            # Fallback: parse script and create timeline with estimated timing
            speaker_segments = parse_conversational_script(script_text, speaker_pair)
            for speaker, text in speaker_segments:
                # Estimate duration based on word count (roughly 2 words per second)
                word_count = len(text.split())
                estimated_duration = max(word_count * 0.5, 1.0)  # Minimum 1 second
                
                timeline.append({
                    'speaker': speaker,
                    'start_time': current_time,
                    'end_time': current_time + estimated_duration,
                    'text': text,
                    'real_timing_data': None  # No real timing data available
                })
                
                current_time += estimated_duration + 0.2  # Add pause between speakers
            
            logger.info(f"✅ Created fallback timeline: {len(timeline)} segments")
            return timeline
        
        # Process timing data if available
        for timing_info in timing_data:
            speaker = timing_info['speaker']
            text = timing_info['text']
            alignment = timing_info['timing_data']
            
            # Calculate duration using documented ElevenLabs format or fallback
            if alignment is not None:
                duration = calculate_duration_from_documented_format(alignment, text)
            else:
                # Fallback: estimate duration based on word count
                word_count = len(text.split())
                duration = max(word_count * 0.5, 1.0)  # Minimum 1 second
                logger.debug(f"📊 Using estimated duration for {speaker}: {duration}s")

            timeline.append({
                'speaker': speaker,
                'start_time': current_time,
                'end_time': current_time + duration,
                'text': text,
                'real_timing_data': alignment  # Include raw timing data (may be None)
            })
            
            current_time += duration + 0.2  # Add pause between speakers
        
        logger.info(f"✅ Created timeline with timing data: {len(timeline)} segments")
        return timeline
        
    except Exception as e:
        logger.error(f"❌ Failed to create timeline with timing data: {str(e)}")
        logger.error(f"🔍 DEBUG: Exception details: {type(e).__name__}: {str(e)}")
        logger.error(f"🔍 DEBUG: timing_data type: {type(timing_data)}")
        logger.error(f"🔍 DEBUG: timing_data content: {timing_data}")
        return []  # Return empty list instead of None

def calculate_duration_from_documented_format(alignment, text):
    """
    Calculate duration from ElevenLabs alignment data according to official docs
    Expected format: alignment['character_end_times_seconds'][-1]
    """
    try:
        if not alignment or not isinstance(alignment, dict):
            return len(text.split()) * 0.5
        
        # Use documented ElevenLabs API format
        if 'character_end_times_seconds' in alignment:
            end_times = alignment['character_end_times_seconds']
            if end_times and isinstance(end_times, list):
                return float(end_times[-1])  # Last character's end time = total duration
        
        # Fallback to word estimation
        return len(text.split()) * 0.5
        
    except Exception as e:
        logger.warning(f"⚠️ Could not parse alignment: {e}, using fallback")
        return len(text.split()) * 0.5