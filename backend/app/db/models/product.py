import uuid
from sqlalchemy import Column, String, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    price = Column(Float)
    currency = Column(String, default="VND")
    image_url = Column(String) # Link S3
    category = Column(String, index=True)
    
    # Metadata mở rộng (Brand, Material, Color...) dùng JSONB
    # Lưu ý: JSON trong SQLAlchemy với Postgres tự động map sang JSONB
    meta_info = Column(JSON, default={})