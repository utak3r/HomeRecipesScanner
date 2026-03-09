import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.api.deps import get_db
from app.db.models.recipe import Recipe

# --- Mocking Fixtures ---

@pytest.fixture
def mock_db_session():
    """Mocking AsyncSession from SQLAlchemy"""
    session = AsyncMock()
    return session

@pytest.fixture
def override_get_db(mock_db_session):
    async def _get_db_override():
        yield mock_db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

# --- TESTS ---

@pytest.mark.asyncio
async def test_list_recipes_empty(async_client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = []
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/recipes/")

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_list_recipes_with_data(async_client, mock_db_session):
    # All data in, short text.
    recipe_1 = Recipe(
        id=1, 
        title="Zupa pomidorowa", 
        cleaned_text="Pyszna zupa z pomidorów.", 
        raw_text=None
    )
    mock_image = MagicMock()
    mock_image.url = "/uploads/zupa.jpg"
    recipe_1.images = [mock_image]

    # No title, no images, long raw text
    long_text = "To jest bardzo długi przepis na ciasto, który specjalnie ma więcej niż piętnaście słów, abyśmy mogli przetestować, czy funkcja skracająca działa poprawnie i dodaje wielokropek."
    recipe_2 = Recipe(
        id=2, 
        title=None, 
        cleaned_text=None, 
        raw_text=long_text
    )
    recipe_2.images = []

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [recipe_1, recipe_2]
    mock_db_session.execute.return_value = mock_result

    # TEST
    response = await async_client.get("/recipes/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    assert data[0]["id"] == 1
    assert data[0]["title"] == "Zupa pomidorowa"
    assert data[0]["thumbnail_url"] == "/uploads/zupa.jpg"
    assert data[0]["short_text"] == "Pyszna zupa z pomidorów."

    assert data[1]["id"] == 2
    assert data[1]["title"] == "Bez tytułu"
    assert data[1]["thumbnail_url"] == "/no_image_thumbnail.png"
    
    expected_short_text = "To jest bardzo długi przepis na ciasto, który specjalnie ma więcej niż piętnaście słów, abyśmy..."
    assert data[1]["short_text"] == expected_short_text

@pytest.mark.asyncio
async def test_get_recipe_not_found(async_client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/recipes/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

@pytest.mark.asyncio
async def test_get_recipe_success(async_client, mock_db_session):
    fake_recipe = Recipe(id=1, title="Testowy Przepis", raw_text="Składniki...")
    fake_recipe.images = []
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_recipe
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/recipes/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Testowy Przepis"

@pytest.mark.asyncio
@patch("app.api.recipes.process_recipe.delay")
@patch("app.api.recipes.save_upload", new_callable=AsyncMock)
async def test_upload_recipe(mock_save_upload, mock_process_delay, async_client, mock_db_session):
    mock_save_upload.return_value = "/fake/path/image.jpg"
    
    async def mock_flush(*args, **kwargs):
        for call in mock_db_session.add.call_args_list:
            instance = call[0][0]
            if isinstance(instance, Recipe):
                instance.id = 42

    mock_db_session.flush.side_effect = mock_flush

    files = {"file": ("test_recipe.jpg", b"fake image content", "image/jpeg")}
    response = await async_client.post("/recipes/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["recipe_id"] == 42
    mock_save_upload.assert_awaited_once()
    assert mock_db_session.add.call_count == 2  # Recipe and RecipeImage
    mock_db_session.flush.assert_awaited_once()
    mock_db_session.commit.assert_awaited_once()
    mock_process_delay.assert_called_once_with(42, "/fake/path/image.jpg")

@pytest.mark.asyncio
async def test_search_recipes(async_client, mock_db_session):
    recipe_1 = Recipe(id=1, title="Ciasto marchewkowe")
    recipe_2 = Recipe(id=2, title="Ciasto czekoladowe")

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [recipe_1, recipe_2]
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/recipes/search/?q=ciasto")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    assert data[0] == {"id": 1, "title": "Ciasto marchewkowe"}
    assert data[1] == {"id": 2, "title": "Ciasto czekoladowe"}
    
    mock_db_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_recipe_not_found(async_client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    payload = {"title": "Nowy tytuł"}
    response = await async_client.put("/recipes/999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    mock_db_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_update_recipe_success(async_client, mock_db_session):
    fake_recipe = Recipe(
        id=1, 
        title="Stary tytuł", 
        cleaned_text="Stary tekst",
        status="new"
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_recipe
    mock_db_session.execute.return_value = mock_result

    payload = {
        "title": "Zaktualizowany tytuł",
        "cleaned_text": "Zaktualizowany tekst",
        "structured": {"skladniki": ["woda", "maka"]}
    }
    response = await async_client.put("/recipes/1", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "updated"}
    assert fake_recipe.title == "Zaktualizowany tytuł"
    assert fake_recipe.cleaned_text == "Zaktualizowany tekst"
    assert fake_recipe.structured == {"skladniki": ["woda", "maka"]}
    assert fake_recipe.status == "new" 

    mock_db_session.commit.assert_awaited_once()
