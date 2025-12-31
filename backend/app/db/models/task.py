import uuid
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base
class SearchTask(Base):
    __tablename__ = "search_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Nullable cho Guest
    status = Column(String, default="PENDING", index=True) # PENDING, PROCESSING, COMPLETED, FAILED
    
    input_image_url = Column(String) # Ảnh user upload
    result = Column(JSON, nullable=True) # Kết quả trả về từ AI Worker
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())