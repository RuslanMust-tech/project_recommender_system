# Архитектура и структура проекта

Краткое описание модулей:

- `app/main.py` — точка входа FastAPI-приложения; подключает роутеры, статические файлы и админ-панель.
- `app/api/` — REST API роутеры: `api_v1.py` собирает роутеры для `users`, `dishes`, `orders`, `recommendations` и `front`.
- `app/db/` — модели SQLAlchemy и утилиты для работы с базой (`session.py`, `base.py`, `admin.py`).
- `app/crud/` — базовый CRUD (`BaseCRUD`) и конкретные реализации для моделей.
- `app/schemas/` — Pydantic-схемы для валидации запросов/ответов API.
- `app/ml/` — модуль машинного обучения: компоненты:
  - `embedding.py` — обёртка над sentence-transformers
  - `index_loader.py` — загрузка индексов/эмбеддингов/источников
  - `feature_extractor.py` — сбор признаков для модели
  - `predictor.py` — загрузка обученной модели (joblib) и прогноз
  - `pipeline.py` — пайплайн предсказаний для последовательностей заказов
  - `api.py` — самостоятельный FastAPI-приложение для предсказаний (может быть подключено внутрь основного сервера)

DB-модель (основные таблицы):

- `food_catalog` (`FoodItem`): id, category, name, pieces, weight_g, composition (JSON), proteins_g, fats_g, carbs_g, calories_kcal, price_rub
- `Order` (`Order`): id, order_id, user_id (FK User.id), food_id (FK food_catalog.id)
- `User` (`User`): id, phone_number

Админ-панель:
- В `app/db/admin.py` используется `sqladmin` для создания админ-интерфейса. При старте вызывается `setup_admin(app)`.

ML-пайплайн (как работают предсказания):

1. `PredictionPipeline.run` получает таблицу заказов (phone, order, time)
2. Для каждой пары (предыдущие заказы, текущий заказ) строится запрос через `QueryBuilder` (заготовка в проекте)
3. `Predictor` использует `FeatureExtractor` и `IndexLoader` для получения признаков и затем загруженную sklearn-модель (`rf_model.pkl`) для предсказания
4. Результат — предсказанные товары (строка, декодируемая `label_encoder`)

Где искать обученные модели:
- По умолчанию `Predictor` ожидает директорию `ml/rag_order_model_custom` с файлами: `rf_model.pkl`, `scaler.pkl`, `label_encoder.pkl`, `indices.pkl`, `sources.pkl`, `source_embeddings.pkl`.

Рекомендации и дальнейшие улучшения:
- Составить OpenAPI-спецификацию/Swagger (FastAPI автогенерирует её, доступна по `/docs`/`/redoc`).
- Добавить тесты для API и ML-пайплайна.
- Добавить сценарии по загрузке/обновлению индексов ML и инструкции по подготовке данных.
