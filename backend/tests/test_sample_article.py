#!/usr/bin/env python3
"""
Test script for the conversational video system with sample article
This demonstrates the Elon-Trump conversational video generation with a real article
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)   )))

from llm import generate_conversational_script
from opencv_video_generator import create_background_video_with_speaker_overlays
from conversational_video import create_conversational_video

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_conversational_system_with_sample():
    """
    Test the conversational video generation system with a sample article
    """
    try:
        logger.info("🚀 Starting conversational video generation with sample article")
        
        # Sample article about Docker and Kubernetes
        sample_article = """
        Docker and Kubernetes have revolutionized software development and deployment. 
        Docker provides containerization technology that packages applications with their dependencies, 
        while Kubernetes orchestrates and manages these containers at scale. 
        Companies worldwide are adopting these technologies to improve deployment efficiency, 
        reduce infrastructure costs, and enable microservices architecture. 
        The containerization market is expected to grow significantly as organizations 
        continue to modernize their software development practices.
        """
        
        logger.info("📝 Step 1: Generating conversational script from sample article.")
        script = generate_conversational_script(sample_article)
        logger.info(f"✅ Script generated: {len(script)} characters")
        logger.info(f"📝 Script preview: {script[:200]}...")
        
        logger.info("⏰ Step 2: Creating speaker timeline...")
        timeline = create_speaker_timeline(script)
        logger.info(f"✅ Timeline created with {len(timeline)} segments")
        
        # Show first few segments
        for i, segment in enumerate(timeline[:5]):
            logger.info(f"   Segment {i+1}: {segment['speaker']} ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s)")
        
        logger.info("🎵 Step 3: Generating conversational audio...")
        audio_path = generate_conversational_voiceover(script)
        logger.info(f"✅ Audio generated: {audio_path}")
        
        logger.info("🎬 Step 4: Creating conversational video...")
        video_path = create_background_video_with_speaker_overlays(script, audio_path)        
        logger.info(f"✅ Video created: {video_path}")
        
        # Save all outputs to outputs directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create outputs directory if it doesn't exist
        os.makedirs("outputs", exist_ok=True)
        
        # Save script
        script_path = f"outputs/conversational_script_{timestamp}.txt"
        with open(script_path, 'w') as f:
            f.write(script)
        logger.info(f"📝 Script saved: {script_path}")
        
        # Save timeline
        import json
        timeline_path = f"outputs/conversational_timeline_{timestamp}.json"
        with open(timeline_path, 'w') as f:
            json.dump(timeline, f, indent=2)
        logger.info(f"⏰ Timeline saved: {timeline_path}")
        
        # Save audio
        import shutil
        audio_output_path = f"outputs/conversational_audio_{timestamp}.wav"
        shutil.copy2(audio_path, audio_output_path)
        logger.info(f"🎵 Audio saved: {audio_output_path}")
        
        # Save video
        video_output_path = f"outputs/conversational_video_{timestamp}.mp4"
        shutil.copy2(video_path, video_output_path)
        logger.info(f"🎬 Video saved: {video_output_path}")
        
        logger.info("✅ Conversational video generation test completed successfully!")
        logger.info("📁 All files saved to outputs/ directory")
        
        return {
            "script": script,
            "timeline": timeline,
            "audio_path": audio_output_path,
            "video_path": video_output_path
        }
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        results = test_conversational_system_with_sample()
        print("\n🎉 Test completed successfully!")
        print(f"📝 Script: outputs/conversational_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        print(f"⏰ Timeline: outputs/conversational_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        print(f"🎵 Audio: outputs/conversational_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        print(f"🎬 Video: outputs/conversational_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1) 