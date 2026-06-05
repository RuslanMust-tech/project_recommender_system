# API

Базовый префикс всех API маршрутов: `/api/v1`

1) Роутеры API

- `/api/v1/users` — CRUD для пользователей (см. `app/api/users.py`). Дополнительно:
  - `GET /api/v1/users/search?phone_number=<int>` — поиск по телефону

- `/api/v1/dishes` — CRUD для блюд (см. `app/api/dishes.py`). Дополнительно:
  - `GET /api/v1/dishes/search/by_name?name=<str>` — поиск по названию
  - `GET /api/v1/dishes/search/by_category?category=<str>` — поиск по категории

- `/api/v1/orders` — CRUD для заказов (см. `app/api/orders.py`).

- `/api/v1/recommendations` — эндпоинты системы рекомендаций (пустые / заготовка) (`app/api/recommendations.py`).

- Фронтенд-ориентированные маршруты (без префикса `/api/v1` — они подключены как `front`):
  - `GET /user/{phone}` — получить пользователя или создать его временно
  - `GET /cart/{phone}` — получить временную корзину
  - `POST /cart` — сохранить временную корзину (payload: phone + cart)
  - `DELETE /cart/{phone}` — очистить корзину
  - `GET /user/{phone}/orders` — получить историю заказов
  - `POST /order` — создать новый заказ (сохранение в БД)
  - `GET /order/{phone}/{order_id}` — получить конкретный заказ
  - `GET /stats` — получить статистику
  - `GET /health` — проверка здоровья приложения

2) ML API (отдельный модуль `app/ml/api.py`)

- `POST /predict` — принимает JSON с полем `orders` (список заказов), возвращает предсказанные следующие товары.
  - Входные схемы: `OrderItem`, `InferenceRequest` (см. `app/ml/api.py`).

3) Примеры запросов

Получить здоровье сервера:
```
curl http://127.0.0.1:8001/health
```

Создать корзину (пример):
```
curl -X POST http://127.0.0.1:8001/cart -H "Content-Type: application/json" -d '{"phone":"+7 999 111 22 33","cart":[{"name":"Яблоко","price":50,"quantity":2}] }'
```

Вызов ML-предсказания (локальный сервер ML в `app/ml/api.py`):
```
curl -X POST http://127.0.0.1:8001/predict -H "Content-Type: application/json" -d '{"orders": [{"user_id": 79991112233, "order_id": 1, "items": ["Яблоко","Банан"]}] }'
```
