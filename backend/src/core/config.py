from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Support Ticket Search API"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # For development only
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    
    # Database
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    SQLITE_DATABASE_URL: str = "sqlite:///./data/app.db"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
