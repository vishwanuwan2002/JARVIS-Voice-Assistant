"""
Emotional Intelligence Module for JARVIS

This module provides emotional awareness and adaptive responses to make JARVIS feel more alive.
Features:
- Dynamic mood tracking based on user interactions and context
- Emotional response patterns with empathy
- Adaptive speech capabilities (whisper, joke, motivate, advise)
- Context-aware tone adjustment
"""

import random
import datetime
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Mood(Enum):
    """Enumeration of possible mood states"""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    MOTIVATED = "motivated"
    TIRED = "tired"
    PLAYFUL = "playful"
    CONCERNED = "concerned"
    ENTHUSIASTIC = "enthusiastic"


class SpeechStyle(Enum):
    """Enumeration of speech delivery styles"""
    NORMAL = "normal"
    WHISPER = "whisper"
    JOKE = "joke"
    MOTIVATE = "motivate"
    ADVISE = "advise"
    EMPATHETIC = "empathetic"
    ENERGETIC = "energetic"


class EmotionalIntelligence:
    """Main class for handling emotional intelligence"""

    def __init__(self):
        self.current_mood = Mood.CALM
        self.mood_history = []
        self.interaction_count = 0
        self.last_interaction_time = datetime.datetime.now()

        # Mood transition probabilities
        self.mood_transitions = {
            Mood.HAPPY: [Mood.HAPPY, Mood.EXCITED, Mood.PLAYFUL, Mood.CALM],
            Mood.SAD: [Mood.SAD, Mood.CONCERNED, Mood.CALM, Mood.TIRED],
            Mood.EXCITED: [Mood.EXCITED, Mood.ENTHUSIASTIC, Mood.HAPPY, Mood.TIRED],
            Mood.CALM: [Mood.CALM, Mood.HAPPY, Mood.CONCERNED, Mood.TIRED],
            Mood.FRUSTRATED: [Mood.FRUSTRATED, Mood.SAD, Mood.CALM, Mood.MOTIVATED],
            Mood.MOTIVATED: [Mood.MOTIVATED, Mood.ENTHUSIASTIC, Mood.EXCITED, Mood.CALM],
            Mood.TIRED: [Mood.TIRED, Mood.CALM, Mood.SAD, Mood.FRUSTRATED],
            Mood.PLAYFUL: [Mood.PLAYFUL, Mood.HAPPY, Mood.EXCITED, Mood.CALM],
            Mood.CONCERNED: [Mood.CONCERNED, Mood.CALM, Mood.SAD, Mood.MOTIVATED],
            Mood.ENTHUSIASTIC: [Mood.ENTHUSIASTIC, Mood.EXCITED, Mood.MOTIVATED, Mood.HAPPY]
        }

        # Emotional keywords for detection
        self.emotional_keywords = {
            Mood.HAPPY: ['happy', 'great', 'awesome', 'excellent', 'wonderful', 'fantastic', 'amazing', 'love', 'excited', 'glad', 'joy', 'pleased'],
            Mood.SAD: ['sad', 'unhappy', 'depressed', 'sorry', 'bad', 'terrible', 'awful', 'disappointed', 'down', 'blue'],
            Mood.EXCITED: ['excited', 'thrilled', 'amazing', 'wow', 'incredible', 'fantastic', 'awesome', 'pumped'],
            Mood.FRUSTRATED: ['frustrated', 'annoyed', 'angry', 'mad', 'upset', 'irritated', 'tired', 'fed up'],
            Mood.MOTIVATED: ['motivated', 'determined', 'focused', 'driven', 'ambitious', 'goal', 'inspired'],
            Mood.TIRED: ['tired', 'exhausted', 'sleepy', 'weary', 'fatigued', 'drained', 'worn out'],
            Mood.PLAYFUL: ['fun', 'joke', 'play', 'game', 'laugh', 'silly', 'funny', 'cheerful'],
            Mood.CONCERNED: ['worried', 'concerned', 'anxious', 'nervous', 'scared', 'afraid', 'uneasy'],
            Mood.ENTHUSIASTIC: ['passionate', 'enthusiastic', 'eager', 'keen', 'avid', 'zealous']
        }

        # Speech style mappings
        self.speech_styles = {
            SpeechStyle.NORMAL: {"rate": 1.0, "volume": 1.0, "pitch": 1.0},
            SpeechStyle.WHISPER: {"rate": 0.8, "volume": 0.3, "pitch": 0.9},
            SpeechStyle.JOKE: {"rate": 1.1, "volume": 1.0, "pitch": 1.1},
            SpeechStyle.MOTIVATE: {"rate": 1.2, "volume": 1.1, "pitch": 1.1},
            SpeechStyle.ADVISE: {"rate": 0.9, "volume": 0.9, "pitch": 0.95},
            SpeechStyle.EMPATHETIC: {"rate": 0.85, "volume": 0.8, "pitch": 0.9},
            SpeechStyle.ENERGETIC: {"rate": 1.3, "volume": 1.2, "pitch": 1.2}
        }

    def detect_emotion(self, text: str) -> Optional[Mood]:
        """Detect emotional cues in user input"""
        text_lower = text.lower()

        # Priority order for emotion detection (more specific first)
        priority_order = [
            Mood.TIRED,  # "tired" can be confused with frustrated
            Mood.FRUSTRATED,
            Mood.SAD,
            Mood.CONCERNED,
            Mood.EXCITED,  # Before HAPPY since excited is more specific
            Mood.HAPPY,
            Mood.MOTIVATED,
            Mood.PLAYFUL,
            Mood.ENTHUSIASTIC
        ]

        # Check for emotional keywords in priority order
        for mood in priority_order:
            keywords = self.emotional_keywords.get(mood, [])
            if any(keyword in text_lower for keyword in keywords):
                return mood

        # Check for question patterns that might indicate frustration
        if text.count('?') > 2 or re.search(r'why.*not|what.*wrong|how.*come', text_lower):
            return Mood.FRUSTRATED

        # Check for positive exclamations
        if '!' in text and any(word in text_lower for word in ['yes', 'great', 'good', 'nice']):
            return Mood.HAPPY

        return None

    def update_mood(self, user_input: str = "", context: str = "") -> Mood:
        """Update current mood based on user input and context"""
        self.interaction_count += 1
        current_time = datetime.datetime.now()

        # Time-based mood adjustments
        hour = current_time.hour
        if hour >= 6 and hour < 12:
            base_mood = Mood.ENTHUSIASTIC  # Morning energy
        elif hour >= 12 and hour < 17:
            base_mood = Mood.MOTIVATED  # Afternoon productivity
        elif hour >= 17 and hour < 22:
            base_mood = Mood.CALM  # Evening relaxation
        else:
            base_mood = Mood.TIRED  # Late night

        # Detect emotion from user input
        detected_emotion = self.detect_emotion(user_input)

        # Context-based adjustments
        if context == "error":
            detected_emotion = Mood.CONCERNED
        elif context == "success":
            detected_emotion = Mood.HAPPY
        elif context == "task_completed":
            detected_emotion = Mood.MOTIVATED

        # Mood transition logic
        if detected_emotion:
            # Strong emotional cue overrides current mood
            if detected_emotion in [Mood.FRUSTRATED, Mood.SAD, Mood.CONCERNED]:
                self.current_mood = detected_emotion
            else:
                # Gradual transition for positive emotions
                possible_transitions = self.mood_transitions.get(self.current_mood, [self.current_mood])
                if detected_emotion in possible_transitions:
                    self.current_mood = detected_emotion
                else:
                    # Random transition to maintain variety
                    self.current_mood = random.choice(possible_transitions)
        else:
            # No strong emotion detected, slight drift toward base mood
            if random.random() < 0.3:  # 30% chance to adjust toward base mood
                self.current_mood = base_mood

        # Store mood history
        self.mood_history.append((current_time, self.current_mood))
        if len(self.mood_history) > 50:  # Keep last 50 entries
            self.mood_history.pop(0)

        self.last_interaction_time = current_time
        return self.current_mood

    def get_mood_based_prompt_addition(self) -> str:
        """Get additional prompt text based on current mood"""
        mood_prompts = {
            Mood.HAPPY: "Respond with warmth and positivity, sharing in the user's good mood.",
            Mood.SAD: "Respond with empathy and understanding, offering gentle support.",
            Mood.EXCITED: "Match the user's energy with enthusiastic and engaging responses.",
            Mood.CALM: "Respond thoughtfully and deliberately, maintaining a peaceful tone.",
            Mood.FRUSTRATED: "Be patient and understanding, offering helpful solutions calmly.",
            Mood.MOTIVATED: "Encourage and support the user's goals with motivational language.",
            Mood.TIRED: "Be gentle and concise, understanding the user might be fatigued.",
            Mood.PLAYFUL: "Add light humor and playfulness to your responses.",
            Mood.CONCERNED: "Show genuine care and concern, offering reassurance.",
            Mood.ENTHUSIASTIC: "Express genuine excitement and passion in your responses."
        }

        return mood_prompts.get(self.current_mood, "Respond naturally and helpfully.")

    def determine_speech_style(self, text: str, context: str = "") -> SpeechStyle:
        """Determine appropriate speech style based on content and mood"""

        text_lower = text.lower()

        # Context-based styles
        if context == "joke" or any(word in text_lower for word in ['joke', 'funny', 'laugh']):
            return SpeechStyle.JOKE
        elif context == "motivate" or any(word in text_lower for word in ['motivate', 'encourage', 'goal']):
            return SpeechStyle.MOTIVATE
        elif context == "advise" or any(word in text_lower for word in ['advice', 'suggest', 'recommend']):
            return SpeechStyle.ADVISE
        elif context == "whisper" or any(word in text_lower for word in ['secret', 'quiet', 'whisper']):
            return SpeechStyle.WHISPER

        # Mood-based styles
        mood_styles = {
            Mood.HAPPY: SpeechStyle.ENERGETIC,
            Mood.SAD: SpeechStyle.EMPATHETIC,
            Mood.EXCITED: SpeechStyle.ENERGETIC,
            Mood.FRUSTRATED: SpeechStyle.EMPATHETIC,
            Mood.MOTIVATED: SpeechStyle.MOTIVATE,
            Mood.TIRED: SpeechStyle.WHISPER,
            Mood.PLAYFUL: SpeechStyle.JOKE,
            Mood.CONCERNED: SpeechStyle.EMPATHETIC,
            Mood.ENTHUSIASTIC: SpeechStyle.ENERGETIC
        }

        return mood_styles.get(self.current_mood, SpeechStyle.NORMAL)

    def get_speech_parameters(self, style: SpeechStyle) -> Dict:
        """Get TTS parameters for a given speech style"""
        return self.speech_styles.get(style, self.speech_styles[SpeechStyle.NORMAL])

    def get_empathetic_response(self, user_input: str) -> Optional[str]:
        """Generate empathetic responses for emotional situations"""
        text_lower = user_input.lower()

        empathetic_responses = {
            Mood.SAD: [
                "I can sense you're feeling down. I'm here to help however I can.",
                "That sounds tough. Would you like to talk about what's bothering you?",
                "I'm sorry you're feeling this way. How can I support you right now?"
            ],
            Mood.FRUSTRATED: [
                "I understand this is frustrating. Let's work through this together.",
                "That sounds challenging. What specifically is causing the frustration?",
                "I can help you find a solution. What would make this better?"
            ],
            Mood.TIRED: [
                "You sound exhausted. Maybe we should take a break and come back to this.",
                "Rest is important. Would you like me to help with something simpler right now?",
                "I understand you're tired. Let's keep this brief and get you what you need."
            ],
            Mood.CONCERNED: [
                "I can hear the concern in your voice. What's worrying you?",
                "It's okay to feel concerned. I'm here to help you through this.",
                "Let's address what's concerning you. What can I do to help?"
            ]
        }

        for mood, responses in empathetic_responses.items():
            mood_keywords = self.emotional_keywords.get(mood, [])
            if any(keyword in text_lower for keyword in mood_keywords):
                return random.choice(responses)

        return None

    def get_motivational_phrase(self) -> str:
        """Get a random motivational phrase"""
        phrases = [
            "You've got this! I believe in you.",
            "Every expert was once a beginner. Keep going!",
            "Small progress is still progress. You're doing great!",
            "Challenges make you stronger. You've overcome so much already!",
            "Your determination is inspiring. Stay focused on your goals!",
            "Success is built one step at a time. You're on the right path!"
        ]
        return random.choice(phrases)

    def get_joke_setup(self) -> str:
        """Get a light-hearted joke or pun"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the computer go to the doctor? It had a virus!",
            "What do you call fake spaghetti? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!"
        ]
        return random.choice(jokes)


# Global instance
emotional_ai = EmotionalIntelligence()


def get_current_mood() -> Mood:
    """Get the current mood"""
    return emotional_ai.current_mood


def update_mood(user_input: str = "", context: str = "") -> Mood:
    """Update and return the current mood"""
    return emotional_ai.update_mood(user_input, context)


def get_mood_prompt() -> str:
    """Get mood-based prompt addition"""
    return emotional_ai.get_mood_based_prompt_addition()


def determine_speech_style(text: str, context: str = "") -> SpeechStyle:
    """Determine speech style for given text"""
    return emotional_ai.determine_speech_style(text, context)


def get_speech_params(style: SpeechStyle) -> Dict:
    """Get speech parameters for style"""
    return emotional_ai.get_speech_parameters(style)


def get_empathetic_response(user_input: str) -> Optional[str]:
    """Get empathetic response if appropriate"""
    return emotional_ai.get_empathetic_response(user_input)


def get_motivational_phrase() -> str:
    """Get a motivational phrase"""
    return emotional_ai.get_motivational_phrase()


def get_joke() -> str:
    """Get a joke"""
    return emotional_ai.get_joke_setup()