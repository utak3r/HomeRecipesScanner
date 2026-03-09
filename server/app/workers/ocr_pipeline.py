import cv2
import numpy as np
import os
from dotenv import load_dotenv, find_dotenv
import pytesseract
from app.workers.ai_processing import ai_clean_and_structure_text, ai_handwritten_text_recognition
from app.workers.image_processing import light_image_preprocessing_for_ocr
from app.workers.ai_processing import RecipeAIError

def ocr_tesseract(img):
    load_dotenv(find_dotenv())
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
    
    data = pytesseract.image_to_data(
        img,
        lang="pol",
        output_type=pytesseract.Output.DICT
    )

    text_lines = []
    confidences = []
    for i, txt in enumerate(data["text"]):
        if txt.strip():
            text_lines.append(txt)
            confidences.append(int(data["conf"][i]))

    text = " ".join(text_lines)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    return text, avg_conf

"""
Main OCR pipeline
Returns a structured text
"""
def run_ocr_pipeline(image_path: str):
    try:
        # Try with Tesseract
        img = light_image_preprocessing_for_ocr(image_path)
        tess_text, confidence = ocr_tesseract(img)

        if confidence < 60:
            # Tesseract failed, go with Google Gemini
            final_result = ai_handwritten_text_recognition(image_path)
        else:
            final_result = ai_clean_and_structure_text(tess_text)

        return final_result

    except RecipeAIError as e:
        print(f"BŁĄD AI: {e}")
        # Failsafe fallback
        return {
            "title": "Błąd przetwarzania",
            "ingredients": [],
            "steps": [],
            "notes": str(e)
        }
    except Exception as e:
        print(f"Krytyczny błąd systemu: {e}")
        return {"error": str(e)}
