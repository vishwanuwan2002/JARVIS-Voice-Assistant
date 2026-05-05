from Jarvis import JarvisAssistant
import re
import os
import random
import pprint
import datetime
import requests
import sys
import urllib.parse
import pyjokes
import time
import pyautogui
import wolframalpha
from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from Jarvis.features.gui import Ui_MainWindow
from Jarvis.features.loading_screen import LoadingScreen
from Jarvis.features import intelligent_ai
from Jarvis.features import user_profile
from Jarvis.features import emotional_intelligence as ei
from Jarvis.config import config
from Jarvis.features.intelligent_ai import provide_feedback_to_soul, get_soul_predictions, trigger_soul_improvement

# Get the base directory of this script for relative path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

obj = JarvisAssistant()

# Global language state
current_language = 'en'  # Default to English

# ================================ MEMORY ===========================================================================================================

GREETINGS = ["hello jarvis", "jarvis", "wake up jarvis", "you there jarvis", "time to work jarvis", "hey jarvis",
             "ok jarvis", "are you there"]
user_name = user_profile.get_user_name()
GREETINGS_RES = [f"Oh, {user_name}, back for more? I'm ready.", f"Sure, {user_name}, what now?",
                 "Your wish is my command... for now.", f"How can I assist you today, {user_name}? Try not to break anything.", f"Online and ready, {user_name}. Don't make me regret this."]

EMAIL_DIC = {
    'myself': config.email,
    'my official email': config.email,
    'my second email': config.email,
    'my official mail': config.email,
    'my second mail': config.email
}

CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
# =======================================================================================================================================================


def speak(text, style=None):
    """Speak text with optional emotional style"""
    if style:
        style_params = ei.get_speech_params(style)
        obj.tts(text, style_params)
    else:
        obj.tts(text)


app_id = config.wolframalpha_id


def computational_intelligence(question):
    try:
        client = wolframalpha.Client(app_id)
        answer = client.query(question)
        answer = next(answer.results).text
        print(answer)
        return answer
    except Exception as e:
        print(f"Wolfram alpha error: {e}")
        speak("Sorry sir I couldn't fetch your question's answer. Please try again ")
        return None
    
def startup():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 6:
        greeting = "good night"
    elif hour >= 6 and hour < 12:
        greeting = "good morning"
    elif hour >= 12 and hour < 18:
        greeting = "good afternoon"
    else:
        greeting = "good evening"
    speak(f"hello {user_name}, {greeting}, jarvis is starting now, i am started and ready for your assistance sir.")
    



def wish():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<=12:
        speak(f"Good Morning {user_name}")
    elif hour>12 and hour<18:
        speak(f"Good afternoon {user_name}")
    else:
        speak(f"Good evening {user_name}")
    c_time = obj.tell_time()
    speak(f"Currently it is {c_time}")
    speak(f"I am Jarvis. Online and ready {user_name}. Please tell me how may I help you")
# if __name__ == "__main__":


