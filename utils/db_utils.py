from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional, Any

from config.config import DatabaseConfig

logger = logging.getLogger(__name__)

class DatabaseUtils:
    _engine = None
    _Session = None

    @classmethod
    def initialize_db(cls) -> None:
        """Initialize database connection engine and session factory"""
        if not cls._engine:
            try:
                cls._engine = create_engine(
                    DatabaseConfig.DATABASE_URL,
                    echo=DatabaseConfig.SQL_ECHO,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )
                cls._Session = sessionmaker(bind=cls._engine)
                logger.info("Database connection initialized successfully")
            except SQLAlchemyError as e:
                logger.error(f"Failed to initialize database: {str(e)}")
                raise

    @classmethod
    def get_session(cls):
        """Get a new database session"""
        if not cls._Session:
            cls.initialize_db()
        return cls._Session()

    @classmethod
    def execute_query(cls, query: str, params: Optional[dict] = None) -> Any:
        """Execute raw SQL query with parameters"""
        if not cls._engine:
            cls.initialize_db()
            
        try:
            with cls._engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return result
        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    @staticmethod
    def handle_transaction(session, operation):
        """Handle database transaction with proper error handling"""
        try:
            result = operation(session)
            session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise
        finally:
            session.close()

    @classmethod
    def cleanup(cls) -> None:
        """Cleanup database connections"""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._Session = None
            logger.info("Database connections cleaned up")

    @staticmethod
    def paginate_query(query, page: int = 1, per_page: int = 10):
        """Add pagination to a query"""
        return query.offset((page - 1) * per_page).limit(per_page)

    @staticmethod
    def add_ordering(query, sort_by: str, order: str = 'asc'):
        """Add ordering to a query"""
        if order.lower() not in ['asc', 'desc']:
            raise ValueError("Order must be either 'asc' or 'desc'")
        
        if hasattr(query.column_descriptions[0]['type'], sort_by):
            order_col = getattr(query.column_descriptions[0]['type'], sort_by)
            return query.order_by(order_col.desc() if order.lower() == 'desc' else order_col.asc())
        raise ValueError(f"Invalid sort column: {sort_by}")
