"""
Configuration Module
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./researchhelper.db"
    
    # Application
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True
    environment: str = "development"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Upload
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    upload_dir: str = "./uploads"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()
