# filename: app/api/endpoints/questions.py
"""
This module provides endpoints for managing questions.

It defines routes for creating, retrieving, updating, and deleting questions.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.crud_questions import create_question, get_questions, update_question, delete_question
from app.db.session import get_db
from app.schemas.questions import QuestionCreate, Question

router = APIRouter()

@router.post("/questions/", response_model=Question, status_code=201)
def create_question_endpoint(question: QuestionCreate, db: Session = Depends(get_db)):
    """
    Create a new question.

    Args:
        question (QuestionCreate): The question data.
        db (Session): The database session.

    Returns:
        Question: The created question.
    """
    return create_question(db=db, question=question)

@router.get("/questions/", response_model=List[Question])
def read_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of questions.

    Args:
        skip (int): The number of questions to skip.
        limit (int): The maximum number of questions to retrieve.
        db (Session): The database session.

    Returns:
        List[Question]: The list of questions.
    """
    questions = get_questions(db, skip=skip, limit=limit)
    return questions

@router.put("/questions/{question_id}", response_model=Question)
def update_question_endpoint(question_id: int, question: QuestionCreate, db: Session = Depends(get_db)):
    """
    Update a question.

    Args:
        question_id (int): The ID of the question to update.
        question (QuestionCreate): The updated question data.
        db (Session): The database session.

    Returns:
        Question: The updated question.

    Raises:
        HTTPException: If the question is not found.
    """
    db_question = update_question(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.delete("/questions/{question_id}")
def delete_question_endpoint(question_id: int, db: Session = Depends(get_db)):
    """
    Delete a question.

    Args:
        question_id (int): The ID of the question to delete.
        db (Session): The database session.

    Returns:
        dict: A success message.

    Raises:
        HTTPException: If the question is not found.
    """
    deleted = delete_question(db, question_id=question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}