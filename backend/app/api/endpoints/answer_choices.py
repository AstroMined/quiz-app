# filename: backend/app/api/endpoints/answer_choices.py

"""
Answer Choices Management API

This module provides API endpoints for managing answer choices in the quiz application.
It includes operations for creating, reading, updating, and deleting answer choices.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_answer_choices module.

Endpoints:
- POST /answer-choices/: Create a new answer choice
- GET /answer-choices/: Retrieve a list of answer choices
- GET /answer-choices/{answer_choice_id}: Retrieve a specific answer choice by ID
- PUT /answer-choices/{answer_choice_id}: Update a specific answer choice
- DELETE /answer-choices/{answer_choice_id}: Delete a specific answer choice

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_answer_choices import (create_answer_choice_in_db,
                                                  delete_answer_choice_from_db,
                                                  read_answer_choice_from_db,
                                                  read_answer_choices_from_db,
                                                  update_answer_choice_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.answer_choices import (AnswerChoiceCreateSchema,
                                                AnswerChoiceSchema,
                                                AnswerChoiceUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/answer-choices/", response_model=AnswerChoiceSchema, status_code=status.HTTP_201_CREATED)
def post_answer_choice(
    answer_choice: AnswerChoiceCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new answer choice.

    This endpoint allows authenticated users to create a new answer choice in the database.
    The answer choice data is validated using the AnswerChoiceCreateSchema.

    Args:
        answer_choice (AnswerChoiceCreateSchema): The answer choice data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        AnswerChoiceSchema: The created answer choice data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    validated_answer_choice = AnswerChoiceCreateSchema(**answer_choice.model_dump())
    answer_choice_data = validated_answer_choice.model_dump()
    created_answer_choice = create_answer_choice_in_db(db=db, answer_choice_data=answer_choice_data)
    return AnswerChoiceSchema.model_validate(created_answer_choice)

@router.get("/answer-choices/", response_model=List[AnswerChoiceSchema])
def get_answer_choices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of answer choices.

    This endpoint allows authenticated users to retrieve a paginated list of answer choices from the database.

    Args:
        skip (int, optional): The number of answer choices to skip. Defaults to 0.
        limit (int, optional): The maximum number of answer choices to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[AnswerChoiceSchema]: A list of answer choices.
    """
    answer_choices = read_answer_choices_from_db(db, skip=skip, limit=limit)
    return [AnswerChoiceSchema.model_validate(ac) for ac in answer_choices]

@router.get("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def get_answer_choice(
    answer_choice_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific answer choice by ID.

    This endpoint allows authenticated users to retrieve a single answer choice by its ID.

    Args:
        answer_choice_id (int): The ID of the answer choice to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        AnswerChoiceSchema: The answer choice data.

    Raises:
        HTTPException: If the answer choice with the given ID is not found.
    """
    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id=answer_choice_id)
    if db_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return AnswerChoiceSchema.model_validate(db_answer_choice)

@router.put("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def put_answer_choice(
    answer_choice_id: int,
    answer_choice: AnswerChoiceUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific answer choice.

    This endpoint allows authenticated users to update an existing answer choice by its ID.

    Args:
        answer_choice_id (int): The ID of the answer choice to update.
        answer_choice (AnswerChoiceUpdateSchema): The updated answer choice data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        AnswerChoiceSchema: The updated answer choice data.

    Raises:
        HTTPException: If the answer choice with the given ID is not found.
    """
    validated_answer_choice = AnswerChoiceUpdateSchema(**answer_choice.model_dump())
    answer_choice_data = validated_answer_choice.model_dump()
    updated_answer_choice = update_answer_choice_in_db(db, answer_choice_id, answer_choice_data)
    
    if updated_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    
    return AnswerChoiceSchema.model_validate(updated_answer_choice)

@router.delete("/answer-choices/{answer_choice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer_choice(
    answer_choice_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific answer choice.

    This endpoint allows authenticated users to delete an existing answer choice by its ID.

    Args:
        answer_choice_id (int): The ID of the answer choice to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: If the answer choice with the given ID is not found.
    """
    success = delete_answer_choice_from_db(db, answer_choice_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return None
