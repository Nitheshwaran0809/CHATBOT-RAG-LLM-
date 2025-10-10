from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # API Configuration
    APP_NAME: str = "ChatGPT Clone with RAG Code Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Groq API
    GROQ_API_KEY: str
    GROQ_CHAT_MODEL: str = "llama-3.1-8b-instant"
    GROQ_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: str = "groq"  # or "local"
    LOCAL_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = "/data/chroma"
    CHROMA_COLLECTION_NAME: str = "code_assistant_collection"
    
    # RAG Configuration
    RETRIEVAL_TOP_K: int = 8
    CHUNK_SIZE_TOKENS: int = 500
    CHUNK_OVERLAP_TOKENS: int = 50
    MAX_CONVERSATION_HISTORY: int = 10
    
    # Manual Data Configuration
    DATA_DIR: str = "/app/data"
    SUPPORTED_ENCODINGS: List[str] = ["utf-8", "latin-1", "cp1252"]
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # Allow all origins for ChromaDB viewer
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
