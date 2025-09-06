#!/usr/bin/env python3
"""
Test script for async video generation
Tests the new async endpoints to ensure they work properly on Render
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your Render URL for testing
TEST_CASE_STUDY_TEXT = """
Case Study: Tesla's Market Disruption

Tesla Inc. has revolutionized the automotive industry through its innovative approach to electric vehicles (EVs). Founded in 2003 by Elon Musk and others, Tesla has become a leading force in sustainable transportation.

Key Innovations:
1. Electric Vehicle Technology: Tesla developed advanced battery technology and electric powertrains that made EVs practical for everyday use.
2. Autonomous Driving: The company pioneered self-driving technology with its Autopilot system.
3. Direct Sales Model: Tesla bypassed traditional dealerships, selling directly to consumers.
4. Supercharger Network: Built a global network of fast-charging stations for long-distance travel.

Market Impact:
Tesla's success forced traditional automakers like Ford, GM, and BMW to accelerate their EV development programs. The company's market capitalization exceeded that of major automakers combined, demonstrating investor confidence in the future of electric transportation.

Challenges:
Despite its success, Tesla faces challenges including production scaling, quality control issues, and increasing competition from established automakers entering the EV market.

Future Outlook:
Tesla continues to expand into new markets including energy storage, solar panels, and potentially autonomous ride-sharing services, positioning itself as more than just an automotive company.
"""

def test_async_case_study_generation():
    """Test the async case study video generation"""
    print("🧪 Testing Async Case Study Video Generation")
    print("=" * 60)
    
    try:
        # Step 1: Health Check
        print("\n1. Testing Health Check...")
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    
        # Step 2: Start Async Job
        print("\n2. Starting Async Case Study Video Generation...")
        payload = {
            "text": TEST_CASE_STUDY_TEXT,
            "speaker_pair": "trump_elon"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/generate-case-study-text-async",
            json=payload,
            timeout=30  # Should complete quickly since it just starts the job
        )
        
        if response.status_code == 200:
            data = response.json()
            job_id = data["job_id"]
            print(f"✅ Async job started successfully!")
            print(f"📋 Job ID: {job_id}")
            print(f"📊 Status: {data['status']}")
            print(f"⏱️ Estimated time: {data['estimated_time']}")
        else:
            print(f"❌ Failed to start async job: {response.status_code}")
            print(f"Error: {response.text}")
            return False
        
        # Step 3: Poll Job Status
        print(f"\n3. Polling job status for: {job_id}")
        max_attempts = 60  # 5 minutes max
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            print(f"\n📊 Polling attempt {attempts}/{max_attempts}...")
            
            try:
                response = requests.get(f"{BASE_URL}/job-status/{job_id}", timeout=10)
                
                if response.status_code == 200:
                    job_status = response.json()
                    print(f"📈 Progress: {job_status['progress']}%")
                    print(f"📊 Status: {job_status['status']}")
                    
                    if job_status['status'] == 'completed':
                        end_time = time.time()
                        total_time = end_time - start_time
                        
                        print(f"\n✅ Job completed successfully!")
                        print(f"⏱️ Total time: {total_time:.2f} seconds")
                        print(f"📊 Final result keys: {list(job_status['result'].keys())}")
                        
                        result = job_status['result']
                        print(f"📝 Script length: {len(result.get('script', ''))}")
                        print(f"🎵 Audio URL: {result.get('audio_url', 'N/A')}")
                        print(f"🎬 Video URL: {result.get('video_url', 'N/A')}")
                        
                        return True
                        
                    elif job_status['status'] == 'failed':
                        print(f"❌ Job failed: {job_status.get('error', 'Unknown error')}")
                        return False
                        
                    else:
                        print(f"⏳ Job still processing...")
                        time.sleep(5)  # Wait 5 seconds before next poll
                        
                else:
                    print(f"⚠️ Failed to get job status: {response.status_code}")
                    time.sleep(5)
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Request error: {e}")
                time.sleep(5)
        
        print(f"\n⏰ Polling timeout after {max_attempts} attempts")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_job_listing():
    """Test the job listing endpoint"""
    print("\n" + "=" * 60)
    print("📋 Testing Job Listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/jobs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Job listing successful")
            print(f"📊 Total jobs: {data['total_jobs']}")
            print(f"🔄 Active jobs: {data['active_jobs']}")
            
            if data['jobs']:
                print("\n📋 Recent jobs:")
                for job in data['jobs'][:3]:  # Show first 3 jobs
                    print(f"  - {job['job_id'][:8]}... ({job['status']}) - {job['task_type']}")
            
            return True
        else:
            print(f"❌ Failed to list jobs: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Job listing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Async Video Generation Test Suite")
    print(f"🌐 Testing against: {BASE_URL}")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    
    # Test 1: Async generation
    success1 = test_async_case_study_generation()
    
    # Test 2: Job listing
    success2 = test_job_listing()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Async Generation: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Job Listing: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Async video generation is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
