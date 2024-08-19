# filename: backend/app/api/endpoints/question_sets.py

"""
Question Sets Management API

This module provides API endpoints for managing question sets in the quiz application.
It includes operations for creating, reading, updating, and deleting question sets,
as well as uploading question sets from files.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_question_sets module.

Endpoints:
- POST /upload-questions/: Upload a question set from a file
- GET /question-sets/: Retrieve a list of question sets
- POST /question-sets/: Create a new question set
- GET /question-sets/{question_set_id}: Retrieve a specific question set by ID
- PUT /question-sets/{question_set_id}: Update a specific question set
- DELETE /question-sets/{question_set_id}: Delete a specific question set

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

import json
from typing import List

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Response,
                     UploadFile, status)
from sqlalchemy.orm import Session

from backend.app.crud.crud_question_sets import (create_question_set_in_db,
                                                 delete_question_set_from_db,
                                                 read_question_set_from_db,
                                                 read_question_sets_from_db,
                                                 update_question_set_in_db)
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.question_sets import (QuestionSetCreateSchema,
                                               QuestionSetSchema,
                                               QuestionSetUpdateSchema)
from backend.app.schemas.questions import QuestionCreateSchema
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/upload-questions/")
async def upload_question_set(
    file: UploadFile = File(...),
    question_set_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Upload a question set from a file.

    This endpoint allows admin users to upload a question set from a JSON file.

    Args:
        file (UploadFile): The JSON file containing the question set data.
        question_set_name (str): The name for the new question set.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        dict: A message indicating successful upload.

    Raises:
        HTTPException: 
            - 403: If the user is not an admin.
            - 400: If the JSON data is invalid.
            - 500: If there's an error during the upload process.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can upload question sets")

    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        for question in question_data:
            QuestionCreateSchema(**question)

        question_set = QuestionSetCreateSchema(name=question_set_name, creator_id=current_user.id)
        question_set_created = create_question_set_in_db(db, question_set.model_dump())

        for question in question_data:
            question['question_set_id'] = question_set_created.id
            create_question_in_db(db, QuestionCreateSchema(**question).model_dump())

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON data: {str(exc)}"
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading question set: {str(exc)}"
        ) from exc

@router.get("/question-sets/", response_model=List[QuestionSetSchema])
def get_question_sets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of question sets.

    This endpoint allows authenticated users to retrieve a paginated list of question sets.

    Args:
        skip (int): The number of question sets to skip (for pagination).
        limit (int): The maximum number of question sets to return (for pagination).
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[QuestionSetSchema]: A list of question sets.
    """
    question_sets = read_question_sets_from_db(db, skip=skip, limit=limit)
    return [QuestionSetSchema.model_validate(qs) for qs in question_sets]

@router.post("/question-sets/", response_model=QuestionSetSchema, status_code=201)
def post_question_set(
    question_set: QuestionSetCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new question set.

    This endpoint allows authenticated users to create a new question set.

    Args:
        question_set (QuestionSetCreateSchema): The question set data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        QuestionSetSchema: The created question set.
    """
    question_set_data = question_set.model_dump()
    question_set_data['creator_id'] = current_user.id
    created_question_set = create_question_set_in_db(db=db, question_set_data=question_set_data)
    return QuestionSetSchema.model_validate(created_question_set)

@router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def get_question_set(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific question set by ID.

    This endpoint allows authenticated users to retrieve a single question set by its ID.

    Args:
        question_set_id (int): The ID of the question set to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        QuestionSetSchema: The question set data.

    Raises:
        HTTPException: If the question set with the given ID is not found.
    """
    question_set = read_question_set_from_db(db, question_set_id=question_set_id)
    if not question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found")
    return QuestionSetSchema.model_validate(question_set)

@router.put("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def put_question_set(
    question_set_id: int,
    question_set: QuestionSetUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific question set.

    This endpoint allows authenticated users to update an existing question set by its ID.

    Args:
        question_set_id (int): The ID of the question set to update.
        question_set (QuestionSetUpdateSchema): The updated question set data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        QuestionSetSchema: The updated question set data.

    Raises:
        HTTPException: If the question set with the given ID is not found.
    """
    question_set_data = question_set.model_dump()
    updated_question_set = update_question_set_in_db(db, question_set_id, question_set_data)
    if updated_question_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")
    return QuestionSetSchema.model_validate(updated_question_set)

@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific question set.

    This endpoint allows authenticated users to delete an existing question set by its ID.

    Args:
        question_set_id (int): The ID of the question set to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        Response: An empty response with a 204 status code.

    Raises:
        HTTPException: If the question set with the given ID is not found.
    """
    deleted = delete_question_set_from_db(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question set not found")
    return Response(status_code=204)
