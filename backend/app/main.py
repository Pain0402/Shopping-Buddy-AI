from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import os

from app.core.config import settings
from app.core.ai_engine import ai_engine
from app.api.v1.search import router as search_router
from app.api.v1.stylist import router as stylist_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("System starting up...")
    
    # Đảm bảo thư mục static tồn tại để tránh lỗi khi mount
    os.makedirs("static/images", exist_ok=True)
    
    ai_engine.initialize()
    yield
    # --- Shutdown ---
    print("System shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# 1. Performance Middleware (Latency Logging)
# Đo thời gian xử lý của mỗi request
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Thêm header X-Process-Time vào response
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log ra console với icon 📡 cho dễ nhìn
    print(f"📡 {request.method} {request.url} - {round(process_time * 1000, 2)}ms")
    
    return response

# 2. Mount Static Files (Để phục vụ ảnh)
# Truy cập: http://localhost:8000/static/images/filename.jpg
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register Routers
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(stylist_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok", "ai_loaded": ai_engine._initialized}