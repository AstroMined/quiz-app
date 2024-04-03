# filename: app/api/endpoints/question_sets.py
"""
This module provides endpoints for managing question sets.

It defines routes for uploading question sets and retrieving question sets from the database.
"""

import json
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.crud import (
    get_question_sets,
    update_question_set,
    delete_question_set,
    create_question_set,
    create_question
)
from app.db import get_db
from app.schemas import (
    QuestionSet,
    QuestionSetCreate,
    QuestionSetUpdate,
    QuestionCreate
)
from app.services import get_current_user
from app.models.users import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload-questions/")
async def upload_question_set_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Endpoint to upload a question set in JSON format.
    """
    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        # Validate question data
        for question in question_data:
            QuestionCreate(**question)  # Validate question against schema

        # Create question set
        question_set = QuestionSetCreate(name=file.filename)
        question_set_created = create_question_set(db, question_set)

        # Create questions and associate with question set
        for question in question_data:
            question['question_set_id'] = question_set_created.id
            try:
                create_question(db, QuestionCreate(**question))
            except ValidationError as exc:
                raise HTTPException(status_code=400, detail=f"Invalid question data: {exc}")

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValidationError) as exc:
        logger.exception("Invalid JSON data")  # Add logging statement
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(exc)}")

    except Exception as exc:
        logger.exception("Error uploading question set")  # Add logging statement
        raise HTTPException(status_code=500, detail=f"Error uploading question set: {str(exc)}")

@router.get("/question-set/", response_model=List[QuestionSet])
def read_questions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve question sets from the database.
    
    Args:
        skip: The number of question sets to skip (for pagination).
        limit: The maximum number of question sets to retrieve (for pagination).
        db: A database session dependency injected by FastAPI.
        
    Returns:
        A list of question set objects.
    """
    questions = get_question_sets(db, skip=skip, limit=limit)
    return questions

@router.post("/question-sets/", response_model=QuestionSet, status_code=201)
def create_question_set_endpoint(question_set: QuestionSetCreate, db: Session = Depends(get_db)):
    """
    Create a new question set.
    """
    return create_question_set(db=db, question_set=question_set)

@router.get("/question-sets/", response_model=List[QuestionSet])
def read_question_sets_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of question sets.
    """
    question_sets = get_question_sets(db, skip=skip, limit=limit)
    return question_sets

@router.put("/question-sets/{question_set_id}", response_model=QuestionSet)
def update_question_set_endpoint(question_set_id: int, question_set: QuestionSetUpdate, db: Session = Depends(get_db)):
    """
    Update a question set.

    Args:
        question_set_id (int): The ID of the question set to update.
        question_set (QuestionSetUpdate): The updated question set data.
        db (Session): The database session.

    Returns:
        QuestionSet: The updated question set.

    Raises:
        HTTPException: If the question set is not found.
    """
    db_question_set = update_question_set(db, question_set_id=question_set_id, question_set=question_set)
    if db_question_set is None:
        raise HTTPException(status_code=404, detail="Question set not found")
    return db_question_set

@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set_endpoint(question_set_id: int, db: Session = Depends(get_db)):
    """
    Delete a question set.

    Args:
        question_set_id (int): The ID of the question set to delete.
        db (Session): The database session.

    Raises:
        HTTPException: If the question set is not found.
    """
    deleted = delete_question_set(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question set not found")
    return Response(status_code=204)
