"""
Loading Screen with Live Wallpaper and Audio
Displays a splash screen with animated WebM video and embedded audio
"""

import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui, QtMultimedia, QtMultimediaWidgets
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    print("[WARNING] QWebEngineView not available - fallback will show text")


class LoadingScreen(QMainWindow):
    """
    Loading screen with live wallpaper background and looping audio
    Shows until user clicks 'Run' button
    """
    
    def __init__(self, video_path=None):
        super().__init__()
        
        # Get base directory for relative paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set default path if not provided
        if video_path is None:
            video_path = os.path.join(self.base_dir, '../../Jarvis/utils/videos', '50504.webm')
        
        self.video_path = video_path
        
        # Initialize UI
        self.init_ui()
        
        # Setup video player
        self.setup_video()
        
        # Track if user clicked run
        self.run_clicked = False
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("JARVIS - Loading")
        self.setGeometry(100, 100, 1440, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # Create video widget for WebM playback
        self.video_widget = QtMultimediaWidgets.QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #1a1a1a;")
        
        # Create fallback label (shown if video can't play and web engine not available)
        from PyQt5.QtWidgets import QLabel
        self.fallback_label = QLabel()
        self.fallback_label.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ffffff;
            font: 18pt 'Arial';
            text-align: center;
        """)
        self.fallback_label.setText("Loading Screen\n(Video file unavailable)\n\nClick Run to continue")
        self.fallback_label.setAlignment(Qt.AlignCenter)
        self.fallback_label.hide()

        # Create web view for fallback video playback
        if WEB_ENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setStyleSheet("background-color: #1a1a1a;")
            self.web_view.hide()
        else:
            self.web_view = None
        
        # Create container for buttons with transparent background
        button_container = QWidget()
        button_container.setStyleSheet("background-color: transparent;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 0, 30, 30)
        button_layout.addStretch()
        
        # Run button
        self.run_button = QPushButton("▶ RUN")
        self.run_button.setFixedSize(150, 60)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #00aaff;
                color: white;
                font: 75 18pt 'MS Shell Dlg 2';
                font-weight: bold;
                border-radius: 10px;
                border: 2px solid #0088cc;
            }
            QPushButton:hover {
                background-color: #0088cc;
                border: 2px solid #00aaff;
            }
            QPushButton:pressed {
                background-color: #006699;
            }
        """)
        self.run_button.clicked.connect(self.on_run_clicked)
        
        # Exit button
        self.exit_button = QPushButton("✕ EXIT")
        self.exit_button.setFixedSize(150, 60)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: white;
                font: 75 18pt 'MS Shell Dlg 2';
                font-weight: bold;
                border-radius: 10px;
                border: 2px solid #cc0000;
            }
            QPushButton:hover {
                background-color: #cc0000;
                border: 2px solid #ff0000;
            }
            QPushButton:pressed {
                background-color: #990000;
            }
        """)
        self.exit_button.clicked.connect(self.on_exit_clicked)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.exit_button)
        button_container.setLayout(button_layout)
        
        # Create main container with video, fallback, and buttons
        main_container = QWidget()
        main_container.setStyleSheet("background-color: transparent;")
        main_layout_inner = QVBoxLayout()
        main_layout_inner.setContentsMargins(0, 0, 0, 0)
        main_layout_inner.addWidget(self.video_widget, 1)
        main_layout_inner.addWidget(self.fallback_label, 1)
        if self.web_view:
            main_layout_inner.addWidget(self.web_view, 1)
        main_layout_inner.addWidget(button_container)
        main_container.setLayout(main_layout_inner)
        
        main_layout.addWidget(main_container)
        
        # Set window properties
        self.setWindowIcon(QIcon("Jarvis/utils/images/jarvis_icon.png"))
    
    def setup_video(self):
        """Setup video player for WebM with embedded audio"""
        # Create media player
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setNotifyInterval(100)
        
        print(f"\n[VIDEO PATH] {self.video_path}")
        print(f"[FILE EXISTS] {os.path.exists(self.video_path)}")
        
        # Check if video file exists
        if os.path.exists(self.video_path):
            # Convert path to absolute for safety
            abs_path = os.path.abspath(self.video_path)
            print(f"[ABSOLUTE PATH] {abs_path}")
            
            # Set media content
            media_url = QUrl.fromLocalFile(abs_path)
            print(f"[MEDIA URL] {media_url.toString()}")
            
            media_content = QMediaContent(media_url)
            self.media_player.setMedia(media_content)
            
            # Connect to end of media signal to loop
            self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
            
            # Connect to error signal
            self.media_player.error.connect(self.on_media_error)
            
            # Set volume to 50%
            self.media_player.setVolume(50)
            
            # Start playing
            self.media_player.play()
            print(f"[SUCCESS] Video loaded and playing: {self.video_path}")
        else:
            print(f"[ERROR] Video file not found at {self.video_path}")
            self.show_fallback()
    
    def on_media_error(self):
        """Handle media player errors"""
        error_code = self.media_player.error()
        error_string = self.media_player.errorString()
        print(f"[MEDIA ERROR] Code: {error_code}, Message: {error_string}")
        self.show_fallback()
    
    def on_media_status_changed(self, status):
        """Handle media status changes to loop video"""
        status_names = {
            QtMultimedia.QMediaPlayer.UnknownMediaStatus: "UnknownMediaStatus",
            QtMultimedia.QMediaPlayer.NoMedia: "NoMedia",
            QtMultimedia.QMediaPlayer.LoadingMedia: "LoadingMedia",
            QtMultimedia.QMediaPlayer.LoadedMedia: "LoadedMedia",
            QtMultimedia.QMediaPlayer.StalledMedia: "StalledMedia",
            QtMultimedia.QMediaPlayer.BufferingMedia: "BufferingMedia",
            QtMultimedia.QMediaPlayer.BufferedMedia: "BufferedMedia",
            QtMultimedia.QMediaPlayer.EndOfMedia: "EndOfMedia",
            QtMultimedia.QMediaPlayer.InvalidMedia: "InvalidMedia",
        }
        
        status_name = status_names.get(status, f"Unknown({status})")
        print(f"[MEDIA STATUS] {status_name}")
        
        # If video codec not supported, show fallback
        if status == QtMultimedia.QMediaPlayer.InvalidMedia:
            print(f"[FALLBACK] Unsupported video codec detected. Showing fallback screen.")
            self.show_fallback()
            return
        
        # Check for errors
        if self.media_player.error() != QtMultimedia.QMediaPlayer.NoError:
            print(f"[MEDIA ERROR] {self.media_player.errorString()}")
        
        # When media ends, restart it
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            print("[LOOP] Restarting video...")
            self.media_player.setPosition(0)
            self.media_player.play()
    
    def show_fallback(self):
        """Show fallback screen when video can't be played"""
        self.video_widget.hide()
        if self.web_view and WEB_ENGINE_AVAILABLE:
            # Try to play video using web engine
            self.fallback_label.hide()
            self.web_view.show()
            # Create HTML to play the video
            video_url = QUrl.fromLocalFile(self.video_path).toString()
            html = f"""
            <html>
            <body style="margin: 0; padding: 0; background-color: #1a1a1a;">
                <video autoplay loop muted style="width: 100%; height: 100%; object-fit: cover;">
                    <source src="{video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </body>
            </html>
            """
            self.web_view.setHtml(html)
            print("[UI] Showing fallback screen with web video playback")
        else:
            # Show text fallback
            self.fallback_label.show()
            print("[UI] Showing fallback screen with text")
    
    def on_run_clicked(self):
        """Handle Run button click"""
        self.run_clicked = True
        print("[RUN] Run button clicked - Starting JARVIS...")

        # Stop video
        self.media_player.stop()

        # Stop web view if active
        if self.web_view:
            self.web_view.stop()

        # Close loading screen
        self.close()
    
    def on_exit_clicked(self):
        """Handle Exit button click"""
        print("[EXIT] Closing application...")

        # Stop video
        self.media_player.stop()

        # Stop web view if active
        if self.web_view:
            self.web_view.stop()

        # Close application
        sys.exit(0)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop video when window closes
        self.media_player.stop()

        # Stop web view if active
        if self.web_view:
            self.web_view.stop()

        event.accept()


def show_loading_screen(video_path=None):
    """
    Display loading screen with WebM video and wait for user action
    
    Args:
        video_path (str): Path to WebM video file with embedded audio
    
    Returns:
        bool: True if user clicked Run, False if Exit
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    loading_screen = LoadingScreen(video_path)
    loading_screen.show()
    
    # Process events until window is closed
    while loading_screen.isVisible():
        app.processEvents()
    
    return loading_screen.run_clicked


if __name__ == "__main__":
    # Test the loading screen
    app = QtWidgets.QApplication(sys.argv)
    
    # Path to WebM video with embedded audio
    video = "Jarvis/utils/videos/50504.webm"
    
    loading = LoadingScreen(video)
    loading.show()
    
    sys.exit(app.exec_())
