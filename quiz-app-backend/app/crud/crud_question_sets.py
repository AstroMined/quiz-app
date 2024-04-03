# filename: app/crud/crud_question_sets.py
"""
This module provides CRUD operations for question sets.
"""

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import QuestionSet
from app.schemas import QuestionSetCreate, QuestionSetUpdate

def get_question_sets(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
    """
    Retrieve a list of question sets.

    Args:
        db (Session): The database session.
        skip (int): The number of question sets to skip.
        limit (int): The maximum number of question sets to retrieve.

    Returns:
        List[QuestionSet]: The list of question sets.
    """
    return db.query(QuestionSet).offset(skip).limit(limit).all()

def create_question_set(db: Session, question_set: QuestionSetCreate) -> QuestionSet:
    """
    Create a new question set.
    """
    existing_question_set = db.query(QuestionSet).filter(QuestionSet.name == question_set.name).first()
    if existing_question_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question set with name '{question_set.name}' already exists.")
    
    db_question_set = QuestionSet(**question_set.dict())
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def update_question_set(db: Session, question_set_id: int, question_set: QuestionSetUpdate) -> QuestionSet:
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    update_data = question_set.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_question_set, field, value)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def delete_question_set(db: Session, question_set_id: int) -> bool:
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    db.delete(db_question_set)
    db.commit()
    return True
