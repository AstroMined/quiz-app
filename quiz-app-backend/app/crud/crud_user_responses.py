# filename: app/crud/crud_user_responses.py

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import UserResponseModel
from app.schemas import UserResponseCreateSchema, UserResponseUpdateSchema

def create_user_response_crud(db: Session, user_response: UserResponseCreateSchema) -> UserResponseModel:
    db_user_response = UserResponseModel(**user_response.model_dump())
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def get_user_response_crud(db: Session, user_response_id: int) -> Optional[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()

def get_user_responses_crud(db: Session, skip: int = 0, limit: int = 100) -> List[UserResponseModel]:
    return db.query(UserResponseModel).offset(skip).limit(limit).all()

def update_user_response_crud(db: Session, user_response_id: int, user_response: UserResponseUpdateSchema) -> UserResponseModel:
    db_user_response = db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()
    if not db_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    update_data = user_response.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user_response, key, value)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def delete_user_response_crud(db: Session, user_response_id: int) -> None:
    db_user_response = db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()
    if not db_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    db.delete(db_user_response)
    db.commit()