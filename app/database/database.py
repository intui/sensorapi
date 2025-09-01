"""
Database connection and session management.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create database engine with NullPool for serverless (no connection pooling)
# Set connect_args based on database type (PostgreSQL vs SQLite)
connect_args = {}
active_db_url = settings.active_database_url

if "postgresql" in active_db_url:
    connect_args = {
        'connect_timeout': 10,  # Quick connection timeout for PostgreSQL
        'application_name': f'sensorapi-{settings.DATABASE_PROVIDER}'  # Identify our app in DB logs
    }

engine = create_engine(
    active_db_url,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    poolclass=None,  # Use NullPool - create fresh connections for each request
    pool_pre_ping=False,  # Don't ping since we're creating fresh connections
    connect_args=connect_args,
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
