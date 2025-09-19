#!/usr/bin/env python3
"""
Vercel entry point for Info Reeler
This file is specifically designed for Vercel deployment
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Hardcoded Gemini API key with fallback
GEMINI_API_KEY = "AIzaSyBALLCySBJgG34579ZD3OehRoktbVyecGc"
FALLBACK_API_KEY = "AIzaSyBjjwI_efGOFQvijmHfP3N7coYgzEonp5s"

# Check for required API keys (Vercel will provide these via environment variables)
# If not found, use hardcoded fallback
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️ Warning: GEMINI_API_KEY environment variable not found!")
    print("Using hardcoded fallback API key")
    print(f"🔑 Using hardcoded Gemini API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
    print(f"🔑 Fallback Gemini API Key available: {FALLBACK_API_KEY[:10]}...{FALLBACK_API_KEY[-4:]}")
else:
    print(f"🔑 Using environment GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:10]}...{os.getenv('GEMINI_API_KEY')[-4:]}")
    print(f"🔑 Fallback Gemini API Key available: {FALLBACK_API_KEY[:10]}...{FALLBACK_API_KEY[-4:]}")

print("✅ Environment variables loaded successfully!")
print("🚀 Starting Info Reeler backend server on Vercel...")

# Import and run the FastAPI app
from main import app

# For Vercel, we need to export the app directly
# Vercel will handle the server startup
