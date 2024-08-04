# filename: app/crud/crud_user.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.users import UserModel
from app.models.groups import GroupModel
from app.models.roles import RoleModel
from app.core.security import get_password_hash

def create_user(db: Session, user_data: dict) -> UserModel:
    default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
    user_role = user_data.get('role', default_role.name)
    
    db_user = UserModel(
        username=user_data['username'],
        email=user_data['email'],
        hashed_password=get_password_hash(user_data['password']),
        role=user_role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    return db.query(UserModel).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_data: dict) -> Optional[UserModel]:
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in user_data.items():
            if key == 'password':
                db_user.hashed_password = get_password_hash(value)
            elif key == 'group_ids':
                groups = db.query(GroupModel).filter(GroupModel.id.in_(value)).all()
                db_user.groups = groups
            else:
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
