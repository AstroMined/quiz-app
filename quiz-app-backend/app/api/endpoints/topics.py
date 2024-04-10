# filename: app/api/endpoints/topics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import TopicSchema, TopicCreateSchema
from app.crud import create_topic_crud, read_topic_crud, update_topic_crud, delete_topic_crud

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
def create_topic_endpoint(topic: TopicCreateSchema, db: Session = Depends(get_db)):
    return create_topic_crud(db=db, topic=topic)

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def read_topic_endpoint(topic_id: int, db: Session = Depends(get_db)):
    topic = read_topic_crud(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/topics/{topic_id}", response_model=TopicSchema)
def update_topic_endpoint(topic_id: int, topic: TopicCreateSchema, db: Session = Depends(get_db)):
    updated_topic = update_topic_crud(db, topic_id, topic)
    if not updated_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return updated_topic

@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic_endpoint(topic_id: int, db: Session = Depends(get_db)):
    deleted = delete_topic_crud(db, topic_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Topic not found")
    return None