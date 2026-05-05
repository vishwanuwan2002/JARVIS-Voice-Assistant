"""
Quick test to show what apps are installed on this system
"""

from Jarvis.features.app_finder import find_app_executable, APP_PATHS

print("Testing app detection on your system...\n")

test_apps = ['youtube', 'spotify', 'discord', 'telegram', 'chrome', 'firefox', 
             'edge', 'notepad', 'calculator', 'file explorer', 'vlc', 'paint']

for app in test_apps:
    path = find_app_executable(app)
    if path:
        print(f"✓ {app.upper():20} -> {path}")
    else:
        print(f"✗ {app.upper():20} -> NOT FOUND")

print("\n" + "="*80)
print("You can add more app paths to APP_PATHS in app_finder.py")
print("Run this after installing new apps to update the detection")
