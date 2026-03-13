import time
import uuid
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger("fastapi")

class StructlogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else "unknown"
        )
        
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id            
            process_time = time.perf_counter() - start_time
            
            logger.info(
                "request_finished",
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2)
            )
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.exception(
                "request_failed",
                error=str(e),
                process_time_ms=round(process_time * 1000, 2)
            )
            raise e
