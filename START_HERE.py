#!/usr/bin/env python3
"""
ONE-CLICK FIX SCRIPT FOR JARVIS
This script fixes the most common issues automatically.
"""

import os
import sys

print("="*70)
print("JARVIS ONE-CLICK FIX")
print("="*70)

# Get OpenAI API key
print("\n1. Checking OpenAI API key...")
try:
    from Jarvis.config import config
    key = getattr(config, 'openai_api_key', '')
    if key and key.startswith('sk-'):
        print("   ✓ API key found in config")
    else:
        key = os.environ.get('OPENAI_API_KEY', '')
        if key:
            print("   ✓ API key found in environment variable")
        else:
            print("   ✗ No API key found!")
            print("   → Go to https://platform.openai.com/api-keys")
            print("   → Copy your key")
            print("   → Edit Jarvis/config/config.py and set: openai_api_key = 'sk-...'")
            sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Clear proxy
print("\n2. Clearing proxy...")
os.environ['HTTPS_PROXY'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['https_proxy'] = ''
os.environ['http_proxy'] = ''
print("   ✓ Proxy cleared for this session")

# Test AI
print("\n3. Testing AI module...")
try:
    from Jarvis import JarvisAssistant
    obj = JarvisAssistant()
    print("   Testing with simple math question...")
    response = obj.ask_ai("What is 5 + 3?")
    if response and not response.startswith("AI error") and not response.startswith("No OpenAI"):
        print(f"   ✓ AI works! Response: {response[:60]}...")
    else:
        print(f"   ⚠ AI response: {response}")
        print("   → This might mean proxy is still blocking")
        print("   → Try: Run PowerShell as Admin and re-run this script")
except Exception as e:
    print(f"   ✗ AI test failed: {e}")
    sys.exit(1)

# List microphones
print("\n4. Available microphones:")
try:
    import speech_recognition as sr
    mics = sr.Microphone.list_microphone_names()
    for i, mic_name in enumerate(mics):
        if i in [1, 2, 16, 19]:
            print(f"   [{i}] {mic_name} ← RECOMMENDED")
        elif "Microphone" in mic_name or "Array" in mic_name:
            print(f"   [{i}] {mic_name} ← TRY THIS")
        else:
            print(f"   [{i}] {mic_name}")
    
    print("\n   Edit Jarvis/config/config.py:")
    print("   Change: microphone_index = None")
    print("   To: microphone_index = 1  (try 1, 2, 16, or 19)")
except Exception as e:
    print(f"   ✗ Microphone error: {e}")

# Summary
print("\n" + "="*70)
print("✅ SETUP COMPLETE - YOU'RE READY TO GO!")
print("="*70)
print("""
NEXT STEPS:

1. (Optional) Set microphone in Jarvis/config/config.py:
   microphone_index = 1

2. Run Jarvis:
   python main.py

3. Speak commands like:
   - "What is 2 plus 2?"
   - "How do I learn Python?"
   - "Tell me a joke"
   - "What's the weather?"

TIPS:
- Jarvis will respond to ANYTHING you say with AI
- First response may take 2-5 seconds (API call)
- Speak clearly near your microphone
- Say "goodbye" or "bye" to exit

ISSUES?
- Run: python diagnose.py
- Read: SETUP_FIX.py
- Check: README_SETUP.md
""")
print("="*70)
print("ENJOY YOUR AI ASSISTANT! 🚀")
print("="*70)
