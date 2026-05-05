"""
JARVIS SETUP GUIDE - NETWORK & MICROPHONE CONFIGURATION

The diagnostics show that your system is mostly ready, but there are two critical issues:

1. PROXY BLOCKING OPENAI API (MOST CRITICAL)
2. MULTIPLE MICROPHONES - NEED TO SELECT THE RIGHT ONE

This guide will help you fix both.
"""

print(__doc__)

# PROXY FIX
print("\n" + "="*70)
print("ISSUE 1: PROXY BLOCKING OPENAI API")
print("="*70)
print("""
ERROR: Cannot reach api.openai.com due to proxy or firewall

SOLUTIONS:

A) TEMPORARY FIX (Current PowerShell session only):
   1. Open PowerShell as Administrator
   2. Run these commands:
   
   $env:HTTPS_PROXY = $null
   $env:HTTP_PROXY = $null
   $env:NO_PROXY = 'api.openai.com'
   
   3. Then run Jarvis:
   & .\.venv\Scripts\python.exe main.py

B) PERMANENT FIX (Windows Environment Variables):
   1. Press Win+X, click "System"
   2. Click "Advanced system settings"
   3. Click "Environment Variables..."
   4. Under "System variables" click "New..."
   5. Add these:
      - Variable name: NO_PROXY
        Variable value: api.openai.com,openai.com
      - Delete/clear HTTP_PROXY, HTTPS_PROXY if they exist
   6. Click OK and restart PowerShell
   7. Verify: echo $env:HTTPS_PROXY (should be empty)
   
C) IF ON CORPORATE NETWORK:
   Ask your IT to whitelist: api.openai.com:443
   Or configure proxy in your code (advanced):
   - Edit Jarvis/features/ai.py
   - Set: proxies = {'https': 'http://user:pass@proxy.corp.com:8080'}
   - Pass to openai.api_request_timeout_sec = 15

D) TEST IF PROXY IS FIXED:
   Once you fix the proxy, test with:
   
   python -c "import requests; print(requests.get('https://api.openai.com/v1/models', timeout=10).status_code)"
   
   Should output: 401 (means API is reachable, just needs auth - that's good!)
""")

# MICROPHONE FIX
print("\n" + "="*70)
print("ISSUE 2: SELECT THE CORRECT MICROPHONE")
print("="*70)
print("""
DETECTED MICROPHONES:
[0] Microsoft Sound Mapper - Input (generic, often slow)
[1] Microphone Array (Realtek) ← TRY THIS FIRST
[2] AI Noise-cancelling Input (ASUS) ← OR THIS
[16] Microphone (Realtek HD Audio Mic input) ← OR THIS
[19] Microphone Array (Realtek HD Audio Mic Array input) ← OR THIS

INSTRUCTIONS:
1. Open Jarvis/config/config.py
2. Change: microphone_index = None
   To: microphone_index = 1  (or try 2, 16, 19)
3. Run: python main.py
4. When Jarvis says "Listening", speak clearly near your mic
5. If no recognition or errors, try the next index

TESTING MICROPHONE:
python -c "
import speech_recognition as sr
r = sr.Recognizer()
mic = sr.Microphone(device_index=1)  # Change 1 to your index
with mic as source:
    print('Speak something...')
    r.adjust_for_ambient_noise(source, duration=0.5)
    try:
        audio = r.listen(source, timeout=5)
        text = r.recognize_google(audio, language='en-in')
        print('Recognized:', text)
    except sr.UnknownValueError:
        print('Could not understand audio')
    except sr.RequestError as e:
        print('API error:', e)
"
""")

# RECOMMENDED STEPS
print("\n" + "="*70)
print("RECOMMENDED SETUP STEPS (IN ORDER)")
print("="*70)
print("""
STEP 1: Fix the proxy (CRITICAL for AI to work)
   → Open PowerShell as Admin
   → Run the temporary fix commands above
   → Test: python test_ai.py
   → You should see AI responses now!

STEP 2: Set microphone index (if speech isn't recognized)
   → Edit Jarvis/config/config.py
   → Set: microphone_index = 1 (start with 1, try 2/16/19 if needed)
   → Test mic with the python command above

STEP 3: Run full Jarvis
   → python main.py
   → Speak commands like: "What is 2 plus 2?"
   → Jarvis should respond!

STEP 4: (Optional) Make proxy fix permanent
   → Follow "PERMANENT FIX" steps under Issue 1
   → This way proxy is cleared even after restarting
""")

print("\n" + "="*70)
print("QUICK COMMAND REFERENCE")
print("="*70)
print("""
# Clear proxy temporarily:
$env:HTTPS_PROXY = $null; $env:HTTP_PROXY = $null

# Test OpenAI API:
python test_ai.py

# List microphones:
python -c "import speech_recognition as sr; [print(i, name) for i, name in enumerate(sr.Microphone.list_microphone_names())]"

# Run Jarvis:
python main.py

# Run diagnostics:
python diagnose.py
""")

print("\n" + "="*70)
print("TROUBLESHOOTING")
print("="*70)
print("""
Q: Images not showing?
A: They should auto-load. If error, just run anyway - Jarvis still works!

Q: Jarvis recognizes speech but doesn't respond?
A: The command doesn't match built-in actions. It should fall back to AI.
   If AI doesn't respond, check: python test_ai.py

Q: AI responds but takes forever?
A: Network latency. This is normal for API calls (~2-5 seconds).

Q: Speech recognition not working at all?
A: Check microphone_index in config. Try other indices.

Q: "Connection refused" or "Proxy error"?
A: Use the temporary proxy fix at the top of this guide.

Q: API key error?
A: Check your API key is valid at https://platform.openai.com/api-keys
   Regenerate if needed and update config.
""")

print("\n" + "="*70)
print("YOU'RE ALMOST THERE! 🚀")
print("="*70)
