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

# Check for required API keys
if not os.getenv("GEMINI_API_KEY"):
    logger.error("❌ Error: GEMINI_API_KEY environment variable is required!")
    logger.error("Please set the GEMINI_API_KEY environment variable in Render dashboard")
    sys.exit(1)

logger.info("✅ Environment variables loaded successfully!")
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