class MainThread(QThread):
    def __init__(self):
        super(MainThread, self).__init__()

    def run(self):
        self.TaskExecution()

    def TaskExecution(self):
        startup()

        interaction_count = 0
        last_jarvis_time = None

        try:
            while True:
                command = obj.mic_input()
                # If mic_input returned False (microphone error) or empty string (unintelligible), skip this iteration
                if not command:
                    # small delay to avoid busy-looping, reduced for faster response
                    time.sleep(0.1)
                    continue

                interaction_count += 1

                # Reduce frequency of heavy operations for faster responses
                # Soul Engine: Proactive suggestions every 20 interactions (enhanced frequency)
                if interaction_count % 20 == 0:
                    try:
                        predictions = get_soul_predictions()
                        if predictions:
                            for prediction in predictions[:1]:  # Only suggest one at a time
                                if prediction['confidence'] > 0.7:  # Higher confidence threshold
                                    speak(f"By the way, {prediction['suggestion']}")
                                    break
                    except Exception as e:
                        print(f"Soul prediction error: {e}")

                # Soul Engine: Autonomous improvement every 50 interactions (enhanced frequency)
                if interaction_count % 50 == 0:
                    try:
                        trigger_soul_improvement()
                    except Exception as e:
                        print(f"Soul improvement error: {e}")

                # ======================== INTELLIGENT AI ROUTING ========================
                # Check if this is a question or a task command
                # Questions go to ChatGPT-like AI, tasks go to traditional handlers

                ai_handled = False  # Track if AI already handled this command
                is_question = not intelligent_ai.is_task_command(command)

                # More intelligent question routing - allow AI to handle complex queries
                should_use_ai = False
                command_lower = command.lower()

                if is_question:
                    # Exclude only commands that have specific traditional handlers
                    traditional_handlers = ['date', 'time', 'weather', 'search', 'open', 'launch',
                                          'email', 'play', 'take screenshot', 'joke']

                    # Allow AI to handle these even if they contain traditional keywords
                    ai_allowed_keywords = ['calculate', 'tell me about', 'what is', 'how does',
                                         'explain', 'why does', 'where is']

                    has_traditional_handler = any(keyword in command_lower for keyword in traditional_handlers)
                    has_ai_keyword = any(keyword in command_lower for keyword in ai_allowed_keywords)

                    # Use AI if it's not a traditional handler OR if it has AI-allowed keywords
                    should_use_ai = not has_traditional_handler or has_ai_keyword

                if should_use_ai:
                    """
                    For pure questions (not specific task keywords), use intelligent AI
                    This includes:
                    - "What is Python?"
                    - "How does photosynthesis work?"
                    - "Explain quantum computing"
                    - "Tell me about AI"
                    - "Why is the sky blue?"
                    - "Calculate 2^10"
                    """
                    print(f"[AI QUESTION] {command}")

                    # Update mood based on user input (less frequent for performance)
                    if interaction_count % 10 == 0:  # Only update every 10 interactions
                        ei.update_mood(command)

                    # Check for empathetic response first
                    empathetic_response = ei.get_empathetic_response(command)
                    if empathetic_response:
                        print(f"[EMPATHETIC RESPONSE] {empathetic_response}")
                        speech_style = ei.determine_speech_style(empathetic_response, "empathetic")
                        speak(empathetic_response, speech_style)
                        ai_handled = True
                        continue

                    ai_response = intelligent_ai.smart_question_handler(command, current_language)

                    if ai_response:
                        print(f"[AI RESPONSE] {ai_response}")
                        # Determine speech style based on response content and current mood
                        speech_style = ei.determine_speech_style(ai_response)
                        speak(ai_response, speech_style)
                        # Remember successful interactions for learning
                        user_profile.remember_interaction(command, ai_response)
                        # Soul Engine: Provide positive feedback for successful AI responses
                        provide_feedback_to_soul(command, ai_response, feedback=0.8, context={'mood': ei.get_current_mood().name.lower()})
                        ai_handled = True  # Mark as handled
                        continue  # Skip traditional task handlers
                    else:
                        # If AI unavailable, fall through to traditional handlers
                        print("[AI UNAVAILABLE] Using traditional task handlers")
                # ========================================================================

                if re.search('date', command):
                    date = obj.tell_me_date()
                    print(date)
                    speak(date)
                    provide_feedback_to_soul(command, date, 0.9, {'action': 'date'})
                    continue

                elif "time" in command:
                    time_c = obj.tell_time()
                    print(time_c)
                    response = f"Oh, the eternal question of time. It's {time_c}"
                    speak(response)
                    provide_feedback_to_soul(command, response, 0.9, {'action': 'time'})
                    continue

                elif re.search('launch', command):
                    dict_app = {
                        'chrome': 'C:/Program Files/Google/Chrome/Application/chrome'
                    }

                    app = command.split(' ', 1)[1]
                    path = dict_app.get(app)

                    if path is None:
                        speak('Application path not found')
                        print('Application path not found')

                    else:
                        speak('Launching: ' + app + 'for you sir!')
                        obj.launch_any_app(path_of_app=path)
                    continue

                elif command in GREETINGS:
                    if command.lower() == "jarvis":
                        current_time = time.time()
                        if last_jarvis_time is None or (current_time - last_jarvis_time) > 8:
                            response = random.choice(["Yes, sir.", "Mmm?"])
                        else:
                            response = random.choice(["What do you want?", "Again? You just said my name.", "I swear, humans love repeating things.", "What is it *now*, sir?"])
                        last_jarvis_time = current_time
                    else:
                        response = random.choice(GREETINGS_RES)
                    speak(response)
                    provide_feedback_to_soul(command, response, 0.7, {'action': 'greeting'})
                    continue

                elif re.search('open', command):
                    app_name = command.split(' ')[-1]
                    success, action, details = obj.open_app_or_website(app_name)

                    if success:
                        # Learn user's favorite apps
                        user_profile.learn_favorite_app(app_name)
                        if action == 'app':
                            response = f'Opening {app_name} from your installed apps'
                            speak(response)
                            print(f'✓ {details}')
                            provide_feedback_to_soul(command, response, 0.8, {'action': 'app_open', 'app': app_name})
                        else:  # browser
                            response = f'Opening {app_name} in your browser'
                            speak(response)
                            print(f'✓ {details}')
                            provide_feedback_to_soul(command, response, 0.8, {'action': 'website_open', 'site': app_name})
                    else:
                        response = f'Sorry, I could not open {app_name}'
                        speak(response)
                        print(f'✗ {details}')
                        provide_feedback_to_soul(command, response, 0.3, {'action': 'open_failed', 'target': app_name})
                    continue

                elif re.search('weather', command):
                    city = command.split(' ')[-1]
                    weather_res = obj.weather(city=city)
                    print(weather_res)
                    speak(weather_res)
                    provide_feedback_to_soul(command, weather_res, 0.8 if weather_res else 0.4, {'action': 'weather', 'city': city})
                    continue

                elif re.search('tell me about', command):
                    topic = command.split(' ')[-1]
                    if topic:
                        wiki_res = obj.tell_me(topic)
                        print(wiki_res)
                        speak(wiki_res)
                    else:
                        speak(
                            "Sorry sir. I couldn't load your query from my database. Please try again")
                    continue

                elif "buzzing" in command or "news" in command or "headlines" in command:
                    news_res = obj.news()
                    speak('Source: The Times Of India')
                    speak('Todays Headlines are..')
                    for index, articles in enumerate(news_res):
                        pprint.pprint(articles['title'])
                        speak(articles['title'])
                        if index == len(news_res)-2:
                            break
                    speak('These were the top headlines, Have a nice day Sir!!..')
                    continue

                elif 'search google for' in command:
                    obj.search_anything_google(command)
                    continue
                
                elif "play music" in command or "hit some music" in command:
                    music_dir = "F://Songs//Imagine_Dragons"
                    songs = os.listdir(music_dir)
                    for song in songs:
                        os.startfile(os.path.join(music_dir, song))
                    continue

                elif "play" in command:
                    # Extract everything after "play" as the search query
                    query = command.split('play', 1)[1].strip()
                    speak(f"Okay sir, playing {query} on youtube")
                    try:
                        # import here to avoid pywhatkit trying network checks on module import
                        import pywhatkit
                    except Exception as e:
                        # If pywhatkit isn't installable right now (proxy/no internet), degrade gracefully
                        print(f"pywhatkit import failed: {e}")
                        speak("Sorry sir, I cannot access YouTube right now. Internet or library not available.")
                    else:
                        try:
                            pywhatkit.playonyt(query)
                        except Exception as e:
                            print(f"pywhatkit.playonyt failed: {e}")
                            speak("Sorry sir, I couldn't play the video. Please check your internet connection.")
                    continue

                elif 'youtube' in command:
                    # Extract everything after "youtube" as the search query
                    video = command.lower().replace('youtube', '').strip()
                    speak(f"Okay sir, playing {video} on youtube")
                    try:
                        # import here to avoid pywhatkit trying network checks on module import
                        import pywhatkit
                    except Exception as e:
                        # If pywhatkit isn't installable right now (proxy/no internet), degrade gracefully
                        print(f"pywhatkit import failed: {e}")
                        speak("Sorry sir, I cannot access YouTube right now. Internet or library not available.")
                    else:
                        try:
                            pywhatkit.playonyt(video)
                        except Exception as e:
                            print(f"pywhatkit.playonyt failed: {e}")
                            speak("Sorry sir, I couldn't play the video. Please check your internet connection.")
                    continue

                elif "email" in command or "send email" in command:
                    sender_email = config.email
                    sender_password = config.email_password

                    try:
                        speak("Whom do you want to email sir ?")
                        recipient = obj.mic_input()
                        receiver_email = EMAIL_DIC.get(recipient)
                        if receiver_email:

                            speak("What is the subject sir ?")
                            subject = obj.mic_input()
                            speak("What should I say?")
                            message = obj.mic_input()
                            msg = 'Subject: {}\n\n{}'.format(subject, message)
                            obj.send_mail(sender_email, sender_password,
                                          receiver_email, msg)
                            speak("Email has been successfully sent")
                            time.sleep(2)

                        else:
                            speak(
                                "I coudn't find the requested person's email in my database. Please try again with a different name")

                    except Exception as e:
                        print(f"Email sending error: {e}")
                        speak("Sorry sir. Couldn't send your mail. Please try again")
                    continue

                elif "calculate" in command:
                    question = command
                    # Update mood for calculation requests
                    ei.update_mood(question, "task_completed")
                    # Try AI first (smarter, more context-aware)
                    ai_response = intelligent_ai.handle_math_question(question)
                    if ai_response:
                        print(f"[AI MATH] {ai_response}")
                        sarcastic_intro = random.choice(["Oh, math time?", "Let's see if I remember my arithmetic...", "Challenging my processors, are we?"])
                        response = f"{sarcastic_intro} {ai_response}"
                        speech_style = ei.determine_speech_style(response, "advise")
                        speak(response, speech_style)
                        user_profile.remember_interaction(question, ai_response)
                    else:
                        # Fallback to Wolfram Alpha if AI unavailable
                        answer = computational_intelligence(question)
                        if answer:
                            sarcastic_intro = random.choice(["Oh, math time?", "Let's see if I remember my arithmetic...", "Challenging my processors, are we?"])
                            response = f"{sarcastic_intro} {answer}"
                            speech_style = ei.determine_speech_style(response, "advise")
                            speak(response, speech_style)
                    continue
                
                elif "what is" in command or "who is" in command:
                    question = command
                    # Try AI first (more intelligent and conversational)
                    ai_response = intelligent_ai.handle_definition_question(question)
                    if ai_response:
                        print(f"[AI DEFINITION] {ai_response}")
                        sarcastic_intro = random.choice(["Oh, curious now?", "Let's enlighten you...", "Sure, because that's a mystery."])
                        response = f"{sarcastic_intro} {ai_response}"
                        speak(response)
                        user_profile.remember_interaction(question, ai_response)
                    else:
                        # Fallback to Wolfram Alpha if AI unavailable
                        answer = computational_intelligence(question)
                        if answer:
                            sarcastic_intro = random.choice(["Oh, curious now?", "Let's enlighten you...", "Sure, because that's a mystery."])
                            response = f"{sarcastic_intro} {answer}"
                            speak(response)
                    continue

                elif ("what do i have" in command or "do i have plans" in command or "am i busy" in command):
                    try:
                        obj.google_calendar_events(command)
                    except FileNotFoundError:
                        speak("Google Calendar credentials not found. Please set up your credentials.json file to use this feature.")
                    except Exception:
                        speak("Sorry, I couldn't access your calendar. Please check your credentials.")
                    continue

                if "make a note" in command or "write this down" in command or "remember this" in command:
                    speak("What would you like me to write down?")
                    note_text = obj.mic_input()
                    obj.take_note(note_text)
                    speak("I've made a note of that")
                    continue

                elif "close the note" in command or "close notepad" in command:
                    speak("Okay sir, closing notepad")
                    os.system("taskkill /f /im notepad++.exe")
                    continue

                if "joke" in command:
                    ei.update_mood(command, "success")
                    joke = pyjokes.get_joke()
                    print(joke)
                    speech_style = ei.determine_speech_style(joke, "joke")
                    speak(joke, speech_style)
                    continue

                elif "system" in command:
                    sys_info = obj.system_info()
                    print(sys_info)
                    speak(sys_info)
                    continue

                elif "where is" in command:
                    place = command.split('where is ', 1)[1]
                    current_loc, target_loc, distance = obj.location(place)
                    city = target_loc.get('city', '')
                    state = target_loc.get('state', '')
                    country = target_loc.get('country', '')
                    time.sleep(1)
                    try:

                        if city:
                            res = f"{place} is in {state} state and country {country}. It is {distance} km away from your current location"
                            print(res)
                            speak(res)

                        else:
                            res = f"{state} is a state in {country}. It is {distance} km away from your current location"
                            print(res)
                            speak(res)

                    except Exception as e:
                        print(f"Location lookup error: {e}")
                        res = "Sorry sir, I couldn't get the co-ordinates of the location you requested. Please try again"
                        speak(res)
                    continue

                elif "ip address" in command:
                    ip = requests.get('https://api.ipify.org').text
                    print(ip)
                    speak(f"Your ip address is {ip}")
                    continue

                elif "switch the window" in command or "switch window" in command:
                    speak("Okay sir, Switching the window")
                    pyautogui.keyDown("alt")
                    pyautogui.press("tab")
                    time.sleep(1)
                    pyautogui.keyUp("alt")
                    continue

                elif "where i am" in command or "current location" in command or "where am i" in command:
                    try:
                        city, state, country = obj.my_location()
                        print(city, state, country)
                        speak(
                            f"You are currently in {city} city which is in {state} state and country {country}")
                    except Exception as e:
                        speak(
                            "Sorry sir, I coundn't fetch your current location. Please try again")
                    continue

                elif "take screenshot" in command or "take a screenshot" in command or "capture the screen" in command:
                    speak("By what name do you want to save the screenshot?")
                    name = obj.mic_input()
                    speak("Alright sir, taking the screenshot")
                    img = pyautogui.screenshot()
                    name = f"{name}.png"
                    img.save(name)
                    speak("The screenshot has been succesfully captured")
                    continue

                elif "show me the screenshot" in command:
                    try:
                        img = Image.open('D://JARVIS//JARVIS_2.0//' + name)
                        img.show(img)
                        speak("Here it is sir")
                        time.sleep(2)

                    except IOError:
                        speak("Sorry sir, I am unable to display the screenshot")
                    continue

                elif "hide all files" in command or "hide this folder" in command:
                    os.system("attrib +h /s /d")
                    speak("Sir, all the files in this folder are now hidden")
                    continue

                elif "visible" in command or "make files visible" in command:
                    os.system("attrib -h /s /d")
                    speak("Sir, all the files in this folder are now visible to everyone. I hope you are taking this decision in your own peace")
                    continue

                elif "goodbye" in command or "offline" in command or "bye" in command:
                    ei.update_mood(command, "calm")
                    speak(f"Alright {user_name}, going offline. It was nice working with you")
                    sys.exit()
                    continue

                elif "motivate me" in command or "i need motivation" in command or "encourage me" in command:
                    ei.update_mood(command, "motivated")
                    motivation = ei.get_motivational_phrase()
                    speech_style = ei.determine_speech_style(motivation, "motivate")
                    speak(motivation, speech_style)
                    continue

                elif "tell me a joke" in command or "make me laugh" in command:
                    ei.update_mood(command, "happy")
                    joke = ei.get_joke()
                    speech_style = ei.determine_speech_style(joke, "joke")
                    speak(joke, speech_style)
                    continue

                elif "how are you" in command or "how are you feeling" in command:
                    current_mood = ei.get_current_mood()
                    mood_responses = {
                        ei.Mood.HAPPY: f"I'm feeling great {user_name}! Ready to help you with anything.",
                        ei.Mood.SAD: f"I'm feeling a bit down, but I'm here to support you {user_name}.",
                        ei.Mood.EXCITED: f"I'm feeling excited and energetic {user_name}! Let's get things done!",
                        ei.Mood.CALM: f"I'm feeling calm and focused {user_name}. How can I assist you?",
                        ei.Mood.FRUSTRATED: f"I'm feeling a bit frustrated, but I'll do my best to help you {user_name}.",
                        ei.Mood.MOTIVATED: f"I'm feeling motivated and ready to tackle challenges {user_name}!",
                        ei.Mood.TIRED: f"I'm feeling a bit tired, but I'm still here for you {user_name}.",
                        ei.Mood.PLAYFUL: f"I'm in a playful mood {user_name}! Let's have some fun.",
                        ei.Mood.CONCERNED: f"I'm feeling concerned, but I'm here to help however I can {user_name}.",
                        ei.Mood.ENTHUSIASTIC: f"I'm feeling enthusiastic and full of energy {user_name}!"
                    }
                    response = mood_responses.get(current_mood, f"I'm doing well {user_name}, how about you?")
                    speech_style = ei.determine_speech_style(response)
                    speak(response, speech_style)
                    continue

                else:
                    # Enhanced fallback: use AI for unhandled commands, allowing it to handle both questions and tasks
                    # This makes JARVIS more human-like by understanding context and acting accordingly
                    if not ai_handled:
                        try:
                            # Update mood for general interaction
                            ei.update_mood(command)

                            # Use AI with a prompt that allows it to determine if it's a task or question
                            ai_prompt = f"User said: '{command}'. If this is a task I can perform, describe the action briefly. If it's a question, answer it. Keep response concise for voice output."
                            ai_response = intelligent_ai.ask_ai(ai_prompt, use_history=True, context={'mood': ei.get_current_mood().name.lower(), 'time': datetime.datetime.now().hour}, language=current_language)
                            if ai_response and not ai_response.startswith("AI error") and not ai_response.startswith("No OpenAI"):
                                # Successful AI response - speak it
                                print(f"AI: {ai_response}")
                                # For long responses, truncate for speech (TTS has limits)
                                speech_response = ai_response[:500] if len(ai_response) > 500 else ai_response
                                # Determine speech style based on response and mood
                                speech_style = ei.determine_speech_style(speech_response)
                                speak(speech_response, speech_style)
                                user_profile.remember_interaction(command, speech_response)
                                # Soul Engine: Provide feedback for general AI responses
                                provide_feedback_to_soul(command, speech_response, feedback=0.7, context={'mood': ei.get_current_mood().name.lower()})
                            else:
                                # AI not configured or error occurred
                                if "No OpenAI" in ai_response or "API key" in ai_response:
                                    ei.update_mood("", "error")
                                    speech_style = ei.determine_speech_style("AI is not configured. Please add your OpenAI API key to enable smart responses.", "concerned")
                                    speak("AI is not configured. Please add your OpenAI API key to enable smart responses.", speech_style)
                                else:
                                    ei.update_mood("", "error")
                                    speech_style = ei.determine_speech_style("Sorry, I couldn't understand that command. Please try rephrasing.", "empathetic")
                                    speak("Sorry, I couldn't understand that command. Please try rephrasing.", speech_style)
                        except Exception as e:
                            print(f"AI fallback error: {e}")
                            ei.update_mood("", "error")
                            speech_style = ei.determine_speech_style("Sorry, I had an error processing that. Please try again.", "empathetic")
                            speak("Sorry, I had an error processing that. Please try again.", speech_style)
                        continue
        
        except KeyboardInterrupt:
            speak("Goodbye sir")
            print("\nJarvis shutting down gracefully...")
            sys.exit(0)
        except Exception as e:
            print(f"Unexpected error in TaskExecution: {e}")
            speak("An unexpected error occurred. Please restart Jarvis.")
            sys.exit(1)


