#!/usr/bin/env python3
"""
Test script to verify dialogue length restrictions are working properly
"""

import sys
import os
sys.path.append('backend')

from backend.llm import generate_conversational_script, validate_and_trim_script

def test_script_length_restrictions():
    """Test that all speaker pairs generate scripts within length limits"""
    
    test_article = """
    Artificial Intelligence is transforming the way businesses operate. Companies are using AI to automate processes, 
    analyze data, and improve customer experiences. Machine learning algorithms can identify patterns in large datasets 
    that humans might miss. This technology is being applied across various industries including healthcare, finance, 
    and manufacturing. The key to successful AI implementation is having quality data and clear objectives.
    """
    
    speaker_pairs = [
        "trump_elon",
        "baburao_samay", 
        "samay_arpit",
        "modi_trump",
        "trump_mrbeast"
    ]
    
    print("🧪 Testing dialogue length restrictions for all speaker pairs...")
    print("=" * 60)
    
    for speaker_pair in speaker_pairs:
        print(f"\n🎭 Testing {speaker_pair}...")
        try:
            # Generate script
            script = generate_conversational_script(test_article, speaker_pair)
            
            # Calculate stats
            word_count = len(script.split())
            estimated_duration = word_count / 2.5  # 150 words per minute
            
            print(f"📊 Generated script stats:")
            print(f"   - Word count: {word_count}")
            print(f"   - Estimated duration: {estimated_duration:.1f} seconds")
            print(f"   - Length status: {'✅ GOOD' if 45 <= estimated_duration <= 75 else '⚠️ OUT OF RANGE'}")
            
            # Show preview
            preview = script[:150] + "..." if len(script) > 150 else script
            print(f"   - Preview: {preview}")
            
        except Exception as e:
            print(f"❌ Error testing {speaker_pair}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Length restriction testing completed!")

if __name__ == "__main__":
    test_script_length_restrictions()
