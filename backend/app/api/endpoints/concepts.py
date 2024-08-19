# filename: backend/app/api/endpoints/concepts.py

"""
Concepts Management API

This module provides API endpoints for managing concepts in the quiz application.
It includes operations for creating, reading, updating, and deleting concepts.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_concepts module.

Endpoints:
- POST /concepts/: Create a new concept
- GET /concepts/: Retrieve a list of concepts
- GET /concepts/{concept_id}: Retrieve a specific concept by ID
- PUT /concepts/{concept_id}: Update a specific concept
- DELETE /concepts/{concept_id}: Delete a specific concept

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_concepts import (create_concept_in_db,
                                            delete_concept_from_db,
                                            read_concept_from_db,
                                            read_concepts_from_db,
                                            update_concept_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.concepts import (ConceptCreateSchema, ConceptSchema,
                                          ConceptUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/concepts/", response_model=ConceptSchema, status_code=201)
def post_concept(
    concept: ConceptCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new concept.

    This endpoint allows authenticated users to create a new concept in the database.
    The concept data is validated using the ConceptCreateSchema.

    Args:
        concept (ConceptCreateSchema): The concept data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        ConceptSchema: The created concept data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    validated_concept = ConceptCreateSchema(**concept.model_dump())
    concept_data = validated_concept.model_dump()
    created_concept = create_concept_in_db(db=db, concept_data=concept_data)
    return ConceptSchema.model_validate(created_concept)

@router.get("/concepts/", response_model=List[ConceptSchema])
def get_concepts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of concepts.

    This endpoint allows authenticated users to retrieve a paginated list of concepts from the database.

    Args:
        skip (int, optional): The number of concepts to skip. Defaults to 0.
        limit (int, optional): The maximum number of concepts to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[ConceptSchema]: A list of concepts.
    """
    concepts = read_concepts_from_db(db, skip=skip, limit=limit)
    return [ConceptSchema.model_validate(c) for c in concepts]

@router.get("/concepts/{concept_id}", response_model=ConceptSchema)
def get_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific concept by ID.

    This endpoint allows authenticated users to retrieve a single concept by its ID.

    Args:
        concept_id (int): The ID of the concept to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        ConceptSchema: The concept data.

    Raises:
        HTTPException: If the concept with the given ID is not found.
    """
    db_concept = read_concept_from_db(db, concept_id=concept_id)
    if db_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return ConceptSchema.model_validate(db_concept)

@router.put("/concepts/{concept_id}", response_model=ConceptSchema)
def put_concept(
    concept_id: int,
    concept: ConceptUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific concept.

    This endpoint allows authenticated users to update an existing concept by its ID.

    Args:
        concept_id (int): The ID of the concept to update.
        concept (ConceptUpdateSchema): The updated concept data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        ConceptSchema: The updated concept data.

    Raises:
        HTTPException: If the concept with the given ID is not found.
    """
    validated_concept = ConceptUpdateSchema(**concept.model_dump())
    concept_data = validated_concept.model_dump()
    updated_concept = update_concept_in_db(db, concept_id, concept_data)
    
    if updated_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    return ConceptSchema.model_validate(updated_concept)

@router.delete("/concepts/{concept_id}", status_code=204)
def delete_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific concept.

    This endpoint allows authenticated users to delete an existing concept by its ID.

    Args:
        concept_id (int): The ID of the concept to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: If the concept with the given ID is not found.
    """
    success = delete_concept_from_db(db, concept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Concept not found")
    return None
