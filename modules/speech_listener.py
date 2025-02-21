import pyaudio
import wave
import numpy as np
import pvporcupine
from threading import Thread, Event
import logging
from sqlalchemy.orm import Session
from typing import Optional, Callable
import os

from config.database import SessionLocal
from modules.models import SensitivitySettings
from modules.sensitivity_manager import SensitivityManager
from modules.notification_handler import NotificationHandler

class SpeechListener:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stop_event = Event()
        self.notification_handler = NotificationHandler()
        self.sensitivity_manager = SensitivityManager()
        
        # Audio settings
        self.chunk_size = 1024
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 16000
        
        # Initialize Porcupine wake word detector
        access_key = os.getenv("PORCUPINE_ACCESS_KEY")
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["hey assistant"]
        )
        
        self.command_callback: Optional[Callable] = None
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def start_listening(self, command_callback: Callable):
        """Start listening for wake words in a separate thread"""
        self.command_callback = command_callback
        self.stop_event.clear()
        Thread(target=self._listen_loop).start()
        self.logger.info("Speech listener started")

    def stop_listening(self):
        """Stop the listening loop"""
        self.stop_event.set()
        self.logger.info("Speech listener stopped")

    def _get_sensitivity(self) -> float:
        """Get current sensitivity setting from database"""
        with SessionLocal() as session:
            settings = session.query(SensitivitySettings).first()
            return settings.wake_word_sensitivity if settings else 0.5

    def _listen_loop(self):
        """Main listening loop"""
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        try:
            while not self.stop_event.is_set():
                # Read audio chunk
                audio_chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                pcm = np.frombuffer(audio_chunk, dtype=np.float32)
                
                # Get current sensitivity
                sensitivity = self._get_sensitivity()
                
                # Check for wake word
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    self.logger.info("Wake word detected")
                    self.notification_handler.notify_wake_word()
                    
                    # Record command audio
                    command_audio = self._record_command(stream)
                    
                    if self.command_callback:
                        self.command_callback(command_audio)

        except Exception as e:
            self.logger.error(f"Error in listening loop: {str(e)}")
        finally:
            stream.stop_stream()
            stream.close()

    def _record_command(self, stream) -> bytes:
        """Record audio after wake word detection"""
        frames = []
        # Record for 3 seconds
        for _ in range(0, int(self.rate / self.chunk_size * 3)):
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            frames.append(data)
        
        return b''.join(frames)

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'porcupine'):
            self.porcupine.delete()
        if hasattr(self, 'audio'):
            self.audio.terminate()
