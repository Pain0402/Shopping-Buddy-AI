from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Cập nhật ProductResponse để có cấu trúc rõ ràng hơn
class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    price: float
    image_url: str
    score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[ProductResponse]

class AdviceRequest(BaseModel):
    product_id: str
    user_question: str

class AdviceResponse(BaseModel):
    product_id: str
    advice: str