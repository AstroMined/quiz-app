# filename: backend/app/api/endpoints/subjects.py

"""
Subjects Management API

This module provides API endpoints for managing subjects in the quiz application.
It includes operations for creating, reading, updating, and deleting subjects.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_subjects module.

Endpoints:
- POST /subjects/: Create a new subject
- GET /subjects/: Retrieve a list of subjects
- GET /subjects/{subject_id}: Retrieve a specific subject by ID
- PUT /subjects/{subject_id}: Update a specific subject
- DELETE /subjects/{subject_id}: Delete a specific subject

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_subjects import (create_subject_in_db,
                                            delete_subject_from_db,
                                            read_subject_from_db,
                                            read_subjects_from_db,
                                            update_subject_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.subjects import (SubjectCreateSchema, SubjectSchema,
                                          SubjectUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def post_subject(
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new subject.

    This endpoint allows authenticated users to create a new subject in the database.
    The subject data is validated using the SubjectCreateSchema.

    Args:
        subject (SubjectCreateSchema): The subject data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        SubjectSchema: The created subject data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    subject_data = subject.model_dump()
    created_subject = create_subject_in_db(db=db, subject_data=subject_data)
    return SubjectSchema.model_validate(created_subject)

@router.get("/subjects/", response_model=List[SubjectSchema])
def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of subjects.

    This endpoint allows authenticated users to retrieve a paginated list of subjects from the database.

    Args:
        skip (int, optional): The number of subjects to skip. Defaults to 0.
        limit (int, optional): The maximum number of subjects to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[SubjectSchema]: A list of subjects.
    """
    subjects = read_subjects_from_db(db, skip=skip, limit=limit)
    return [SubjectSchema.model_validate(s) for s in subjects]

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific subject by ID.

    This endpoint allows authenticated users to retrieve a single subject by its ID.

    Args:
        subject_id (int): The ID of the subject to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        SubjectSchema: The subject data.

    Raises:
        HTTPException: If the subject with the given ID is not found.
    """
    db_subject = read_subject_from_db(db, subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectSchema.model_validate(db_subject)

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
def put_subject(
    subject_id: int,
    subject: SubjectUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific subject.

    This endpoint allows authenticated users to update an existing subject by its ID.

    Args:
        subject_id (int): The ID of the subject to update.
        subject (SubjectUpdateSchema): The updated subject data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        SubjectSchema: The updated subject data.

    Raises:
        HTTPException: If the subject with the given ID is not found.
    """
    subject_data = subject.model_dump()
    db_subject = update_subject_in_db(db, subject_id, subject_data)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectSchema.model_validate(db_subject)

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific subject.

    This endpoint allows authenticated users to delete an existing subject by its ID.

    Args:
        subject_id (int): The ID of the subject to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: If the subject with the given ID is not found.
    """
    success = delete_subject_from_db(db, subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None
