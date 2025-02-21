from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import os
from pathlib import Path

# Get the absolute path to the data directory
data_dir = Path(__file__).parent.parent / 'data'
db_path = data_dir / 'config.db'

# Create data directory if it doesn't exist
data_dir.mkdir(parents=True, exist_ok=True)

# Database URL
DATABASE_URL = f'sqlite:///{db_path}'

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args={'check_same_thread': False}
)

# Create session factory
session_factory = sessionmaker(bind=engine)

# Create thread-safe session registry
Session = scoped_session(session_factory)

def get_session():
    """Get a new database session"""
    return Session()

def init_db():
    """Initialize the database, creating tables"""
    from modules.models import Base
    Base.metadata.create_all(engine)

def close_db():
    """Close all sessions and dispose engine"""
    Session.remove()
    engine.dispose()
