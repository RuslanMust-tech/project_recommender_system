from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db

ModelType = TypeVar('ModelType')
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)
CrudModel = TypeVar('CrudModel')

class BaseRouter(Generic[CrudModel, ModelType, CreateSchema, UpdateSchema, ResponseSchema]):
    def __init__(
        self,
        model_class: Type[ModelType],
        crud_class: Type[CrudModel],
        create_schema: Type[CreateSchema],
        update_schema: Type[UpdateSchema],
        response_schema: Type[ResponseSchema],
        response_model = None
    ):
        self.router = APIRouter()
        self.model_class = model_class
        self.crud_class = crud_class
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        self.response_model = response_model or response_schema
        self.setup_routes()
    
    def setup_routes(self):
        # POST / - создание
        @self.router.post("/", response_model=self.response_model)
        async def create(item: self.create_schema, db: Session = Depends(get_db)):
            return await self.create(item, db)
        
        # GET /{id} - получение одной записи
        @self.router.get("/{item_id}", response_model=self.response_model)
        async def read_one(item_id: int, db: Session = Depends(get_db)):
            return await self.read_one(item_id, db)
        
        # GET / - получение всех записей
        @self.router.get("/", response_model=List[self.response_model])
        async def read_all(
            skip: int = Query(0, ge=0), limit: int = Query(1000, ge=1, le=10000), db: Session = Depends(get_db)):
            return await self.read_all(skip, limit, db)
        
        # PUT /{id} - обновление
        @self.router.put("/{item_id}", response_model=self.response_model)
        async def update(
            item_id: int, item: self.update_schema, db: Session = Depends(get_db)):
            return await self.update(item_id, item, db)
        
        # DELETE /{id} - удаление
        @self.router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete(item_id: int, db: Session = Depends(get_db)):
            return await self.delete(item_id, db)
        
        # Дополнительные кастомные маршруты
        self.setup_custom_routes()
    
    def setup_custom_routes(self):
        pass
    
    # Методы для переопределения в наследниках
    async def create(self, item: CreateSchema, db: Session) -> ResponseSchema:
        crud = self.crud_class(db, self.model_class)
        data = item.model_dump()
        instance = crud.create(data)
        return self.response_schema.model_validate(instance)
    
    async def read_one(self, item_id: int, db: Session) -> ResponseSchema:
        crud = self.crud_class(db, self.model_class)
        instance = crud.read_one(id=item_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        return self.response_schema.model_validate(instance)
    
    async def read_all(self, skip: int, limit: int, db: Session) -> List[ResponseSchema]:
        crud = self.crud_class(db, self.model_class)
        instances = crud.read_all()
        # Применяем пагинацию
        instances = instances[skip:skip + limit]
        return [self.response_schema.model_validate(instance) for instance in instances]
    
    async def update(self, item_id: int, item: UpdateSchema, db: Session) -> ResponseSchema:
        crud = self.crud_class(db, self.model_class)
        data = item.model_dump(exclude_unset=True)
        instance = crud.update(item_id, data)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        return self.response_schema.model_validate(instance)
    
    async def delete(self, item_id: int, db: Session):
        crud = self.crud_class(db, self.model_class)
        success = crud.delete(item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        return None
    
    def get_router(self) -> APIRouter:
        return self.router
