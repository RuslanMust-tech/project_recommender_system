# скрипт генерации рандомных заказов, для запуска:
# uv run --project app python3 app/scripts/seed_orders.py --rows 500 --users 20

import argparse
import random
import sys
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import func

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base
from app.db.models.FoodItem import FoodItem
from app.db.models.Order import Order
from app.db.models.User import User
from app.db.session import SessionLocal, engine


DEMO_PHONE_START = 7_900_000_0000


def has_any(text: str, words: list[str]) -> bool:
    lowered = text.lower()
    return any(word.lower() in lowered for word in words)


def pick(items: list[FoodItem], fallback: list[FoodItem]) -> FoodItem:
    return random.choice(items or fallback)


def find_foods(foods: list[FoodItem], predicate: Callable[[FoodItem], bool]) -> list[FoodItem]:
    return [food for food in foods if predicate(food)]


def ensure_demo_users(db, count: int) -> list[User]:
    users = db.query(User).all()
    if len(users) >= count:
        return users

    existing_phones = {user.phone_number for user in users}
    for offset in range(count - len(users)):
        phone = DEMO_PHONE_START + offset
        if phone not in existing_phones:
            db.add(User(phone_number=phone))

    db.commit()
    return db.query(User).all()


def build_basket(main: FoodItem, foods: list[FoodItem], max_size: int) -> list[FoodItem]:
    category_text = f"{main.category} {main.name}"
    sauces = find_foods(foods, lambda food: has_any(f"{food.category} {food.name}", ["соус", "васаби", "имбирь"]))
    drinks = find_foods(foods, lambda food: has_any(f"{food.category} {food.name}", ["добрый", "морс", "сок", "чай", "aqua", "cola"]))
    sides = find_foods(foods, lambda food: has_any(f"{food.category} {food.name}", ["картофель", "наггетсы", "крылья", "гренки", "палочки"]))
    desserts = find_foods(foods, lambda food: has_any(f"{food.category} {food.name}", ["чизкейк", "донат", "тирамису", "мусс", "десерт"]))
    rolls = find_foods(foods, lambda food: has_any(f"{food.category} {food.name}", ["ролл", "они", "суши", "сет"]))
    pizzas = find_foods(foods, lambda food: has_any(f"{food.category} {food.name}", ["пицца", "пепперони", "маргарита"]))

    basket = [main]

    if has_any(category_text, ["ролл", "они", "суши", "сет"]):
        if random.random() < 0.75:
            basket.append(pick(sauces, foods))
        if random.random() < 0.35:
            basket.append(pick(drinks, foods))
        if random.random() < 0.25:
            basket.append(pick(rolls, foods))
    elif has_any(category_text, ["пицца", "пепперони", "маргарита"]):
        if random.random() < 0.70:
            basket.append(pick(drinks, foods))
        if random.random() < 0.45:
            basket.append(pick(sauces, foods))
        if random.random() < 0.25:
            basket.append(pick(pizzas, foods))
    elif has_any(category_text, ["бургер", "пита", "крылья", "наггетсы"]):
        if random.random() < 0.70:
            basket.append(pick(sides, foods))
        if random.random() < 0.60:
            basket.append(pick(drinks, foods))
        if random.random() < 0.35:
            basket.append(pick(sauces, foods))
    else:
        if random.random() < 0.45:
            basket.append(pick(drinks, foods))
        if random.random() < 0.30:
            basket.append(pick(desserts, foods))
        if random.random() < 0.25:
            basket.append(pick(sauces, foods))

    random.shuffle(basket)
    return basket[:max_size]


def seed_orders(rows_target: int, users_count: int, max_items: int, seed: int) -> None:
    random.seed(seed)
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        foods = db.query(FoodItem).all()
        if not foods:
            raise RuntimeError("food_catalog пустой: сначала загрузите блюда в БД")

        users = ensure_demo_users(db, users_count)
        addon_words = ["соус", "васаби", "имбирь", "палочки", "вилка", "ложка"]
        mains = find_foods(foods, lambda food: not has_any(f"{food.category} {food.name}", addon_words))
        if not mains:
            mains = foods

        next_order_id = (db.query(func.max(Order.order_id)).scalar() or 0) + 1
        created_rows = 0
        created_orders = 0

        while created_rows < rows_target:
            user = random.choice(users)
            remaining = rows_target - created_rows
            basket_size = random.randint(1, min(max_items, remaining))
            main = random.choice(mains)
            basket = build_basket(main, foods, basket_size)

            for food in basket:
                db.add(Order(order_id=next_order_id, user_id=user.id, food_id=food.id))
                created_rows += 1

            next_order_id += 1
            created_orders += 1

        db.commit()
        print(f"Created {created_rows} Order rows in {created_orders} synthetic orders")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic food delivery order history.")
    parser.add_argument("--rows", type=int, default=500, help="How many Order rows to create")
    parser.add_argument("--users", type=int, default=80, help="Minimum demo users count")
    parser.add_argument("--max-items", type=int, default=5, help="Maximum items per synthetic order")
    parser.add_argument("--seed", type=int, default=21, help="Random seed")
    args = parser.parse_args()

    seed_orders(args.rows, args.users, args.max_items, args.seed)


if __name__ == "__main__":
    main()
