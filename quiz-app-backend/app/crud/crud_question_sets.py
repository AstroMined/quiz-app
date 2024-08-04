# filename: app/crud/crud_question_sets.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.question_sets import QuestionSetModel
from app.models.questions import QuestionModel
from app.models.groups import GroupModel

def create_question_set(db: Session, question_set_data: dict) -> QuestionSetModel:
    db_question_set = QuestionSetModel(
        name=question_set_data['name'],
        description=question_set_data.get('description'),
        is_public=question_set_data.get('is_public', True),
        creator_id=question_set_data['creator_id']
    )
    db.add(db_question_set)
    db.flush()

    if 'question_ids' in question_set_data:
        questions = db.query(QuestionModel).filter(QuestionModel.id.in_(question_set_data['question_ids'])).all()
        db_question_set.questions = questions

    if 'group_ids' in question_set_data:
        groups = db.query(GroupModel).filter(GroupModel.id.in_(question_set_data['group_ids'])).all()
        db_question_set.groups = groups

    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def get_question_set(db: Session, question_set_id: int) -> Optional[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()

def get_question_sets(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).offset(skip).limit(limit).all()

def update_question_set(db: Session, question_set_id: int, question_set_data: dict) -> Optional[QuestionSetModel]:
    db_question_set = get_question_set(db, question_set_id)
    if db_question_set:
        for key, value in question_set_data.items():
            if key == 'question_ids':
                questions = db.query(QuestionModel).filter(QuestionModel.id.in_(value)).all()
                db_question_set.questions = questions
            elif key == 'group_ids':
                groups = db.query(GroupModel).filter(GroupModel.id.in_(value)).all()
                db_question_set.groups = groups
            else:
                setattr(db_question_set, key, value)
        db.commit()
        db.refresh(db_question_set)
    return db_question_set

def delete_question_set(db: Session, question_set_id: int) -> bool:
    db_question_set = get_question_set(db, question_set_id)
    if db_question_set:
        db.delete(db_question_set)
        db.commit()
        return True
    return False
