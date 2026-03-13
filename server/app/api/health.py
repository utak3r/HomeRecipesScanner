from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.deps import get_db
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check():
    return {"status": "ok"}

@router.get("/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/celery")
async def celery_health_check():
    try:
        inspect = celery_app.control.inspect()
        ping_result = inspect.ping()
        if ping_result:
            return {"status": "ok", "celery": "connected", "ping": ping_result}
        else:
            return {"status": "error", "celery": "no_workers"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
