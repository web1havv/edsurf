#!/usr/bin/env python3
"""
Simple FastAPI app for Railway deployment
This is a minimal version to test if the basic setup works
"""
import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Info Reeler API - Simple Version")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Info Reeler API is running!", "status": "ok"}

@app.get("/health")
async def health_check():
    logger.info("🏥 Health check requested")
    return {"status": "healthy", "message": "API is running"}

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working", "port": os.getenv("PORT", "8000")}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting simple app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
