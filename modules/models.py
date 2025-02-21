from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sensitivity_settings = relationship("SensitivitySetting", back_populates="user")
    command_history = relationship("CommandHistory", back_populates="user")

class SensitivitySetting(Base):
    __tablename__ = 'sensitivity_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    wake_word_threshold = Column(Float, default=0.5)
    noise_tolerance = Column(Float, default=0.3)
    min_command_duration = Column(Integer, default=500)  # in milliseconds
    max_silence_duration = Column(Integer, default=2000)  # in milliseconds
    is_active = Column(Boolean, default=True)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="sensitivity_settings")

class CommandHistory(Base):
    __tablename__ = 'command_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    command_text = Column(String(200), nullable=False)
    execution_time = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    confidence_score = Column(Float)
    
    user = relationship("User", back_populates="command_history")

class WakeWordModel(Base):
    __tablename__ = 'wake_word_models'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(50), unique=True, nullable=False)
    model_path = Column(String(200), nullable=False)
    version = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationPreference(Base):
    __tablename__ = 'notification_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    visual_enabled = Column(Boolean, default=True)
    audio_enabled = Column(Boolean, default=True)
    notification_volume = Column(Float, default=0.7)
    visual_style = Column(String(50), default='default')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
