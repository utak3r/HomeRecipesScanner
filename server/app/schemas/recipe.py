from pydantic import BaseModel
from typing import Optional


class RecipeImageOut(BaseModel):
    id: int
    url: str

    class Config:
        from_attributes = True


class RecipeOut(BaseModel):
    id: int
    title: Optional[str]
    structured: Optional[dict]
    images: list[RecipeImageOut]
    status: str

    class Config:
        from_attributes = True


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    structured: Optional[dict] = None


class TagRequest(BaseModel):
    tags: list[str]


class RecipeListOut(BaseModel):
    id: int
    title: str
    thumbnail_url: str
    short_text: str
    status: str

    class Config:
        from_attributes = True


class TagOut(BaseModel):
    id: int
    name: str
    recipe_count: int

    class Config:
        from_attributes = True

