# filepath: backend/app/api/endpoints/subjects.py

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
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.crud.crud_subjects import (create_subject_in_db,
                                            delete_subject_from_db,
                                            read_subject_from_db,
                                            read_subjects_from_db,
                                            update_subject_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.subjects import (SubjectCreateSchema, SubjectSchema,
                                          SubjectUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.services.logging_service import logger

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def post_subject(
    request: Request,
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new subject.

    This endpoint allows authenticated users to create a new subject in the database.
    The subject data is validated using the SubjectCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        subject (SubjectCreateSchema): The subject data to be created.
        db (Session): The database session.

    Returns:
        SubjectSchema: The created subject data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subject_data = subject.model_dump()
    try:
        created_subject = create_subject_in_db(db=db, subject_data=subject_data)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Subject with this name already exists")
    except HTTPException as e:
        # Re-raise the HTTPException from create_subject_in_db
        raise e
    return SubjectSchema.model_validate(created_subject)

@router.get("/subjects/", response_model=List[SubjectSchema])
def get_subjects(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of subjects.

    This endpoint allows authenticated users to retrieve a paginated list of subjects from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of subjects to skip. Defaults to 0.
        limit (int, optional): The maximum number of subjects to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[SubjectSchema]: A list of subjects.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subjects = read_subjects_from_db(db, skip=skip, limit=limit)
    return [SubjectSchema.model_validate(s) for s in subjects]

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def get_subject(
    request: Request,
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific subject by ID.

    This endpoint allows authenticated users to retrieve a single subject by its ID.

    Args:
        request (Request): The FastAPI request object.
        subject_id (int): The ID of the subject to retrieve.
        db (Session): The database session.

    Returns:
        SubjectSchema: The subject data.

    Raises:
        HTTPException: If the subject with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_subject = read_subject_from_db(db, subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectSchema.model_validate(db_subject)

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
def put_subject(
    request: Request,
    subject_id: int,
    subject: SubjectUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific subject.

    This endpoint allows authenticated users to update an existing subject by its ID.

    Args:
        request (Request): The FastAPI request object.
        subject_id (int): The ID of the subject to update.
        subject (SubjectUpdateSchema): The updated subject data.
        db (Session): The database session.

    Returns:
        SubjectSchema: The updated subject data.

    Raises:
        HTTPException: If the subject with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subject_data = subject.model_dump(exclude_unset=True)
    logger.debug(f"Updating subject {subject_id} with data: {subject_data}")
    try:
        db_subject = update_subject_in_db(db, subject_id, subject_data)
        if db_subject is None:
            raise HTTPException(status_code=404, detail="Subject not found")
    except HTTPException as e:
        # Re-raise the HTTPException from update_subject_in_db
        logger.error(f"Error updating subject {subject_id}: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating subject {subject_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
    logger.debug(f"Successfully updated subject {subject_id}")
    return SubjectSchema.model_validate(db_subject)

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(
    request: Request,
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific subject.

    This endpoint allows authenticated users to delete an existing subject by its ID.

    Args:
        request (Request): The FastAPI request object.
        subject_id (int): The ID of the subject to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the subject with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_subject_from_db(db, subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None
