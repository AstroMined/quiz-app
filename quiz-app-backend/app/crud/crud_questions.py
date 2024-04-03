# filename: app/crud/crud_questions.py
"""
This module provides CRUD operations for questions.

It includes functions for creating, retrieving, updating, and deleting questions.
"""

from typing import List
from sqlalchemy.orm import Session
from app.models import Question, AnswerChoice
from app.schemas import QuestionCreate, QuestionUpdate

def create_question(db: Session, question: QuestionCreate) -> Question:
    db_question = Question(
        text=question.text,
        question_set_id=question.question_set_id,
        subtopic_id=question.subtopic_id,
        explanation=question.explanation
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.answer_choices:
        db_choice = AnswerChoice(
            text=choice.text,
            is_correct=choice.is_correct,
            question=db_question
        )
        db.add(db_choice)

    db.commit()
    return db_question

def get_questions(db: Session, skip: int = 0, limit: int = 100) -> List[Question]:
    """
    Retrieve a list of questions.

    Args:
        db (Session): The database session.
        skip (int): The number of questions to skip.
        limit (int): The maximum number of questions to retrieve.

    Returns:
        List[Question]: The list of questions.
    """
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions

def get_question(db: Session, question_id: int) -> Question:
    """
    Retrieve a question by ID.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.

    Returns:
        Question: The retrieved question, or None if not found.
    """
    return db.query(Question).filter(Question.id == question_id).first()

def update_question(db: Session, question_id: int, question: QuestionUpdate) -> Question:
    """
    Update a question.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to update.
        question (QuestionUpdate): The updated question data.

    Returns:
        Question: The updated question, or None if not found.
    """
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question:
        update_data = question.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int) -> bool:
    """
    Delete a question.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to delete.

    Returns:
        bool: True if the question was deleted, False otherwise.
    """
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False