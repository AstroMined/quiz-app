# filename: app/api/endpoints/questions.py
"""
This module provides endpoints for managing questions.

It defines routes for creating, retrieving, updating, and deleting questions.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response  # Import Response
from sqlalchemy.orm import Session
from app.crud import crud_questions
from app.db.session import get_db
from app.schemas.questions import QuestionCreate, Question, QuestionUpdate

router = APIRouter()

@router.post("/questions/", response_model=Question, status_code=201)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """
    Create a new question.

    Args:
        question (QuestionCreate): The question data.
        db (Session): The database session.

    Returns:
        Question: The created question.
    """
    return crud_questions.create_question(db, question)

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
    questions = crud_questions.get_questions(db, skip=skip, limit=limit)
    return questions

@router.put("/questions/{question_id}", response_model=Question)
def update_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)):
    """
    Update a question.

    Args:
        question_id (int): The ID of the question to update.
        question (QuestionUpdate): The updated question data.
        db (Session): The database session.

    Returns:
        Question: The updated question.

    Raises:
        HTTPException: If the question is not found.
    """
    db_question = crud_questions.update_question(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """
    Delete a question.

    Args:
        question_id (int): The ID of the question to delete.
        db (Session): The database session.

    Raises:
        HTTPException: If the question is not found.
    """
    deleted = crud_questions.delete_question(db, question_id=question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return Response(status_code=204)