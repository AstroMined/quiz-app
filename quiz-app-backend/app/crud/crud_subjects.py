# filename: app/crud/crud_subjects.py

from sqlalchemy.orm import Session
from app.models.subjects import SubjectModel
from app.schemas.subjects import SubjectCreateSchema, SubjectUpdateSchema

def create_subject(db: Session, subject: SubjectCreateSchema) -> SubjectModel:
    db_subject = SubjectModel(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def read_subject(db: Session, subject_id: int) -> SubjectModel:
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()

def read_subjects(db: Session, skip: int = 0, limit: int = 100) -> list[SubjectModel]:
    return db.query(SubjectModel).offset(skip).limit(limit).all()

def update_subject(db: Session, subject_id: int, subject: SubjectUpdateSchema) -> SubjectModel:
    db_subject = read_subject(db, subject_id)
    if db_subject:
        update_data = subject.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subject, key, value)
        db.commit()
        db.refresh(db_subject)
    return db_subject

def delete_subject(db: Session, subject_id: int) -> bool:
    db_subject = read_subject(db, subject_id)
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False
