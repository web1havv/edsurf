from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import tempfile
import logging
import sys
from datetime import datetime

from opencv_video_generator import test_video_overlay
from llm import generate_script, generate_conversational_script, test_api_key, generate_case_study_summary, translate_text
from conversational_tts import generate_conversational_voiceover, SPEAKER_PAIRS
from opencv_video_generator import create_background_video_with_speaker_overlays
from article_extractor import extract_article_from_url
from topic_search import search_and_extract_topic
from case_study_processor import process_case_study_file, process_case_study_text
from quiz_generator import generate_quiz_from_content, calculate_quiz_score, save_quiz_data, load_quiz_data

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Info Reeler API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Info Reeler API"
    }

# Simple test endpoint
@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify server is working"""
    return {
        "message": "Server is working!",
        "timestamp": datetime.now().isoformat()
    }

class ArticleInput(BaseModel):
    url: str = None
    text: str = None
    title: str = None
    speaker_pair: str = "trump_mrbeast"  # Default to Trump & MrBeast

class TopicInput(BaseModel):
    topic: str
    speaker_pair: str = "trump_mrbeast"  # Default to Trump & MrBeast

class ReelResponse(BaseModel):
    script: str
    audio_url: str
    video_url: str = None

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Info Reeler API Server")
    logger.info(f"📅 Server started at: {datetime.now()}")
    
    # Test API key validity
    try:
        logger.info("🔑 Testing Gemini API key validity...")
        api_key_status = test_api_key()
        if api_key_status["valid"]:
            logger.info("✅ Gemini API key is valid and working!")
            logger.info(f"📊 API Key Info: {api_key_status.get('info', 'N/A')}")
        else:
            logger.error(f"❌ Gemini API key is invalid: {api_key_status.get('error', 'Unknown error')}")
    except Exception as e:
        logger.error(f"❌ Failed to test API key: {str(e)}")
    
    logger.info("🏥 Health check endpoint available at /health")
    logger.info("📝 Generate reel endpoint available at /generate-reel")

@app.post("/generate-reel", response_model=ReelResponse)
async def generate_info_reel(article: ArticleInput):
    request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Starting reel generation process")
    logger.info(f"📄 [{request_id}] Input: URL={article.url}, Text length={len(article.text) if article.text else 0}")
    
    try:
        # Step 1: Extract/clean content
        logger.info(f"📖 [{request_id}] Step 1: Extracting content")
        if article.url:
            logger.info(f"🌐 [{request_id}] Extracting from URL: {article.url}")
            content = extract_article_from_url(article.url)
            logger.info(f"📄 [{request_id}] Extracted content length: {len(content)} characters")
        else:
            logger.info(f"📝 [{request_id}] Using provided text content")
            content = article.text
            logger.info(f"📄 [{request_id}] Content length: {len(content)} characters")
        
        # Step 2: Generate script (async)
        logger.info(f"🤖 [{request_id}] Step 2: Generating script with Gemini AI")
        loop = asyncio.get_event_loop()
        script = await loop.run_in_executor(None, generate_script, content)
        logger.info(f"📜 [{request_id}] Script generated successfully")
        logger.info(f"📜 [{request_id}] Script length: {len(script)} characters")
        logger.debug(f"📜 [{request_id}] Script preview: {script[:200]}...")
        
        # Step 3: Generate audio
        logger.info(f"🎵 [{request_id}] Step 3: Generating audio")
        audio_path, timing_data = await loop.run_in_executor(None, generate_conversational_voiceover, script, None, article.speaker_pair)
        logger.info(f"🎵 [{request_id}] Audio generated: {audio_path}")
        
        # Step 4: Create video with default background
        logger.info(f"🎬 [{request_id}] Step 4: Creating video with default background")
        video_path = await loop.run_in_executor(None, create_background_video_with_speaker_overlays, script, audio_path, None, None, article.speaker_pair, timing_data)
        logger.info(f"🎬 [{request_id}] Video created: {video_path}")
        
        # Save all content to organized folder structure
        logger.info(f"💾 [{request_id}] Step 5: Saving files to organized folder structure")
        
        # Create organized output directories
        output_base = os.path.expanduser("~/Downloads/info_reeler_outputs")
        scripts_dir = os.path.join(output_base, "scripts")
        audio_dir = os.path.join(output_base, "audio")
        videos_dir = os.path.join(output_base, "videos")
        
        for directory in [scripts_dir, audio_dir, videos_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Create better filenames with timestamp and request ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_filename = f"script_{timestamp}_{request_id}.txt"
        audio_filename = f"audio_{timestamp}_{request_id}.wav"
        video_filename = f"video_{timestamp}_{request_id}.mp4"
        
        # Save script to organized folder
        script_path = os.path.join(scripts_dir, script_filename)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        logger.info(f"📝 [{request_id}] Script saved: {script_path}")
        
        # Move audio and video to organized folders
        audio_url = os.path.join(audio_dir, audio_filename)
        video_url = os.path.join(videos_dir, video_filename)
        
        shutil.move(audio_path, audio_url)
        shutil.move(video_path, video_url)
        
        # Also save to static dir for web access
        static_dir = "static"
        os.makedirs(static_dir, exist_ok=True)
        static_audio_url = os.path.join(static_dir, audio_filename)
        static_video_url = os.path.join(static_dir, video_filename)
        
        # Copy files to static directory for web access
        import shutil
        shutil.copy2(audio_url, static_audio_url)
        shutil.copy2(video_url, static_video_url)
        
        logger.info(f"✅ [{request_id}] Reel generation completed successfully!")
        logger.info(f"📁 [{request_id}] Files saved to organized folders:")
        logger.info(f"📝 Script: {script_path}")
        logger.info(f"🎵 Audio: {audio_url}")
        logger.info(f"🎬 Video: {video_url}")
        logger.info(f"📊 [{request_id}] File sizes: Audio={os.path.getsize(audio_url)} bytes, Video={os.path.getsize(video_url)} bytes")
        
        return ReelResponse(
            script=script,
            audio_url=f"/download/{audio_filename}",
            video_url=f"/download/{video_filename}"
        )
    except Exception as e:
        logger.error(f"❌ [{request_id}] Error during reel generation: {str(e)}")
        logger.error(f"❌ [{request_id}] Error type: {type(e).__name__}")
        logger.error(f"❌ [{request_id}] Full error details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-conversational-reel", response_model=ReelResponse)
async def generate_conversational_reel(article: ArticleInput):
    request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Starting conversational reel generation process")
    logger.info(f"📄 [{request_id}] Input: URL={article.url}, Text length={len(article.text) if article.text else 0}")
    
    try:
        # Step 1: Extract/clean content
        logger.info(f"📖 [{request_id}] Step 1: Extracting content")
        if article.url:
            logger.info(f"🌐 [{request_id}] Extracting from URL: {article.url}")
            content = extract_article_from_url(article.url)
            logger.info(f"📄 [{request_id}] Extracted content length: {len(content)} characters")
        else:
            logger.info(f"📝 [{request_id}] Using provided text content")
            content = article.text
            logger.info(f"📄 [{request_id}] Content length: {len(content)} characters")
        
        # Step 2: Generate conversational script (async)
        logger.info(f"🤖 [{request_id}] Step 2: Generating conversational script with Gemini AI")
        loop = asyncio.get_event_loop()
        script = await loop.run_in_executor(None, generate_conversational_script, content)
        logger.info(f"📜 [{request_id}] Conversational script generated successfully")
        logger.info(f"📜 [{request_id}] Script length: {len(script)} characters")
        logger.debug(f"📜 [{request_id}] Script preview: {script[:200]}...")
        
        # Step 3: Generate conversational audio with speaker pair
        speaker_pair = getattr(article, 'speaker_pair', 'trump_mrbeast')  # Default to Trump & MrBeast
        logger.info(f"🎵 [{request_id}] Step 3: Generating conversational audio with speaker pair: {speaker_pair}")
        audio_path, timing_data = await loop.run_in_executor(None, generate_conversational_voiceover, script, None, speaker_pair)
        logger.info(f"🎵 [{request_id}] Conversational audio generated: {audio_path}")
        
        # Step 4: Create conversational video with background and speaker overlays
        logger.info(f"🎬 [{request_id}] Step 4: Creating conversational video with background and speaker overlays")
        logger.info(f"🎭 [{request_id}] VIDEO GENERATION - Using speaker_pair for conversational-reel: {speaker_pair}")
        video_path = await loop.run_in_executor(None, create_background_video_with_speaker_overlays, script, audio_path, None, None, speaker_pair, timing_data)
        logger.info(f"🎬 [{request_id}] Conversational video with background created: {video_path}")
        
        # Save all content to organized folder structure
        logger.info(f"💾 [{request_id}] Step 5: Saving files to organized folder structure")
        
        # Create organized output directories
        output_base = os.path.expanduser("~/Downloads/info_reeler_outputs")
        scripts_dir = os.path.join(output_base, "scripts")
        audio_dir = os.path.join(output_base, "audio")
        videos_dir = os.path.join(output_base, "videos")
        
        for directory in [scripts_dir, audio_dir, videos_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Create better filenames with timestamp and request ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_filename = f"conversational_script_{timestamp}_{request_id}.txt"
        audio_filename = f"conversational_audio_{timestamp}_{request_id}.wav"
        video_filename = f"conversational_video_{timestamp}_{request_id}.mp4"
        
        # Save script to organized folder
        script_path = os.path.join(scripts_dir, script_filename)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        logger.info(f"📝 [{request_id}] Conversational script saved: {script_path}")
        
        # Move audio and video to organized folders
        audio_url = os.path.join(audio_dir, audio_filename)
        video_url = os.path.join(videos_dir, video_filename)
        
        shutil.move(audio_path, audio_url)
        shutil.move(video_path, video_url)
        
        # Also save to static dir for web access
        static_dir = "static"
        os.makedirs(static_dir, exist_ok=True)
        static_audio_url = os.path.join(static_dir, audio_filename)
        static_video_url = os.path.join(static_dir, video_filename)
        
        # Copy files to static directory for web access
        import shutil
        shutil.copy2(audio_url, static_audio_url)
        shutil.copy2(video_url, static_video_url)
        
        logger.info(f"✅ [{request_id}] Conversational reel generation completed successfully!")
        logger.info(f"📁 [{request_id}] Files saved to organized folders:")
        logger.info(f"📝 Script: {script_path}")
        logger.info(f"🎵 Audio: {audio_url}")
        logger.info(f"🎬 Video: {video_url}")
        logger.info(f"📊 [{request_id}] File sizes: Audio={os.path.getsize(audio_url)} bytes, Video={os.path.getsize(video_url)} bytes")
        
        return ReelResponse(
            script=script,
            audio_url=f"/download/{audio_filename}",
            video_url=f"/download/{video_filename}"
        )
    except Exception as e:
        logger.error(f"❌ [{request_id}] Error during conversational reel generation: {str(e)}")
        logger.error(f"❌ [{request_id}] Error type: {type(e).__name__}")
        logger.error(f"❌ [{request_id}] Full error details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-article-reel", response_model=ReelResponse)
async def generate_article_reel(article: ArticleInput):
    """
    Generate conversational reel from any article URL
    """
    request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Starting article reel generation process")
    logger.info(f"📄 [{request_id}] Input: URL={article.url}, Text length={len(article.text) if article.text else 0}")
    
    # EXTENSIVE LOGGING FOR SPEAKER_PAIR DEBUG
    logger.info(f"🎭 [{request_id}] DEBUGGING SPEAKER_PAIR:")
    logger.info(f"🎭 [{request_id}] - Raw article object: {article}")
    logger.info(f"🎭 [{request_id}] - article.speaker_pair value: {getattr(article, 'speaker_pair', 'NOT_FOUND')}")
    logger.info(f"🎭 [{request_id}] - article.__dict__: {article.__dict__}")
    logger.info(f"🎭 [{request_id}] - hasattr(article, 'speaker_pair'): {hasattr(article, 'speaker_pair')}")
    if hasattr(article, 'speaker_pair'):
        logger.info(f"🎭 [{request_id}] - Direct access article.speaker_pair: {article.speaker_pair}")
    else:
        logger.error(f"❌ [{request_id}] - SPEAKER_PAIR ATTRIBUTE NOT FOUND IN ARTICLE OBJECT!")
    
    try:
        # Step 1: Extract article content from URL
        logger.info(f"📖 [{request_id}] Step 1: Extracting article content")
        if article.url:
            logger.info(f"🌐 [{request_id}] Extracting from URL: {article.url}")
            article_data = await asyncio.get_event_loop().run_in_executor(None, extract_article_from_url, article.url)
            content = article_data['content']
            title = article_data['title']
            logger.info(f"📄 [{request_id}] Extracted content length: {len(content)} characters")
            logger.info(f"📝 [{request_id}] Article title: {title}")
        else:
            logger.info(f"📝 [{request_id}] Using provided text content")
            content = article.text
            title = article.title or "Article"
            logger.info(f"📄 [{request_id}] Content length: {len(content)} characters")
        
        # Step 2: Generate conversational script with speaker pair
        speaker_pair = getattr(article, 'speaker_pair', 'trump_mrbeast')  # Default to Trump & MrBeast
        logger.info(f"🤖 [{request_id}] Step 2: Generating conversational script for {speaker_pair}")
        logger.info(f"🎭 [{request_id}] SCRIPT GENERATION - Selected speaker_pair: {speaker_pair}")
        logger.info(f"🎭 [{request_id}] SCRIPT GENERATION - Calling generate_conversational_script with parameters:")
        logger.info(f"🎭 [{request_id}] - content length: {len(content)}")
        logger.info(f"🎭 [{request_id}] - speaker_pair: {speaker_pair}")
        loop = asyncio.get_event_loop()
        script = await loop.run_in_executor(None, generate_conversational_script, content, speaker_pair)
        logger.info(f"📜 [{request_id}] Conversational script generated successfully")
        logger.info(f"📜 [{request_id}] Script length: {len(script)} characters")
        logger.debug(f"📜 [{request_id}] Script preview: {script[:200]}...")
        
        # Step 3: Generate conversational audio with speaker pair
        speaker_pair = getattr(article, 'speaker_pair', 'trump_mrbeast')  # Default to Trump & MrBeast
        logger.info(f"🎵 [{request_id}] Step 3: Generating conversational audio with speaker pair: {speaker_pair}")
        audio_path, timing_data = await loop.run_in_executor(None, generate_conversational_voiceover, script, None, speaker_pair)
        logger.info(f"🎵 [{request_id}] Audio generated successfully: {audio_path}")
        
        # Step 4: Create conversational video with background and speaker overlays
        logger.info(f"🎬 [{request_id}] Step 4: Creating conversational video with background and speaker overlays")
        logger.info(f"🎭 [{request_id}] VIDEO GENERATION - Using speaker_pair: {speaker_pair}")
        video_path = await loop.run_in_executor(None, create_background_video_with_speaker_overlays, script, audio_path, None, None, speaker_pair, timing_data)
        logger.info(f"🎬 [{request_id}] Video with background created successfully: {video_path}")
        
        # Step 5: Save files to outputs directory
        logger.info(f"💾 [{request_id}] Step 5: Saving files to outputs directory")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        # Save script
        script_filename = f"article_script_{timestamp}.txt"
        script_path = os.path.join("outputs", script_filename)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\nURL: {article.url}\n\n{script}")
        logger.info(f"📝 [{request_id}] Script saved: {script_path}")
        
        # Save timeline
        from conversational_tts import create_speaker_timeline_with_timing_data
        timeline = create_speaker_timeline_with_timing_data(script, speaker_pair, timing_data)
        timeline_filename = f"article_timeline_{timestamp}.json"
        timeline_path = os.path.join("outputs", timeline_filename)
        import json
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        with open(timeline_path, 'w', encoding='utf-8') as f:
            json.dump(timeline, f, indent=2)
        logger.info(f"⏰ [{request_id}] Timeline saved: {timeline_path}")
        
        # Copy audio to outputs
        audio_filename = f"article_audio_{timestamp}.wav"
        audio_output_path = os.path.join("outputs", audio_filename)
        import shutil
        shutil.copy2(audio_path, audio_output_path)
        logger.info(f"🎵 [{request_id}] Audio saved: {audio_output_path}")
        
        # Copy video to outputs
        video_filename = f"article_video_{timestamp}.mp4"
        video_output_path = os.path.join("outputs", video_filename)
        shutil.copy2(video_path, video_output_path)
        logger.info(f"🎬 [{request_id}] Video saved: {video_output_path}")
        
        # Clean up temporary files
        try:
            os.remove(audio_path)
            os.remove(video_path)
            logger.debug(f"🗑️ [{request_id}] Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"⚠️ [{request_id}] Failed to clean up temporary files: {str(e)}")
        
        logger.info(f"✅ [{request_id}] Article reel generation completed successfully!")
        
        return ReelResponse(
            script=script,
            audio_url=f"/download/{audio_filename}",
            video_url=f"/download/{video_filename}"
        )
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Failed to generate article reel: {str(e)}")
        logger.error(f"❌ [{request_id}] Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Failed to generate article reel: {str(e)}")

@app.post("/generate-topic-reel", response_model=ReelResponse)
async def generate_topic_reel(topic_input: TopicInput):
    """
    Generate conversational reel from any topic by searching for relevant articles
    """
    request_id = f"topic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Starting topic reel generation process")
    logger.info(f"🎯 [{request_id}] Topic: {topic_input.topic}")
    logger.info(f"🎭 [{request_id}] Speaker pair: {topic_input.speaker_pair}")
    
    try:
        # Step 1: Search for articles about the topic
        logger.info(f"🔍 [{request_id}] Step 1: Searching for articles about '{topic_input.topic}'")
        loop = asyncio.get_event_loop()
        article_data = await loop.run_in_executor(None, search_and_extract_topic, topic_input.topic)
        
        if not article_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not find any good articles about '{topic_input.topic}'. Please try a different topic or be more specific."
            )
        
        content = article_data['content']
        title = article_data['title']
        source_url = article_data.get('url', 'Unknown')
        
        logger.info(f"✅ [{request_id}] Found article: {title}")
        logger.info(f"🌐 [{request_id}] Source URL: {source_url}")
        logger.info(f"📄 [{request_id}] Content length: {len(content)} characters")
        
        # Step 2: Generate conversational script with speaker pair
        speaker_pair = topic_input.speaker_pair
        logger.info(f"🤖 [{request_id}] Step 2: Generating conversational script for {speaker_pair}")
        script = await loop.run_in_executor(None, generate_conversational_script, content, speaker_pair)
        logger.info(f"📜 [{request_id}] Conversational script generated successfully")
        logger.info(f"📜 [{request_id}] Script length: {len(script)} characters")
        
        # Step 3: Generate conversational audio with speaker pair
        logger.info(f"🎵 [{request_id}] Step 3: Generating conversational audio with speaker pair: {speaker_pair}")
        audio_path, timing_data = await loop.run_in_executor(None, generate_conversational_voiceover, script, None, speaker_pair)
        logger.info(f"🎵 [{request_id}] Audio generated successfully: {audio_path}")
        
        # Step 4: Create conversational video with background and speaker overlays
        logger.info(f"🎬 [{request_id}] Step 4: Creating conversational video with background and speaker overlays")
        video_path = await loop.run_in_executor(None, create_background_video_with_speaker_overlays, script, audio_path, None, None, speaker_pair, timing_data)
        logger.info(f"🎬 [{request_id}] Video with background created successfully: {video_path}")
        
        # Step 5: Save files to outputs directory
        logger.info(f"💾 [{request_id}] Step 5: Saving files to outputs directory")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        # Save script with topic and source information
        script_filename = f"topic_script_{timestamp}.txt"
        script_path = os.path.join("outputs", script_filename)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f"Topic: {topic_input.topic}\n")
            f.write(f"Source Title: {title}\n")
            f.write(f"Source URL: {source_url}\n")
            f.write(f"Speaker Pair: {speaker_pair}\n")
            f.write(f"Search Rank: {article_data.get('search_rank', 'N/A')}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("\n" + "="*50 + "\n\n")
            f.write(script)
        logger.info(f"📝 [{request_id}] Script saved: {script_path}")
        
        # Save timeline
        from conversational_tts import create_speaker_timeline_with_timing_data
        timeline = create_speaker_timeline_with_timing_data(script, speaker_pair, timing_data)
        timeline_filename = f"topic_timeline_{timestamp}.json"
        timeline_path = os.path.join("outputs", timeline_filename)
        import json
        
        # Add metadata to timeline
        timeline_with_metadata = {
            "metadata": {
                "topic": topic_input.topic,
                "source_title": title,
                "source_url": source_url,
                "speaker_pair": speaker_pair,
                "search_rank": article_data.get('search_rank', 'N/A'),
                "generated": datetime.now().isoformat()
            },
            "timeline": timeline
        }
        
        with open(timeline_path, 'w', encoding='utf-8') as f:
            json.dump(timeline_with_metadata, f, indent=2)
        logger.info(f"⏰ [{request_id}] Timeline saved: {timeline_path}")
        
        # Copy audio to outputs
        audio_filename = f"topic_audio_{timestamp}.wav"
        audio_output_path = os.path.join("outputs", audio_filename)
        import shutil
        shutil.copy2(audio_path, audio_output_path)
        logger.info(f"🎵 [{request_id}] Audio saved: {audio_output_path}")
        
        # Copy video to outputs
        video_filename = f"topic_video_{timestamp}.mp4"
        video_output_path = os.path.join("outputs", video_filename)
        shutil.copy2(video_path, video_output_path)
        logger.info(f"🎬 [{request_id}] Video saved: {video_output_path}")
        
        # Clean up temporary files
        try:
            os.remove(audio_path)
            os.remove(video_path)
            logger.debug(f"🗑️ [{request_id}] Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"⚠️ [{request_id}] Failed to clean up temporary files: {str(e)}")
        
        logger.info(f"✅ [{request_id}] Topic reel generation completed successfully!")
        logger.info(f"🎯 [{request_id}] Topic: {topic_input.topic}")
        logger.info(f"📚 [{request_id}] Source: {title}")
        
        return ReelResponse(
            script=script,
            audio_url=f"/download/{audio_filename}",
            video_url=f"/download/{video_filename}"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"❌ [{request_id}] Failed to generate topic reel: {str(e)}")
        logger.error(f"❌ [{request_id}] Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Failed to generate topic reel: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    logger.info(f"📥 Download request for file: {filename}")
    
    # Check outputs directory first (for new API-generated files)
    outputs_path = os.path.join("outputs", filename)
    if os.path.exists(outputs_path):
        logger.info(f"✅ File found in outputs: {outputs_path}")
        return FileResponse(outputs_path)
    
    # Fallback to static directory (for legacy files)
    static_path = os.path.join("static", filename)
    if os.path.exists(static_path):
        logger.info(f"✅ File found in static: {static_path}")
        return FileResponse(static_path)
    
    logger.error(f"❌ File not found in outputs or static: {filename}")
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/files")
async def list_files():
    """List all stored files with their details"""
    try:
        files = []
        total_size = 0
        
        # Check both outputs and static directories
        directories = [
            ("outputs", "API Generated"),
            ("static", "Legacy")
        ]
        
        for dir_name, dir_label in directories:
            if os.path.exists(dir_name):
                for filename in os.listdir(dir_name):
                    file_path = os.path.join(dir_name, filename)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        
                        # Determine file type
                        if filename.endswith((".wav", ".mp3")):
                            file_type = "audio"
                        elif filename.endswith(".mp4"):
                            file_type = "video" 
                        elif filename.endswith(".txt"):
                            file_type = "script"
                        elif filename.endswith(".json"):
                            file_type = "timeline"
                        else:
                            file_type = "other"
                        
                        files.append({
                            "filename": filename,
                            "size_bytes": file_size,
                            "size_mb": round(file_size / 1024 / 1024, 2),
                            "type": file_type,
                            "source": dir_label,
                            "location": dir_name,
                            "download_url": f"/download/{filename}"
                        })
                        total_size += file_size
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x["filename"], reverse=True)
        
        logger.info(f"📁 Listed {len(files)} files, total size: {total_size} bytes")
        
        return {
            "files": files,
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }
    except Exception as e:
        logger.error(f"❌ Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a specific file"""
    try:
        file_path = os.path.join("static", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        file_size = os.path.getsize(file_path)
        os.remove(file_path)
        
        logger.info(f"🗑️ Deleted file: {filename} ({file_size} bytes)")
        
        return {
            "message": "File deleted successfully",
            "filename": filename,
            "size_bytes": file_size
        }
    except Exception as e:
        logger.error(f"❌ Error deleting file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.delete("/files")
async def clear_all_files():
    """Delete all stored files"""
    try:
        static_dir = "static"
        if not os.path.exists(static_dir):
            return {"message": "No files to delete", "deleted_count": 0}
        
        deleted_count = 0
        total_size = 0
        
        for filename in os.listdir(static_dir):
            file_path = os.path.join(static_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                deleted_count += 1
                total_size += file_size
        
        logger.info(f"🗑️ Deleted {deleted_count} files, total size: {total_size} bytes")
        
        return {
            "message": "All files deleted successfully",
            "deleted_count": deleted_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }
    except Exception as e:
        logger.error(f"❌ Error clearing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear files: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint - serve the frontend"""
    return FileResponse("static/index.html")

@app.get("/frontend")
async def serve_frontend():
    """Serve the main frontend"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    logger.info("🏥 Health check requested")
    return {"status": "healthy", "models_loaded": True}

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify app is working"""
    return {"message": "FastAPI app is working!", "timestamp": datetime.now().isoformat()}

@app.get("/speaker-pairs")
async def get_speaker_pairs():
    """Get available speaker pairs for frontend selection"""
    logger.info("🎭 Speaker pairs requested")
    return {
        "speaker_pairs": SPEAKER_PAIRS,
        "default": "trump_mrbeast"
    }


# Case Study Endpoints (Full Video Generation) - Legacy synchronous endpoints
@app.post("/generate-case-study")
async def generate_case_study_from_file(file: UploadFile = File(...), speaker_pair: str = Form(None)):
    """Generate case study summary, script, and FULL VIDEO from uploaded file"""
    request_id = f"casestudy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Starting case study processing from file: {file.filename}")
    logger.info(f"🔄 [{request_id}] Speaker pair: {speaker_pair}")
    
    try:
        if not file:
            logger.error(f"❌ [{request_id}] No file uploaded")
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        if not file.filename:
            logger.error(f"❌ [{request_id}] File has no filename")
            raise HTTPException(status_code=400, detail="File has no filename")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process case study file (summary, script, and video if speaker pair provided)
            logger.info(f"📚 [{request_id}] Processing case study file: {file.filename}")
            logger.info(f"🎭 [{request_id}] DEBUG - Speaker pair received: '{speaker_pair}'")
            case_study_data = process_case_study_file(temp_file_path, speaker_pair)
            
            # If speaker pair is provided, generate full video
            video_url = None
            audio_url = None
            logger.info(f"🎭 [{request_id}] DEBUG - Checking video generation conditions:")
            logger.info(f"🎭 [{request_id}] DEBUG - speaker_pair: '{speaker_pair}' (type: {type(speaker_pair)})")
            logger.info(f"🎭 [{request_id}] DEBUG - case_study_data['script']: '{case_study_data['script']}' (length: {len(case_study_data['script']) if case_study_data['script'] else 0})")
            logger.info(f"🎭 [{request_id}] DEBUG - Condition result: {bool(speaker_pair and case_study_data['script'])}")
            
            if speaker_pair and case_study_data["script"]:
                logger.info(f"🎬 [{request_id}] Generating full video for case study with speaker pair: {speaker_pair}")
                
                try:
                    # Step 1: Generate conversational audio
                    loop = asyncio.get_event_loop()
                    logger.info(f"🎵 [{request_id}] Starting audio generation...")
                    audio_path, timing_data = await loop.run_in_executor(
                        None, generate_conversational_voiceover, case_study_data["script"], None, speaker_pair
                    )
                    logger.info(f"🎵 [{request_id}] Case study audio generated: {audio_path}")
                    
                    # Step 2: Create video with speaker overlays
                    logger.info(f"🎬 [{request_id}] Starting video generation...")
                    video_path = await loop.run_in_executor(
                        None, create_background_video_with_speaker_overlays, 
                        case_study_data["script"], audio_path, None, None, speaker_pair, timing_data
                    )
                    logger.info(f"🎬 [{request_id}] Case study video created: {video_path}")
                    
                except Exception as video_error:
                    logger.error(f"❌ [{request_id}] Video generation failed: {str(video_error)}")
                    logger.error(f"❌ [{request_id}] Video generation error details: {type(video_error).__name__}")
                    import traceback
                    logger.error(f"❌ [{request_id}] Full traceback: {traceback.format_exc()}")
                    # Continue without video - just return script and summary
                    audio_path = None
                    video_path = None
                
                # Step 3: Save files to organized folder structure (only if video generation succeeded)
                if audio_path and video_path:
                    logger.info(f"💾 [{request_id}] Saving case study files to organized folders")
                    
                    # Create organized output directories
                    output_base = os.path.expanduser("~/Downloads/info_reeler_outputs")
                    scripts_dir = os.path.join(output_base, "case_studies", "scripts")
                    audio_dir = os.path.join(output_base, "case_studies", "audio")
                    videos_dir = os.path.join(output_base, "case_studies", "videos")
                    
                    for directory in [scripts_dir, audio_dir, videos_dir]:
                        os.makedirs(directory, exist_ok=True)
                    
                    # Create filenames with timestamp and request ID
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    script_filename = f"case_study_script_{timestamp}_{request_id}.txt"
                    audio_filename = f"case_study_audio_{timestamp}_{request_id}.wav"
                    video_filename = f"case_study_video_{timestamp}_{request_id}.mp4"
                    
                    # Save script to organized folder
                    script_path = os.path.join(scripts_dir, script_filename)
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(f"Case Study: {file.filename}\nSpeaker Pair: {speaker_pair}\n\nSUMMARY:\n{case_study_data['summary']}\n\nSCRIPT:\n{case_study_data['script']}")
                    logger.info(f"📝 [{request_id}] Case study script saved: {script_path}")
                    
                    # Move audio and video to organized folders
                    final_audio_path = os.path.join(audio_dir, audio_filename)
                    final_video_path = os.path.join(videos_dir, video_filename)
                    
                    shutil.move(audio_path, final_audio_path)
                    shutil.move(video_path, final_video_path)
                    
                    # Also save to static dir for web access
                    static_dir = "static"
                    os.makedirs(static_dir, exist_ok=True)
                    static_audio_path = os.path.join(static_dir, audio_filename)
                    static_video_path = os.path.join(static_dir, video_filename)
                    
                    # Copy files to static directory for web access
                    import shutil
                    shutil.copy2(final_audio_path, static_audio_path)
                    shutil.copy2(final_video_path, static_video_path)
                    
                    # Set URLs for response
                    video_url = f"/download/{video_filename}"
                    audio_url = f"/download/{audio_filename}"
                    
                    logger.info(f"✅ [{request_id}] Case study video generation completed successfully!")
                    logger.info(f"🎬 [{request_id}] Video: {video_url}")
                    logger.info(f"🎵 [{request_id}] Audio: {audio_url}")
                else:
                    logger.warning(f"⚠️ [{request_id}] Video generation failed, returning script only")
                    video_url = None
                    audio_url = None
            
            logger.info(f"✅ [{request_id}] Case study processing completed successfully")
            
            response_data = {
                "content": case_study_data["content"],
                "summary": case_study_data["summary"],
                "script": case_study_data["script"],
                "speaker_pair": speaker_pair,
                "processed_at": case_study_data["processed_at"],
                "video_url": video_url,
                "audio_url": audio_url,
                "status": "success" if video_url and audio_url else "partial_success"
            }
            
            logger.info(f"📤 [{request_id}] Returning response with status: {response_data['status']}")
            logger.info(f"📤 [{request_id}] Response keys: {list(response_data.keys())}")
            
            return response_data
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"❌ [{request_id}] Error during case study processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class CaseStudyTextRequest(BaseModel):
    text: str
    speaker_pair: str = None

@app.post("/generate-case-study-text")
async def generate_case_study_from_text(request: CaseStudyTextRequest):
    """Generate case study summary, script, and FULL VIDEO from text content"""
    request_id = f"casestudy_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Starting case study processing from text")
    
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="No text content provided")
        
        # Process case study text (summary, script, and video if speaker pair provided)
        speaker_pair = request.speaker_pair
        logger.info(f"📚 [{request_id}] Processing case study text: {len(request.text)} characters")
        logger.info(f"🎭 [{request_id}] DEBUG - Speaker pair received: '{speaker_pair}'")
        case_study_data = process_case_study_text(request.text, speaker_pair)
        
        # If speaker pair is provided, generate full video
        video_url = None
        audio_url = None
        logger.info(f"🎭 [{request_id}] DEBUG - Checking video generation conditions:")
        logger.info(f"🎭 [{request_id}] DEBUG - speaker_pair: '{speaker_pair}' (type: {type(speaker_pair)})")
        logger.info(f"🎭 [{request_id}] DEBUG - case_study_data['script']: '{case_study_data['script']}' (length: {len(case_study_data['script']) if case_study_data['script'] else 0})")
        logger.info(f"🎭 [{request_id}] DEBUG - Condition result: {bool(speaker_pair and case_study_data['script'])}")
        
        if speaker_pair and case_study_data["script"]:
            logger.info(f"🎬 [{request_id}] Generating full video for case study with speaker pair: {speaker_pair}")
            
            try:
                # Step 1: Generate conversational audio
                loop = asyncio.get_event_loop()
                logger.info(f"🎵 [{request_id}] Starting audio generation...")
                audio_path, timing_data = await loop.run_in_executor(
                    None, generate_conversational_voiceover, case_study_data["script"], None, speaker_pair
                )
                logger.info(f"🎵 [{request_id}] Case study audio generated: {audio_path}")
                
                # Step 2: Create video with speaker overlays
                logger.info(f"🎬 [{request_id}] Starting video generation...")
                video_path = await loop.run_in_executor(
                    None, create_background_video_with_speaker_overlays, 
                    case_study_data["script"], audio_path, None, None, speaker_pair, timing_data
                )
                logger.info(f"🎬 [{request_id}] Case study video created: {video_path}")
                
            except Exception as video_error:
                logger.error(f"❌ [{request_id}] Video generation failed: {str(video_error)}")
                logger.error(f"❌ [{request_id}] Video generation error details: {type(video_error).__name__}")
                import traceback
                logger.error(f"❌ [{request_id}] Full traceback: {traceback.format_exc()}")
                # Continue without video - just return script and summary
                audio_path = None
                video_path = None
            
            # Step 3: Save files to organized folder structure (only if video generation succeeded)
            if audio_path and video_path:
                logger.info(f"💾 [{request_id}] Saving case study files to organized folders")
                
                # Create organized output directories
                output_base = os.path.expanduser("~/Downloads/info_reeler_outputs")
                scripts_dir = os.path.join(output_base, "case_studies", "scripts")
                audio_dir = os.path.join(output_base, "case_studies", "audio")
                videos_dir = os.path.join(output_base, "case_studies", "videos")
                
                for directory in [scripts_dir, audio_dir, videos_dir]:
                    os.makedirs(directory, exist_ok=True)
                
                # Create filenames with timestamp and request ID
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                script_filename = f"case_study_script_{timestamp}_{request_id}.txt"
                audio_filename = f"case_study_audio_{timestamp}_{request_id}.wav"
                video_filename = f"case_study_video_{timestamp}_{request_id}.mp4"
                
                # Save script to organized folder
                script_path = os.path.join(scripts_dir, script_filename)
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(f"Case Study Text Input\nSpeaker Pair: {speaker_pair}\n\nSUMMARY:\n{case_study_data['summary']}\n\nSCRIPT:\n{case_study_data['script']}")
                logger.info(f"📝 [{request_id}] Case study script saved: {script_path}")
                
                # Move audio and video to organized folders
                final_audio_path = os.path.join(audio_dir, audio_filename)
                final_video_path = os.path.join(videos_dir, video_filename)
                
                shutil.move(audio_path, final_audio_path)
                shutil.move(video_path, final_video_path)
                
                # Also save to static dir for web access
                static_dir = "static"
                os.makedirs(static_dir, exist_ok=True)
                static_audio_path = os.path.join(static_dir, audio_filename)
                static_video_path = os.path.join(static_dir, video_filename)
                
                # Copy files to static directory for web access
                import shutil
                shutil.copy2(final_audio_path, static_audio_path)
                shutil.copy2(final_video_path, static_video_path)
                
                # Set URLs for response
                video_url = f"/download/{video_filename}"
                audio_url = f"/download/{audio_filename}"
                
                logger.info(f"✅ [{request_id}] Case study video generation completed successfully!")
                logger.info(f"🎬 [{request_id}] Video: {video_url}")
                logger.info(f"🎵 [{request_id}] Audio: {audio_url}")
            else:
                logger.warning(f"⚠️ [{request_id}] Video generation failed, returning script only")
                video_url = None
                audio_url = None
        
        logger.info(f"✅ [{request_id}] Case study text processing completed successfully")
        
        response_data = {
            "content": case_study_data["content"],
            "summary": case_study_data["summary"],
            "script": case_study_data["script"],
            "speaker_pair": speaker_pair,
            "processed_at": case_study_data["processed_at"],
            "video_url": video_url,
            "audio_url": audio_url,
            "status": "success" if video_url and audio_url else "partial_success"
        }
        
        logger.info(f"📤 [{request_id}] Returning response with status: {response_data['status']}")
        logger.info(f"📤 [{request_id}] Response keys: {list(response_data.keys())}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Error during case study text processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Quiz Endpoints
class QuizRequest(BaseModel):
    content: str
    video_data: dict = {}

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: list

@app.post("/generate-quiz")
async def generate_quiz(request: QuizRequest):
    """Generate quiz from case study content"""
    request_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Starting quiz generation")
    
    try:
        if not request.content:
            raise HTTPException(status_code=400, detail="No content provided for quiz generation")
        
        logger.info(f"🧠 [{request_id}] Generating quiz from content: {len(request.content)} characters")
        quiz_data = generate_quiz_from_content(request.content)
        
        # Save quiz data
        save_quiz_data(quiz_data)
        
        logger.info(f"✅ [{request_id}] Quiz generated successfully: {quiz_data['quiz_id']}")
        
        return quiz_data
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Error during quiz generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-quiz")
async def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    request_id = f"submit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Processing quiz submission: {submission.quiz_id}")
    
    try:
        # Load quiz data
        quiz_data = load_quiz_data(submission.quiz_id)
        
        # Calculate score
        logger.info(f"📊 [{request_id}] Calculating quiz score")
        results = calculate_quiz_score(quiz_data, submission.answers)
        
        logger.info(f"✅ [{request_id}] Quiz scored: {results['score']}/{results['total_questions']}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Error during quiz submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class TranslationRequest(BaseModel):
    text: str
    target_language: str

@app.post("/translate")
async def translate_content(request: TranslationRequest):
    """
    Translate text to specified language
    """
    request_id = f"translate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Translating text to {request.target_language}")
    
    try:
        # Translate the text
        translated_text = translate_text(request.text, request.target_language)
        
        logger.info(f"✅ [{request_id}] Translation completed successfully")
        
        return {
            "original_text": request.text,
            "translated_text": translated_text,
            "target_language": request.target_language,
            "request_id": request_id
        }
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Error during translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

class QuizTranslationRequest(BaseModel):
    quiz_id: str
    target_language: str

@app.post("/translate-quiz")
async def translate_quiz(request: QuizTranslationRequest):
    """
    Translate quiz questions and options to specified language
    """
    request_id = f"translate_quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"🔄 [{request_id}] Translating quiz {request.quiz_id} to {request.target_language}")
    
    try:
        # Load quiz data
        quiz_data = load_quiz_data(request.quiz_id)
        if not quiz_data:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Translate quiz title
        translated_title = translate_text(quiz_data['title'], request.target_language)
        
        # Translate questions and options
        translated_questions = []
        for question in quiz_data['questions']:
            translated_question = translate_text(question['question'], request.target_language)
            translated_options = [translate_text(option, request.target_language) for option in question['options']]
            
            translated_questions.append({
                'question': translated_question,
                'options': translated_options,
                'correct_answer': question['correct_answer']
            })
        
        # Create translated quiz data
        translated_quiz = {
            'quiz_id': quiz_data['quiz_id'],
            'title': translated_title,
            'questions': translated_questions,
            'total_questions': quiz_data['total_questions'],
            'created_at': quiz_data.get('created_at', ''),
            'language': request.target_language
        }
        
        logger.info(f"✅ [{request_id}] Quiz translation completed successfully")
        
        return translated_quiz
        
    except Exception as e:
        logger.error(f"❌ [{request_id}] Error during quiz translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quiz translation failed: {str(e)}") 
