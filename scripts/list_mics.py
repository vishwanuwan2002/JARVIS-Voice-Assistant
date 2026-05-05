import speech_recognition as sr

print("Available microphone devices:")
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(i, name)

print("\nIf you see your microphone in the list, open Jarvis/ config/config.py and set microphone_index to that integer value, then re-run Jarvis.")
