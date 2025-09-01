"""
Core application configuration and settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional, Literal
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    APP_NAME: str = "SensorAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API Configuration
    API_PREFIX: str = "/api/v1"
    GRAPHQL_ENDPOINT: str = "/graphql"
    
    # Database Configuration
    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None
    TIGER_CLOUD_DATABASE_URL: Optional[str] = None
    
    # Database Selection
    DATABASE_PROVIDER: Literal["aiven", "tiger_cloud"] = "aiven"
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def active_database_url(self) -> str:
        """Get the active database URL based on DATABASE_PROVIDER setting."""
        if self.DATABASE_PROVIDER == "tiger_cloud":
            if not self.TIGER_CLOUD_DATABASE_URL:
                raise ValueError("TIGER_CLOUD_DATABASE_URL not configured but DATABASE_PROVIDER is set to 'tiger_cloud'")
            # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
            url = self.TIGER_CLOUD_DATABASE_URL
            if url.startswith('postgres://'):
                url = url.replace('postgres://', 'postgresql://', 1)
            return url
        else:
            # Default to Aiven database
            return self.DATABASE_URL
    
    @property 
    def database_info(self) -> dict:
        """Get information about the active database configuration."""
        return {
            "provider": self.DATABASE_PROVIDER,
            "url": self.active_database_url,
            "is_tiger_cloud": self.DATABASE_PROVIDER == "tiger_cloud",
            "supports_timescaledb": self.DATABASE_PROVIDER == "tiger_cloud"
        }


# Global settings instance
settings = Settings()
