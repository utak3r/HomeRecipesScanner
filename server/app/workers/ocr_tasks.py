import os
import asyncio
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal, engine
from app.db.models.recipe import Recipe
from app.workers.ocr_pipeline import run_ocr_pipeline

logger = get_task_logger(__name__)

@celery_app.task
def process_recipe(recipe_id: int, image_path: str):
    logger.info(f'celery_app.task calling process_recipe with params {recipe_id}, {image_path}')
    asyncio.run(_pipeline(recipe_id, image_path))

async def _pipeline(recipe_id: int, image_path: str):
    try:
        async with AsyncSessionLocal() as db:
            try:
                recipe = await db.get(Recipe, recipe_id)

                if not recipe:
                    raise ValueError(f"Recipe {recipe_id} not found")

                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"Image not found: {image_path}")

                logger.info(f'Processing recipe {recipe_id} with an image {image_path}')

                recipe.status = "processing"
                await db.commit()

                result = run_ocr_pipeline(image_path)

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
                logger.error(f"Error processing recipe {recipe_id}: {str(e)}")
                await db.rollback()
                
                recipe = await db.get(Recipe, recipe_id)
                if recipe:
                    recipe.status = "failed"
                    await db.commit()
                raise e
    finally:
        # Clear the connections pool!
        await engine.dispose()
