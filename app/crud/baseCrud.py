from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Type, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

ModelType = TypeVar('ModelType')

class BaseCRUD(ABC, Generic[ModelType]):
    """Базовый CRUD класс с общей реализацией"""
    
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    def create(self, data: Dict[str, Any]) -> ModelType:
        """Создать новую запись"""
        instance = self.model(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def read_one(self, **kwargs) -> Optional[ModelType]:
        """Найти одну запись"""
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    
    def read_all(self) -> List[ModelType]:
        """Получить все записи"""
        query = select(self.model)
        result = self.db.execute(query)
        return list(result.scalars().all())
    
    def read_filter(self, **kwargs) -> List[ModelType]:
        """Найти записи по фильтру"""
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key).contains(value))
        
        result = self.db.execute(query)
        return list(result.scalars().all())
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """Обновить запись по ID"""
        instance = self.db.get(self.model, id)
        if not instance:
            return None
        
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """Удалить запись по ID"""
        instance = self.db.get(self.model, id)
        if not instance:
            return False
        
        self.db.delete(instance)
        self.db.commit()
        return True
    
    def exists(self, **kwargs) -> bool:
        """Проверить существование записи"""
        return self.read_one(**kwargs) is not None
    
    def count(self) -> int:
        """Получить количество записей"""
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)
        result = self.db.execute(query)
        return result.scalar()
