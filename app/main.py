from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.api_v1 import api_router
from app.core.config import get_settings
from app.db.admin import setup_admin

settings = get_settings()

# Создаем директории для статических файлов, если их нет
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

app = FastAPI(title=settings.app_name, version="0.1")

# Подключаем API роутеры
app.include_router(api_router, prefix="/api/v1")

# Настраиваем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Добавляем корневой эндпоинт для отдачи HTML из корня проекта
@app.get("/", response_class=HTMLResponse)
async def root():
    # Ищем index.html в разных местах
    index_path = Path("index.html")
    if not index_path.exists():
        index_path = Path("templates/index.html")
    if not index_path.exists():
        return HTMLResponse(content="<h1>index.html not found</h1><p>Please make sure index.html exists in the project root or templates folder.</p>", status_code=404)
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page():
    analytics_path = Path("templates/analytics.html")
    if not analytics_path.exists():
        return HTMLResponse(content="<h1>analytics.html not found</h1>", status_code=404)

    with open(analytics_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

setup_admin(app)
