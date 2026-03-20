import os
import subprocess
import shutil
import zipfile
import tempfile
import psycopg2
import boto3
from datetime import datetime
from dotenv import load_dotenv

# Domyślne ładowanie .env (można nadpisać w funkcjach)
load_dotenv()

BACKUP_DIR = "../backups"

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Utworzono katalog: {BACKUP_DIR}")

def get_db_connection(config):
    return psycopg2.connect(
        dbname=config['DB_NAME'],
        user=config['DB_USER'],
        password=config['DB_PASSWORD'],
        host=config['DB_HOST'],
        port=config['DB_PORT']
    )

def download_images(config, temp_dir):
    print("Pobieranie obrazów z tabeli recipe_images...")
    images_dir = os.path.join(temp_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    try:
        conn = get_db_connection(config)
        cur = conn.cursor()
        cur.execute("SELECT file_path FROM recipe_images")
        rows = cur.fetchall()
        
        count = 0
        if config['STORAGE'] == 'cloud':
            s3 = boto3.client(
                's3',
                aws_access_key_id=config['S3_ACCESS_KEY'],
                aws_secret_access_key=config['S3_SECRET_KEY'],
                endpoint_url=config['S3_ENDPOINT_URL'],
                region_name=config['S3_REGION']
            )
            for (file_path,) in rows:
                local_path = os.path.join(images_dir, file_path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                print(f"  Ściąganie z S3: {file_path}")
                s3.download_file(config['S3_BUCKET'], file_path, local_path)
                count += 1
        else:
            # Zakładamy STORAGE=local, obrazy w katalogu 'uploads' w root projektu
            base_uploads = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
            for (file_path,) in rows:
                source_path = os.path.join(base_uploads, file_path)
                if os.path.exists(source_path):
                    dest_path = os.path.join(images_dir, file_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    print(f"  Kopiowanie lokalne: {file_path}")
                    count += 1
                else:
                    print(f"  OSTRZEŻENIE: Plik nie istnieje locally: {source_path}")
        
        cur.close()
        conn.close()
        print(f"Pobrano {count} obrazów.")
        return images_dir
    except Exception as e:
        print(f"BŁĄD podczas pobierania obrazów: {e}")
        return None

def backup():
    # Ładowanie specyficznie .env.prod zgodnie z wymaganiem
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env.prod")
    if os.path.exists(env_path):
        print(f"Ładowanie konfiguracji z {env_path}")
        load_dotenv(env_path, override=True)
    else:
        print(f"OSTRZEŻENIE: Plik {env_path} nie istnieje. Używam domyślnego .env")

    config = {
        'DB_USER': os.getenv("POSTGRES_USER"),
        'DB_PASSWORD': os.getenv("POSTGRES_PASSWORD"),
        'DB_NAME': os.getenv("POSTGRES_DB"),
        'DB_HOST': os.getenv("POSTGRES_HOST", "localhost"),
        'DB_PORT': os.getenv("POSTGRES_PORT", "5432"),
        'STORAGE': os.getenv("STORAGE", "local"),
        'S3_BUCKET': os.getenv("S3_BUCKET"),
        'S3_ACCESS_KEY': os.getenv("S3_ACCESS_KEY"),
        'S3_SECRET_KEY': os.getenv("S3_SECRET_KEY"),
        'S3_REGION': os.getenv("S3_REGION", "auto"),
        'S3_ENDPOINT_URL': os.getenv("S3_ENDPOINT_URL"),
        'DB_CONTAINER': "postgres_db" # Zachowano dla kompatybilności wstecznej jeśli potrzebne
    }

    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"backup_{config['DB_NAME']}_{timestamp}"
    zip_filename = os.path.abspath(f"{BACKUP_DIR}/{base_name}.zip")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        sql_filename = os.path.join(temp_dir, f"{base_name}.sql")
        
        print(f"Rozpoczynam tworzenie kopii zapasowej bazy: {config['DB_NAME']}...")
        
        # Przygotowanie polecenia pg_dump. 
        # Jeśli HOST to localhost i mamy DB_CONTAINER, używamy dockera.
        # W przeciwnym razie (np. Supabase), używamy pg_dump bezpośrednio.
        env = os.environ.copy()
        env["PGPASSWORD"] = config['DB_PASSWORD']
        
        if config['DB_HOST'] in ['localhost', '127.0.0.1', 'db'] and shutil.which("docker"):
            print("Używam pg_dump przez Docker...")
            cmd = f"docker exec -e PGPASSWORD={config['DB_PASSWORD']} {config['DB_CONTAINER']} pg_dump -U {config['DB_USER']} -h localhost -p 5432 {config['DB_NAME']} > {sql_filename}"
            # Uwaga: wewnątrz kontenera host to zazwyczaj localhost
        else:
            print(f"Używam pg_dump bezpośrednio (Host: {config['DB_HOST']})...")
            cmd = f"pg_dump -h {config['DB_HOST']} -p {config['DB_PORT']} -U {config['DB_USER']} {config['DB_NAME']} > {sql_filename}"

        try:
            subprocess.run(cmd, shell=True, check=True, env=env)
            print(f"Zrzut SQL gotowy.")
            
            # Pobieranie obrazów
            images_path = download_images(config, temp_dir)
            
            # Pakowanie do ZIP
            print(f"Pakowanie do ZIP: {zip_filename}...")
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Dodaj SQL
                zipf.write(sql_filename, arcname=f"{base_name}.sql")
                # Dodaj obrazy
                if images_path and os.path.exists(images_path):
                    for root, dirs, files in os.walk(images_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join("images", os.path.relpath(file_path, images_path))
                            zipf.write(file_path, arcname=arcname)
            
            print(f"SUKCES! Kopia zapisana w: {zip_filename}")
        except subprocess.CalledProcessError as e:
            print(f"BŁĄD podczas tworzenia kopii SQL: {e}")
        except Exception as e:
            print(f"BŁĄD podczas tworzenia backupu: {e}")

def restore(filename):
    # Przy restore też warto załadować .env.prod jeśli chcemy przywracać na produkcję
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env.prod")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)

    DB_USER = os.getenv("POSTGRES_USER", "recipes_user")
    DB_NAME = os.getenv("POSTGRES_DB", "recipes")
    DB_CONTAINER = "postgres_db"

    if not os.path.exists(filename):
        print(f"BŁĄD: Plik {filename} nie istnieje!")
        return

    print(f"UWAGA: Przywracanie bazy z pliku {filename} nadpisze obecne dane!")
    print("Jeśli to plik ZIP, musisz go najpierw rozpakować i wskazać plik .sql.")
    confirm = input("Czy na pewno chcesz kontynuować? (t/n): ")
    
    if confirm.lower() != 't':
        print("Anulowano.")
        return

    print("Rozpoczynam przywracanie...")
    
    cmd = f"docker exec -i {DB_CONTAINER} psql -U {DB_USER} -d {DB_NAME} < {filename}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("SUKCES! Baza danych została przywrócona.")
    except subprocess.CalledProcessError as e:
        print(f"BŁĄD podczas przywracania: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Użycie:")
        print("  python db_tool.py backup          - tworzy nową kopię (SQL + obrazy w ZIP)")
        print("  python db_tool.py restore [plik]  - przywraca bazę z pliku .sql")
        sys.exit(1)

    action = sys.argv[1]
    
    if action == "backup":
        backup()
    elif action == "restore":
        if len(sys.argv) < 3:
            print("BŁĄD: Podaj ścieżkę do pliku backupu!")
        else:
            restore(sys.argv[2])
    else:
        print(f"Nieznana akcja: {action}")
