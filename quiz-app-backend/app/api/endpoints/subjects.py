# filename: app/api/endpoints/subjects.py
"""
This module defines the API endpoints for managing subjects in the application.

It includes endpoints to create and read subjects.
It also includes a service to get the database session and CRUD operations to manage subjects.

Imports:
----------
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
app.db.session: For getting the database session.
app.schemas.subjects: For validating and deserializing subject data.
app.crud: For performing CRUD operations on the subjects.

Variables:
----------
router: The API router instance.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.subjects import SubjectSchema, SubjectCreateSchema
from app.crud.crud_subjects import (
    create_subject_crud,
    read_subject_crud,
    update_subject_crud,
    delete_subject_crud
)
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
# pylint: disable=unused-argument
def create_subject_endpoint(
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new subject.

    Args:
        subject (SubjectCreateSchema): The subject data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        SubjectSchema: The created subject.
    """
    return create_subject_crud(db=db, subject=subject)

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
# pylint: disable=unused-argument
def read_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Read a subject by ID.

    Args:
        subject_id (int): The ID of the subject to be read.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        SubjectSchema: The read subject.

    Raises:
        HTTPException: If the subject is not found.
    """
    subject = read_subject_crud(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
# pylint: disable=unused-argument
def update_subject_endpoint(
    subject_id: int,
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a subject by ID.

    Args:
        subject_id (int): The ID of the subject to be updated.
        subject (SubjectCreateSchema): The updated subject data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        SubjectSchema: The updated subject.

    Raises:
        HTTPException: If the subject is not found.
    """
    updated_subject = update_subject_crud(db, subject_id, subject)
    if not updated_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return updated_subject

@router.delete("/subjects/{subject_id}", status_code=204)
# pylint: disable=unused-argument
def delete_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a subject by ID.

    Args:
        subject_id (int): The ID of the subject to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the subject is not found.
    """
    deleted = delete_subject_crud(db, subject_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None
