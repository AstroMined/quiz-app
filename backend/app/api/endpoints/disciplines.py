# filename: backend/app/api/endpoints/disciplines.py

"""
Disciplines Management API

This module provides API endpoints for managing disciplines in the quiz application.
It includes operations for creating, reading, updating, and deleting disciplines.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_disciplines module.

Endpoints:
- POST /disciplines/: Create a new discipline
- GET /disciplines/: Retrieve a list of disciplines
- GET /disciplines/{discipline_id}: Retrieve a specific discipline by ID
- PUT /disciplines/{discipline_id}: Update a specific discipline
- DELETE /disciplines/{discipline_id}: Delete a specific discipline

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_disciplines import (
    create_discipline_in_db,
    delete_discipline_from_db,
    read_discipline_from_db,
    read_disciplines_from_db,
    update_discipline_in_db,
)
from backend.app.db.session import get_db
from backend.app.schemas.disciplines import (
    DisciplineCreateSchema,
    DisciplineSchema,
    DisciplineUpdateSchema,
)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()


@router.post("/disciplines/", response_model=DisciplineSchema, status_code=201)
def post_discipline(
    request: Request, discipline: DisciplineCreateSchema, db: Session = Depends(get_db)
):
    """
    Create a new discipline.

    This endpoint allows authenticated users to create a new discipline in the database.
    The discipline data is validated using the DisciplineCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        discipline (DisciplineCreateSchema): The discipline data to be created.
        db (Session): The database session.

    Returns:
        DisciplineSchema: The created discipline data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_discipline = DisciplineCreateSchema(**discipline.model_dump())
    discipline_data = validated_discipline.model_dump()
    created_discipline = create_discipline_in_db(db=db, discipline_data=discipline_data)
    return DisciplineSchema.model_validate(created_discipline)


@router.get("/disciplines/", response_model=List[DisciplineSchema])
def get_disciplines(
    request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve a list of disciplines.

    This endpoint allows authenticated users to retrieve a paginated list of disciplines from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of disciplines to skip. Defaults to 0.
        limit (int, optional): The maximum number of disciplines to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[DisciplineSchema]: A list of disciplines.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    disciplines = read_disciplines_from_db(db, skip=skip, limit=limit)
    return [DisciplineSchema.model_validate(d) for d in disciplines]


@router.get("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def get_discipline(request: Request, discipline_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific discipline by ID.

    This endpoint allows authenticated users to retrieve a single discipline by its ID.

    Args:
        request (Request): The FastAPI request object.
        discipline_id (int): The ID of the discipline to retrieve.
        db (Session): The database session.

    Returns:
        DisciplineSchema: The discipline data.

    Raises:
        HTTPException: If the discipline with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_discipline = read_discipline_from_db(db, discipline_id=discipline_id)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return DisciplineSchema.model_validate(db_discipline)


@router.put("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def put_discipline(
    request: Request,
    discipline_id: int,
    discipline: DisciplineUpdateSchema,
    db: Session = Depends(get_db),
):
    """
    Update a specific discipline.

    This endpoint allows authenticated users to update an existing discipline by its ID.

    Args:
        request (Request): The FastAPI request object.
        discipline_id (int): The ID of the discipline to update.
        discipline (DisciplineUpdateSchema): The updated discipline data.
        db (Session): The database session.

    Returns:
        DisciplineSchema: The updated discipline data.

    Raises:
        HTTPException: If the discipline with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_discipline = DisciplineUpdateSchema(**discipline.model_dump())
    discipline_data = validated_discipline.model_dump()
    updated_discipline = update_discipline_in_db(db, discipline_id, discipline_data)
    if updated_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return DisciplineSchema.model_validate(updated_discipline)


@router.delete("/disciplines/{discipline_id}", status_code=204)
def delete_discipline(
    request: Request, discipline_id: int, db: Session = Depends(get_db)
):
    """
    Delete a specific discipline.

    This endpoint allows authenticated users to delete an existing discipline by its ID.

    Args:
        request (Request): The FastAPI request object.
        discipline_id (int): The ID of the discipline to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the discipline with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_discipline_from_db(db, discipline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return None
