# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.crud.dishes import FoodItemCrud
# from app.db.session import get_db
# from app.db.models.FoodItem import FoodItem
# from app.schemas.dish import FoodItemBase 
# router = APIRouter()

# @router.post("/create", response_model=None, tags=["dishes"])
# def create(dish_data: FoodItemBase, db: Session = Depends(get_db)):
#     crud = FoodItemCrud(db)
#     print(dish_data.model_dump())
#     dish = crud.create(dish_data.model_dump())
#     return dish


# @router.post("/read_one", response_model=None, tags=["dishes"])
# def create(dish_data: FoodItemBase, db: Session = Depends(get_db)):
#     crud = FoodItemCrud(db)
#     print(dish_data.model_dump())
#     dish = crud.create(dish_data.model_dump())
#     return dish



# реализация эндпоинтов для блюд 

from fastapi import Depends
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.crud.dishes import FoodItemCrud
from app.db.models.FoodItem import FoodItem
from app.schemas.dish import FoodItemBase, FoodItemUpdate, FoodItemResponse
from app.api.baseRouter import BaseRouter

# Создаем роутер для блюд
class DishesRouter(BaseRouter[FoodItemCrud, FoodItem, FoodItemBase, FoodItemUpdate, FoodItemResponse]):
    def _setup_custom_routes(self):
        @self.router.get("/search/by_name", response_model=List[self.response_model])
        async def search_by_name(
            name: str, db: Session = Depends(get_db)):
            crud = self.crud_class(db, )
            items = crud.read_filter(name=name)
            return [self.response_schema.model_validate(item) for item in items]
        
        @self.router.get("/category/{category_id}", response_model=List[self.response_model])
        async def get_by_category(
            category_id: int, db: Session = Depends(get_db)):
            crud = self.crud_class(db, )
            items = crud.read_filter(category_id=category_id)
            return [self.response_schema.model_validate(item) for item in items]

# Создаем экземпляр роутера
dishes_router_instance = DishesRouter(
    crud_class=FoodItemCrud,
    create_schema=FoodItemBase,
    update_schema=FoodItemUpdate,
    response_schema=FoodItemResponse,
    response_model=None  # или можно указать свою модель ответа
)

router = dishes_router_instance.get_router()