"""Speech-to-text wrapper module.

Provides a lightweight, fallback-capable STT interface. Preferred path:
1. If `faster_whisper` or `whisper` is installed and a local model path is provided via
   the environment variable `WHISPER_MODEL_PATH`, use a local Whisper model.
2. Otherwise, fall back to the existing `speech_recognition` Google recognizer (online)
   which is already used by the project.

This keeps defaults free: no paid services required. Local Whisper models may be large
but are optional—if you have CPU/GPU and download a model, set `WHISPER_MODEL_PATH`.
"""

import os
import io
import traceback
from typing import Optional

try:
    import speech_recognition as sr
except Exception:
    sr = None

_HAS_WHISPER = False
_WHISPER_IMPL = None

# Try faster_whisper first (faster, optional)
try:
    from faster_whisper import WhisperModel
    _WHISPER_IMPL = 'faster_whisper'
    _HAS_WHISPER = True
except Exception:
    try:
        import whisper
        _WHISPER_IMPL = 'whisper'
        _HAS_WHISPER = True
    except Exception:
        _HAS_WHISPER = False


class STTProvider:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.environ.get('WHISPER_MODEL_PATH')
        self.recognizer = sr.Recognizer() if sr else None

        self.whisper_model = None
        if _HAS_WHISPER and self.model_path:
            try:
                if _WHISPER_IMPL == 'faster_whisper':
                    # use faster_whisper
                    self.whisper_model = WhisperModel(self.model_path, device="cpu", compute_type="int8")
                else:
                    # use openai/whisper
                    self.whisper_model = whisper.load_model(self.model_path)
                print(f"STT: Loaded whisper model ({_WHISPER_IMPL}) at {self.model_path}")
            except Exception as e:
                print(f"STT: Failed to load whisper model: {e}")
                traceback.print_exc()
                self.whisper_model = None

    def listen_and_transcribe(self, timeout: float = 1.0, phrase_time_limit: float = 3.0) -> str:
        """Listen on the default microphone and return transcribed text.

        Returns empty string when speech is unintelligible, False on fatal errors.
        """
        if not sr:
            print("STT: speech_recognition not installed")
            return False

        try:
            with sr.Microphone() as source:
                print("STT: Adjusting for ambient noise (0.1s)...")
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                except Exception:
                    pass
                print("STT: Listening...")
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                except sr.WaitTimeoutError:
                    print("STT: No speech detected (listen timeout)")
                    return ""

            # If we have a local whisper model loaded, use it
            if self.whisper_model:
                try:
                    wav_data = audio.get_wav_data()
                    print("STT: Transcribing with Whisper model...")
                    if _WHISPER_IMPL == 'faster_whisper':
                        # faster_whisper expects a filename or numpy array; use in-memory bytes via tempfile
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpf:
                            tmpf.write(wav_data)
                            tmpf.flush()
                            segments, info = self.whisper_model.transcribe(tmpf.name, beam_size=5)
                            text = " ".join([seg.text for seg in segments])
                        return text.lower().strip()
                    else:
                        # openai/whisper
                        audio_file = io.BytesIO(wav_data)
                        audio_file.name = "audio.wav"
                        result = self.whisper_model.transcribe(audio_file)
                        return result['text'].lower().strip()
                except Exception as e:
                    print(f"STT: Whisper transcription failed: {e}")
                    traceback.print_exc()

            # Fallback to Google recognizer (online) via speech_recognition
            try:
                print("STT: Using Google speech recognition (fallback)...")
                text = self.recognizer.recognize_google(audio, language='en-in')
                return text.lower()
            except sr.UnknownValueError:
                print("STT: Could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"STT: Speech recognition request failed: {e}")
                return False

        except Exception as e:
            print(f"STT: Microphone access or transcription error: {e}")
            traceback.print_exc()
            return False


# Lightweight default provider singleton
default_stt = STTProvider()

if __name__ == '__main__':
    p = default_stt
    print('Say something...')
    print(p.listen_and_transcribe())
