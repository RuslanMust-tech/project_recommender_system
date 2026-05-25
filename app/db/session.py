# здесь будет находиться код для работы с базой данных, включая функции для получения сессии и инициализации базы данных
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# Создаем engine
engine = create_engine(
    settings.database_url,
    echo=True,  # выводит SQL запросы в консоль (для отладки)
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """Функция для получения сессии БД (для Depends)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session():
    """Простая функция для получения сессии (без Depends)"""
    return SessionLocal()