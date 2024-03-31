# filename: app/crud/crud_user_utils.py
"""
This module provides utility functions for user-related operations.
"""

from sqlalchemy.orm import Session
from app.models import User

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
