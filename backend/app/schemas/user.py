from typing import Optional
from pydantic import BaseModel, EmailStr
import uuid

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool

class Config:
    from_attributes = True # Cho phép đọc từ ORM model