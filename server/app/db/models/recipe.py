from sqlalchemy import (
    String, Text, DateTime, func, Index, event
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from app.db.base import Base
from datetime import datetime

class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str | None] = mapped_column(String)

    full_text: Mapped[str | None] = mapped_column(Text)

    structured: Mapped[dict | None] = mapped_column(JSONB)

    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    status: Mapped[str | None] = mapped_column(String, default="new")

    language: Mapped[str] = mapped_column(default="pl")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    images = relationship(
        "RecipeImage",
        back_populates="recipe",
        cascade="all, delete",
        order_by="RecipeImage.page_number"
    )

    tags = relationship(
        "Tag",
        secondary="recipe_tags",
        back_populates="recipes"
    )

Index(
"ix_recipe_search",
Recipe.search_vector,
postgresql_using="gin"
)

def update_full_text(target):
    if not target.structured:
        target.full_text = target.title or ""
        return
    s = target.structured
    parts = []

    title = s.get("title") or target.title
    if title:
        parts.append(title)
    
    ingredients_data = s.get("ingredients", [])
    if isinstance(ingredients_data, list):
        ing_strings = []
        for ing in ingredients_data:
            name = ing.get("name", "")
            amount = ing.get("amount", "")
            if name:
                ing_strings.append(f"{name}: {amount}" if amount else name)
        if ing_strings:
            parts.append(", ".join(ing_strings))
        
    steps = s.get("steps")
    if isinstance(steps, list):
        parts.append("\n".join(steps))
    elif steps:
        parts.append(str(steps))
    
    notes = s.get("notes")
    if notes:
        parts.append(str(notes))
    
    target.full_text = "\n".join(parts)


@event.listens_for(Recipe, 'before_insert')
@event.listens_for(Recipe, 'before_update')
def receive_before_insert_update(mapper, connection, target):
    update_full_text(target)
