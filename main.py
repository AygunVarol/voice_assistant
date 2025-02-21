import logging
import threading
from config.config import Config
from modules.speech_listener import SpeechListener
from modules.command_processor import CommandProcessor
from modules.wake_word_detector import WakeWordDetector
from modules.notification_manager import NotificationManager
from modules.database_manager import DatabaseManager
from utils.db_utils import init_db

class VoiceAssistant:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = Config()
        
        # Initialize database
        self.db = DatabaseManager()
        init_db()
        
        # Initialize core components
        self.notification_manager = NotificationManager()
        self.wake_word_detector = WakeWordDetector(
            sensitivity=self.config.wake_word_sensitivity
        )
        self.command_processor = CommandProcessor(
            notification_manager=self.notification_manager,
            db_manager=self.db
        )
        self.speech_listener = SpeechListener(
            wake_word_detector=self.wake_word_detector,
            command_processor=self.command_processor
        )
        
        # Initialize thread control
        self.is_running = False
        self.listener_thread = None

    def start(self):
        """Start the voice assistant"""
        self.logger.info("Starting voice assistant...")
        self.is_running = True
        
        # Start speech listener in separate thread
        self.listener_thread = threading.Thread(
            target=self.speech_listener.start_listening
        )
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        self.notification_manager.notify_startup()
        self.logger.info("Voice assistant started successfully")

    def stop(self):
        """Stop the voice assistant"""
        self.logger.info("Stopping voice assistant...")
        self.is_running = False
        
        if self.listener_thread:
            self.speech_listener.stop_listening()
            self.listener_thread.join()
            
        self.notification_manager.notify_shutdown()
        self.db.close()
        self.logger.info("Voice assistant stopped successfully")

def main():
    assistant = VoiceAssistant()
    try:
        assistant.start()
        
        # Keep main thread alive
        while assistant.is_running:
            try:
                command = input()
                if command.lower() == "quit":
                    break
            except KeyboardInterrupt:
                break
                
    finally:
        assistant.stop()

if __name__ == "__main__":
    main()
