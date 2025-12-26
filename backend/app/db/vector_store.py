import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_items(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        if not ids:
            return
        self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas)
        logger.info(f"Upserted {len(ids)} items to vector store.")

    def search(self, query_embedding: List[float], n_results: int = 5):
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

    def get_item(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy metadata của một sản phẩm theo ID.
        Dùng cho RAG context retrieval.
        """
        try:
            result = self.collection.get(ids=[product_id])
            if result['ids']:
                # Trả về metadata của kết quả đầu tiên
                return result['metadatas'][0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving item {product_id}: {e}")
            return None

# Singleton instance
vector_store = VectorStore()