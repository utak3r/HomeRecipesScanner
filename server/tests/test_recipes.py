import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock, ANY

from app.main import app
from app.api.deps import get_db
from app.db.models.recipe import Recipe
from app.db.models.tag import Tag
from app.services.storage import get_storage, StorageService

# --- Mocking Fixtures ---

@pytest.fixture
def mock_storage():
    storage = MagicMock(spec=StorageService)
    storage.get_url.side_effect = lambda x: f"/uploads/{x}"
    return storage

@pytest.fixture
def mock_db_session():
    """Mocking AsyncSession from SQLAlchemy"""
    session = AsyncMock()
    return session

@pytest.fixture
def override_deps(mock_db_session, mock_storage):
    async def _get_db_override():
        yield mock_db_session
    
    async def _get_storage_override():
        return mock_storage

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_storage] = _get_storage_override
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(override_deps):
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
        full_text="Pyszna zupa z pomidorów.",
        status="new"
    )


    mock_image = MagicMock()
    mock_image.file_path = "zupa.jpg"
    recipe_1.images = [mock_image]

    # No title, no images, long raw text
    long_text = "To jest bardzo długi przepis na ciasto, który specjalnie ma więcej niż piętnaście słów, abyśmy mogli przetestować, czy funkcja skracająca działa poprawnie i dodaje wielokropek."
    recipe_2 = Recipe(
        id=2, 
        title=None, 
        full_text=long_text,
        status="processing"
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
    assert data[0]["thumbnail_url"] == "/uploads/thumbs/zupa.jpg"

    assert data[0]["short_text"] == "Pyszna zupa z pomidorów."

    assert data[1]["id"] == 2
    assert data[1]["title"] == "Bez tytułu"
    assert data[1]["thumbnail_url"] == "/static/no_image_thumbnail.png"

    
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
    fake_recipe = Recipe(id=1, title="Testowy Przepis", full_text="Składniki...", status="processed")
    
    mock_image = MagicMock()
    mock_image.id = 10
    mock_image.file_path = "przepis.jpg"
    fake_recipe.images = [mock_image]
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_recipe
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/recipes/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Testowy Przepis"
    assert len(data["images"]) == 1
    assert data["images"][0]["url"] == "/uploads/przepis.jpg"


@pytest.mark.asyncio
@patch("app.api.recipes.process_recipe.delay")
async def test_upload_recipe_multiple_files(mock_process_delay, async_client, mock_db_session, mock_storage):
    mock_storage.save = AsyncMock(side_effect=["/path/1.jpg", "/path/2.jpg"])
    
    async def mock_flush(*args, **kwargs):
        for call in mock_db_session.add.call_args_list:
            instance = call[0][0]
            if isinstance(instance, Recipe):
                instance.id = 100

    mock_db_session.flush.side_effect = mock_flush

    files = [
        ("files", ("page1.jpg", b"content1", "image/jpeg")),
        ("files", ("page2.jpg", b"content2", "image/jpeg"))
    ]
    response = await async_client.post("/recipes/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["recipe_id"] == 100
    
    assert mock_storage.save.await_count == 2
    assert mock_db_session.add.call_count == 3 
    
    mock_process_delay.assert_called_once_with(100, ["/path/1.jpg", "/path/2.jpg"], request_id=ANY)




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
async def test_list_recipes_by_tag_success(async_client, mock_db_session):
    tag_name = "Obiad"
    recipe = Recipe(
        id=10, 
        title="Kurczak w sosie", 
        full_text="Instrukcja gotowania obiadu...",
        status="new"
    )


    recipe.images = []

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [recipe]
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get(f"/recipes/by-tag/{tag_name}")

    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["id"] == 10
    assert data[0]["title"] == "Kurczak w sosie"
    assert data[0]["thumbnail_url"] == "/static/no_image_thumbnail.png"

    assert data[0]["short_text"] == "Instrukcja gotowania obiadu..."

@pytest.mark.asyncio
async def test_list_recipes_by_tag_empty(async_client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = []
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/recipes/by-tag/NieistniejacyTag")

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_remove_tag_success(async_client, mock_db_session):
    tag_to_remove = Tag(id=5, name="Szybkie")
    fake_recipe = Recipe(id=1, title="Test", tags=[tag_to_remove])
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_recipe
    mock_db_session.execute.return_value = mock_result

    response = await async_client.delete("/tags/1/5")

    assert response.status_code == 200
    assert response.json() == {"status": "removed"}
    assert len(fake_recipe.tags) == 0
    mock_db_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_remove_tag_not_associated(async_client, mock_db_session):
    fake_recipe = Recipe(id=1, title="Test", tags=[])
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_recipe
    mock_db_session.execute.return_value = mock_result

    response = await async_client.delete("/tags/1/99")

    assert response.status_code == 404
    assert "Tag not associated" in response.json()["detail"]

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
        full_text="Stary tekst",
        status="new"
    )


    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_recipe
    mock_db_session.execute.return_value = mock_result

    payload = {
        "title": "Zaktualizowany tytuł",
        "full_text": "Zaktualizowany tekst",
        "structured": {"skladniki": ["woda", "maka"]}
    }

    response = await async_client.put("/recipes/1", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "updated"}
    assert fake_recipe.title == "Zaktualizowany tytuł"
    assert fake_recipe.full_text == "Zaktualizowany tekst"

    assert fake_recipe.structured == {"skladniki": ["woda", "maka"]}
    assert fake_recipe.status == "new" 

    mock_db_session.commit.assert_awaited_once()
