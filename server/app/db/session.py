from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os
import urllib.parse
import structlog

logger = structlog.get_logger("db")
load_dotenv()

USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")
DBNAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql+asyncpg://{USER}:{urllib.parse.quote_plus(PASSWORD)}@{HOST}:{PORT}/{DBNAME}"
#logger.info("DATABASE_URL", DATABASE_URL=DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)
