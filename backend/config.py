import os
from pathlib import Path

class Config:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 5000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # File paths
    BASE_DIR = Path(__file__).parent
    print(BASE_DIR)
    FULL_JOURNAL_TEXT_PATH = BASE_DIR / "data" / "full_journal_text.txt"
    JOURNAL_IMAGES_PATH = BASE_DIR / "data" / "journal_images"
    COGNITIVE_DISTORTIONS_PATH = BASE_DIR / "data" / "cognitive_distortions.json"
    
    # LLM Configuration
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OCR_LLM_MODEL = os.getenv("OCR_LLM_MODEL", "qwen2.5vl:7b")
    # OLLAMA_REASONING = os.getenv("OLLAMA_REASONING", "True")
    
    # Vector Store Configuration
    RETRIEVER_K = int(os.getenv("RETRIEVER_K", 3))
   
    # Text Splitter Configuration 
    TEXT_SPLITTER = os.getenv("TEXT_SPLITTER", "semantic") # "semantic" or "recursive"
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 300))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
    
    # # Embedding Configuration
    # EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") 