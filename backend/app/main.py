from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.health import router as health_router
from app.api.v1.businesses import router as businesses_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.payments import router as payments_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import Business, Vendor  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Local development only. Use Alembic migrations before production.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description=(
        "Cross-border SME payments orchestration MVP. "
        "Sandbox-first; no real-money transfers in local mode."
    ),
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(health_router)
app.include_router(
    businesses_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    vendors_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["root"])
async def root():
    return FileResponse("app/static/index.html")

app.include_router(
    payments_router,
    prefix=settings.api_v1_prefix,
)
