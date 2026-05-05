#!/usr/bin/env python3
"""Quick test to verify Jarvis AI is working."""

from Jarvis import JarvisAssistant

obj = JarvisAssistant()

# Test questions
test_queries = [
    "What is 2 + 2?",
    "Tell me a joke",
    "What is Python?",
    "Solve for x: 2x + 5 = 13",
]

print("Testing Jarvis AI responses:")
print("=" * 60)

for query in test_queries:
    print(f"\nQuery: {query}")
    try:
        response = obj.ask_ai(query)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("AI test complete!")
