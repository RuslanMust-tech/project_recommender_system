# CRUD для блюд
from app.crud.baseCrud import IBaseCRUD
from app.db.models import FoodItem
from sqlalchemy.orm import Session

class FoodItemCrud(IBaseCRUD):
    def create(self, foodItemData) -> FoodItem:
        item = FoodItem(**foodItemData)
        self.db.add(item)
        self.db.commit()
        return item
    
    def read(self):
        select(User).where(User.name == "spongebob")

    def update(self):
        pass

    def delete(self):
        pass