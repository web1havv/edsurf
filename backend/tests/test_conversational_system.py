#!/usr/bin/env python3
"""
Test script for the conversational video system
This demonstrates the Elon-Trump conversational video generation
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)   )))

from llm import generate_conversational_script
from conversational_tts import generate_conversational_voiceover, create_speaker_timeline
from conversational_video import create_conversational_video

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_conversational_system():
    """Test the complete conversational video generation system"""
    
    # Sample article content for testing
    test_article = """
    Artificial Intelligence is transforming the world in unprecedented ways. 
    From healthcare to transportation, AI is revolutionizing industries and creating new opportunities. 
    Companies are investing billions in AI research and development, while governments are developing 
    policies to regulate this rapidly evolving technology. The future of work is being reshaped as 
    automation and AI tools become more sophisticated. However, concerns about job displacement and 
    ethical implications remain significant challenges that need to be addressed.
    """
    
    try:
        logger.info("🚀 Starting conversational video generation test")
        
        # Step 1: Generate conversational script
        logger.info("📝 Step 1: Generating conversational script...")
        script = generate_conversational_script(test_article)
        logger.info(f"✅ Script generated: {len(script)} characters")
        logger.info(f"📝 Script preview: {script[:200]}...")
        
        # Step 2: Create speaker timeline
        logger.info("⏰ Step 2: Creating speaker timeline...")
        timeline = create_speaker_timeline(script)
        logger.info(f"✅ Timeline created with {len(timeline)} segments")
        
        # Show timeline details
        for i, segment in enumerate(timeline[:3]):  # Show first 3 segments
            logger.info(f"   Segment {i+1}: {segment['speaker']} ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s)")
        
        # Step 3: Generate conversational audio
        logger.info("🎵 Step 3: Generating conversational audio...")
        audio_path = generate_conversational_voiceover(script)
        logger.info(f"✅ Audio generated: {audio_path}")
        
        # Step 4: Create conversational video
        logger.info("🎬 Step 4: Creating conversational video...")
        video_path = create_conversational_video(script, audio_path)
        logger.info(f"✅ Video created: {video_path}")
        
        # Save results to outputs directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outputs_dir = "outputs"
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Save script
        script_path = os.path.join(outputs_dir, f"conversational_script_{timestamp}.txt")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        logger.info(f"📝 Script saved: {script_path}")
        
        # Save timeline
        timeline_path = os.path.join(outputs_dir, f"conversational_timeline_{timestamp}.json")
        import json
        with open(timeline_path, 'w', encoding='utf-8') as f:
            json.dump(timeline, f, indent=2)
        logger.info(f"⏰ Timeline saved: {timeline_path}")
        
        # Copy audio and video to outputs
        import shutil
        audio_output = os.path.join(outputs_dir, f"conversational_audio_{timestamp}.wav")
        video_output = os.path.join(outputs_dir, f"conversational_video_{timestamp}.mp4")
        
        shutil.copy2(audio_path, audio_output)
        shutil.copy2(video_path, video_output)
        
        logger.info(f"🎵 Audio saved: {audio_output}")
        logger.info(f"🎬 Video saved: {video_output}")
        
        logger.info("✅ Conversational video generation test completed successfully!")
        logger.info("📁 All files saved to outputs/ directory")
        
        return {
            'script_path': script_path,
            'timeline_path': timeline_path,
            'audio_path': audio_output,
            'video_path': video_output
        }
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        raise

if __name__ == "__main__":
    try:
        results = test_conversational_system()
        print("\n🎉 Test completed successfully!")
        print(f"📝 Script: {results['script_path']}")
        print(f"⏰ Timeline: {results['timeline_path']}")
        print(f"🎵 Audio: {results['audio_path']}")
        print(f"🎬 Video: {results['video_path']}")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1) 