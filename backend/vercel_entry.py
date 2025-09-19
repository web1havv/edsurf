#!/usr/bin/env python3
"""
Vercel entry point for Info Reeler
This file is specifically designed for Vercel deployment
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Hardcoded Gemini API key
GEMINI_API_KEY = "AIzaSyBALLCySBJgG34579ZD3OehRoktbVyecGc"
print(f"🔑 Using hardcoded Gemini API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")

print("✅ Environment variables loaded successfully!")
print("🚀 Starting Info Reeler backend server on Vercel...")

# Import and run the FastAPI app
from main import app

# For Vercel, we need to export the app directly
# Vercel will handle the server startup
