from pydantic import BaseModel
from typing import List, Optional


class RecipeImageOut(BaseModel):
    id: int
    url: str

    class Config:
        from_attributes = True


class RecipeOut(BaseModel):
    id: int
    title: Optional[str]
    raw_text: Optional[str]
    cleaned_text: Optional[str]
    structured: Optional[dict]
    images: List[RecipeImageOut]

    class Config:
        from_attributes = True


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    cleaned_text: Optional[str] = None
    structured: Optional[dict] = None
    images: Optional[List[RecipeImageOut]] = None


class TagRequest(BaseModel):
    tags: List[str]


class RecipeListOut(BaseModel):
    id: int
    title: str
    thumbnail_url: str
    short_text: str

    class Config:
        from_attributes = True
