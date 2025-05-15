from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from ..database import Base

# Define generic types for SQLAlchemy model and Pydantic schema
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository with CRUD operations for database models.
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update a record."""
        try:
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def remove(self, db: Session, *, id: Any) -> ModelType:
        """Delete a record."""
        try:
            obj = db.query(self.model).get(id)
            db.delete(obj)
            db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e