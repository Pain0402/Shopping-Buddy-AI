from app.core.celery_app import celery_app
import time

@celery_app.task
def test_celery_task(word: str):
    """
    Task test đơn giản: Chờ 5s rồi trả về chuỗi chào hỏi.
    """
    print(f"Executing task for: {word}")
    time.sleep(5) # Giả lập xử lý nặng
    return f"Hello {word}, task completed!"