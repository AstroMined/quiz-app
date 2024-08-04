# filename: app/crud/crud_answer_choices.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.answer_choices import AnswerChoiceModel

def create_answer_choice(db: Session, answer_choice_data: dict) -> AnswerChoiceModel:
    db_answer_choice = AnswerChoiceModel(**answer_choice_data)
    db.add(db_answer_choice)
    db.commit()
    db.refresh(db_answer_choice)
    return db_answer_choice

def get_answer_choice(db: Session, answer_choice_id: int) -> Optional[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == answer_choice_id).first()

def get_answer_choices(db: Session, skip: int = 0, limit: int = 100) -> List[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).offset(skip).limit(limit).all()

def update_answer_choice(db: Session, answer_choice_id: int, answer_choice_data: dict) -> Optional[AnswerChoiceModel]:
    db_answer_choice = get_answer_choice(db, answer_choice_id)
    if db_answer_choice:
        for key, value in answer_choice_data.items():
            setattr(db_answer_choice, key, value)
        db.commit()
        db.refresh(db_answer_choice)
    return db_answer_choice

def delete_answer_choice(db: Session, answer_choice_id: int) -> bool:
    db_answer_choice = get_answer_choice(db, answer_choice_id)
    if db_answer_choice:
        db.delete(db_answer_choice)
        db.commit()
        return True
    return False
