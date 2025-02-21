import logging
from typing import Dict, Optional
import speech_recognition as sr
from sqlalchemy.orm import Session
from config.database import SessionLocal
from modules.models import Command, CommandHistory
from modules.notification_handler import NotificationHandler
import datetime

class CommandProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.notification_handler = NotificationHandler()
        self.logger = logging.getLogger(__name__)
        
        # Command patterns/handlers
        self.command_patterns = {
            'lights': self._handle_lights_command,
            'music': self._handle_music_command,
            'volume': self._handle_volume_command,
            'temperature': self._handle_temperature_command
        }

    def process_command(self, audio_data: bytes) -> Optional[Dict]:
        """Process the audio command and execute appropriate action"""
        try:
            # Convert audio to text
            audio = sr.AudioData(audio_data, sample_rate=16000, sample_width=2)
            text = self.recognizer.recognize_google(audio).lower()
            
            # Log command attempt
            self._log_command(text)
            
            # Parse command and execute
            command_type = self._parse_command_type(text)
            if command_type in self.command_patterns:
                self.notification_handler.show_processing()
                result = self.command_patterns[command_type](text)
                self.notification_handler.show_success()
                return result
            else:
                self.notification_handler.show_error("Unrecognized command")
                return None
                
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            self.notification_handler.show_error("Could not understand command")
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing command: {str(e)}")
            self.notification_handler.show_error("Error processing command")
            return None

    def _parse_command_type(self, text: str) -> Optional[str]:
        """Extract the command type from text"""
        for command_type in self.command_patterns.keys():
            if command_type in text:
                return command_type
        return None

    def _log_command(self, command_text: str):
        """Log command to database"""
        try:
            db: Session = SessionLocal()
            command_history = CommandHistory(
                command_text=command_text,
                timestamp=datetime.datetime.now()
            )
            db.add(command_history)
            db.commit()
        except Exception as e:
            self.logger.error(f"Error logging command: {str(e)}")
        finally:
            db.close()

    def _handle_lights_command(self, text: str) -> Dict:
        """Handle light-related commands"""
        action = "on" if "on" in text else "off"
        # Implementation for controlling lights would go here
        return {
            "command_type": "lights",
            "action": action,
            "status": "success"
        }

    def _handle_music_command(self, text: str) -> Dict:
        """Handle music-related commands"""
        action = "play" if "play" in text else "stop"
        # Implementation for controlling music would go here
        return {
            "command_type": "music",
            "action": action,
            "status": "success"
        }

    def _handle_volume_command(self, text: str) -> Dict:
        """Handle volume-related commands"""
        action = "up" if "up" in text else "down"
        # Implementation for controlling volume would go here
        return {
            "command_type": "volume",
            "action": action,
            "status": "success"
        }

    def _handle_temperature_command(self, text: str) -> Dict:
        """Handle temperature-related commands"""
        # Parse temperature value from text
        try:
            temp = next(int(word) for word in text.split() if word.isdigit())
            return {
                "command_type": "temperature",
                "value": temp,
                "status": "success"
            }
        except StopIteration:
            return {
                "command_type": "temperature",
                "status": "error",
                "message": "No temperature value found in command"
            }
