"""
Test JarvisAssistant.open_app_or_website with fuzzy matching
"""

from Jarvis import JarvisAssistant

obj = JarvisAssistant()

print("="*80)
print("Testing JarvisAssistant.open_app_or_website with fuzzy-matched names")
print("="*80)

test_cases = [
    'vs code',           # should map to vscode
    'visual studio code',# should map to vscode  
    'telegram desktop',  # should map to telegram
    'notepad',          # direct match
    'youtube',          # browser fallback
    'explorer',         # should map to file explorer
]

for app_name in test_cases:
    print(f"\nTesting: '{app_name}'")
    success, action, details = obj.open_app_or_website(app_name)
    print(f"  Success: {success}")
    print(f"  Action: {action}")
    print(f"  Details: {details}")

print("\n" + "="*80)
print("Test completed!")
print("="*80)
