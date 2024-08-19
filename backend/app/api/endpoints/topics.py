# filename: backend/app/api/endpoints/topics.py

"""
Topics Management API

This module provides API endpoints for managing topics in the quiz application.
It includes operations for creating, reading, updating, and deleting topics.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_topics module.

Endpoints:
- POST /topics/: Create a new topic
- GET /topics/: Retrieve a list of topics
- GET /topics/{topic_id}: Retrieve a specific topic by ID
- PUT /topics/{topic_id}: Update a specific topic
- DELETE /topics/{topic_id}: Delete a specific topic

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_topics import (create_topic_in_db,
                                          delete_topic_from_db,
                                          read_topic_from_db,
                                          read_topics_from_db,
                                          update_topic_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.topics import (TopicCreateSchema, TopicSchema,
                                        TopicUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
def post_topic(
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new topic.

    This endpoint allows authenticated users to create a new topic in the database.
    The topic data is validated using the TopicCreateSchema.

    Args:
        topic (TopicCreateSchema): The topic data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        TopicSchema: The created topic data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    topic_data = topic.model_dump()
    created_topic = create_topic_in_db(db=db, topic_data=topic_data)
    return TopicSchema.model_validate(created_topic)

@router.get("/topics/", response_model=List[TopicSchema])
def get_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of topics.

    This endpoint allows authenticated users to retrieve a paginated list of topics from the database.

    Args:
        skip (int, optional): The number of topics to skip. Defaults to 0.
        limit (int, optional): The maximum number of topics to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[TopicSchema]: A list of topics.
    """
    topics = read_topics_from_db(db, skip=skip, limit=limit)
    return [TopicSchema.model_validate(t) for t in topics]

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific topic by ID.

    This endpoint allows authenticated users to retrieve a single topic by its ID.

    Args:
        topic_id (int): The ID of the topic to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        TopicSchema: The topic data.

    Raises:
        HTTPException: If the topic with the given ID is not found.
    """
    db_topic = read_topic_from_db(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return TopicSchema.model_validate(db_topic)

@router.put("/topics/{topic_id}", response_model=TopicSchema)
def put_topic(
    topic_id: int,
    topic: TopicUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific topic.

    This endpoint allows authenticated users to update an existing topic by its ID.

    Args:
        topic_id (int): The ID of the topic to update.
        topic (TopicUpdateSchema): The updated topic data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        TopicSchema: The updated topic data.

    Raises:
        HTTPException: If the topic with the given ID is not found.
    """
    topic_data = topic.model_dump()
    db_topic = update_topic_in_db(db, topic_id, topic_data)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return TopicSchema.model_validate(db_topic)

@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific topic.

    This endpoint allows authenticated users to delete an existing topic by its ID.

    Args:
        topic_id (int): The ID of the topic to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: If the topic with the given ID is not found.
    """
    success = delete_topic_from_db(db, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return None
