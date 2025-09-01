"""
Main application entry point for the Sensor Data GraphQL API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.core.config import settings
from app.graphql.schema import schema
from app.database.database import engine, Base
from app.database import models
from app.api.endpoints.health import router as health_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

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

# Include health and database management endpoints
app.include_router(health_router, prefix="/api/v1", tags=["health", "database"])

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "graphql_endpoint": "/graphql",
        "database_info_endpoint": "/api/v1/database/info",
        "health_endpoint": "/api/v1/health",
        "environment": settings.ENVIRONMENT,
        "database_provider": settings.DATABASE_PROVIDER,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
