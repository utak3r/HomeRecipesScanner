from sqlalchemy import (
    String, Text, DateTime, func, Index
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

    raw_text: Mapped[str | None] = mapped_column(Text)

    cleaned_text: Mapped[str | None] = mapped_column(Text)

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
