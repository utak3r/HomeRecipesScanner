import os
import sys

UPLOAD_DIR = "uploads"
THUMB_DIR = os.path.join(UPLOAD_DIR, "thumbs")
THUMB_SIZE = (300, 300)

try:
    from PIL import Image
except ImportError:
    print("Brak biblioteki Pillow. Zainstaluj za pomocą: pip install Pillow")
    sys.exit(1)

def main():
    if not os.path.exists(UPLOAD_DIR):
        print(f"Katalog {UPLOAD_DIR} nie istnieje. Uruchom skrypt z katalogu głównego serwera.")
        return

    os.makedirs(THUMB_DIR, exist_ok=True)

    count = 0
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if os.path.isfile(file_path):
            thumb_path = os.path.join(THUMB_DIR, filename)
            
            if not os.path.exists(thumb_path):
                try:
                    with Image.open(file_path) as img:
                        img.thumbnail(THUMB_SIZE)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                            
                        img.save(thumb_path)
                        print(f"Wygenerowano miniaturę dla {filename}")
                        count += 1
                except Exception as e:
                    pass
                
    print(f"Gotowe! Wygenerowano {count} nowych miniatur.")

if __name__ == "__main__":
    main()
