from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.services.storage import S3Client
from app.api import deps
from app.db.models.user import User
from app.db.models.task import SearchTask
from app.schemas.task import TaskCreateResponse, TaskStatusResponse

router = APIRouter()

# 1. API Gửi ảnh & Tạo Task
@router.post("/visual", response_model=TaskCreateResponse)
async def search_visual(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    1. Upload ảnh lên S3
    2. Tạo bản ghi Task (PENDING)
    3. Trả về Task ID để Client polling
    """
    # Validate
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # A. Upload S3 (I/O Bound)
    s3_client = S3Client()
    file_key = await s3_client.upload_file(file)
    
    # B. Lưu Task vào DB
    new_task = SearchTask(
        user_id=current_user.id,
        input_image_url=file_key,
        status="PENDING" 
        # Sau này ta sẽ bắn event vào Redis Queue ở đây (Task 3.x)
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    return {
        "task_id": new_task.id,
        "status": "PENDING",
        "message": "Image uploaded. AI processing started."
    }

# 2. API Kiểm tra trạng thái Task (Polling)
@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Mobile App gọi API này 2s/lần để lấy kết quả.
    """
    # Query DB tìm task
    result = await db.execute(select(SearchTask).where(SearchTask.id == task_id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Bảo mật: Chỉ chủ sở hữu task mới được xem (Optional)
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
        
    # Manual mapping to match Schema fields (id -> task_id, error_message -> error)
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result,
        "error": task.error_message,
        "created_at": task.created_at
    }