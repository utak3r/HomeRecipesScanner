import pytest
from unittest.mock import patch, MagicMock
import cv2
import numpy as np
from app.workers.ocr_pipeline import run_ocr_pipeline, ocr_tesseract
from app.workers.ai_processing import ai_handwritten_text_recognition, ai_clean_and_structure_text
from app.workers.image_processing import light_image_preprocessing_for_ocr

MOCK_JSON_RESULT = {
    "title": "Test",
    "ingredients": [{"name": "Mąka", "amount": "1 kg"}],
    "steps": ["Krok 1"],
    "notes": ""
}


@patch('app.workers.ocr_pipeline.light_image_preprocessing_for_ocr')
@patch('app.workers.ocr_pipeline.ocr_tesseract')
@patch('app.workers.ocr_pipeline.ai_handwritten_text_recognition')
@patch('app.workers.ocr_pipeline.ai_clean_and_structure_text')
def test_pipeline_tesseract_success(mock_clean_structure, mock_handwritten, mock_tesseract, mock_preprocess):
    mock_preprocess.return_value = "dummy_cv2_image"
    mock_tesseract.side_effect = [("Tekst strony 1", 90), ("Tekst strony 2", 80)]
    mock_clean_structure.return_value = MOCK_JSON_RESULT

    paths = ["p1.jpg", "p2.jpg"]
    result = run_ocr_pipeline(paths)

    assert result == MOCK_JSON_RESULT
    assert mock_preprocess.call_count == 2
    assert mock_tesseract.call_count == 2

    mock_clean_structure.assert_called_once_with("Tekst strony 1\n\nTekst strony 2")
    mock_handwritten.assert_not_called()


@patch('app.workers.ocr_pipeline.light_image_preprocessing_for_ocr')
@patch('app.workers.ocr_pipeline.ocr_tesseract')
@patch('app.workers.ocr_pipeline.ai_handwritten_text_recognition')
def test_pipeline_tesseract_failure(mock_handwritten, mock_tesseract, mock_preprocess):
    mock_preprocess.return_value = "dummy_cv2_image"
    mock_tesseract.return_value = ("Błąd", 40) # Słaba pewność
    mock_handwritten.return_value = MOCK_JSON_RESULT

    paths = ["p1.jpg"]
    result = run_ocr_pipeline(paths)

    assert result == MOCK_JSON_RESULT

    mock_handwritten.assert_called_once_with(paths)


@patch('app.workers.ocr_pipeline.ai_clean_and_structure_text')
@patch('app.workers.ocr_pipeline.ai_handwritten_text_recognition')
def test_functional_pipeline_with_dummy_image(mock_handwritten, mock_clean_structure, tmp_path):
    test_image_path = str(tmp_path / "test_print.jpg")
    img = np.ones((200, 500, 3), dtype=np.uint8) * 255
    cv2.putText(img, 'Maka 1 kg', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    cv2.imwrite(test_image_path, img)

    mock_clean_structure.return_value = MOCK_JSON_RESULT

    result = run_ocr_pipeline([test_image_path])

    assert result == MOCK_JSON_RESULT
    mock_clean_structure.assert_called_once()


# Full End-to-End integration test, using Gemini API.
# To skip it, run `pytest -m "not integration"`
@pytest.mark.integration
def test_full_e2e_real_api(tmp_path):
    test_image_path = str(tmp_path / "test_e2e.jpg")
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255
    cv2.putText(img, 'Cukier 500g', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.imwrite(test_image_path, img)

    result = run_ocr_pipeline([test_image_path])

    assert isinstance(result, dict)
    assert "title" in result
    assert "ingredients" in result
