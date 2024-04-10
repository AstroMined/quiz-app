# filename: app/crud/crud_subjects.py
from sqlalchemy.orm import Session
from app.models.subjects import SubjectModel
from app.schemas.subjects import SubjectCreateSchema

def create_subject_crud(db: Session, subject: SubjectCreateSchema) -> SubjectModel:
    db_subject = SubjectModel(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def read_subject_crud(db: Session, subject_id: int) -> SubjectModel:
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()

def update_subject_crud(db: Session, subject_id: int, subject: SubjectCreateSchema) -> SubjectModel:
    db_subject = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if db_subject:
        db_subject.name = subject.name
        db.commit()
        db.refresh(db_subject)
    return db_subject

def delete_subject_crud(db: Session, subject_id: int) -> bool:
    db_subject = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False
