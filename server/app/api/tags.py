from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.schemas.recipe import TagRequest
from app.db.models.recipe import Recipe
from app.db.models.tag import Tag

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/{recipe_id}")
async def add_tags(recipe_id: int, data: TagRequest, db: AsyncSession = Depends(get_db)):
    recipe = await db.get(Recipe, recipe_id)

    for name in data.tags:
        result = await db.execute(select(Tag).where(Tag.name == name))
        tag = result.scalar_one_or_none()

        if not tag:
            tag = Tag(name=name)
            db.add(tag)

        recipe.tags.append(tag)

    await db.commit()

    return {"status": "ok"}
