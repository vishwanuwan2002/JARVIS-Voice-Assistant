#!/usr/bin/env python3
"""
Performance test script for JARVIS
Tests response times for various operations
"""

import time
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Jarvis.features import intelligent_ai
from Jarvis.features import tts
from Jarvis import JarvisAssistant

def test_ai_response_caching():
    """Test AI response caching performance"""
    print("Testing AI response caching...")

    # Test query
    test_query = "What is Python?"

    # First call (should be slower)
    start_time = time.time()
    response1 = intelligent_ai.ask_ai(test_query, use_history=False)
    first_call_time = time.time() - start_time

    # Second call (should be faster due to caching)
    start_time = time.time()
    response2 = intelligent_ai.ask_ai(test_query, use_history=False)
    second_call_time = time.time() - start_time

    print(".2f")
    print(".2f")
    print(".1f")

    return first_call_time, second_call_time

def test_tts_providers():
    """Test TTS provider performance"""
    print("\nTesting TTS providers...")

    test_text = "Hello, this is a test of the text to speech system."

    # Test pyttsx3 (current fallback)
    try:
        start_time = time.time()
        success = tts.speak(test_text)
        pyttsx3_time = time.time() - start_time
        print(".2f")
    except Exception as e:
        print(f"pyttsx3 test failed: {e}")
        pyttsx3_time = None

    return pyttsx3_time

def test_stt_timeout():
    """Test STT timeout settings"""
    print("\nTesting STT timeout settings...")

    obj = JarvisAssistant()

    # Test mic input timeout (will timeout since no speech)
    start_time = time.time()
    result = obj.mic_input()
    stt_time = time.time() - start_time

    print(".2f")
    print(f"Result: {result}")

    return stt_time

def main():
    print("JARVIS Performance Test Suite")
    print("=" * 40)

    # Test AI caching
    try:
        first_time, second_time = test_ai_response_caching()
    except Exception as e:
        print(f"AI caching test failed: {e}")

    # Test TTS
    try:
        tts_time = test_tts_providers()
    except Exception as e:
        print(f"TTS test failed: {e}")

    # Test STT timeout
    try:
        stt_timeout = test_stt_timeout()
    except Exception as e:
        print(f"STT test failed: {e}")

    print("\nPerformance Test Complete")
    print("To enable ElevenLabs TTS, add your ELEVENLABS_API_KEY to .env")
    print("To enable local Whisper STT, set WHISPER_MODEL_PATH in .env")

if __name__ == "__main__":
    main()