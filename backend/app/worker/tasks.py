from app.core.celery_app import celery_app
from app.db.session import SessionLocal 
# Import app.db.base để đảm bảo tất cả Models (User, Product, Task) được đăng ký vào Metadata
import app.db.base 
from app.db.models.task import SearchTask
from app.db.models.product import Product
from app.services.storage import S3Client
from app.core.ai_engine import ai_engine
from app.db.vector_store import vector_store
# Import thư viện xử lý timeout
import signal
from contextlib import contextmanager
import torch # Thêm thư viện torch
# Import Stylist AI mới
from app.services.ai.stylist import stylist_ai

# --- FIX DEADLOCK: Cấu hình PyTorch chạy đơn luồng ---
# Celery dùng 'prefork' pool, xung đột với OpenMP của PyTorch gây treo (deadlock).
# Ép về 1 thread sẽ giải quyết vấn đề này.
torch.set_num_threads(1)

# Context manager để giới hạn thời gian chạy của 1 đoạn code
class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

@celery_app.task
def test_celery_task(word: str):
    return f"Hello {word}"

@celery_app.task
def process_visual_search(task_id: str):
    print(f"🔥 [DEBUG] Bắt đầu xử lý Task ID: {task_id}", flush=True)
    
    # 1. Kết nối DB (Sync)
    db = SessionLocal()
    try:
        task = db.query(SearchTask).filter(SearchTask.id == task_id).first()
        
        if not task:
            print("❌ [DEBUG] Không tìm thấy Task trong DB", flush=True)
            return "Task not found"

        # 2. Update status -> PROCESSING
        task.status = "PROCESSING"
        db.commit()
        print("✅ [DEBUG] Đã update status -> PROCESSING", flush=True)

        # 3. Download Ảnh từ S3
        s3 = S3Client()
        print(f"📥 [DEBUG] Đang tải ảnh từ S3: {task.input_image_url} ...", flush=True)
        
        # Thêm try-catch cho việc download
        try:
            image_bytes = s3.download_file_as_bytes(task.input_image_url)
            print(f"✅ [DEBUG] Tải ảnh thành công. Kích thước: {len(image_bytes)} bytes", flush=True)
        except Exception as e:
            print(f"❌ [DEBUG] Lỗi tải ảnh: {e}", flush=True)
            raise e

        # 4. AI Inference (Tạo Vector)
        print("🧠 [DEBUG] Bắt đầu chạy AI Inference (CLIP)...", flush=True)
        
        # Dùng time_limit để tránh việc AI treo mãi mãi (Timeout 60s)
        try:
            with time_limit(60):
                query_vector = ai_engine.create_embedding(image_bytes)
            print("✅ [DEBUG] AI Inference hoàn tất. Vector size: 512", flush=True)
        except TimeoutException:
            print("❌ [DEBUG] AI Inference bị treo quá 60s -> KILL", flush=True)
            raise Exception("AI Model timeout")

        # 5. Tìm kiếm Vector (ChromaDB)
        print("🔍 [DEBUG] Đang tìm kiếm trong ChromaDB...", flush=True)
        results = vector_store.search(query_vector, k=5)
        
        # Kiểm tra kết quả
        if not results['ids'] or len(results['ids'][0]) == 0:
            print("⚠️ [DEBUG] Không tìm thấy sản phẩm nào giống.", flush=True)
            task.result = []
            task.status = "COMPLETED"
            db.commit()
            return "No results found"

        top_ids = results['ids'][0] # Chroma trả về list lồng nhau
        print(f"✅ [DEBUG] Tìm thấy {len(top_ids)} sản phẩm tương đồng: {top_ids}", flush=True)

        # 6. Lấy thông tin chi tiết từ Postgres
        products = db.query(Product).filter(Product.id.in_(top_ids)).all()
        print(f"✅ [DEBUG] Lấy được {len(products)} sản phẩm từ Postgres", flush=True)
        
        # --- LOGIC MỚI: GỌI STYLIST ---
        advice = ""
        if products:
            # Lấy sản phẩm giống nhất (Top 1) để hỏi Stylist
            best_match = products[0]
            print(f"🤖 [DEBUG] Đang hỏi ý kiến Stylist về: {best_match.name}...", flush=True)
            try:
                advice = stylist_ai.get_outfit_advice(
                    product_name=best_match.name,
                    product_desc=best_match.description or "Sản phẩm thời trang"
                )
                print("✅ [DEBUG] Stylist đã trả lời!", flush=True)
            except Exception as e:
                print(f"⚠️ [DEBUG] Lỗi Stylist: {e}", flush=True)
                advice = "Stylist đang bận, bạn tự phối nhé!"

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
        task.result = {
            "products": result_data,
            "stylist_advice": advice # Thêm lời khuyên vào kết quả
        }
        task.status = "COMPLETED"
        db.commit()
        print("🎉 [DEBUG] Task hoàn thành xuất sắc!", flush=True)
        return f"Found {len(products)} products"

    except Exception as e:
        print(f"💥 [DEBUG] Lỗi nghiêm trọng: {e}", flush=True)
        db.rollback() 
        try:
            task = db.query(SearchTask).filter(SearchTask.id == task_id).first()
            if task:
                task.status = "FAILED"
                task.error_message = str(e)
                db.commit()
                print("✅ [DEBUG] Đã cập nhật status -> FAILED", flush=True)
        except Exception as sub_e:
            print(f"❌ [DEBUG] Không thể cập nhật status FAILED: {sub_e}", flush=True)
            
    finally:
        db.close()