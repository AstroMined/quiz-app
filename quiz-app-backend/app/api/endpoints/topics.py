# filename: app/api/endpoints/topics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.topics import TopicSchema, TopicCreateSchema, TopicUpdateSchema
from app.crud.crud_topics import create_topic, read_topic, read_topics, update_topic, delete_topic
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
def post_topic(
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_topic(db=db, topic=topic)

@router.get("/topics/", response_model=List[TopicSchema])
def get_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    topics = read_topics(db, skip=skip, limit=limit)
    return topics

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_topic = read_topic(db, topic_id=topic_id)
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
    db_topic = update_topic(db, topic_id, topic)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic

@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic_endpoint(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_topic(db, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return success
