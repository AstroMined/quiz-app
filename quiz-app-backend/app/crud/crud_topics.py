# filename: app/crud/crud_topics.py

from sqlalchemy.orm import Session
from app.models import TopicModel
from app.schemas import TopicCreateSchema

def create_topic_crud(db: Session, topic: TopicCreateSchema) -> TopicModel:
    db_topic = TopicModel(**topic.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def read_topic_crud(db: Session, topic_id: int) -> TopicModel:
    return db.query(TopicModel).filter(TopicModel.id == topic_id).first()

def update_topic_crud(db: Session, topic_id: int, topic: TopicCreateSchema) -> TopicModel:
    db_topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if db_topic:
        db_topic.name = topic.name
        db_topic.subject_id = topic.subject_id
        db.commit()
        db.refresh(db_topic)
    return db_topic

def delete_topic_crud(db: Session, topic_id: int) -> bool:
    db_topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if db_topic:
        db.delete(db_topic)
        db.commit()
        return True
    return False
