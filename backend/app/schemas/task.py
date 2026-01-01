from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

class TaskBase(BaseModel):
    pass

# Schema trả về khi tạo Task xong
class TaskCreateResponse(BaseModel):
    task_id: UUID
    status: str
    message: str

# Schema trả về khi Polling (Check status)
class TaskStatusResponse(BaseModel):
    task_id: UUID
    status: str      # PENDING, PROCESSING, COMPLETED, FAILED
    result: Optional[Any] = None # Kết quả JSON (Danh sách sản phẩm)
    error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True