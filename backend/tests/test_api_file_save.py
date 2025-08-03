#!/usr/bin/env python3
"""
Test API File Saving
Verify that the API properly saves all outputs to the outputs directory
"""

import os
import sys
import logging
import requests
import json
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_api_file_saving():
    """Test that API saves all files to outputs directory"""
    try:
        logger.info("📁 Testing API file saving to outputs directory...")
        
        # Check if outputs directory exists and list current files
        if os.path.exists("outputs"):
            before_files = set(os.listdir("outputs"))
            logger.info(f"📂 Files in outputs before API call: {len(before_files)}")
        else:
            before_files = set()
            logger.info("📂 Outputs directory doesn't exist yet")
        
        # Test article reel generation with a simple article
        test_data = {
            "text": "Artificial Intelligence is rapidly transforming industries worldwide. Machine learning algorithms are becoming more sophisticated and can now perform complex tasks that were once thought impossible for computers.",
            "title": "AI Revolution Test Article"
        }
        
        logger.info("🚀 Making API request to /generate-article-reel...")
        logger.info(f"📄 Test article: {len(test_data['text'])} characters")
        
        # Make API request (assuming server is running on localhost:8000)
        response = requests.post(
            "http://localhost:8000/generate-article-reel",
            json=test_data,
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ API request successful!")
            logger.info(f"📝 Script length: {len(result['script'])} characters")
            logger.info(f"🎵 Audio URL: {result['audio_url']}")
            logger.info(f"🎬 Video URL: {result['video_url']}")
            
            # Check outputs directory after API call
            if os.path.exists("outputs"):
                after_files = set(os.listdir("outputs"))
                new_files = after_files - before_files
                
                logger.info(f"📂 Files in outputs after API call: {len(after_files)}")
                logger.info(f"🆕 New files created: {len(new_files)}")
                
                # List new files
                for filename in sorted(new_files):
                    file_path = os.path.join("outputs", filename)
                    file_size = os.path.getsize(file_path)
                    
                    # Determine file type
                    if filename.endswith((".wav", ".mp3")):
                        file_type = "🎵 Audio"
                    elif filename.endswith(".mp4"):
                        file_type = "🎬 Video"
                    elif filename.endswith(".txt"):
                        file_type = "📝 Script"
                    elif filename.endswith(".json"):
                        file_type = "⏰ Timeline"
                    else:
                        file_type = "📄 Other"
                    
                    logger.info(f"   {file_type}: {filename} ({file_size} bytes, {file_size/1024/1024:.2f} MB)")
                
                # Expected file types
                expected_types = [".txt", ".json", ".wav", ".mp4"]
                found_types = []
                
                for filename in new_files:
                    for ext in expected_types:
                        if filename.endswith(ext):
                            found_types.append(ext)
                            break
                
                logger.info(f"✅ File types found: {found_types}")
                logger.info(f"🎯 Expected types: {expected_types}")
                
                if len(found_types) >= 4:  # Script, timeline, audio, video
                    logger.info("🎉 SUCCESS: All expected file types created!")
                    return True
                else:
                    logger.warning(f"⚠️ Missing some file types. Found {len(found_types)}/4")
                    return False
            else:
                logger.error("❌ Outputs directory not created")
                return False
        else:
            logger.error(f"❌ API request failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Could not connect to API. Make sure server is running on localhost:8000")
        logger.info("💡 Start the server with: python main.py")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

def test_files_endpoint():
    """Test the /files endpoint to see all saved files"""
    try:
        logger.info("📋 Testing /files endpoint...")
        
        response = requests.get("http://localhost:8000/files", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Files endpoint working!")
            logger.info(f"📁 Total files: {data.get('total_files', 0)}")
            logger.info(f"💾 Total size: {data.get('total_size_mb', 0):.2f} MB")
            
            files = data.get('files', [])
            
            # Group files by type
            file_types = {}
            for file_info in files:
                file_type = file_info.get('type', 'unknown')
                if file_type not in file_types:
                    file_types[file_type] = []
                file_types[file_type].append(file_info)
            
            logger.info("📊 Files by type:")
            for file_type, type_files in file_types.items():
                logger.info(f"   {file_type}: {len(type_files)} files")
            
            return True
        else:
            logger.error(f"❌ Files endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Files endpoint test failed: {str(e)}")
        return False

def main():
    """Run file saving tests"""
    logger.info("🧪 Starting API File Saving Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Files Endpoint", test_files_endpoint),
        ("API File Saving", test_api_file_saving),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            logger.error(f"❌ FAILED: {test_name} - {str(e)}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n🎯 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! API file saving is working correctly!")
        logger.info("📁 All outputs are being saved to the outputs directory!")
    else:
        logger.info("❌ Some tests failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)