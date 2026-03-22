import urllib.request
import urllib.error
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from app.workers.ai_processing import ai_extract_recipe_from_url_content, RecipeAIError

def clean_html_for_gemini(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    og_image = ""
    meta_og = soup.find("meta", property="og:image")
    if meta_og:
        og_image = meta_og.get("content", "")
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()

    return f"Sugerowany URL zdjęcia (z metatagów): {og_image}\n\nKOD STRONY:\n{soup.get_text(separator=' ', strip=True)}"

def fetch_url_content(url: str) -> str:
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return clean_html_for_gemini(html)
    except urllib.error.URLError as e:
        raise RuntimeError(f"Błąd pobierania strony: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Niespodziewany błąd pobierania: {str(e)}")

def run_url_pipeline(url: str):
    try:
        content = fetch_url_content(url)
        if not content or len(content) < 100:
            raise RuntimeError("Pobrana strona jest zbyt krótka lub pusta.")
        
        final_result = ai_extract_recipe_from_url_content(content)
        return final_result

    except RecipeAIError as e:
        print(f"BŁĄD AI: {e}")
        return {
            "title": "Błąd przetwarzania",
            "ingredients": [],
            "steps": [],
            "notes": str(e),
            "image_url": ""
        }
    except Exception as e:
        print(f"Krytyczny błąd systemu: {e}")
        return {"error": str(e)}
