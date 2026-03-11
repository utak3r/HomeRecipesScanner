from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db
from app.schemas.recipe import RecipeOut, RecipeUpdate, RecipeListOut
from typing import List
from sqlalchemy.orm import selectinload
from app.services.storage import save_upload
from app.db.models.recipe import Recipe
from app.db.models.image import RecipeImage
from app.db.models.tag import Tag
from app.workers.ocr_tasks import process_recipe

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("/", response_model=List[RecipeListOut])
async def list_recipes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recipe).options(selectinload(Recipe.images)).order_by(Recipe.created_at.desc())
    )
    recipes = result.scalars().all()
    
    response = []
    for r in recipes:
        if r.images:
            img_url = r.images[0].url
            if img_url.startswith("/uploads/"):
                thumbnail_url = img_url.replace("/uploads/", "/uploads/thumbs/", 1)
            else:
                thumbnail_url = img_url
        else:
            thumbnail_url = "/static/no_image_thumbnail.png"
        
        text_source = r.full_text or ""
        words = text_source.split()
        short_text = " ".join(words[:15]) + ("..." if len(words) > 15 else "")
        status = r.status
        
        response.append({
            "id": r.id,
            "title": r.title or "Bez tytułu",
            "thumbnail_url": thumbnail_url,
            "short_text": short_text,
            "status": status
        })
    return response


@router.post("/upload")
async def upload_recipe(files: list[UploadFile] = File(...), db: AsyncSession = Depends(get_db)):

    recipe = Recipe(status="processing")
    db.add(recipe)
    await db.flush()

    file_paths = []

    for index, file in enumerate(files, start=1):
        path = await save_upload(file)
        file_paths.append(path)

        image = RecipeImage(
            recipe_id=recipe.id,
            file_path=path,
            image_type="scan",
            page_number=index
        )
        db.add(image)

    await db.commit()

    process_recipe.delay(recipe.id, file_paths)

    return {
        "recipe_id": recipe.id,
        "files_count": len(file_paths),
        "status": "processing"
    }

@router.get("/{recipe_id}", response_model=RecipeOut)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recipe).options(selectinload(Recipe.images)).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(404)

    return recipe

@router.get("/search/")
async def search_recipes(q: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Recipe).where(
        Recipe.search_vector.op("@@")(
            func.plainto_tsquery("polish", q)
        )
    )

    result = await db.execute(stmt)
    recipes = result.scalars().all()

    return [
        {"id": r.id, "title": r.title}
        for r in recipes
    ]

@router.put("/{recipe_id}")
async def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(404)

    for field, value in data.model_dump(exclude_none=True).items():
        if field == "images":
            continue
        setattr(recipe, field, value)

    await db.commit()

    return {"status": "updated"}

@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(404)

    await db.delete(recipe)
    await db.commit()

    return {"status": "deleted"}

@router.post("/{recipe_id}/images")
async def add_image(
    recipe_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    path = await save_upload(file)

    image = RecipeImage(
        recipe_id=recipe_id,
        file_path=path,
        image_type="scan"
    )

    db.add(image)
    await db.commit()

    return {"status": "added"}

@router.get("/{recipe_id}/status")
async def get_status(recipe_id: int, db: AsyncSession = Depends(get_db)):
    recipe = await db.get(Recipe, recipe_id)
    return {"status": recipe.status}

@router.post("/{recipe_id}/reprocess")
async def reprocess_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recipe).options(selectinload(Recipe.images)).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if not recipe.images:
        raise HTTPException(status_code=400, detail="No images attached to this recipe")

    recipe.status = "processing"
    await db.commit()

    file_paths = [img.file_path for img in recipe.images]
    process_recipe.delay(recipe.id, file_paths)

    return {
        "recipe_id": recipe.id,
        "files_count": len(file_paths),
        "status": "processing"
    }

@router.get("/by-tag/{tag_name}", response_model=List[RecipeListOut])
async def list_recipes_by_tag(tag_name: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Recipe)
        .join(Recipe.tags)
        .where(func.lower(Tag.name) == tag_name.lower())
        .options(selectinload(Recipe.images))
        .order_by(Recipe.created_at.desc())
    )
    
    result = await db.execute(stmt)
    recipes = result.scalars().all()
    
    response = []
    for r in recipes:
        if r.images:
            img_url = r.images[0].url
            thumbnail_url = img_url.replace("/uploads/", "/uploads/thumbs/", 1) if img_url.startswith("/uploads/") else img_url
        else:
            thumbnail_url = "/static/no_image_thumbnail.png"
        
        text_source = r.full_text or ""
        words = text_source.split()
        short_text = " ".join(words[:15]) + ("..." if len(words) > 15 else "")
        
        response.append({
            "id": r.id,
            "title": r.title or "Bez tytułu",
            "thumbnail_url": thumbnail_url,
            "short_text": short_text
        })
    
    return response
