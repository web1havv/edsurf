#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hardcoded Gemini API key
GEMINI_API_KEY = "AIzaSyBALLCySBJgG34579ZD3OehRoktbVyecGc"
print(f"🔑 Using hardcoded Gemini API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")

print("✅ Environment variables loaded successfully!")
print("🚀 Starting Info Reeler backend server...")

# Import and run the FastAPI app
from main import app
import uvicorn

if __name__ == "__main__":
    # Use Railway's PORT environment variable, fallback to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        timeout_keep_alive=30,  # Keep connections alive for 30 seconds
        timeout_graceful_shutdown=30  # Graceful shutdown timeout
    ) 