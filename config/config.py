import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "voice_assistant"
    user: str = "admin"
    password: str = "password"  # In production, use environment variables
    
@dataclass 
class AudioConfig:
    chunk_size: int = 1024
    sample_rate: int = 16000
    channels: int = 1
    format: str = "int16"
    
@dataclass
class WakeWordConfig:
    wake_words: list = None
    sensitivity: float = 0.5
    min_confidence: float = 0.7
    
    def __post_init__(self):
        if self.wake_words is None:
            self.wake_words = ["hey assistant", "wake up"]

@dataclass
class NotificationConfig:
    visual_enabled: bool = True
    audio_enabled: bool = True
    notification_sound: str = "notification.wav"

class Config:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
        # Database configuration
        self.db = DatabaseConfig()
        
        # Audio processing settings
        self.audio = AudioConfig()
        
        # Wake word detection settings
        self.wake_word = WakeWordConfig()
        
        # Notification settings
        self.notification = NotificationConfig()
        
        # Paths
        self.paths = {
            'models': self.project_root / 'models',
            'audio': self.project_root / 'audio',
            'logs': self.project_root / 'logs'
        }
        
        # Create directories if they don't exist
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)
            
    def get_db_url(self) -> str:
        """Generate SQLAlchemy database URL"""
        return f"postgresql://{self.db.user}:{self.db.password}@{self.db.host}:{self.db.port}/{self.db.database}"
    
    def update_wake_word_sensitivity(self, sensitivity: float) -> None:
        """Update wake word detection sensitivity"""
        if 0.0 <= sensitivity <= 1.0:
            self.wake_word.sensitivity = sensitivity
        else:
            raise ValueError("Sensitivity must be between 0.0 and 1.0")
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary format"""
        return {
            'database': self.db.__dict__,
            'audio': self.audio.__dict__,
            'wake_word': self.wake_word.__dict__,
            'notification': self.notification.__dict__,
            'paths': {k: str(v) for k, v in self.paths.items()}
        }

# Create global config instance
config = Config()
