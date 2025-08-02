#!/usr/bin/env python3
"""
Test OpenCV Video Generation Pipeline
Tests the new reliable OpenCV-based video generation system
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

def test_opencv_video_generation():
    """Test the complete OpenCV video generation"""
    try:
        logger.info("🎬 Testing OpenCV Video Generation System...")
        
        # Import the new OpenCV system
        from opencv_video_generator import create_background_video_with_speaker_overlays
        
        # Test script
        script = """**Trump:** You know, folks, this whole artificial intelligence thing - it's incredible, really incredible. I've been talking to some of the smartest people about AI.

**Elon:** Well, Donald, AI is definitely one of the most important technologies of our time. At Tesla and SpaceX, we're using machine learning for everything.

**Trump:** Elon's doing amazing work, absolutely amazing. But let me tell you something - we need to make sure America leads in AI."""
        
        # Use valid test audio
        audio_path = "test_new_api.mp3"
        if not os.path.exists(audio_path):
            logger.error(f"❌ Test audio not found: {audio_path}")
            return False
        
        # Create output path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"test_opencv_output_{timestamp}.mp4"
        
        logger.info(f"🎯 Testing OpenCV video generation...")
        logger.info(f"📝 Script: {len(script)} chars")
        logger.info(f"🎵 Audio: {audio_path}")
        logger.info(f"📹 Output: {output_path}")
        
        # Generate video using OpenCV
        video_path = create_background_video_with_speaker_overlays(
            script_text=script,
            audio_path=audio_path,
            output_path=output_path
        )
        
        # Verify output
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            logger.info(f"✅ OpenCV video generated successfully!")
            logger.info(f"📁 Output file: {video_path}")
            logger.info(f"📊 File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
            
            # Test that we can read the video with OpenCV
            import cv2
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
                logger.info(f"🎬 Video properties:")
                logger.info(f"   Duration: {duration:.2f}s")
                logger.info(f"   Resolution: {width}x{height}")
                logger.info(f"   FPS: {fps}")
                logger.info(f"   Frames: {frame_count}")
                
                cap.release()
                return True
            else:
                logger.error(f"❌ Could not read generated video with OpenCV")
                return False
        else:
            logger.error(f"❌ Video file was not created: {video_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ OpenCV video generation failed: {str(e)}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return False

def test_opencv_setup():
    """Test OpenCV installation and basic functionality"""
    try:
        logger.info("🔧 Testing OpenCV setup...")
        
        import cv2
        import numpy as np
        
        logger.info(f"✅ OpenCV version: {cv2.__version__}")
        
        # Test basic OpenCV functionality
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        test_img[:] = (255, 0, 0)  # Blue image
        
        # Test video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        test_writer = cv2.VideoWriter('test_opencv.mp4', fourcc, 30, (100, 100))
        
        if test_writer.isOpened():
            logger.info("✅ OpenCV VideoWriter working")
            test_writer.write(test_img)
            test_writer.release()
            
            # Clean up test file
            if os.path.exists('test_opencv.mp4'):
                os.remove('test_opencv.mp4')
            
            return True
        else:
            logger.error("❌ OpenCV VideoWriter failed to open")
            return False
        
    except Exception as e:
        logger.error(f"❌ OpenCV setup test failed: {str(e)}")
        return False

def test_ffmpeg():
    """Test FFmpeg installation"""
    try:
        logger.info("🎵 Testing FFmpeg setup...")
        
        import subprocess
        
        # Test FFmpeg (use local binary if available)
        ffmpeg_path = './ffmpeg' if os.path.exists('./ffmpeg') else 'ffmpeg'
        result = subprocess.run([ffmpeg_path, '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"✅ FFmpeg available: {version_line}")
            return True
        else:
            logger.error("❌ FFmpeg not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ FFmpeg test failed: {str(e)}")
        return False

def main():
    """Run all OpenCV pipeline tests"""
    logger.info("🚀 Starting OpenCV Pipeline Test Suite")
    logger.info("🎯 Testing MoviePy-free video generation system")
    logger.info("=" * 60)
    
    tests = [
        ("OpenCV Setup", test_opencv_setup),
        ("FFmpeg Setup", test_ffmpeg),
        ("OpenCV Video Generation", test_opencv_video_generation)
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
        logger.info("🎉 ALL TESTS PASSED! OpenCV pipeline is ready!")
        logger.info("🚀 MoviePy has been completely replaced with OpenCV!")
        logger.info("💪 Your video generation is now rock-solid reliable!")
    else:
        logger.info("❌ Some tests failed. Fix issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)