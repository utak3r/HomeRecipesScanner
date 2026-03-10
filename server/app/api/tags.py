from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.schemas.recipe import TagRequest, TagOut
from app.db.models.recipe import Recipe
from app.db.models.tag import Tag, recipe_tags

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(
            Tag.id,
            Tag.name,
            func.count(recipe_tags.c.recipe_id).label("recipe_count")
        )
        .outerjoin(recipe_tags)
        .group_by(Tag.id)
        .order_by(func.count(recipe_tags.c.recipe_id).desc())
    )

    result = await db.execute(stmt)

    return [
        {"id": row.id, "name": row.name, "recipe_count": row.recipe_count}
        for row in result
    ]

@router.post("/{recipe_id}")
async def add_tags(recipe_id: int, data: TagRequest, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(
        select(Recipe).options(selectinload(Recipe.tags)).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    for name in data.tags:
        tag_result = await db.execute(select(Tag).where(Tag.name == name))
        tag = tag_result.scalar_one_or_none()

        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        
        if tag not in recipe.tags:
            recipe.tags.append(tag)

    await db.commit()
    return {"status": "ok", "tags_added": data.tags}

@router.delete("/{recipe_id}/{tag_id}")
async def remove_tag_from_recipe(
    recipe_id: int, 
    tag_id: int, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Recipe)
        .options(selectinload(Recipe.tags))
        .where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    tag_to_remove = next((t for t in recipe.tags if t.id == tag_id), None)

    if not tag_to_remove:
        raise HTTPException(status_code=404, detail="Tag not associated with this recipe")
    recipe.tags.remove(tag_to_remove)
    
    await db.commit()
    return {"status": "removed"}

@router.delete("/{tag_id}")
async def remove_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Tag)
        .options(selectinload(Tag.recipes))
        .where(Tag.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag.recipes:
        raise HTTPException(
            status_code=400, 
            detail=f"Tag '{tag.name}' jest używany w {len(tag.recipes)} przepisach. Nie można go usunąć."
        )

    await db.delete(tag)
    await db.commit()
    
    return {"status": "deleted"}

@router.put("/{tag_id}")
async def edit_tag(tag_id: int, data: TagRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if not data.tags or not data.tags[0].strip():
        raise HTTPException(status_code=400, detail="Tag name cannot be empty")

    new_name = data.tags[0].strip()
    existing_tag = await db.execute(
        select(Tag).where(Tag.name == new_name)
    )
    if existing_tag.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Tag '{new_name}' already exists")

    tag.name = new_name
    await db.commit()
    
    return {"status": "updated", "tag_id": tag.id, "new_name": tag.name}
