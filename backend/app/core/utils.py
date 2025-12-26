from PIL import Image
import io

def process_image(image_bytes: bytes, max_size: int = 800) -> Image.Image:
    """
    1. Convert bytes -> PIL Image
    2. Resize nếu ảnh quá lớn (giữ nguyên tỷ lệ khung hình) để giảm tải cho RAM và CPU
    3. Convert mode về RGB (tránh lỗi với ảnh PNG transparent)
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert sang RGB để tránh lỗi kênh Alpha của PNG
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Resize nếu chiều dài hoặc rộng vượt quá max_size
        # Sử dụng thumbnail để giữ tỷ lệ khung hình
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
        return image
    except Exception as e:
        raise ValueError(f"Image processing failed: {str(e)}")