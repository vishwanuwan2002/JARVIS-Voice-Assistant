#!/usr/bin/env python
"""
Diagnostic script to test each microphone and find which ones actually work
"""
import speech_recognition as sr

print("=" * 60)
print("MICROPHONE DIAGNOSTIC TEST")
print("=" * 60)

r = sr.Recognizer()
mics = sr.Microphone.list_microphone_names()

print(f"\nTotal microphones detected: {len(mics)}\n")

working_mics = []
broken_mics = []

for i, name in enumerate(mics):
    print(f"Testing {i}: {name}...", end=" ")
    try:
        mic = sr.Microphone(device_index=i)
        with mic as source:
            # Try to adjust for ambient noise
            try:
                r.adjust_for_ambient_noise(source, duration=0.1)
                print("✅ WORKS")
                working_mics.append((i, name))
            except Exception as e:
                print(f"⚠️  Cannot adjust: {e}")
                broken_mics.append((i, name, str(e)))
    except Exception as e:
        print(f"❌ FAILED: {e}")
        broken_mics.append((i, name, str(e)))

print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)

if working_mics:
    print(f"\n✅ WORKING MICROPHONES ({len(working_mics)}):")
    for i, name in working_mics:
        print(f"  [{i}] {name}")
        if len(working_mics) == 1:
            print(f"  → Use this one! Set microphone_index = {i}")
else:
    print("\n❌ NO WORKING MICROPHONES FOUND")

if broken_mics:
    print(f"\n❌ BROKEN MICROPHONES ({len(broken_mics)}):")
    for i, name, error in broken_mics:
        print(f"  [{i}] {name}")
        print(f"       Error: {error}")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("=" * 60)

if working_mics:
    idx, name = working_mics[0]
    print(f"\n✅ Use microphone index: {idx}")
    print(f"   Device: {name}")
    print(f"\n   Update Jarvis/config/config.py:")
    print(f"   microphone_index = {idx}")
else:
    print("\n❌ No working microphones found!")
    print("\nTroubleshooting steps:")
    print("1. Check if microphone is plugged in and enabled")
    print("2. Check Windows Sound Settings")
    print("3. Try a different microphone port")
    print("4. Restart your computer")
    print("5. Update audio drivers")

print("\n" + "=" * 60)
