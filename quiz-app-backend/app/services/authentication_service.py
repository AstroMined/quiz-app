# filename: app/services/authentication_service.py

from sqlalchemy.orm import Session
from app.services.user_service import get_user_by_username
from app.core.security import verify_password
from app.models.users import UserModel


def authenticate_user(db: Session, username: str, password: str) -> UserModel:
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False
    return user
