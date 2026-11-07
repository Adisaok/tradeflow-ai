from fastapi import APIRouter
from sqlalchemy import text
from redis.asyncio import Redis
from app.core.config import settings
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def health():
    return {"status": "ok", "service": settings.app_name, "environment": settings.app_env}


@router.get("/health/ready", summary="Readiness probe")
async def readiness():
    checks = {"database": "unknown", "redis": "unknown"}
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
    try:
        client = Redis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        await client.aclose()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"
    ready = all(value == "ok" for value in checks.values())
    return {"status": "ready" if ready else "not_ready", "checks": checks}
