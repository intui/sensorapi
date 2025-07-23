"""
Database connection and session management.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create database engine with serverless-optimized connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=1,  # Single connection for serverless (lambda functions)
    max_overflow=0,  # No overflow in serverless to prevent connection leaks
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=60,  # Recycle connections quickly in serverless (1 minute)
    connect_args={'connect_timeout': 10},  # Quick connection timeout
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session (for FastAPI dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager for database sessions (for manual session management)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
