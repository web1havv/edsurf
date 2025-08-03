"""
Test Caption Rendering - Phase 2
"""

import cv2
import numpy as np
import os, sys
from datetime import datetime

# Add parent directory to Python path so we can import from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test the caption renderer
def test_caption_rendering():
    """Test caption rendering on sample frames"""
    print("🎨 Testing Caption Rendering...")
    
    # Import modules
    from captions.caption_renderer import CaptionRenderer
    from captions.caption_processor import enhance_timeline_with_captions
    
    # Create test frame (1080x1920 vertical video)
    test_frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
    test_frame[:] = (50, 100, 50)  # Dark green background
    
    # Initialize renderer
    renderer = CaptionRenderer(1080, 1920)
    
    # Test different captions
    test_captions = [
        {"text": "So what's the big deal with Docker?", "speaker": "elon"},
        {"text": "It's HUGE! Really, really HUGE!", "speaker": "trump"},
        {"text": "This is a very long caption that should wrap to multiple lines automatically when it exceeds the maximum width.", "speaker": "elon"},
        {"text": "Short text.", "speaker": "trump"}
    ]
    
    # Render each caption
    for i, caption in enumerate(test_captions):
        frame_copy = test_frame.copy()
        rendered_frame = renderer.render_caption(
            frame_copy, caption["text"], caption["speaker"]
        )
        
        # Save test frame
        output_path = f"test_caption_{i+1}_{caption['speaker']}.jpg"
        cv2.imwrite(output_path, rendered_frame)
        print(f"✅ Saved test frame: {output_path}")

def test_full_video_with_captions():
    """Test creating a full video with captions"""
    print("🎬 Testing Full Video Generation with Captions...")
    
    # Store current working directory
    original_cwd = os.getcwd()
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Temporarily change to backend directory where speaker images are located
        os.chdir(backend_dir)
        print(f"🔄 Changed working directory to: {backend_dir}")
            

        # Import video generator
        from opencv_video_generator import OpenCVVideoGenerator
        
        # Create generator instance
        generator = OpenCVVideoGenerator()
        
        # Test script
        test_script = """Docker is revolutionary technology. It changes everything about software deployment. You just put your stuff in a container and it works everywhere. It's like magic, but better. The best containerization platform ever created."""
        
        # Generate video with captions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"test_video_with_captions_{timestamp}.mp4"
        
        result = generator.create_video_with_overlays_and_captions(
            script_text=test_script,
            audio_path=None,  # Silent video for testing
            output_path=output_path,
            speaker_pair='trump_elon',
            enable_captions=True,
            timing_data=None
        )
            
        if result and os.path.exists(result):
            print(f"✅ Video with captions created: {result}")
            return result
        else:
            print("❌ Failed to create video")
            return None
                
    except Exception as e:
        print(f"❌ Error creating video with captions: {str(e)}")
        return None

    finally:
        # Always restore original working directory
        os.chdir(original_cwd)
        print(f"🔄 Restored working directory to: {original_cwd}")

if __name__ == "__main__":
    print("🚀 PHASE 2: CAPTION RENDERING TESTS")
    print("="*50)
    
    # Test 1: Caption rendering on individual frames
    test_caption_rendering()
    
    # Test 2: Full video generation with captions
    test_full_video_with_captions()
    
    print("\n✅ Phase 2 tests completed!")
    print("📹 Check the generated files to see caption rendering results")