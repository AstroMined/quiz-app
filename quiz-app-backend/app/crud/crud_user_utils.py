# filename: app/crud/crud_user_utils.py
"""
This module provides utility functions for user-related operations.
"""

from sqlalchemy.orm import Session
from app.models import UserModel

def get_user_by_username_crud(db: Session, username: str) -> UserModel:
    """
    Retrieve a user by username.

    Args:
        db (Session): The database session.
        username (str): The username of the user.

    Returns:
        User: The user with the specified username.
    """
    return db.query(UserModel).filter(UserModel.username == username).first()
