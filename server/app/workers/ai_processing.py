import json
from google import genai
from google.genai import types, errors
import cv2
import numpy as np
from PIL import Image
import os
from dotenv import load_dotenv
from functools import cache
from app.workers.image_processing import heavy_image_preprocessing_for_ocr


class RecipeAIError(Exception):
    """Exception for issues with AI processing."""
    pass

@cache
def get_gemini_client():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No API key in environment!")
        
    return genai.Client(api_key=api_key)

def get_models_list():
    client = get_gemini_client()    
    available_models = []
    
    for m in client.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            
    return available_models


def ai_clean_and_structure_text(raw_ocr_text: str) -> dict:
    prompt = f"""
Jesteś systemem eksperckim do analizy i korekty tekstów kulinarnych.
Otrzymasz surowy tekst przepisu pochodzący z systemu OCR 
(często zawiera błędy, brak polskich znaków, literówki).

Twoje zadania (wykonaj je jednocześnie):
1. ZROZUM I NAPRAW: Popraw oczywiste błędy OCR (np. "rnqka" -> "mąka", "cuk1er" -> "cukier"), 
   uzupełnij brakujące polskie znaki.
2. USTRUKTURYZUJ: Sformatuj naprawiony tekst OD RAZU jako JSON.

Zasady rygorystyczne:
- Zwróć WYŁĄCZNIE poprawny kod JSON.
- NIE zmieniaj znaczenia i proporcji. Zachowaj oryginalne nazewnictwo po poprawie ortografii.
- Jeśli brak ilości przy składniku, wstaw pusty string "".
- Nie zgaduj brakujących danych.

Wymagana struktura JSON:
{{
  "title": "Tytuł przepisu (jeśli istnieje)",
  "ingredients": [
    {{"name": "nazwa składnika", "amount": "ilość i jednostka"}}
  ],
  "steps": [
    "krok 1",
    "krok 2"
  ],
  "notes": "wszelkie dodatkowe uwagi, informacje o pieczeniu, dopiski autora"
}}

SUROWY TEKST OCR:
{raw_ocr_text}
"""

    client = get_gemini_client()
    config = types.GenerateContentConfig(
        temperature=0.0,
        response_mime_type="application/json"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        raw_json_text = response.text.strip()
        raw_json_text = raw_json_text.replace("```json", "").replace("```", "")
        
        return json.loads(raw_json_text)
    
    # API errors, like bad API key or query limit
    except errors.APIError as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            raise RecipeAIError("Gemini API queries limit exceeded. Wait a moment and try again.")
        elif "401" in error_msg or "403" in error_msg or "API_KEY_INVALID" in error_msg:
            raise RecipeAIError("Authorization error. Check your GEMINI_API_KEY.")
        else:
            raise RecipeAIError(f"Error on Google servers side: {error_msg}")

    # JSON parsing errors
    except json.JSONDecodeError:
        raise RecipeAIError("AI responded with an invalid format (JSON expected).")
    
    # Network errors, like no internet, timeout etc.
    except Exception as e:
        raise RecipeAIError(f"Unexpected error while communicating with AI: {str(e)}")



def ai_image_to_json(images_list: list[np.ndarray]) -> dict:
    prompt = """
Jesteś systemem eksperckim do analizy odręcznych przepisów kulinarnych.
Twoim zadaniem jest odczytać przepis z załączonych obrazków i OD RAZU sformatować go jako jeden spójny JSON.

Zasady:
- Zignoruj skreślenia i błędy, wyciągnij logiczny sens przepisu.
- Popraw oczywiste błędy ortograficzne wynikające z niewyraźnego pisma.
- Jeśli brak ilości, wstaw pusty string "".
- Nie zgaduj brakujących danych.

Wymagana struktura:
{
  "title": "Tytuł przepisu",
  "ingredients": [
    {"name": "składnik", "amount": "ilość"}
  ],
  "steps": ["krok 1", "krok 2"],
  "notes": "uwagi"
}
"""
    
    images = [Image.fromarray(img) for img in images_list]
    client = get_gemini_client()
    
    config = types.GenerateContentConfig(
        temperature=0.0,
        response_mime_type="application/json"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, *images],
            config=config
        )

        raw_json_text = response.text.strip()
        raw_json_text = raw_json_text.replace("```json", "").replace("```", "")
        return json.loads(raw_json_text)

    # API errors, like bad API key or query limit
    except errors.APIError as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            raise RecipeAIError("Gemini API queries limit exceeded. Wait a moment and try again.")
        elif "401" in error_msg or "403" in error_msg or "API_KEY_INVALID" in error_msg:
            raise RecipeAIError("Authorization error. Check your GEMINI_API_KEY.")
        else:
            raise RecipeAIError(f"Error on Google servers side: {error_msg}")

    # JSON parsing errors
    except json.JSONDecodeError:
        raise RecipeAIError("AI responded with an invalid format (JSON expected).")
    
    # Network errors, like no internet, timeout etc.
    except Exception as e:
        raise RecipeAIError(f"Unexpected error while communicating with AI: {str(e)}")


def ai_handwritten_text_recognition(image_paths: list[str]) -> str:
    processed_images = []
    for path in image_paths:
        img = heavy_image_preprocessing_for_ocr(path)
        processed_images.append(img)
    
    return ai_image_to_json(processed_images)
