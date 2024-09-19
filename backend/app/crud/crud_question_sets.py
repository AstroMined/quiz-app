# filename: backend/app/crud/crud_question_sets.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (QuestionSetToGroupAssociation,
                                             QuestionSetToQuestionAssociation)
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.questions import QuestionModel


def check_existing_question_set(db: Session, name: str, creator_id: int) -> Optional[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(
        QuestionSetModel.name == name,
        QuestionSetModel.creator_id == creator_id
    ).first()

def create_question_set_in_db(db: Session, question_set_data: Dict) -> QuestionSetModel:
    existing_question_set = check_existing_question_set(db, question_set_data['name'], question_set_data['creator_id'])
    if existing_question_set:
        raise ValueError("A question set with this name already exists for this user")
    
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
            if key not in ['question_ids', 'group_ids'] and value is not None:
                setattr(db_question_set, key, value)
        
        if 'question_ids' in question_set_data:
            # Remove existing associations
            db.query(QuestionSetToQuestionAssociation).filter_by(question_set_id=question_set_id).delete()
            
            # Add new associations
            for question_id in question_set_data['question_ids']:
                association = QuestionSetToQuestionAssociation(question_set_id=question_set_id, question_id=question_id)
                db.add(association)
        
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
