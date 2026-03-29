import pytest
import urllib.error
from unittest.mock import patch, MagicMock, mock_open
from app.workers.url_pipeline import clean_html_for_gemini, fetch_url_content, run_url_pipeline
from app.workers.ai_processing import RecipeAIError

# --- UNIT TESTS for clean_html_for_gemini ---

def test_clean_html_for_gemini_with_og_image():
    html = """
    <html>
        <head>
            <meta property="og:image" content="https://example.com/image.jpg">
            <style>body { color: red; }</style>
        </head>
        <body>
            <nav>Menu</nav>
            <h1>Recipe Title</h1>
            <p>Some recipe content.</p>
            <script>alert('hello');</script>
        </body>
    </html>
    """
    result = clean_html_for_gemini(html)
    
    assert "Sugerowany URL zdjęcia (z metatagów): https://example.com/image.jpg" in result
    assert "Recipe Title" in result
    assert "Some recipe content." in result
    assert "Menu" not in result
    assert "alert('hello');" not in result
    assert "body { color: red; }" not in result

def test_clean_html_for_gemini_without_og_image():
    html = "<html><body><h1>No Image</h1></body></html>"
    result = clean_html_for_gemini(html)
    
    assert "Sugerowany URL zdjęcia (z metatagów): " in result
    assert " (z metatagów): \n" in result # og_image should be empty
    assert "No Image" in result

# --- UNIT TESTS for fetch_url_content ---

@patch("urllib.request.urlopen")
def test_fetch_url_content_success(mock_urlopen):
    # Mock the response object
    mock_response = MagicMock()
    mock_response.read.return_value = b"<html><body><h1>Success</h1></body></html>"
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response
    
    result = fetch_url_content("https://example.com")
    
    assert "Success" in result
    mock_urlopen.assert_called_once()

@patch("urllib.request.urlopen")
def test_fetch_url_content_url_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
    
    with pytest.raises(RuntimeError) as excinfo:
        fetch_url_content("https://example.com")
    
    assert "Błąd pobierania strony: Connection refused" in str(excinfo.value)

@patch("urllib.request.urlopen")
def test_fetch_url_content_generic_exception(mock_urlopen):
    mock_urlopen.side_effect = Exception("Unexpected error")
    
    with pytest.raises(RuntimeError) as excinfo:
        fetch_url_content("https://example.com")
    
    assert "Niespodziewany błąd pobierania: Unexpected error" in str(excinfo.value)

# --- UNIT TESTS for run_url_pipeline ---

@patch("app.workers.url_pipeline.fetch_url_content")
@patch("app.workers.url_pipeline.ai_extract_recipe_from_url_content")
def test_run_url_pipeline_success(mock_ai_extract, mock_fetch):
    mock_fetch.return_value = "A" * 150 # Long enough content
    mock_ai_result = {"title": "Mock Recipe", "ingredients": []}
    mock_ai_extract.return_value = mock_ai_result
    
    result = run_url_pipeline("https://example.com")
    
    assert result == mock_ai_result
    mock_fetch.assert_called_once_with("https://example.com")
    mock_ai_extract.assert_called_once_with(mock_fetch.return_value)

@patch("app.workers.url_pipeline.fetch_url_content")
def test_run_url_pipeline_too_short_content(mock_fetch):
    mock_fetch.return_value = "Short"
    
    result = run_url_pipeline("https://example.com")
    
    assert "error" in result
    assert "Pobrana strona jest zbyt krótka lub pusta" in result["error"]

@patch("app.workers.url_pipeline.fetch_url_content")
@patch("app.workers.url_pipeline.ai_extract_recipe_from_url_content")
def test_run_url_pipeline_ai_error(mock_ai_extract, mock_fetch):
    mock_fetch.return_value = "A" * 150
    mock_ai_extract.side_effect = RecipeAIError("AI failed")
    
    result = run_url_pipeline("https://example.com")
    
    assert result["title"] == "Błąd przetwarzania"
    assert "AI failed" in result["notes"]

@patch("app.workers.url_pipeline.fetch_url_content")
def test_run_url_pipeline_fetch_error(mock_fetch):
    mock_fetch.side_effect = RuntimeError("Fetch failed")
    
    result = run_url_pipeline("https://example.com")
    
    assert result == {"error": "Fetch failed"}

# --- FUNCTIONAL TESTS for run_url_pipeline ---

@patch("urllib.request.urlopen")
@patch("app.workers.url_pipeline.ai_extract_recipe_from_url_content")
def test_functional_url_pipeline(mock_ai_extract, mock_urlopen):
    # This test exercises most of the pipeline code path including HTML cleaning
    mock_response = MagicMock()
    mock_response.read.return_value = b"<html><body><h1>Recipe Name</h1><p>Delicious!</p><p>" + b"A" * 100 + b"</p></body></html>"
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response
    
    mock_ai_result = {
        "title": "Recipe Name",
        "ingredients": [{"name": "Love", "amount": "1 cup"}],
        "steps": ["Be happy"],
        "notes": "Enjoy"
    }
    mock_ai_extract.return_value = mock_ai_result
    
    result = run_url_pipeline("https://example.com")
    
    assert result == mock_ai_result
    mock_urlopen.assert_called_once()
    mock_ai_extract.assert_called_once()
    
    # Check what was passed to AI (should be cleaned text)
    cleaned_content_passed_to_ai = mock_ai_extract.call_args[0][0]
    assert "Recipe Name" in cleaned_content_passed_to_ai
    assert "Delicious!" in cleaned_content_passed_to_ai
    assert "<html>" not in cleaned_content_passed_to_ai
