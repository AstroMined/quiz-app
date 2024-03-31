# filename: app/services/auth_service.py
"""
This module provides authentication and authorization services.
"""

from sqlalchemy.orm import Session
from app.crud import get_user_by_username
from app.core import verify_password
from app.models import User

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
    if not user.is_active:
        return False
    return user
