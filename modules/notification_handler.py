import os
import platform
import threading
import logging
from typing import Optional
import simpleaudio as sa
from PIL import Image, ImageTk
import tkinter as tk
from sqlalchemy.orm import Session
from config.database import get_db_session
from modules.models import NotificationSetting

class NotificationHandler:
    def __init__(self):
        self._setup_logging()
        self._load_settings()
        self._setup_audio()
        self._setup_visual()
        
    def _setup_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    def _load_settings(self):
        with get_db_session() as session:
            settings = session.query(NotificationSetting).first()
            if settings:
                self.audio_enabled = settings.audio_enabled
                self.visual_enabled = settings.visual_enabled
            else:
                self.audio_enabled = True
                self.visual_enabled = True
                
    def _setup_audio(self):
        self.audio_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "data", "notification.wav"
        )
        if not os.path.exists(self.audio_path):
            self.logger.warning("Notification sound file not found")
            
    def _setup_visual(self):
        self.notification_window: Optional[tk.Tk] = None
        if platform.system() == "Windows":
            self.visual_duration = 2000  # ms
        else:
            self.visual_duration = 2000  # ms
            
    def notify_wake_word(self):
        """Notification when wake word is detected"""
        self._play_notification("wake")
        self._show_notification("Wake Word Detected", "Listening for command...")
        
    def notify_command_processing(self):
        """Notification when processing a command"""
        self._play_notification("process")
        self._show_notification("Processing", "Processing your command...")
        
    def notify_command_complete(self):
        """Notification when command execution is complete"""
        self._play_notification("complete") 
        self._show_notification("Complete", "Command executed successfully")
        
    def notify_error(self, error_msg: str):
        """Notification for errors"""
        self._play_notification("error")
        self._show_notification("Error", error_msg)
        
    def _play_notification(self, notification_type: str):
        """Play audio notification if enabled"""
        if not self.audio_enabled:
            return
            
        try:
            wave_obj = sa.WaveObject.from_wave_file(self.audio_path)
            play_obj = wave_obj.play()
            # Non-blocking play
            threading.Thread(
                target=play_obj.wait_done,
                daemon=True
            ).start()
        except Exception as e:
            self.logger.error(f"Error playing notification: {str(e)}")
            
    def _show_notification(self, title: str, message: str):
        """Show visual notification if enabled"""
        if not self.visual_enabled:
            return
            
        def create_notification_window():
            if self.notification_window:
                self.notification_window.destroy()
                
            window = tk.Tk()
            window.title(title)
            window.geometry("300x100+50+50")
            window.attributes('-topmost', True)
            
            if platform.system() == "Windows":
                window.attributes('-alpha', 0.9)
                
            label = tk.Label(
                window,
                text=message,
                wraplength=250,
                justify='center'
            )
            label.pack(expand=True)
            
            window.after(self.visual_duration, window.destroy)
            self.notification_window = window
            window.mainloop()
            
        # Show notification in separate thread
        threading.Thread(
            target=create_notification_window,
            daemon=True
        ).start()
        
    def update_settings(self, audio_enabled: bool, visual_enabled: bool):
        """Update notification settings"""
        self.audio_enabled = audio_enabled
        self.visual_enabled = visual_enabled
        
        with get_db_session() as session:
            settings = session.query(NotificationSetting).first()
            if settings:
                settings.audio_enabled = audio_enabled
                settings.visual_enabled = visual_enabled
            else:
                settings = NotificationSetting(
                    audio_enabled=audio_enabled,
                    visual_enabled=visual_enabled
                )
                session.add(settings)
            session.commit()
