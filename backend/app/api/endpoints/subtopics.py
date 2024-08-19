# filename: backend/app/api/endpoints/subtopics.py

"""
Subtopics Management API

This module provides API endpoints for managing subtopics in the quiz application.
It includes operations for creating, reading, updating, and deleting subtopics.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_subtopics module.

Endpoints:
- POST /subtopics/: Create a new subtopic
- GET /subtopics/: Retrieve a list of subtopics
- GET /subtopics/{subtopic_id}: Retrieve a specific subtopic by ID
- PUT /subtopics/{subtopic_id}: Update a specific subtopic
- DELETE /subtopics/{subtopic_id}: Delete a specific subtopic

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_subtopics import (create_subtopic_in_db,
                                             delete_subtopic_from_db,
                                             read_subtopic_from_db,
                                             read_subtopics_from_db,
                                             update_subtopic_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.subtopics import (SubtopicCreateSchema,
                                           SubtopicSchema,
                                           SubtopicUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/subtopics/", response_model=SubtopicSchema, status_code=201)
def post_subtopic(
    subtopic: SubtopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new subtopic.

    This endpoint allows authenticated users to create a new subtopic in the database.
    The subtopic data is validated using the SubtopicCreateSchema.

    Args:
        subtopic (SubtopicCreateSchema): The subtopic data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        SubtopicSchema: The created subtopic data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    subtopic_data = subtopic.model_dump()
    created_subtopic = create_subtopic_in_db(db=db, subtopic_data=subtopic_data)
    return SubtopicSchema.model_validate(created_subtopic)

@router.get("/subtopics/", response_model=List[SubtopicSchema])
def get_subtopics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of subtopics.

    This endpoint allows authenticated users to retrieve a paginated list of subtopics from the database.

    Args:
        skip (int, optional): The number of subtopics to skip. Defaults to 0.
        limit (int, optional): The maximum number of subtopics to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[SubtopicSchema]: A list of subtopics.
    """
    subtopics = read_subtopics_from_db(db, skip=skip, limit=limit)
    return [SubtopicSchema.model_validate(s) for s in subtopics]

@router.get("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def get_subtopic(
    subtopic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific subtopic by ID.

    This endpoint allows authenticated users to retrieve a single subtopic by its ID.

    Args:
        subtopic_id (int): The ID of the subtopic to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        SubtopicSchema: The subtopic data.

    Raises:
        HTTPException: If the subtopic with the given ID is not found.
    """
    db_subtopic = read_subtopic_from_db(db, subtopic_id=subtopic_id)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return SubtopicSchema.model_validate(db_subtopic)

@router.put("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def put_subtopic(
    subtopic_id: int,
    subtopic: SubtopicUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific subtopic.

    This endpoint allows authenticated users to update an existing subtopic by its ID.

    Args:
        subtopic_id (int): The ID of the subtopic to update.
        subtopic (SubtopicUpdateSchema): The updated subtopic data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        SubtopicSchema: The updated subtopic data.

    Raises:
        HTTPException: If the subtopic with the given ID is not found.
    """
    subtopic_data = subtopic.model_dump()
    db_subtopic = update_subtopic_in_db(db, subtopic_id, subtopic_data)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return SubtopicSchema.model_validate(db_subtopic)

@router.delete("/subtopics/{subtopic_id}", status_code=204)
def delete_subtopic(
    subtopic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific subtopic.

    This endpoint allows authenticated users to delete an existing subtopic by its ID.

    Args:
        subtopic_id (int): The ID of the subtopic to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: If the subtopic with the given ID is not found.
    """
    success = delete_subtopic_from_db(db, subtopic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return None
