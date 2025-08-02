#!/usr/bin/env python3
"""
Test script for the article extraction and URL-based video generation system
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from article_extractor import extract_article_from_url
from llm import generate_conversational_script
from conversational_tts import generate_conversational_voiceover, create_speaker_timeline
from conversational_video import create_conversational_video

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_article_extraction():
    """
    Test article extraction from various URLs
    """
    test_urls = [
        "https://medium.com/@john_doe/understanding-docker-containers-a-beginners-guide",
        "https://techcrunch.com/2024/01/15/ai-revolution-transforms-software-development/",
        "https://github.com/kubernetes/kubernetes/blob/main/README.md",
        "https://stackoverflow.com/questions/12345/what-is-docker-and-why-use-it"
    ]
    
    for url in test_urls:
        try:
            logger.info(f"🔍 Testing article extraction from: {url}")
            article_data = extract_article_from_url(url)
            
            logger.info(f"✅ Successfully extracted article")
            logger.info(f"📝 Title: {article_data['title']}")
            logger.info(f"📄 Content length: {len(article_data['content'])} characters")
            logger.info(f"📋 Summary: {article_data['summary'][:200]}...")
            
            # Test script generation
            logger.info(f"🤖 Generating conversational script...")
            script = generate_conversational_script(article_data['content'])
            logger.info(f"📜 Script generated: {len(script)} characters")
            logger.info(f"📜 Preview: {script[:300]}...")
            
            break  # Just test with the first working URL
            
        except Exception as e:
            logger.error(f"❌ Failed to extract from {url}: {str(e)}")
            continue

def test_full_pipeline():
    """
    Test the complete pipeline with a sample article
    """
    try:
        logger.info("🚀 Starting full article-to-video pipeline test")
        
        # Sample article about Docker
        sample_article = """
        Docker is a platform for developing, shipping, and running applications in containers. 
        Containers are lightweight, portable, and self-contained units that can run anywhere Docker is installed.
        
        Docker containers package an application and all its dependencies into a standardized unit for software development. 
        This includes the code, runtime, system tools, system libraries, and settings.
        
        The key benefits of Docker include:
        - Consistency across environments
        - Isolation between applications
        - Portability across different systems
        - Efficiency in resource usage
        - Rapid deployment and scaling
        
        Docker uses a client-server architecture. The Docker daemon runs on the host machine and manages containers, 
        while the Docker client communicates with the daemon through a REST API.
        
        Docker images are the building blocks of containers. They are read-only templates that contain the application 
        code, runtime, libraries, and dependencies. Images are created from Dockerfiles, which are text files that 
        contain instructions for building the image.
        
        Kubernetes is often used alongside Docker for container orchestration, providing features like automatic scaling, 
        load balancing, and service discovery.
        """
        
        logger.info("📝 Step 1: Using sample article about Docker")
        logger.info(f"📄 Article length: {len(sample_article)} characters")
        
        # Generate conversational script
        logger.info("🤖 Step 2: Generating conversational script")
        script = generate_conversational_script(sample_article)
        logger.info(f"📜 Script generated: {len(script)} characters")
        logger.info(f"📜 Preview: {script[:300]}...")
        
        # Generate audio
        logger.info("🎵 Step 3: Generating conversational audio")
        audio_path = generate_conversational_voiceover(script)
        logger.info(f"🎵 Audio generated: {audio_path}")
        
        # Create video
        logger.info("🎬 Step 4: Creating conversational video")
        video_path = create_conversational_video(script, audio_path)
        logger.info(f"🎬 Video created: {video_path}")
        
        # Save outputs
        logger.info("💾 Step 5: Saving outputs")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save script
        script_filename = f"test_article_script_{timestamp}.txt"
        script_path = os.path.join("outputs", script_filename)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: Docker Container Technology\n\n{script}")
        logger.info(f"📝 Script saved: {script_path}")
        
        # Save timeline
        timeline = create_speaker_timeline(script)
        timeline_filename = f"test_article_timeline_{timestamp}.json"
        timeline_path = os.path.join("outputs", timeline_filename)
        import json
        with open(timeline_path, 'w', encoding='utf-8') as f:
            json.dump(timeline, f, indent=2)
        logger.info(f"⏰ Timeline saved: {timeline_path}")
        
        # Copy audio and video to outputs
        audio_filename = f"test_article_audio_{timestamp}.wav"
        video_filename = f"test_article_video_{timestamp}.mp4"
        audio_output_path = os.path.join("outputs", audio_filename)
        video_output_path = os.path.join("outputs", video_filename)
        
        import shutil
        shutil.copy2(audio_path, audio_output_path)
        shutil.copy2(video_path, video_output_path)
        
        logger.info(f"🎵 Audio saved: {audio_output_path}")
        logger.info(f"🎬 Video saved: {video_output_path}")
        
        # Clean up temporary files
        try:
            os.remove(audio_path)
            os.remove(video_path)
            logger.debug("🗑️ Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"⚠️ Failed to clean up temporary files: {str(e)}")
        
        logger.info("✅ Full article-to-video pipeline test completed successfully!")
        logger.info(f"📁 All files saved to outputs/ directory")
        
    except Exception as e:
        logger.error(f"❌ Full pipeline test failed: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("🧪 Starting article system tests")
    
    # Test 1: Article extraction
    logger.info("📖 Test 1: Article extraction from URLs")
    test_article_extraction()
    
    # Test 2: Full pipeline
    logger.info("🎬 Test 2: Full article-to-video pipeline")
    test_full_pipeline()
    
    logger.info("✅ All tests completed!") 