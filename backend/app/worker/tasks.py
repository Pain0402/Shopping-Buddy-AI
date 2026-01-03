from app.core.celery_app import celery_app
from app.db.session import SessionLocal # Worker dùng Sync Session cho đơn giản và ổn định
# Import app.db.base để đảm bảo tất cả Models (User, Product, Task) được đăng ký vào Metadata
import app.db.base 
from app.db.models.task import SearchTask
from app.db.models.product import Product
from app.services.storage import S3Client
from app.core.ai_engine import ai_engine
from app.db.vector_store import vector_store
import json
import time

@celery_app.task
def test_celery_task(word: str):
    return f"Hello {word}"

@celery_app.task
def process_visual_search(task_id: str):
    print(f"🔥 Bắt đầu xử lý Task AI: {task_id}")
    
    # 1. Kết nối DB (Sync)
    db = SessionLocal()
    try:
        task = db.query(SearchTask).filter(SearchTask.id == task_id).first()
        
        if not task:
            print("❌ Không tìm thấy Task trong DB")
            return "Task not found"

        # 2. Update status -> PROCESSING
        task.status = "PROCESSING"
        db.commit()

        # 3. Download Ảnh từ S3
        s3 = S3Client()
        print(f"📥 Đang tải ảnh: {task.input_image_url}")
        image_bytes = s3.download_file_as_bytes(task.input_image_url)

        # 4. AI Inference (Tạo Vector)
        print("🧠 Đang chạy AI Model...")
        query_vector = ai_engine.create_embedding(image_bytes)

        # 5. Tìm kiếm Vector (ChromaDB)
        print("🔍 Đang tìm kiếm trong ChromaDB...")
        results = vector_store.search(query_vector, k=5)
        
        # Kiểm tra kết quả
        if not results['ids'] or len(results['ids'][0]) == 0:
            print("⚠️ Không tìm thấy sản phẩm nào giống.")
            task.result = []
            task.status = "COMPLETED"
            db.commit()
            return "No results found"

        top_ids = results['ids'][0] # Chroma trả về list lồng nhau
        print(f"✅ Tìm thấy {len(top_ids)} sản phẩm tương đồng.")

        # 6. Lấy thông tin chi tiết từ Postgres
        # (Chroma chỉ chứa ID và Vector, Postgres chứa Tên, Giá, Ảnh sản phẩm)
        products = db.query(Product).filter(Product.id.in_(top_ids)).all()
        
        # Convert SQLAlchemy Objects -> JSON List
        result_data = []
        for p in products:
            result_data.append({
                "id": str(p.id),
                "name": p.name,
                "price": p.price,
                "image_url": p.image_url,
                "category": p.category,
                "description": p.description
            })

        # 7. Lưu kết quả và Hoàn thành
        task.result = result_data
        task.status = "COMPLETED"
        db.commit()
        print("🎉 Task hoàn thành xuất sắc!")
        return f"Found {len(products)} products"

    except Exception as e:
        print(f"💥 Lỗi nghiêm trọng khi xử lý task: {e}")
        db.rollback() # Quan trọng: Rollback để tránh lỗi PendingRollbackError cho request sau
        # Cố gắng lưu trạng thái FAILED (nếu kết nối DB vẫn ổn sau rollback)
        try:
            # Re-query task để update status (vì object cũ có thể đã bị detach/lỗi)
            task = db.query(SearchTask).filter(SearchTask.id == task_id).first()
            if task:
                task.status = "FAILED"
                task.error_message = str(e)
                db.commit()
        except Exception as sub_e:
            print(f"Không thể cập nhật status FAILED: {sub_e}")
            
    finally:
        db.close()