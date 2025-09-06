#!/usr/bin/env python3
"""
Simple test to check if the health endpoint works
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import app
    print("✅ Successfully imported app from main.py")
    
    # Test the health endpoint
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    print(f"✅ Health endpoint response: {response.status_code}")
    print(f"✅ Health endpoint data: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
