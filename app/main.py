from fastapi import FastAPI

from app.api.api_v1 import api_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1")
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "app is running"}


@app.get("/health", tags=["root"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
