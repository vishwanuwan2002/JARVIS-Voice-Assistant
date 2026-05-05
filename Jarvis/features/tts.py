"""Text-to-speech wrapper module with emotional intelligence.

Provides a unified `speak(text, style)` function. Preference order:
1. If `ELEVENLABS_API_KEY` is set, use ElevenLabs TTS (online, high-quality, human-like).
2. If `COQUI_TTS` environment variable is set to a local server or `COQUI_MODEL` is set, try Coqui TTS (local, free).
3. Otherwise, use `pyttsx3` (offline, cross-platform, free) as a reliable fallback.

Enhanced with speech styles for emotional expression: whisper, joke, motivate, advise, etc.
"""

import os
import traceback
import requests
import tempfile
from typing import Dict, Optional

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    # coqui-tts can be used if available; not required
    from TTS.api import TTS
except Exception:
    TTS = None


class TTSProvider:
    def __init__(self):
        self.elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY')
        self.elevenlabs_voice_id = os.environ.get('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')  # Default: Rachel (very natural female voice)
        self.coqui = None
        self.py_engine = None

        # ElevenLabs is preferred for human-like voice
        if self.elevenlabs_api_key:
            print("TTS: ElevenLabs API key found - using high-quality human-like voice")
        else:
            print("TTS: No ElevenLabs API key - for best human-like voice, set ELEVENLABS_API_KEY environment variable")

        # If Coqui TTS is available and a model is specified, initialize it as secondary option
        try:
            coqui_model = os.environ.get('COQUI_MODEL')
            if TTS and coqui_model and not self.elevenlabs_api_key:
                try:
                    self.coqui = TTS(coqui_model)
                    print(f"TTS: Loaded Coqui model {coqui_model}")
                except Exception as e:
                    print(f"TTS: Failed to initialize Coqui: {e}")
        except Exception:
            pass

        # Initialize pyttsx3 as fallback
        if pyttsx3 and not self.coqui and not self.elevenlabs_api_key:
            try:
                self.py_engine = pyttsx3.init()
                self.py_engine.setProperty('rate', 200)  # Normal speaking speed
                voices = self.py_engine.getProperty('voices')
                if voices:
                    self.py_engine.setProperty('voice', voices[0].id)
                print("TTS: Initialized pyttsx3 fallback engine")
            except Exception as e:
                print(f"TTS: pyttsx3 init failed: {e}")

    def speak(self, text: str, style_params: Optional[Dict] = None) -> bool:
        try:
            # Default style parameters
            if style_params is None:
                style_params = {"rate": 1.0, "volume": 1.0, "pitch": 1.0}

            # ElevenLabs - highest quality, most human-like
            if self.elevenlabs_api_key:
                return self._speak_elevenlabs(text, style_params)

            # Coqui TTS - good quality, local
            if self.coqui:
                # Coqui returns audio array; speak requires playback; keep it simple and use coqui's save_wav
                out_path = "coqui_out.wav"
                self.coqui.tts_to_file(text=text, file_path=out_path)
                # Play via platform default player
                if os.name == 'nt':
                    os.startfile(out_path)
                else:
                    import subprocess
                    subprocess.call(['aplay', out_path])
                return True

            # pyttsx3 fallback with style support
            if self.py_engine:
                return self._speak_pyttsx3(text, style_params)

            print("TTS: No TTS engine available")
            return False
        except Exception as e:
            print(f"TTS error: {e}")
            traceback.print_exc()
            return False

    def _speak_elevenlabs(self, text: str, style_params: Dict) -> bool:
        """Use ElevenLabs API for ultra-human-like voice synthesis with style support."""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }

            # Adjust voice settings based on style
            stability = 0.5
            similarity_boost = 0.5

            if style_params.get("volume", 1.0) < 0.5:
                stability = 0.3  # More expressive for whisper
                similarity_boost = 0.3
            elif style_params.get("rate", 1.0) > 1.2:
                stability = 0.7  # More stable for energetic speech
                similarity_boost = 0.7

            data = {
                "text": text,
                "model_id": "eleven_flash_v2_5",  # Updated to newer model
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                # Save audio to temp file and play
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name

                # Play the audio
                if os.name == 'nt':
                    os.startfile(temp_path)  # Windows will use default MP3 player
                else:
                    import subprocess
                    # Try common audio players
                    for player in ['mpg123', 'mplayer', 'aplay']:
                        try:
                            subprocess.call([player, temp_path], timeout=30)
                            break
                        except (subprocess.TimeoutExpired, FileNotFoundError):
                            continue

                # Clean up temp file after a delay (simple approach)
                import threading
                def cleanup():
                    import time
                    time.sleep(5)  # Wait for playback
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                threading.Thread(target=cleanup, daemon=True).start()

                return True
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            return False

    def _speak_pyttsx3(self, text: str, style_params: Dict) -> bool:
        """Use pyttsx3 with style parameter support."""
        try:
            if not self.py_engine:
                return False

            # Get current voice properties
            current_rate = self.py_engine.getProperty('rate') or 200
            current_volume = self.py_engine.getProperty('volume') or 1.0

            # Apply style adjustments
            rate_multiplier = style_params.get("rate", 1.0)
            volume_multiplier = style_params.get("volume", 1.0)

            new_rate = int(current_rate * rate_multiplier)
            new_volume = min(1.0, current_volume * volume_multiplier)

            # Set adjusted properties
            self.py_engine.setProperty('rate', new_rate)
            self.py_engine.setProperty('volume', new_volume)

            # Speak the text
            self.py_engine.say(text)
            self.py_engine.runAndWait()

            # Reset to defaults for next call
            self.py_engine.setProperty('rate', current_rate)
            self.py_engine.setProperty('volume', current_volume)

            return True

        except Exception as e:
            print(f"pyttsx3 styled speech error: {e}")
            return False


# Singleton
default_tts = TTSProvider()

def speak(text: str, style_params: Optional[Dict] = None) -> bool:
    return default_tts.speak(text, style_params)


if __name__ == '__main__':
    speak('Hello from Kael AI. This is a quick TTS test.')
