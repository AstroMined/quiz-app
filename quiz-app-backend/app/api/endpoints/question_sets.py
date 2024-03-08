# filename: app/api/endpoints/question_sets.py
"""
This module provides endpoints for managing question sets.

It defines routes for uploading question sets and retrieving question sets from the database.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.crud.crud_question_sets import create_question_set, get_question_sets
from app.db.session import get_db
import json

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