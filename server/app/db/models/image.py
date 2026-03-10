from sqlalchemy import ForeignKey, String, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime

class RecipeImage(Base):
    __tablename__ = "recipe_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE")
    )

    file_path: Mapped[str] = mapped_column(String)

    image_type: Mapped[str] = mapped_column(String)

    page_number: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    recipe = relationship("Recipe", back_populates="images")

    @property
    def url(self) -> str:
        if self.file_path.startswith("http"):
            return self.file_path
        return "/" + self.file_path.replace("\\", "/")
