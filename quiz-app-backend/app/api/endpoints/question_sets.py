# filename: app/api/endpoints/question_sets.py
"""
This module provides endpoints for managing question sets.

It defines routes for uploading question sets and retrieving question sets from the database.
"""

import json
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Response,
    status
)
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.db import get_db
from app.services import get_current_user
from app.models import UserModel, QuestionSetModel
from app.crud import (
    create_question_crud,
    read_question_sets_crud,
    read_question_set_crud,
    update_question_set_crud,
    delete_question_set_crud,
    create_question_set_crud
)
from app.schemas import (
    QuestionSetSchema,
    QuestionSetCreateSchema,
    QuestionSetUpdateSchema,
    QuestionCreateSchema
)

router = APIRouter()

@router.post("/upload-questions/")
async def upload_question_set_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Endpoint to upload a question set in JSON format.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can upload question sets")

    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        # Validate question data
        for question in question_data:
            QuestionCreateSchema(**question)  # Validate question against schema

        # Create question set
        question_set = QuestionSetCreateSchema(name=file.filename)
        question_set_created = create_question_set_crud(db, question_set)

        # Create questions and associate with question set
        for question in question_data:
            question['question_set_id'] = question_set_created.id
            create_question_crud(db, QuestionCreateSchema(**question))

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON data: {str(exc)}") from exc

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading question set: {str(exc)}") from exc

@router.get("/question-set/", response_model=List[QuestionSetSchema])
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
    questions = read_question_sets_crud(db, skip=skip, limit=limit)
    return questions

@router.post("/question-sets/", response_model=QuestionSetSchema, status_code=201)
def create_question_set_endpoint(question_set: QuestionSetCreateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Create a new question set.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can create question sets")

    if len(question_set.name) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question set name must be at least 3 characters long")

    return create_question_set_crud(db=db, question_set=question_set)

@router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def get_question_set_endpoint(question_set_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a question set by ID.
    """
    question_set = read_question_set_crud(db, question_set_id=question_set_id)
    if not question_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question set with ID {question_set_id} not found")
    return question_set

@router.get("/question-sets/", response_model=List[QuestionSetSchema])
def read_question_sets_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of question sets.
    """
    question_sets = read_question_sets_crud(db, skip=skip, limit=limit)
    return question_sets

@router.put("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def update_question_set_endpoint(question_set_id: int, question_set: QuestionSetUpdateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Update a question set.

    Args:
        question_set_id (int): The ID of the question set to update.
        question_set (QuestionSetUpdate): The updated question set data.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        QuestionSet: The updated question set.

    Raises:
        HTTPException: If the question set is not found or the user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can update question sets")

    db_question_set = update_question_set_crud(db, question_set_id=question_set_id, question_set=question_set)
    if db_question_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")
    return db_question_set

@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set_endpoint(question_set_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can delete question sets")

    deleted = delete_question_set_crud(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
