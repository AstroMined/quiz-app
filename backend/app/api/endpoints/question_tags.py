# filename: backend/app/api/endpoints/question_tags.py

"""
Question Tags Management API

This module provides API endpoints for managing question tags in the quiz application.
It includes operations for creating, reading, updating, and deleting question tags.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_question_tags module.

Endpoints:
- POST /question-tags/: Create a new question tag
- GET /question-tags/: Retrieve a list of question tags
- GET /question-tags/{tag_id}: Retrieve a specific question tag by ID
- PUT /question-tags/{tag_id}: Update a specific question tag
- DELETE /question-tags/{tag_id}: Delete a specific question tag

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_question_tags import (create_question_tag_in_db,
                                                 delete_question_tag_from_db,
                                                 read_question_tag_from_db,
                                                 read_question_tags_from_db,
                                                 update_question_tag_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.question_tags import (QuestionTagCreateSchema,
                                               QuestionTagSchema,
                                               QuestionTagUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/question-tags/", response_model=QuestionTagSchema, status_code=status.HTTP_201_CREATED)
def post_question_tag(
    question_tag: QuestionTagCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new question tag.

    This endpoint allows authenticated users to create a new question tag in the database.
    The question tag data is validated using the QuestionTagCreateSchema.

    Args:
        question_tag (QuestionTagCreateSchema): The question tag data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        QuestionTagSchema: The created question tag data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    question_tag_data = question_tag.model_dump()
    created_tag = create_question_tag_in_db(db=db, question_tag_data=question_tag_data)
    return QuestionTagSchema.model_validate(created_tag)

@router.get("/question-tags/", response_model=List[QuestionTagSchema])
def get_question_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of question tags.

    This endpoint allows authenticated users to retrieve a paginated list of question tags from the database.

    Args:
        skip (int, optional): The number of question tags to skip. Defaults to 0.
        limit (int, optional): The maximum number of question tags to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[QuestionTagSchema]: A list of question tags.
    """
    question_tags = read_question_tags_from_db(db, skip=skip, limit=limit)
    return [QuestionTagSchema.model_validate(tag) for tag in question_tags]

@router.get("/question-tags/{tag_id}", response_model=QuestionTagSchema)
def get_question_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific question tag by ID.

    This endpoint allows authenticated users to retrieve a single question tag by its ID.

    Args:
        tag_id (int): The ID of the question tag to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        QuestionTagSchema: The question tag data.

    Raises:
        HTTPException: If the question tag with the given ID is not found.
    """
    db_question_tag = read_question_tag_from_db(db, question_tag_id=tag_id)
    if db_question_tag is None:
        raise HTTPException(status_code=404, detail="Question tag not found")
    return QuestionTagSchema.model_validate(db_question_tag)

@router.put("/question-tags/{tag_id}", response_model=QuestionTagSchema)
def put_question_tag(
    tag_id: int,
    question_tag: QuestionTagUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific question tag.

    This endpoint allows authenticated users to update an existing question tag by its ID.

    Args:
        tag_id (int): The ID of the question tag to update.
        question_tag (QuestionTagUpdateSchema): The updated question tag data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        QuestionTagSchema: The updated question tag data.

    Raises:
        HTTPException: If the question tag with the given ID is not found.
    """
    question_tag_data = question_tag.model_dump()
    updated_tag = update_question_tag_in_db(db, tag_id, question_tag_data)
    if updated_tag is None:
        raise HTTPException(status_code=404, detail="Question tag not found")
    return QuestionTagSchema.model_validate(updated_tag)

@router.delete("/question-tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific question tag.

    This endpoint allows authenticated users to delete an existing question tag by its ID.

    Args:
        tag_id (int): The ID of the question tag to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: If the question tag with the given ID is not found.
    """
    success = delete_question_tag_from_db(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question tag not found")
    return None