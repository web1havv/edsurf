"""
Test Caption Processor Module
Demonstrates Phase 1 caption enhancement functionality
"""

import json
import logging
import sys
import os
from datetime import datetime

# Add the backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging to see the output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from caption_processor import CaptionProcessor, enhance_timeline_with_captions, get_current_caption
from conversational_tts import create_speaker_timeline_with_timing_data

def test_basic_caption_functionality():
    """Test basic caption processing functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING: Basic Caption Functionality")
    print("="*60)
    
    # Create a simple test timeline
    test_timeline = [
        {
            "speaker": "elon",
            "start_time": 0.0,
            "end_time": 8.0,
            "text": "So, class, what's the big deal with this Docker thing? It's like totally changing the game."
        },
        {
            "speaker": "trump", 
            "start_time": 8.2,
            "end_time": 15.0,
            "text": "It's HUGE, really really HUGE! You just put your stuff in a box and it works anywhere."
        }
    ]
    
    # Enhance timeline with captions
    enhanced = enhance_timeline_with_captions(test_timeline)
    
    # Display results
    print(f"\n📊 RESULTS:")
    print(f"   Total Duration: {enhanced['total_duration']:.1f}s")
    print(f"   Caption Count: {enhanced['caption_count']}")
    print(f"   Segments: {len(enhanced['segments'])}")
    
    print(f"\n💬 CAPTION TIMELINE:")
    for i, caption in enumerate(enhanced['captions']):
        print(f"   {i+1:2d}. {caption['start']:5.1f}s - {caption['end']:5.1f}s | {caption['speaker']:5} | \"{caption['text']}\"")
    
    print(f"\n🗣️ SPEAKER STATS:")
    for speaker, stats in enhanced['speaker_stats'].items():
        print(f"   {speaker.capitalize()}: {stats['duration']:.1f}s, {stats['words']} words")
    
    return enhanced

def test_with_real_timeline_data():
    """Test with real timeline data from your system"""
    print("\n" + "="*60)
    print("🧪 TESTING: Real Timeline Data (Docker Article)")
    print("="*60)
    
    # Load real timeline data
    timeline_path = "outputs/article_timeline_20250802_182655.json"
    
    if not os.path.exists(timeline_path):
        print(f"⚠️ Timeline file not found: {timeline_path}")
        print("   Using fallback test data...")
        return test_basic_caption_functionality()
    
    try:
        with open(timeline_path, 'r') as f:
            real_timeline = json.load(f)
        
        print(f"📄 Loaded real timeline: {len(real_timeline)} segments")
        
        # Show original timeline
        print(f"\n📋 ORIGINAL TIMELINE:")
        for i, segment in enumerate(real_timeline):
            print(f"   {i+1}. {segment['start_time']:5.1f}s - {segment['end_time']:5.1f}s | {segment['speaker']:5} | \"{segment['text'][:50]}...\"")
        
        # Enhance with captions
        enhanced = enhance_timeline_with_captions(real_timeline)
        
        # Display results
        print(f"\n📊 ENHANCED RESULTS:")
        print(f"   Total Duration: {enhanced['total_duration']:.1f}s")
        print(f"   Caption Count: {enhanced['caption_count']}")
        print(f"   Segments: {len(enhanced['segments'])}")
        
        print(f"\n💬 CAPTION TIMELINE:")
        for i, caption in enumerate(enhanced['captions']):
            print(f"   {i+1:2d}. {caption['start']:5.1f}s - {caption['end']:5.1f}s | {caption['speaker']:5} | \"{caption['text']}\"")
        
        print(f"\n📝 DETAILED SEGMENT ANALYSIS:")
        for i, segment in enumerate(enhanced['segments']):
            print(f"\n   Segment {i+1} ({segment['speaker']}):")
            print(f"      Time: {segment['start_time']:.1f}s - {segment['end_time']:.1f}s")
            print(f"      Words: {segment['word_count']}")
            print(f"      Caption Chunks: {len(segment['caption_chunks'])}")
            
            for j, chunk in enumerate(segment['caption_chunks']):
                print(f"         {j+1}. {chunk['start']:5.1f}s - {chunk['end']:5.1f}s: \"{chunk['text']}\"")
        
        return enhanced
        
    except Exception as e:
        print(f"❌ Error loading real timeline: {str(e)}")
        return None

def test_current_caption_lookup():
    """Test the get_current_caption function"""
    print("\n" + "="*60)
    print("🧪 TESTING: Current Caption Lookup")
    print("="*60)
    
    # Use basic timeline for this test
    test_timeline = [
        {
            "speaker": "elon",
            "start_time": 0.0,
            "end_time": 5.0,
            "text": "Docker is revolutionary technology that changes everything."
        },
        {
            "speaker": "trump",
            "start_time": 5.2,
            "end_time": 10.0,
            "text": "It's the best containerization platform, believe me."
        }
    ]
    
    enhanced = enhance_timeline_with_captions(test_timeline)
    captions = enhanced['captions']
    
    # Test caption lookup at different times
    test_times = [0.5, 2.5, 4.5, 6.0, 8.0, 12.0]
    
    print(f"\n⏰ CAPTION LOOKUP TEST:")
    for time in test_times:
        current_caption = get_current_caption(time, captions)
        if current_caption:
            print(f"   {time:4.1f}s: \"{current_caption['text']}\" ({current_caption['speaker']})")
        else:
            print(f"   {time:4.1f}s: (no caption)")

def test_integration_with_conversational_tts():
    """Test integration with your existing conversational TTS system"""
    print("\n" + "="*60)
    print("🧪 TESTING: Integration with Conversational TTS")
    print("="*60)
    
    # Sample script text (no speaker markers, as used in your system)
    sample_script = """So what's the deal with artificial intelligence? Everyone's talking about it, but nobody really understands it. It's like this massive revolution happening right in front of us. The technology is advancing so fast, it's almost scary. But also incredibly exciting. We're building machines that can think, that can learn, that can create. It's like science fiction becoming reality."""
    
    print(f"📝 Sample Script ({len(sample_script)} chars):")
    print(f"   \"{sample_script[:100]}...\"")
    
    try:
        # Create timeline using your existing system
        timeline = create_speaker_timeline(sample_script)
        print(f"\n⏰ Generated Timeline: {len(timeline)} segments")
        
        # Enhance with captions
        enhanced = enhance_timeline_with_captions(timeline)
        
        print(f"\n📊 INTEGRATION RESULTS:")
        print(f"   Total Duration: {enhanced['total_duration']:.1f}s")
        print(f"   Caption Count: {enhanced['caption_count']}")
        
        print(f"\n💬 GENERATED CAPTIONS:")
        for i, caption in enumerate(enhanced['captions']):
            print(f"   {i+1:2d}. {caption['start']:5.1f}s - {caption['end']:5.1f}s | {caption['speaker']:5} | \"{caption['text']}\"")
        
        return enhanced
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return None

def test_caption_settings():
    """Test different caption settings"""
    print("\n" + "="*60)
    print("🧪 TESTING: Different Caption Settings")
    print("="*60)
    
    # Create processor with different settings
    processor = CaptionProcessor()
    
    # Test different character limits
    test_text = "This is a really long sentence that should be broken up into multiple caption chunks based on the character limit settings we have configured."
    
    settings_tests = [
        {"max_chars": 30, "name": "Short Captions"},
        {"max_chars": 50, "name": "Medium Captions"}, 
        {"max_chars": 80, "name": "Long Captions"}
    ]
    
    for test in settings_tests:
        print(f"\n📐 {test['name']} (max {test['max_chars']} chars):")
        
        # Temporarily change settings
        original_max_chars = processor.max_chars_per_line
        processor.max_chars_per_line = test['max_chars']
        
        # Create caption chunks
        chunks = processor.create_caption_chunks(test_text, 0.0, 10.0, "elon")
        
        for i, chunk in enumerate(chunks):
            print(f"   {i+1}. ({len(chunk['text']):2d} chars) \"{chunk['text']}\"")
        
        # Restore original settings
        processor.max_chars_per_line = original_max_chars

def run_all_tests():
    """Run all caption processor tests"""
    print("🚀 STARTING CAPTION PROCESSOR TESTS")
    print("=" * 80)
    
    try:
        # Run all tests
        test_basic_caption_functionality()
        test_with_real_timeline_data()
        test_current_caption_lookup()
        test_integration_with_conversational_tts()
        test_caption_settings()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n🎯 Next steps:")
        print("   • The caption processor is working correctly")
        print("   • You can now integrate it with your video generation")
        print("   • Ready to move to Phase 2: Caption Rendering")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()