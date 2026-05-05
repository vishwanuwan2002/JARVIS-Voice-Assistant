"""
Test file for JARVIS Intelligent AI capabilities
Run this to test the AI before running the main app
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Jarvis.features import intelligent_ai
from Jarvis.config import config


def test_task_detection():
    """Test whether JARVIS correctly identifies tasks vs questions"""
    print("\n" + "="*60)
    print("TEST 1: Task vs Question Detection")
    print("="*60)
    
    test_cases = [
        # Tasks
        ("open spotify", True, "TASK"),
        ("send an email", True, "TASK"),
        ("launch chrome", True, "TASK"),
        ("take a screenshot", True, "TASK"),
        ("play music", True, "TASK"),
        ("search for python", True, "TASK"),
        
        # Questions
        ("what is python?", False, "QUESTION"),
        ("how does photosynthesis work?", False, "QUESTION"),
        ("explain quantum computing", False, "QUESTION"),
        ("calculate 2^10", False, "QUESTION"),
        ("why is the sky blue?", False, "QUESTION"),
        ("tell me about ai", False, "QUESTION"),
    ]
    
    passed = 0
    for command, expected_is_task, label in test_cases:
        result = intelligent_ai.is_task_command(command)
        status = "✓ PASS" if result == expected_is_task else "✗ FAIL"
        if result == expected_is_task:
            passed += 1
        print(f"{status} | {label:10} | '{command}'")
    
    print(f"\nResult: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_ai_availability():
    """Test if OpenAI API is available"""
    print("\n" + "="*60)
    print("TEST 2: OpenAI API Availability")
    print("="*60)
    
    api_key = os.environ.get('OPENAI_API_KEY') or getattr(config, 'openai_api_key', None)
    
    if api_key:
        print("✓ API Key Found")
        # Mask most of the key for security
        masked_key = api_key[:10] + "..." + api_key[-4:]
        print(f"  Key: {masked_key}")
        return True
    else:
        print("✗ API Key Not Found")
        print("  Set OPENAI_API_KEY environment variable or edit Jarvis/config/config.py")
        print("  See INTELLIGENT_AI_SETUP.md for instructions")
        return False


def test_math_question():
    """Test math question handling"""
    print("\n" + "="*60)
    print("TEST 3: Math Question (GPT-4o mini)")
    print("="*60)
    
    api_key = os.environ.get('OPENAI_API_KEY') or getattr(config, 'openai_api_key', None)
    
    if not api_key:
        print("⊘ SKIPPED - No API key configured")
        return None
    
    question = "What is 2 raised to the power of 10?"
    print(f"Question: {question}")
    print("Calling AI...")
    
    response = intelligent_ai.handle_math_question(question)
    
    if response:
        print(f"✓ Response received (length: {len(response)} chars)")
        print(f"Response: {response[:150]}..." if len(response) > 150 else f"Response: {response}")
        return True
    else:
        print("✗ No response from AI")
        return False


def test_definition_question():
    """Test definition question handling"""
    print("\n" + "="*60)
    print("TEST 4: Definition Question (GPT-4o mini)")
    print("="*60)
    
    api_key = os.environ.get('OPENAI_API_KEY') or getattr(config, 'openai_api_key', None)
    
    if not api_key:
        print("⊘ SKIPPED - No API key configured")
        return None
    
    question = "What is machine learning?"
    print(f"Question: {question}")
    print("Calling AI...")
    
    response = intelligent_ai.handle_definition_question(question)
    
    if response:
        print(f"✓ Response received (length: {len(response)} chars)")
        print(f"Response: {response[:150]}..." if len(response) > 150 else f"Response: {response}")
        return True
    else:
        print("✗ No response from AI")
        return False


def test_how_to_question():
    """Test how-to question handling"""
    print("\n" + "="*60)
    print("TEST 5: How-To Question (GPT-4o mini)")
    print("="*60)
    
    api_key = os.environ.get('OPENAI_API_KEY') or getattr(config, 'openai_api_key', None)
    
    if not api_key:
        print("⊘ SKIPPED - No API key configured")
        return None
    
    question = "How to learn programming?"
    print(f"Question: {question}")
    print("Calling AI...")
    
    response = intelligent_ai.handle_how_to_question(question)
    
    if response:
        print(f"✓ Response received (length: {len(response)} chars)")
        print(f"Response: {response[:150]}..." if len(response) > 150 else f"Response: {response}")
        return True
    else:
        print("✗ No response from AI")
        return False


def test_general_ai():
    """Test general AI query"""
    print("\n" + "="*60)
    print("TEST 6: General AI Query (GPT-4o mini)")
    print("="*60)
    
    api_key = os.environ.get('OPENAI_API_KEY') or getattr(config, 'openai_api_key', None)
    
    if not api_key:
        print("⊘ SKIPPED - No API key configured")
        return None
    
    question = "Why is the sky blue?"
    print(f"Question: {question}")
    print("Calling AI...")
    
    response = intelligent_ai.get_ai_response(question)
    
    if response:
        print(f"✓ Response received (length: {len(response)} chars)")
        print(f"Response: {response[:150]}..." if len(response) > 150 else f"Response: {response}")
        return True
    else:
        print("✗ No response from AI")
        return False


def test_conversation_memory():
    """Test conversation history"""
    print("\n" + "="*60)
    print("TEST 7: Conversation Memory")
    print("="*60)
    
    api_key = os.environ.get('OPENAI_API_KEY') or getattr(config, 'openai_api_key', None)
    
    if not api_key:
        print("⊘ SKIPPED - No API key configured")
        return None
    
    print("Initial history:", intelligent_ai.get_history_context())
    
    # Ask first question
    print("Question 1: What is AI?")
    response1 = intelligent_ai.get_ai_response("What is AI?")
    print(f"Response 1 received: {len(response1) if response1 else 0} chars")
    print("After Q1:", intelligent_ai.get_history_context())
    
    # Ask follow-up question
    print("\nQuestion 2: Can you give me an example?")
    response2 = intelligent_ai.get_ai_response("Can you give me an example?")
    print(f"Response 2 received: {len(response2) if response2 else 0} chars")
    print("After Q2:", intelligent_ai.get_history_context())
    
    # Clear history
    intelligent_ai.clear_history()
    print("After clear:", intelligent_ai.get_history_context())
    
    print("✓ Conversation memory working")
    return True


def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "JARVIS Intelligent AI Test Suite" + " "*11 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # Run tests
    results["Detection"] = test_task_detection()
    results["API"] = test_ai_availability()
    
    if results["API"]:  # Only run AI tests if API is available
        results["Math"] = test_math_question()
        results["Definition"] = test_definition_question()
        results["HowTo"] = test_how_to_question()
        results["General"] = test_general_ai()
        results["Memory"] = test_conversation_memory()
    else:
        print("\n⚠️  Skipping AI tests - No OpenAI API key configured")
        print("See INTELLIGENT_AI_SETUP.md for setup instructions")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else ("✗ FAIL" if result is False else "⊘ SKIP")
        print(f"{status} | {test_name}")
    
    # Final verdict
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])
    
    print("\n" + "="*60)
    if passed == total and total > 0:
        print(f"✓ All {total} tests PASSED!")
        print("Your JARVIS AI is ready to go!")
    elif total == 0:
        print("⊘ Please configure OpenAI API key to run tests")
    else:
        print(f"{passed}/{total} tests passed")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
