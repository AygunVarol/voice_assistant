import logging
from typing import Dict, Optional
import speech_recognition as sr
from datetime import datetime
from threading import Lock

from ..models.command_history import CommandHistory
from ..models.user_preferences import UserPreferences
from ..utils.db_utils import get_db_session
from ..config.config import Config

class CommandProcessor:
    def __init__(self, notification_manager):
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        self.notification_manager = notification_manager
        self.command_lock = Lock()
        self.command_patterns = {
            'lights': self._handle_lights_command,
            'music': self._handle_music_command,
            'volume': self._handle_volume_command,
            'sensitivity': self._handle_sensitivity_command
        }
        
    def process_command(self, audio_data: bytes) -> bool:
        """Process the audio command and execute appropriate action"""
        with self.command_lock:
            try:
                # Convert audio to text
                audio = sr.AudioData(audio_data, Config.SAMPLE_RATE, Config.SAMPLE_WIDTH)
                text = self.recognizer.recognize_google(audio).lower()
                
                # Log the command
                self._log_command(text)
                
                # Notify processing started
                self.notification_manager.show_processing()
                
                # Find matching command pattern
                for keyword, handler in self.command_patterns.items():
                    if keyword in text:
                        return handler(text)
                        
                self.logger.info(f"No matching command found for: {text}")
                return False
                
            except sr.UnknownValueError:
                self.logger.warning("Could not understand audio")
                return False
            except Exception as e:
                self.logger.error(f"Error processing command: {str(e)}")
                return False
            finally:
                self.notification_manager.hide_processing()

    def _log_command(self, command_text: str) -> None:
        """Log command to database"""
        try:
            session = get_db_session()
            command_history = CommandHistory(
                command=command_text,
                timestamp=datetime.now()
            )
            session.add(command_history)
            session.commit()
        except Exception as e:
            self.logger.error(f"Error logging command: {str(e)}")

    def _get_user_preferences(self) -> Optional[Dict]:
        """Get current user preferences from database"""
        try:
            session = get_db_session()
            prefs = session.query(UserPreferences).first()
            return prefs.to_dict() if prefs else None
        except Exception as e:
            self.logger.error(f"Error getting preferences: {str(e)}")
            return None

    def _handle_lights_command(self, command_text: str) -> bool:
        """Handle light-related commands"""
        try:
            if "on" in command_text:
                # Implementation for turning lights on
                self.logger.info("Turning lights on")
                return True
            elif "off" in command_text:
                # Implementation for turning lights off
                self.logger.info("Turning lights off")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error handling lights command: {str(e)}")
            return False

    def _handle_music_command(self, command_text: str) -> bool:
        """Handle music-related commands"""
        try:
            if "play" in command_text:
                # Implementation for playing music
                self.logger.info("Playing music")
                return True
            elif "stop" in command_text:
                # Implementation for stopping music
                self.logger.info("Stopping music")
                return True
            elif "pause" in command_text:
                # Implementation for pausing music
                self.logger.info("Pausing music")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error handling music command: {str(e)}")
            return False

    def _handle_volume_command(self, command_text: str) -> bool:
        """Handle volume-related commands"""
        try:
            if "up" in command_text:
                # Implementation for volume up
                self.logger.info("Increasing volume")
                return True
            elif "down" in command_text:
                # Implementation for volume down
                self.logger.info("Decreasing volume")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error handling volume command: {str(e)}")
            return False

    def _handle_sensitivity_command(self, command_text: str) -> bool:
        """Handle sensitivity adjustment commands"""
        try:
            session = get_db_session()
            prefs = session.query(UserPreferences).first()
            
            if "increase" in command_text:
                prefs.wake_word_sensitivity += 0.1
                self.logger.info("Increasing sensitivity")
            elif "decrease" in command_text:
                prefs.wake_word_sensitivity -= 0.1
                self.logger.info("Decreasing sensitivity")
            
            session.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error handling sensitivity command: {str(e)}")
            return False
