# JARVIS - AI-Powered Voice Assistant 

> *"Your intelligent, emotionally-aware, self-evolving desktop companion"*

JARVIS is a feature-rich, AI-powered voice assistant for Windows built with Python. It combines voice recognition, natural language processing, emotional intelligence, and a self-learning "Soul Engine" to deliver a truly interactive and personalized assistant experience.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

##  Features

###  Intelligent AI (Powered by OpenAI)
- Natural language understanding for both questions and task commands
- Automatic differentiation between queries and actionable commands
- Smart response caching for faster repeated interactions
- Multi-turn conversation history with context awareness
- Math, definitions, and general knowledge via GPT-4o mini

###  Voice Interaction
- **Speech-to-Text**: Google Speech Recognition (primary) with Whisper compatibility
- **Text-to-Speech**: pyttsx3 (offline) with ElevenLabs API support for ultra-realistic voices
- Adaptive voice styles based on context (whisper, energetic, empathetic, etc.)

###  Emotional Intelligence
- Dynamic mood tracking that evolves with user interactions
- 10 distinct mood states (Happy, Sad, Excited, Calm, Playful, etc.)
- Context-aware emotional responses with empathy
- Adaptive speech delivery (joke style, motivational, advisory, empathetic)
- Mood-based response selection

###  Soul Engine (Self-Evolving Layer)
- **Autonomous learning** from every user interaction
- **Personality matrix** that evolves over time
- **Predictive suggestions** - proactively offers help based on usage patterns
- **Reinforcement learning** to optimize responses from feedback
- **Memory decay** - recent interactions weighted more heavily
- Database-driven personality evolution (SQLite)

###  Core Capabilities

| Category | Commands |
|----------|----------|
| **🌤️ Weather** | Get current weather for any city |
| **📰 News** | Top headlines from Times of India |
| **💻 System** | System stats, IP address, file visibility |
| **📧 Email** | Send emails via SMTP |
| **📅 Calendar** | Google Calendar integration |
| **🌐 Web** | Open websites/apps, Google search |
| **▶️ Media** | YouTube playback, local music |
| **📍 Location** | Current location, distance to places |
| **📝 Notes** | Take and manage notes |
| **📸 Screenshots** | Capture and display screenshots |
| **🔢 Math** | Computational queries (Wolfram Alpha) |
| **📖 Knowledge** | Wikipedia lookups, definitions |
| **🎭 Fun** | Jokes, motivation, playful banter |
| **🗣️ Greetings** | Context-aware greeting responses |

###  Graphical User Interface
- PyQt5-based modern GUI with animated elements
- Live wallpaper and initiating animations (GIF)
- Loading screen with video playback
- Real-time clock and date display
- Start/Exit controls

###  User Profile Learning
- Remembers user name and preferences
- Learns favorite apps over time
- Stores interaction history in SQLite
- Personalized responses based on usage patterns

###  Multi-Language Support
- Language detection via `langdetect`
- Configurable default language
- AI responses in user's preferred language

---

##  Quick Start

### Prerequisites
- **Windows 10/11**
- **Python 3.8+** (Python 3.8.10 recommended)
- **Working microphone**
- **Internet connection** (for AI features, weather, news, etc.)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/JARVIS-master.git
cd JARVIS-master

# 2. Set up the environment (recommended)
python -m venv Jarvis
Jarvis\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API keys (see Configuration section)
```

### Configuration

#### 1. OpenAI API Key (Required for AI features)
Set your OpenAI API key as an environment variable:

```bash
# PowerShell (temporary)
$env:OPENAI_API_KEY = 'sk-your-key-here'

# Or permanently via Windows Environment Variables
# Settings → System → Environment Variables → New
# Name: OPENAI_API_KEY   Value: sk-your-key-here
```

Or create a `.env` file (copy from `.env.example`):
```
OPENAI_API_KEY=sk-your-key-here
```

#### 2. Microphone Setup
Edit `Jarvis/config/config.py`:

```python
# Find available microphones:
python -c "import speech_recognition as sr; [print(i, name) for i, name in enumerate(sr.Microphone.list_microphone_names())]"

