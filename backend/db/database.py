from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Database configuration
engine: Optional[object] = None
SessionLocal: Optional[object] = None
Base = declarative_base()

def get_database_engine():
    """Get or create database engine with optimized connection pooling"""
    global engine
    if engine is None:
        from config import settings
        engine = create_engine(
            settings.postgres_dsn,
            pool_size=20,  # Increased connection pool
            max_overflow=30,  # Additional connections when needed
            pool_pre_ping=True,  # Validate connections before use
            pool_recycle=3600,  # Recycle connections every hour
            pool_timeout=30,  # Timeout for getting connection from pool
            echo=False,  # Set to True for SQL query logging
            connect_args={
                "options": "-c default_transaction_isolation=read_committed"
            }
        )
        logger.info("Database engine created with connection pooling")
    return engine

def get_session_local():
    """Get or create database session factory"""
    global SessionLocal
    if SessionLocal is None:
        engine = get_database_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Database session factory created")
    return SessionLocal

def get_db():
    """Database dependency for FastAPI"""
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        from .models import Base
        engine = get_database_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")


