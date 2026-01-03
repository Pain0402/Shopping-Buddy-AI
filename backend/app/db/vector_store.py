import chromadb
from app.core.config import settings

class VectorStore:
    def __init__(self):
        # Kết nối tới ChromaDB container qua HTTP
        self.client = chromadb.HttpClient(
            host="chromadb", # Tên service trong docker-compose
            port=8000
        )
        
        # Lấy hoặc tạo Collection "products"
        # Dùng khoảng cách cosine (cosine distance) để so sánh độ giống nhau
        self.collection = self.client.get_or_create_collection(
            name="products",
            metadata={"hnsw:space": "cosine"}
        )

    def search(self, query_vector, k=5):
        """Tìm kiếm top K sản phẩm giống nhất"""
        return self.collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )

    def add_product(self, product_id: str, embedding: list):
        """Thêm vector sản phẩm vào kho"""
        self.collection.add(
            ids=[product_id],
            embeddings=[embedding]
        )

# Singleton instance
vector_store = VectorStore()