# Then set:
microphone_index = 1  # Change 1 to your microphone's index
```

#### 3. Optional API Keys

| Service | Config Field | Purpose |
|---------|-------------|---------|
| Wolfram Alpha | `wolframalpha_id` | Advanced math/computational queries |
| OpenWeatherMap | `openweathermap_api_key` | Weather data |
| ElevenLabs (TTS) | Environment: `ELEVENLABS_API_KEY` | Ultra-realistic voice |
| Google Calendar | `credentials.json` | Calendar integration |

### Running JARVIS

```bash
# Method 1: Run directly
python main.py

# Method 2: One-click setup & run
python START_HERE.py
```

> **First run?** Use `python START_HERE.py` — it checks your setup, tests the AI, lists available microphones, and clears proxy settings automatically.

---

## 🎤 Voice Commands

### Greetings
- "Wake up Jarvis" / "Hey Jarvis" / "You there Jarvis"
- Just say "Jarvis" to get attention

### Information & Knowledge
- *"What is Python?"* / *"Who is Einstein?"*
- *"Tell me about black holes"*
- *"What's the weather in Tokyo?"*
- *"What's the news today?"* / *"Show me headlines"*
- *"Calculate 2 to the power of 10"*

### Productivity
- *"Open YouTube"* / *"Launch Chrome"*
- *"Send an email"*
- *"Make a note"* / *"Write this down"*
- *"What do I have on my calendar?"*
- *"Search Google for..."*

### Media & Entertainment
- *"Play [song name]"* (YouTube)
- *"Play music"* / *"Hit some music"*
- *"Tell me a joke"* / *"Make me laugh"*
- *"Motivate me"* / *"I need motivation"*

### System & Utilities
- *"What's my IP address?"*
- *"Show system info"*
- *"Take a screenshot"*
- *"Where am I?"* / *"Where is Paris?"*
- *"Hide all files"* / *"Make files visible"*
- *"Switch the window"*

### General Chat
- *"How are you?"* / *"How are you feeling?"*
- *"What's on your mind?"*
- Any question — JARVIS will use AI to respond intelligently

### Exit
- *"Goodbye"* / *"Bye"* / *"Go offline"*

---

##  Project Architecture

```
JARVIS-master/
├── main.py                          # Application entry point & GUI
├── START_HERE.py                    # One-click setup & diagnostics
├── SETUP_FIX.py                     # Advanced setup troubleshooting
├── diagnose.py                      # System diagnostics
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
│
├── Jarvis/
│   ├── __init__.py                  # JarvisAssistant core class
│   ├── memory.db                    # Conversation memory (SQLite)
│   ├── soul_engine.db               # Self-evolving personality DB
│   ├── user_profile.db              # User preferences & history
│   │
│   ├── config/
│   │   ├── config.py                # API keys & settings
│   │   ├── credentials.json         # Google Calendar OAuth
│   │   └── app_overrides.json       # App launch overrides
│   │
│   ├── features/
│   │   ├── intelligent_ai.py        # AI router (GPT-4o mini)
│   │   ├── emotional_intelligence.py# Mood & empathy engine
│   │   ├── soul_engine.py           # Self-learning layer
│   │   ├── user_profile.py          # User learning & history
│   │   ├── memory.py                # Conversation memory
│   │   ├── llm.py                   # LLM abstraction layer
│   │   ├── ai.py                    # AI wrapper utilities
│   │   ├── ai_cache.json            # Response cache file
│   │   │
│   │   ├── stt.py                   # Speech-to-Text (Whisper)
│   │   ├── tts.py                   # Text-to-Speech (ElevenLabs)
│   │   ├── gui.py                   # PyQt5 UI definitions
│   │   ├── loading_screen.py        # Video loading screen
│   │   │
│   │   ├── weather.py               # Weather service
│   │   ├── news.py                  # News headlines
│   │   ├── wikipedia.py             # Wikipedia lookups
│   │   ├── google_search.py         # Google search
│   │   ├── google_calendar.py       # Calendar integration
│   │   ├── youtube_search.py        # YouTube playback
│   │   ├── send_email.py            # Email via SMTP
│   │   ├── launch_app.py            # Launch Windows apps
│   │   ├── website_open.py          # Open websites
│   │   ├── app_finder.py            # Smart app/website detection
│   │   ├── date_time.py             # Date/time functions
│   │   ├── loc.py                   # Location services
│   │   ├── note.py                  # Note taking
│   │   ├── system_stats.py          # System information
│   │   └── ...
│   │
│   └── utils/
│       ├── images/                  # GUI animations (GIF)
│       └── videos/                  # Loading screen videos
│
├── driver/
│   └── chromedriver.exe             # Selenium WebDriver
│
├── wheels/                          # Pre-built wheel packages
├── scripts/                         # Utility scripts
└── gui.ui                           # Qt Designer UI file
```

---

##  How It Works

### Interaction Flow

```
User speaks → Microphone → Speech-to-Text (STT)
                              ↓
                    Intelligent AI Router
                    ┌───────────────┐
                    │ Is it a       │
                    │ question?     │ ← Emotional Intelligence checks mood
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    AI Question       Task Command      Fallback Handler
    (GPT-4o mini)   (Traditional)      (AI for anything else)
            │               │               │
            ▼               ▼               ▼
    Soul Engine learns ← Response → User Profile updated
                            │
                            ▼
                    Text-to-Speech (TTS)
                            │
                            ▼
                    User hears response
