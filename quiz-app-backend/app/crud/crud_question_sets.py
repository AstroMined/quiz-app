# filename: app/crud/crud_question_sets.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.question_sets import QuestionSetModel
from app.models.questions import QuestionModel
from app.models.groups import GroupModel
from app.models.associations import QuestionSetToQuestionAssociation, QuestionSetToGroupAssociation

def create_question_set_in_db(db: Session, question_set_data: Dict) -> QuestionSetModel:
    db_question_set = QuestionSetModel(
        name=question_set_data['name'],
        description=question_set_data.get('description'),
        is_public=question_set_data.get('is_public', True),
        creator_id=question_set_data['creator_id']
    )
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def read_question_set_from_db(db: Session, question_set_id: int) -> Optional[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()

def read_question_sets_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).offset(skip).limit(limit).all()

def update_question_set_in_db(db: Session, question_set_id: int, question_set_data: Dict) -> Optional[QuestionSetModel]:
    db_question_set = read_question_set_from_db(db, question_set_id)
    if db_question_set:
        for key, value in question_set_data.items():
            if key not in ['question_ids', 'group_ids']:
                setattr(db_question_set, key, value)
        db.commit()
        db.refresh(db_question_set)
    return db_question_set

def delete_question_set_from_db(db: Session, question_set_id: int) -> bool:
    db_question_set = read_question_set_from_db(db, question_set_id)
    if db_question_set:
        db.delete(db_question_set)
        db.commit()
        return True
    return False

def create_question_set_to_question_association_in_db(db: Session, question_set_id: int, question_id: int) -> bool:
    association = QuestionSetToQuestionAssociation(question_set_id=question_set_id, question_id=question_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_set_to_question_association_from_db(db: Session, question_set_id: int, question_id: int) -> bool:
    association = db.query(QuestionSetToQuestionAssociation).filter_by(
        question_set_id=question_set_id, question_id=question_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_set_to_group_association_in_db(db: Session, question_set_id: int, group_id: int) -> bool:
    association = QuestionSetToGroupAssociation(question_set_id=question_set_id, group_id=group_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_set_to_group_association_from_db(db: Session, question_set_id: int, group_id: int) -> bool:
    association = db.query(QuestionSetToGroupAssociation).filter_by(
        question_set_id=question_set_id, group_id=group_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_questions_for_question_set_from_db(db: Session, question_set_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionSetToQuestionAssociation).filter(
        QuestionSetToQuestionAssociation.question_set_id == question_set_id
    ).all()

def read_groups_for_question_set_from_db(db: Session, question_set_id: int) -> List[GroupModel]:
    return db.query(GroupModel).join(QuestionSetToGroupAssociation).filter(
        QuestionSetToGroupAssociation.question_set_id == question_set_id
    ).all()
