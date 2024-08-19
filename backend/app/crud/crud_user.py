# filename: backend/app/crud/crud_users.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel


def create_user_in_db(db: Session, user_data: Dict) -> UserModel:
    hashed_password = get_password_hash(user_data['password'])
    db_user = UserModel(
        username=user_data['username'],
        email=user_data['email'],
        hashed_password=hashed_password,
        is_active=user_data.get('is_active', True),
        is_admin=user_data.get('is_admin', False),
        role_id=user_data['role_id']
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def read_user_from_db(db: Session, user_id: int) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def read_user_by_username_from_db(db: Session, username: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.username == username).first()

def read_user_by_email_from_db(db: Session, email: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.email == email).first()

def read_users_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    return db.query(UserModel).offset(skip).limit(limit).all()

def update_user_in_db(db: Session, user_id: int, user_data: Dict) -> Optional[UserModel]:
    db_user = read_user_from_db(db, user_id)
    if db_user:
        for key, value in user_data.items():
            if key == 'password':
                db_user.hashed_password = get_password_hash(value)
            else:
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user_from_db(db: Session, user_id: int) -> bool:
    db_user = read_user_from_db(db, user_id)
    if db_user:
        db.delete(db_user)
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

def read_groups_for_user_from_db(db: Session, user_id: int) -> List[GroupModel]:
    return db.query(GroupModel).join(UserToGroupAssociation).filter(
        UserToGroupAssociation.user_id == user_id
    ).all()

def read_role_for_user_from_db(db: Session, user_id: int) -> Optional[RoleModel]:
    user = read_user_from_db(db, user_id)
    return user.role if user else None

def read_created_question_sets_for_user_from_db(db: Session, user_id: int) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(QuestionSetModel.creator_id == user_id).all()
