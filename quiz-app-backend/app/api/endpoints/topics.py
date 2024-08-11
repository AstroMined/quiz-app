# filename: app/api/endpoints/topics.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.crud_topics import (create_topic_in_db, delete_topic_from_db, read_topic_from_db,
                                  read_topics_from_db, update_topic_in_db)
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.topics import (TopicCreateSchema, TopicSchema,
                                TopicUpdateSchema)
from app.services.user_service import get_current_user

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
def post_topic(
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_topic_in_db(db=db, topic=topic)

@router.get("/topics/", response_model=List[TopicSchema])
def get_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    topics = read_topics_from_db(db, skip=skip, limit=limit)
    return topics

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_topic = read_topic_from_db(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic

@router.put("/topics/{topic_id}", response_model=TopicSchema)
def put_topic(
    topic_id: int,
    topic: TopicUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_topic = update_topic_in_db(db, topic_id, topic)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic

@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic_endpoint(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_topic_from_db(db, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return success
