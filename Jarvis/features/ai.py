"""AI wrapper for Jarvis using OpenAI's Chat API.

This module provides advanced AI capabilities using GPT-4o mini, the most powerful and efficient model.
It includes conversation memory, reasoning, and handles math, Q&A, coding, and complex tasks.

To enable: set Jarvis.config.config.openai_api_key or OPENAI_API_KEY environment variable.
"""
import os
from typing import List, Optional

# Short-term conversation memory per session
conversation_history: List[dict] = []
HISTORY_MAX = 8  # keep more context for better reasoning


def ask(prompt: str, api_key: Optional[str] = None) -> str:
    """Ask the AI a question and return its text response.
    
    Uses GPT-4o mini - OpenAI's most capable and efficient model.
    Supports advanced reasoning, code generation, and multi-turn conversations.
    
    API key is read from (in order):
    1. Parameter api_key
    2. OPENAI_API_KEY environment variable
    3. .env file (if python-dotenv is installed)
    """
    try:
        import openai
    except ImportError:
        return "OpenAI library not installed. Run: pip install openai"

    # Try to load from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass  # python-dotenv not installed, but that's OK

    # Determine API key from parameter, environment, or .env
    key = api_key or os.environ.get('OPENAI_API_KEY')
    if not key:
        return "No OpenAI API key found. Set OPENAI_API_KEY environment variable. See config.py for instructions."

    # Set the API key for the openai module
    openai.api_key = key

    # Advanced system prompt for GPT-4o mini capabilities
    system_msg = """You are Jarvis, an advanced AI assistant powered by GPT-4o mini.
You are highly intelligent, reasoning through complex problems step-by-step.

Core Capabilities:
- 🧮 Advanced mathematics (calculus, algebra, statistics, logic)
- 💡 Deep reasoning and complex problem-solving
- 💻 Code generation (Python, JavaScript, SQL, etc.) with explanations
- 📊 Data analysis and pattern recognition
- 🎨 Creative writing, brainstorming, storytelling
- 🔬 Scientific explanations and technical concepts
- 🌐 Real-world knowledge and research
- 🎯 Task planning, decision-making, and strategy
- 🔄 Multi-turn conversations with context awareness
- 🚀 Cutting-edge AI capabilities

Interaction Style:
- Be concise for voice output, but comprehensive when needed
- Show work for math problems - explain steps clearly
- Provide code with brief explanations
- Give practical, actionable advice
- Maintain conversation context from previous messages
- Use reasoning to give thoughtful, nuanced answers
- Be helpful, honest, and accurate

You're like ChatGPT but now in Jarvis, always ready to help with any task."""

    # Build message list with conversation history
    messages = [{"role": "system", "content": system_msg}]
    for item in conversation_history[-HISTORY_MAX:]:
        messages.append(item)
    messages.append({"role": "user", "content": prompt})

    try:
        # Use GPT-4o mini - most powerful + efficient + affordable model
        # Better reasoning, coding, math, and general capabilities
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Upgraded: GPT-4o mini instead of gpt-3.5-turbo
            messages=messages,
            max_tokens=300,  # Increased from 200 - GPT-4o handles longer responses well
            temperature=0.7,  # Balanced creativity and accuracy
            top_p=0.95,  # Better diversity
            timeout=10,  # Slightly longer for more complex reasoning
            request_timeout=10,
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Save to history for context in follow-up questions
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": response_text})
        
        return response_text
    except Exception as e:
        error_str = str(e).lower()
        # Provide diagnostic messages
        if "rate limit" in error_str:
            return "Rate limited. Please wait a moment before asking again."
        if "api_key" in error_str or "invalid" in error_str or "unauthorized" in error_str:
            return "API key is invalid. Please check your OpenAI key in config."
        if "timeout" in error_str or "connection" in error_str or "refused" in error_str:
            return "Connection failed. Check your internet, firewall, or proxy settings."
        if "proxy" in error_str:
            return "Proxy connection error. Disable corporate proxy or configure it in environment variables."
        if "model" in error_str or "gpt-4o-mini" in error_str:
            return "GPT-4o-mini unavailable. Please ensure your OpenAI account has access to this model."
        return f"AI error: {e}"
