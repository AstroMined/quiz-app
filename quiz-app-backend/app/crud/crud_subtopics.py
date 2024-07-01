# crud/crud_subtopics.py

from sqlalchemy.orm import Session
from app.models.subtopics import SubtopicModel
from app.schemas.subtopics import SubtopicCreateSchema

def create_subtopic_crud(db: Session, subtopic: SubtopicCreateSchema) -> SubtopicModel:
    db_subtopic = SubtopicModel(**subtopic.model_dump())
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)
    return db_subtopic

def read_subtopic_crud(db: Session, subtopic_id: int) -> SubtopicModel:
    return db.query(SubtopicModel).filter(SubtopicModel.id == subtopic_id).first()

def update_subtopic_crud(db: Session, subtopic_id: int, subtopic: SubtopicCreateSchema) -> SubtopicModel:
    db_subtopic = read_subtopic_crud(db, subtopic_id)
    if db_subtopic:
        update_data = subtopic.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subtopic, key, value)
        db.commit()
        db.refresh(db_subtopic)
    return db_subtopic

def delete_subtopic_crud(db: Session, subtopic_id: int) -> None:
    db_subtopic = read_subtopic_crud(db, subtopic_id)
    if db_subtopic:
        db.delete(db_subtopic)
        db.commit()
