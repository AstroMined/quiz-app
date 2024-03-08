# filename: app/crud/crud_questions.py
from sqlalchemy.orm import Session
from app.models.questions import QuestionSet
from app.schemas.question_set import QuestionSetCreate, QuestionSetUpdate
from typing import List

def create_question_set(db: Session, question_set: QuestionSetCreate):
    db_question_set = QuestionSet(**question_set.dict())
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def get_question_sets(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
    return db.query(QuestionSet).offset(skip).limit(limit).all()

def update_question_set(db: Session, question_set_id: int, question_set: QuestionSetUpdate):
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if db_question_set:
        for var, value in vars(question_set).items():
            setattr(db_question_set, var, value) if value else None
        db.commit()
        db.refresh(db_question_set)
    return db_question_set

def delete_question_set(db: Session, question_set_id: int):
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if db_question_set:
        db.delete(db_question_set)
        db.commit()
        return True
    return False
