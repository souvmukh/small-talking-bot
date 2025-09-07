from pydantic import DirectoryPath, FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """Defines all application settings and validates them using pydantic"""
    # By using Pydantic's types, it automatically checks if these paths are valid directories.
    VOSK_MODEL_DIR: DirectoryPath = "./models"
    VOSK_MODEL_NAME: DirectoryPath = "vosk-model-small-en-us-0.15"
    VOSK_MODEL_PATH: DirectoryPath = os.path.join(VOSK_MODEL_DIR, VOSK_MODEL_NAME)
    
    DOCUMENTS_PATH: DirectoryPath = "./documents"

    OLLAMA_MODEL: str = "phi3"
    
    # RAG settings
    TEXT_CHUNK_SIZE: int = 500
    TEXT_CHUNK_OVERLAP: int = 50

    # Logging settings
    LOG_FILE: str = "chatbot.log"
    LOG_LEVEL: str = "INFO"

    # Database setting for caching
    DATABASE_PATH: str = "chatbot_cache.db"

    # This allows Pydantic to read from a .env file if you want, but we'll use defaults.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a single, validated settings object to be imported by other modules.
settings = Settings()
