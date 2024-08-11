# filename: app/crud/crud_groups.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.groups import GroupModel
from app.models.users import UserModel
from app.models.question_sets import QuestionSetModel
from app.models.associations import UserToGroupAssociation, QuestionSetToGroupAssociation

def create_group_in_db(db: Session, group_data: Dict) -> GroupModel:
    db_group = GroupModel(
        name=group_data['name'],
        description=group_data.get('description'),
        creator_id=group_data['creator_id'],
        is_active=group_data.get('is_active', True)
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def read_group_from_db(db: Session, group_id: int) -> Optional[GroupModel]:
    return db.query(GroupModel).filter(GroupModel.id == group_id).first()

def read_groups_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[GroupModel]:
    return db.query(GroupModel).offset(skip).limit(limit).all()

def update_group_in_db(db: Session, group_id: int, group_data: Dict) -> Optional[GroupModel]:
    db_group = read_group_from_db(db, group_id)
    if db_group:
        for key, value in group_data.items():
            setattr(db_group, key, value)
        db.commit()
        db.refresh(db_group)
    return db_group

def delete_group_from_db(db: Session, group_id: int) -> bool:
    db_group = read_group_from_db(db, group_id)
    if db_group:
        db.delete(db_group)
        db.commit()
        return True
    return False

def create_user_to_group_association_in_db(db: Session, user_id: int, group_id: int) -> bool:
    association = UserToGroupAssociation(user_id=user_id, group_id=group_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_user_to_group_association_from_db(db: Session, user_id: int, group_id: int) -> bool:
    association = db.query(UserToGroupAssociation).filter_by(
        user_id=user_id, group_id=group_id
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

def read_users_for_group_from_db(db: Session, group_id: int) -> List[UserModel]:
    return db.query(UserModel).join(UserToGroupAssociation).filter(
        UserToGroupAssociation.group_id == group_id
    ).all()

def read_question_sets_for_group_from_db(db: Session, group_id: int) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).join(QuestionSetToGroupAssociation).filter(
        QuestionSetToGroupAssociation.group_id == group_id
    ).all()
