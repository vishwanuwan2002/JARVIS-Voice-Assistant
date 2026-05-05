#!/usr/bin/env python3
"""
Quick diagnostic tool to help fix Jarvis issues.
"""

import sys
import os

print("=" * 70)
print("JARVIS DIAGNOSTIC TOOL")
print("=" * 70)

# 1. Check Python
print("\n1. Python Version:")
print(f"   {sys.version}")

# 2. Check imports
print("\n2. Core Dependencies:")
deps = ['speech_recognition', 'pyttsx3', 'PyQt5', 'openai', 'requests', 'pillow']
for dep in deps:
    try:
        mod = __import__(dep)
        version = getattr(mod, '__version__', 'unknown')
        print(f"   ✓ {dep} ({version})")
    except ImportError:
        print(f"   ✗ {dep} NOT INSTALLED")

# 3. Check config
print("\n3. Configuration:")
try:
    from Jarvis.config import config
    print(f"   ✓ Config loaded")
    print(f"   - User name: {getattr(config, 'user_name', 'NOT SET')}")
    print(f"   - Microphone index: {getattr(config, 'microphone_index', 'AUTO')}")
    key = getattr(config, 'openai_api_key', '')
    if key:
        print(f"   - OpenAI API key: {key[:20]}... (CONFIGURED)")
    else:
        print(f"   - OpenAI API key: NOT SET (check environment variable OPENAI_API_KEY)")
except Exception as e:
    print(f"   ✗ Config error: {e}")

# 4. Check image files
print("\n4. Image Files:")
image_dir = "Jarvis/utils/images"
if os.path.isdir(image_dir):
    images = os.listdir(image_dir)
    for img in images:
        print(f"   ✓ {img}")
else:
    print(f"   ✗ Image directory not found: {image_dir}")

# 5. Check microphone
print("\n5. Microphone Detection:")
try:
    import speech_recognition as sr
    mics = sr.Microphone.list_microphone_names()
    for i, mic_name in enumerate(mics):
        print(f"   [{i}] {mic_name}")
    if not mics:
        print("   ✗ NO MICROPHONES DETECTED")
except Exception as e:
    print(f"   ✗ Microphone error: {e}")

# 6. Network test
print("\n6. Network Connectivity:")
try:
    import requests
    response = requests.get('https://api.openai.com/v1/models', timeout=5)
    if response.status_code in [401, 403]:
        print("   ✓ Can reach OpenAI API (auth needed)")
    else:
        print(f"   ? OpenAI API response: {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot reach OpenAI API: {e}")

# 7. Summary
print("\n" + "=" * 70)
print("SUMMARY & NEXT STEPS:")
print("=" * 70)
print("""
1. If images say "NOT FOUND", images exist but Python can't access them.
   → Run from D:\\JARVIS-master directory

2. If microphone shows "NO MICROPHONES", check:
   - Windows Settings → Privacy → Microphone (enable)
   - Set USB headset as default recording device if using one
   - Run: python -c "import pyaudio; print(pyaudio.PyAudio().get_device_count())"

3. If OpenAI API is unreachable:
   - Check internet connection
   - Disable corporate proxy: $env:HTTP_PROXY=$null; $env:HTTPS_PROXY=$null
   - Set OpenAI API key in environment: $env:OPENAI_API_KEY='sk-...'

4. To test AI directly:
   python test_ai.py

5. To run full Jarvis:
   python main.py

6. For detailed setup guide:
   See README_SETUP.md
""")
print("=" * 70)
