# filename: app/crud/crud_question_sets.py

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import QuestionSetModel,QuestionModel
from app.schemas import (
    QuestionSetCreateSchema,
    QuestionSetUpdateSchema
)

def read_question_set_crud(db: Session, question_set_id: int) -> QuestionSetModel:
    question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    return question_set


def read_question_sets_crud(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSetModel]:
    question_sets = db.query(QuestionSetModel).offset(skip).limit(limit).all()
    if not question_sets:
        raise HTTPException(status_code=404, detail="No question sets found.")
    
    return question_sets

def create_question_set_crud(db: Session, question_set: QuestionSetCreateSchema) -> QuestionSetModel:
    existing_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.name == question_set.name).first()
    if existing_question_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question set with name '{question_set.name}' already exists.")

    db_question_set = QuestionSetModel(**question_set.model_dump())
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def update_question_set_crud(db: Session, question_set_id: int, question_set: QuestionSetUpdateSchema) -> QuestionSetModel:
    db_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    update_data = question_set.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "question_ids":
            db_question_set.question_ids = value
        else:
            setattr(db_question_set, field, value)

    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def delete_question_set_crud(db: Session, question_set_id: int) -> bool:
    db_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    db.delete(db_question_set)
    db.commit()
    return True
