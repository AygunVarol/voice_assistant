import threading
import time
import pygame
import logging
from typing import Optional
from pathlib import Path

class NotificationManager:
    def __init__(self):
        self._active = False
        self._notification_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Initialize pygame for audio notifications
        pygame.mixer.init()
        
        # Get sound file paths
        self.sound_dir = Path(__file__).parent.parent / "assets" / "sounds"
        self.activation_sound = str(self.sound_dir / "activation.wav")
        self.processing_sound = str(self.sound_dir / "processing.wav")
        self.completion_sound = str(self.sound_dir / "completion.wav")
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_notification(self, notification_type: str):
        """Start showing a notification of the specified type"""
        if self._active:
            return
            
        self._active = True
        self._stop_event.clear()
        
        if notification_type == "activation":
            self._play_sound(self.activation_sound)
        elif notification_type == "processing":
            self._notification_thread = threading.Thread(
                target=self._show_processing_notification
            )
            self._notification_thread.start()
        elif notification_type == "completion":
            self._play_sound(self.completion_sound)
            
        self.logger.info(f"Started {notification_type} notification")

    def stop_notification(self):
        """Stop showing the current notification"""
        if not self._active:
            return
            
        self._stop_event.set()
        if self._notification_thread:
            self._notification_thread.join()
            self._notification_thread = None
            
        self._active = False
        self.logger.info("Stopped notification")

    def _show_processing_notification(self):
        """Show an ongoing processing notification"""
        while not self._stop_event.is_set():
            self._play_sound(self.processing_sound)
            time.sleep(1.0)

    def _play_sound(self, sound_file: str):
        """Play a notification sound"""
        try:
            sound = pygame.mixer.Sound(sound_file)
            sound.play()
        except Exception as e:
            self.logger.error(f"Error playing notification sound: {e}")

    def is_active(self) -> bool:
        """Check if a notification is currently active"""
        return self._active
