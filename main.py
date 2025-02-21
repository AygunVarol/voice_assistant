import logging
from pathlib import Path
import sys

from config.database import init_db
from modules.speech_listener import SpeechListener
from modules.command_processor import CommandProcessor
from modules.sensitivity_manager import SensitivityManager 
from modules.notification_handler import NotificationHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VoiceAssistant:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        init_db()
        
        # Initialize components
        self.sensitivity_manager = SensitivityManager()
        self.notification_handler = NotificationHandler()
        self.command_processor = CommandProcessor(self.notification_handler)
        self.speech_listener = SpeechListener(
            sensitivity_manager=self.sensitivity_manager,
            command_processor=self.command_processor,
            notification_handler=self.notification_handler
        )

    def start(self):
        """Start the voice assistant"""
        try:
            self.logger.info("Starting voice assistant...")
            self.notification_handler.notify_startup()
            self.speech_listener.start_listening()
            
        except Exception as e:
            self.logger.error(f"Error starting voice assistant: {str(e)}")
            self.notification_handler.notify_error("Failed to start voice assistant")
            sys.exit(1)

    def stop(self):
        """Stop the voice assistant"""
        try:
            self.logger.info("Stopping voice assistant...")
            self.speech_listener.stop_listening()
            self.notification_handler.notify_shutdown()
            
        except Exception as e:
            self.logger.error(f"Error stopping voice assistant: {str(e)}")
            self.notification_handler.notify_error("Error during shutdown")

def main():
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize and start voice assistant
    assistant = VoiceAssistant()
    
    try:
        assistant.start()
        
        # Keep main thread alive
        while True:
            try:
                input()  # Wait for enter key
            except KeyboardInterrupt:
                break
            
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        
    finally:
        assistant.stop()

if __name__ == "__main__":
    main()
