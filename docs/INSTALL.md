# Установка и запуск

Требования:

- Python 3.10+ (рекомендуется 3.11)
- Виртуальное окружение (venv)

Шаги локальной установки:

1. Клонируйте репозиторий и перейдите в корень проекта:
```
git clone <repo-url>
cd project_recommender_system
```

2. Создайте виртуальное окружение и установите зависимости:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. (Опционально) Установите дополнительные зависимости для ML (sentence-transformers и joblib), если планируете запускать ML-модуль:
```
pip install sentence-transformers joblib numpy pandas faiss-cpu
```

4. Инициализация базы и запуск приложения:
```
# запустить приложение (локально)
python run.py

# или напрямую через uvicorn (без autoreload/с reload)
./app/.venv/bin/uvicorn app.main:app --reload --port 8001
```

Примечания:
- По умолчанию используется SQLite (строка подключения в `app/core/config.py`).
- Админ-панель (sqladmin) инициализируется при старте приложения через `app.db.admin.setup_admin(app)`; открывается по `/admin`.
