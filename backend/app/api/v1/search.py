from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from app.core.ai_engine import ai_engine
from app.db.vector_store import vector_store
from app.api.v1.schemas import SearchResponse, ProductResponse
from app.core.utils import process_image

router = APIRouter()

SEARCH_THRESHOLD = 0.6 

@router.post("/search/visual", response_model=SearchResponse)
async def visual_search(
    request: Request,
    file: UploadFile = File(...)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # 1. Đọc và Xử lý ảnh (Resize) bằng hàm util mới
        contents = await file.read()
        # CPU Bound -> run in threadpool để không block async loop
        image = await run_in_threadpool(process_image, contents)

        # 2. Tạo Embedding
        embedding = await run_in_threadpool(ai_engine.get_embedding, image)

        # 3. Truy vấn Vector DB
        search_results = await run_in_threadpool(
            vector_store.search, 
            query_embedding=embedding, 
            n_results=5
        )

        # 4. Map kết quả trả về (Full Info & Image URL)
        items = []
        if search_results['ids'] and search_results['distances']:
            ids = search_results['ids'][0]
            distances = search_results['distances'][0]
            metadatas = search_results['metadatas'][0]
            
            # Lấy Base URL từ request hiện tại để build link ảnh chính xác
            # Giúp hoạt động đúng trên cả localhost và Android Emulator (10.0.2.2)
            base_url = str(request.base_url).rstrip("/")

            for i in range(len(ids)):
                if distances[i] < SEARCH_THRESHOLD:
                    # Lấy đường dẫn ảnh từ metadata, nếu không có thì để rỗng
                    rel_path = metadatas[i].get('image_url', '')
                    
                    # Xử lý Full URL
                    if rel_path.startswith("http") and not rel_path.startswith("http://localhost") and not rel_path.startswith("http://10.0.2.2"):
                        full_img_url = rel_path
                    else:
                        # Nếu là đường dẫn tương đối (/static/...) thì ghép với base_url
                        full_img_url = f"{base_url}{rel_path}"

                    items.append(ProductResponse(
                        id=ids[i],
                        name=metadatas[i].get('name', 'Unknown'),
                        category=metadatas[i].get('category', 'Unknown'),
                        price=metadatas[i].get('price', 0.0),
                        image_url=full_img_url,
                        score=distances[i],
                        metadata=metadatas[i]
                    ))

        return SearchResponse(results=items)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")