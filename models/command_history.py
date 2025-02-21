from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CommandHistory(Base):
    __tablename__ = 'command_history'

    id = Column(Integer, primary_key=True)
    command = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    wake_word = Column(String(50))
    success = Column(Integer, default=1)  # 1 = success, 0 = failure
    sensitivity_level = Column(Integer)
    execution_time_ms = Column(Integer)
    error_message = Column(String(255))

    def __init__(self, command, wake_word=None, success=1, sensitivity_level=None, 
                 execution_time_ms=None, error_message=None):
        self.command = command
        self.wake_word = wake_word
        self.success = success
        self.sensitivity_level = sensitivity_level
        self.execution_time_ms = execution_time_ms
        self.error_message = error_message

    def to_dict(self):
        return {
            'id': self.id,
            'command': self.command,
            'timestamp': self.timestamp.isoformat(),
            'wake_word': self.wake_word,
            'success': bool(self.success),
            'sensitivity_level': self.sensitivity_level,
            'execution_time_ms': self.execution_time_ms,
            'error_message': self.error_message
        }

    @classmethod
    def get_recent_commands(cls, session, limit=10):
        return session.query(cls).order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_failed_commands(cls, session, limit=10):
        return session.query(cls).filter(cls.success == 0)\
                               .order_by(cls.timestamp.desc())\
                               .limit(limit).all()

    @classmethod
    def get_stats(cls, session):
        total = session.query(cls).count()
        successful = session.query(cls).filter(cls.success == 1).count()
        failed = session.query(cls).filter(cls.success == 0).count()
        
        return {
            'total_commands': total,
            'successful_commands': successful,
            'failed_commands': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
