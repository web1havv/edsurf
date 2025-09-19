#!/usr/bin/env python3
"""
Render entry point for Info Reeler
This file is specifically designed for Render deployment with better error handling
"""
import os
import sys
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Hardcoded Gemini API key
GEMINI_API_KEY = "AIzaSyBALLCySBJgG34579ZD3OehRoktbVyecGc"
logger.info(f"🔑 Using hardcoded Gemini API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")

logger.info("✅ Environment variables loaded successfully!")

# Check FFmpeg availability
try:
    from conversational_tts import check_ffmpeg_availability
    ffmpeg_status = check_ffmpeg_availability()
    if ffmpeg_status:
        logger.info(f"✅ FFmpeg check completed: {ffmpeg_status}")
    else:
        logger.warning("⚠️ FFmpeg not available - audio processing will fail")
except Exception as e:
    logger.warning(f"⚠️ Could not check FFmpeg availability: {str(e)}")

logger.info("🚀 Starting Info Reeler backend server on Render...")

try:
    # Import uvicorn first
    import uvicorn
    logger.info("✅ Uvicorn imported successfully")
    
    # Try to import the app with better error handling
    logger.info("📦 Importing FastAPI app...")
    from main import app
    logger.info("✅ FastAPI app imported successfully")
    
    # Use Render's PORT environment variable, fallback to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🌐 Starting server on port {port}")
    logger.info(f"🌐 Host: 0.0.0.0")
    
    # Start the server with proper configuration for Render
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        access_log=True,
        timeout_keep_alive=30,
        timeout_graceful_shutdown=30
    )
    
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error("This might be due to missing dependencies. Check the build logs.")
    logger.error("Make sure all packages in requirements.txt are installed.")
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Startup error: {e}")
    logger.error("Check the logs above for more details.")
    sys.exit(1)
