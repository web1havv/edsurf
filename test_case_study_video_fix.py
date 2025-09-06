#!/usr/bin/env python3
"""
Test script to verify case study video generation is working
"""

import requests
import json
import time

def test_case_study_video_generation():
    """Test the case study video generation endpoint"""
    
    # Test data
    test_text = """
    This is a test case study about artificial intelligence and its impact on modern business. 
    AI is transforming industries by automating processes, providing insights from data, and 
    enabling new business models. Companies are using AI to improve customer service, optimize 
    supply chains, and make better decisions. The technology is becoming more accessible and 
    affordable, allowing small businesses to compete with larger enterprises.
    """
    
    speaker_pair = "trump_elon"
    
    print("🧪 Testing case study video generation...")
    print(f"📝 Test text length: {len(test_text)} characters")
    print(f"🎭 Speaker pair: {speaker_pair}")
    
    # Make API request
    url = "http://localhost:8000/generate-case-study-text"
    payload = {
        "text": test_text,
        "speaker_pair": speaker_pair
    }
    
    try:
        print("🌐 Making API request...")
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API request successful!")
            print(f"📊 Response keys: {list(data.keys())}")
            
            if "video_url" in data and data["video_url"]:
                print(f"🎬 Video generated successfully: {data['video_url']}")
                print(f"🎵 Audio generated: {data.get('audio_url', 'N/A')}")
                return True
            else:
                print("❌ No video URL in response - video generation failed")
                print(f"📜 Script generated: {len(data.get('script', ''))} characters")
                return False
                
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - video generation might be taking too long")
        return False
    except Exception as e:
        print(f"❌ Error during API request: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_case_study_video_generation()
    if success:
        print("\n🎉 Case study video generation is working!")
    else:
        print("\n💥 Case study video generation needs fixing")
