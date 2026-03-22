import os
import asyncio
import urllib.request
import tempfile
import uuid
from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal, engine
from app.db.models.recipe import Recipe
from app.db.models.image import RecipeImage
from app.workers.url_pipeline import run_url_pipeline
import structlog

logger = structlog.get_logger("celery")

def download_image_to_temp(url: str) -> str:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        data = response.read()
        
    fd, temp_path = tempfile.mkstemp(suffix=".jpg")
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
    return temp_path

@celery_app.task(bind=True)
def process_url_recipe(self, recipe_id: int, url: str, request_id: str = None):
    if request_id:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
    logger.info("url_processing_started", recipe_id=recipe_id, url=url)
    asyncio.run(_pipeline(recipe_id, url))

async def _pipeline(recipe_id: int, url: str):
    try:
        async with AsyncSessionLocal() as db:
            try:
                recipe = await db.get(Recipe, recipe_id)
                if not recipe:
                    raise ValueError(f"Recipe {recipe_id} not found")

                result = run_url_pipeline(url)

                if "error" in result:
                    raise RuntimeError(f"Krytyczny błąd systemu URL: {result['error']}")
                if result.get("title") == "Błąd przetwarzania":
                    raise RuntimeError(f"Błąd AI: {result.get('notes')}")

                image_url = result.get("image_url")
                if image_url:
                    try:
                        temp_img_path = download_image_to_temp(image_url)
                        
                        # Upload to storage
                        from app.services.storage import get_storage
                        storage = get_storage()
                        
                        # We need to simulate a file object with async read()
                        class MockUploadFile:
                            def __init__(self, filename, content):
                                self.filename = filename
                                self.content = content
                            async def read(self):
                                return self.content

                        with open(temp_img_path, "rb") as f:
                            content = f.read()
                            upload_file = MockUploadFile(f"url_{uuid.uuid4().hex[:8]}.jpg", content)
                            saved_path = await storage.save(upload_file)

                        # Create RecipeImage
                        recipe_img = RecipeImage(
                            recipe_id=recipe_id,
                            file_path=saved_path,
                            image_type="url_image",
                            page_number=1
                        )
                        db.add(recipe_img)
                        await db.flush()
                        
                        os.unlink(temp_img_path)
                    except Exception as e:
                        logger.warning("failed_to_download_url_image", error=str(e), image_url=image_url)

                ingredients_list = [f"- {i.get('name', '')} {i.get('amount', '')}".strip() for i in result.get("ingredients", [])]
                ingredients_text = "\n".join(ingredients_list)
                
                steps_list = [f"{idx+1}. {step}" for idx, step in enumerate(result.get("steps", []))]
                steps_text = "\n".join(steps_list)
                
                flat_cleaned_text = f"{result.get('title', 'Brak tytułu')}\n\n" \
                                    f"SKŁADNIKI:\n{ingredients_text}\n\n" \
                                    f"PRZYGOTOWANIE:\n{steps_text}\n\n" \
                                    f"UWAGI:\n{result.get('notes', '')}"

                recipe = await db.get(Recipe, recipe_id)
                if recipe:
                    recipe.title = result.get("title")
                    recipe.full_text = flat_cleaned_text.strip()
                    recipe.structured = result
                    recipe.status = "processed"
                    await db.commit()

                return {
                    "status": "success",
                    "recipe_id": recipe_id
                }

            except Exception as e:
                logger.exception("url_processing_failed", recipe_id=recipe_id, error=str(e))
                await db.rollback()
                
                recipe = await db.get(Recipe, recipe_id)
                if recipe:
                    recipe.status = "failed"
                    await db.commit()
                raise e
    finally:
        await engine.dispose()
