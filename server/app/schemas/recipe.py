from pydantic import BaseModel, HttpUrl
from typing import Optional


class RecipeUrlRequest(BaseModel):
    url: HttpUrl


class RecipeImageOut(BaseModel):
    id: int
    url: str

    class Config:
        from_attributes = True


class TagBasicOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class RecipeOut(BaseModel):
    id: int
    title: Optional[str]
    structured: Optional[dict]
    images: list[RecipeImageOut]
    status: str
    source: str
    tags: list[TagBasicOut] = []

    class Config:
        from_attributes = True


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    full_text: Optional[str] = None
    structured: Optional[dict] = None


class TagRequest(BaseModel):
    tags: list[str]


class RecipeListOut(BaseModel):
    id: int
    title: str
    thumbnail_url: str
    short_text: str
    status: str
    source: str
    tags: list[TagBasicOut] = []


    class Config:
        from_attributes = True


class TagOut(BaseModel):
    id: int
    name: str
    recipe_count: int

    class Config:
        from_attributes = True

