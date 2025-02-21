from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import logging
from typing import Generator

from models.user_preferences import UserPreferences
from models.command_history import CommandHistory
from config.config import DatabaseConfig

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.engine = create_engine(
            config.database_url,
            echo=config.echo_queries,
            pool_pre_ping=True
        )
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
    def init_db(self) -> None:
        """Initialize database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    @contextmanager
    def session_scope(self) -> Generator:
        """Provide a transactional scope around a series of operations"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {str(e)}")
            raise
        finally:
            session.close()

    def save_user_preferences(self, sensitivity: float, wake_word: str) -> None:
        """Save user preferences to database"""
        with self.session_scope() as session:
            prefs = UserPreferences(
                sensitivity=sensitivity,
                wake_word=wake_word
            )
            session.add(prefs)

    def get_user_preferences(self) -> UserPreferences:
        """Retrieve latest user preferences"""
        with self.session_scope() as session:
            return session.query(UserPreferences).order_by(
                UserPreferences.created_at.desc()
            ).first()

    def log_command(self, command: str, success: bool) -> None:
        """Log command execution to history"""
        with self.session_scope() as session:
            history = CommandHistory(
                command=command,
                success=success
            )
            session.add(history)

    def get_command_history(self, limit: int = 100) -> list:
        """Retrieve command execution history"""
        with self.session_scope() as session:
            return session.query(CommandHistory).order_by(
                CommandHistory.executed_at.desc()
            ).limit(limit).all()

    def cleanup_old_history(self, days: int = 30) -> None:
        """Remove command history older than specified days"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        with self.session_scope() as session:
            session.query(CommandHistory).filter(
                CommandHistory.executed_at < cutoff
            ).delete()

    def get_success_rate(self) -> float:
        """Calculate command success rate"""
        with self.session_scope() as session:
            total = session.query(CommandHistory).count()
            if total == 0:
                return 0.0
                
            successful = session.query(CommandHistory).filter(
                CommandHistory.success == True
            ).count()
            
            return (successful / total) * 100
