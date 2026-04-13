from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    # NOTE: these are required in production, but we keep safe defaults so
    # unit tests and CI can import the app without secrets.
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Vector DB
    # Uses PGVector under the hood seamlessly
    
    # Email
    RESEND_API_KEY: Optional[str] = None
    
    # LinkedIn
    LINKEDIN_EMAIL: Optional[str] = None
    LINKEDIN_PASSWORD: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"

    # Web / API
    # Comma-separated list of allowed origins for CORS in production.
    # Example: "https://app.example.com,https://admin.example.com"
    ALLOWED_ORIGINS: str = ""

    # Admin
    # Comma-separated list of admin emails.
    ADMIN_EMAILS: str = ""
    
    # Rate Limits
    LINKEDIN_CONNECTION_DAILY_LIMIT: int = 15
    LINKEDIN_PROFILE_VIEW_DAILY_LIMIT: int = 80
    EMAIL_DAILY_LIMIT: int = 50
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    SENTRY_RELEASE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
