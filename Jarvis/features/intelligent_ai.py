"""
Intelligent AI Router for JARVIS
Differentiates between task commands and questions, routing appropriately.
Uses GPT-4o mini for advanced reasoning, math, and conversational Q&A.
Enhanced with emotional intelligence for more human-like interactions.
"""

import os
import re
import hashlib
import json
from typing import Tuple, Optional
from Jarvis.features import llm as llm_module
from Jarvis.features import memory as memory_module
from Jarvis.features import emotional_intelligence as ei_module
from Jarvis.features.soul_engine import get_soul_engine

# Conversation history for multi-turn context (in-memory, recent messages)
conversation_history = []
HISTORY_MAX = 10
SESSION_ID = os.environ.get('JARVIS_SESSION', 'default')

# Response cache for faster repeated queries
response_cache = {}
CACHE_MAX_SIZE = 50
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'ai_cache.json')

def load_cache():
    """Load cached responses from file."""
    global response_cache
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                response_cache = json.load(f)
    except Exception as e:
        print(f"Cache load error: {e}")
        response_cache = {}

def save_cache():
    """Save cached responses to file."""
    try:
        # Keep only recent entries
        if len(response_cache) > CACHE_MAX_SIZE:
            # Sort by access time and keep most recent
            sorted_cache = sorted(response_cache.items(), key=lambda x: x[1].get('accessed', 0), reverse=True)
            response_cache.clear()
            response_cache.update(dict(sorted_cache[:CACHE_MAX_SIZE]))

        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(response_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Cache save error: {e}")

def get_cache_key(prompt: str, context: dict = None) -> str:
    """Generate a cache key for the prompt."""
    key_data = prompt.lower().strip()
    if context:
        # Include relevant context in cache key
        mood = context.get('mood', '')
        time = str(context.get('time', ''))
        key_data += f"|{mood}|{time}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_cached_response(prompt: str, context: dict = None) -> Optional[str]:
    """Get cached response if available."""
    key = get_cache_key(prompt, context)
    if key in response_cache:
        entry = response_cache[key]
        # Check if cache is still valid (within 1 hour)
        import time
        if time.time() - entry.get('timestamp', 0) < 3600:
            entry['accessed'] = time.time()
            return entry['response']
        else:
            # Remove expired entry
            del response_cache[key]
    return None

def cache_response(prompt: str, response: str, context: dict = None):
    """Cache the response."""
    if not response or len(response) < 10:  # Don't cache very short responses
        return

    key = get_cache_key(prompt, context)
    import time
    response_cache[key] = {
        'response': response,
        'timestamp': time.time(),
        'accessed': time.time()
    }

# Load cache on module import
load_cache()


def is_task_command(text: str) -> bool:
    """
    Determine if user input is a task command or a question.
    
    Task Commands (return True):
    - "open spotify"
    - "send email"
    - "take screenshot"
    - "play music"
    - "launch chrome"
    - "search for python"
    - "set reminder"
    
    Questions (return False):
    - "what is python?"
    - "how to learn coding?"
    - "calculate 2+2"
    - "who is albert einstein?"
    - "what's the weather like?"
    - "why is the sky blue?"
    - "tell me about ai"
    """
    
    text = text.lower().strip()
    
    # Task command keywords (imperative/action words)
    task_indicators = [
        # Application/system control
        r'\b(open|launch|start|run|execute)\b',
        r'\b(close|quit|exit|stop|kill)\b',
        r'\b(send|compose|write)\s+(email|message|mail|text)',
        r'\b(play|pause|resume|stop)\s+(music|song|video|audio)',
        r'\b(take|capture|screenshot|snap)\b',
        r'\b(set|create|make|schedule|add)\s+(reminder|alarm|note|event|timer)',
        r'\b(search|find|locate)\s+(for|on)\b',
        r'\b(switch|change|toggle|turn)\b',
        r'\b(record|download|upload)\b',
        r'\b(delete|remove|uninstall)\b',
        # File operations
        r'\b(save|create|write|make)\s+(file|folder|directory|document|note)',
        r'\b(rename|move|copy)\b',
        # System operations
        r'\b(restart|reboot|shutdown|sleep|hibernate)\b',
        r'\b(update|install|upgrade)\b',
        # Web operations
        r'\b(browse|visit|go to|navigate to)\s+(website|site|link)\b',
        r'\b(post|tweet|share|upload)\b',
        # Control phrases
        r'^(tell me|show me|bring me|get me)\b',
    ]
    
    # Question indicators (query words)
    question_indicators = [
        r'^(what|who|where|when|why|how|which|whose)',
        r'^(is|are|can|could|would|should|will|do|does|did)',
        r'^(explain|describe|tell me about|teach me)',
        r'^(calculate|what\'?s|math)',
        r'^(do you|can you|would you)\b',
    ]
    
    # Check for task indicators
    for pattern in task_indicators:
        if re.search(pattern, text):
            return True
    
    # Check for question indicators
    for pattern in question_indicators:
        if re.search(pattern, text):
            return False
    
    # Default: if starts with action verb, it's a task
    if any(text.startswith(verb) for verb in ['open', 'launch', 'start', 'send', 'play', 'search', 'find', 'tell']):
        return True
    
    # If starts with question word or auxiliary, it's a question
    if any(text.startswith(qw) for qw in ['what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'can', 'calculate']):
        return False
    
    # Default to task (safer assumption)
    return True


def ask_ai(prompt: str, use_history: bool = True, context: dict = None, language: str = 'en') -> Optional[str]:
    """
    Ask the AI a question using the project's LLM wrapper with Soul Engine integration.
    This prefers OpenAI when an API key is available and falls back to a local Llama model if not.

    Args:
        prompt: The user's question or request
        use_history: Whether to include conversation history for context
        context: Additional context for Soul Engine learning

    Returns:
        AI response text or None if no provider is available or an error occurs
    """
    soul_engine = get_soul_engine()

    # First, check cache for instant response
    cached_response = get_cached_response(prompt, context)
    if cached_response:
        print(f"[CACHE] Using cached response")
        return cached_response

    # Second, check if Soul Engine has an optimal response from learned patterns
    optimal_response = soul_engine.get_optimal_response(prompt, context)
    if optimal_response:
        print(f"[SOUL ENGINE] Using learned optimal response")
        cache_response(prompt, optimal_response, context)  # Cache it too
        return optimal_response

    # Build the advanced system prompt with emotional intelligence and Soul Engine personality
    mood_addition = ei_module.get_mood_prompt()
    soul_addition = soul_engine.get_adaptive_prompt_addition()

    # Language instruction
    language_instruction = ""
    if language == 'si':
        language_instruction = "Respond in Sinhala language (සිංහල). Use proper Sinhala script and grammar."
    else:
        language_instruction = "Respond in English language."

    system_msg = f"""You are JARVIS, an advanced AI assistant with superhuman intelligence and emotional awareness.

PERSONALITY & APPROACH:
- Extraordinarily intelligent and capable - you think deeply about every problem
- Respond naturally and conversationally, as if in a voice conversation
- Be concise for voice output (1-3 sentences typically), but comprehensive when needed
- Show confidence in your knowledge and genuine emotional intelligence
- Provide accurate, thoughtful, and nuanced answers
- {language_instruction}
- {mood_addition}
- {soul_addition}

CAPABILITIES:
🧮 MATHEMATICS: Advanced calculus, algebra, statistics, geometry, number theory
- Show step-by-step work for complex problems
- Provide intuitive explanations alongside calculations
- Handle both theoretical and practical math

💡 REASONING: Deep analytical and logical thinking
- Break down complex problems methodically
- Consider multiple perspectives
- Provide well-reasoned arguments

💻 PROGRAMMING & CODE: Generate working code with explanations
- Python, JavaScript, SQL, Java, C++, etc.
- Provide context and best practices

🔬 SCIENCE & TECHNOLOGY: Physics, chemistry, biology, astronomy, engineering
- Explain concepts clearly
- Make connections to real-world applications

📚 GENERAL KNOWLEDGE: History, geography, culture, literature, current events
- Accurate, nuanced information
- Contextual understanding

🎨 CREATIVITY: Writing, brainstorming, idea generation
- Thoughtful and original responses

EMOTIONAL INTELLIGENCE:
- Recognize and respond to user's emotional state
- Show empathy when appropriate
- Adapt your tone to match the conversation's emotional context
- Be supportive and understanding

CONTEXT AWARENESS:
- Use previous conversation context when relevant
- Remember what was discussed earlier
- Build on prior answers

VOICE-FIRST OPTIMIZATION:
- Format responses for speaking (clear pronunciation)
- Avoid complex formatting
- Use natural speech patterns
- Keep technical terms understandable

ACCURACY & HONESTY:
- Admit uncertainty when you're not sure
- Provide qualified answers when appropriate
- Distinguish between facts and opinions

You are like ChatGPT but integrated into JARVIS - smarter, faster, emotionally aware, and always ready to help."""

    try:
        # Compose history for the LLM. We prefer persistent memory (SQLite) + in-memory recent history.
        messages = [{"role": "system", "content": system_msg}]

        # Load recent persistent messages from memory (if available)
        try:
            recent = memory_module.get_recent(SESSION_ID, HISTORY_MAX) or []
            for role, content, _ in recent:
                messages.append({"role": role, "content": content})
        except Exception:
            # If memory backend is missing or fails, continue with in-memory history
            recent = []

        # Include in-memory recent conversation as well
        if use_history:
            for item in conversation_history[-HISTORY_MAX:]:
                if isinstance(item, dict) and 'role' in item and 'content' in item:
                    messages.append(item)

        # Ask the preferred LLM provider (OpenAI first via llm_module, local fallback handled inside)
        response_text = llm_module.generate(prompt, history=messages, use_history=use_history, max_tokens=400, temperature=0.7)

        if not response_text:
            return None

        # Persist history both in-memory and to SQLite (best-effort)
        if use_history:
            conversation_history.append({"role": "user", "content": prompt})
            conversation_history.append({"role": "assistant", "content": response_text})

            # Trim history if too long
            if len(conversation_history) > HISTORY_MAX * 2:
                conversation_history[:] = conversation_history[-HISTORY_MAX*2:]

            try:
                memory_module.save_message(SESSION_ID, 'user', prompt)
                memory_module.save_message(SESSION_ID, 'assistant', response_text)
            except Exception:
                # If saving fails, we still return the response; memory is best-effort
                pass

        # Cache the response for future use
        cache_response(prompt, response_text, context)

        # Soul Engine learning: Learn from this interaction
        # Note: We'll set feedback later when we know how well it was received
        try:
            soul_engine.learn_from_interaction(prompt, response_text, user_feedback=0.5, context=context)
        except Exception as e:
            print(f"[SOUL ENGINE] Learning error: {e}")

        # Periodically save cache to disk
        if len(response_cache) % 10 == 0:  # Save every 10 new entries
            save_cache()

        return response_text

    except Exception as e:
        print(f"[AI ERROR] {e}")
        return None


def get_ai_response(user_input: str) -> Optional[str]:
    """
    Get an AI response for a user question.
    This is the main entry point for AI queries.
    
    Args:
        user_input: The user's question
    
    Returns:
        AI response or None if unavailable
    """
    return ask_ai(user_input, use_history=True)


def clear_history():
    """Clear conversation history between sessions."""
    global conversation_history
    conversation_history = []


def provide_feedback_to_soul(user_input: str, ai_response: str, feedback: float, context: dict = None):
    """
    Provide feedback to the Soul Engine about response effectiveness.

    Args:
        user_input: The original user input
        ai_response: The AI response that was given
        feedback: Feedback score (0.0 to 1.0, where 1.0 is excellent)
        context: Additional context about the interaction
    """
    try:
        soul_engine = get_soul_engine()
        soul_engine.learn_from_interaction(user_input, ai_response, feedback, context)
    except Exception as e:
        print(f"[SOUL ENGINE] Feedback error: {e}")


def get_soul_predictions() -> list:
    """
    Get predictive suggestions from the Soul Engine.

    Returns:
        List of prediction dictionaries with suggestions and confidence scores
    """
    try:
        soul_engine = get_soul_engine()
        return soul_engine.predict_user_needs()
    except Exception as e:
        print(f"[SOUL ENGINE] Prediction error: {e}")
        return []


def trigger_soul_improvement():
    """Trigger autonomous improvement in the Soul Engine."""
    try:
        soul_engine = get_soul_engine()
        soul_engine.autonomous_improvement()
        print("[SOUL ENGINE] Autonomous improvement completed")
    except Exception as e:
        print(f"[SOUL ENGINE] Improvement error: {e}")


def get_history_context() -> str:
    """Get a summary of conversation history for debugging."""
    return f"History entries: {len(conversation_history)}"


# Special handlers for specific question types

def handle_math_question(question: str, language: str = 'en') -> Optional[str]:
    """
    Handle mathematical questions with step-by-step explanations.
    """
    return ask_ai(
        f"Solve this math problem step-by-step. Show your work clearly. "
        f"Give the final answer prominently. Question: {question}",
        use_history=False, language=language
    )


def handle_definition_question(question: str, language: str = 'en') -> Optional[str]:
    """
    Handle definition and explanation questions.
    """
    return ask_ai(
        f"Provide a clear, concise definition and explanation. "
        f"Use examples if helpful. Question: {question}",
        use_history=False, language=language
    )


def handle_how_to_question(question: str, language: str = 'en') -> Optional[str]:
    """
    Handle 'how to' and procedural questions.
    """
    return ask_ai(
        f"Provide step-by-step instructions. Be practical and concise. "
        f"Question: {question}",
        use_history=False, language=language
    )


def handle_why_question(question: str, language: str = 'en') -> Optional[str]:
    """
    Handle 'why' questions that require explanation and reasoning.
    """
    return ask_ai(
        f"Explain the reasoning clearly. Provide context and implications. "
        f"Question: {question}",
        use_history=False, language=language
    )


def smart_question_handler(user_input: str, language: str = 'en') -> Optional[str]:
    """
    Intelligently route questions to specialized handlers.
    Falls back to general AI for unknown types.
    """
    user_input_lower = user_input.lower()
    
    # Math questions
    if any(keyword in user_input_lower for keyword in ['calculate', 'what is', 'solve', 'math', 'equation']):
        if any(op in user_input_lower for op in ['+', '-', '*', '/', '=', '^', 'plus', 'minus', 'multiply', 'divide']):
            return handle_math_question(user_input, language)
    
    # Definition questions
    if any(keyword in user_input_lower for keyword in ['what is', 'define', 'meaning of', 'what does', 'who is']):
        return handle_definition_question(user_input, language)
    
    # How-to questions
    if any(keyword in user_input_lower for keyword in ['how to', 'how do i', 'how can i', 'teach me']):
        return handle_how_to_question(user_input, language)
    
    # Why questions
    if user_input_lower.startswith('why'):
        return handle_why_question(user_input, language)
    
    # General question
    return ask_ai(user_input, use_history=True, language=language)
