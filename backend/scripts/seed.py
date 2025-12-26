import sys
import os
import requests
from PIL import Image
from io import BytesIO

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.ai_engine import ai_engine
from app.db.vector_store import vector_store

# Thư mục lưu ảnh static
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
os.makedirs(STATIC_DIR, exist_ok=True)

def download_and_save_image(url: str, filename: str) -> str:
    """
    Tải ảnh từ URL, lưu vào static/images và trả về đường dẫn tương đối.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Lưu file
        filepath = os.path.join(STATIC_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
            
        return f"/static/images/{filename}"
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def seed_data():
    print("Initializing AI Engine...")
    ai_engine.initialize()

    sample_products = [
        {
            "id": "prod_001",
            "url": "https://myo.vn/wp-content/uploads/2023/11/ao-thun-in-mona-32.jpg",
            "metadata": {"name": "Áo Thun Mona Lisa", "category": "T-Shirt", "price": 20.0}
        },
        {
            "id": "prod_002",
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Vincent_van_Gogh_-_Self-Portrait_-_Google_Art_Project_%28454045%29.jpg/330px-Vincent_van_Gogh_-_Self-Portrait_-_Google_Art_Project_%28454045%29.jpg",
            "metadata": {"name": "Áo Khoác Van Gogh", "category": "Jacket", "price": 55.0}
        },
        {
            "id": "prod_003",
            "url": "https://images-na.ssl-images-amazon.com/images/I/71FzctEw97L._SS400_.jpg",
            "metadata": {"name": "Áo khoác anime pain", "category": "Dress", "price": 120.0}
        }
    ]

    ids = []
    embeddings = []
    metadatas = []

    print(f"Processing {len(sample_products)} items...")

    for prod in sample_products:
        try:
            filename = f"{prod['id']}.jpg"
            print(f"Downloading image for {prod['id']}...")
            
            # 1. Tải và lưu ảnh static
            local_path = download_and_save_image(prod['url'], filename)
            
            if not local_path:
                print(f"Skipping {prod['id']} due to download error.")
                continue

            # 2. Tạo embedding từ file local
            full_local_path = os.path.join(STATIC_DIR, filename)
            image = Image.open(full_local_path).convert("RGB")
            vector = ai_engine.get_embedding(image)
            
            # 3. Cập nhật metadata có image_url
            meta = prod["metadata"].copy()
            meta["image_url"] = local_path
            
            ids.append(prod["id"])
            embeddings.append(vector)
            metadatas.append(meta)
            print(f"Processed: {prod['id']}")
            
        except Exception as e:
            print(f"Error processing {prod['id']}: {e}")

    if ids:
        vector_store.add_items(ids, embeddings, metadatas)
        print("Seeding completed successfully with Local Images!")
    else:
        print("No items to seed.")

if __name__ == "__main__":
    seed_data()