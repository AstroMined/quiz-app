# filename: backend/app/crud/crud_answer_choices.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import QuestionToAnswerAssociation
from backend.app.models.questions import QuestionModel


def create_answer_choice_in_db(db: Session, answer_choice_data: Dict) -> AnswerChoiceModel:
    db_answer_choice = AnswerChoiceModel(
        text=answer_choice_data['text'],
        is_correct=answer_choice_data['is_correct'],
        explanation=answer_choice_data.get('explanation')
    )
    db.add(db_answer_choice)
    db.commit()
    db.refresh(db_answer_choice)
    
    if 'question_ids' in answer_choice_data and answer_choice_data['question_ids']:
        for question_id in answer_choice_data['question_ids']:
            create_question_to_answer_association_in_db(db, question_id, db_answer_choice.id)
    
    db.refresh(db_answer_choice)
            
    return db_answer_choice

def read_answer_choice_from_db(db: Session, answer_choice_id: int) -> Optional[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == answer_choice_id).first()

def read_answer_choices_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).offset(skip).limit(limit).all()

def update_answer_choice_in_db(db: Session, answer_choice_id: int, answer_choice_data: Dict) -> Optional[AnswerChoiceModel]:
    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id)
    if db_answer_choice:
        for key, value in answer_choice_data.items():
            setattr(db_answer_choice, key, value)
        db.commit()
        db.refresh(db_answer_choice)
    return db_answer_choice

def delete_answer_choice_from_db(db: Session, answer_choice_id: int) -> bool:
    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id)
    if db_answer_choice:
        db.delete(db_answer_choice)
        db.commit()
        return True
    return False

def create_question_to_answer_association_in_db(db: Session, question_id: int, answer_choice_id: int) -> bool:
    association = QuestionToAnswerAssociation(question_id=question_id, answer_choice_id=answer_choice_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_answer_association_from_db(db: Session, question_id: int, answer_choice_id: int) -> bool:
    association = db.query(QuestionToAnswerAssociation).filter_by(
        question_id=question_id, answer_choice_id=answer_choice_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_answer_choices_for_question_from_db(db: Session, question_id: int) -> List[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).join(QuestionToAnswerAssociation).filter(
        QuestionToAnswerAssociation.question_id == question_id
    ).all()

def read_questions_for_answer_choice_from_db(db: Session, answer_choice_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToAnswerAssociation).filter(
        QuestionToAnswerAssociation.answer_choice_id == answer_choice_id
    ).all()
