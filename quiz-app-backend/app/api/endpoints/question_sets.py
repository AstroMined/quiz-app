# filename: app/api/endpoints/question_sets.py
"""
This module provides endpoints for managing question sets.

It defines routes for uploading question sets and retrieving question sets from the database.
"""

import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.crud.crud_question_sets import get_question_sets, update_question_set, delete_question_set
from app.crud.crud_question_sets import create_question_set as create_question_set_crud
from app.db.session import get_db
from app.schemas.question_sets import QuestionSet, QuestionSetCreate, QuestionSetUpdate

router = APIRouter()

@router.post("/upload-questions/")
async def upload_question_set(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint to upload a question set in JSON format.
    
    Args:
        file: An UploadFile object representing the JSON file containing the question set data.
        db: A database session dependency injected by FastAPI.
        
    Raises:
        HTTPException: If the uploaded file is not a valid JSON file.
        
    Returns:
        The created question set object.
    """
    content = await file.read()
    try:
        question_data = json.loads(content.decode('utf-8'))
        # Assuming you have a function to process and validate the JSON data
        question_set_created = create_question_set(db, question_data)
        return question_set_created
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

@router.get("/question-set/", response_model=List[QuestionSet])
def read_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
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
def create_question_set(question_set: QuestionSetCreate, db: Session = Depends(get_db)):
    """
    Create a new question set.
    """
    return create_question_set_crud(db=db, question_set=question_set)

@router.get("/question-sets/", response_model=List[QuestionSet])
def read_question_sets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
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