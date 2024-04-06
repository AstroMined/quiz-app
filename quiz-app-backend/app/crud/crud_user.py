# filename: app/crud/crud_user.py
"""
This module provides CRUD operations for users.
"""

from sqlalchemy.orm import Session
from app.models import UserModel
from app.schemas import UserCreateSchema
from app.core import get_password_hash

def create_user_crud(db: Session, user: UserCreateSchema) -> UserModel:
    """
    Create a new user.

    Args:
        db (Session): The database session.
        user (UserCreate): The user data.

    Returns:
        User: The created user.
    """
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def remove_user_crud(db: Session, user_id: int) -> UserModel:
    """
    Remove a user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to remove.

    Returns:
        User: The removed user, or None if the user doesn't exist.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None
