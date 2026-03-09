import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ocr_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["app.workers.ocr_tasks"]
)

celery_app.conf.task_routes = {
    "app.workers.ocr_tasks.*": {"queue": "ocr"}
}

celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1, # Only one task at once
    task_acks_late=True,          # ACK task being done
    result_expires=3600,          # Results expire after an hour
)
