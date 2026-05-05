"""LLM wrapper: Prefer Ollama (local LLM), otherwise fall back to OpenAI.

Provides generate(prompt, max_tokens, temperature, use_history, history) -> str

Ollama requires the Ollama server running on localhost:11434 with deepseek-r1 model.
OpenAI requires OPENAI_API_KEY environment variable.
"""

import os
import traceback
import requests
from typing import List, Optional

_OPENAI_AVAILABLE = False
_OLLAMA_AVAILABLE = False

try:
    import openai
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

# Check if Ollama server is accessible
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        _OLLAMA_AVAILABLE = True
        print("LLM: Ollama server detected and available")
    else:
        print(f"LLM: Ollama server responded with status {response.status_code}")
        _OLLAMA_AVAILABLE = False
except Exception as e:
    print(f"LLM: Ollama server not accessible: {e}")
    _OLLAMA_AVAILABLE = False


def _call_openai(messages: List[dict], max_tokens: int = 400, temperature: float = 0.7) -> Optional[str]:
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return None
        openai.api_key = api_key
        
        # Disable proxy to bypass proxy connection errors
        import urllib3
        urllib3.disable_warnings()
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''
        
        response = openai.ChatCompletion.create(
            model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM OpenAI error: {e}")
        traceback.print_exc()
        return None


def _call_ollama(prompt: str, max_tokens: int = 400, temperature: float = 0.7) -> Optional[str]:
    try:
        if not _OLLAMA_AVAILABLE:
            print("LLM: Ollama server not available")
            return None

        # Use deepseek-r1:latest as default model
        model = os.environ.get('OLLAMA_MODEL', 'deepseek-r1:latest')

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": min(max_tokens, 300),  # Cap at 300 for faster responses
                "temperature": temperature,
                "top_p": 0.95
            }
        }

        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30  # Faster response time
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('response', '').strip()
        else:
            print(f"LLM Ollama error: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"LLM Ollama error: {e}")
        traceback.print_exc()
        return None


def generate(prompt: str, history: Optional[List[dict]] = None, use_history: bool = True, max_tokens: int = 250, temperature: float = 0.7) -> Optional[str]:
    """Generate text using preferred provider.

    Prefer Ollama (local LLM), otherwise fall back to OpenAI.
    """
    # Build messages for OpenAI if needed
    messages = []
    if use_history and history:
        messages.extend(history)
    # Append user prompt
    messages.append({"role": "user", "content": prompt})

    # Try Ollama first (local LLM)
    if _OLLAMA_AVAILABLE:
        # For Ollama, build a simple concatenated prompt with history
        ollama_prompt = ""
        if use_history and history:
            # Build conversation context
            ollama_prompt = "\n".join([f"{m.get('role', 'user')}: {m.get('content')}" for m in history if m.get('content')])
            ollama_prompt += "\nuser: " + prompt
        else:
            ollama_prompt = prompt

        out = _call_ollama(ollama_prompt, max_tokens=max_tokens, temperature=temperature)
        if out:
            return out

    # Fallback to OpenAI if API key present
    if _OPENAI_AVAILABLE and os.environ.get('OPENAI_API_KEY'):
        out = _call_openai(messages=messages, max_tokens=max_tokens, temperature=temperature)
        if out:
            return out

    # No provider available
    return None
