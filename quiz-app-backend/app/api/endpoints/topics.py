# filename: app/api/endpoints/topics.py
"""
This module defines the API endpoints for managing topics in the application.

It includes endpoints to create and read topics.
It also includes a service to get the database session and CRUD operations to manage topics.

Imports:
----------
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
app.db: For getting the database session.
app.schemas: For validating and deserializing topic data.
app.crud: For performing CRUD operations on the topics.

Variables:
----------
router: The API router instance.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import TopicSchema, TopicCreateSchema
from app.crud import create_topic_crud, read_topic_crud, update_topic_crud, delete_topic_crud
from app.services import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
# pylint: disable=unused-argument
def create_topic_endpoint(
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new topic.

    Args:
        topic (TopicCreateSchema): The topic data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The created topic.
    """
    return create_topic_crud(db=db, topic=topic)

@router.get("/topics/{topic_id}", response_model=TopicSchema)
# pylint: disable=unused-argument
def read_topic_endpoint(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Read a topic by its ID.

    Args:
        topic_id (int): The ID of the topic to be read.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The read topic.

    Raises:
        HTTPException: If the topic is not found.
    """
    topic = read_topic_crud(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/topics/{topic_id}", response_model=TopicSchema)
# pylint: disable=unused-argument
def update_topic_endpoint(
    topic_id: int,
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a topic by its ID.

    Args:
        topic_id (int): The ID of the topic to be updated.
        topic (TopicCreateSchema): The updated topic data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The updated topic.

    Raises:
        HTTPException: If the topic is not found.
    """
    updated_topic = update_topic_crud(db, topic_id, topic)
    if not updated_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return updated_topic

@router.delete("/topics/{topic_id}", status_code=204)
# pylint: disable=unused-argument
def delete_topic_endpoint(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a topic by its ID.

    Args:
        topic_id (int): The ID of the topic to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the topic is not found.
    """
    deleted = delete_topic_crud(db, topic_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Topic not found")
    return None
