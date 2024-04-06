# filename: app/api/endpoints/questions.py
"""
This module provides endpoints for managing questions.

It defines routes for creating, retrieving, updating, and deleting questions.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.crud import (
    create_question_crud,
    get_question_crud,
    get_questions_crud,
    update_question_crud,
    delete_question_crud
)
from app.db import get_db
from app.schemas import QuestionCreateSchema, QuestionSchema, QuestionUpdateSchema
from app.services import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/questions/", response_model=QuestionSchema, status_code=201)
def create_question_endpoint(question: QuestionCreateSchema, db: Session = Depends(get_db)):
    """
    Create a new question.

    Args:
        question (QuestionCreate): The question data.
        db (Session): The database session.

    Returns:
        Question: The created question.
    """
    return create_question_crud(db, question)

@router.get("/questions/{question_id}", response_model=QuestionSchema)
def get_question_endpoint(question_id: int, question: QuestionUpdateSchema, db: Session = Depends(get_db)):
    """
    Retrieve a question.

    Args:
        question_id (int): The ID of the question to retrieve.
        db (Session): The database session.

    Returns:
        Question: The question.
    """
    question = get_question_crud(db, question_id)
    return question

@router.get("/questions/", response_model=List[QuestionSchema])
def get_questions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Retrieve a list of questions.

    Args:
        skip (int): The number of questions to skip.
        limit (int): The maximum number of questions to retrieve.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        List[Question]: The list of questions.
    """
    questions = get_questions_crud(db, skip=skip, limit=limit)
    return questions

@router.put("/questions/{question_id}", response_model=QuestionSchema)
def update_question_endpoint(question_id: int, question: QuestionUpdateSchema, db: Session = Depends(get_db)):
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
    db_question = update_question_crud(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.delete("/questions/{question_id}", status_code=204)
def delete_question_endpoint(question_id: int, db: Session = Depends(get_db)):
    """
    Delete a question.

    Args:
        question_id (int): The ID of the question to delete.
        db (Session): The database session.

    Raises:
        HTTPException: If the question is not found.
    """
    deleted = delete_question_crud(db, question_id=question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return Response(status_code=204)