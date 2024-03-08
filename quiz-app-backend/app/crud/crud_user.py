# filename: app/crud/crud_user.py
"""
This module provides CRUD operations for users.

It includes functions for creating users, retrieving users by username,
authenticating users, and removing users.
"""

from app.schemas.user import UserCreate, UserLogin
from sqlalchemy.orm import Session
from app.models.users import User
from app.core.security import verify_password, get_password_hash

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db (Session): The database session.
        user (UserCreate): The user data.

    Returns:
        User: The created user.
    """
    fake_hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> User:
    """
    Retrieve a user by username.

    Args:
        db (Session): The database session.
        username (str): The username of the user.

    Returns:
        User: The user with the specified username.
    """
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> User:
    """
    Authenticate a user.

    Args:
        db (Session): The database session.
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        User: The authenticated user, or False if authentication fails.
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def remove_user(db: Session, user_id: int) -> User:
    """
    Remove a user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to remove.

    Returns:
        User: The removed user, or None if the user doesn't exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None