import asyncio
import sys
import os
from datetime import datetime
import uuid
import requests
from io import BytesIO

# Thêm đường dẫn để import được app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal
from app.db.models.product import Product
from app.core.ai_engine import ai_engine
from app.db.vector_store import vector_store

# Danh sách sản phẩm mẫu (Lấy ảnh từ Unsplash để demo)
SAMPLE_PRODUCTS = [
    {
        "name": "Áo Thun Trắng Basic",
        "price": 150000,
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600",
        "category": "Ao",
        "desc": "Áo thun cotton trắng đơn giản, thoáng mát."
    },
    {
        "name": "Quần Jean Xanh Cổ Điển",
        "price": 450000,
        "image_url": "https://images.unsplash.com/photo-1542272454315-4c01d7abdf4a?w=600",
        "category": "Quan",
        "desc": "Quần jean denim xanh, dáng suông."
    },
    {
        "name": "Váy Hoa Mùa Hè",
        "price": 320000,
        "image_url": "https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=600",
        "category": "Vay",
        "desc": "Váy hoa nhí, chất liệu voan nhẹ nhàng."
    },
    {
        "name": "Giày Sneaker Trắng",
        "price": 800000,
        "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600",
        "category": "Giay",
        "desc": "Giày thể thao trắng năng động."
    },
    {
        "name": "Áo Hoodie Đen",
        "price": 550000,
        "image_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600",
        "category": "Ao",
        "desc": "Áo hoodie nỉ bông ấm áp."
    }
]

async def seed():
    print("🌱 Bắt đầu nạp dữ liệu mẫu...")
    
    # 1. Khởi tạo DB Session
    db = AsyncSessionLocal()
    
    try:
        for item in SAMPLE_PRODUCTS:
            print(f"🔄 Đang xử lý: {item['name']}...")
            
            # 2. Tải ảnh về RAM
            try:
                response = requests.get(item["image_url"], timeout=10)
                if response.status_code != 200:
                    print(f"❌ Lỗi tải ảnh: {item['image_url']}")
                    continue
                image_bytes = response.content
            except Exception as e:
                print(f"❌ Lỗi mạng: {e}")
                continue

            # 3. Tạo Embedding (Dùng AI Engine)
            # Lưu ý: Hàm này chạy CPU khá nặng
            vector = ai_engine.create_embedding(image_bytes)
            
            # 4. Lưu vào Postgres
            product_id = uuid.uuid4()
            product = Product(
                id=product_id,
                name=item["name"],
                price=item["price"],
                image_url=item["image_url"], # Ở môi trường thật, đây nên là S3 Key sau khi upload
                category=item["category"],
                description=item["desc"],
                meta_info={"source": "seed_script"}
            )
            db.add(product)
            
            # 5. Lưu vào ChromaDB
            # ID trong Chroma phải khớp ID Postgres (convert sang string)
            vector_store.add_product(str(product_id), vector)
            
            print(f"✅ Đã thêm: {item['name']} (ID: {product_id})")

        await db.commit()
        print("🎉 NẠP DỮ LIỆU THÀNH CÔNG!")
        
    except Exception as e:
        print(f"💥 Có lỗi xảy ra: {e}")
        await db.rollback()
    finally:
        await db.close()

if __name__ == "__main__":
    # Chạy hàm async
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed())