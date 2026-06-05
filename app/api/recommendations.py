from collections import Counter, defaultdict
from itertools import combinations
from typing import Any, Iterable, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.FoodItem import FoodItem
from app.db.models.Order import Order
from app.db.models.User import User
from app.db.session import get_db


router = APIRouter()


ADDON_KEYWORDS_BY_CATEGORY = {
    "Роллы": ["соус", "васаби", "имбирь", "напит", "морс", "сок", "чай", "cola"],
    "Сеты": ["соус", "васаби", "имбирь", "напит", "морс", "сок", "чай", "cola"],
    "Онигири": ["соус", "васаби", "имбирь", "напит", "морс", "сок", "чай", "cola"],
    "Пицца": ["соус", "напит", "морс", "сок", "чай", "cola", "десерт", "чизкейк"],
    "Бургеры": ["картофель", "соус", "напит", "морс", "сок", "чай", "cola"],
    "Закуски": ["соус", "напит", "морс", "сок", "чай", "cola"],
    "Паста": ["напит", "морс", "сок", "чай", "cola", "десерт", "чизкейк"],
    "Супы": ["напит", "морс", "сок", "чай", "cola", "гренки"],
}

DEFAULT_ADDON_KEYWORDS = ["соус", "напит", "морс", "сок", "чай", "cola", "чизкейк", "донат"]


def _dish_payload(food: FoodItem, score: Optional[float] = None, reason: Optional[str] = None) -> dict[str, Any]:
    payload = {
        "id": food.id,
        "name": food.name,
        "category": food.category,
        "price_rub": food.price_rub,
        "calories_kcal": food.calories_kcal,
    }
    if score is not None:
        payload["score"] = round(score, 4)
    if reason:
        payload["reason"] = reason
    return payload


def _order_baskets(db: Session) -> list[set[int]]:
    rows = db.query(Order.order_id, Order.food_id).filter(Order.food_id.isnot(None)).all()
    grouped: dict[int, set[int]] = defaultdict(set)
    for order_id, food_id in rows:
        grouped[order_id].add(food_id)
    return [basket for basket in grouped.values() if basket]


def _food_map(db: Session) -> dict[int, FoodItem]:
    return {food.id: food for food in db.query(FoodItem).all()}


def _popular_food_ids(db: Session) -> Counter[int]:
    rows = db.query(Order.food_id, func.count(Order.id)).group_by(Order.food_id).all()
    return Counter({food_id: count for food_id, count in rows if food_id is not None})


def _contains_any(food: FoodItem, keywords: Iterable[str]) -> bool:
    text = f"{food.category} {food.name}".lower()
    return any(keyword.lower() in text for keyword in keywords)


def _phone_to_user(db: Session, phone: Optional[str]) -> Optional[User]:
    if not phone:
        return None
    digits = "".join(ch for ch in phone if ch.isdigit())
    if not digits:
        return None
    return db.query(User).filter(User.phone_number == int(digits)).first()


def _association_candidates(db: Session, item_ids: list[int], limit: int) -> list[dict[str, Any]]:
    baskets = _order_baskets(db)
    foods = _food_map(db)
    input_ids = set(item_ids)
    if not baskets or not input_ids:
        return []

    matching_baskets = [basket for basket in baskets if basket & input_ids]
    candidate_counts: Counter[int] = Counter()
    for basket in matching_baskets:
        candidate_counts.update(basket - input_ids)

    result = []
    total_orders = len(baskets)
    for food_id, support_count in candidate_counts.most_common():
        food = foods.get(food_id)
        if not food:
            continue
        confidence = support_count / len(matching_baskets)
        support = support_count / total_orders
        result.append(
            {
                **_dish_payload(
                    food,
                    confidence,
                    f"{round(confidence * 100)}% покупают вместе"
                ),
                "support": round(support, 4),
                "confidence": round(confidence, 4),
                "co_orders": support_count,
            }
        )
        if len(result) >= limit:
            break
    return result


def _category_candidates(db: Session, item_ids: list[int], limit: int) -> list[dict[str, Any]]:
    foods = _food_map(db)
    popular = _popular_food_ids(db)
    input_ids = set(item_ids)
    cart_foods = [foods[item_id] for item_id in item_ids if item_id in foods]
    if not cart_foods:
        return []

    keywords: list[str] = []
    for food in cart_foods:
        keywords.extend(ADDON_KEYWORDS_BY_CATEGORY.get(food.category, DEFAULT_ADDON_KEYWORDS))

    candidates = [
        food for food in foods.values()
        if food.id not in input_ids and _contains_any(food, keywords)
    ]
    candidates.sort(key=lambda food: (popular.get(food.id, 0), food.price_rub or 0), reverse=True)

    return [
        _dish_payload(food, float(popular.get(food.id, 0)))
        for food in candidates[:limit]
    ]


def _combo_candidates(db: Session, item_ids: list[int], limit: int) -> list[dict[str, Any]]:
    foods = _food_map(db)
    input_ids = set(item_ids)
    cart_foods = [foods[item_id] for item_id in item_ids if item_id in foods]
    if not cart_foods:
        return []

    popular = _popular_food_ids(db)
    combos = []
    for main in cart_foods:
        keywords = ADDON_KEYWORDS_BY_CATEGORY.get(main.category, DEFAULT_ADDON_KEYWORDS)
        addons = [
            food for food in foods.values()
            if food.id not in input_ids and food.id != main.id and _contains_any(food, keywords)
        ]
        addons.sort(key=lambda food: (popular.get(food.id, 0), food.price_rub or 0), reverse=True)
        selected = addons[:2]
        if not selected:
            continue

        combo_items = [main, *selected]
        total = sum(food.price_rub or 0 for food in combo_items)
        combos.append(
            {
                "title": f"Комбо к {main.name}",
                "reason": "Готовый набор для увеличения среднего чека",
                "total_price_rub": total,
                "items": [_dish_payload(food) for food in combo_items],
            }
        )
        if len(combos) >= limit:
            break
    return combos


def _personal_candidates(db: Session, phone: Optional[str], item_ids: list[int], limit: int) -> list[dict[str, Any]]:
    user = _phone_to_user(db, phone)
    if not user:
        return []

    input_ids = set(item_ids)
    rows = (
        db.query(FoodItem, func.count(Order.id).label("orders_count"))
        .join(Order, Order.food_id == FoodItem.id)
        .filter(Order.user_id == user.id, FoodItem.id.notin_(input_ids or [-1]))
        .group_by(FoodItem.id)
        .order_by(func.count(Order.id).desc())
        .limit(limit)
        .all()
    )
    return [
        _dish_payload(food, float(count), "Брали ранее")
        for food, count in rows
    ]


def _top_association_rules(db: Session, limit: int) -> list[dict[str, Any]]:
    baskets = _order_baskets(db)
    foods = _food_map(db)
    if not baskets:
        return []

    item_counts: Counter[int] = Counter()
    pair_counts: Counter[tuple[int, int]] = Counter()
    for basket in baskets:
        item_counts.update(basket)
        for left, right in combinations(sorted(basket), 2):
            pair_counts[(left, right)] += 1

    rules = []
    total_orders = len(baskets)
    for (left, right), pair_count in pair_counts.items():
        for antecedent, consequent in ((left, right), (right, left)):
            source = foods.get(antecedent)
            target = foods.get(consequent)
            if not source or not target:
                continue
            confidence = pair_count / item_counts[antecedent]
            support = pair_count / total_orders
            lift = confidence / (item_counts[consequent] / total_orders)
            rules.append(
                {
                    "source": _dish_payload(source),
                    "target": _dish_payload(target),
                    "support": round(support, 4),
                    "confidence": round(confidence, 4),
                    "lift": round(lift, 4),
                    "co_orders": pair_count,
                }
            )

    rules.sort(key=lambda rule: (rule["lift"], rule["confidence"], rule["co_orders"]), reverse=True)
    return rules[:limit]


@router.get("/cart")
def recommend_for_cart(
    item_ids: list[int] = Query(default=[]),
    phone: Optional[str] = None,
    limit: int = Query(default=6, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Рекомендации для корзины: ассоциации, категории, комбо и персональные повторы."""
    clean_item_ids = list(dict.fromkeys(item_ids))
    return {
        "input_item_ids": clean_item_ids,
        "frequently_bought_together": _association_candidates(db, clean_item_ids, limit),
        "category_addons": _category_candidates(db, clean_item_ids, limit),
        "combos": _combo_candidates(db, clean_item_ids, limit),
        "personal_repeats": _personal_candidates(db, phone, clean_item_ids, limit),
    }


@router.get("/analytics/overview")
def analytics_overview(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_order_rows = db.query(func.count(Order.id)).scalar() or 0
    total_orders = db.query(func.count(func.distinct(Order.order_id))).scalar() or 0
    avg_items = round(total_order_rows / total_orders, 2) if total_orders else 0

    top_dishes = (
        db.query(FoodItem, func.count(Order.id).label("orders_count"))
        .join(Order, Order.food_id == FoodItem.id)
        .group_by(FoodItem.id)
        .order_by(func.count(Order.id).desc())
        .limit(limit)
        .all()
    )
    category_rows = (
        db.query(FoodItem.category, func.count(Order.id), func.sum(FoodItem.price_rub))
        .join(Order, Order.food_id == FoodItem.id)
        .group_by(FoodItem.category)
        .order_by(func.count(Order.id).desc())
        .all()
    )
    size_rows = (
        db.query(Order.order_id, func.count(Order.id).label("size"))
        .group_by(Order.order_id)
        .all()
    )
    size_distribution = Counter(size for _, size in size_rows)

    return {
        "metrics": {
            "total_users": total_users,
            "total_orders": total_orders,
            "total_order_rows": total_order_rows,
            "avg_items_per_order": avg_items,
        },
        "top_dishes": [
            {**_dish_payload(food), "orders_count": count}
            for food, count in top_dishes
        ],
        "category_sales": [
            {"category": category, "orders_count": count, "revenue_rub": revenue or 0}
            for category, count, revenue in category_rows
        ],
        "order_size_distribution": [
            {"items_count": size, "orders_count": count}
            for size, count in sorted(size_distribution.items())
        ],
        "association_rules": _top_association_rules(db, limit),
    }


@router.get("/analytics/users/{phone}")
def analytics_user(phone: str, db: Session = Depends(get_db)):
    user = _phone_to_user(db, phone)
    if not user:
        return {"user": None, "orders": [], "top_dishes": []}

    rows = (
        db.query(FoodItem, func.count(Order.id).label("orders_count"))
        .join(Order, Order.food_id == FoodItem.id)
        .filter(Order.user_id == user.id)
        .group_by(FoodItem.id)
        .order_by(func.count(Order.id).desc())
        .limit(15)
        .all()
    )
    order_rows = (
        db.query(Order.order_id, func.count(Order.id), func.sum(FoodItem.price_rub))
        .join(FoodItem, Order.food_id == FoodItem.id)
        .filter(Order.user_id == user.id)
        .group_by(Order.order_id)
        .order_by(Order.order_id.desc())
        .limit(30)
        .all()
    )
    return {
        "user": {"id": user.id, "phone_number": user.phone_number},
        "orders": [
            {"order_id": order_id, "items_count": count, "total_rub": total or 0}
            for order_id, count, total in order_rows
        ],
        "top_dishes": [
            {**_dish_payload(food), "orders_count": count}
            for food, count in rows
        ],
    }


@router.get("/analytics/dishes/{dish_id}")
def analytics_dish(dish_id: int, db: Session = Depends(get_db)):
    food = db.get(FoodItem, dish_id)
    if not food:
        return {"dish": None, "bought_with": []}

    baskets = _order_baskets(db)
    foods = _food_map(db)
    related: Counter[int] = Counter()
    orders_count = 0
    for basket in baskets:
        if dish_id in basket:
            orders_count += 1
            related.update(basket - {dish_id})

    return {
        "dish": _dish_payload(food),
        "orders_count": orders_count,
        "bought_with": [
            {**_dish_payload(foods[food_id]), "co_orders": count}
            for food_id, count in related.most_common(15)
            if food_id in foods
        ],
    }


@router.get("/analytics/search-dishes")
def search_dishes(q: str = "", limit: int = Query(default=20, ge=1, le=50), db: Session = Depends(get_db)):
    query = db.query(FoodItem)
    if q:
        query = query.filter(FoodItem.name.contains(q))
    foods = query.order_by(FoodItem.name.asc()).limit(limit).all()
    return {"items": [_dish_payload(food) for food in foods]}
