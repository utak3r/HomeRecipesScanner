from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.api import recipes, tags, health
from app.utils.logger import setup_logging
from app.utils.middleware import StructlogMiddleware

# In production, set json_format=True
setup_logging(level="INFO", json_format=False)

app = FastAPI(title="Baza przepisów kulinarnych")
app.add_middleware(StructlogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(recipes.router)
app.include_router(tags.router)
app.include_router(health.router)
