#!/usr/bin/env python3
"""
Test MoviePy Video Generation Pipeline
Tests video generation without hitting ElevenLabs API
"""

import os
import sys
import logging
import tempfile
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_moviepy_compatibility():
    """Test MoviePy compatibility layer"""
    try:
        logger.info("🧪 Testing MoviePy Compatibility Layer...")
        from moviepy_compat import check_moviepy_compatibility
        logger.info("✅ MoviePy compatibility layer imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ MoviePy compatibility layer failed: {str(e)}")
        return False

def test_sample_audio_generation():
    """Create a sample audio file for testing"""
    try:
        logger.info("🎵 Creating sample audio for testing...")
        
        # Check if we have existing test audio files (prioritize larger, valid files)
        test_audio_files = [
            "test_new_api.mp3",      # 67KB - best for testing
            "test_elon_audio.mp3",   # 30KB - good backup
            "test_audio.mp3",
            "test_trump_final.mp3",
            "test_elon_final.mp3"
        ]
        
        for audio_file in test_audio_files:
            if os.path.exists(audio_file):
                logger.info(f"✅ Found existing test audio: {audio_file}")
                return audio_file
        
        # If no existing files, create a simple audio file using pydub
        logger.info("🔊 Creating synthetic test audio...")
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Create a 10-second test tone (440Hz - A note)
        tone = Sine(440).to_audio_segment(duration=10000)  # 10 seconds
        
        # Save as WAV for testing
        test_audio_path = "test_moviepy_sample.wav"
        tone.export(test_audio_path, format="wav")
        
        logger.info(f"✅ Created synthetic test audio: {test_audio_path}")
        return test_audio_path
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample audio: {str(e)}")
        return None

def test_conversational_script():
    """Create a sample conversational script for testing"""
    return """**Trump:** You know, folks, this whole artificial intelligence thing - it's incredible, really incredible. I've been talking to some of the smartest people about AI, and they tell me things that would blow your mind.

**Elon:** Well, Donald, AI is definitely one of the most important technologies of our time. At Tesla and SpaceX, we're using machine learning for everything from autonomous driving to rocket landing algorithms.

**Trump:** Elon's doing amazing work, absolutely amazing. But let me tell you something - we need to make sure America leads in AI. China's not sleeping, believe me. They're working very hard on this stuff.

**Elon:** That's absolutely right. The competition is intense, and whoever leads in AI will have significant advantages. That's why we need to accelerate development while also being thoughtful about safety.

**Trump:** Safety, yes - very important. But we also need to move fast. That's what I did with the vaccine development - Operation Warp Speed. We can do the same thing with AI."""

def test_video_generation_pipeline():
    """Test the complete video generation without ElevenLabs"""
    try:
        logger.info("🎬 Testing Complete Video Generation Pipeline...")
        
        # Step 1: Test compatibility
        if not test_moviepy_compatibility():
            return False
        
        # Step 2: Get sample audio
        audio_path = test_sample_audio_generation()
        if not audio_path:
            logger.error("❌ No audio file available for testing")
            return False
        
        # Step 3: Get sample script
        script = test_conversational_script()
        logger.info(f"📝 Using test script ({len(script)} characters)")
        
        # Step 4: Test video generation
        logger.info("🎬 Testing conversational video with background overlays...")
        from conversational_video import create_background_video_with_speaker_overlays
        
        # Create output path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"test_moviepy_output_{timestamp}.mp4"
        
        logger.info(f"🎯 Testing video generation...")
        logger.info(f"📝 Script: {len(script)} chars")
        logger.info(f"🎵 Audio: {audio_path}")
        logger.info(f"📹 Output: {output_path}")
        
        # Generate video
        video_path = create_background_video_with_speaker_overlays(
            script_text=script,
            audio_path=audio_path,
            output_path=output_path
        )
        
        # Verify output
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            logger.info(f"✅ Video generated successfully!")
            logger.info(f"📁 Output file: {video_path}")
            logger.info(f"📊 File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
            
            # Test that we can read the video
            from moviepy import VideoFileClip
            test_clip = VideoFileClip(video_path)
            logger.info(f"🎬 Video duration: {test_clip.duration:.2f}s")
            logger.info(f"🖼️ Video size: {test_clip.size}")
            test_clip.close()
            
            return True
        else:
            logger.error(f"❌ Video file was not created: {video_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Video generation pipeline failed: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return False

def test_minecraft_background():
    """Test Minecraft background video specifically"""
    try:
        logger.info("🎮 Testing Minecraft background video...")
        
        minecraft_path = "../minecraft-1.mp4"
        if not os.path.exists(minecraft_path):
            logger.error(f"❌ Minecraft video not found: {minecraft_path}")
            return False
        
        from moviepy import VideoFileClip
        from moviepy_compat import safe_resize, safe_set_duration
        
        # Test loading and basic operations
        clip = VideoFileClip(minecraft_path)
        logger.info(f"🎮 Minecraft video loaded successfully")
        logger.info(f"⏱️ Duration: {clip.duration:.2f}s")
        logger.info(f"🖼️ Size: {clip.size}")
        logger.info(f"🎞️ FPS: {clip.fps}")
        
        # Test resizing
        resized_clip = safe_resize(clip, (1080, 1920))
        logger.info(f"✅ Resize successful: {resized_clip.size}")
        
        # Test duration setting
        duration_clip = safe_set_duration(resized_clip, 5.0)
        logger.info(f"✅ Duration setting successful: {duration_clip.duration:.2f}s")
        
        # Cleanup
        clip.close()
        resized_clip.close()
        duration_clip.close()
        
        logger.info("✅ Minecraft background video test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Minecraft background test failed: {str(e)}")
        return False

def main():
    """Run all MoviePy pipeline tests"""
    logger.info("🚀 Starting MoviePy Pipeline Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("MoviePy Compatibility", test_moviepy_compatibility),
        ("Minecraft Background", test_minecraft_background),
        ("Complete Video Pipeline", test_video_generation_pipeline)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            logger.error(f"❌ FAILED: {test_name} - {str(e)}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n🎯 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! MoviePy pipeline is ready!")
        logger.info("🚀 You can now safely test with ElevenLabs API")
    else:
        logger.info("❌ Some tests failed. Fix issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)