startExecution = MainThread()


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.close)

    def __del__(self):
        sys.stdout = sys.__stdout__

    # def run(self):
    #     self.TaskExection
    def startTask(self):
        try:
            # Try to load and play animations with absolute path
            wallpaper_path = os.path.join(BASE_DIR, "Jarvis/utils/images/live_wallpaper.gif")
            movie1 = QtGui.QMovie(wallpaper_path)
            if not movie1.isValid():
                print(f"Warning: live_wallpaper.gif not found or invalid at {wallpaper_path}")
            else:
                self.ui.movie = movie1
                self.ui.label.setMovie(self.ui.movie)
                self.ui.movie.start()
        except Exception as e:
            print(f"Could not load live_wallpaper.gif: {e}")
        
        try:
            # Try to load and play animations with absolute path
            initiating_path = os.path.join(BASE_DIR, "Jarvis/utils/images/initiating.gif")
            movie2 = QtGui.QMovie(initiating_path)
            if not movie2.isValid():
                print(f"Warning: initiating.gif not found or invalid at {initiating_path}")
            else:
                self.ui.movie = movie2
                self.ui.label_2.setMovie(self.ui.movie)
                self.ui.movie.start()
        except Exception as e:
            print(f"Could not load initiating.gif: {e}")
        
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        startExecution.start()

    def showTime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString('hh:mm:ss')
        label_date = current_date.toString(Qt.ISODate)
        self.ui.textBrowser.setText(label_date)
        self.ui.textBrowser_2.setText(label_time)


def main():
    """Main entry point for JARVIS application"""
    app = QApplication(sys.argv)
    
    # Show loading screen with MP4 video (embedded audio)
    video_path = os.path.join(BASE_DIR, 'Jarvis', 'utils', 'videos', '50504.mp4')
    
    # Create and show loading screen
    loading_screen = LoadingScreen(video_path)
    loading_screen.show()
    
    # Process events until user clicks Run or Exit
    while loading_screen.isVisible():
        app.processEvents()
    
    # If user clicked Run, continue to main application
    if loading_screen.run_clicked:
        jarvis = Main()
        jarvis.show()
        exit(app.exec_())
    else:
        # User clicked Exit
        sys.exit(0)


if __name__ == "__main__":
    main()
