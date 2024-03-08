# filename: app/crud/crud_questions.py
"""
This module provides CRUD operations for question sets.

It includes functions for creating, retrieving, updating, and deleting question sets.
"""

from sqlalchemy.orm import Session
from app.models.questions import QuestionSet
from app.schemas.question_set import QuestionSetCreate, QuestionSetUpdate
from typing import List

def create_question_set(db: Session, question_set: QuestionSetCreate) -> QuestionSet:
    """
    Create a new question set.

    Args:
        db (Session): The database session.
        question_set (QuestionSetCreate): The question set data.

    Returns:
        QuestionSet: The created question set.
    """
    db_question_set = QuestionSet(**question_set.dict())
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

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

def update_question_set(db: Session, question_set_id: int, question_set: QuestionSetUpdate) -> QuestionSet:
    """
    Update a question set.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set to update.
        question_set (QuestionSetUpdate): The updated question set data.

    Returns:
        QuestionSet: The updated question set.
    """
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if db_question_set:
        for var, value in vars(question_set).items():
            setattr(db_question_set, var, value) if value else None
        db.commit()
        db.refresh(db_question_set)
    return db_question_set

def delete_question_set(db: Session, question_set_id: int) -> bool:
    """
    Delete a question set.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set to delete.

    Returns:
        bool: True if the question set was deleted, False otherwise.
    """
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if db_question_set:
        db.delete(db_question_set)
        db.commit()
        return True
    return False