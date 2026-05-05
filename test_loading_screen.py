#!/usr/bin/env python
"""Test loading screen video playback"""

import sys
import os

# Add Jarvis to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from Jarvis.features.loading_screen import LoadingScreen

if __name__ == "__main__":
    print("\n" + "="*70)
    print("LOADING SCREEN TEST - Video Playback Debug")
    print("="*70 + "\n")
    
    app = QApplication(sys.argv)
    
    # Path to video
    video_path = os.path.join(os.path.dirname(__file__), 'Jarvis', 'utils', 'videos', '50504.webm')
    
    print(f"[TEST] Video path: {video_path}")
    print(f"[TEST] File exists: {os.path.exists(video_path)}\n")
    
    # Create loading screen
    print("[TEST] Creating LoadingScreen...\n")
    loading_screen = LoadingScreen(video_path)
    loading_screen.show()
    
    print(f"\n[TEST] Loading screen displayed. Close it to exit.")
    print("[TEST] Watching for media status changes...\n")
    
    # Run event loop
    sys.exit(app.exec_())
