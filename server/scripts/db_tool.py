import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Załadowanie zmiennych z .env
load_dotenv()

# Konfiguracja pobrana z Twojego środowiska
DB_CONTAINER = "postgres_db"
DB_USER = os.getenv("POSTGRES_USER", "recipes_user")
DB_NAME = os.getenv("POSTGRES_DB", "recipes")
BACKUP_DIR = "../backups"

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Utworzono katalog: {BACKUP_DIR}")

def backup():
    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BACKUP_DIR}/backup_{DB_NAME}_{timestamp}.sql"
    
    print(f"Rozpoczynam tworzenie kopii zapasowej bazy: {DB_NAME}...")
    
    # Polecenie pg_dump wykonane wewnątrz kontenera i zapisane na hoście
    cmd = f"docker exec -t {DB_CONTAINER} pg_dump -U {DB_USER} {DB_NAME} > {filename}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"SUKCES! Kopia zapisana w: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"BŁĄD podczas tworzenia kopii: {e}")

def restore(filename):
    if not os.path.exists(filename):
        print(f"BŁĄD: Plik {filename} nie istnieje!")
        return

    print(f"UWAGA: Przywracanie bazy z pliku {filename} nadpisze obecne dane!")
    confirm = input("Czy na pewno chcesz kontynuować? (t/n): ")
    
    if confirm.lower() != 't':
        print("Anulowano.")
        return

    print("Rozpoczynam przywracanie...")
    
    # Polecenie psql wykonane wewnątrz kontenera, czytające z pliku na hoście
    # Używamy -i (interactive), aby przesłać strumień danych
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
        print("  python db_tool.py backup          - tworzy nową kopię")
        print("  python db_tool.py restore [plik]  - przywraca bazę z pliku")
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
