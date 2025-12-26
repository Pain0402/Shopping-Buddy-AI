import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Shopping Buddy"
    API_V1_STR: str = "/api/v1"
    
    # AI Configuration
    CLIP_MODEL_NAME: str = "clip-ViT-B-32" 
    YOLO_MODEL_PATH: str = "yolov8n.pt"
    
    # Vector DB
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "product_embeddings"

    # LLM Configuration (Phase 3)
    # Tự động đọc từ file .env hoặc biến môi trường
    GOOGLE_API_KEY: str = "" 

    class Config:
        env_file = ".env"

settings = Settings()