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
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.crud.crud_topics import (
    create_topic_in_db,
    delete_topic_from_db,
    read_topic_from_db,
    read_topics_from_db,
    update_topic_in_db,
)
from backend.app.db.session import get_db
from backend.app.schemas.topics import TopicCreateSchema, TopicSchema, TopicUpdateSchema
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.services.logging_service import logger

router = APIRouter()


@router.post("/topics/", response_model=TopicSchema, status_code=201)
def post_topic(
    request: Request, topic: TopicCreateSchema, db: Session = Depends(get_db)
):
    """
    Create a new topic.

    This endpoint allows authenticated users to create a new topic in the database.
    The topic data is validated using the TopicCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        topic (TopicCreateSchema): The topic data to be created.
        db (Session): The database session.

    Returns:
        TopicSchema: The created topic data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    topic_data = topic.model_dump()
    try:
        created_topic = create_topic_in_db(db=db, topic_data=topic_data)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Topic with this name already exists"
        )
    except HTTPException as e:
        # Re-raise the HTTPException from create_topic_in_db
        raise e
    return TopicSchema.model_validate(created_topic)


@router.get("/topics/", response_model=List[TopicSchema])
def get_topics(
    request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve a list of topics.

    This endpoint allows authenticated users to retrieve a paginated list of topics from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of topics to skip. Defaults to 0.
        limit (int, optional): The maximum number of topics to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[TopicSchema]: A list of topics.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    topics = read_topics_from_db(db, skip=skip, limit=limit)
    return [TopicSchema.model_validate(t) for t in topics]


@router.get("/topics/{topic_id}", response_model=TopicSchema)
def get_topic(request: Request, topic_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific topic by ID.

    This endpoint allows authenticated users to retrieve a single topic by its ID.

    Args:
        request (Request): The FastAPI request object.
        topic_id (int): The ID of the topic to retrieve.
        db (Session): The database session.

    Returns:
        TopicSchema: The topic data.

    Raises:
        HTTPException: If the topic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_topic = read_topic_from_db(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Debug logging
    logger.debug(f"Raw db_topic: {db_topic}")
    logger.debug(f"db_topic subjects: {db_topic.subjects}")

    topic_schema = TopicSchema.model_validate(db_topic)

    # More debug logging
    logger.debug(f"Converted topic_schema: {topic_schema}")
    logger.debug(f"topic_schema subjects: {topic_schema.subjects}")

    return topic_schema


@router.put("/topics/{topic_id}", response_model=TopicSchema)
def put_topic(
    request: Request,
    topic_id: int,
    topic: TopicUpdateSchema,
    db: Session = Depends(get_db),
):
    """
    Update a specific topic.

    This endpoint allows authenticated users to update an existing topic by its ID.

    Args:
        request (Request): The FastAPI request object.
        topic_id (int): The ID of the topic to update.
        topic (TopicUpdateSchema): The updated topic data.
        db (Session): The database session.

    Returns:
        TopicSchema: The updated topic data.

    Raises:
        HTTPException: If the topic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    topic_data = topic.model_dump(exclude_unset=True)
    try:
        db_topic = update_topic_in_db(db, topic_id, topic_data)
        if db_topic is None:
            raise HTTPException(
                status_code=404,
                detail="Topic not found or one or more subjects do not exist",
            )
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Topic with this name already exists"
        )
    return TopicSchema.model_validate(db_topic)


@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic(request: Request, topic_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific topic.

    This endpoint allows authenticated users to delete an existing topic by its ID.

    Args:
        request (Request): The FastAPI request object.
        topic_id (int): The ID of the topic to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the topic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_topic_from_db(db, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return None
