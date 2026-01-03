from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
import io

class AIEngine:
    _instance = None

    def __new__(cls):
        # Singleton Pattern: Chỉ tạo instance nếu chưa có
        if cls._instance is None:
            cls._instance = super(AIEngine, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        print("🚀 Đang tải CLIP Model... (Việc này sẽ tốn chút thời gian lần đầu)")
        # Sử dụng model patch32 (nhẹ hơn, nhanh hơn, độ chính xác ổn)
        model_id = "openai/clip-vit-base-patch32"
        
        self.model = CLIPModel.from_pretrained(model_id)
        self.processor = CLIPProcessor.from_pretrained(model_id)
        print("✅ CLIP Model đã sẵn sàng!")

    def create_embedding(self, image_bytes: bytes):
        """
        Input: Ảnh dạng bytes
        Output: Vector 512 chiều (List[float])
        """
        # 1. Chuyển bytes thành PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # 2. Tiền xử lý (Resize, Normalize theo chuẩn OpenAI)
        inputs = self.processor(images=image, return_tensors="pt")
        
        # 3. Chạy Inference (Không tính gradient để tiết kiệm RAM)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        
        # 4. Chuẩn hóa vector (Normalization) để dùng Cosine Similarity
        image_features /= image_features.norm(dim=-1, keepdim=True)
        
        # 5. Chuyển Tensor thành List Python thường
        return image_features.squeeze().tolist()

# Tạo biến toàn cục để các file khác import dùng luôn
ai_engine = AIEngine()