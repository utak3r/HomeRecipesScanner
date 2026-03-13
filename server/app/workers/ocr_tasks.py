import os
import asyncio
from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal, engine
from app.db.models.recipe import Recipe
from app.db.models.image import RecipeImage
from app.workers.ocr_pipeline import run_ocr_pipeline
import structlog

logger = structlog.get_logger("celery")

@celery_app.task(bind=True)
def process_recipe(self, recipe_id: int, file_paths: list[str], request_id: str = None):
    if request_id:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
    logger.info("processing_started", recipe_id=recipe_id, files_count=len(file_paths))
    asyncio.run(_pipeline(recipe_id, file_paths))

async def _pipeline(recipe_id: int, file_paths: list[str]):
    try:
        async with AsyncSessionLocal() as db:
            try:
                recipe = await db.get(Recipe, recipe_id)
                if not recipe:
                    raise ValueError(f"Recipe {recipe_id} not found")

                # to be sure OCR gets pages in proper order,
                # we're getting them from databse, sorted by page number
                result = await db.execute(
                    select(RecipeImage)
                    .where(RecipeImage.recipe_id == recipe_id)
                    .order_by(RecipeImage.page_number.asc())
                )
                images = result.scalars().all()
                if not images:
                    raise ValueError(f"No images found for recipe {recipe_id}")
                sorted_paths = [img.file_path for img in images]

                for path in sorted_paths:
                    if not os.path.exists(path):
                        raise FileNotFoundError(f"Image not found: {path}")

                logger.info("db_metadata_loaded", recipe_id=recipe_id)
                recipe.status = "processing"
                await db.commit()

                result = run_ocr_pipeline(sorted_paths)

                if "error" in result:
                    raise RuntimeError(f"Krytyczny błąd systemu OCR: {result['error']}")
                if result.get("title") == "Błąd przetwarzania":
                    raise RuntimeError(f"Błąd AI: {result.get('notes')}")
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
                    recipe.cleaned_text = flat_cleaned_text.strip()
                    recipe.structured = result
                    recipe.status = "processed"
                    await db.commit()

                return {
                    "status": "success",
                    "recipe_id": recipe_id
                }

            except Exception as e:
                logger.exception("processing_failed", recipe_id=recipe_id, error=str(e))
                await db.rollback()
                
                recipe = await db.get(Recipe, recipe_id)
                if recipe:
                    recipe.status = "failed"
                    await db.commit()
                raise e
    finally:
        # Clear the connections pool!
        await engine.dispose()
