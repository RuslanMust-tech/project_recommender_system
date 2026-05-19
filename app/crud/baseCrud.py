from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class IBaseCRUD(ABC):
    
    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def create():
        pass

    @abstractmethod
    def read():
        pass

    @abstractmethod
    def update():
        pass

    @abstractmethod
    def delete():
        pass