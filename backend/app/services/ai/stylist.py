import google.generativeai as genai
import os
import logging
from app.core.config import settings
from app.core.prompts import STYLIST_SYSTEM_PROMPT, create_user_prompt

logger = logging.getLogger(__name__)

class StylistService:
    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            logger.warning("GOOGLE_API_KEY is missing. Stylist service will not work.")
        else:
            genai.configure(api_key=api_key)
            # Dùng model Flash cho nhanh và tiết kiệm
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')

    async def get_advice(self, product_metadata: dict, user_question: str) -> str:
        """
        Gọi Gemini API để lấy lời khuyên.
        """
        if not settings.GOOGLE_API_KEY:
             return "Lỗi cấu hình: Thiếu API Key."

        try:
            # 1. Tạo Prompt (Augmentation)
            prompt = create_user_prompt(
                product_name=product_metadata.get("name", "Sản phẩm không tên"),
                product_category=product_metadata.get("category", "Thời trang"),
                user_question=user_question
            )

            # 2. Gọi API (Generation)
            # generate_content_async giúp không bị chặn luồng chính
            response = await self.model.generate_content_async(
                contents=[
                    {"role": "user", "parts": [STYLIST_SYSTEM_PROMPT + "\n" + prompt]}
                ]
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"LLM Error: {str(e)}")
            return "Xin lỗi, hiện tại tư vấn viên AI đang bận. Bạn hãy thử lại sau nhé! 🤖"

stylist_service = StylistService()