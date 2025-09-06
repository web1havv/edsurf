#!/usr/bin/env python3
"""
Test script to verify case study video generation is working
"""

import requests
import json

def test_case_study_video_generation():
    """Test case study video generation with text input"""
    
    # Test data
    test_text = """
    This is a test case study about artificial intelligence and machine learning.
    AI has revolutionized many industries including healthcare, finance, and transportation.
    Machine learning algorithms can process vast amounts of data to identify patterns.
    Deep learning networks have achieved remarkable results in image recognition.
    Natural language processing has enabled chatbots and virtual assistants.
    The future of AI holds promise for solving complex global challenges.
    """
    
    speaker_pair = "trump_mrbeast"
    
    # API endpoint
    url = "http://localhost:8000/generate-case-study-text"
    
    # Request payload
    payload = {
        "text": test_text,
        "speaker_pair": speaker_pair
    }
    
    print("🧪 Testing case study video generation...")
    print(f"📝 Text length: {len(test_text)} characters")
    print(f"🎭 Speaker pair: {speaker_pair}")
    print(f"🌐 API endpoint: {url}")
    
    try:
        # Make the request
        response = requests.post(url, json=payload, timeout=300)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful!")
            print(f"📋 Summary present: {'summary' in data}")
            print(f"📜 Script present: {'script' in data}")
            print(f"🎬 Video URL present: {'video_url' in data}")
            print(f"🎵 Audio URL present: {'audio_url' in data}")
            
            if 'video_url' in data:
                print(f"🎬 Video URL: {data['video_url']}")
            if 'audio_url' in data:
                print(f"🎵 Audio URL: {data['audio_url']}")
            if 'script' in data:
                print(f"📜 Script length: {len(data['script'])} characters")
                print(f"📜 Script preview: {data['script'][:200]}...")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_case_study_video_generation()
