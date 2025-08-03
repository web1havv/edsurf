#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required API keys
if not os.getenv("GEMINI_API_KEY"):
    print("❌ Error: GEMINI_API_KEY environment variable is required!")
    print("Please create a .env file with your API keys:")
    print("GEMINI_API_KEY=your_gemini_api_key_here")
    sys.exit(1)

print("✅ Environment variables loaded successfully!")
print("🚀 Starting Info Reeler backend server...")

# Import and run the FastAPI app
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 