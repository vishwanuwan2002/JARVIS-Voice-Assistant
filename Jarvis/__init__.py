import speech_recognition as sr
from Jarvis.config import config
import pyttsx3

# New feature modules: STT, TTS, Memory, Intelligent AI
from Jarvis.features import date_time
from Jarvis.features import stt as stt_module
from Jarvis.features import tts as tts_module
from Jarvis.features import memory as memory_module
from Jarvis.features import intelligent_ai as intelligent_ai_module
from Jarvis.features import launch_app
from Jarvis.features import website_open
from Jarvis.features import weather
from Jarvis.features import wikipedia
from Jarvis.features import news
from Jarvis.features import send_email
from Jarvis.features import google_search
from Jarvis.features import google_calendar
from Jarvis.features import note
from Jarvis.features import system_stats
from Jarvis.features import loc
from Jarvis.features import ai as ai_module
from Jarvis.features import app_finder
from Jarvis.features import user_profile


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voices', voices[0].id)

class JarvisAssistant:
    def __init__(self):
        # Initialize conversation memory (SQLite)
        try:
            memory_module.init_db()
        except Exception:
            # Non-fatal: memory will be unavailable if initialization fails
            print('Warning: conversation memory initialization failed')

    def mic_input(self):
        """
        Fetch input from mic
        return: user's voice input as text if true, false if fail
        """
        # Prefer the unified STT provider (Whisper if available, otherwise speech_recognition)
        try:
            stt_result = stt_module.default_stt.listen_and_transcribe()
            if stt_result is not False:
                return stt_result
            # If the provider returned False (fatal) fall through to legacy method
        except Exception as e:
            print(f"STT provider failed, falling back to legacy mic_input: {e}")

        # Legacy fallback (keeps original behavior if STT wrapper not usable)
        try:
            r = sr.Recognizer()
            # Use ambient noise adjustment so threshold adapts to environment
            mic_index = getattr(config, 'microphone_index', None)
            if mic_index is None:
                # print available microphones to help user choose a device index
                print("Available microphone devices:")
                for i, name in enumerate(sr.Microphone.list_microphone_names()):
                    print(i, name)
                print("Using default microphone (set Jarvis.config.config.microphone_index to choose a specific device)")
                mic_params = {}
            else:
                print(f"Using microphone device_index={mic_index}")
                mic_params = {'device_index': mic_index}
            with sr.Microphone(**mic_params) as source:
                # quick ambient adjustment for responsiveness
                print("Adjusting for ambient noise (0.1s)...")
                try:
                    r.adjust_for_ambient_noise(source, duration=0.1)
                except Exception as e:
                    # If the microphone isn't accessible, bubble up a friendly message
                    print(f"adjust_for_ambient_noise failed: {e}")
                print("Listening...")
                # timeouts help avoid hanging indefinitely; keep short for snappy responses
                try:
                    audio = r.listen(source, timeout=1, phrase_time_limit=3)
                except sr.WaitTimeoutError:
                    print("No speech detected (listen timeout)")
                    return ""
            try:
                print("Recognizing...")
                command = r.recognize_google(audio, language='en-in').lower()
                print(f'You said: {command}')
                return command
            except sr.UnknownValueError:
                # Speech was unintelligible
                print('Could not understand audio')
                return ""
            except sr.RequestError as e:
                # API/service error (network/connectivity issue)
                print(f"Speech recognition request failed: {e}")
                return False
            except Exception as e:
                print(f"Unexpected error recognizing speech: {e}")
                return False
        except Exception as e:
            print(f"Microphone access error: {e}")
            print(f"Error code: {getattr(e, 'errno', 'N/A')}")
            print("\n⚠️  Microphone Error - Troubleshooting:")
            print("1. Check if microphone is plugged in and working")
            print("2. Try changing microphone_index in Jarvis/config/config.py")
            print("3. Run this to list available microphones:")
            print("   python -c \"import speech_recognition as sr; [print(i, name) for i, name in enumerate(sr.Microphone.list_microphone_names())]\"")
            print("4. Close other apps using the microphone")
            import sys
            sys.exit(1)
            return False


    def tts(self, text, style_params=None):
        """
        Convert any text to speech with optional style parameters
        :param text: text(String)
        :param style_params: dict with style parameters (rate, volume, pitch)
        :return: True/False (Play sound if True otherwise write exception to log and return  False)
        """
        try:
            # Prefer new TTS provider (Coqui if configured, otherwise pyttsx3 fallback)
            ok = tts_module.speak(text, style_params)
            if ok:
                return True
            # Fallback to existing pyttsx3 engine
            engine.say(text)
            engine.runAndWait()
            engine.setProperty('rate', 175)
            return True
        except Exception as e:
            t = "Sorry I couldn't understand and handle this input"
            print(f"TTS error: {e}")
            print(t)
            return False

    def tell_me_date(self):

        return date_time.date()

    def tell_time(self):

        return date_time.time()

    def launch_any_app(self, path_of_app):
        """
        Launch any windows application 
        :param path_of_app: path of exe 
        :return: True is success and open the application, False if fail
        """
        return launch_app.launch_app(path_of_app)

    def website_opener(self, domain):
        """
        This will open website according to domain
        :param domain: any domain, example "youtube.com"
        :return: True if success, False if fail
        """
        return website_open.website_opener(domain)

    def open_app_or_website(self, app_name):
        """
        Try to open an installed app, fallback to browser if not found.
        :param app_name: Name of the application to open (e.g., "youtube", "spotify")
        :return: Tuple (success: bool, action: str, details: str)
        """
        return app_finder.open_app_or_browser(app_name)


    def weather(self, city):
        """
        Return weather
        :param city: Any city of this world
        :return: weather info as string if True, or False
        """
        try:
            res = weather.fetch_weather(city)
        except Exception as e:
            print(e)
            res = False
        return res

    def tell_me(self, topic):
        """
        Tells about anything from wikipedia
        :param topic: any string is valid options
        :return: First 500 character from wikipedia if True, False if fail
        """
        return wikipedia.tell_me_about(topic)

    def news(self):
        """
        Fetch top news of the day from google news
        :return: news list of string if True, False if fail
        """
        return news.get_news()
    
    def send_mail(self, sender_email, sender_password, receiver_email, msg):

        return send_email.mail(sender_email, sender_password, receiver_email, msg)

    def google_calendar_events(self, text):
        service = google_calendar.authenticate_google()
        date = google_calendar.get_date(text) 
        
        if date:
            return google_calendar.get_events(date, service)
        else:
            pass
    
    def search_anything_google(self, command):
        google_search.google_search(command)

    def take_note(self, text):
        note.note(text)
    
    def system_info(self):
        return system_stats.system_stats()

    def location(self, location):
        current_loc, target_loc, distance = loc.loc(location)
        return current_loc, target_loc, distance

    def my_location(self):
        city, state, country = loc.my_location()
        return city, state, country

    def ask_ai(self, prompt: str, language: str = 'en') -> str:
        """Ask the configured AI using the intelligent_ai module with LLM wrapper.

        This method uses the new intelligent_ai module which:
        - Prefers OpenAI if OPENAI_API_KEY is set
        - Falls back to local Llama if LLM_MODEL_PATH is set
        - Persists conversation history to SQLite

        Returns a user-friendly response or error message.
        """
        try:
            # Use the new intelligent_ai module with LLM wrapper
            resp = intelligent_ai_module.ask_ai(prompt, use_history=True, language=language)
            if resp is None:
                return "AI unavailable. Check your internet connection or set OPENAI_API_KEY environment variable."
            return resp
        except Exception as e:
            return f"AI interface error: {e}"