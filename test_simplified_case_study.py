#!/usr/bin/env python3
"""
Test script for the Simplified Case Study Platform
Tests summary generation and quiz functionality (no video generation)
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000"
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

def test_simplified_case_study_platform():
    """Test the simplified case study platform functionality"""
    print("🧪 Testing Simplified Case Study Platform")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Case Study Text Processing (Summary Only)
    print("\n2. Testing Case Study Text Processing...")
    try:
        payload = {
            "text": TEST_CASE_STUDY_TEXT,
            "speaker_pair": "trump_elon"
        }
        
        response = requests.post(
            f"{BASE_URL}/generate-case-study-text",
            json=payload,
            timeout=60  # 1 minute timeout for processing
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Case study text processing successful")
            print(f"📊 Content length: {len(data.get('content', ''))}")
            print(f"📋 Summary length: {len(data.get('summary', ''))}")
            print(f"📜 Script length: {len(data.get('script', ''))}")
            print(f"🎭 Speaker pair: {data.get('speaker_pair', 'N/A')}")
            
            # Display summary preview
            summary = data.get('summary', '')
            if summary:
                print(f"\n📋 Summary Preview:")
                print(f"   {summary[:200]}...")
            
            # Store content for quiz generation
            case_study_content = data.get('content', '')
            
        else:
            print(f"❌ Case study processing failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Case study processing error: {e}")
        return False
    
    # Test 3: Quiz Generation
    print("\n3. Testing Quiz Generation...")
    try:
        payload = {
            "content": case_study_content,
            "video_data": {}
        }
        
        response = requests.post(
            f"{BASE_URL}/generate-quiz",
            json=payload,
            timeout=60  # 1 minute timeout
        )
        
        if response.status_code == 200:
            quiz_data = response.json()
            print("✅ Quiz generation successful")
            print(f"📊 Quiz ID: {quiz_data.get('quiz_id', 'N/A')}")
            print(f"📝 Title: {quiz_data.get('title', 'N/A')}")
            print(f"❓ Questions: {len(quiz_data.get('questions', []))}")
            
            # Display first question as example
            if quiz_data.get('questions'):
                first_q = quiz_data['questions'][0]
                print(f"\n📋 Sample Question:")
                print(f"   Q: {first_q.get('question', 'N/A')}")
                print(f"   Options: {first_q.get('options', [])}")
                print(f"   Correct: {first_q.get('correct_answer', 'N/A')}")
            
            # Store quiz data for submission test
            quiz_id = quiz_data.get('quiz_id')
            
        else:
            print(f"❌ Quiz generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Quiz generation error: {e}")
        return False
    
    # Test 4: Quiz Submission
    print("\n4. Testing Quiz Submission...")
    try:
        # Create sample answers (all correct for testing)
        sample_answers = {}
        for i, question in enumerate(quiz_data.get('questions', [])):
            sample_answers[i] = question.get('correct_answer', 0)
        
        payload = {
            "quiz_id": quiz_id,
            "answers": sample_answers
        }
        
        response = requests.post(
            f"{BASE_URL}/submit-quiz",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Quiz submission successful")
            print(f"📊 Score: {results.get('score', 0)}/{results.get('total_questions', 0)}")
            print(f"📈 Percentage: {results.get('percentage', 0)}%")
            print(f"⏰ Submitted at: {results.get('submitted_at', 'N/A')}")
            
        else:
            print(f"❌ Quiz submission failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Quiz submission error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! Simplified Case Study Platform is working correctly!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Simplified Case Study Platform Tests")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    success = test_simplified_case_study_platform()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Click on the '📚 Case Study' tab")
        print("3. Upload a PDF or paste case study text")
        print("4. Select a speaker pair")
        print("5. Click 'Generate Case Study Summary'")
        print("6. Click 'Start Quiz' to test the quiz functionality")
        print("\n🎯 Current Features:")
        print("✅ PDF/Text upload and processing")
        print("✅ AI-generated case study summaries")
        print("✅ Conversational script generation")
        print("✅ Interactive quiz with 5 questions")
        print("✅ Scorecard with detailed results")
        print("\n🚀 Video generation will be added in the next phase!")
    else:
        print("\n❌ Tests failed. Please check the backend server and try again.")
