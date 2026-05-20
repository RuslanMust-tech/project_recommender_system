from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud.dishes import FoodItemCrud
from app.db.session import get_db
from app.db.models.FoodItem import FoodItem
from app.schemas.dish import FoodItemBase 
router = APIRouter()

@router.post("/create", response_model=None, tags=["dishes"])
def create(dish_data: FoodItemBase, db: Session = Depends(get_db)):
    crud = FoodItemCrud(db)
    print(dish_data.model_dump())
    dish = crud.create(dish_data.model_dump())
    return dish


@router.post("/read_one", response_model=None, tags=["dishes"])
def create(dish_data: FoodItemBase, db: Session = Depends(get_db)):
    crud = FoodItemCrud(db)
    print(dish_data.model_dump())
    dish = crud.create(dish_data.model_dump())
    return dish



# реализация эндпоинтов для блюд 

#CRUD