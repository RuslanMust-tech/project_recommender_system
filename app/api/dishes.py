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

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db

# Типы для дженериков
ModelType = TypeVar('ModelType')
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)

class BaseRouter(Generic[ModelType, CreateSchema, UpdateSchema, ResponseSchema]):
    """Базовый дженерик класс для роутеров с CRUD операциями"""
    
    def __init__(
        self,
        prefix: str,
        tags: List[str],
        crud_class: Type,
        create_schema: Type[CreateSchema],
        update_schema: Type[UpdateSchema],
        response_schema: Type[ResponseSchema],
        response_model = None
    ):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.crud_class = crud_class
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        self.response_model = response_model or response_schema
        self._setup_routes()
    
    def _setup_routes(self):
        """Настройка всех стандартных CRUD маршрутов"""
        
        # POST / - создание
        @self.router.post("/", response_model=self.response_model)
        async def create(
            item: self.create_schema,
            db: Session = Depends(get_db)
        ):
            return await self._create(item, db)
        
        # GET /{id} - получение одной записи
        @self.router.get("/{item_id}", response_model=self.response_model)
        async def read_one(
            item_id: int,
            db: Session = Depends(get_db)
        ):
            return await self._read_one(item_id, db)
        
        # GET / - получение всех записей
        @self.router.get("/", response_model=List[self.response_model])
        async def read_all(
            skip: int = Query(0, ge=0),
            limit: int = Query(100, ge=1, le=1000),
            db: Session = Depends(get_db)
        ):
            return await self._read_all(skip, limit, db)
        
        # PUT /{id} - обновление
        @self.router.put("/{item_id}", response_model=self.response_model)
        async def update(
            item_id: int,
            item: self.update_schema,
            db: Session = Depends(get_db)
        ):
            return await self._update(item_id, item, db)
        
        # DELETE /{id} - удаление
        @self.router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete(
            item_id: int,
            db: Session = Depends(get_db)
        ):
            return await self._delete(item_id, db)
        
        # Дополнительные кастомные маршруты
        self._setup_custom_routes()
    
    def _setup_custom_routes(self):
        """Переопределить в наследниках для добавления кастомных маршрутов"""
        pass
    
    # Методы для переопределения в наследниках
    async def _create(self, item: CreateSchema, db: Session) -> ResponseSchema:
        """Создание записи"""
        crud = self.crud_class(db)
        data = item.model_dump()
        instance = crud.create(data)
        return self.response_schema.model_validate(instance)
    
    async def _read_one(self, item_id: int, db: Session) -> ResponseSchema:
        """Получение одной записи"""
        crud = self.crud_class(db)
        instance = crud.read_one(id=item_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        return self.response_schema.model_validate(instance)
    
    async def _read_all(self, skip: int, limit: int, db: Session) -> List[ResponseSchema]:
        """Получение всех записей"""
        crud = self.crud_class(db)
        instances = crud.read_all()
        # Применяем пагинацию
        instances = instances[skip:skip + limit]
        return [self.response_schema.model_validate(instance) for instance in instances]
    
    async def _update(self, item_id: int, item: UpdateSchema, db: Session) -> ResponseSchema:
        """Обновление записи"""
        crud = self.crud_class(db)
        data = item.model_dump(exclude_unset=True)
        instance = crud.update(item_id, data)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        return self.response_schema.model_validate(instance)
    
    async def _delete(self, item_id: int, db: Session):
        """Удаление записи"""
        crud = self.crud_class(db)
        success = crud.delete(item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        return None
    
    def get_router(self) -> APIRouter:
        """Получить роутер"""
        return self.router
#CRUD