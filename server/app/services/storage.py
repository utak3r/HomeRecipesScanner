import os
import uuid
from PIL import Image

UPLOAD_DIR = "uploads"
THUMB_DIR = os.path.join(UPLOAD_DIR, "thumbs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

THUMB_SIZE = (300, 300)

async def save_upload(file):
    ext = file.filename.split(".")[-1]
    name = f"{uuid.uuid4()}.{ext}"

    path = os.path.join(UPLOAD_DIR, name)

    with open(path, "wb") as f:
        f.write(await file.read())
        
    try:
        with Image.open(path) as img:
            img.thumbnail(THUMB_SIZE)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            thumb_path = os.path.join(THUMB_DIR, name)
            img.save(thumb_path)
    except Exception as e:
        print(f"Błąd generowania miniatury: {e}")

    return path
