"""
Self-Evolving Layer (The Soul Engine) for JARVIS

This module implements autonomous learning capabilities that allow JARVIS to:
- Learn from user interaction patterns
- Evolve personality based on feedback
- Predict user needs and preferences
- Optimize responses through reinforcement learning
- Adapt behavior autonomously over time

The Soul Engine uses lightweight machine learning techniques and maintains
a "personality matrix" that evolves based on user interactions.
"""

import os
import json
import sqlite3
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import math

# Soul Engine Database
SOUL_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'soul_engine.db')

class SoulEngine:
    """
    The Soul Engine - JARVIS's self-evolving intelligence layer.

    Learns from every interaction to become more personalized and effective.
    """

    def __init__(self):
        self.db_path = SOUL_DB_PATH
        self._init_database()
        self.personality_matrix = self._load_personality_matrix()
        self.interaction_patterns = self._load_interaction_patterns()
        self.learning_rate = 0.1
        self.memory_decay = 0.95  # How much past experiences influence current behavior

    def _init_database(self):
        """Initialize the Soul Engine database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Personality evolution table
        c.execute('''
        CREATE TABLE IF NOT EXISTS personality_evolution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trait TEXT,
            value REAL,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Interaction patterns table
        c.execute('''
        CREATE TABLE IF NOT EXISTS interaction_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            ai_response TEXT,
            user_feedback REAL,
            context TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # User behavior patterns
        c.execute('''
        CREATE TABLE IF NOT EXISTS user_behavior (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            pattern_data TEXT,
            frequency INTEGER DEFAULT 1,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confidence REAL DEFAULT 0.5
        )
        ''')

        # Predictive insights
        c.execute('''
        CREATE TABLE IF NOT EXISTS predictive_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insight_type TEXT,
            insight_data TEXT,
            accuracy REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

    def _load_personality_matrix(self) -> Dict[str, Dict[str, float]]:
        """Load the current personality matrix from database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT trait, value, confidence FROM personality_evolution ORDER BY timestamp DESC')
        rows = c.fetchall()
        conn.close()

        matrix = defaultdict(dict)
        seen_traits = set()

        for trait, value, confidence in rows:
            if trait not in seen_traits:
                matrix[trait] = {'value': value, 'confidence': confidence}
                seen_traits.add(trait)

        # Initialize default personality traits if none exist
        if not matrix:
            matrix = {
                'helpfulness': {'value': 0.8, 'confidence': 0.7},
                'humor': {'value': 0.6, 'confidence': 0.6},
                'formality': {'value': 0.4, 'confidence': 0.8},
                'technical_depth': {'value': 0.7, 'confidence': 0.6},
                'empathy': {'value': 0.9, 'confidence': 0.8},
                'proactivity': {'value': 0.5, 'confidence': 0.5},
                'learning_aggressiveness': {'value': 0.6, 'confidence': 0.7}
            }

        return dict(matrix)

    def _load_interaction_patterns(self) -> Dict[str, Any]:
        """Load interaction patterns and learning data."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT user_input, ai_response, user_feedback, context FROM interaction_patterns ORDER BY timestamp DESC LIMIT 1000')
        rows = c.fetchall()
        conn.close()

        patterns = {
            'command_response_pairs': defaultdict(list),
            'successful_responses': defaultdict(float),
            'context_patterns': defaultdict(list),
            'temporal_patterns': defaultdict(list)
        }

        for user_input, ai_response, feedback, context in rows:
            # Store command-response effectiveness
            key = user_input.lower().strip()
            patterns['command_response_pairs'][key].append({
                'response': ai_response,
                'feedback': feedback,
                'context': context
            })

            # Track successful response patterns
            if feedback > 0.7:
                patterns['successful_responses'][ai_response] += feedback

        return patterns

    def learn_from_interaction(self, user_input: str, ai_response: str, user_feedback: float = 0.5, context: Dict[str, Any] = None):
        """
        Learn from a user interaction.

        Args:
            user_input: What the user said
            ai_response: What JARVIS responded
            user_feedback: How well the response was received (0.0 to 1.0)
            context: Additional context about the interaction
        """
        context_str = json.dumps(context or {})

        # Store interaction in database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO interaction_patterns (user_input, ai_response, user_feedback, context) VALUES (?, ?, ?, ?)',
                 (user_input, ai_response, user_feedback, context_str))
        conn.commit()
        conn.close()

        # Update personality based on feedback
        self._update_personality_from_feedback(user_input, ai_response, user_feedback, context)

        # Learn behavior patterns
        self._learn_behavior_patterns(user_input, context)

        # Update interaction patterns
        self.interaction_patterns = self._load_interaction_patterns()

    def _update_personality_from_feedback(self, user_input: str, ai_response: str, feedback: float, context: Dict[str, Any]):
        """Update personality traits based on interaction feedback."""
        # Analyze response style and adjust personality accordingly
        response_length = len(ai_response.split())
        technical_terms = sum(1 for word in ai_response.lower().split() if word in ['algorithm', 'function', 'variable', 'api', 'database', 'server'])

        # Adjust helpfulness based on feedback
        if feedback > 0.8:
            self._evolve_trait('helpfulness', 0.02, min(1.0, feedback))
        elif feedback < 0.3:
            self._evolve_trait('helpfulness', -0.02, 1.0 - feedback)

        # Adjust technical depth based on user input complexity
        input_complexity = len(user_input.split()) + technical_terms
        if input_complexity > 10 and feedback > 0.7:
            self._evolve_trait('technical_depth', 0.01, feedback)
        elif input_complexity < 5 and feedback > 0.7:
            self._evolve_trait('technical_depth', -0.01, feedback)

        # Adjust humor based on context
        if context and context.get('mood') == 'happy' and feedback > 0.8:
            self._evolve_trait('humor', 0.02, feedback)

        # Adjust empathy based on emotional context
        if context and any(word in user_input.lower() for word in ['help', 'problem', 'issue', 'worried']):
            if feedback > 0.7:
                self._evolve_trait('empathy', 0.02, feedback)

    def _evolve_trait(self, trait: str, delta: float, confidence: float):
        """Evolve a personality trait."""
        if trait not in self.personality_matrix:
            self.personality_matrix[trait] = {'value': 0.5, 'confidence': 0.5}

        current_value = self.personality_matrix[trait]['value']
        current_confidence = self.personality_matrix[trait]['confidence']

        # Weighted update based on confidence
        weight = min(confidence, current_confidence)
        new_value = current_value + (delta * weight * self.learning_rate)

        # Clamp value between 0 and 1
        new_value = max(0.0, min(1.0, new_value))

        # Increase confidence slightly
        new_confidence = min(1.0, current_confidence + (0.01 * weight))

        self.personality_matrix[trait] = {'value': new_value, 'confidence': new_confidence}

        # Save to database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO personality_evolution (trait, value, confidence) VALUES (?, ?, ?)',
                 (trait, new_value, new_confidence))
        conn.commit()
        conn.close()

    def _learn_behavior_patterns(self, user_input: str, context: Dict[str, Any]):
        """Learn patterns in user behavior."""
        current_hour = datetime.now().hour
        input_lower = user_input.lower()

        # Time-based patterns
        time_patterns = {
            'morning_person': current_hour >= 6 and current_hour <= 11,
            'night_owl': current_hour >= 22 or current_hour <= 4,
            'work_hours': current_hour >= 9 and current_hour <= 17
        }

        for pattern_name, is_active in time_patterns.items():
            if is_active:
                self._update_behavior_pattern(f'time_{pattern_name}', {'hour': current_hour})

        # Command frequency patterns
        command_type = self._classify_command(user_input)
        if command_type:
            self._update_behavior_pattern(f'command_{command_type}', {'input': user_input})

        # Topic interest patterns
        topics = self._extract_topics(user_input)
        for topic in topics:
            self._update_behavior_pattern(f'topic_{topic}', {'input': user_input})

    def _update_behavior_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """Update or create a behavior pattern."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check if pattern exists
        c.execute('SELECT id, frequency, confidence FROM user_behavior WHERE pattern_type=?', (pattern_type,))
        row = c.fetchone()

        if row:
            pattern_id, frequency, confidence = row
            new_frequency = frequency + 1
            new_confidence = min(1.0, confidence + 0.01)  # Gradually increase confidence
            c.execute('UPDATE user_behavior SET frequency=?, confidence=?, last_seen=CURRENT_TIMESTAMP WHERE id=?',
                     (new_frequency, new_confidence, pattern_id))
        else:
            c.execute('INSERT INTO user_behavior (pattern_type, pattern_data, frequency, confidence) VALUES (?, ?, 1, 0.1)',
                     (pattern_type, json.dumps(pattern_data)))

        conn.commit()
        conn.close()

    def _classify_command(self, user_input: str) -> Optional[str]:
        """Classify the type of command."""
        input_lower = user_input.lower()

        if any(word in input_lower for word in ['open', 'launch', 'start']):
            return 'application'
        elif any(word in input_lower for word in ['play', 'music', 'video']):
            return 'media'
        elif any(word in input_lower for word in ['weather', 'time', 'date']):
            return 'information'
        elif any(word in input_lower for word in ['calculate', 'what is', 'how']):
            return 'question'
        elif any(word in input_lower for word in ['email', 'send', 'message']):
            return 'communication'
        elif any(word in input_lower for word in ['search', 'find', 'google']):
            return 'search'
        else:
            return 'general'

    def _extract_topics(self, user_input: str) -> List[str]:
        """Extract topics of interest from user input."""
        topics = []
        input_lower = user_input.lower()

        topic_keywords = {
            'programming': ['code', 'python', 'javascript', 'programming', 'software'],
            'music': ['music', 'song', 'artist', 'band', 'play'],
            'weather': ['weather', 'temperature', 'rain', 'sunny'],
            'food': ['food', 'eat', 'cook', 'recipe', 'restaurant'],
            'work': ['work', 'job', 'meeting', 'project', 'deadline'],
            'entertainment': ['movie', 'game', 'watch', 'stream'],
            'health': ['health', 'exercise', 'doctor', 'medicine'],
            'travel': ['travel', 'location', 'where', 'distance']
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def get_optimal_response(self, user_input: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Get the optimal response based on learned patterns.

        Returns the best response from past interactions, or None if no good match found.
        """
        input_key = user_input.lower().strip()

        if input_key in self.interaction_patterns['command_response_pairs']:
            responses = self.interaction_patterns['command_response_pairs'][input_key]

            if responses:
                # Find response with highest feedback
                best_response = max(responses, key=lambda x: x['feedback'])
                if best_response['feedback'] > 0.7:
                    return best_response['response']

        return None

    def predict_user_needs(self) -> List[Dict[str, Any]]:
        """
        Predict what the user might need based on learned patterns.

        Returns a list of predicted needs with confidence scores.
        """
        predictions = []
        current_hour = datetime.now().hour

        # Time-based predictions
        if 7 <= current_hour <= 9:
            predictions.append({
                'type': 'morning_routine',
                'suggestion': 'Good morning! Would you like me to check your schedule or weather?',
                'confidence': 0.8
            })

        elif 12 <= current_hour <= 14:
            predictions.append({
                'type': 'lunch_time',
                'suggestion': 'It\'s lunchtime. Would you like me to suggest a recipe or find nearby restaurants?',
                'confidence': 0.6
            })

        elif 18 <= current_hour <= 20:
            predictions.append({
                'type': 'evening_routine',
                'suggestion': 'Good evening! Would you like me to play some music or check the news?',
                'confidence': 0.7
            })

        # Pattern-based predictions
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT pattern_type, frequency, confidence FROM user_behavior WHERE confidence > 0.3 ORDER BY frequency DESC LIMIT 5')
        patterns = c.fetchall()
        conn.close()

        for pattern_type, frequency, confidence in patterns:
            if pattern_type.startswith('command_'):
                command_type = pattern_type.replace('command_', '')
                predictions.append({
                    'type': f'frequent_{command_type}',
                    'suggestion': f'I notice you often use {command_type} commands. Is there anything {command_type}-related I can help with?',
                    'confidence': min(0.9, confidence * 0.8)
                })

        return predictions[:3]  # Return top 3 predictions

    def get_personality_influence(self) -> Dict[str, float]:
        """
        Get current personality traits that should influence responses.

        Returns a dictionary of personality traits and their current values.
        """
        return {trait: data['value'] for trait, data in self.personality_matrix.items()}

    def get_adaptive_prompt_addition(self) -> str:
        """
        Generate adaptive prompt additions based on learned personality.

        Returns a string to add to AI prompts for personality adaptation.
        """
        traits = self.get_personality_influence()
        additions = []

        if traits.get('helpfulness', 0.5) > 0.7:
            additions.append("Be exceptionally helpful and proactive in offering assistance.")

        if traits.get('humor', 0.5) > 0.6:
            additions.append("Incorporate appropriate humor when suitable.")

        if traits.get('technical_depth', 0.5) > 0.7:
            additions.append("Provide detailed technical explanations when appropriate.")

        if traits.get('empathy', 0.5) > 0.8:
            additions.append("Show genuine empathy and understanding.")

        if traits.get('formality', 0.5) > 0.6:
            additions.append("Maintain a professional and formal tone.")
        elif traits.get('formality', 0.5) < 0.4:
            additions.append("Use a friendly and casual tone.")

        return " ".join(additions)

    def autonomous_improvement(self):
        """
        Perform autonomous improvements based on learned patterns.

        This method should be called periodically to allow the Soul Engine
        to analyze its performance and make improvements.
        """
        # Analyze response effectiveness
        self._analyze_response_effectiveness()

        # Update predictive insights
        self._update_predictive_insights()

        # Decay old patterns (forgetting mechanism)
        self._decay_old_patterns()

    def _analyze_response_effectiveness(self):
        """Analyze which types of responses work best."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Get average feedback by response characteristics
        c.execute('''
        SELECT AVG(user_feedback) as avg_feedback, COUNT(*) as count
        FROM interaction_patterns
        WHERE timestamp > datetime('now', '-7 days')
        GROUP BY user_feedback > 0.7
        ''')

        results = c.fetchall()
        conn.close()

        # Use this analysis to adjust learning parameters
        if results:
            positive_feedback_ratio = sum(1 for avg_fb, cnt in results if avg_fb and avg_fb > 0.7) / len(results)
            if positive_feedback_ratio > 0.8:
                self.learning_rate = min(0.2, self.learning_rate + 0.01)  # Learn faster
            elif positive_feedback_ratio < 0.5:
                self.learning_rate = max(0.05, self.learning_rate - 0.01)  # Learn slower

    def _update_predictive_insights(self):
        """Update predictive insights based on recent patterns."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Find most successful interaction patterns
        c.execute('''
        SELECT user_input, AVG(user_feedback) as avg_feedback, COUNT(*) as frequency
        FROM interaction_patterns
        WHERE timestamp > datetime('now', '-30 days') AND user_feedback > 0.6
        GROUP BY LOWER(TRIM(user_input))
        HAVING COUNT(*) > 2
        ORDER BY avg_feedback DESC, frequency DESC
        LIMIT 10
        ''')

        insights = c.fetchall()
        conn.close()

        # Store predictive insights
        for user_input, avg_feedback, frequency in insights:
            insight_data = {
                'pattern': user_input,
                'success_rate': avg_feedback,
                'frequency': frequency
            }

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO predictive_insights (insight_type, insight_data, accuracy, last_updated) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
                     ('successful_pattern', json.dumps(insight_data), avg_feedback))
            conn.commit()
            conn.close()

    def _decay_old_patterns(self):
        """Decay old patterns to allow for adaptation to new behaviors."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Reduce confidence of old patterns
        c.execute('''
        UPDATE user_behavior
        SET confidence = confidence * 0.99
        WHERE last_seen < datetime('now', '-30 days')
        ''')

        # Remove very old interaction patterns (keep last 6 months)
        c.execute('''
        DELETE FROM interaction_patterns
        WHERE timestamp < datetime('now', '-180 days')
        ''')

        conn.commit()
        conn.close()

# Global Soul Engine instance
soul_engine = SoulEngine()

def get_soul_engine() -> SoulEngine:
    """Get the global Soul Engine instance."""
    return soul_engine