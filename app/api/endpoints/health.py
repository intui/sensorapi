"""
Health check and database info endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db
from app.core.config import settings
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@router.get("/database/info")
async def database_info(db: Session = Depends(get_db)):
    """Get information about the current database configuration."""
    try:
        # Get database version
        result = db.execute(text("SELECT version();"))
        db_version = result.fetchone()[0]
        
        # Check for TimescaleDB extension
        timescaledb_version = None
        try:
            result = db.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';"))
            ts_result = result.fetchone()
            if ts_result:
                timescaledb_version = ts_result[0]
        except:
            pass
        
        # Count API tables
        result = db.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'api_%'
        """))
        table_count = result.fetchone()[0]
        
        # Count sensor readings
        reading_count = 0
        try:
            result = db.execute(text("SELECT COUNT(*) FROM api_sensor_readings;"))
            reading_count = result.fetchone()[0]
        except:
            pass
        
        return {
            "database": {
                "provider": settings.DATABASE_PROVIDER,
                "version": db_version,
                "timescaledb_version": timescaledb_version,
                "supports_timescaledb": settings.database_info["supports_timescaledb"],
                "is_tiger_cloud": settings.database_info["is_tiger_cloud"]
            },
            "statistics": {
                "api_tables": table_count,
                "sensor_readings": reading_count
            },
            "configuration": settings.database_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.get("/database/switch-guide")
async def database_switch_guide():
    """Get instructions for switching databases."""
    return {
        "current_provider": settings.DATABASE_PROVIDER,
        "available_providers": ["aiven", "tiger_cloud"],
        "switch_instructions": {
            "description": "Use the database management script to switch between providers",
            "commands": {
                "switch_to_aiven": "python scripts/manage_database.py switch aiven",
                "switch_to_tiger_cloud": "python scripts/manage_database.py switch tiger_cloud",
                "check_status": "python scripts/manage_database.py status",
                "test_connection": "python scripts/manage_database.py test-connection"
            },
            "note": "Restart the application after switching providers"
        },
        "provider_info": {
            "aiven": {
                "description": "Original Aiven PostgreSQL database",
                "timescaledb_support": "Limited (extension available)",
                "data_count": "~422K sensor readings"
            },
            "tiger_cloud": {
                "description": "Tiger Cloud PostgreSQL with TimescaleDB optimizations", 
                "timescaledb_support": "PostgreSQL service tier (no hypertables)",
                "data_count": "~4.5M sensor readings (imported household data)"
            }
        }
    }