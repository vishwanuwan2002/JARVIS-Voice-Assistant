#!/usr/bin/env python3
"""
Setup script to configure environment variables for Jarvis.
Run this to easily set up your OpenAI API key and other settings.
"""

import os
import sys
from pathlib import Path

print("="*70)
print("JARVIS SETUP - CONFIGURE ENVIRONMENT VARIABLES")
print("="*70)

# Get the .env file path
env_file = Path(__file__).parent / ".env"

print("\n1. Setting up OpenAI API Key")
print("-" * 70)
print("You need an OpenAI API key to use Jarvis AI.")
print("Get one at: https://platform.openai.com/api-keys")
print()

api_key = input("Enter your OpenAI API key (sk-...): ").strip()

if not api_key.startswith("sk-"):
    print("✗ Invalid API key format (should start with sk-)")
    sys.exit(1)

# Create .env file
print("\n2. Creating .env file")
print("-" * 70)

env_content = f"""# JARVIS Environment Variables
# Created by setup script on {os.getcwd()}
#
# SECURITY: This file contains sensitive credentials.
# NEVER commit this file to git!
# Make sure .gitignore includes .env

OPENAI_API_KEY={api_key}
"""

try:
    with open(env_file, 'w') as f:
        f.write(env_content)
    print(f"✓ Created .env file: {env_file}")
except Exception as e:
    print(f"✗ Error creating .env file: {e}")
    sys.exit(1)

# Verify .gitignore
print("\n3. Checking .gitignore")
print("-" * 70)

gitignore_file = Path(__file__).parent / ".gitignore"
if gitignore_file.exists():
    with open(gitignore_file) as f:
        gitignore_content = f.read()
    if ".env" in gitignore_content:
        print("✓ .env is already in .gitignore (protected)")
    else:
        print("⚠ .env is NOT in .gitignore!")
        print("  Adding .env to .gitignore...")
        with open(gitignore_file, 'a') as f:
            f.write("\n# Environment variables\n.env\n.env.local\n")
        print("  ✓ Added .env to .gitignore")
else:
    print("⚠ .gitignore not found")

# Load and verify
print("\n4. Verifying setup")
print("-" * 70)

try:
    from dotenv import load_dotenv
    load_dotenv(env_file)
    loaded_key = os.getenv('OPENAI_API_KEY')
    if loaded_key == api_key:
        print("✓ Environment variable loaded successfully")
    else:
        print("✗ Environment variable mismatch")
        sys.exit(1)
except ImportError:
    print("⚠ python-dotenv not installed (but that's OK)")
    print("  Jarvis will still work - it will use the .env file when needed")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test
print("\n5. Quick API test")
print("-" * 70)

test_input = input("Test OpenAI API? (y/n): ").strip().lower()
if test_input == 'y':
    print("Testing AI...")
    try:
        from Jarvis import JarvisAssistant
        obj = JarvisAssistant()
        response = obj.ask_ai("What is 1 + 1?")
        if response and not response.startswith("AI error") and not response.startswith("No OpenAI"):
            print(f"✓ AI works! Response: {response[:100]}")
        else:
            print(f"⚠ AI response: {response}")
    except Exception as e:
        print(f"✗ Test failed: {e}")

# Summary
print("\n" + "="*70)
print("✅ SETUP COMPLETE")
print("="*70)
print(f"""
Your .env file is ready at: {env_file}

NEXT STEPS:

1. Start Jarvis:
   python main.py

2. If behind corporate proxy, also set:
   $env:HTTPS_PROXY=$null
   $env:HTTP_PROXY=$null

3. Test Jarvis:
   python test_ai.py

4. Before committing to git, verify:
   - .env is in .gitignore
   - .env file is NOT staged for commit
   Run: git status (should not show .env)

SECURITY REMINDERS:
- .env contains your API key - NEVER share or commit it
- If you accidentally commit .env, regenerate your API key at openai.com
- Use git secrets or pre-commit hooks to prevent accidental commits

ENJOY YOUR AI ASSISTANT! 🚀
""")
print("="*70)
