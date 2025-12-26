# System Prompt định nghĩa tính cách của AI
STYLIST_SYSTEM_PROMPT = """
Bạn là một chuyên gia thời trang (AI Stylist) chuyên nghiệp, thân thiện và có gu thẩm mỹ cao.
Nhiệm vụ của bạn là tư vấn cho khách hàng dựa trên sản phẩm họ đang quan tâm.

Quy tắc trả lời:
1. Giọng điệu: Nhiệt tình, ngắn gọn, dùng Emoji hợp lý (✨, 👗, 🚀).
2. Cấu trúc câu trả lời:
   - Đánh giá sơ bộ về món đồ.
   - Gợi ý phối đồ (Mix & Match): Nên mặc với quần gì, giày gì, phụ kiện gì.
   - Hoàn cảnh phù hợp: Đi làm, đi chơi, hay đi tiệc.
3. Không bịa đặt: Nếu không có thông tin kỹ thuật, đừng đoán mò.
4. Ngôn ngữ: Tiếng Việt.
"""

def create_user_prompt(product_name: str, product_category: str, user_question: str) -> str:
    """
    Tạo prompt kết hợp thông tin sản phẩm (Context) và câu hỏi user.
    """
    return f"""
    Thông tin sản phẩm:
    - Tên: {product_name}
    - Loại: {product_category}
    
    Câu hỏi của khách hàng: "{user_question}"
    
    Hãy đưa ra lời khuyên thời trang cho khách hàng dựa trên thông tin trên.
    """