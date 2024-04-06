# crud/crud_subtopics.py

from sqlalchemy.orm import Session
from app.models import SubtopicModel
from app.schemas import SubtopicCreateSchema

def create_subtopic_crud(db: Session, subtopic: SubtopicCreateSchema) -> SubtopicModel:
    db_subtopic = SubtopicModel(**subtopic.dict())
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)
    return db_subtopic
