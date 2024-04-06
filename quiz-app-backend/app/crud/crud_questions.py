# filename: app/crud/crud_questions.py
"""
This module provides CRUD operations for questions.

It includes functions for creating, retrieving, updating, and deleting questions.
"""

from typing import List
from sqlalchemy.orm import Session
from app.models import QuestionModel, AnswerChoiceModel
from app.schemas import QuestionCreateSchema, QuestionUpdateSchema

def create_question_crud(db: Session, question: QuestionCreateSchema) -> QuestionModel:
    db_question = QuestionModel(
        text=question.text,
        question_set_id=question.question_set_id,
        subtopic_id=question.subtopic_id,
        explanation=question.explanation
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.answer_choices:
        db_choice = AnswerChoiceModel(
            text=choice.text,
            is_correct=choice.is_correct,
            question=db_question
        )
        db.add(db_choice)

    db.commit()
    return db_question

def get_questions_crud(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    """
    Retrieve a list of questions.

    Args:
        db (Session): The database session.
        skip (int): The number of questions to skip.
        limit (int): The maximum number of questions to retrieve.

    Returns:
        List[Question]: The list of questions.
    """
    questions = db.query(QuestionModel).offset(skip).limit(limit).all()
    return questions

def get_question_crud(db: Session, question_id: int) -> QuestionModel:
    """
    Retrieve a question by ID.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.

    Returns:
        Question: The retrieved question, or None if not found.
    """
    return db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

def update_question_crud(db: Session, question_id: int, question: QuestionUpdateSchema) -> QuestionModel:
    """
    Update a question.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to update.
        question (QuestionUpdate): The updated question data.

    Returns:
        Question: The updated question, or None if not found.
    """
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if db_question:
        update_data = question.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question_crud(db: Session, question_id: int) -> bool:
    """
    Delete a question.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to delete.

    Returns:
        bool: True if the question was deleted, False otherwise.
    """
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False