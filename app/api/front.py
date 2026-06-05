from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.FoodItem import FoodItem
from app.db.models.Order import Order as DBOrder
from app.db.models.User import User
from app.db.session import get_db


front = APIRouter()

# Корзина пока остается временной: в текущей схеме БД нет таблицы cart/cart_items.
carts_db: dict[str, list[dict[str, Any]]] = {}


class CartItem(BaseModel):
    id: Optional[int] = None
    name: str
    price: int
    quantity: int = 1
    img: str = ""
    weight: str = ""
    type: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class OrderItem(BaseModel):
    id: Optional[int] = None
    name: str
    quantity: int = 1
    price: int
    type: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class FrontOrder(BaseModel):
    id: int
    date: str
    total: int
    payment: str
    address: str
    items: List[OrderItem]

    model_config = ConfigDict(extra="ignore")


class CartRequest(BaseModel):
    phone: str
    cart: List[CartItem]


class OrderRequest(BaseModel):
    phone: str
    order: FrontOrder


def _normalize_phone(phone: str) -> int:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if not digits:
        raise HTTPException(status_code=400, detail="Некорректный номер телефона")
    return int(digits)


def _get_or_create_user(db: Session, phone: str) -> User:
    phone_number = _normalize_phone(phone)
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user:
        return user

    user = User(phone_number=phone_number)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _user_response(user: User) -> dict[str, Any]:
    phone = str(user.phone_number)
    return {
        "id": user.id,
        "phone": phone,
        "phone_number": user.phone_number,
        "cart": carts_db.get(phone, []),
    }


def _serialize_order(order_id: int, rows: list[DBOrder]) -> dict[str, Any]:
    food_counter = Counter(row.food_id for row in rows if row.food_item)
    items = []
    total = 0

    for food_id, quantity in food_counter.items():
        food = next(row.food_item for row in rows if row.food_id == food_id and row.food_item)
        price = food.price_rub or 0
        total += price * quantity
        items.append(
            {
                "id": food.id,
                "name": food.name,
                "quantity": quantity,
                "price": price,
            }
        )

    return {
        "id": order_id,
        "date": "Дата не сохранена",
        "total": total,
        "payment": "Оплата через СБП",
        "address": "Адрес не сохранен",
        "items": items,
        "status": "Завершен",
    }


@front.get("/user/{phone}")
def get_user(phone: str, db: Session = Depends(get_db)):
    """Получить пользователя или создать его в SQLite."""
    user = _get_or_create_user(db, phone)
    return _user_response(user)


@front.get("/cart/{phone}")
def get_cart(phone: str):
    """Получить временную корзину пользователя."""
    return {"cart": carts_db.get(str(_normalize_phone(phone)), [])}


@front.post("/cart")
def save_cart(data: CartRequest):
    """Сохранить временную корзину пользователя."""
    phone = str(_normalize_phone(data.phone))
    carts_db[phone] = [item.model_dump() for item in data.cart]
    return {"message": "Корзина сохранена"}


@front.delete("/cart/{phone}")
def clear_cart(phone: str):
    """Очистить временную корзину пользователя."""
    carts_db[str(_normalize_phone(phone))] = []
    return {"message": "Корзина очищена"}


@front.get("/user/{phone}/orders")
def get_orders(phone: str, db: Session = Depends(get_db)):
    """Получить историю заказов пользователя из SQLite."""
    user = db.query(User).filter(User.phone_number == _normalize_phone(phone)).first()
    if not user:
        return {"orders": []}

    rows = (
        db.query(DBOrder)
        .filter(DBOrder.user_id == user.id)
        .order_by(DBOrder.order_id.desc(), DBOrder.id.asc())
        .all()
    )

    grouped_orders: dict[int, list[DBOrder]] = defaultdict(list)
    for row in rows:
        grouped_orders[row.order_id].append(row)

    return {
        "orders": [
            _serialize_order(order_id, order_rows)
            for order_id, order_rows in grouped_orders.items()
        ]
    }

@front.post("/order")
def create_order(data: OrderRequest, db: Session = Depends(get_db)):
    """Создать заказ: одна строка Order на одну позицию товара."""
    user = _get_or_create_user(db, data.phone)
    order_id = data.order.id or int(datetime.now().timestamp())
    created_rows = 0

    for item in data.order.items:
        # Пропускаем соусы и приборы (если не нужно сохранять)
        if item.type in {"sauce", "utensil"}:
            continue
            
        # Ищем блюдо по ID или имени
        food = None
        if item.id:
            food = db.get(FoodItem, item.id)
        if not food and item.name:
            food = db.query(FoodItem).filter(FoodItem.name == item.name).first()
            
        if not food:
            print(f"Food not found: {item}")
            continue

        quantity = max(item.quantity or 1, 1)
        # Создаём отдельную запись для каждой единицы товара
        for _ in range(quantity):
            db.add(DBOrder(
                order_id=order_id, 
                user_id=user.id, 
                food_id=food.id
            ))
            created_rows += 1

    if created_rows == 0:
        raise HTTPException(
            status_code=400,
            detail="В заказе нет позиций, которые можно сохранить в БД",
        )

    db.commit()
    
    # Очищаем временную корзину
    carts_db[str(user.phone_number)] = []

    return {"message": "Заказ оформлен", "order_id": order_id, "items_created": created_rows}

# @front.post("/order")
# def create_order(data: OrderRequest, db: Session = Depends(get_db)):
#     """Создать заказ в SQLite: одна строка Order на одну позицию товара."""
#     user = _get_or_create_user(db, data.phone)
#     order_id = data.order.id or int(datetime.now().timestamp())
#     created_rows = 0

#     for item in data.order.items:
#         if not item.id or item.type in {"sauce", "utensil"}:
#             continue

#         food = db.get(FoodItem, item.id)
#         if not food:
#             continue

#         quantity = max(item.quantity or 1, 1)
#         for _ in range(quantity):
#             db.add(DBOrder(order_id=order_id, user_id=user.id, food_id=food.id))
#             created_rows += 1

#     if created_rows == 0:
#         raise HTTPException(
#             status_code=400,
#             detail="В заказе нет позиций, которые можно сохранить в БД",
#         )

#     db.commit()
#     carts_db[str(user.phone_number)] = []

#     return {"message": "Заказ оформлен", "order_id": order_id}


@front.get("/order/{phone}/{order_id}")
def get_order(phone: str, order_id: int, db: Session = Depends(get_db)):
    """Получить конкретный заказ пользователя из SQLite."""
    user = db.query(User).filter(User.phone_number == _normalize_phone(phone)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    rows = (
        db.query(DBOrder)
        .filter(DBOrder.user_id == user.id, DBOrder.order_id == order_id)
        .order_by(DBOrder.id.asc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    return _serialize_order(order_id, rows)


@front.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Получить статистику приложения из SQLite и временных корзин."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_order_rows = db.query(func.count(DBOrder.id)).scalar() or 0
    total_orders = db.query(func.count(func.distinct(DBOrder.order_id))).scalar() or 0
    total_items_in_carts = sum(len(cart) for cart in carts_db.values())

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_order_rows": total_order_rows,
        "total_items_in_carts": total_items_in_carts,
    }


@front.get("/health")
def health_check():
    """Проверка работоспособности."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
