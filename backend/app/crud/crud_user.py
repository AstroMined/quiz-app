# filename: backend/app/crud/crud_user.py

from typing import Dict, List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import func

from backend.app.core.security import get_password_hash
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel
from backend.app.services.logging_service import logger


def create_user_in_db(db: Session, user_data: Dict) -> UserModel:
    db_user = UserModel(
        username=user_data['username'].lower(),  # Store username in lowercase
        email=user_data['email'],
        hashed_password=user_data['hashed_password'],
        is_active=user_data.get('is_active', True),
        is_admin=user_data.get('is_admin', False),
        role_id=user_data.get('role_id')
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as exc:
        db.rollback()
        error_info = str(exc.orig)
        if "role_id" in error_info:
            raise ValueError("Role is required for user creation") from exc
        elif "username" in error_info:
            raise ValueError("Username already exists") from exc
        elif "email" in error_info:
            raise ValueError("Email already exists") from exc
        else:
            raise ValueError("Username or email already exists") from exc
    except Exception as exc:
        db.rollback()
        logger.error("Error creating user: %s", exc)
        raise ValueError(f"Error creating user: {str(exc)}") from exc

def read_user_from_db(db: Session, user_id: int) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def read_user_by_username_from_db(db: Session, username: str) -> Optional[UserModel]:
    user = db.query(UserModel).filter(func.lower(UserModel.username) == username.lower()).first()
    if user and user.token_blacklist_date:
        # Ensure token_blacklist_date is timezone-aware
        if user.token_blacklist_date.tzinfo is None:
            user.token_blacklist_date = user.token_blacklist_date.replace(tzinfo=timezone.utc)
    return user

def read_user_by_email_from_db(db: Session, email: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.email == email).first()

def read_users_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    return db.query(UserModel).offset(skip).limit(limit).all()

def update_user_in_db(db: Session, user_id: int, user_data: Dict) -> Optional[UserModel]:
    db_user = read_user_from_db(db, user_id)
    if db_user:
        try:
            for key, value in user_data.items():
                if key == 'password':
                    db_user.hashed_password = get_password_hash(value)
                elif key == 'role_id':
                    role = db.query(RoleModel).filter(RoleModel.id == value).first()
                    if not role:
                        raise ValueError("Invalid role_id")
                    db_user.role_id = value
                elif key == 'username':
                    db_user.username = value.lower()  # Store username in lowercase when updating
                else:
                    setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as exc:
            db.rollback()
            error_info = str(exc.orig)
            if "username" in error_info:
                raise ValueError("Username already exists") from exc
            elif "email" in error_info:
                raise ValueError("Email already exists") from exc
            else:
                raise ValueError("Error updating user") from exc
        except ValueError:
            db.rollback()
            raise
    return None

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
    except IntegrityError:
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

def update_user_token_blacklist_date(db: Session, user_id: int, new_date: Optional[datetime]) -> Optional[UserModel]:
    db_user = read_user_from_db(db, user_id)
    if db_user:
        if new_date is not None:
            # Ensure new_date is timezone-aware
            if new_date.tzinfo is None:
                new_date = new_date.replace(tzinfo=timezone.utc)
        db_user.token_blacklist_date = new_date
        db.commit()
        db.refresh(db_user)
        return db_user
    return None
