# filename: app/crud/crud_question_tags.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.question_tags import QuestionTagModel
from app.models.questions import QuestionModel
from app.models.associations import QuestionToTagAssociation

def create_question_tag_in_db(db: Session, question_tag_data: Dict) -> QuestionTagModel:
    db_question_tag = QuestionTagModel(
        tag=question_tag_data['tag'],
        description=question_tag_data.get('description')
    )
    db.add(db_question_tag)
    db.commit()
    db.refresh(db_question_tag)
    return db_question_tag

def read_question_tag_from_db(db: Session, question_tag_id: int) -> Optional[QuestionTagModel]:
    return db.query(QuestionTagModel).filter(QuestionTagModel.id == question_tag_id).first()

def read_question_tag_by_tag_from_db(db: Session, tag: str) -> Optional[QuestionTagModel]:
    return db.query(QuestionTagModel).filter(QuestionTagModel.tag == tag).first()

def read_question_tags_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionTagModel]:
    return db.query(QuestionTagModel).offset(skip).limit(limit).all()

def update_question_tag_in_db(db: Session, question_tag_id: int, question_tag_data: Dict) -> Optional[QuestionTagModel]:
    db_question_tag = read_question_tag_from_db(db, question_tag_id)
    if db_question_tag:
        for key, value in question_tag_data.items():
            setattr(db_question_tag, key, value)
        db.commit()
        db.refresh(db_question_tag)
    return db_question_tag

def delete_question_tag_from_db(db: Session, question_tag_id: int) -> bool:
    db_question_tag = read_question_tag_from_db(db, question_tag_id)
    if db_question_tag:
        db.delete(db_question_tag)
        db.commit()
        return True
    return False

def create_question_to_tag_association_in_db(db: Session, question_id: int, tag_id: int) -> bool:
    association = QuestionToTagAssociation(question_id=question_id, question_tag_id=tag_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_tag_association_from_db(db: Session, question_id: int, tag_id: int) -> bool:
    association = db.query(QuestionToTagAssociation).filter_by(
        question_id=question_id, question_tag_id=tag_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_tags_for_question_from_db(db: Session, question_id: int) -> List[QuestionTagModel]:
    return db.query(QuestionTagModel).join(QuestionToTagAssociation).filter(
        QuestionToTagAssociation.question_id == question_id
    ).all()

def read_questions_for_tag_from_db(db: Session, tag_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToTagAssociation).filter(
        QuestionToTagAssociation.question_tag_id == tag_id
    ).all()
