#!/usr/bin/env python3
"""
Simple Info Reeler Test
Tests the simplified system with clean scripts and Trump voice
"""

import requests
import json
import time
import os
from datetime import datetime

def test_simple_generation():
    """Test the simplified Info Reeler system"""
    
    print("🧪 Testing Simplified Info Reeler System")
    print("=" * 60)
    print("🎤 Trump Voice TTS + Clean Scripts + Constant Image")
    print()
    
    # Test article
    test_content = """
    Artificial Intelligence (AI) is transforming the world as we know it. 
    From self-driving cars to virtual assistants, AI is becoming increasingly 
    integrated into our daily lives. Machine learning algorithms can now 
    process vast amounts of data to make predictions and decisions that 
    were once impossible. Companies are using AI to improve customer 
    service, optimize operations, and create innovative products. 
    However, this rapid advancement also raises important questions about 
    privacy, job displacement, and ethical considerations. As we move 
    forward, it's crucial to develop AI responsibly while harnessing 
    its potential to solve complex global challenges.
    """
    
    print("📝 Test Content:")
    print(f"   Length: {len(test_content)} characters")
    print(f"   Topics: AI, Machine Learning, Technology")
    print()
    
    # API endpoint
    url = "http://localhost:8000/generate-reel"
    
    # Request payload
    payload = {
        "text": test_content,
        "title": "The Future of Artificial Intelligence"
    }
    
    print("🚀 Starting generation process...")
    print("⏱️ This may take 1-2 minutes...")
    print()
    
    try:
        # Make the request
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Generation completed successfully!")
            print(f"⏱️ Total time: {end_time - start_time:.2f} seconds")
            print()
            
            # Display results
            print("📊 Generation Results:")
            print(f"   📝 Script length: {len(result.get('script', ''))} characters")
            print(f"   🖼️ Images generated: {len(result.get('images', []))}")
            print(f"   🎵 Audio URL: {result.get('audio_url', 'N/A')}")
            print(f"   🎬 Video URL: {result.get('video_url', 'N/A')}")
            print()
            
            # Show clean script preview
            script = result.get('script', '')
            if script:
                print("📜 Clean Script Preview:")
                lines = script.split('\n')[:5]  # Show first 5 lines
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        print(f"   {i}. {line[:80]}{'...' if len(line) > 80 else ''}")
                print()
            
            return True
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (took longer than 5 minutes)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("Make sure the backend is running: cd backend && python3 run.py")
        return False
    except Exception as e:
        print(f"❌ Error during generation: {str(e)}")
        return False

def check_simple_outputs():
    """Check the organized outputs after simple generation"""
    
    print("📁 Checking Simple Organized Outputs...")
    print("=" * 60)
    
    output_base = os.path.expanduser("~/Downloads/info_reeler_outputs")
    
    if not os.path.exists(output_base):
        print("❌ Output folder not found!")
        return False
    
    folders = {
        "📝 Scripts": "scripts",
        "🖼️ Images": "images", 
        "🎵 Audio": "audio",
        "🎬 Videos": "videos"
    }
    
    total_files = 0
    new_files = 0
    
    for folder_name, folder_path in folders.items():
        full_path = os.path.join(output_base, folder_path)
        
        if not os.path.exists(full_path):
            print(f"{folder_name}: ❌ Folder not found")
            continue
            
        files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
        file_count = len(files)
        total_files += file_count
        
        # Check for new files (created in last 5 minutes)
        current_time = time.time()
        new_files_in_folder = 0
        
        for file in files:
            file_path = os.path.join(full_path, file)
            file_time = os.path.getmtime(file_path)
            if current_time - file_time < 300:  # 5 minutes
                new_files_in_folder += 1
                new_files += 1
        
        print(f"{folder_name}:")
        print(f"   📂 Path: {full_path}")
        print(f"   📊 Total files: {file_count}")
        print(f"   🆕 New files: {new_files_in_folder}")
        
        if new_files_in_folder > 0:
            print("   📄 New files:")
            for file in files:
                file_path = os.path.join(full_path, file)
                file_time = os.path.getmtime(file_path)
                if current_time - file_time < 300:  # 5 minutes
                    size = os.path.getsize(file_path)
                    size_mb = size / 1024 / 1024
                    mtime = datetime.fromtimestamp(file_time)
                    print(f"      • {file} ({size_mb:.1f}MB) - {mtime.strftime('%H:%M:%S')}")
        
        print()
    
    print("=" * 60)
    print(f"📊 Total files: {total_files}")
    print(f"🆕 New files generated: {new_files}")
    
    if new_files > 0:
        print("🎉 Success! New content was generated with simplified system!")
        return True
    else:
        print("⚠️ No new files detected. Check if generation completed successfully.")
        return False

def main():
    """Main test function"""
    
    print("🎬 Simplified Info Reeler System Test")
    print("=" * 60)
    print("🔧 Testing with clean scripts and Trump voice")
    print()
    
    # Step 1: Test simple generation
    print("🔧 Step 1: Testing simplified content generation...")
    success = test_simple_generation()
    
    if not success:
        print("❌ Generation test failed!")
        return
    
    print()
    
    # Step 2: Check organized outputs
    print("🔧 Step 2: Checking organized outputs...")
    check_simple_outputs()
    
    print()
    print("🎉 Simplified test completed!")
    print("💡 Check your organized outputs in: ~/Downloads/info_reeler_outputs/")
    print("🎤 Audio should now have Trump voice or fallback TTS")
    print("📝 Scripts should be clean without annotations")
    print("🖼️ Images should be constant background")

if __name__ == "__main__":
    main() 