```

### Core Intelligence Components

1. **Intelligent AI Router** (`intelligent_ai.py`): Determines if input is a question or command, routes to the appropriate handler, and provides GPT-4o mini powered responses with caching.

2. **Emotional Intelligence** (`emotional_intelligence.py`): Tracks mood through interaction patterns, provides empathetic responses, adjusts speech style (tone/rate/pitch) based on context.

3. **Soul Engine** (`soul_engine.py`): A self-evolving layer that learns from every interaction. Maintains a personality matrix, predicts user needs, provides proactive suggestions, and improves autonomously through reinforcement learning.

4. **User Profile** (`user_profile.py`): Learns user preferences (favorite apps, common queries), stores interaction history, personalizes responses based on past behavior.

---

##  Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Microphone not detected** | Run `python scripts/list_mics.py` to find device index, set `microphone_index` in config |
| **AI not responding** | Ensure `OPENAI_API_KEY` environment variable is set correctly |
| **Proxy blocking** | Run `python START_HERE.py` which clears proxy settings automatically |
| **Dependency errors** | Activate virtual environment and run `pip install -r requirements.txt` |
| **Google Calendar not working** | Place `credentials.json` in `Jarvis/config/` and authenticate |

### Diagnostic Tools

```bash
# Run full diagnostics
python diagnose.py

# Test AI specifically
python test_intelligent_ai.py

# List available microphones
python scripts/list_mics.py

# Run setup fix script
python SETUP_FIX.py

# Test voice recognition
python test_microphones.py
```

### Quick Fix
Run the one-click fix script that automatically resolves the most common issues:

```bash
python START_HERE.py
```

---

## 💡 Tips & Tricks

- **First response may take 2-5 seconds** (API call to OpenAI) — subsequent responses are faster due to caching
- **Speak clearly** near your microphone for best recognition
- **Use natural language** — JARVIS understands conversational phrasing, not rigid commands
- **Mention context** — JARVIS uses emotional intelligence to adapt responses to your mood
- **For math**, try *"What's 15% of 200?"* or *"Calculate the square root of 144"*
- **For YouTube**, just say *"Play [song/video name]"* and JARVIS will find and play it

---

##  Dependencies

Key dependencies (see `requirements.txt` for full list):

- **PyQt5** — GUI framework
- **OpenAI** — GPT-4o mini for intelligent responses
- **SpeechRecognition** — Speech-to-text via Google API
- **pyttsx3** — Offline text-to-speech
- **ElevenLabs API** — Premium voice synthesis (optional)
- **pywhatkit** — YouTube/media playback
- **WolframAlpha** — Computational intelligence
- **PyAutoGUI** — Screen capture & window control
- **selenium** — Web automation
- **geopy/geocoder** — Location services
- **Pillow** — Image handling
- **requests** — HTTP API calls
- **python-dotenv** — Environment variable management
- **langdetect** — Language detection
- **wikipedia** — Knowledge lookups

##  License

This project is licensed under the MIT License.

