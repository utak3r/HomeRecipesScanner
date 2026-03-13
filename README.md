# 🥘 Inteligentny Skaner Przepisów Kulinarnych

![Backend Tech Stack](https://img.shields.io/badge/Backend%20Stack-Python%20%7C%20FastAPI%20%7C%20Redis%20%7C%20Celery%20%7C%20Tesseract%20%7C%20Gemini%20AI-blue)
![Mobile Tech Stack](https://img.shields.io/badge/Mobile%20Client%20Stack-Flutter-blue)
![Web Tech Stack](https://img.shields.io/badge/Web%20Client%20Stack-Vite%20%7C%20Node-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Aplikacja do digitalizacji drukowanych oraz ręcznie pisanych przepisów kulinarnych. System wykorzystuje hybrydowe podejście OCR: 
najpierw lokalny silnik **Tesseract** podejmuje próbę odczytu tekstu, co w przypadku skanów tekstów drukowanych się powodzi, natomiast 
dla skanów przepisów spisanych odręcznie na kartce (lub kartkach) używa **Google Gemini AI**. Odczytane pismo (niezależnie od pochodzenia) 
poddawane jest analizie i strukturyzacji do postaci JSON z użyciem **Google Gemini AI**. Skany zapisane są w podpiętym wolemnie, a ustrukturyzowane 
dane zapisane w bazie PostgreSQL, która te dane indeksuje i umożliwia późniejsze wyszukiwanie pełnotekstowe.


---

## 🏗️ Architektura Systemu

System bazuje na architekturze mikroserwisowej zorkiestrowanej przez Docker Compose. Poniżej znajduje się wizualizacja przepływów danych:

```mermaid
graph TB
    %% Definicja Stylów
    classDef mobile fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,rx:10,ry:10;
    classDef web fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,rx:10,ry:10;
    classDef server fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20,rx:5,ry:5;
    classDef storage fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef cloud fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c,stroke-dasharray: 5 5;
    classDef worker fill:#eceff1,stroke:#455a64,stroke-width:2px,color:#263238;

    User((👤 User))
    
    subgraph Client1 [Mobile application]
        App1[📱 Flutter]:::mobile
    end
    
    subgraph Client2 [Web page]
	      App2[ 🌐 Vite + Node.JS]:::web
	  end

    subgraph Backend [Docker Stack]
        API[🚀 FastAPI Server]:::server
        Redis[(Redis Broker)]:::worker
        
        subgraph WorkerEnv [Worker Container]
            Worker[⚙️ Celery Worker]:::worker
            Tess[[📄 Tesseract OCR]]:::worker
        end

        DB[(🗄️ PostgreSQL)]:::storage
        Vol[(📂 Image Volume)]:::storage
    end

    subgraph AI [Cloud services]
        Gemini[🧠 Gemini AI]:::cloud
    end

    User --> App1
    App1 <==>|REST API| API
    User --> App2
    App2 <==>|REST API| API
    API <-->|Upload / Download| Vol
    API -->|Queue Task| Redis
    Redis --> Worker
    Worker -->|Read| Vol
    Worker --- Tess
    Worker ==>|Handwritten OCR & JSON| Gemini
    Worker -->|Save Result| DB
```

---

## 🛠️ Stack Technologiczny

- **Frontend mobilny:** Flutter (Mobile App) – interfejs użytkownika i obsługa aparatu.
- **Frontend webowy:** Vite + Node - interfejs użytkownika.
- **Backend API:** FastAPI (Python) – lekki i szybki serwer pośredniczący.
- **Asynchroniczność:** Celery + Redis – obsługa zadań OCR w tle.
- **OCR Poziom 1:** Tesseract OCR – silnik zainstalowany lokalnie w kontenerze workera.
- **OCR Poziom 2 & AI:** Google Gemini API – zaawansowana analiza wizualna i strukturyzacja danych.
- **Baza danych:** PostgreSQL – przechowywanie metadanych przepisów oraz JSON.
- **Storage:** Docker Volumes – przechowywanie oryginalnych plików graficznych.

## ⚙️ Pipeline Przetwarzania Danych

1. **Ingest:** Aplikacja mobilna przesyła zdjęcie na endpoint `/recipes/upload`.
2. **Staging:** API zapisuje zdjęcie na wolumenie, tworzy rekord w bazie ze statusem `processing` i zleca zadanie do Redisa.
3. **Lokalny OCR:** Celery Worker próbuje przetworzyć obraz za pomocą Tesseracta.
4. **AI Fallback:** Jeśli tekst jest nieczytelny (np. trudne pismo odręczne), system automatycznie przesyła obraz do Google Gemini.
5. **Strukturyzacja:** Niezależnie od źródła tekstu, Gemini transformuje go w czysty obiekt JSON.
6. **Finalizacja:** Dane JSON oraz ścieżka do zdjęcia są aktualizowane w bazie, a status zmienia się na `processed`.

---

## 🚀 Instalacja i Konfiguracja - backend

### Wymagania

- Docker & Docker Compose
- Klucz API do Google Gemini (do pobrania z Google AI Studio)

### Kroki uruchomienia

1. Sklonuj repozytorium.
2. Utwórz plik `.env` w podkatalogu `server` i uzupełnij dane:
```
GEMINI_API_KEY=twoj_klucz_api
POSTGRES_USER=recipes_user
POSTGRES_PASSWORD=password
POSTGRES_DB=recipes
DATABASE_URL=postgresql+asyncpg://recipes_user:recipes@db:5432/recipes
REDIS_URL=redis://redis:6379/0
```
3. Uruchom cały stos technologiczny:

```bash
cd server
docker-compose up --build
```

## 🚀 Instalacja i Konfiguracja - aplikacja mobilna

### Wymagania

- Android Studio
- Flutter SDK

### Kroki uruchomienia

1. Sklonuj repozytorium.
2. Skopiuj plik `przepisy_flutter/.env.example` na `przepisy_flutter/.env` i wyedytuj wedle potrzeb.
3. Zbuduj aplikację Flutter:
```bash
cd przepisy_flutter
flutter build apk --dart-define-from-file=.env
```
4. Gotowy plik w wersji release znajduje się w `build\app\outputs\flutter-apk\app-release.apk`


## 🚀 Instalacja i Konfiguracja - aplikacja webowa

### Wymagania

- Docker & Docker Compose

### Kroki uruchomienia

1. Sklonuj repozytorium.
2. Utwórz plik `.env` w podkatalogu `client-web` i uzupełnij dane:
```
VITE_API_URL=http://twoje.ip.backendu:8000
```
3. Uruchom cały stos technologiczny:

```bash
cd client-web
docker-compose up --build
```


---

## 📝 Licencja

Projekt udostępniany na licencji MIT.
