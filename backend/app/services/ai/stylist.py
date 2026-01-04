import google.generativeai as genai
from app.core.config import settings

class GeminiStylist:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.is_active = True
        except Exception as e:
            print(f"⚠️ Không thể khởi tạo Gemini: {e}")
            self.is_active = False

    def get_outfit_advice(self, product_name: str, product_desc: str) -> str:
        """
        Xin lời khuyên phối đồ từ Gemini.
        """
        if not self.is_active:
            return "Chức năng tư vấn đang bảo trì."

        prompt = f"""
        Bạn là một Fashion Stylist chuyên nghiệp và thân thiện.
        Tôi vừa tìm thấy một sản phẩm thời trang này:
        - Tên: {product_name}
        - Mô tả: {product_desc}
        
        Hãy cho tôi 3 gợi ý phối đồ (Outfit ideas) thật sành điệu với món đồ này để đi chơi hoặc đi làm.
        Trả lời ngắn gọn, dùng gạch đầu dòng và thêm emoji cho sinh động.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Lỗi khi gọi Gemini: {e}")
            return "Xin lỗi, stylist đang bận suy nghĩ, bạn thử lại sau nhé!"

# Singleton Instance
stylist_ai = GeminiStylist()