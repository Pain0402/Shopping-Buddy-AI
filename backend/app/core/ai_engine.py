from sentence_transformers import SentenceTransformer
from ultralytics import YOLO
from PIL import Image
import threading
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AIEngine:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # Implement Singleton Pattern an toàn với Thread
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AIEngine, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def initialize(self):
        """Load models vào bộ nhớ. Chỉ chạy 1 lần."""
        if self._initialized:
            return
        
        logger.info("Loading AI Models...")
        # Load CLIP Model (dùng cho embedding)
        self.clip_model = SentenceTransformer(settings.CLIP_MODEL_NAME)
        
        # Load YOLO Model (dùng cho object detection - future proofing)
        self.yolo_model = YOLO(settings.YOLO_MODEL_PATH)
        
        self._initialized = True
        logger.info("AI Models loaded successfully.")

    def get_embedding(self, image: Image.Image):
        """Tạo vector embedding từ hình ảnh sử dụng CLIP."""
        if not self._initialized:
            raise RuntimeError("AI Engine not initialized")
        
        # Encode image trả về list vector (float)
        embedding = self.clip_model.encode(image)
        return embedding.tolist()

    def detect_objects(self, image: Image.Image):
        """Phát hiện vật thể (cho các tính năng mở rộng sau này)."""
        if not self._initialized:
            raise RuntimeError("AI Engine not initialized")
        return self.yolo_model(image)

# Global Instance
ai_engine = AIEngine()