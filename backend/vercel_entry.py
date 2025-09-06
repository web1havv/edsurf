#!/usr/bin/env python3
"""
Vercel entry point for Info Reeler
This file is specifically designed for Vercel deployment
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check for required API keys (Vercel will provide these via environment variables)
if not os.getenv("GEMINI_API_KEY"):
    print("❌ Error: GEMINI_API_KEY environment variable is required!")
    print("Please set the GEMINI_API_KEY environment variable in Vercel dashboard")
    sys.exit(1)

print("✅ Environment variables loaded successfully!")
print("🚀 Starting Info Reeler backend server on Vercel...")

# Import and run the FastAPI app
from main import app

# For Vercel, we need to export the app directly
# Vercel will handle the server startup
