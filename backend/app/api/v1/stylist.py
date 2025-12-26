from fastapi import APIRouter, HTTPException
from app.services.ai.stylist import stylist_service
from app.db.vector_store import vector_store
from app.api.v1.schemas import AdviceRequest, AdviceResponse

router = APIRouter()

@router.post("/stylist/advice", response_model=AdviceResponse)
async def get_styling_advice(request: AdviceRequest):
    """
    RAG Endpoint:
    1. Lấy thông tin sản phẩm từ DB (Retrieval)
    2. Gửi context + câu hỏi cho LLM (Generation)
    """
    
    # 1. Retrieval: Lấy thông tin từ DB
    product_metadata = vector_store.get_item(request.product_id)

    if not product_metadata:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2. Generation: Gọi AI Stylist
    advice = await stylist_service.get_advice(
        product_metadata=product_metadata,
        user_question=request.user_question
    )

    return AdviceResponse(
        product_id=request.product_id,
        advice=advice
    )