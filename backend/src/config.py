"""
Configuration module for MCP Registry Backend.

Loads and validates environment variables using pydantic-settings.
"""

import os
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL connection string",
        validation_alias="DATABASE_URL"
    )
    
    # Azure Entra ID Configuration
    azure_client_id: str = Field(
        ...,
        description="Azure Entra ID application client ID",
        validation_alias="AZURE_CLIENT_ID"
    )
    
    azure_tenant_id: str = Field(
        ...,
        description="Azure Entra ID tenant ID",
        validation_alias="AZURE_TENANT_ID"
    )
    
    entra_admin_group_id: str = Field(
        ...,
        description="Azure Entra ID admin group ID",
        validation_alias="ENTRA_ADMIN_GROUP_ID"
    )
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Allowed CORS origins (comma-separated)",
        validation_alias="CORS_ORIGINS"
    )
    
    # Application Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        validation_alias="LOG_LEVEL"
    )
    
    environment: str = Field(
        default="development",
        description="Environment name (development, staging, production)",
        validation_alias="ENVIRONMENT"
    )
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            # Return the string as-is, we'll parse it in a property
            return v
        if isinstance(v, list):
            return ",".join(v)
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is a recognized Python logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def entra_authority(self) -> str:
        """Get the Entra ID authority URL for token validation."""
        return f"https://login.microsoftonline.com/{self.azure_tenant_id}/v2.0"
    
    @property
    def jwks_uri(self) -> str:
        """Get the JWKS URI for token signature verification."""
        return f"https://login.microsoftonline.com/{self.azure_tenant_id}/discovery/v2.0/keys"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings instance.
    
    This function can be used as a FastAPI dependency if needed.
    
    Returns:
        Settings: Application settings
    """
    return settings
