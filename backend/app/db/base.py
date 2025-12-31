# Import tất cả models vào đây để Alembic có thể detect được
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.product import Product
from app.db.models.task import SearchTask