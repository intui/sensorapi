"""
Main application entry point for the Sensor Data GraphQL API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.core.config import settings
from app.graphql.schema import schema
from app.database.database import engine
from app.database import models

# Note: Database tables should be created via migrations (alembic)
# DO NOT create tables at import time in serverless environments
# This would exhaust database connections and cause deployment failures

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

@app.on_event("shutdown")
async def shutdown_event():
    """Dispose of database connections on shutdown."""
    engine.dispose()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Include GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "graphql_endpoint": "/graphql",
        "environment": settings.ENVIRONMENT,
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity test."""
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "database": "unknown"
    }
    
    # Test database connectivity
    try:
        from sqlalchemy import text
        from app.database.database import SessionLocal
        db = SessionLocal()
        try:
            # Simple query to test connection
            db.execute(text("SELECT 1"))
            health_status["database"] = "connected"
        finally:
            db.close()
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"] = f"error: {str(e)}"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
