from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - Using SQLite for quick start
    database_url: str = "sqlite:///./serri_flow.db"
    
    # API Keys
    api_key: str = "your-secret-api-key-here"
    calendly_api_token: Optional[str] = None
    huggingface_api_token: Optional[str] = None
    
    # App Settings
    debug: bool = True
    log_level: str = "INFO"
    
    # AI Model Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    qa_model: str = "distilbert-base-uncased-distilled-squad"
    
    class Config:
        env_file = ".env"


settings = Settings()