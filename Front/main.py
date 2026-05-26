from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import random
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или конкретный origin фронта, например "http://127.0.0.1:5500"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Временная БД
users_db = {}

# Отдача статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

# ======================
# Models
# ======================

class CartItem(BaseModel):
    name: str
    price: int
    qty: int
    img: str = ""
    weight: str = ""


class Order(BaseModel):
    id: int
    date: str
    total: int
    payment: str
    address: str
    items: List[str]


class CartRequest(BaseModel):
    phone: str
    cart: List[CartItem]


class OrderRequest(BaseModel):
    phone: str
    order: Order


# ======================
# USER
# ======================

@app.get("/user/{phone}")
def get_user(phone: str):
    if phone not in users_db:
        users_db[phone] = {
            "phone": phone,
            "cart": [],
            "orders": []
        }

    return users_db[phone]


# ======================
# CART
# ======================

@app.get("/cart/{phone}")
def get_cart(phone: str):
    user = users_db.get(phone)

    if not user:
        return {"cart": []}

    return {"cart": user["cart"]}


@app.post("/cart")
def save_cart(data: CartRequest):
    if data.phone not in users_db:
        users_db[data.phone] = {
            "phone": data.phone,
            "cart": [],
            "orders": []
        }

    users_db[data.phone]["cart"] = [
        item.dict() for item in data.cart
    ]

    return {"message": "Корзина сохранена"}


# ======================
# ORDERS
# ======================

@app.get("/orders/{phone}")
def get_orders(phone: str):
    user = users_db.get(phone)

    if not user:
        return {"orders": []}

    return {"orders": user["orders"]}


@app.post("/order")
def create_order(data: OrderRequest):
    if data.phone not in users_db:
        users_db[data.phone] = {
            "phone": data.phone,
            "cart": [],
            "orders": []
        }

    users_db[data.phone]["orders"].append(
        data.order.dict()
    )

    users_db[data.phone]["cart"] = []

    return {
        "message": "Заказ оформлен"
    }