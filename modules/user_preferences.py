from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserPreferences(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    wake_word_sensitivity = Column(Float, default=0.5)
    notification_type = Column(String(20), default='audio')
    notification_enabled = Column(Boolean, default=True)
    volume_level = Column(Integer, default=50)
    language = Column(String(10), default='en-US')
    created_at = Column(String(50), default=lambda: datetime.now().isoformat())
    updated_at = Column(String(50), default=lambda: datetime.now().isoformat(), 
                       onupdate=lambda: datetime.now().isoformat())

    def __init__(self, user_id, wake_word_sensitivity=0.5, notification_type='audio',
                 notification_enabled=True, volume_level=50, language='en-US'):
        self.user_id = user_id
        self.wake_word_sensitivity = wake_word_sensitivity
        self.notification_type = notification_type
        self.notification_enabled = notification_enabled
        self.volume_level = volume_level
        self.language = language

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'wake_word_sensitivity': self.wake_word_sensitivity,
            'notification_type': self.notification_type,
            'notification_enabled': self.notification_enabled,
            'volume_level': self.volume_level,
            'language': self.language,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def update_preferences(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
