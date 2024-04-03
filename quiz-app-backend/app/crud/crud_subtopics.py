# crud/crud_subtopics.py

from sqlalchemy.orm import Session
from app.models import Subtopic
from app.schemas import SubtopicCreate

def create_subtopic(db: Session, subtopic: SubtopicCreate) -> Subtopic:
    db_subtopic = Subtopic(**subtopic.dict())
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)
    return db_subtopic