from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.services.storage import S3Client
from app.api import deps
from app.db.models.user import User
from app.db.models.task import SearchTask
from app.schemas.task import TaskCreateResponse, TaskStatusResponse

# Import task từ worker (chỉ import function definition)
from app.worker.tasks import process_visual_search

router = APIRouter()

@router.post("/visual", response_model=TaskCreateResponse)
async def search_visual(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Validate
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # 1. Upload S3
    s3_client = S3Client()
    file_key = await s3_client.upload_file(file)
    
    # 2. Lưu Task vào DB (PENDING)
    new_task = SearchTask(
        user_id=current_user.id,
        input_image_url=file_key,
        status="PENDING"
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    # 3. KÍCH HOẠT WORKER (QUAN TRỌNG NHẤT)
    # .delay() sẽ gửi message vào Redis, Worker sẽ bắt lấy và chạy nền
    process_visual_search.delay(str(new_task.id))
    
    return {
        "task_id": new_task.id,
        "status": "PENDING",
        "message": "Image uploaded. AI processing started."
    }

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    result = await db.execute(select(SearchTask).where(SearchTask.id == task_id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
        
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result,
        "error": task.error_message,
        "created_at": task.created_at
    }