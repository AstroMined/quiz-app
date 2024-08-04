# filename: app/crud/crud_topics.py

from sqlalchemy.orm import Session
from app.models.topics import TopicModel
from app.schemas.topics import TopicCreateSchema, TopicUpdateSchema

def create_topic(db: Session, topic: TopicCreateSchema) -> TopicModel:
    db_topic = TopicModel(**topic.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def read_topic(db: Session, topic_id: int) -> TopicModel:
    return db.query(TopicModel).filter(TopicModel.id == topic_id).first()

def read_topics(db: Session, skip: int = 0, limit: int = 100) -> list[TopicModel]:
    return db.query(TopicModel).offset(skip).limit(limit).all()

def update_topic(db: Session, topic_id: int, topic: TopicUpdateSchema) -> TopicModel:
    db_topic = read_topic(db, topic_id)
    if db_topic:
        update_data = topic.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_topic, key, value)
        db.commit()
        db.refresh(db_topic)
    return db_topic

def delete_topic(db: Session, topic_id: int) -> bool:
    db_topic = read_topic(db, topic_id)
    if db_topic:
        db.delete(db_topic)
        db.commit()
        return True
    return False
