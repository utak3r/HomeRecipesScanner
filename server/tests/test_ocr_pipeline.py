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
    """
    Test for successful Tesseract.
    It should call ai_clean_and_structure_text.
    """
    mock_preprocess.return_value = "dummy_cv2_image"
    mock_tesseract.return_value = ("Brudny tekst z tesseracta", 85)
    mock_clean_structure.return_value = MOCK_JSON_RESULT

    result = run_ocr_pipeline("dummy_path.jpg")

    assert result == MOCK_JSON_RESULT
    mock_preprocess.assert_called_once_with("dummy_path.jpg")
    mock_tesseract.assert_called_once_with("dummy_cv2_image")
    mock_clean_structure.assert_called_once_with("Brudny tekst z tesseracta")
    
    mock_handwritten.assert_not_called()


@patch('app.workers.ocr_pipeline.light_image_preprocessing_for_ocr')
@patch('app.workers.ocr_pipeline.ocr_tesseract')
@patch('app.workers.ocr_pipeline.ai_handwritten_text_recognition')
@patch('app.workers.ocr_pipeline.ai_clean_and_structure_text')
def test_pipeline_tesseract_failure(mock_clean_structure, mock_handwritten, mock_tesseract, mock_preprocess):
    """
    Test for unsuccessful Tesseract (confidence < 60).
    It should call ai_handwritten_text_recognition.
    """
    mock_preprocess.return_value = "dummy_cv2_image"
    mock_tesseract.return_value = ("Bzdury", 45)
    mock_handwritten.return_value = MOCK_JSON_RESULT

    result = run_ocr_pipeline("dummy_path.jpg")

    assert result == MOCK_JSON_RESULT
    mock_preprocess.assert_called_once_with("dummy_path.jpg")
    mock_tesseract.assert_called_once_with("dummy_cv2_image")
    mock_handwritten.assert_called_once_with("dummy_path.jpg")
    
    mock_clean_structure.assert_not_called()


@patch('app.workers.ocr_pipeline.ai_clean_and_structure_text')
@patch('app.workers.ocr_pipeline.ai_handwritten_text_recognition')
def test_functional_pipeline_with_dummy_image(mock_handwritten, mock_clean_structure, tmp_path):
    """
    Functional test using real Tesseract and OpenCV.
    Gemini is still mocked out.
    """
    # Creating a sample image
    test_image_path = str(tmp_path / "test_print.jpg")
    img = np.ones((200, 500, 3), dtype=np.uint8) * 255
    cv2.putText(img, 'Maka 1 kg', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    cv2.imwrite(test_image_path, img)

    # Mocking out Gemini API
    mock_clean_structure.return_value = MOCK_JSON_RESULT

    # Test.
    # Tesseract should be successful.
    result = run_ocr_pipeline(test_image_path)

    assert result == MOCK_JSON_RESULT
    
    mock_clean_structure.assert_called_once()
    mock_handwritten.assert_not_called()


# Full End-to-End integration test, using Gemini API.
# To skip it, run `pytest -m "not integration"`
@pytest.mark.integration
def test_full_e2e_real_api(tmp_path):
    test_image_path = str(tmp_path / "test_e2e.jpg")
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255
    cv2.putText(img, 'Cukier 500g', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.imwrite(test_image_path, img)

    result = run_ocr_pipeline(test_image_path)

    assert isinstance(result, dict)
    assert "title" in result
    assert "ingredients" in result
