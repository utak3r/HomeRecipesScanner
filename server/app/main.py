from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from app.api import recipes, tags


app = FastAPI(title="Baza przepisów kulinarnych")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(recipes.router)
app.include_router(tags.router)
